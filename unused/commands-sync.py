import os

system_password = 'asen4018'
sender_path = '/root/comms-gs/test.txt'
receiver_ip = '192.168.56.102'
receiver_path = receiver_ip+':/root/comms-gs/test.txt'

# os.system("sshpass -p '"+system_password+"' rsync -ave ssh /root/comms-gs/test.txt 192.168.56.102:/root/comms-gs/test.txt")
os.system("sshpass -p '"+system_password+"' rsync -ave ssh "+sender_path+" "+receiver_path)


