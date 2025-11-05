import threading, time
from rt_calculator import Rt_calculator_service
from erlang_calculator import Erlang_calculator_service
from server_logs import Server_logger

class Server:
    def __init__(self):
        self.serv_logger = Server_logger()
        self.services = [
            Rt_calculator_service(self.serv_logger.logger),
            Erlang_calculator_service(self.serv_logger.logger)
        ]
        self.service_threads = []

    def start_services(self):
        self.serv_logger.logger.info("Test")
        for service in self.services:
            self.service_threads.append(threading.Thread(
                target=service.start,
                daemon=True
            ))

        for thread in self.service_threads:
            thread.start()

    def stop(self):
        for service in self.services:
            service.close()

if __name__ == "__main__":
    server = Server()

    try:
        server.start_services()
        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nInterrupción recibida (Ctrl+C). Iniciando cierre seguro.")

    finally:
        server.stop()
