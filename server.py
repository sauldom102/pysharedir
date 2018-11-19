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
byte_counter = 0
byte_size = 0
while True:
	datos_recibidos = socket_cliente.recv(1024)

	try:
		data_str = datos_recibidos.decode('utf-8', 'replace')

		if data_str.startswith('NEW_FILE'):
			print(data_str)
			filename = data_str[data_str.index(' ') + 1:data_str.index('|||') - 1]
			byte_size = int(data_str[data_str.index('|||') + 4:])
			writing_file = filename
			print('Seems to be a new file {} ({})'.format(writing_file, byte_size))
		else:
			data_json = json.loads(data_str)
			print(data_json)

			if type(data_json) is list:
				if data_json[0] == "add_dir":
					for d in data_json[1]:
						os.makedirs(os.path.join(ruta, d))
				elif data_json[0] == "remove_dir":
					for d in data_json[1]:
						shutil.rmtree(os.path.join(ruta, d))
				elif data_json[0] == "remove_file":
					for f in data_json[1]:
						os.remove(os.path.join(ruta, f))
						
	except (json.decoder.JSONDecodeError, UnicodeDecodeError) as e:
		if writing_file:
		
			with open(os.path.join(ruta, writing_file), 'ab') as f:
				byte_counter += len(datos_recibidos)
				f.write(datos_recibidos)
			
			if byte_counter < byte_size:
				print('writing file {}... ({} / {})'.format(writing_file, byte_counter, byte_size))
				pass
			else:
				print('Finished file {}'.format(writing_file))
				writing_file = False
				byte_counter = 0
