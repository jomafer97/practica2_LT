from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from .popups import ConfigPopup, GridForm
from kivy.app import App
import json
import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from Shared.message_builder import build_message, validate_message
from clientSocket import ClientSocket
from .message_sender import MessageSender

CODEC_QOE_MAP = {
    "Excelente": ("G.711", "G722_64k"),
    "Buena": ("G.729", "G.726", "ilbc_mode_20"),
    "Normal": ("G.723.1", "G.723.1", "G.726", "G.728", "ilbc_mode_30"),
}


class MainPanel(BoxLayout):
    def handle_button_press(self, button_name):
        if button_name == "softphone_origen":
            self.open_softphone_popup()
        elif button_name == "red_transporte":
            self.open_red_popup()
        elif button_name == "softphone_destino":
            self.open_destino_popup()

    def open_softphone_popup(self):
        section = "Softphone (Origen)"
        form = GridForm()

        form.add_widget(Label(text="Calidad Voz (QoE):"))
        qoe_spinner = Spinner(text="Buena", values=("Excelente", "Buena", "Normal"))
        form.add_widget(qoe_spinner)

        form.add_widget(Label(text="Codec (elegido):"))
        codec_spinner = Spinner(text="G.711", values=CODEC_QOE_MAP["Buena"])
        form.add_widget(codec_spinner)

        qoe_spinner.bind(
            text=lambda spinner, text: self.on_qoe_select(
                spinner, text, codec_spinner, section
            )
        )

        qoe_spinner.bind(
            text=lambda instance, value: self._live_update_data(
                instance, value, section, "QoE"
            )
        )
        codec_spinner.bind(
            text=lambda instance, value: self._live_update_data(
                instance, value, section, "Codec"
            )
        )

        form.add_widget(Label(text="Jitter (ms):"))
        jitter_input = TextInput(multiline=False, input_filter="float")
        form.add_widget(jitter_input)

        jitter_input.bind(
            text=lambda instance, value: self._live_update_data(
                instance, value, section, "Jitter (ms)"
            )
        )

        popup = ConfigPopup(
            title_text="Configuración Softphone (Origen)", content_widget=form
        )
        popup.open()

        self._live_update_data(qoe_spinner, qoe_spinner.text, section, "QoE")
        self._live_update_data(codec_spinner, codec_spinner.text, section, "Codec")
        self._live_update_data(jitter_input, jitter_input.text, section, "Jitter (ms)")

    def on_qoe_select(self, spinner_qoe, text_qoe, spinner_codec, section):
        """Actualiza la lista de codecs cuando cambia la QoE."""
        if text_qoe in CODEC_QOE_MAP:
            spinner_codec.values = CODEC_QOE_MAP[text_qoe]
            if spinner_codec.text not in spinner_codec.values:
                spinner_codec.text = spinner_codec.values[0]

        self._live_update_data(spinner_codec, spinner_codec.text, section, "Codec")

    def open_red_popup(self):
        form = GridForm()
        section = "Red de Transporte"

        form.add_widget(Label(text="Encapsulación WAN:"))
        encap_spinner = Spinner(
            text="Ethernet", values=("Ethernet", "Ethernet + 802.1q", "PPPoE")
        )
        form.add_widget(encap_spinner)

        form.add_widget(Label(text="Velocidad Red (Kbps):"))
        velocidad_input = TextInput(multiline=False, input_filter="float")
        form.add_widget(velocidad_input)

        form.add_widget(Label(text="Retardo Red (ms):"))
        retardo_input = TextInput(multiline=False, input_filter="float")
        form.add_widget(retardo_input)

        encap_spinner.bind(
            text=lambda instance, value: self._live_update_data(
                instance, value, section, "Encapsulación"
            )
        )
        velocidad_input.bind(
            text=lambda instance, value: self._live_update_data(
                instance, value, section, "Velocidad Red"
            )
        )
        retardo_input.bind(
            text=lambda instance, value: self._live_update_data(
                instance, value, section, "Retardo Red"
            )
        )

        popup = ConfigPopup(
            title_text="Configuración Red de Transporte", content_widget=form
        )
        popup.open()

        self._live_update_data(
            encap_spinner, encap_spinner.text, section, "Encapsulación"
        )

    def open_destino_popup(self):
        form = GridForm(cols=2)

        app = App.get_running_app()
        if not hasattr(app, "destination_results_widgets"):
            app.destination_results_widgets = {}

        app.destination_results_widgets.clear()

        field_names = [
            "Rt2jit (ms)",
            "Rt1_5jit (ms)",
            "CSI (ms)",
            "Rphy (ms)",
            "Rpaq (ms)",
            "Rs (ms)",
        ]

        for field_name in field_names:
            form.add_widget(Label(text=f"{field_name}:"))

            result_input = TextInput(
                text="---",
                multiline=False,
                disabled=True,
                background_color=(0.2, 0.2, 0.2, 1),
            )
            form.add_widget(result_input)

            app.destination_results_widgets[field_name] = result_input

        popup = ConfigPopup(
            title_text="Softphone (Destino) - Resultados", content_widget=form
        )
        popup.open()

    def open_global_popup(self):
        form = GridForm()
        section = "Parámetros Globales"

        form.add_widget(Label(text="Num. Empresas (Nc):"))
        nc_input = TextInput(multiline=False, input_filter="int")
        form.add_widget(nc_input)

        form.add_widget(Label(text="Líneas / Cliente (Nl):"))
        nl_input = TextInput(multiline=False, input_filter="int")
        form.add_widget(nl_input)

        form.add_widget(Label(text="T. Medio Llamada (Tpll):"))
        tpll_input = TextInput(multiline=False, input_filter="float")
        form.add_widget(tpll_input)

        form.add_widget(Label(text="Prob. Bloqueo (Pb) [GoS]:"))
        pb_input = TextInput(multiline=False, input_filter="float", text="0.01")
        form.add_widget(pb_input)

        form.add_widget(Label(text="Precio / Mbps [Costes]:"))
        precio_mbps_input = TextInput(multiline=False, input_filter="float")
        form.add_widget(precio_mbps_input)

        form.add_widget(Label(text="Precio Máx. Total [Costes]:"))
        precio_max_input = TextInput(multiline=False, input_filter="float")
        form.add_widget(precio_max_input)

        form.add_widget(Label(text="Email para Informe [Paso 8]:"))
        email_input = TextInput(multiline=False)
        form.add_widget(email_input)

        nc_input.bind(
            text=lambda i, v: self._live_update_data(i, v, section, "Num. Empresas")
        )
        nl_input.bind(
            text=lambda i, v: self._live_update_data(i, v, section, "Líneas / Cliente")
        )
        tpll_input.bind(
            text=lambda i, v: self._live_update_data(i, v, section, "T. Medio Llamada")
        )
        pb_input.bind(
            text=lambda i, v: self._live_update_data(i, v, section, "Prob. Bloqueo")
        )
        precio_mbps_input.bind(
            text=lambda i, v: self._live_update_data(i, v, section, "Precio / Mbps")
        )
        precio_max_input.bind(
            text=lambda i, v: self._live_update_data(i, v, section, "Precio Máx. Total")
        )
        email_input.bind(
            text=lambda i, v: self._live_update_data(i, v, section, "Email")
        )

        popup = ConfigPopup(
            title_text="Parámetros Globales, GoS y Costes", content_widget=form
        )
        popup.open()

        self._live_update_data(pb_input, pb_input.text, section, "Prob. Bloqueo")

    def _live_update_data(self, instance, value, section, field):
        """Actualiza el diccionario de resumen en tiempo real."""
        app = App.get_running_app()
        if not hasattr(app, "summary_data"):
            app.summary_data = {}

        if section not in app.summary_data:
            app.summary_data[section] = {}

        if value:
            app.summary_data[section][field] = value
        elif field in app.summary_data[section]:
            del app.summary_data[section][field]

        self._update_summary_display()

    def _update_summary_display(self):
        """Formatea los datos del resumen y los muestra en el Label."""
        app = App.get_running_app()
        if not hasattr(app, "summary_data"):
            return

        summary_str = "RESUMEN DE CONFIGURACIÓN (PASO 1):\n"

        sections_order = [
            "Softphone (Origen)",
            "Red de Transporte",
            "Parámetros Globales",
        ]

        for section in sections_order:
            if section in app.summary_data and app.summary_data[section]:
                summary_str += f"\n{section}:\n"
                for field, value in app.summary_data[section].items():
                    summary_str += f"  - {field}: {value}\n"

        if hasattr(self, "ids") and "panel_resultados" in self.ids:
            self.ids.panel_resultados.text = summary_str
        else:
            print("Error: No se encontró 'panel_resultados' en self.ids")

    def send_data(self):
        app = App.get_running_app()
        summary = getattr(app, "summary_data", {})

        payload = {
            "codec": summary.get("Softphone (Origen)", {}).get("Codec", "G.711"),
            "jitter": float(
                summary.get("Softphone (Origen)", {}).get("Jitter (ms)", 30)
            ),
            "netDelay": float(
                summary.get("Red de Transporte", {}).get("Retardo Red", 0)
            ),
        }

        MessageSender.send("RT_REQUEST", payload)
