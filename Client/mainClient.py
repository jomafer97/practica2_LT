import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from clientSocket import ClientSocket
from Shared.message_builder import build_message, validate_message

client = ClientSocket()

message = build_message("RT_REQUEST", codec="G.711", jitter=20, netDelay=200)
addr = ("127.0.0.1", 32003)
client.send_message(message, addr)
message, address = client.recv_message(1024)
print("Respuesta RT_RESPONSE:")
print(message)
print("-" * 20)

message = build_message(
    "ERLANG_REQUEST",
    numLines=1200,
    numCalls=12000,
    avgDuration=3,
    blockingPercentage=0.03,
)
addr = ("127.0.0.1", 32004)
client.send_message(message, addr)
message, address = client.recv_message(1024)
print("Respuesta ERLANG_RESPONSE:")
print(message)
print("-" * 20)

message = build_message(
    "BW_REQUEST",
    codec="G.711",
    pppoe=False,
    vlan8021q=False,
    reservedBW=0.3,
    totalCalls=150 * 20,
)
addr = ("127.0.0.1", 32005)
client.send_message(message, addr)
message, address = client.recv_message(1024)
print("Respuesta BW_RESPONSE:")
print(message)
print("-" * 20)

callBW = {
    "RTP": message["uncompressed"]["callBW"],
    "cRTP": message["compressed"]["callBW"],
}
BWst = {"RTP": message["uncompressed"]["BWst"], "cRTP": message["compressed"]["BWst"]}

message = build_message("COST_REQUEST", callBW=callBW, BWst=BWst, Pmax=28390)
addr = ("127.0.0.1", 32006)
client.send_message(message, addr)
message, address = client.recv_message(1024)
print("Respuesta COST_RESPONSE:")
print(message)
print("-" * 20)

message = build_message(
    "PLR_REQUEST", bitstream="000001111110001101100000010000000111010111111110000110000"
)
addr = ("127.0.0.1", 32007)
client.send_message(message, addr)
message, address = client.recv_message(1024)
print("Respuesta PLR_RESPONSE:")
print(message)
print("-" * 20)


email = "el_email_del_usuario@mail.com"
rt_request = {"codec": "G.711", "jitter": 30.0, "netDelay": 10.0}
erlang_request = {
    "numLines": 10,
    "numCalls": 5,
    "avgDuration": 180.0,
    "blockingPercentage": 0.01,
}
bw_request = {
    "codec": "G.729",
    "pppoe": True,
    "vlan8021q": False,
    "reservedBW": 0.2,
    "totalCalls": 50,
}
cost_request = {
    "Pmax": 100.0,
    "callBW": {"RTP": 87200, "cRTP": 31200},
    "BWst": {"RTP": 4.36, "cRTP": 1.56},
}
plr_request = {"bitstream": "101010..."}
rt_response = {
    "rt2jit": "45.12",
    "rt1_5jit": "38.50",
    "csi": "15.00",
    "rphy": "10.00",
    "rpac": "5.00",
    "algD": None,
}
erlang_response = {"Erlangs": 1.23, "maxLines": 5}
bw_response = {
    "compressed": {"packetLength": 120, "callBW": 31200, "BWst": 1.56},
    "uncompressed": {"PacketLength": 320, "callBW": 87200, "BWst": 4.36},
    "pps": 50,
}
cost_response = {
    "mbpsCost": 22.94,
    "RTP": {"valid": True, "possibleCalls": 50},
    "cRTP": {"valid": True, "possibleCalls": 140},
}
plr_response = {"p": 0.01, "q": 0.5, "pi1": 0.02, "pi0": 0.98, "E": 1.5}

report_body = build_message(
    "REPORT_REQUEST",
    RT_REQUEST=rt_request,
    RT_RESPONSE=rt_response,
    ERLANG_REQUEST=erlang_request,
    ERLANG_RESPONSE=erlang_response,
    BW_REQUEST=bw_request,
    BW_RESPONSE=bw_response,
    COST_REQUEST=cost_request,
    COST_RESPONSE=cost_response,
    PLR_REQUEST=plr_request,
    PLR_RESPONSE=plr_response,
)

final_report_message = {"email": email, **report_body}

addr = ("127.0.0.1", 32008)

client.send_message(final_report_message, addr)
message, address = client.recv_message(1024)

print("Respuesta del REPORT_REQUEST:")
print(message)
print("-" * 20)
