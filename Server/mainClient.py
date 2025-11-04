from clientSocket import ClientSocket

client = ClientSocket()

datos_a_enviar = {
    "codec": "G.711",
    "bitrate": 64.0,
    "mensaje": "Prueba de JSON UDP"
}
