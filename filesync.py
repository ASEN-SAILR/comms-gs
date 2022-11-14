import os
import time

# while(1):

# 	os.system('rsync -avPz -e ssh /src/ user@remote:/path/to/dst')
# 	time.sleep(10)

def read_file():
    with open("test.txt", "r") as f:
        file = f.readlines()
    return file

initial = read_file()

while True:
	current = read_file()
	if initial != current:
		for line in current:
			if line not in initial:
				timstamp = time.time()
				print(timestamp-int(line))
				
		timestampstr = '\"\\n' + str(timestamp) + '\"'
		os.system('echo -e '+timestampstr+' >> test.txt')

		# initial = current
