import json

messages = {
    # SOLICITUD DEL CÁLCULO DE RT
    "RT_REQUEST": {
        "codec": None,
        "jitter (ms)": None,
        "vRed (Mbps)": None,
        "rR (ms)": None
    },

    "RT_RESPONSE": {
        "Rt2jit (ms)": None,
        "Rt1.5jit (ms)": None,
        "CSI (ms)": None,
        "Rfis (ms)": None,
        "Rpaq (ms)": None,
        "Rs (ms)": None
    },

    # SOLICITUD DEL CÁLCULO DEL COSTE
    "COST_REQUEST": {
        "BWstRTP (Mbps)": None,
        "BWstcRTP (Mbps)": None,
        "Pmax (euros)": None,
        "Nllamadas (llamadas)": None
    },

    "COST_RESPONSE": {
        "PMbps (euros)": None,
        "Verificar": None,
        "NllamadasCumple (llamadas)": None
    },

    # SOLICITUD DEL CÁLCULO DEL PLR
    "PLR_REQUEST": {
        "bitstream": None
    },

    "PLR_RESPONSE": {
        "p": None,
        "q": None,
        "pi1": None,
        "pi0": None,
        "E (paquetes)": None
    }
}

def build_message(type: str, params: dict) -> dict:
    base_message = messages.get(type, {})

    if not base_message:
        return {}

    message = base_message.copy()

    message.update(params)

    return json.dumps(message, indent=4)


def validate_message(json_message: str, expected_type: str, template: dict = messages) -> bool:
    try:
        message = json.loads(json_message)

        if not isinstance(message, dict):
            return False

    except json.JSONDecodeError:
        return False

    expected_template = template.get(expected_type)

    if expected_template is None:
        return False

    received_keys = set(message.keys())
    template_keys = set(expected_template.keys())

    if received_keys != template_keys:
        return False

    for key, value in message.items():
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return False

    return True
