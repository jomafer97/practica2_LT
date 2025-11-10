from serverSocket import ServerSocket
from Shared.message_builder import build_message, validate_message
import threading


class Erlang_calculator_service:
    def __init__(self, logger):
        self.serviceSocket = ServerSocket('127.0.0.1', 32004)
        self.logger = logger

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

        numChannels = message ["numChannels"]
        numCalls= message["numCalls"]
        avgDuration = message["avgDuration"]
        blockingPercentage = message["blockingPercentage"]
        self.logger.info("ERLANG CALCULATOR: Succesfully called")

        A = (numChannels*numCalls*avgDuration)/3600
        maxNum = self.needed_lines(A, blockingPercentage)
        result = build_message(
            "ERLANG_RESPONSE",
            Erlangs=A,
            maxLinesNum= maxNum
        )

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
