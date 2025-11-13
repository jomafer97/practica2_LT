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

# Configuración de campos para Parámetros Globales
GLOBAL_PARAMS_FIELDS = [
    ("Num. Empresas (Nc):", "int", "", "Num. Empresas"),
    ("Líneas / Cliente (Nl):", "int", "", "Líneas / Cliente"),
    ("T. Medio Llamada (Tpll):", "float", "", "T. Medio Llamada"),
    ("Prob. Bloqueo (Pb) [GoS]:", "float", "0.01", "Prob. Bloqueo"),
]


class Step2Panel(BoxLayout):
    """Panel para Paso 2: Muestra imágenes y permite configurar Parámetros Globales."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        self.section = "Parámetros Globales"

    def handle_button_press(self, button_name):
        """Dispatch de botones a sus métodos correspondientes."""
        if button_name == "softphone_destino":
            self.show_erlang_results()

    def open_global_popup(self):
        """Abre popup para configurar Parámetros Globales."""
        form = GridForm()
        
        for label_text, input_type, default, _ in GLOBAL_PARAMS_FIELDS:
            widget = self._create_input_field(form, label_text, default, input_type)
            widget.bind(text=lambda i, v, lt=label_text: self._on_field_change(i, v, lt))
        
        popup = ConfigPopup(title_text="Parámetros Globales - GoS", content_widget=form)
        popup.open()
        
        # Inicializar Prob. Bloqueo con su valor por defecto
        self._on_field_change(None, "0.01", "Prob. Bloqueo (Pb) [GoS]:")

    def send_global_data(self):
        """Envía ERLANG_REQUEST al servidor con los Parámetros Globales."""
        app = App.get_running_app()
        global_data = getattr(app, "summary_data", {}).get(self.section, {})
        
        try:
            num_companies = int(global_data.get("Num. Empresas", 0))
            lines_per_client = int(global_data.get("Líneas / Cliente", 0))
            avg_duration = float(global_data.get("T. Medio Llamada", 0))
            blocking_prob = float(global_data.get("Prob. Bloqueo", 0.01))
            
            # Calcular número de líneas (Nc × Nl) y número de llamadas
            num_lines = num_companies * lines_per_client
            num_calls = num_lines  # Asumimos que cada línea puede hacer una llamada
            
            payload = {
                "numLines": num_lines,
                "numCalls": num_calls,
                "avgDuration": avg_duration,
                "blockingPercentage": blocking_prob,
            }
            MessageSender.send("ERLANG_REQUEST", payload, callback=self._on_erlang_response)
        except (ValueError, KeyError) as e:
            self._show_error_popup(f"Valores inválidos: {str(e)}")

    def _on_erlang_response(self, response):
        """Callback para procesar la respuesta ERLANG_RESPONSE del servidor."""
        try:
            print(f"DEBUG: Respuesta recibida tipo: {type(response)}, contenido: {response}")
            # Procesar respuesta - el servidor envía directamente:
            # {"Erlangs": <value>, "maxLines": <value>}
            erlang_data = response if isinstance(response, dict) else {}
            
            print(f"DEBUG: erlang_data: {erlang_data}")
            
            # Guardar resultados en la app
            app = App.get_running_app()
            if not hasattr(app, "erlang_results_data"):
                app.erlang_results_data = {}
            app.erlang_results_data["Erlangs"] = erlang_data.get("Erlangs", "---")
            app.erlang_results_data["maxLines"] = erlang_data.get("maxLines", "---")
            
            print(f"DEBUG: Datos guardados: {app.erlang_results_data}")
            
            # Mostrar mensaje de éxito
            MessageSender._show_popup_success("ERLANG_REQUEST", {}, response)
        except Exception as e:
            print(f"DEBUG: Error en _on_erlang_response: {str(e)}")
            self._show_error_popup(f"Error procesando respuesta Erlang: {str(e)}")

    def show_erlang_results(self):
        """Muestra los resultados de Erlang guardados (similar a destino en pantalla 1)."""
        app = App.get_running_app()
        
        print(f"DEBUG show_erlang_results: hasattr erlang_results_data = {hasattr(app, 'erlang_results_data')}")
        if hasattr(app, "erlang_results_data"):
            print(f"DEBUG show_erlang_results: erlang_results_data = {app.erlang_results_data}")
        
        form = GridForm(cols=2)
        
        erlangs = app.erlang_results_data.get("Erlangs", "---") if hasattr(app, "erlang_results_data") else "---"
        max_lines = app.erlang_results_data.get("maxLines", "---") if hasattr(app, "erlang_results_data") else "---"
        
        print(f"DEBUG: Mostrando Erlangs={erlangs}, maxLines={max_lines}")
        
        form.add_widget(Label(text="Erlangs (Erlang):"))
        form.add_widget(Label(text=str(erlangs), color=(1, 1, 1, 1), size_hint_x=1))
        
        form.add_widget(Label(text="maxLines (Líneas):"))
        form.add_widget(Label(text=str(max_lines), color=(1, 1, 1, 1), size_hint_x=1))
        
        popup = ConfigPopup(title_text="Softphone (Destino) - Resultados Erlang", content_widget=form)
        popup.open()

    def _create_input_field(self, form, label_text, default_value, input_type):
        """Crea un campo de entrada (Label + Widget)."""
        form.add_widget(Label(text=label_text))
        
        widget = TextInput(multiline=False, text=default_value)
        if input_type == "float":
            widget.input_filter = "float"
        elif input_type == "int":
            widget.input_filter = "int"
        
        form.add_widget(widget)
        return widget

    def _on_field_change(self, instance, value, label_text):
        """Callback cuando cambia un campo, actualiza datos y vista."""
        field_name = self._get_field_name(label_text)
        if field_name:
            self._update_data(field_name, value)
            self._update_summary_display()

    def _get_field_name(self, label_text):
        """Obtiene el nombre del campo a partir de la etiqueta."""
        for label, _, _, field_name in GLOBAL_PARAMS_FIELDS:
            if label == label_text:
                return field_name
        return None

    def _update_data(self, field_name, value):
        """Actualiza summary_data con el nuevo valor."""
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
        """Actualiza el panel de resumen con los parámetros actuales."""
        app = App.get_running_app()
        data = getattr(app, "summary_data", {}).get(self.section, {})
        
        if not data:
            summary_str = "Sin parámetros configurados aún."
        else:
            summary_str = "PARÁMETROS GLOBALES:\n"
            for field_name, value in data.items():
                summary_str += f"  • {field_name}: {value}\n"
        
        if hasattr(self, "ids") and "panel_resultados" in self.ids:
            self.ids.panel_resultados.text = summary_str

    def _show_error_popup(self, message):
        """Muestra un popup de error."""
        form = GridForm()
        form.add_widget(Label(text=f"Error: {message}"))
        popup = ConfigPopup(title_text="Error de Entrada", content_widget=form)
        popup.open()
