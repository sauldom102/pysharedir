import socket
import json
import os
import shutil
from threading import Thread

class Client(Thread):

	CHUNK_SIZE = 1024
	writing_file = False
	byte_counter = 0
	byte_size = 0

	def __init__(self, sckt, clt_data, save_path):
		super().__init__()
		self.sckt = sckt
		self.clt_data = clt_data
		self.save_path = save_path

		print("Cliente {} conectado".format(clt_data))

	def run(self):
		while True:
			datos_recibidos = self.sckt.recv(self.CHUNK_SIZE)

			try:
				if not self.writing_file:
					data_str = datos_recibidos.decode()

					if data_str.startswith('NEW_FILE'):
						filename = data_str[data_str.index(' ') + 1:data_str.index('|||') - 1]
						self.byte_size = int(data_str[data_str.index('|||') + 4:])
						self.writing_file = filename
						print('Seems to be a new file {} ({})'.format(self.writing_file, self.byte_size))
					else:
						data_json = json.loads(data_str)
						print(data_json)

						if type(data_json) is list:
							if data_json[0] == "add_dir":
								for d in data_json[1]:
									os.makedirs(os.path.join(self.save_path, d))
							elif data_json[0] == "remove_dir":
								for d in data_json[1]:
									rel_dir = os.path.join(self.save_path, d)
									if os.path.isdir(rel_dir):
										shutil.rmtree(rel_dir)
							elif data_json[0] == "remove_file":
								for f in data_json[1]:
									rel_file = os.path.join(self.save_path, f)
									if os.path.isfile(rel_file):
										os.remove(rel_file)
				else:
					with open(os.path.join(self.save_path, self.writing_file), 'ab') as f:
						self.byte_counter += self.CHUNK_SIZE
						if self.byte_counter == self.byte_size:
							datos_recibidos = datos_recibidos.strip()
						f.write(datos_recibidos)
					
					if not self.byte_counter < self.byte_size:
						print('Finished file {}'.format(self.writing_file))
						self.writing_file = False
						self.byte_counter = 0
			except (json.decoder.JSONDecodeError, UnicodeDecodeError) as e:
				pass

servidor = socket.socket()
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

servidor.bind(("", 9000))
servidor.listen(1)

while True:
	sock, client_data = servidor.accept()
	save_path = input('Enter the directory where you want to receive the files: ')
	t = Client(sock, client_data, save_path)
	t.start()