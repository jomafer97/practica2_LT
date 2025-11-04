from serverSocket import ServerSocket
import time
import json

# Cargamos el diccionario
with open('codec_db.json', 'r') as file:
    codec_db = json.load(file)

server = ServerSocket('', 32003)

message, addr = server.recv_message(1024)

recv_codec = message["codec"]
print(f"El códec recibido ha sido: {recv_codec}")

print("Los parámetros de este códec son:")

print(json.dumps(codec_db[recv_codec], indent=2, sort_keys=False))

time.sleep(5)
server.close()
