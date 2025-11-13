import threading

from serverSocket import ServerSocket
from Shared.message_builder import build_message, validate_message
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

class Report_creator_service:
    def __init__(self, logger):
        self.serviceSocket = ServerSocket('127.0.0.1', 32008)
        self.logger = logger
        self.ID = "REPORT_CREATOR"

    def task(self, message, addr):
        pass

    def start(self):
        while True:
            message, addr = self.serviceSocket.recv_message(1024)

            try:
                validate_message(message, "REPORT_REQUEST")

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
