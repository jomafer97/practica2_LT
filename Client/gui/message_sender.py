import json
from kivy.uix.label import Label
from kivy.app import App
from .popups import ConfigPopup, GridForm
from clientSocket import ClientSocket
from Shared.message_builder import build_message


class MessageSender:
    """Clase genérica para enviar mensajes de cualquier tipo al backend."""

    @staticmethod
    def send(msg_type: str, payload_data: dict):
        """
        Envía un mensaje genérico al backend.

        Args:
            msg_type (str): Tipo de mensaje, por ejemplo 'RT_REQUEST'
            payload_data (dict): Datos del mensaje (codec, jitter, etc.)
        """
        # Verificar datos
        if not payload_data:
            form = GridForm()
            form.add_widget(Label(text=f"No hay datos para enviar ({msg_type})."))
            popup = ConfigPopup(title_text="Enviar Datos - Error", content_widget=form)
            popup.open()
            return

        # Construir mensaje usando el builder
        try:
            message = build_message(msg_type, **payload_data)
        except Exception as e:
            MessageSender._show_popup_error(
                f"Error al construir mensaje {msg_type}: {e}"
            )
            return

        # Enviar mensaje
        client = ClientSocket()
        addr = ("127.0.0.1", 32003)
        try:
            client.send_message(message, addr)
            answer, _ = client.recv_message(1024)
            print(f"Respuesta recibida ({msg_type}): {answer}")
            MessageSender._show_popup_success(msg_type, payload_data, answer)
        except Exception as e:
            MessageSender._show_popup_error(f"No se pudo enviar {msg_type}: {e}")

    @staticmethod
    def _show_popup_success(msg_type, payload, answer):
        form = GridForm()
        form.add_widget(Label(text=f"✅ {msg_type} enviado correctamente."))

        form.add_widget(Label(text="\n--- Payload (JSON) ---\n"))
        payload_label = Label(text=json.dumps(payload, indent=2, ensure_ascii=False))
        form.add_widget(payload_label)

        form.add_widget(Label(text="\n--- Respuesta (JSON) ---\n"))
        answer_label = Label(text=str(answer))
        form.add_widget(answer_label)

        popup = ConfigPopup(title_text=f"{msg_type} - Resultado", content_widget=form)
        popup.open()

    @staticmethod
    def _show_popup_error(msg):
        form = GridForm()
        form.add_widget(Label(text=msg))
        popup = ConfigPopup(title_text="Error de Envío", content_widget=form)
        popup.open()
