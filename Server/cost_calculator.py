from serverSocket import ServerSocket
from Shared.message_builder import build_message, validate_message
import threading

COST_MBPS = 100.0
class Cost_calculator_service:
    def __init__(self, logger):
        self.serviceSocket = ServerSocket('127.0.0.1', 32006)
        self.logger = logger
        self.ID = "COST_CALCULATOR"

    def task(self, message, addr):
        try:
            self.logger.info(f"{self.ID}: Message received from client {addr}:\n{message}")

            callBW = message["callBW"]
            BWst = message["BWst"]
            Pmax = message["Pmax"]

            cost = {
                "RTP": BWst["RTP"] * COST_MBPS,
                "cRTP": BWst["cRTP"] * COST_MBPS
            }

            rtp = {
                "valid": cost["RTP"] <= Pmax,
                "possibleCalls": int(BWst["RTP"] * 1e6 / callBW["RTP"]) if cost["RTP"] <= Pmax else int(
                    Pmax * 1.0 / (callBW["RTP"] * 1e-6 * COST_MBPS))
            }

            crtp = {
                "valid": cost["cRTP"] <= Pmax,
                "possibleCalls": int(BWst["cRTP"] * 1e6 / callBW["cRTP"]) if cost["cRTP"] <= Pmax else int(
                    Pmax * 1.0 / (callBW["cRTP"] * 1e-6 * COST_MBPS))
            }

            response = build_message(
                "COST_RESPONSE",
                mbpsCost=COST_MBPS,
                RTP=rtp,
                cRTP=crtp
            )

        except Exception as e:
            self.logger.error(f"{self.ID}: from client {addr}, {str(e)}")
            response = build_message("ERROR", source=self.ID, error=str(e))

        self.serviceSocket.send_message(response, addr)

    def start(self):
        while True:
            message, addr = self.serviceSocket.recv_message(1024)

            try:
                validate_message(message, "COST_REQUEST")

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
        self.logger.info("COST CALCULATION REQUEST SERVICE: Socket closed")
