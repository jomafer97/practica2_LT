from serverSocket import ServerSocket
from Shared.message_builder import build_message, validate_message
import threading

class Rt_calculator_service:
    def __init__(self, logger):
        self.serviceSocket = ServerSocket('127.0.0.1', 32003)
        self.logger = logger
        self.ID = "RT_CALCULATOR"

    def task(self, message, addr):
        # TO DO
        self.logger.info(f"{self.ID}: Successfully called")

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
                validate_message(message, "RT_REQUEST")
                self.logger.info(f"{self.ID}: Valid message received")
                self.logger.info(message)

                thread = threading.Thread(
                    target=self.task,
                    args=(message, addr),
                    daemon=True
                )

                thread.start()

            except Exception as e:
                self.logger.error(f"{self.ID}: {str(e)}")
                error_msg = build_message("ERROR", source=self.ID, message=str(e))
                self.serviceSocket.send_message(error_msg, addr)

    def close(self):
        self.serviceSocket.close()

