import os
import time

# while(1):

# 	os.system('rsync -avPz -e ssh /src/ user@remote:/path/to/dst')
# 	time.sleep(10)

def read_file():
    with open("test.txt") as f:
        file = f.read().splitlines()
    return file

initial = read_file()

while True:
	current = read_file()
	if initial[-1:] != current[-1:]:
		timestamp = time.time()
		print(timestamp-float(current[-1:][0]))
				
		os.system('echo -e '+str(timestamp)+' >> test.txt')
		initial = read_file()
	
	
