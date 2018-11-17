import socket
import json
import os
import shutil
import time

servidor = socket.socket()
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

servidor.bind(("", 9000))
servidor.listen(1)

socket_cliente, datos_cliente = servidor.accept()
print("Cliente {} conectado".format(datos_cliente))

ruta = "/home/saul/example"

writing_file = False
while True:
	datos_recibidos = socket_cliente.recv(1024)

	try:
		if not writing_file:
			datos_recibidos = datos_recibidos.decode('utf-8', 'replace')

			# if type(datos_recibidos) is str:
			if datos_recibidos.startswith('NEW_FILE'):
				filename = ' '.join(datos_recibidos.split()[1:])
				writing_file = filename
				print('Seems to be a new file {}'.format(writing_file))
			else:
				datos_recibidos = json.loads(datos_recibidos)
				print(datos_recibidos)

				if type(datos_recibidos) is list:
					if datos_recibidos[0] == "add_dir":
						for d in datos_recibidos[1]:
							os.makedirs(os.path.join(ruta, d))
					elif datos_recibidos[0] == "remove_dir":
						for d in datos_recibidos[1]:
							shutil.rmtree(os.path.join(ruta, d))
		else:
			data = datos_recibidos.decode('utf-8', 'replace')

			if type(data) is str and data.endswith('END_OF_FILE'):
				print('Finish the writing of {}'.format(writing_file))
				writing_file = False
			else:
				print('writing file {}...'.format(writing_file))
				with open(os.path.join(ruta, writing_file), 'ab') as f:
					f.write(datos_recibidos)
	except (json.decoder.JSONDecodeError, UnicodeDecodeError) as e:
		pass	
