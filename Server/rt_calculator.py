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
            response = build_message(
                "ERLANG_REQUEST",
                numChannels=20,
                numCalls=10,
                avgDuration=5,
                blockingPercentage=2
            )

        except Exception as e:
            response = build_message(
                "ERROR",
                source=self.ID,
                message=str(e)
            )

        self.serviceSocket.send_message(response, addr)

    def start(self):
        while True:
            message, addr = self.serviceSocket.recv_message(1024)

            try:
                self.logger.info(f"{self.ID}: Petition received from client {addr}")
                validate_message(message, "RT_REQUEST")
                self.logger.info(message)

                thread = threading.Thread(
                    target=self.task,
                    args=(message, addr),
                    daemon=True
                )

                thread.start()

            except Exception as e:
                self.logger.error(f"{self.ID}: {str(e)}")
                error_msg = build_message("ERROR", source=self.ID, error=str(e))
                self.serviceSocket.send_message(error_msg, addr)

    def close(self):
        self.serviceSocket.close()

