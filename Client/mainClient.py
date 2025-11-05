from clientSocket import ClientSocket
import json

client = ClientSocket()

datos_a_enviar = {
    "codec": "G.711"
}

addr = ('127.0.0.1', 32003)

client.send_message(datos_a_enviar, addr)

addr = ('127.0.0.1', 32004)

client.send_message(datos_a_enviar, addr)

message, address = client.recv_message(1024)

print(message)
