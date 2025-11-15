from serverSocket import ServerSocket
from Shared.message_builder import build_message, validate_message
import threading
import json

class BW_calculator_service:
    """
    Servicio de red para calcular el ancho de banda (Bandwidth) de llamadas.

    Escucha en un socket, recibe solicitudes de cálculo de BW,
    procesa los datos basándose en una base de datos de códecs
    y devuelve los resultados del cálculo en un hilo separado por cada petición.
    """
    def __init__(self, IP, logger):
        """
        Inicializa el servicio de calculadora de BW.

        :param logger: Una instancia de un logger para registrar los eventos del servicio.
        :type logger: logging.Logger
        """
        
        self.serviceSocket = ServerSocket(IP, 32005)
        self.logger = logger
        self.ID = "BW_CALCULATOR"
        self.db = self._load_database('codec_db.json')

    def _load_database(self, filename):

        """
        Carga la base de datos de códecs desde un archivo JSON.

        Es un método interno utilizado durante la inicialización.

        :param filename: El nombre del archivo JSON a cargar.
        :type filename: str
        :raises RuntimeError: Si el archivo no se encuentra (FileNotFoundError)
                            o si el archivo contiene JSON inválido (json.JSONDecodeError).
        :returns: Los datos de la base de datos cargados.
        :rtype: dict
        """
        self.logger.info(f"{self.ID}: Attempting to load database from {filename}")
        try:
            with open(filename, 'r') as file:
                db_data = json.load(file)
            self.logger.info(f"{self.ID}: Database loaded successfully.")
            return db_data

        except FileNotFoundError:
            error_msg = f"FATAL ERROR: Database file '{filename}' not found."
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

        except json.JSONDecodeError as e:
            error_msg = f"FATAL ERROR: Database file '{filename}' contains invalid JSON format. Details: {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    def task(self, message, addr):
        """
        Procesa una solicitud de cálculo de BW y envía la respuesta.

        Esta función se ejecuta en un hilo separado por cada solicitud.
        Realiza el cálculo del ancho de banda para escenarios comprimidos
        y no comprimidos basándose en los parámetros del mensaje
        (códec, pppoe, vlan, etc.) y los datos de la base de datos.

        Maneja internamente los errores (KeyError, ValueError) que puedan
        surgir durante el cálculo, registrándolos y terminando la tarea
        sin enviar respuesta.

        :param message: El mensaje de solicitud deserializado (un diccionario)
                        que contiene los detalles para el cálculo.
        :type message: dict
        :param addr: La dirección (IP, puerto) del cliente que envió la solicitud.
        :type addr: tuple
        
        
        Ejemplo de uso:

        Asumiendo datos en `self.db`:
        `self.db["G.711"] = {"pps": 50, "VPS (B)": 160}`

        Un **mensaje de entrada (message)** tendría esta estructura:
        ```json
        {
            "codec": "G.711",
            "pppoe": true,
            "vlan8021q": false,
            "reservedBW": 0.25,
            "totalCalls": 50
        }
        ```

        Tras el cálculo, el **mensaje de respuesta** generado sería:
        ```json
        {
            "type": "BW_RESPONSE",
            "payload": {
                "compressed": {
                    "packetLength": 1504,
                    "callBW": 94000.0,
                    "BWst": 4.7
                },
                "uncompressed": {
                    "packetLength": 1792,
                    "callBW": 112000.0,
                    "BWst": 5.6
                },
                "pps": 50
            }
        }
        ```

        """
        IP_header = 160
        UDP_header = 64
        RTP_header = 96
        ETH_CRC_header = 144

        UNCOMPRESSED_HEADER = ETH_CRC_header + IP_header + UDP_header + RTP_header
        COMPRESSED_HEADER = ETH_CRC_header + 32

        uncompressed_data = {
            "packetLength": None,
            "callBW": None,
            "BWst": None
        }

        compressed_data = {
            "packetLength": None,
            "callBW": None,
            "BWst": None
        }

        try:
            codec_name = message["codec"]
            codec_details = self.db.get(codec_name)

            if not codec_details:
                raise KeyError(f"Codec '{codec_name}' not found.")
            pps = codec_details["pps"]

            uncompressed_data["packetLength"] = UNCOMPRESSED_HEADER + codec_details["VPS (B)"] * 8
            compressed_data["packetLength"] = COMPRESSED_HEADER + codec_details["VPS (B)"] * 8

            if message["pppoe"]:
                uncompressed_data["packetLength"] += 48
                compressed_data["packetLength"] += 48

            if message["vlan8021q"]:
                uncompressed_data["packetLength"] += 32
                compressed_data["packetLength"] += 32

            uncompressed_data["callBW"] = uncompressed_data["packetLength"] * pps * (1 + message["reservedBW"])
            compressed_data["callBW"] = compressed_data["packetLength"] * pps * (1 + message["reservedBW"])

            uncompressed_data["BWst"] = uncompressed_data["callBW"] * message["totalCalls"] * 1e-6
            compressed_data["BWst"] = compressed_data["callBW"] * message["totalCalls"] * 1e-6

            response = build_message(
                "BW_RESPONSE",
                compressed=compressed_data,
                uncompressed=uncompressed_data,
                pps=pps
            )

        except (KeyError, ValueError) as e:
            self.logger.error(f"{self.ID}: from client {addr}, {str(e)}")
            response = build_message("ERROR", source=self.ID, error=str(e))

        self.serviceSocket.send_message(response, addr)

    def start(self):
        """
        Inicia el bucle principal del servidor para escuchar solicitudes.

        Es un bucle infinito que espera mensajes en el socket.
        Cuando se recibe un mensaje 'BW_REQUEST' válido,
        inicia un nuevo hilo (thread) para procesarlo
        llamando a 'self.task'.
        """
        while True:
            message, addr = self.serviceSocket.recv_message(1024)

            try:
                validate_message(message, "BW_REQUEST")

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
        """
        Cierra el socket del servidor.
        """
        self.serviceSocket.close()

