from clientSocket import ClientSocket

client = ClientSocket()

datos_a_enviar = {
    "codec": "G.711"
}

addr = ('127.0.0.1', 32003)

client.send_message(datos_a_enviar, addr)

client.close()
