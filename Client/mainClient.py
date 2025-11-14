import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from clientSocket import ClientSocket
from Shared.message_builder import build_message, validate_message

client = ClientSocket()

message = build_message(
    "RT_REQUEST",
    codec="G.711",
    jitter=20,
    netDelay=200
)

addr = ('127.0.0.1', 32003)

client.send_message(message, addr)

message, address = client.recv_message(1024)

print(message)

message = build_message(
    "ERLANG_REQUEST",
    numLines=120,
    numCalls=12,
    avgDuration=1200,
    blockingPercentage=0.01
)

addr = ('127.0.0.1', 32004)

client.send_message(message, addr)

message, address = client.recv_message(1024)

print(message)

message = build_message(
    "BW_REQUEST",
    codec="G.711",
    pppoe=False,
    vlan8021q=False,
    reservedBW=0.3,
    totalCalls=150*20
)

addr = ('127.0.0.1', 32005)

client.send_message(message, addr)

message, address = client.recv_message(1024)

print(message)

callBW = {
    "RTP": message["uncompressed"]["callBW"],
    "cRTP": message["compressed"]["callBW"]
}

print(callBW)

BWst = {
    "RTP": message["uncompressed"]["BWst"],
    "cRTP": message["compressed"]["BWst"]
}

print(BWst)

message = build_message(
    "COST_REQUEST",
    callBW=callBW,
    BWst=BWst,
    Pmax = 28390
)

addr = ('127.0.0.1', 32006)

client.send_message(message, addr)

message, address = client.recv_message(1024)

print(message)

message = build_message(
    "PLR_REQUEST",
    bitstream="000001111110001101100000010000000111010111111110000110000"
)

addr = ('127.0.0.1', 32007)

client.send_message(message, addr)

message, address = client.recv_message(1024)

print(message)

# --- PREPARACIÓN DE DATOS PARA INFORME FINAL ---

rt_req_data = {
    "codec": "G.711",
    "jitter": 20,
    "netDelay": 50
}
rt_resp_data = {
    "rt2jit": 140.0,
    "rt1_5jit": 115.0,
    "csi": 10.0,
    "rphy": 5.0,
    "rpac": 15.0,
    "algD": 10.0
}

erlang_req_data = {
    "numLines": 50,
    "numCalls": 200,
    "avgDuration": 120,
    "blockingPercentage": 0.02
}
erlang_resp_data = {
    "Erlangs": 6.667,
    "maxLines": 12
}

bw_req_data = {
    "codec": "G.711",
    "pppoe": False,
    "vlan8021q": True,
    "reservedBW": 0.15,
    "totalCalls": 12
}
bw_resp_data = {
    "compressed": {
        "packetLength": 352,
        "callBW": 31200,
        "BWst": 0.374
    },
    "uncompressed": {
        "PacketLength": 704,
        "callBW": 87200,
        "BWst": 1.046
    },
    "pps": 50
}

cost_req_data = {
    "callBW": {
        "RTP": 87200,
        "cRTP": 31200
    },
    "BWst": {
        "RTP": 1.046,
        "cRTP": 0.374
    },
    "Pmax": 500
}
cost_resp_data = {
    "mbpsCost": 478.01,
    "RTP": {
        "valid": True,
        "possibleCalls": 5
    },
    "cRTP": {
        "valid": True,
        "possibleCalls": 16
    }
}

plr_req_data = {
    "bitstream": "11101000101011101011010101"
}
plr_resp_data = {
    "p": 0.115,
    "q": 0.342,
    "pi1": 0.252,
    "pi0": 0.748,
    "E": 3.96
}

try:
    email = "jomafer@correo.ugr.es"

    mensaje_reporte_completo = build_message(
        "REPORT_REQUEST",
        email=email,
        RT_REQUEST=rt_req_data,
        RT_RESPONSE=rt_resp_data,
        ERLANG_REQUEST=erlang_req_data,
        ERLANG_RESPONSE=erlang_resp_data,
        BW_REQUEST=bw_req_data,
        BW_RESPONSE=bw_resp_data,
        COST_REQUEST=cost_req_data,
        COST_RESPONSE=cost_resp_data,
        PLR_REQUEST=plr_req_data,
        PLR_RESPONSE=plr_resp_data
    )

    addr = ('127.0.0.1', 32008)

    print("Cliente: Enviando reporte completo...")
    client.send_message(mensaje_reporte_completo, addr)

    print("Cliente: Esperando confirmación del servidor...")
    respuesta_reporte, address = client.recv_message(16384)

    print("--- Respuesta del Servidor (Reporte) ---")
    print(respuesta_reporte)
    print("-----------------------------------------")

except Exception as e:
    print(f"Cliente: Error al construir o enviar el reporte: {e}")
    import traceback
    traceback.print_exc()
