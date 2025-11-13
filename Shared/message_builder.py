import json

messages = {
    # RT CALCULATION REQUEST
    "RT_REQUEST": {
        "codec": None,
        "jitter": None,             # (ms)
        "netDelay": None            # (ms)
    },

    "RT_RESPONSE": {
        "rt2jit": None,             # (ms)
        "rt1_5jit": None,           # (ms)
        "csi": None,                # (ms)
        "rphy": None,               # (ms)
        "rpac": None,               # (ms)
    },

    # TRAFFIC CALCULATION REQUEST
    "ERLANG_REQUEST": {
        "numLines": None,           # (int)
        "numCalls": None,           # (int)
        "avgDuration": None,        # (s)
        "blockingPercentage": None  # (0,1)
    },

    "ERLANG_RESPONSE": {
        "Erlangs": None,            # (erlangs)
        "maxLines": None            # (lines)
    },

    # BW CALCULATION REQUEST
    "BW_REQUEST": {
        "codec": None,
        "pppoe": None,              # (bool)
        "vlan8021q": None,          # (bool)
        "reservedBW": None,         # (0, 1)
        "totalCalls":None           # (int)
    },

    "BW_RESPONSE": {
        "compressed":{
            "packetLength": None,  # (bits)
            "callBW": None,        # (bps)
            "BWst": None           # (Mbps)
        },
        "uncompressed":{
            "PacketLength": None,  # (bits)
            "callBW": None,        # (bps)
            "BWst": None           # (Mbps)
        },
        "pps":None                 # (packets per second)
    },

    # COST CALCULATION REQUEST
    "COST_REQUEST": {
        "callBW":{
            "RTP":None,             # (bps)
            "cRTP":None             # (bps)
        },
        "BWst":{
            "RTP":None,             # (Mbps)
            "cRTP":None             # (Mbps)
        },
        "Pmax": None,               # (euros)
    },

    "COST_RESPONSE": {
        "mbpsCost": None,           # (euros)
        "RTP":{
            "valid": None,          # (bool)
            "possibleCalls": None   # (calls)
        },
        "cRTP":{
            "valid": None,          # (bool)
            "possibleCalls": None   # (calls)
        }
    },

    # PLR CALCULATION REQUEST
    "PLR_REQUEST": {
        "bitstream": None           # (string)
    },

    "PLR_RESPONSE": {
        "p": None,
        "q": None,
        "pi1": None,
        "pi0": None,
        "E": None
    },

    # REPORT REQUEST
    "REPORT_REQUEST":{
        # RT CALCULATION REQUEST
        "RT_REQUEST": {
            "codec": None,
            "jitter": None,             # (ms)
            "netDelay": None            # (ms)
        },

        "RT_RESPONSE": {
            "rt2jit": None,             # (ms)
            "rt1_5jit": None,           # (ms)
            "csi": None,                # (ms)
            "rphy": None,               # (ms)
            "rpac": None,               # (ms)
        },

        # TRAFFIC CALCULATION REQUEST
        "ERLANG_REQUEST": {
            "numLines": None,           # (int)
            "numCalls": None,           # (int)
            "avgDuration": None,        # (s)
            "blockingPercentage": None  # (0,1)
        },

        "ERLANG_RESPONSE": {
            "Erlangs": None,            # (erlangs)
            "maxLines": None            # (lines)
        },

        # BW CALCULATION REQUEST
        "BW_REQUEST": {
            "codec": None,
            "pppoe": None,              # (bool)
            "vlan8021q": None,          # (bool)
            "reservedBW": None,         # (0, 1)
            "totalCalls":None           # (int)
        },

        "BW_RESPONSE": {
            "compressed":{
                "packetLength": None,  # (bits)
                "callBW": None,        # (bps)
                "BWst": None           # (Mbps)
            },
            "uncompressed":{
                "PacketLength": None,  # (bits)
                "callBW": None,        # (bps)
                "BWst": None           # (Mbps)
            },
            "pps":None                 # (packets per second)
        },

        # COST CALCULATION REQUEST
        "COST_REQUEST": {
            "callBW":{
                "RTP":None,             # (bps)
                "cRTP":None             # (bps)
            },
            "BWst":{
                "RTP":None,             # (Mbps)
                "cRTP":None             # (Mbps)
            },
            "Pmax": None,               # (euros)
        },

        "COST_RESPONSE": {
            "mbpsCost": None,           # (euros)
            "RTP":{
                "valid": None,          # (bool)
                "possibleCalls": None   # (calls)
            },
            "cRTP":{
                "valid": None,          # (bool)
                "possibleCalls": None   # (calls)
            }
        },

        # PLR CALCULATION REQUEST
        "PLR_REQUEST": {
            "bitstream": None           # (string)
        },

        "PLR_RESPONSE": {
            "p": None,
            "q": None,
            "pi1": None,
            "pi0": None,
            "E": None
        },
    },

    # ERROR MESSAGES
    "ERROR":{
        "source": None,
        "error": None
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
