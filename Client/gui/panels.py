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

# Mapeo de QoE a opciones de codec disponibles
CODEC_QOE_MAP = {
    "Excelente": ("G.711", "G722_64k"),
    "Buena": ("G.729", "G.726", "ilbc_mode_20"),
    "Normal": ("G.723.1", "G.723.1", "G.726", "G.728", "ilbc_mode_30"),
}

# Mapeo de respuesta del servidor a nombres de campos
RT_RESPONSE_MAPPING = {
    "rt2jit": "Rt2jit (ms)",
    "rt1_5jit": "Rt1_5jit (ms)",
    "csi": "CSI (ms)",
    "rphy": "Rphy (ms)",
    "rpac": "Rpaq (ms)",
}


class MainPanel(BoxLayout):
    """Panel para Paso 1: Configuración de Softphone Origen, Red Transporte y Softphone Destino."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.section_softphone = "Softphone (Origen)"
        self.section_red = "Red de Transporte"

    def handle_button_press(self, button_name):
        """Dispatch de botones a sus métodos correspondientes."""
        actions = {
            "softphone_origen": self.open_softphone_popup,
            "red_transporte": self.open_red_popup,
            "softphone_destino": self.open_destino_popup,
        }
        if button_name in actions:
            actions[button_name]()

    def open_softphone_popup(self):
        """Abre popup para configurar Softphone Origen (QoE, Codec, Jitter)."""
        form = GridForm()
        
        qoe_spinner = self._create_spinner(form, "Calidad Voz (QoE):", "Buena", ("Excelente", "Buena", "Normal"))
        codec_spinner = self._create_spinner(form, "Codec (elegido):", "G.711", CODEC_QOE_MAP["Buena"])
        jitter_input = self._create_input(form, "Jitter (ms):", "", "float")
        
        qoe_spinner.bind(text=lambda s, t: self._update_codec_options(t, codec_spinner))
        
        for widget, field in [(qoe_spinner, "QoE"), (codec_spinner, "Codec"), (jitter_input, "Jitter (ms)")]:
            widget.bind(text=lambda i, v, f=field: self._update_field(self.section_softphone, f, v))
        
        popup = ConfigPopup(title_text="Configuración Softphone (Origen)", content_widget=form)
        popup.open()
        
        # Inicializar datos
        for widget, field in [(qoe_spinner, "QoE"), (codec_spinner, "Codec"), (jitter_input, "Jitter (ms)")]:
            self._update_field(self.section_softphone, field, widget.text)

    def open_red_popup(self):
        """Abre popup para configurar Red de Transporte (Encapsulación, Velocidad, Retardo)."""
        form = GridForm()
        
        encap = self._create_spinner(form, "Encapsulación WAN:", "Ethernet", ("Ethernet", "Ethernet + 802.1q", "PPPoE"))
        velocidad = self._create_input(form, "Velocidad Red (Kbps):", "", "float")
        retardo = self._create_input(form, "Retardo Red (ms):", "", "float")
        
        for widget, field in [(encap, "Encapsulación"), (velocidad, "Velocidad Red"), (retardo, "Retardo Red")]:
            widget.bind(text=lambda i, v, f=field: self._update_field(self.section_red, f, v))
        
        popup = ConfigPopup(title_text="Configuración Red de Transporte", content_widget=form)
        popup.open()
        
        self._update_field(self.section_red, "Encapsulación", encap.text)

    def open_destino_popup(self):
        """Abre popup mostrando resultados de RT_RESPONSE (resultados calculados)."""
        app = App.get_running_app()
        
        form = GridForm(cols=2)
        
        for field_name in ["Rt2jit (ms)", "Rt1_5jit (ms)", "CSI (ms)", "Rphy (ms)", "Rpaq (ms)", "Rs (ms)"]:
            form.add_widget(Label(text=f"{field_name}:"))
            stored_value = app.destination_results_data.get(field_name, "---") if hasattr(app, "destination_results_data") else "---"
            form.add_widget(Label(text=stored_value, color=(1, 1, 1, 1), size_hint_x=1))
        
        popup = ConfigPopup(title_text="Softphone (Destino) - Resultados", content_widget=form)
        popup.open()

    def send_data(self):
        """Envía RT_REQUEST al servidor y carga resultados via callback."""
        app = App.get_running_app()
        summary = getattr(app, "summary_data", {})
        
        payload = {
            "codec": summary.get(self.section_softphone, {}).get("Codec", "G.711"),
            "jitter": float(summary.get(self.section_softphone, {}).get("Jitter (ms)", 30)),
            "netDelay": float(summary.get(self.section_red, {}).get("Retardo Red", 0)),
        }
        
        MessageSender.send("RT_REQUEST", payload, callback=self._on_response_received)

    def _create_spinner(self, form, label_text, default, values):
        """Crea un Spinner (dropdown) con etiqueta."""
        form.add_widget(Label(text=label_text))
        widget = Spinner(text=default, values=values)
        form.add_widget(widget)
        return widget

    def _create_input(self, form, label_text, default, input_type):
        """Crea un TextInput con etiqueta y validación de tipo."""
        form.add_widget(Label(text=label_text))
        widget = TextInput(multiline=False, text=default)
        if input_type == "float":
            widget.input_filter = "float"
        elif input_type == "int":
            widget.input_filter = "int"
        form.add_widget(widget)
        return widget

    def _update_codec_options(self, qoe_text, codec_spinner):
        """Actualiza opciones de codec cuando cambia QoE."""
        if qoe_text in CODEC_QOE_MAP:
            codec_spinner.values = CODEC_QOE_MAP[qoe_text]
            if codec_spinner.text not in codec_spinner.values:
                codec_spinner.text = codec_spinner.values[0]
        self._update_field(self.section_softphone, "Codec", codec_spinner.text)

    def _update_field(self, section, field, value):
        """Actualiza un campo en summary_data y redibuja el resumen."""
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
        """Actualiza el panel de resumen mostrando configuración actual."""
        app = App.get_running_app()
        summary = getattr(app, "summary_data", {})
        
        summary_str = "RESUMEN - PASO 1:\n"
        for section in [self.section_softphone, self.section_red]:
            if section in summary and summary[section]:
                summary_str += f"\n{section}:\n"
                for field, value in summary[section].items():
                    summary_str += f"  • {field}: {value}\n"
        
        if hasattr(self, "ids") and "panel_resultados" in self.ids:
            self.ids.panel_resultados.text = summary_str

    def _on_response_received(self, response):
        """Callback: procesa RT_RESPONSE del servidor y almacena resultados."""
        app = App.get_running_app()
        if not hasattr(app, "destination_results_data"):
            app.destination_results_data = {}
        
        if isinstance(response, dict):
            for resp_key, field_name in RT_RESPONSE_MAPPING.items():
                if resp_key in response:
                    value = response[resp_key]
                    formatted = f"{value:.2f}" if isinstance(value, (int, float)) else str(value)
                    app.destination_results_data[field_name] = formatted
