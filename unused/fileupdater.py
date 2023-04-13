import os
import time

timestamp = '\"\\n' + str(time.time())+'\"'
print(timestamp)
os.system('echo -e '+timestamp+' >> test.txt')
