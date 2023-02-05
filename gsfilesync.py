import os
import time

# while(1):

#       os.system('rsync -avPz -e ssh /src/ user@remote:/path/to/dst')
#       time.sleep(10)


def read_file():
    with open("test.txt") as f:
        file = f.read().splitlines()
    return file


initial = read_file()

while True:
        current = read_file()
        if initial[-1:] != current[-1:]:
                timestamp = time.time()
                # print(timestamp-float(current[-1:][0]))

                os.system('echo -e '+str(timestamp)+' >> test.txt')
                initial = read_file()
        #os.system("sshpass -p 'asen4018' rsync -ave ssh /root/comms-gs/test.txt 192.168.56.102:/root/comms-gs/text.txt")
                os.system(
                    "sshpass -p 'asen4018' rsync -ave ssh /root/comms-gs/test.txt 192.168.56.102:/root/comms-gs/test.txt")
        time.sleep(1)
