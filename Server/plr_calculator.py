from serverSocket import ServerSocket
from Shared.message_builder import build_message, validate_message
import threading
import math

class PLR_calculator_service:
    """
    Servicio de red para calcular métricas de Tasa de Pérdida de Paquetes (PLR).

    Analiza un 'bitstream' (flujo de bits) de '0's (recibidos) y '1's (perdidos)
    para calcular las probabilidades de un modelo de Markov de dos estados
    (similar al modelo Gilbert-Elliot) para la pérdida de paquetes.
    """
    def __init__(self, IP, logger):
        """
        Inicializa el servicio de calculadora de PLR.

        :param logger: Una instancia de un logger para registrar los eventos del servicio.
        :type logger: logging.Logger
        """
        self.serviceSocket = ServerSocket(IP, 32007)
        self.logger = logger
        self.ID = "PLR_CALCULATOR"

    def task(self, message, addr):
        """
        Procesa una solicitud de cálculo de PLR y envía la respuesta.

        Esta función se ejecuta en un hilo. Analiza un 'bitstream'
        (cadena de '0's y '1's) para modelar la pérdida de paquetes.
        '0' = paquete recibido (estado "Bueno").
        '1' = paquete perdido (estado "Malo").

        Calcula:
        - p: Probabilidad de transición Bueno -> Malo.
        - q: Probabilidad de transición Malo -> Bueno.
        - pi1: Probabilidad estacionaria de estar en estado Malo (pérdida).
        - pi0: Probabilidad estacionaria de estar en estado Bueno (recibido).
        - E: Longitud media de la ráfaga de pérdidas (1/q).

        :param message: El mensaje de solicitud (dict) que debe
                        contener la clave 'bitstream'.
        :type message: dict
        :param addr: La dirección (IP, puerto) del cliente.
        :type addr: tuple

        Ejemplo de uso:

        Un **mensaje de entrada (message)** tendría esta estructura:
        ```json
        {
            "bitstream": "000110010000111000"
        }
        ```

        **Cálculo (simplificado):**
        - `num_zeros` (recibidos) = 13
        - `num_ones` (perdidos) = 6
        - `bursts` (ráfagas de '1's) = ['11', '1', '111']
        - `nBursts` = 3
        - `p` (Prob. 0->1) = 3 / 13 = 0.2307...
        - `q` (Prob. 1->0) = 1 - ((1+0+2) / 6) = 1 - (3/6) = 0.5
        - `pi1` (Prob. pérdida) = 0.2307 / (0.2307 + 0.5) = 0.3157...
        - `pi0` (Prob. recibido) = 1 - 0.3157... = 0.6842...
        - `E` (Long. ráfaga) = 1 / 0.5 = 2.0

        El **mensaje de respuesta** generado sería (valores aproximados):
        ```json
        {
            "type": "PLR_RESPONSE",
            "payload": {
                "p": 0.23076923076923078,
                "q": 0.5,
                "pi1": 0.3157894736842105,
                "pi0": 0.6842105263157895,
                "E": 2.0
            }
        }
        ```
        """
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
        """
        Inicia el bucle principal del servidor para escuchar solicitudes.

        Espera mensajes. Si recibe un 'PLR_REQUEST' válido,
        inicia un nuevo hilo (thread) para procesar la tarea
        ('self.task').
        """
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
        """
        Cierra el socket del servidor.
        """
        self.serviceSocket.close()
