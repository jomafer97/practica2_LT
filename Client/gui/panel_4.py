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

# Configuración de campos para Simulación de Costes (Paso 4)
# MODIFICADO: Alineado con COST_REQUEST (BWst y callBW se obtienen del paso 3)
COST_PARAMS_FIELDS = [
    ("Presupuesto Máximo (Pmax €):", "float", "1000.0", "Pmax"),
]


class Step4Panel(BoxLayout):
    """Panel para Paso 4: Simulación de Costes (COST_REQUEST)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 10
        self.spacing = 10
        self.section = "Parámetros de Costes"

    def handle_button_press(self, button_name):
        if button_name == "softphone_destino":
            self.show_cost_results()

    def open_config_popup(self):
        """Abre popup para configurar Parámetros de Costes."""
        form = GridForm()

        for label_text, input_type, default, field_name in COST_PARAMS_FIELDS:
            widget = self._create_input_field(form, label_text, default, input_type)
            widget.bind(
                text=lambda i, v, lt=label_text: self._on_field_change(i, v, lt)
            )
            # Inicializar valor por defecto
            self._on_field_change(widget, default, label_text)

        popup = ConfigPopup(
            title_text="Parámetros de Costes - Simulación", content_widget=form
        )
        popup.open()

    def send_cost_data(self):
        """Envía COST_REQUEST al servidor."""
        app = App.get_running_app()
        cost_data = getattr(app, "summary_data", {}).get(self.section, {})
        bw_results = getattr(app, "bw_results_data", {})

        if not bw_results:
            self._show_error_popup("No se han calculado los datos de BW (Paso 3).")
            return

        try:
            # 1. Get Pmax from this panel
            pmax = float(cost_data.get("Pmax", 1000.0))

            # 2. Extract data from BW_RESPONSE (Paso 3)
            # Mapping: RTP -> uncompressed, cRTP -> compressed
            uncompressed = bw_results.get("uncompressed", {})
            compressed = bw_results.get("compressed", {})

            call_bw_rtp = uncompressed.get("callBW")
            call_bw_crtp = compressed.get("callBW")
            bwst_rtp = uncompressed.get("BWst")
            bwst_crtp = compressed.get("BWst")

            if any(v is None for v in [call_bw_rtp, call_bw_crtp, bwst_rtp, bwst_crtp]):
                self._show_error_popup("Datos de BW (Paso 3) incompletos.")
                return

            payload = {
                "callBW": {"RTP": call_bw_rtp, "cRTP": call_bw_crtp},
                "BWst": {"RTP": bwst_rtp, "cRTP": bwst_crtp},
                "Pmax": pmax,
            }
            MessageSender.send("COST_REQUEST", payload, callback=self._on_cost_response)
        except (ValueError, KeyError, TypeError) as e:
            self._show_error_popup(
                f"Valores inválidos o faltan datos de BW (Paso 3): {str(e)}"
            )

    def _on_cost_response(self, response):
        """Callback para procesar la respuesta COST_RESPONSE."""
        try:
            cost_data = response if isinstance(response, dict) else {}

            app = App.get_running_app()
            # Guardar la respuesta COMPLETA
            app.cost_results_data = cost_data

            MessageSender._show_popup_success("COST_REQUEST", {}, response)
        except Exception as e:
            self._show_error_popup(f"Error procesando respuesta COST: {str(e)}")

    def show_cost_results(self):
        """Muestra los resultados de Costes guardados."""
        app = App.get_running_app()
        form = GridForm(cols=2)

        results = getattr(app, "cost_results_data", {})

        # Helper to add nested data
        def add_result(form_widget, key, value, indent=""):
            form_widget.add_widget(Label(text=f"{indent}{key}:"))
            if isinstance(value, dict):
                form_widget.add_widget(Label(text=""))  # Empty cell for dict title
                for k, v in value.items():
                    add_result(form_widget, k, v, indent="    ")
            else:
                form_widget.add_widget(
                    Label(text=str(value), color=(1, 1, 1, 1), size_hint_x=1)
                )

        if not results:
            form.add_widget(Label(text="Resultados Costes:"))
            form.add_widget(Label(text="---", color=(1, 1, 1, 1), size_hint_x=1))
        else:
            for key, value in results.items():
                add_result(form, key, value)

        popup = ConfigPopup(
            title_text="Softphone (Destino) - Resultados Costes", content_widget=form
        )
        popup.open()

    # --- Métodos Helper (idénticos a panel_2 y panel_3) ---

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
        for label, _, _, field_name in COST_PARAMS_FIELDS:
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
