from serverSocket import ServerSocket
from Shared.message_builder import build_message, validate_message
import threading

class Cost_calculator_service:
    def __init__(self, logger):
        self.serviceSocket = ServerSocket('127.0.0.1', 32006)
        self.logger = logger
        self.id = "cost_calculation_request_ID"

    def task(self, message, addr):
        self.logger.info("COST CALCULATION REQUEST: Successfully called")
        self.logger.info(f"Received message: {message}")

        try:
            # Extract fields from message
            BWstRTP = message["BWstRTP"]
            BWstcRTP = message["BWstcRTP"]
            Pmax = message["Pmax"]
            numCalls = message["numCalls"]

            # Fixed price per Mbps
            PMbps = 1.0

            # Compute total costs
            total_cost_stRTP = BWstRTP * PMbps
            total_cost_stcRTP = BWstcRTP * PMbps

            # Determine affordability
            verificationstRTP = total_cost_stRTP <= Pmax
            verificationstcRTP = total_cost_stcRTP <= Pmax

            # Compute number of affordable calls
            if verificationstRTP:
                compliantCallstRTP = numCalls
            else:
                compliantCallstRTP = int((Pmax / total_cost_stRTP) * numCalls) if total_cost_stRTP > 0 else 0

            if verificationstcRTP:
                compliantCallstcRTP = numCalls
            else:
                compliantCallstcRTP = int((Pmax / total_cost_stcRTP) * numCalls) if total_cost_stcRTP > 0 else 0

            # Build the response
            response = build_message(
                "COST_RESPONSE",
                PMbps=PMbps,
                verificationstRTP=verificationstRTP,
                verificationstcRTP=verificationstcRTP,
                compliantCallstRTP=compliantCallstRTP,
                compliantCallstcRTP=compliantCallstcRTP
            )

            # Send the response
            self.serviceSocket.send_message(response, addr)
            self.logger.info(f"Response sent: {response}")

        except Exception as e:
            self.logger.error(f"Error during cost calculation: {e}")

    def start(self):
        self.logger.info("COST CALCULATION REQUEST SERVICE: Started and listening...")
        while True:
            message, addr = self.serviceSocket.recv_message(1024)

            if validate_message(message, "COST_REQUEST"):
                self.logger.info("COST CALCULATION REQUEST: Valid message received")
                self.logger.info(message)

                thread = threading.Thread(
                    target=self.task,
                    args=(message, addr),
                    daemon=True
                )
                thread.start()
            else:
                self.logger.info("COST CALCULATION REQUEST: Wrong message received")
                pass

    def close(self):
        self.serviceSocket.close()
        self.logger.info("COST CALCULATION REQUEST SERVICE: Socket closed")
