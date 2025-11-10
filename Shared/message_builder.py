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
        "maxLinesNum": None         # (Calls)
    },

    # BW CALCULATION REQUEST
    "BW_REQUEST": {
        "codec": None,
        "extendedHeader": None,     # (bits),
        "maxNumCalls": None,        # (Calls)
        "ReservedBW": None           # (bps)
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
        raise ValueError(f"Error: invalid message type '{type}'.")

    message = base_message.copy()

    for key, value in kwargs.items():
        if key in message:
            message[key] = value
        else:
            raise KeyError(f"Error: invalid argument '{key}' for message '{type}'.")

    return message

def validate_message(message_dict: dict, expected_type: str, template: dict = messages):
    if not isinstance(message_dict, dict):
        raise TypeError(f"Message is not a dictionary; received type {type(message_dict).__name__}.")

    expected_template = template.get(expected_type)
    if expected_template is None:
        raise ValueError(f"Invalid expected_type: '{expected_type}' template not found.")

    received_keys = set(message_dict.keys())
    template_keys = set(expected_template.keys())

    if received_keys != template_keys:
        missing = template_keys - received_keys
        extra = received_keys - template_keys

        error_parts = []
        if missing:
            error_parts.append(f"Missing keys: {missing}")
        if extra:
            error_parts.append(f"Unexpected keys: {extra}")

        raise ValueError(f"Message key mismatch for '{expected_type}'. {' '.join(error_parts)}")

    for key, value in message_dict.items():
        if value is None:
            raise ValueError(f"Empty value (None) for required field: '{key}'.")

        if isinstance(value, str) and value.strip() == "":
            raise ValueError(f"Empty string value for required field: '{key}'.")

    return True
