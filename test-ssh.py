import os

os.system("sshpass -p 'asen-sailr' rsync -ave ssh test.txt 169.254.179.9:/sailr/test.txt")
