from serverSocket import ServerSocket
from Shared.message_builder import build_message, validate_message
import threading


class Erlang_calculator_service:
    def __init__(self, logger):
        self.serviceSocket = ServerSocket('127.0.0.1', 32004)
        self.logger = logger
        self.ID = "ERLANG_CALCULATOR"

    def erlang_b(self, E, N):
        B = 1.0
        for n in range(1, N+1):
            B = (E * B) / (n + E * B)
        return B

    def needed_lines(self, A, blockingPercentage):
        N = 1
        while True:
            B = self.erlang_b(A, N)
            if B <= blockingPercentage:
                return N
            N += 1


    def task(self, message, addr):
        try:
            self.logger.info(f"{self.ID}: Message received from client {addr}:\n{message}")

            numLines = message ["numLines"]
            numCalls= message["numCalls"]
            avgDuration = message["avgDuration"]
            blockingPercentage = message["blockingPercentage"]

            A = (numLines*numCalls*avgDuration)/3600
            maxLines = self.needed_lines(A, blockingPercentage)

            response = build_message(
                "ERLANG_RESPONSE",
                Erlangs=A,
                maxLines= maxLines
            )

        except Exception as e:
            self.logger.error(f"{self.ID}: from client {addr}, {str(e)}")
            response = build_message("ERROR", source=self.ID, error=str(e))

        self.serviceSocket.send_message(response, addr)

    def start(self):
        while True:
            message, addr = self.serviceSocket.recv_message(1024)

            try:
                validate_message(message, "ERLANG_REQUEST")

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
