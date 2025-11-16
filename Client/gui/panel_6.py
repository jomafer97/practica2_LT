from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from .popups import ConfigPopup, GridForm, InfoPopup
from kivy.app import App
import os, sys
import json  # <-- AÑADIDO
import traceback  # <-- AÑADIDO

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from .message_sender import MessageSender

EMAIL_PARAMS_FIELDS = [
    ("Introduzca su email", "str", "", "email"),  # Valor por defecto vacío
]


class Step6Panel(BoxLayout):
    """Panel para Paso 6: Simulación REPORT (REPORT_REQUEST)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 10
        self.spacing = 10
        self.section = "Envio Email"

    def handle_button_press(self, button_name):
        if button_name == "configurar_email":
            self.open_config_popup()
        if button_name == "question_6":
            self.open_question6_popup()
    
    def open_question6_popup(self):
        """ Abre popup con la información de este paso """
        info_text_1 =("Añadir información del envío del correo electrónico")

        popup = InfoPopup(
            title="Información Paso 8",
            info_text = info_text_1
        )
        popup.open()

    def open_config_popup(self):
        """Abre popup para configurar Parámetros de REPORT."""
        form = GridForm()

        for label_text, input_type, default, field_name in EMAIL_PARAMS_FIELDS:
            widget = self._create_input_field(form, label_text, default, input_type)
            widget.bind(
                text=lambda i, v, lt=label_text: self._on_field_change(i, v, lt)
            )
            # Inicializar valor por defecto si no existe
            app = App.get_running_app()
            email_data = getattr(app, "summary_data", {}).get(self.section, {})
            current_email = email_data.get("email", default)
            widget.text = current_email
            self._on_field_change(widget, current_email, label_text)

        popup = ConfigPopup(
            title_text="Configurar Email para Informe", content_widget=form
        )
        popup.open()

    # --- ESTA ES LA FUNCIÓN CORREGIDA ---
    def send_email_data(self):
        """
        Recopila TODOS los datos de la app y envía el
        gran payload 'REPORT_REQUEST'.
        
        ESTA VERSIÓN ESTÁ CORREGIDA para buscar los datos
        en las 'cajas' (summary_data y results_data) correctas.
        """
        app = App.get_running_app()
        summary_data = getattr(app, "summary_data", {})

        try:
            # --- 1. Rescatar todos los DATOS DE ENTRADA (REQUESTS) ---
            rt_req_raw = summary_data.get("Softphone (Origen)", {})
            erlang_req_raw = summary_data.get("Parámetros Globales", {})
            bw_req_raw = summary_data.get("Parámetros de Tráfico", {}) # <-- Nombre arreglado
            cost_req_raw = summary_data.get("Parámetros de Costes", {}) # <-- Nombre arreglado
            plr_req_raw = summary_data.get("Parámetros de PLR", {})    # <-- Nombre arreglado
            email_req_raw = summary_data.get("Envio Email", {})

            # --- 2. Rescatar todas las RESPUESTAS (RESULTS) ---
            rt_resp_raw = getattr(app, "destination_results_data", {})
            erlang_resp_raw = getattr(app, "erlang_results_data", {})
            bw_resp_raw = getattr(app, "bw_results_data", {})
            cost_resp_raw = getattr(app, "cost_results_data", {})
            plr_resp_raw = getattr(app, "plr_results_data", {})

            
            # --- 3. Procesar datos que necesitan lógica (como en panel_3.py) ---
            
            # Lógica de BW (Paso 3)
            encap_str = bw_req_raw.get("Encapsulación", "Ethernet")
            bw_pppoe = "PPPoE" in encap_str
            bw_vlan8021q = "802.1q" in encap_str
            bw_reserved = float(bw_req_raw.get("BW Reservado", 0.2))

            # --- 4. Construir el PAYLOAD final ---
            payload = {
                "email": email_req_raw.get("email"),
                
                # --- PASO 1 ---
                "RT_REQUEST": {
                    "codec": rt_req_raw.get("Codec"),
                    "jitter": float(rt_req_raw.get("Jitter (ms)")) if rt_req_raw.get("Jitter (ms)") else None,
                    "netDelay": float(rt_req_raw.get("Retardo de Red (ms)")) if rt_req_raw.get("Retardo de Red (ms)") else None,
                },
                "RT_RESPONSE": rt_resp_raw, 

                # --- PASO 2 ---
                "ERLANG_REQUEST": {
                    "numLines": int(erlang_req_raw.get("Num. Empresas")) if erlang_req_raw.get("Num. Empresas") else None,
                    "numCalls": int(erlang_req_raw.get("Líneas / Cliente")) if erlang_req_raw.get("Líneas / Cliente") else None,
                    "avgDuration": float(erlang_req_raw.get("T. Medio Llamada")) if erlang_req_raw.get("T. Medio Llamada") else None,
                    "blockingPercentage": float(erlang_req_raw.get("Prob. Bloqueo")) if erlang_req_raw.get("Prob. Bloqueo") else None,
                },
                "ERLANG_RESPONSE": erlang_resp_raw,

                # --- PASO 3 ---
                "BW_REQUEST": {
                    # Datos rescatados de otros pasos
                    "codec": rt_req_raw.get("Codec"), 
                    "totalCalls": erlang_resp_raw.get("maxLines"),
                    # Datos procesados de este paso
                    "pppoe": bw_pppoe,
                    "vlan8021q": bw_vlan8021q,
                    "reservedBW": bw_reserved,
                },
                "BW_RESPONSE": bw_resp_raw,

                # --- PASO 4 ---
                "COST_REQUEST": {
                    # Dato de este paso
                    "Pmax": float(cost_req_raw.get("Pmax")) if cost_req_raw.get("Pmax") else None,
                    # Datos rescatados de la respuesta del Paso 3
                    "callBW": {
                        "RTP": bw_resp_raw.get("uncompressed", {}).get("callBW"),
                        "cRTP": bw_resp_raw.get("compressed", {}).get("callBW")
                    },
                    "BWst": {
                        "RTP": bw_resp_raw.get("uncompressed", {}).get("BWst"),
                        "cRTP": bw_resp_raw.get("compressed", {}).get("BWst")
                    }
                },
                "COST_RESPONSE": cost_resp_raw,
                
                # --- PASO 5 ---
                "PLR_REQUEST": {
                    "bitstream": plr_req_raw.get("Bitstream")
                },
                "PLR_RESPONSE": plr_resp_raw
            }

            # --- 5. Validación de Email ---
            if not payload["email"]:
                self._show_error_popup("El email no puede estar vacío. Configúralo primero.")
                return

            # --- 6. Envío ---
            MessageSender.send(
                "REPORT_REQUEST", payload, callback=self._on_email_response
            )
            
            # (Opcional) Imprime el payload que SÍ se está enviando
            print("--- DEBUG (PANEL 6): Enviando este payload al servidor ---")
            print(json.dumps(payload, indent=2))
            # ---------------------------------------------------------------


        except (ValueError, KeyError, TypeError, AttributeError) as e:
            error_msg = f"Error al construir el informe: {str(e)}. Faltan datos de pasos anteriores. Asegúrate de pulsar 'Calcular' en TODOS los pasos."
            print(f"--- ERROR (PANEL 6): {error_msg}")
            self._show_error_popup(error_msg)
            # Imprime el traceback en la consola del cliente para depurar
            traceback.print_exc()
    # --- FIN DE LA FUNCIÓN CORREGIDA ---


    def _on_email_response(self, response):
        """Callback para procesar la respuesta REQUEST_RESPONSE."""
        try:
            email_data = (
                response if isinstance(response, dict) else {"status": str(response)}
            )
            app = App.get_running_app()
            app.email_results_data = email_data

            self.show_email_results()
        except Exception as e:
            self._show_error_popup(f"Error procesando respuesta REPORT: {str(e)}")

    def show_email_results(self):
        """Muestra un popup de éxito/fracaso del envío del informe."""
        app = App.get_running_app()
        form = GridForm(cols=1)

        results = getattr(
            app,
            "email_results_data",
            {"status": "Respuesta desconocida"},
        )

        form.add_widget(Label(text="Informe enviado al servidor."))
        form.add_widget(
            Label(text=f"Respuesta del servidor: {results.get('status', str(results))}")
        )

        popup = ConfigPopup(title_text="Informe Enviado", content_widget=form)
        popup.open()

    def _create_input_field(self, form, label_text, default_value, input_type):
        form.add_widget(Label(text=label_text))
        widget = TextInput(multiline=False, text=default_value)
        if input_type == "float":
            widget.input_filter = "float"
        elif input_type == "int":
            widget.input_filter = "int"
        form.add_widget(widget)
        return widget

    def _on_field_change(self, instance, value, label_text):
        field_name = self._get_field_name(label_text)
        if field_name:
            self._update_data(field_name, value)
            self._update_summary_display()

    def _get_field_name(self, label_text):
        for label, _, _, field_name in EMAIL_PARAMS_FIELDS:
            if label == label_text:
                return field_name
        return None

    def _update_data(self, field_name, value):
        app = App.get_running_app()
        if not hasattr(app, "summary_data"):
            app.summary_data = {}
        if self.section not in app.summary_data:
            app.summary_data[self.section] = {}

        if value:
            app.summary_data[self.section][field_name] = value
        elif field_name in app.summary_data[self.section]:
            del app.summary_data[self.section][field_name]

    def _update_summary_display(self):
        app = App.get_running_app()
        data = getattr(app, "summary_data", {}).get(self.section, {})

        if not data:
            summary_str = "Email no configurado."
        else:
            summary_str = f"{self.section.upper()}:\n"
            for field_name, value in data.items():
                summary_str += f"   • {field_name}: {value}\n"

        if hasattr(self, "ids") and "panel_resultados" in self.ids:
            self.ids.panel_resultados.text = summary_str

    def _show_error_popup(self, message):
        form = GridForm()
        form.add_widget(Label(text=f"Error: {message}"))
        popup = ConfigPopup(title_text="Error de Entrada", content_widget=form)
        popup.open()