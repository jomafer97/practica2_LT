#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 10 10:37:03 2025

@author: josedavid
"""

from serverSocket import ServerSocket
from Shared.message_builder import build_message, validate_message
import threading
import json

class BW_calculator_service:

    def __init__(self, logger):
        self.serviceSocket = ServerSocket('127.0.0.1', 32005)
        self.logger = logger
        self.ID = "BW_CALCULATOR"
        self.db = self._load_database('codec_db.json')

    def _load_database(self, filename):
        self.logger.info(f"{self.ID}: Attempting to load database from {filename}")

        try:
            with open(filename, 'r') as file:
                db_data = json.load(file)
            self.logger.info(f"{self.ID}: Database loaded successfully.")
            return db_data

        except FileNotFoundError:
            error_msg = f"FATAL ERROR: Database file '{filename}' not found."
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

        except json.JSONDecodeError as e:
            error_msg = f"FATAL ERROR: Database file '{filename}' contains invalid JSON format. Details: {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    def task(self, message, addr):
        cabEther_CRC = 144
        cabIP = 160
        cabIP_UDP_RTP_comp = 32
        cabUDP = 64
        cabRTP = 96

        try:
            # Extracción y validación de datos
            BWres = float(message["ReservedBW"]) / 100
            Ncalls = float(message["maxNumCalls"])
            ExtHead = float(message.get("extendedHeader", 0))
            codec_name = message["codec"]

            codec_details = self.db.get(codec_name)

            if not codec_details:
                raise KeyError(f"Codec '{codec_name}' not found.")

            VPS = float(codec_details["VPS (B)"]) * 8
            packetps = float(codec_details["pps"])

        except (KeyError, ValueError) as e:
            self.logger.error(f"Error processing message from {addr}: {e}")
            return

        # Cálculos
        Cab = cabEther_CRC + cabIP + cabUDP + cabRTP + ExtHead
        Cabcomp = cabEther_CRC + ExtHead + cabIP_UDP_RTP_comp

        nuncompressedPktLength = Cab + VPS
        compressedPktLength = Cabcomp + VPS

        BWu_per_call = nuncompressedPktLength * packetps * (1 + BWres)
        BWuComp_per_call = compressedPktLength * packetps * (1 + BWres)

        BandWidthRTP = BWu_per_call * Ncalls
        BandWidthcRTP = BWuComp_per_call * Ncalls

        # Respuesta
        response = build_message(
            "BW_RESPONSE",
            uncompressedPktLength=nuncompressedPktLength,
            compressedPktLength=compressedPktLength,
            pps=packetps,
            BWcRTP=BandWidthcRTP,
            BWRTP=BandWidthRTP
        )
        self.logger.info("f{self.ID}: Successfully called")
        self.serviceSocket.send_message(response, addr)

    def start(self):
        while True:
            message, addr = self.serviceSocket.recv_message(1024)

            if validate_message(message, "BW_REQUEST"):
                self.logger.info("f{self.ID}: Valid message received")
                self.logger.info(message)

                thread = threading.Thread(
                    target=self.task,
                    args=(message, addr),
                    daemon=True
                )

                thread.start()
            else:
                self.logger.info("f{self.ID}: Wrong message received")
                pass

    def close(self):
        self.serviceSocket.close()
