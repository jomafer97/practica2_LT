from serverSocket import ServerSocket
from Shared.message_builder import build_message, validate_message
import threading

class Erlang_calculator_service:
    def __init__(self, logger):
        self.serviceSocket = ServerSocket('127.0.0.1', 32004)
        self.logger = logger


    def task(self, message, addr):
        # TO DO
        self.logger.info("ERLANG CALCULATOR: Succesfully called")

        result = {
            "codec" : "ERLANG"
        }

        self.serviceSocket.send_message(result, addr)

    def start(self):
        while True:
            message, addr = self.serviceSocket.recv_message(1024)

            if validate_message(message, "ERLANG_REQUEST"):
                self.logger.info("ERLANG CALCULATOR: Valid message received")
                self.logger.info(message)

                thread = threading.Thread(
                    target=self.task,
                    args=(message, addr),
                    daemon=True
                )

                thread.start()
            else:
                self.logger.info("ERLANG CALCULATOR: Wrong message received")
                pass

    def close(self):
        self.serviceSocket.close()
