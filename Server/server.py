import sys, os, threading, time, logging

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from rt_calculator import Rt_calculator_service
from erlang_calculator import Erlang_calculator_service
from bw_calculator import BW_calculator_service
from cost_calculator import Cost_calculator_service
from plr_calculator import PLR_calculator_service
from report_creator import Report_creator_service

IP = '127.0.0.1'

class Server:
    """
    Servidor principal de la aplicación.

    Esta clase es responsable de configurar el logging,
    inicializar todos los servicios de cálculo (RT, Erlang, BW, Cost, PLR)
    y lanzarlos cada uno en un hilo (thread) demonizado separado.
    También gestiona el apagado ordenado de los servicios.
    """

    def __init__(self):
        """
        Inicializa el servidor.

        Configura un logger para registrar en 'server.log',
        instancia cada uno de los servicios de cálculo pasándoles
        el logger y los almacena en una lista 'self.services'.
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.file_handler = logging.FileHandler('server.log', mode='a', encoding='utf-8')
        self.formatter = logging.Formatter(
            '%(asctime)s (%(levelname)s) - %(message)s'
        )
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

        self.services = [
            Rt_calculator_service(IP, self.logger),
            Erlang_calculator_service(IP,self.logger),
            Cost_calculator_service(IP, self.logger),
            BW_calculator_service(IP, self.logger),
            PLR_calculator_service(IP, self.logger),
            Report_creator_service(IP, self.logger)
        ]

        self.service_threads = []

    def start_services(self):
        """
        Inicia todos los servicios de cálculo en hilos separados.

        Itera sobre la lista 'self.services', creando un hilo demonizado
        (daemon=True) para cada uno, apuntando al método 'start()'
        de dicho servicio. Luego, inicia todos los hilos.
        """
        self.logger.info("Starting server...")
        for service in self.services:
            self.service_threads.append(threading.Thread(
                target=service.start,
                daemon=True
            ))

        for thread in self.service_threads:
            thread.start()

        self.logger.info("Server successfully started.")

    def stop(self):
        """
        Detiene todos los servicios de forma ordenada.

        Itera sobre la lista 'self.services' y llama al método 'close()'
        de cada uno, lo que debería cerrar sus sockets y permitir
        que sus hilos terminen.
        """
        for service in self.services:
            service.close()

if __name__ == "__main__":
    server = Server()

    try:
        server.start_services()
        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nShutting down...")

    finally:
        server.stop()
