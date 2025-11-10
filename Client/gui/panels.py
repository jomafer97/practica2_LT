from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from .popups import ConfigPopup, GridForm


class MainPanel(BoxLayout):
    def handle_button_press(self, button_name):
        if button_name == "softphone_origen":
            self.open_softphone_popup()
        elif button_name == "red_transporte":
            self.open_red_popup()
        elif button_name == "softphone_destino":
            self.open_destino_popup()

    def open_softphone_popup(self):
        form = GridForm()
        form.add_widget(Label(text="Calidad Voz (QoE) [Paso 2]:"))
        form.add_widget(
            Spinner(
                text="Buena", values=("Excelente", "Buena", "Normal", "Pobre", "Mala")
            )
        )
        form.add_widget(Label(text="Codec (elegido) [Paso 2]:"))
        form.add_widget(
            Spinner(text="G.711", values=("G.711", "G.729", "G.723.1 (6.3)", "..."))
        )
        form.add_widget(Label(text="BW Softphone (Kbps) [Paso 3]:"))
        form.add_widget(TextInput(multiline=False, input_filter="float"))
        popup = ConfigPopup(
            title_text="Configuración Softphone (Origen)", content_widget=form
        )
        popup.open()

    def open_red_popup(self):
        form = GridForm()
        form.add_widget(Label(text="Encapsulación WAN (Tcwan):"))
        form.add_widget(
            Spinner(text="Ethernet", values=("Ethernet", "Ethernet+802.1q", "PPPoE"))
        )
        form.add_widget(Label(text="Reserva BW (BWres %):"))
        form.add_widget(TextInput(multiline=False, input_filter="float"))
        form.add_widget(Label(text="Tipo RTP [Paso 5]:"))
        form.add_widget(Spinner(text="RTP", values=("RTP", "cRTP")))
        form.add_widget(Label(text="Secuencia PLR [Paso 7]:"))
        form.add_widget(TextInput(multiline=False))
        form.add_widget(Label(text="O cargar PLR desde .txt:"))
        form.add_widget(Button(text="Abrir Fichero"))
        popup = ConfigPopup(
            title_text="Configuración Red de Transporte", content_widget=form
        )
        popup.open()

    def open_destino_popup(self):
        form = GridForm(cols=1)
        form.add_widget(Label(text="Este panel mostrará resultados."))
        form.add_widget(
            Label(text="(p.ej. Tamaño Buffer Anti-Jitter, Retardo Decodif.)")
        )
        form.add_widget(Label(text="No requiere configuración de entrada."))
        popup = ConfigPopup(
            title_text="Softphone (Destino) - Resultados", content_widget=form
        )
        popup.open()

    def open_global_popup(self):
        form = GridForm()
        form.add_widget(Label(text="Num. Empresas (Nc):"))
        form.add_widget(TextInput(multiline=False, input_filter="int"))
        form.add_widget(Label(text="Líneas / Cliente (Nl):"))
        form.add_widget(TextInput(multiline=False, input_filter="int"))
        form.add_widget(Label(text="T. Medio Llamada (Tpll):"))
        form.add_widget(TextInput(multiline=False, input_filter="float"))
        form.add_widget(Label(text="Prob. Bloqueo (Pb) [GoS]:"))
        form.add_widget(TextInput(multiline=False, input_filter="float", text="0.01"))
        form.add_widget(Label(text="Precio / Mbps [Costes]:"))
        form.add_widget(TextInput(multiline=False, input_filter="float"))
        form.add_widget(Label(text="Precio Máx. Total [Costes]:"))
        form.add_widget(TextInput(multiline=False, input_filter="float"))
        form.add_widget(Label(text="Email para Informe [Paso 8]:"))
        form.add_widget(TextInput(multiline=False))
        popup = ConfigPopup(
            title_text="Parámetros Globales, GoS y Costes", content_widget=form
        )
        popup.open()
