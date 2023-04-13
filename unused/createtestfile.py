import os
import time

timestamp = time.time()
os.system('echo -e '+str(timestamp)+' >> test.txt')