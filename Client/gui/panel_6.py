from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from .popups import ConfigPopup, GridForm
from kivy.app import App
import os, sys

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

    def send_email_data(self):
        """
        Recopila TODOS los datos de la app y envía el
        gran payload 'REPORT_REQUEST'.
        """
        app = App.get_running_app()
        summary_data = getattr(app, "summary_data", {})

        try:
            rt_req_raw = summary_data.get("Softphone (Origen)", {})
            erlang_req_raw = summary_data.get("Parámetros Globales", {})
            bw_req_raw = summary_data.get("Parámetros BW", {})
            cost_req_raw = summary_data.get("Parámetros Coste", {})
            plr_req_raw = summary_data.get("Parámetros PLR", {})
            email_req_raw = summary_data.get("Envio Email", {})

            rt_resp_raw = getattr(app, "destination_results_data", {})
            erlang_resp_raw = getattr(app, "erlang_results_data", {})
            bw_resp_raw = getattr(app, "bw_results_data", {})
            cost_resp_raw = getattr(app, "cost_results_data", {})
            plr_resp_raw = getattr(app, "plr_results_data", {})

            payload = {
                "email": email_req_raw.get("email"),
                "RT_REQUEST": {
                    "codec": rt_req_raw.get("Codec"),
                    "jitter": (
                        float(rt_req_raw.get("Jitter (ms)"))
                        if rt_req_raw.get("Jitter (ms)")
                        else None
                    ),
                    "netDelay": (
                        float(rt_req_raw.get("Retardo de Red (ms)"))
                        if rt_req_raw.get("Retardo de Red (ms)")
                        else None
                    ),
                },
                "RT_RESPONSE": {
                    "rt2jit": rt_resp_raw.get("Rt2jit (ms)"),
                    "rt1_5jit": rt_resp_raw.get("Rt1_5jit (ms)"),
                    "csi": rt_resp_raw.get("CSI (ms)"),
                    "rphy": rt_resp_raw.get("Rphy (ms)"),
                    "rpac": rt_resp_raw.get("Rpaq (ms)"),
                    "algD": rt_resp_raw.get(
                        "algD"
                    ),  # (No estaba en tu Panel 1, pero sí en tu JSON)
                },
                "ERLANG_REQUEST": {
                    "numLines": (
                        int(erlang_req_raw.get("Num. Empresas"))
                        if erlang_req_raw.get("Num. Empresas")
                        else None
                    ),
                    "numCalls": (
                        int(erlang_req_raw.get("Líneas / Cliente"))
                        if erlang_req_raw.get("Líneas / Cliente")
                        else None
                    ),
                    "avgDuration": (
                        float(erlang_req_raw.get("T. Medio Llamada"))
                        if erlang_req_raw.get("T. Medio Llamada")
                        else None
                    ),
                    "blockingPercentage": (
                        float(erlang_req_raw.get("Prob. Bloqueo"))
                        if erlang_req_raw.get("Prob. Bloqueo")
                        else None
                    ),
                },
                "ERLANG_RESPONSE": {
                    "Erlangs": erlang_resp_raw.get("Erlangs"),
                    "maxLines": erlang_resp_raw.get("maxLines"),
                },
                # --- El resto de paneles (sigue este patrón) ---
                "BW_REQUEST": {
                    "codec": bw_req_raw.get("Codec"),  # (Nombre de campo asumido)
                    "pppoe": bw_req_raw.get("pppoe"),  # (Nombre de campo asumido)
                    "vlan8021q": bw_req_raw.get(
                        "vlan8021q"
                    ),  # (Nombre de campo asumido)
                    "reservedBW": (
                        float(bw_req_raw.get("reservedBW"))
                        if bw_req_raw.get("reservedBW")
                        else None
                    ),  # (Nombre de campo asumido)
                    "totalCalls": (
                        int(bw_req_raw.get("totalCalls"))
                        if bw_req_raw.get("totalCalls")
                        else None
                    ),  # (Nombre de campo asumido)
                },
                "BW_RESPONSE": bw_resp_raw,  # Asumimos que la respuesta ya tiene la estructura correcta
                "COST_REQUEST": {
                    # (Completa con los campos de tu panel de Costes)
                    "Pmax": (
                        float(cost_req_raw.get("Pmax"))
                        if cost_req_raw.get("Pmax")
                        else None
                    ),  # (Nombre de campo asumido)
                    "callBW": cost_req_raw.get(
                        "callBW"
                    ),  # (Esto vendrá de BW_RESPONSE)
                    "BWst": cost_req_raw.get("BWst"),  # (Esto vendrá de BW_RESPONSE)
                },
                "COST_RESPONSE": cost_resp_raw,  # Asumimos que la respuesta ya tiene la estructura correcta
                "PLR_REQUEST": {
                    "bitstream": plr_req_raw.get(
                        "bitstream"
                    )  # (Nombre de campo asumido)
                },
                "PLR_RESPONSE": plr_resp_raw,  # Asumimos que la respuesta ya tiene la estructura correcta
            }

            # --- 4. Validación de Email ---
            if not payload["email"]:
                self._show_error_popup(
                    "El email no puede estar vacío. Configúralo primero."
                )
                return

            # --- 5. Envío ---
            MessageSender.send(
                "REPORT_REQUEST", payload, callback=self._on_email_response
            )

        except (ValueError, KeyError, TypeError) as e:
            self._show_error_popup(
                f"Error al construir el informe: {str(e)}. Faltan datos de pasos anteriores."
            )

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
