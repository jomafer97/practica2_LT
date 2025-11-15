from serverSocket import ServerSocket
from Shared.message_builder import build_message, validate_message
import threading


class Erlang_calculator_service:
    """
    Servicio de red para cálculos de telefonía usando Erlang.

    Escucha en un socket peticiones para calcular la intensidad
    de tráfico (en Erlangs) y el número de líneas necesarias
    para un grado de servicio (GoS) específico, basándose en la
    fórmula de Erlang B.
    """
    def __init__(self, IP, logger):
        """
        Inicializa el servicio de calculadora de Erlang.

        :param logger: Una instancia de un logger para registrar los eventos del servicio.
        :type logger: logging.Logger
        """
        self.serviceSocket = ServerSocket(IP, 32004)
        self.logger = logger
        self.ID = "ERLANG_CALCULATOR"

    def erlang_b(self, E, N):
        """
        Calcula la probabilidad de bloqueo usando la fórmula Erlang B.

        Esta es una implementación iterativa de la fórmula de Erlang B
        que calcula el Grado de Servicio (GoS) o probabilidad de que
        todas las N líneas estén ocupadas para un tráfico E.

        :param E: La intensidad de tráfico ofrecida (en Erlangs).
        :type E: float
        :param N: El número de líneas o canales disponibles.
        :type N: int
        :returns: La probabilidad de bloqueo (B).
        :rtype: float
        """
        B = 1.0
        for n in range(1, N+1):
            B = (E * B) / (n + E * B)
        return B

    def needed_lines(self, A, blockingPercentage):
        """
        Calcula el número de líneas (N) necesarias para un tráfico (A)
        y un porcentaje de bloqueo objetivo.

        Itera incrementando el número de líneas N hasta que la
        probabilidad de bloqueo calculada por `erlang_b` sea
        menor o igual que el porcentaje de bloqueo deseado.

        :param A: La intensidad de tráfico (en Erlangs) que se
                  desea manejar.
        :type A: float
        :param blockingPercentage: El porcentaje de bloqueo máximo
                                  aceptable (p.ej., 0.01 para 1%).
        :type blockingPercentage: float
        :returns: El número mínimo de líneas (N) necesarias.
        :rtype: int
        """
        N = 1
        while True:
            B = self.erlang_b(A, N)
            if B <= blockingPercentage:
                return N
            N += 1


    def task(self, message, addr):
        """
        Procesa una solicitud de cálculo Erlang y envía la respuesta.

        Esta función se ejecuta en un hilo separado.
        Extrae los parámetros del mensaje, calcula la intensidad
        de tráfico (A) y luego determina las líneas máximas
        (maxLines) necesarias usando 'needed_lines'.

        :param message: El mensaje de solicitud (dict) que debe
                        contener 'numLines', 'numCalls', 'avgDuration',
                        y 'blockingPercentage'.
        :type message: dict
        :param addr: La dirección (IP, puerto) del cliente.
        :type addr: tuple

        Ejemplo de uso:

        Un **mensaje de entrada (message)** tendría esta estructura:
        ```json
        {
            "numLines": 100,
            "numCalls": 10,
            "avgDuration": 180,
            "blockingPercentage": 0.01
        }
        ```

        **Cálculo (simplificado):**
        - `A` (Tráfico) = (100 * 10 * 180) / 3600 = 50.0 Erlangs
        - `maxLines` = needed_lines(50.0, 0.01) (resulta en 63)

        El **mensaje de respuesta** generado sería:
        ```json
        {
            "type": "ERLANG_RESPONSE",
            "payload": {
                "Erlangs": 50.0,
                "maxLines": 63
            }
        }
        ```
        """
        try:
            self.logger.info(f"{self.ID}: Message received from client {addr}:\n{message}")

            numLines = message ["numLines"]
            numCalls = message["numCalls"]
            avgDuration = message["avgDuration"]
            blockingPercentage = message["blockingPercentage"]

            A = (numLines*numCalls*avgDuration)/3600
            maxLines = self.needed_lines(A, blockingPercentage)

            response = build_message(
                "ERLANG_RESPONSE",
                Erlangs=A,
                maxLines= maxLines
            )

        except Exception as e:
            self.logger.error(f"{self.ID}: from client {addr}, {str(e)}")
            response = build_message("ERROR", source=self.ID, error=str(e))

        self.serviceSocket.send_message(response, addr)

    def start(self):
        """
        Inicia el bucle principal del servidor para escuchar solicitudes.

        Es un bucle infinito que espera mensajes. Si recibe un
        mensaje 'ERLANG_REQUEST' válido, inicia un nuevo hilo
        para procesar la tarea ('self.task').
        """
        while True:
            message, addr = self.serviceSocket.recv_message(1024)

            try:
                validate_message(message, "ERLANG_REQUEST")

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
