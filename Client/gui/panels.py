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

CODEC_QOE_MAP = {
    "Excelente": ("G.711", "G722_64k"),
    "Buena": ("G.729", "G.726_32k", "ilbc_mode_20"),
    "Normal": ("G.723.1_6.3", "G.723.1_5.3", "G.726_24k", "G.728", "ilbc_mode_30"),
}

RT_RESPONSE_MAPPING = {
    "rt2jit": "Retardo Total (Buffer x2) (ms)",
    "rt1_5jit": "Retardo Total (Buffer x1.5) (ms)",
    "csi": "CSI (ms)",
    "rphy": "Retardo Físico (ms)",
    "rpac": "Retardo Paquetización (ms)",
    "algD": "Retardo Algorítmico (ms)",
}


class MainPanel(BoxLayout):
    """Panel para Paso 1: Configuración de Softphone Origen, Red Transporte y Softphone Destino."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.section_softphone = "Softphone (Origen)"

    def handle_button_press(self, button_name):
        """Dispatch de botones a sus métodos correspondientes."""
        actions = {
            "softphone_origen": self.open_softphone_popup,
            "softphone_destino": self.open_destino_popup,
            "question_1": self.open_question1_popup,
        }
        if button_name in actions:
            actions[button_name]()

    def open_question1_popup(self):
        """ Abre popup con la información de este paso """
        info_text_1 = (
            "Este panel te permite simular la calidad (QoS) de una llamada VoIP.\n\n"
            "[b]1. Configurar Parámetros:[/b]\n"
            "   - Haz clic en la imagen del softphone de la [color=33AFFF]izquierda[/color] para abrir el menú de configuración.\n"
            "   - Selecciona la Calidad de Voz (QoE), el Codec, el Jitter y el Retardo de Red.\n\n"
            "[b]2. Calcular Resultados:[/b]\n"
            "   - Pulsa el botón [color=33FF57]'Enviar Datos (Paso 1)'[/color] para que el servidor realice los cálculos de calidad.\n\n"
            "[b]3. Ver Resultados:[/b]\n"
            "   - Haz clic en la imagen del softphone de la [color=33AFFF]derecha[/color] para ver los resultados, incluyendo una valoración del retardo total."
        )

        popup = InfoPopup(
            title="Información Paso 1, 2 y 3: Cálculo QoS",
            info_text = info_text_1
        )
        popup.open()

    def open_softphone_popup(self):
        """Abre popup para configurar Softphone Origen (QoE, Codec, Jitter, Retardo Red)."""
        form = GridForm()

        qoe_spinner = self._create_spinner(
            form, "Calidad Voz (QoE):", "Excelente", ("Excelente", "Buena", "Normal")
        )
        codec_spinner = self._create_spinner(
            form, "Codec (elegido):", "G.711", CODEC_QOE_MAP["Excelente"]
        )
        jitter_input = self._create_input(form, "Jitter (ms):", "", "float")

        net_delay_input = self._create_input(form, "Retardo de Red (ms):", "", "float")

        qoe_spinner.bind(text=lambda s, t: self._update_codec_options(t, codec_spinner))

        for widget, field in [
            (qoe_spinner, "QoE"),
            (codec_spinner, "Codec"),
            (jitter_input, "Jitter (ms)"),
            (net_delay_input, "Retardo de Red (ms)"),
        ]:
            widget.bind(
                text=lambda i, v, f=field: self._update_field(
                    self.section_softphone, f, v
                )
            )

        popup = ConfigPopup(
            title_text="Configuración Softphone (Origen)", content_widget=form
        )
        popup.open()

        for widget, field in [
            (qoe_spinner, "QoE"),
            (codec_spinner, "Codec"),
            (jitter_input, "Jitter (ms)"),
            (net_delay_input, "Retardo de Red (ms)"),
        ]:
            self._update_field(self.section_softphone, field, widget.text)

    def open_destino_popup(self):
        """Abre popup mostrando resultados de RT_RESPONSE (resultados calculados)."""

        def get_delay_feedback(delay_value):
            """Devuelve el mensaje y color según el valor del retardo."""
            if delay_value is None:
                return "Valor no calculado", (1, 1, 1, 1)  # Blanco
            if 0 <= delay_value <= 150:
                return "Aceptable para la mayoría de aplicaciones", (
                    0,
                    1,
                    0,
                    1,
                )  # Verde
            elif 150 < delay_value <= 400:
                return "Moderadamente aceptable", (1, 0.65, 0, 1)  # Naranja
            else:  # > 400
                return "Inaceptable", (1, 0, 0, 1)  # Rojo

        app = App.get_running_app()

        form = GridForm(cols=2)

        results_data = getattr(app, "destination_results_data", {})
        if results_data:
            # 1. Mostrar todos los resultados numéricos
            for key, field_name in RT_RESPONSE_MAPPING.items():
                raw_value = results_data.get(key)
                value_str = (
                    f"{raw_value:.2f}" if isinstance(raw_value, (int, float)) else "---"
                )
                form.add_widget(Label(text=f"{field_name}:"))
                form.add_widget(
                    Label(text=value_str, color=(1, 1, 1, 1), size_hint_x=1)
                )

            # 2. Añadir un separador visual
            form.add_widget(Label(text="-" * 20))
            form.add_widget(Label(text="-" * 20))

            # 3. Añadir los comentarios de feedback al final
            for key, name in [
                ("rt2jit", "Retardo Total (Buffer x2)"),
                ("rt1_5jit", "Retardo Total (Buffer x1.5)"),
            ]:
                feedback_text, feedback_color = get_delay_feedback(
                    results_data.get(key)
                )
                form.add_widget(Label(text=f"Valoración {name}:"))
                form.add_widget(Label(text=feedback_text, color=feedback_color))

        else:
            form.add_widget(Label(text="Resultados:"))
            form.add_widget(Label(text="---", color=(1, 1, 1, 1), size_hint_x=1))

        popup = ConfigPopup(
            title_text="Softphone (Destino) - Resultados", content_widget=form
        )
        popup.open()

    def send_data(self):
        """Envía RT_REQUEST al servidor y carga resultados via callback."""
        app = App.get_running_app()
        summary = getattr(app, "summary_data", {})

        try:
            payload = {
                "codec": summary.get(self.section_softphone, {}).get("Codec"),
                "jitter": float(
                    summary.get(self.section_softphone, {}).get("Jitter (ms)", 30)
                ),
                "netDelay": float(
                    summary.get(self.section_softphone, {}).get(
                        "Retardo de Red (ms)", 0
                    )
                ),
            }

            MessageSender.send(
                "RT_REQUEST", payload, callback=self._on_response_received
            )
        except (ValueError, KeyError) as e:
            form = GridForm()
            form.add_widget(
                Label(
                    text=f"Error: {str(e)}. Asegúrate de que 'Jitter' y 'Retardo de Red' tienen valores numéricos."
                )
            )
            popup = ConfigPopup(title_text="Error de Envío", content_widget=form)
            popup.open()

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

        section = self.section_softphone
        if section in summary and summary[section]:
            summary_str += f"\n{section}:\n"
            for field, value in summary[section].items():
                summary_str += f"   • {field}: {value}\n"

        if hasattr(self, "ids") and "panel_resultados" in self.ids:
            self.ids.panel_resultados.text = summary_str

    def _on_response_received(self, response):
        """Callback: procesa RT_RESPONSE del servidor y almacena resultados."""
        app = App.get_running_app()
        if not hasattr(app, "destination_results_data"):
            app.destination_results_data = {}

        app.destination_results_data.clear()
        if isinstance(response, dict):
            # Guardamos el diccionario de respuesta completo con valores numéricos raw
            app.destination_results_data = response

        self.open_destino_popup()
