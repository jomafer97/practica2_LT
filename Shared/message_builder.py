import json

messages = {
    # RT CALCULATION REQUEST
    "RT_REQUEST": {
        "codec": None,
        "jitter": None,           # (ms)
        "networkSpeed": None,     # (Mbps)
        "networkDelay": None      # (ms)
    },

    "RT_RESPONSE": {
        "Rt2jit": None,           # (ms)
        "Rt1_5jit": None,         # (ms)
        "CSI": None,              # (ms)
        "Rphy": None,             # (ms)
        "Rpaq": None,             # (ms)
        "Rs": None                # (ms)
    },

    # TRAFFIC CALCULATION REQUEST
    "ERLANG_REQUEST": {
        "numChannels": None,        # (Channels)
        "numCalls": None,           # (Calls)
        "avgDuration": None,        # (s)
        "blockingPercentage": None  # (%)
    },

    "ERLANG_RESPONSE": {
        "Erlangs": None,            # (Erlang)
        "maxNumCalls": None         # (Calls)
    },

    # BW CALCULATION REQUEST
    "BW_REQUEST": {
        "codec": None,
        "extendedHeader": None,     # (bits),
        "maxNumCalls": None,        # (Calls)
        "BandWidth": None           # (bps)
    },

    "BW_RESPONSE": {
        "uncompressedPktLength": None, # (bits)
        "compressedPktLength": None,   # (bits)
        "pps": None,                   # (packets per second)
        "BandWidthcRTP": None,         # (bps)
        "BandWidthRTP": None           # (bps)
    },

    # COST CALCULATION REQUEST
    "COST_REQUEST": {
        "BWstRTP": None,            # (Mbps)
        "BWstcRTP": None,           # (Mbps)
        "Pmax": None,               # (euros)
        "numCalls": None            # (calls)
    },

    "COST_RESPONSE": {
        "PMbps": None,              # (euros)
        "verification": None,
        "compliantCalls": None      # (calls)
    },

    # PLR CALCULATION REQUEST
    "PLR_REQUEST": {
        "bitstream": None
    },

    "PLR_RESPONSE": {
        "p": None,
        "q": None,
        "pi1": None,
        "pi0": None,
        "E": None                   # (packets)
    },

    # ERROR MESSAGES
    "ERROR":{
        "source": None,
        "message": None
    }
}

def build_message(type: str, **kwargs):
    base_message = messages.get(type)
    if base_message is None:
        raise ValueError(f"Error: El tipo de mensaje '{type}' no se encontró en las plantillas.")

    message = base_message.copy()

    for key, value in kwargs.items():
        if key in message:
            message[key] = value
        else:
            raise KeyError(f"Error: El argumento '{key}' no es válido para el tipo de mensaje '{type}'.")

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
