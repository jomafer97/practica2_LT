import json
from kivy.uix.label import Label
from kivy.app import App
from .popups import ConfigPopup, GridForm
from clientSocket import ClientSocket
from Shared.message_builder import build_message


def send_data_handler(self, *args):
    app = App.get_running_app()
    summary = getattr(app, "summary_data", {}) if app else {}

    pretty = json.dumps(summary, indent=2, ensure_ascii=False)

    if not summary:
        form = GridForm()
        form.add_widget(Label(text="No hay datos para enviar."))
        popup = ConfigPopup(title_text="Enviar Datos - Error", content_widget=form)
        popup.open()
        return

    codec = None
    jitter = None
    network_speed_mbps = None
    network_delay_ms = None

    try:
        codec = summary.get("Softphone (Origen)", {}).get("Codec")
        jitter_val = summary.get("Softphone (Origen)", {}).get("Jitter (ms)")
        if jitter_val:
            try:
                jitter = float(str(jitter_val))
            except Exception:
                jitter = None
        else:
            qoe = summary.get("Softphone (Origen)", {}).get("QoE")
            if qoe:
                qoe_map = {"Excelente": 5, "Buena": 20, "Normal": 50}
                jitter = qoe_map.get(qoe, 30)
            else:
                jitter = None

        vel = summary.get("Red de Transporte", {}).get("Velocidad Red")
        if vel:
            try:
                vel_val = float(str(vel))
                network_speed_mbps = vel_val / 1000.0
            except Exception:
                network_speed_mbps = None

        ret = summary.get("Red de Transporte", {}).get("Retardo Red")
        if ret:
            try:
                network_delay_ms = float(str(ret))
            except Exception:
                network_delay_ms = None
    except Exception:
        pass

    message = {
        "codec": codec or "G.711",
        "jitter": jitter or 30,
        "netDelay": network_delay_ms or 0.0,
    }

    send_ok = False
    send_err = None

    payload = message
    payload = build_message(
        "RT_REQUEST",
        **{
            "codec": message["codec"],
            "jitter": message["jitter"],
            "netDelay": message["netDelay"],
        },
    )

    client = ClientSocket()
    addr = ("127.0.0.1", 32003)
    client.send_message(payload, addr)
    payload, addr = client.recv_message(1024)
    print(payload)
    send_ok = True

    form = GridForm()
    if send_ok:
        form.add_widget(Label(text="Datos enviados correctamente al servicio RT."))
    else:
        form.add_widget(Label(text=f"No se pudo enviar: {send_err}"))

    form.add_widget(Label(text="\n--- Payload (JSON) ---\n"))
    payload_label = Label(text=json.dumps(message, indent=2, ensure_ascii=False))
    form.add_widget(payload_label)

    popup = ConfigPopup(title_text="Enviar Datos - Resultado", content_widget=form)
    popup.open()
