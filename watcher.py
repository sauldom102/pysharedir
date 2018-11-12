import os
import time
import socket
import json

if __name__ == "__main__":
	with socket.socket() as s:
		s.connect(('10.10.1.6', 9000))

		path_to_watch = "/home/saul/Desktop"

		before_dirs = []
		before_files = []
		for root, dirs, files in os.walk(path_to_watch, topdown=False):
			for _dir in dirs:
				before_dirs.append(os.path.join(root, _dir)[len(path_to_watch) + 1:])
			for f in files:
				before_files.append(os.path.join(root, f)[len(path_to_watch) + 1:])
			
		while True:
			time.sleep (5)
			after_dirs = []
			after_files = []
			for root, dirs, files in os.walk(path_to_watch, topdown=False):
				for _dir in dirs:
					after_dirs.append(os.path.join(root, _dir)[len(path_to_watch) + 1:])
				for f in files:
					after_files.append(os.path.join(root, f)[len(path_to_watch) + 1:])

			added_dirs = ('add_dir', [f for f in after_dirs if not f in before_dirs])
			removed_dirs = ('remove_dir', [f for f in before_dirs if not f in after_dirs])

			added_files = ('add_file', [f for f in after_files if not f in before_files])
			removed_files = ('remove_file', [f for f in before_files if not f in after_files])
			
			if added_dirs[1]:
				s.send(json.dumps(added_dirs).encode(), 1024)
			if removed_dirs[1]:
				s.send(json.dumps(removed_dirs).encode(), 1024)
			if added_files[1]:
				s.send(json.dumps(added_files).encode(), 1024)
				for filename in added_files[1]:
					with open(os.path.join(path_to_watch, filename), 'rb') as f:
						s.sendfile(f)
			if removed_files[1]:
				s.send(json.dumps(removed_files).encode(), 1024)
			
			before_dirs = after_dirs
			before_files = after_files