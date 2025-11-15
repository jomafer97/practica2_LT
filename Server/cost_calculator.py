from serverSocket import ServerSocket
from Shared.message_builder import build_message, validate_message
import threading

COST_MBPS = 100.0
class Cost_calculator_service:
    """
    Servicio de red para calcular el coste de ancho de banda (BW).

    Escucha peticiones en un socket, recibe datos de BW (RTP y cRTP)
    y un presupuesto máximo (Pmax). Calcula el coste total basado en
    un precio fijo por Mbps (COST_MBPS) y determina si el escenario es
    válido y cuántas llamadas son posibles dentro de ese presupuesto.
    """
    def __init__(self, IP, logger):
        """
        Inicializa el servicio de calculadora de Coste.

        :param logger: Una instancia de un logger para registrar los eventos del servicio.
        :type logger: logging.Logger
        """
        self.serviceSocket = ServerSocket(IP, 32006)
        self.logger = logger
        self.ID = "COST_CALCULATOR"

    def task(self, message, addr):
        """
        Procesa una solicitud de cálculo de coste y envía la respuesta.

        Esta función se ejecuta en un hilo separado. Extrae los datos
        de ancho de banda (BWst, callBW) y el presupuesto (Pmax) del
        mensaje.

        Calcula el coste para RTP y cRTP, y determina la validez
        (si el coste está dentro del presupuesto) y el número de
        llamadas posibles para cada escenario.

        Maneja internamente excepciones generales durante el cálculo.

        :param message: El mensaje de solicitud deserializado (dict)
                        que debe contener 'callBW', 'BWst' y 'Pmax'.
        :type message: dict
        :param addr: La dirección (IP, puerto) del cliente que envió la solicitud.
        :type addr: tuple

        Ejemplo de uso:

        Asumiendo `COST_MBPS = 100.0`.

        Un **mensaje de entrada (message)** tendría esta estructura:
        ```json
        {
            "callBW": {
                "RTP": 112000.0,
                "cRTP": 94000.0
            },
            "BWst": {
                "RTP": 5.6,
                "cRTP": 4.7
            },
            "Pmax": 500.0
        }
        ```

        **Cálculo (simplificado):**
        - Coste RTP = 5.6 Mbps * 100.0 = 560.0 (No válido, > 500.0)
        - Coste cRTP = 4.7 Mbps * 100.0 = 470.0 (Válido, <= 500.0)
        - Posibles llamadas RTP = 44 (calculado en base a Pmax)
        - Posibles llamadas cRTP = 50 (calculado en base a BWst/callBW)

        El **mensaje de respuesta** generado sería:
        ```json
        {
            "type": "COST_RESPONSE",
            "payload": {
                "mbpsCost": 100.0,
                "RTP": {
                    "valid": false,
                    "possibleCalls": 44
                },
                "cRTP": {
                    "valid": true,
                    "possibleCalls": 50
                }
            }
        }
        ```
        """
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
        """
        Inicia el bucle principal del servidor para escuchar solicitudes.

        Es un bucle infinito que espera mensajes en el socket.
        Cuando se recibe un mensaje, intenta validarlo como 'COST_REQUEST'.
        Si es válido, inicia un nuevo hilo (thread) para procesarlo
        llamando a 'self.task'.
        Si la validación falla o falta el mensaje, captura la excepción,
        registra el error y envía un mensaje de error al cliente.
        """
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
        """
        Cierra el socket del servidor y registra el evento.
        """
        self.serviceSocket.close()
        self.logger.info("COST CALCULATION REQUEST SERVICE: Socket closed")
