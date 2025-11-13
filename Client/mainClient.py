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
    numLines=150,
    numCalls=20,
    avgDuration=180,
    blockingPercentage=0.03
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