import os
import time
import socket
import json

def _get_file_lines(file_path):
	if os.path.isfile(file_path):
		with open(file_path, 'r') as f:
			return f.read().splitlines()
	
	return []

def _get_file_extensions(file_content):
	for f in file_content:
		splitted = f.split('.')
		if len(splitted) >= 2 and splitted[0] == '*':
			yield '.'.join(splitted[1:])

def get_files_and_dirs(path):
	_dirs_list = []
	_files_list = []
	
	fileallow_path = os.path.join(path, '.fileallow')
	fileignore_path = os.path.join(path, '.fileignore')

	_fileallow = _get_file_lines(fileallow_path)
	_fileignore = _get_file_lines(fileignore_path)

	for root, dirs, files in os.walk(path, topdown=False):
		for _dir in dirs:
			rel_dir = os.path.join(root, _dir)[len(path) + 1:]

			if rel_dir not in _fileignore:
				_dirs_list.append(rel_dir)
		for f in files:
			if f not in ('.fileallow', '.fileignore'):
				file_rel_path = os.path.join(root, f)[len(path) + 1:]
				filedir = os.path.split(file_rel_path)[0]
				file_ext = os.path.splitext(file_rel_path)[1][1:]
				
				if len(_fileallow) > 0:
					if (file_ext in list(_get_file_extensions(_fileallow))) or (file_rel_path in _fileallow):
						_files_list.append(file_rel_path)

				elif len(_fileignore) > 0:
					if (file_rel_path not in _fileignore) and (filedir not in _fileignore) and (file_ext not in list(_get_file_extensions(_fileignore))):
						_files_list.append(file_rel_path)
				else:
					_files_list.append(file_rel_path)

	return (_files_list, _dirs_list)

def remove_contents(file_path):
	with open(file_path, 'w') as f:
		f.write('')

if __name__ == "__main__":
	with socket.socket() as s:
		server_ip = input('Enter the server IP: ')

		s.connect((server_ip, 9000))

		path_to_watch = input('Enter the path you want to watch: ')
		
		before_files, before_dirs = get_files_and_dirs(path_to_watch)
		# before_files, before_dirs = [], []
			
		while True:
			time.sleep (5)

			after_files, after_dirs = get_files_and_dirs(path_to_watch)

			added_dirs = ('add_dir', [f for f in after_dirs if not f in before_dirs])
			removed_dirs = ('remove_dir', [f for f in before_dirs if not f in after_dirs])

			added_files = ('add_file', [f for f in after_files if not f in before_files])
			removed_files = ('remove_file', [f for f in before_files if not f in after_files])
			
			if added_dirs[1]:
				print(added_dirs)
				s.send(json.dumps(added_dirs).encode())
			if removed_dirs[1]:
				print(removed_dirs)
				s.send(json.dumps(removed_dirs).encode())
			if added_files[1]:
				print(added_files)
				# s.send(json.dumps(added_files).encode())
				for filename in added_files[1]:
					file_path = os.path.join(path_to_watch, filename)
					with open(file_path, 'rb') as f:
						bytesize = os.path.getsize(f.name)
						mbsize = bytesize / 1e6
						s_time = time.time()
						print('Sending {} with a size of {}MB'.format(filename, mbsize))

						msg = 'NEW_FILE {} ||| {}'.format(filename, bytesize)
						msg += ' '*(1024 - len(msg))
						s.send(msg.encode())
						content = f.read(1024)
						s.send(content)
						while True:
							content = f.read(1024)
							len_content = len(content)

							if len_content == 0:
								break

							if len_content != 1024:
								content += b' '*(1024 - len_content)
							s.send(content)

						f_time = time.time() - s_time
						print('File {} sent successfully in {} seconds ({}MB/s)'.format(filename, f_time, round(mbsize/f_time, 2)))
						remove_contents(file_path)
			if removed_files[1]:
				print(removed_files)
				s.send(json.dumps(removed_files).encode())
			
			before_dirs = after_dirs
			before_files = after_files