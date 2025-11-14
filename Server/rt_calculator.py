from serverSocket import ServerSocket
from Shared.message_builder import build_message, validate_message
import threading
import json

class Rt_calculator_service:
    def __init__(self, logger):
        self.serviceSocket = ServerSocket('127.0.0.1', 32003)
        self.logger = logger
        self.ID = "RT_CALCULATOR"
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
        try:
            self.logger.info(f"{self.ID}: Message received from client {addr}:\n{message}")

            codec = message["codec"]
            jitter = message["jitter"]
            netDelay = message["netDelay"]

            if codec not in self.db:
                self.logger.error(f"{self.ID}: Invalid codec received '{codec}'")
                response = build_message(
                    "ERROR",
                    source=self.ID,
                    error=f"f{self.ID}:Provided codec is not registered {codec}"
                )
                self.serviceSocket.send_message(response, addr)
                return

            codec_data = self.db[codec]

            csi = codec_data["CSI (ms)"]
            rphy = csi*0.1
            packet = codec_data["VPS (ms)"] - codec_data["CSI (ms)"]
            algD = codec_data["algD (ms)"]
            rjitter2 = 2*jitter
            rjitter15 = 1.5*jitter

            rt2 = csi + packet + algD + rjitter2 + netDelay + rphy
            rt15 = csi + packet + algD + rjitter15 + netDelay + rphy

            response = build_message(
                "RT_RESPONSE",
                rt2jit=rt2,
                rt1_5jit=rt15,
                csi=csi,
                rphy=rphy,
                rpac=packet,
                algD=algD
            )

        except Exception as e:
            self.logger.error(f"{self.ID}: from client {addr}, {str(e)}")
            response = build_message("ERROR", source=self.ID, error=str(e))

        self.serviceSocket.send_message(response, addr)

    def start(self):
        while True:
            message, addr = self.serviceSocket.recv_message(1024)

            try:
                validate_message(message, "RT_REQUEST")

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

