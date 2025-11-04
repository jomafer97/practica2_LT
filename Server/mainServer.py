from serverSocket import ServerSocket
import time

server = ServerSocket('', 32003)

message = {
    "codec": "G.711",
    "bitrate": 64.0,
    "mensaje": "Prueba de JSON UDP"
}

while True:
    message, addr = server.recv_message(1024)

    message_str = message.decode("utf-8")

    print(message_str + '\n')
    print(f"{addr}\n")

    if message_str == "Bye":
        time.sleep(5)
        server.close()
        break
