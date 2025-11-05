import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from clientSocket import ClientSocket
from Shared.message_builder import build_message, validate_message

client = ClientSocket()

params = {
    "codec": "G.711",
    "jitter (ms)": 20,
    "vRed (Mbps)": 300,
    "rR (ms)": 120
}

message = build_message("RT_REQUEST", params)

addr = ('127.0.0.1', 32003)

client.send_message(message, addr)

addr = ('127.0.0.1', 32004)

params = {
    "BWstRTP (Mbps)": 300,
    "BWstcRTP (Mbps)": 200,
    "Pmax (euros)": 1000,
    "Nllamadas (llamadas)": 30
}

message = build_message("COST_REQUEST", params)

client.send_message(message, addr)

message, address = client.recv_message(1024)

print(message)
