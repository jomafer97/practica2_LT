from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from .popups import ConfigPopup, GridForm, InfoPopup
from kivy.uix.textinput import TextInput
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.utils import platform
import os, sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from .message_sender import MessageSender

# --- Directorio Home del Usuario ---
if platform == 'win':
    user_path = os.environ['USERPROFILE']
else:
    user_path = os.path.expanduser('~')

BITSTREAM_KEY = "Bitstream"


class Step5Panel(BoxLayout):
    """Panel para Paso 5: Simulación PLR (PLR_REQUEST)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 10
        self.spacing = 10
        self.section = "Parámetros de PLR"
        self.file_popup = None

    def handle_button_press(self, button_name):
        if button_name == "question_5":
            self.open_question5_popup()
        if button_name == "configurar_manual":
            self.open_text_input_popup()

    def open_question5_popup(self):
        """ Abre popup con la información de este paso """
        info_text_1 = (
            "Este panel calcula los parámetros necesarios para calcular la probabilidad de pérdida de paquetes (PLR) a partir de un bitstream.\n\n"
            "[b]1. Introducir el Bitstream:[/b]\n"
            "   Tienes dos opciones para proporcionar la traza de bits (una cadena de 0s y 1s):\n"
            "   - [b]Cargar Fichero:[/b] Haz clic en el [color=9D33FF]icono del archivo[/color] para seleccionar un fichero `.txt` que contenga el bitstream.\n"
            "   - [b]Entrada Manual:[/b] Haz clic en el botón [color=9D33FF]'Introducir Bitstream (Manual)'[/color] para pegar o escribir la cadena directamente.\n\n"
            "[b]2. Calcular Resultados:[/b]\n"
            "   - Pulsa el botón [color=33FF57]'Enviar Datos (Paso 5 - PLR)'[/color] para que el servidor calcule los parámetros p, q, pi1, pi0 y E.\n\n"
            "[b]3. Ver Resultados:[/b]\n"
            "   - Los resultados se mostrarán automáticamente en una ventana emergente después del cálculo."
        )

        popup = InfoPopup(
            title="Información Paso 7: Cálculo de PLR",
            info_text = info_text_1
        )
        popup.open()

    def open_text_input_popup(self):
        """Abre un popup para introducir el bitstream manualmente."""
        form = GridForm(cols=1)

        app = App.get_running_app()
        current_bitstream = getattr(app, "summary_data", {}).get(self.section, {}).get(BITSTREAM_KEY, "")

        form.add_widget(Label(text="Introduzca el bitstream (cadena de 0s y 1s):"))
        text_input = TextInput(text=current_bitstream, multiline=True)
        form.add_widget(text_input)

        def on_ok(instance):
            content = text_input.text.strip()
            if not content:
                self._show_error_popup("El bitstream no puede estar vacío.")
                return

            self._update_data(BITSTREAM_KEY, content)
            self._update_summary_display()

        popup = ConfigPopup(title_text="Introducir Bitstream Manualmente", content_widget=form)
        popup.bind(on_dismiss=on_ok)  # Guardar al cerrar
        popup.open()

    def open_config_popup(self):
        """
        Abre un Popup con un FileChooser para seleccionar un archivo .txt.
        Se debe crear un Popup diferente por las peculiaridades de FileChooser
        """
        popup_layout = BoxLayout(orientation='vertical', spacing=10)

        self.filechooser = FileChooserListView(
            path=user_path,  # Empezar en el directorio Home
            filters=['*.txt']  # Mostrar archivos .txt
        )
        popup_layout.add_widget(self.filechooser)

        # Botones de "OK" y "Cancelar"
        button_layout = BoxLayout(size_hint_y=None, height=44, spacing=10)
        ok_btn = Button(text='Seleccionar')
        cancel_btn = Button(text='Cancelar')
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(ok_btn)
        popup_layout.add_widget(button_layout)

        # Crear el Popup
        self.file_popup = Popup(
            title='Seleccionar archivo Bitstream (.txt)',
            content=popup_layout,
            size_hint=(0.9, 0.9)
        )

        cancel_btn.bind(on_press=self.file_popup.dismiss)
        ok_btn.bind(on_press=self._on_file_selected)

        self.file_popup.open()

    def _on_file_selected(self, instance_button):
        """
        Callback que se ejecuta al pulsar "OK" en el FileChooser.
        """
        if self.filechooser.selection:
            # Obtener la ruta del archivo
            file_path = self.filechooser.selection[0]

            # Leer el archivo y actualizar los datos
            self._read_bitstream_from_file(file_path)

            # Cerrar el popup del FileChooser
            if self.file_popup:
                self.file_popup.dismiss()

    def _read_bitstream_from_file(self, path):
        """
        Lee el contenido del archivo y lo guarda en app.summary_data.
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:

                content = f.read().strip() # Eliminamos los espacios
            if not content:
                self._show_error_popup("El archivo seleccionado está vacío.")
                return

            self._update_data(BITSTREAM_KEY, content) # Actualiza la data con el contenido del archivo leído
            self._update_summary_display() # Actualiza el resumen en el panel

        except UnicodeDecodeError:
            self._show_error_popup(f"Error: El archivo no es UTF - 8")
        except Exception as e:
            self._show_error_popup(f"Error al leer el archivo:\n{e}")

    def send_plr_data(self):
        """Envía PLR_REQUEST al servidor."""
        app = App.get_running_app()
        plr_data = getattr(app, "summary_data", {}).get(self.section, {})

        try:
            bitstream_str = plr_data.get(BITSTREAM_KEY, "")
            if not bitstream_str:
                self._show_error_popup("El Bitstream no puede estar vacío. Por favor, cargue un archivo.")
                return

            payload = {"bitstream": bitstream_str}

            print(f"--- DEBUG: PASO 2 - Enviando PLR_REQUEST...")
            print(f"--- DEBUG: Payload: {payload}")

            MessageSender.send("PLR_REQUEST", payload, callback=self._on_plr_response)

            print("--- DEBUG: Mensaje enviado. Esperando respuesta (callback)...")

        except (ValueError, KeyError) as e:
            print(f"--- DEBUG: ERROR - Excepción en send_plr_data: {e}")
            self._show_error_popup(f"Valores inválidos: {str(e)}")

    def _on_plr_response(self, response):
        """Callback para procesar la respuesta PLR_RESPONSE."""

        print("\n--- DEBUG: PASO 3 - ¡Respuesta PLR recibida! ---")
        print(f"--- DEBUG: Datos recibidos: {response}")

        try:
            plr_data = response if isinstance(response, dict) else {}

            app = App.get_running_app()
            # Guardar la respuesta COMPLETA
            app.plr_results_data = plr_data

            self.show_plr_results()
        except Exception as e:
            print(f"--- DEBUG: ERROR - Excepción en _on_plr_response: {e}")
            self._show_error_popup(f"Error procesando respuesta PLR: {str(e)}")

    def show_plr_results(self):
        """Muestra los resultados de PLR guardados."""
        app = App.get_running_app()
        form = GridForm(cols=2)

        results = getattr(
            app,
            "plr_results_data",
            {"p": "---", "q": "---", "pi1": "---", "pi0": "---", "E": "---"},
        )

        for key, value in results.items():

            if isinstance(value, (int, float)):
                value_str = f"{value:.3f}"
            else:
                value_str = str(value)

            form.add_widget(Label(text=f"{key}:"))
            form.add_widget(Label(text=value_str, color=(1, 1, 1, 1), size_hint_x=1))

        popup = ConfigPopup(
            title_text="Softphone (Destino) - Resultados PLR", content_widget=form
        )
        popup.open()
    # --- Métodos Helper ---

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
            # Mostramos el bitstream (o parte de él) en el resumen
            bitstream_val = data.get(BITSTREAM_KEY, "")
            if len(bitstream_val) > 50:
                 summary_str += f"   • {BITSTREAM_KEY}: {bitstream_val[:50]}...\n"
            else:
                 summary_str += f"   • {BITSTREAM_KEY}: {bitstream_val}\n"


        if hasattr(self, "ids") and "panel_resultados" in self.ids:
            self.ids.panel_resultados.text = summary_str

    def _show_error_popup(self, message):
        form = GridForm()
        form.add_widget(Label(text=f"Error: {message}"))
        popup = ConfigPopup(title_text="Error de Entrada", content_widget=form)
        popup.open()
