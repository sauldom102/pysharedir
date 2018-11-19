import os
import time
import socket
import json
from io import BufferedReader

def get_files_and_dirs(path):
	_dirs_list = []
	_files_list = []

	for root, dirs, files in os.walk(path, topdown=False):
		for _dir in dirs:
			_dirs_list.append(os.path.join(root, _dir)[len(path) + 1:])
		for f in files:
			_files_list.append(os.path.join(root, f)[len(path) + 1:])

	return (_files_list, _dirs_list)

if __name__ == "__main__":
	with socket.socket() as s:
		s.connect(('10.10.1.6', 9000))

		path_to_watch = "/home/saul/Desktop"
		
		before_files, before_dirs = get_files_and_dirs(path_to_watch)
			
		while True:
			time.sleep (7)

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
					print(filename)
					with open(os.path.join(path_to_watch, filename), 'rb') as f:
						bytesize = os.path.getsize(f.name)

						msg = 'NEW_FILE {} ||| {}'.format(filename, bytesize)
						s.send(msg.encode() + (' '*(1024 - len(msg))).encode())
						s.sendfile(f)
						s.send((' '*(bytesize % 1024)).encode())
			if removed_files[1]:
				print(removed_files)
				s.send(json.dumps(removed_files).encode(), 1024)
			
			before_dirs = after_dirs
			before_files = after_files