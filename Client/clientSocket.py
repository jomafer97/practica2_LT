import json
from socket import *

class ClientSocket:
    def __init__(self):
        self.clientSocket = socket(AF_INET, SOCK_DGRAM)

    def recv_message(self, bytes):
        message, address = self.clientSocket.recvfrom(bytes)

        message_str = message.decode("utf-8")
        json_data = json.loads(message_str)

        return json_data, address

    def send_message(self, json_data, addr):
        self.clientSocket.sendto(json.dumps(json_data).encode('utf-8'), addr)

    def close(self):
        self.clientSocket.close()
