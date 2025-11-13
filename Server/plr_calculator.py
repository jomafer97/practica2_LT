from serverSocket import ServerSocket
from Shared.message_builder import build_message, validate_message
import threading
import math

class PLR_calculator_service:
    def __init__(self, logger):
        self.serviceSocket = ServerSocket('127.0.0.1', 32007)
        self.logger = logger
        self.ID = "PLR_CALCULATOR"

    def task(self, message, addr):
        try:
            self.logger.info(f"{self.ID}: Message received from client {addr}:\n{message}")

            bitstream = message["bitstream"]

            num_zeros = bitstream.count('0')
            num_ones = bitstream.count('1')

            if num_ones == 0 or num_zeros == 0:
                if num_ones == 0:
                    p = 0
                    q = 1
                    pi1 = 0
                    pi0 = 1
                    e = 0
                else:
                    p = 1
                    q = 0
                    pi1 = 1
                    pi0 = 0
                    e = len(bitstream)

            else:
                ones = bitstream.split('0')
                bursts = [burst for burst in ones if burst]
                nBursts = len(bursts)

                avg_len = 0

                for burst in bursts:
                    avg_len += (len(burst) - 1)

                p = nBursts*1.0/num_zeros
                q = 1 - avg_len*1.0/num_ones
                pi1 = p / (p + q)
                pi0 = 1 - pi1
                e=1/q

            response = build_message(
                "PLR_RESPONSE",
                p=p,
                q=q,
                pi1=pi1,
                pi0=pi0,
                E=e
            )

        except Exception as e:
            self.logger.error(f"{self.ID}: from client {addr}, {str(e)}")
            response = build_message("ERROR", source=self.ID, error=str(e))

        self.serviceSocket.send_message(response, addr)

    def start(self):
        while True:
            message, addr = self.serviceSocket.recv_message(1024)

            try:
                validate_message(message, "PLR_REQUEST")

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
