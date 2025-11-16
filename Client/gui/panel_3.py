from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from .popups import ConfigPopup, GridForm, InfoPopup
from kivy.app import App
import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from .message_sender import MessageSender

TRAFFIC_PARAMS_FIELDS = [
    (
        "Encapsulación L2:",
        "spinner",
        "Ethernet",
        ("Ethernet", "Ethernet + 802.1q", "PPPoE", "PPP + 802.1q"),
        "Encapsulación",
    ),
    ("BW Reservado (0-1):", "float", "0.2", "BW Reservado"),
]


class Step3Panel(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 10
        self.spacing = 10
        self.section = "Parámetros de Tráfico"

    def handle_button_press(self, button_name):
        if button_name == "softphone_destino":
            self.show_bw_results()
        if button_name == "question_3":
            self.open_question3_popup()

    def open_question3_popup(self):
        """ Abre popup con la información de este paso """
        info_text_1 =("Para calculary mostrar el ancho de banda será necesario introducir el tipo de encapsulación"
        "deseada, así como el BW Reservado")

        popup = InfoPopup(
            title="Información Paso 5",
            info_text = info_text_1
        )
        popup.open()

    def open_config_popup(self):
        form = GridForm()

        for label_text, input_type, default, *rest in TRAFFIC_PARAMS_FIELDS:
            field_name = rest[-1]

            if input_type == "spinner":
                options = rest[0]
                widget = self._create_spinner(form, label_text, default, options)
            else:
                widget = self._create_input_field(form, label_text, default, input_type)

            widget.bind(
                text=lambda i, v, lt=label_text: self._on_field_change(i, v, lt)
            )
            self._on_field_change(widget, default, label_text)

        popup = ConfigPopup(
            title_text="Parámetros de Tráfico - BW", content_widget=form
        )
        popup.open()

    def send_traffic_data(self):
        app = App.get_running_app()
        summary = getattr(app, "summary_data", {})
        traffic_data = summary.get(self.section, {})

        try:
            codec = summary.get("Softphone (Origen)", {}).get("Codec", "G.711")
            total_calls = getattr(app, "erlang_results_data", {}).get("maxLines", 0)

            if total_calls == "---" or total_calls == 0:
                self._show_error_popup(
                    "No se han calculado las 'maxLines' del Paso 2 (Erlang)."
                )
                return

            encap_str = traffic_data.get("Encapsulación", "Ethernet")
            pppoe = "PPP" in encap_str
            vlan8021q = "802.1q" in encap_str
            reserved_bw = float(traffic_data.get("BW Reservado", 0.2))

            payload = {
                "codec": codec,
                "pppoe": pppoe,
                "vlan8021q": vlan8021q,
                "reservedBW": reserved_bw,
                "totalCalls": int(total_calls),
            }

            MessageSender.send("BW_REQUEST", payload, callback=self._on_bw_response)

        except (ValueError, KeyError, AttributeError) as e:
            self._show_error_popup(
                f"Valores inválidos o faltan datos de pasos anteriores: {str(e)}"
            )

    def _on_bw_response(self, response):
        try:
            bw_data = response if isinstance(response, dict) else {}
            app = App.get_running_app()
            app.bw_results_data = bw_data
            self.show_bw_results()
        except Exception as e:
            self._show_error_popup(f"Error procesando respuesta BW: {str(e)}")

    def show_bw_results(self):
        app = App.get_running_app()
        form = GridForm(cols=2)
        results = getattr(app, "bw_results_data", {})

        def add_result(form_widget, key, value, indent=""):
            if key == "packetLength":
                value_str = f"{value} bytes"
            elif key == "callBW":
                value_str = f"{value:.2f} bps"
            elif key == "BWst":
                value_str = f"{value:.3f} Mbps"
            elif key == "pps":
                value_str = f"{value} pps"
            else:
                value_str = str(value)

            form_widget.add_widget(Label(text=f"{indent}{key}:"))

            if isinstance(value, dict):
                form_widget.add_widget(Label(text=""))
                for k, v in value.items():
                    add_result(form_widget, k, v, indent="    ")
            else:
                form_widget.add_widget(
                    Label(text=value_str, color=(1, 1, 1, 1), size_hint_x=1)
                )

        if not results:
            form.add_widget(Label(text="Resultados BW:"))
            form.add_widget(Label(text="---", color=(1, 1, 1, 1), size_hint_x=1))
        else:
            for key, value in results.items():
                add_result(form, key, value)

        popup = ConfigPopup(
            title_text="Softphone (Destino) - Resultados BW", content_widget=form
        )
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

    def _create_spinner(self, form, label_text, default, values):
        form.add_widget(Label(text=label_text))
        widget = Spinner(text=default, values=values)
        form.add_widget(widget)
        return widget

    def _on_field_change(self, instance, value, label_text):
        field_name = self._get_field_name(label_text)
        if field_name:
            self._update_data(field_name, value)
            self._update_summary_display()

    def _get_field_name(self, label_text):
        for field_tuple in TRAFFIC_PARAMS_FIELDS:
            if field_tuple[0] == label_text:
                return field_tuple[-1]
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
            summary_str = "Sin parámetros configurados aún."
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
