import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from clientSocket import ClientSocket
from Shared.message_builder import build_message, validate_message

client = ClientSocket()

message = build_message("RT_REQUEST", codec="G.711", jitter=20, networkSpeed=100, networkDelay=20)
print(message)
addr = ('127.0.0.1', 32003)

client.send_message(message, addr)

addr = ('127.0.0.1', 32004)

message = build_message("ERLANG_REQUEST", numChannels=20, numCalls=10, avgDuration=5, blockingPercentage=2)
print(message)
client.send_message(message, addr)

message, address = client.recv_message(1024)

print(message)
