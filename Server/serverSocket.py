import json
from socket import *

class ServerSocket:
    def __init__(self, IP, port):
        self.serverSocket = socket(AF_INET, SOCK_DGRAM)
        self.serverSocket.bind((IP, port))

    def recv_message(self, bytes):
        message, address = self.serverSocket.recvfrom(bytes)

        message_str = message.decode("utf-8")
        json_data = json.loads(message_str)

        return json_data, address

    def send_message(self, json_data, addr):
        try:
            self.serverSocket.sendto(json.dumps(json_data).encode('utf-8'), addr)
        except Exception:
            print("Invalid format")

    def close(self):
        self.serverSocket.close()
