import threading, smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from serverSocket import ServerSocket
from Shared.message_builder import build_message, validate_message

# --- LIBRERÍAS PDF ---
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# --- CREDENTIALS ---
SENDER_EMAIL = "josedavidalias@correo.ugr.es"
SENDER_PASSWORD = "JdAs04"
SMTP_SERVER = "correo.ugr.es"
SMTP_PORT = 587
# --------------------

class Report_creator_service:
    def __init__(self, IP, logger):
        self.serviceSocket = ServerSocket(IP, 32008)
        self.logger = logger
        self.ID = "REPORT_CREATOR"

    def _generate_pdf_report(self, report_text, filename="voip_report.pdf"):
        """Genera un archivo PDF a partir del texto plano."""
        try:
            c = canvas.Canvas(filename, pagesize=A4)
            width, height = A4

            # --- Configuración de Fuentes ---
            FONT_TITULO = "Helvetica-Bold"
            FONT_CUERPO = "Helvetica"
            FONT_FORMULA = "Courier"

            # --- Márgenes y Espaciado ---
            MARGIN_X = 50
            MARGIN_TOP = height - 50
            MARGIN_BOTTOM = 50
            LINE_HEIGHT = 14

            y_position = MARGIN_TOP

            lines = report_text.split('\n')

            for line in lines:
                # --- Lógica de Formato ---

                # 1. Si la línea es un separador '==='
                if line.startswith("==="):
                    y_position -= (LINE_HEIGHT / 2)
                    c.setStrokeColorRGB(0.6, 0.6, 0.6)
                    c.line(MARGIN_X, y_position, width - MARGIN_X, y_position)
                    y_position -= (LINE_HEIGHT * 1.5)

                # 2. Si es el título principal
                elif "INFORME DE CALCULO VoIP" in line:
                    c.setFont(FONT_TITULO, 18)
                    c.drawCentredString(width / 2, y_position, line.strip())
                    y_position -= (LINE_HEIGHT * 2.5)

                # 3. Si es un título de sección "--- ... ---"
                elif line.strip().startswith("---") and line.strip().endswith("---"):
                    y_position -= (LINE_HEIGHT / 2)
                    c.setFont(FONT_TITULO, 14)
                    c.setFillColorRGB(0.1, 0.1, 0.4)
                    c.drawString(MARGIN_X, y_position, line.strip().replace("---", ""))
                    c.setFillColorRGB(0, 0, 0)
                    y_position -= (LINE_HEIGHT * 1.5)

                # 4. Si es una fórmula o línea con resultado (contiene '=')
                elif "=" in line:
                    c.setFont(FONT_FORMULA, 10)
                    c.drawString(MARGIN_X + 15, y_position, line.strip())
                    y_position -= LINE_HEIGHT

                # 5. Texto normal
                else:
                    c.setFont(FONT_CUERPO, 10)
                    c.drawString(MARGIN_X, y_position, line.strip())
                    y_position -= LINE_HEIGHT

                # --- Salto de Página Automático ---
                if y_position < MARGIN_BOTTOM:
                    c.showPage()
                    y_position = MARGIN_TOP
                    c.setFont(FONT_CUERPO, 10)

            # --- Guardar el PDF ---
            c.save()
            self.logger.info(f"{self.ID}: PDF report generated: {filename}")
            return filename

        except Exception as e:
            self.logger.error(f"{self.ID}: Error generating PDF report: {e}")
            return None

    def _send_email_with_pdf(self, receiver_email, subject, pdf_filename):
        """Envía el email con el PDF adjunto."""
        if not receiver_email:
            self.logger.warning(f"{self.ID}: Destination mail not reachable.")
            return

        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = subject

        # 1. Cuerpo del mensaje
        msg.attach(MIMEText("Estimado usuario,\n\n Se adjunta el informe detallado de los cálculos que ha realizado con la aplicación.\n\nUn saludo.", 'plain'))

        # 2. Adjuntar el PDF
        try:
            with open(pdf_filename, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(pdf_filename)}")
            msg.attach(part)
        except FileNotFoundError:
            self.logger.error(f"{self.ID}: Generated PDF file not found for attachment.")
            return

        # 3. Conexión y Envío
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
            self.logger.info(f"{self.ID}: PDF report successfully sent to {receiver_email}.")

        except Exception as e:
            self.logger.error(f"{self.ID}: Error sending report: {e}")

    def generate_plain_text_report(self, report_request_data):
        """
        Genera el informe detallado en texto plano, insertando valores de REQUEST y RESPONSE.
        """

        # Extracción de datos
        rt_req = report_request_data["RT_REQUEST"]
        erlang_req = report_request_data["ERLANG_REQUEST"]
        bw_req = report_request_data["BW_REQUEST"]
        cost_req = report_request_data["COST_REQUEST"]
        plr_req = report_request_data["PLR_REQUEST"]

        rt_res = report_request_data["RT_RESPONSE"]
        erlang_res = report_request_data["ERLANG_RESPONSE"]
        bw_res = report_request_data["BW_RESPONSE"]
        cost_res = report_request_data["COST_RESPONSE"]
        plr_res = report_request_data["PLR_RESPONSE"]

        reporte = "========================================================\n"
        reporte += f"             INFORME DE CALCULO VoIP\n"
        reporte += "========================================================\n\n"

        # --- QoS (Retardo Rt) ---
        reporte += "--- Retardo Boca a Oido ---\n"
        reporte += "Rt caso peor = CSI + R.Paq. + R.Fisico + 2 * Jitter\n"
        reporte += f"Rt caso peor = {rt_res['csi']} + {rt_res['rpac']} + {rt_res['rphy']} + 2 * {rt_req['jitter']} = {rt_res['rt2jit']} ms \n"
        reporte += "Rt caso ajustado = CSI + R.Paq. + R.Fisico + 2 * Jitter\n"
        reporte += f"Rt caso ajustado = {rt_res['csi']} + {rt_res['rpac']} + {rt_res['rphy']} + 1.5 * {rt_req['jitter']} = {rt_res['rt1_5jit']} ms\n"

        # --- GoS (Erlangs) ---
        reporte += "--- GoS (Grado de Servicio) ---\n"
        reporte += "BHT = (Ncanales * Nllamadas * Tpllamada(seg)) / 3600 seg \n"
        reporte += f"BHT = ({erlang_req['numLines']} * {erlang_req['numCalls']} * {erlang_req['avgDuration']})/ 3600 seg = {erlang_res['Erlangs']} erlangs\n"
        reporte += "Max. lineas = Erlang B (Erlangs, Pbloqueo)\n"
        reporte += f"Max. lineas = Erlang B ({erlang_res['Erlangs']},{erlang_req['blockingPercentage']}) = {erlang_res['maxLines']} lineas\n"

        # --- Ancho de Banda (BW) ---
        reporte += "--- Ancho de Banda ---\n"
        reporte += "BW llamada = ((Tam.Datos + Tam.Cabeceras) * paq.p.segundo) * (1+ BW reservado)\n"

        reporte += f"BW llamada RTP = ({bw_res['uncompressed']['PacketLength']} * {bw_res['pps']}) * (1 + {bw_req['reservedBW']}) = {bw_res['uncompressed']['callBW']} bps\n"
        reporte += f"BW llamada cRTP = ({bw_res['compressed']['packetLength']} * {bw_res['pps']}) * (1 + {bw_req['reservedBW']}) = {bw_res['compressed']['callBW']} bps\n"

        reporte += "BW Total RTP = Llamadas Totales * BW llamada RTP \n"
        reporte += f"BW Total RTP = {bw_req['totalCalls']} * {bw_res['uncompressed']['callBW']} = {bw_res['uncompressed']['BWst']} Mbps\n"
        reporte += "BW Total cRTP = Llamadas Totales * BW llamada cRTP \n"
        reporte += f"BW Total cRTP = {bw_req['totalCalls']} * {bw_res['compressed']['callBW']} = {bw_res['compressed']['BWst']} Mbps\n"

        # --- Costes (€) ---
        reporte += "--- Costes ---\n"
        reporte += f"Precio Maximo a Pagar (Pmax) = {cost_req['Pmax']} euros\n"
        reporte += "Coste Mbps = 100 euros\n"
        reporte += f"Coste RTP = {cost_req['BWst']['RTP']} * 100 euros\n"
        reporte += f"Coste cRTP = {cost_req['BWst']['cRTP']} * 100 euros\n"
        reporte += f"Llamadas Posibles RTP = {cost_res['RTP']['possibleCalls']} llamadas\n"
        reporte += f"Llamadas Posibles cRTP = {cost_res['cRTP']['possibleCalls']} llamadas\n"

        # --- PLR (Pérdida de Paquetes) ---
        reporte += "--- PLR (Modelo de Markov) ---\n"
        reporte += f"Secuencia Binaria = {plr_req['bitstream']}\n"
        reporte += f"p = {plr_res['p']}\n"
        reporte += f"q = {plr_res['q']}\n"
        reporte += f"E = {plr_res['E']}\n"
        reporte += f"pi1 = {plr_res['pi1']}\n"
        reporte += f"pi0 = {plr_res['pi0']}\n"

        reporte += "\n========================================================\n"
        return reporte

    def task(self, message, addr):
        pdf_filename = None
        try:
            self.logger.info(f"{self.ID}: Message received from client {addr}:\n{message}")

            # 1. Extracción
            report_request_data = message

            # 2. Generación del Informe
            plain_report_text = self.generate_plain_text_report(report_request_data)

            # 3. Generación del PDF
            pdf_filename = self._generate_pdf_report(plain_report_text)

            # 4. Envío del Email con PDF adjunto
            receiver_email = report_request_data.get("email")

            if pdf_filename and receiver_email:
                 self._send_email_with_pdf(
                    receiver_email,
                    subject=f"Informe Practica 2 resultados VoIP",
                    pdf_filename=pdf_filename
                )

            # 5. Construcción de la Respuesta
            response = build_message(
                "REPORT_RESPONSE",
                report=plain_report_text
            )
            self.logger.info(f"{self.ID}: Task finished and response ready.")

        except Exception as e:
            self.logger.error(f"{self.ID}: Error of client {addr}: {e}")
            response = build_message("ERROR", source=self.ID, error=str(e))

        finally:

            if pdf_filename and os.path.exists(pdf_filename):
                try:
                    os.remove(pdf_filename)
                    self.logger.info(f"{self.ID}: Cleaned up PDF: {pdf_filename}")
                except Exception as e:
                    self.logger.error(f"{self.ID}: Failed to remove PDF: {e}")


        if self.serviceSocket:
            self.serviceSocket.send_message(response, addr)

    def start(self):
        while True:
            message, addr = self.serviceSocket.recv_message(8192)

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
