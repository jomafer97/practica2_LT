from serverSocket import ServerSocket
from Shared.message_builder import build_message, validate_message
import threading
import json

class Rt_calculator_service:
    def __init__(self, IP, logger):
        """
    Servicio de red para calcular el Retardo Total (RT) en VoIP.

    Escucha peticiones en un socket. Utiliza una base de datos de códecs
    y parámetros de red (jitter, retardo de red) proporcionados por
    el cliente para calcular el retardo total (RT) de extremo a extremo
    para dos escenarios de jitter buffer (1.5x y 2x Jitter).
    """
        self.serviceSocket = ServerSocket(IP, 32003)
        self.logger = logger
        self.ID = "RT_CALCULATOR"
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
        Procesa una solicitud de cálculo de RT y envía la respuesta.

        Esta función se ejecuta en un hilo. Extrae el códec, jitter
        y retardo de red del mensaje. Busca los datos del códec en la
        base de datos y calcula el RT para 2x Jitter y 1.5x Jitter.

        Si el códec no se encuentra, envía un mensaje de ERROR al cliente.

        :param message: El mensaje de solicitud (dict) que debe
                        contener 'codec', 'jitter' y 'netDelay'.
        :type message: dict
        :param addr: La dirección (IP, puerto) del cliente.
        :type addr: tuple

        Ejemplo de uso:

        Asumiendo datos en `self.db`:
        `self.db["G.729"] = {"CSI (ms)": 10, "VPS (ms)": 30, "algD (ms)": 5}`

        Un **mensaje de entrada (message)** tendría esta estructura:
        ```json
        {
            "codec": "G.729",
            "jitter": 20,
            "netDelay": 50
        }
        ```

        **Cálculo (simplificado):**
        - `csi` = 10, `rphy` = 1, `packet` = 20, `algD` = 5
        - `rjitter2` = 40, `rjitter15` = 30, `netDelay` = 50
        - `rt2` = 10 + 20 + 5 + 40 + 50 + 1 = 126
        - `rt15` = 10 + 20 + 5 + 30 + 50 + 1 = 116

        El **mensaje de respuesta** generado sería:
        ```json
        {
            "type": "RT_RESPONSE",
            "payload": {
                "rt2jit": 126.0,
                "rt1_5jit": 116.0,
                "csi": 10,
                "rphy": 1.0,
                "rpac": 20
            }
        }
        ```
        """
        try:
            self.logger.info(f"{self.ID}: Message received from client {addr}:\n{message}")

            codec = message["codec"]
            jitter = message["jitter"]
            netDelay = message["netDelay"]

            if codec not in self.db:
                self.logger.error(f"{self.ID}: Invalid codec received '{codec}'")
                response = build_message(
                    "ERROR",
                    source=self.ID,
                    error=f"f{self.ID}:Provided codec is not registered {codec}"
                )
                self.serviceSocket.send_message(response, addr)
                return

            codec_data = self.db[codec]

            csi = codec_data["CSI (ms)"]
            rphy = csi*0.1
            packet = codec_data["VPS (ms)"] - codec_data["CSI (ms)"]
            algD = codec_data["algD (ms)"]
            rjitter2 = 2*jitter
            rjitter15 = 1.5*jitter

            rt2 = csi + packet + algD + rjitter2 + netDelay + rphy
            rt15 = csi + packet + algD + rjitter15 + netDelay + rphy

            response = build_message(
                "RT_RESPONSE",
                rt2jit=rt2,
                rt1_5jit=rt15,
                csi=csi,
                rphy=rphy,
                rpac=packet,
                algD=algD
            )

        except Exception as e:
            self.logger.error(f"{self.ID}: from client {addr}, {str(e)}")
            response = build_message("ERROR", source=self.ID, error=str(e))

        self.serviceSocket.send_message(response, addr)

    def start(self):
        """
        Inicia el bucle principal del servidor para escuchar solicitudes.

        Espera mensajes. Si recibe un 'RT_REQUEST' válido
        (validado por 'validate_message'), inicia un nuevo hilo
        para procesar la tarea ('self.task'). Si la validación falla,
        captura la excepción y envía un mensaje de error al cliente.
        """
        while True:
            message, addr = self.serviceSocket.recv_message(1024)

            try:
                validate_message(message, "RT_REQUEST")

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

