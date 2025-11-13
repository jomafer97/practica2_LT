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
        IP_header = 160
        UDP_header = 64
        RTP_header = 96
        ETH_CRC_header = 144

        UNCOMPRESSED_HEADER = ETH_CRC_header + IP_header + UDP_header + RTP_header
        COMPRESSED_HEADER = ETH_CRC_header + 32

        uncompressed_data = {
            "packetLength": None,
            "callBW": None,
            "BWst": None
        }

        compressed_data = {
            "packetLength": None,
            "callBW": None,
            "BWst": None
        }

        try:
            codec_name = message["codec"]
            codec_details = self.db.get(codec_name)

            if not codec_details:
                raise KeyError(f"Codec '{codec_name}' not found.")
            pps = codec_details["pps"]

            uncompressed_data["packetLength"] = UNCOMPRESSED_HEADER + codec_details["VPS (B)"] * 8
            compressed_data["packetLength"] = COMPRESSED_HEADER + codec_details["VPS (B)"] * 8

            if message["pppoe"]:
                uncompressed_data["packetLength"] += 48
                compressed_data["packetLength"] += 48

            if message["vlan8021q"]:
                uncompressed_data["packetLength"] += 32
                compressed_data["packetLength"] += 32

            uncompressed_data["callBW"] = uncompressed_data["packetLength"] * pps * (1 + message["reservedBW"])
            compressed_data["callBW"] = compressed_data["packetLength"] * pps * (1 + message["reservedBW"])

            uncompressed_data["BWst"] = uncompressed_data["callBW"] * message["totalCalls"] * 1e-6
            compressed_data["BWst"] = compressed_data["callBW"] * message["totalCalls"] * 1e-6

            response = build_message(
                "BW_RESPONSE",
                compressed=compressed_data,
                uncompressed=uncompressed_data,
                pps=pps
            )

        except (KeyError, ValueError) as e:
            self.logger.error(f"{self.ID}: from client {addr}, {str(e)}")
            response = build_message("ERROR", source=self.ID, error=str(e))

        self.serviceSocket.send_message(response, addr)

    def start(self):
        while True:
            message, addr = self.serviceSocket.recv_message(1024)

            try:
                validate_message(message, "BW_REQUEST")

                thread = threading.Thread(
                    target=self.task,
                    args=(message, addr),
                    daemon=True
                )

                thread.start()

            except Exception as e:
                self.logger.error(f"{self.ID}: from client {addr}, {str(e)}")
                error_msg = build_message("ERROR", source=self.ID, error=str(e))
                self.serviceSocket.send_message(error_msg, addr)


    def close(self):
        self.serviceSocket.close()

