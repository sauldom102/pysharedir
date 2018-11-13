import socket
import json
import os
import shutil

servidor = socket.socket()
servidor.bind(("", 9000))
servidor.listen(1)

socket_cliente, datos_cliente = servidor.accept()
print("Cliente {} conectado".format(datos_cliente))

ruta = "D:\\Users\\pablo\\Documents\\Servidor"

while True:
    datos_recibidos = socket_cliente.recv(1024)
    try:
        datos_recibidos = datos_recibidos.decode()
    except UnicodeDecodeError as e:
        print("UnicodeDecodeError: {}".format(e))
    try:
        datos_recibidos = json.loads(datos_recibidos)
        if type(datos_recibidos) is list:
            if datos_recibidos[0] == "add_dir":
                for d in datos_recibidos[1]:
                    os.makedirs(os.path.join(ruta, d))
            elif datos_recibidos[0] == "remove_dir":
                for d in datos_recibidos[1]:
                    shutil.rmtree(os.path.join(ruta, d))
    except (json.decoder.JSONDecodeError, UnicodeDecodeError):
        pass
    print(datos_recibidos)
