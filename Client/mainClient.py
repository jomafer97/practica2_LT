import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from clientSocket import ClientSocket
from Shared.message_builder import build_message, validate_message

client = ClientSocket()

message = build_message(
    "ERLANG_REQUEST",
    numChannels=150,             # 100 lineas
    numCalls=20,                # 500 Llamadas por hora
    avgDuration=180,             # Duración promedio de la llamada: 180 segundos (3 minutos)
    blockingPercentage=0.03         # Porcentaje máximo de bloqueo tolerado: 1%
)

addr = ('127.0.0.1', 32004)

client.send_message(message, addr)

message, address = client.recv_message(1024)

print(message)

message = build_message(
    "BW_REQUEST",
    codec="G.711",
    extendedHeader=0,
    maxNumCalls=180,
    ReservedBW=60
)

addr = ('127.0.0.1', 32005)

client.send_message(message, addr)

message, address = client.recv_message(1024)

print(message)

message = build_message(
    "COST_REQUEST",
    BWstRTP=300,             # 100 lineas
    BWstcRTP=150,                # 500 Llamadas por hora
    Pmax=500,             # Duración promedio de la llamada: 180 segundos (3 minutos)
    numCalls=100         # Porcentaje máximo de bloqueo tolerado: 1%
)

addr = ('127.0.0.1', 32006)

client.send_message(message, addr)

message, address = client.recv_message(1024)

print(message)
