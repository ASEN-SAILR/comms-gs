import sys
sys.path.append('/home/ground-station/automation')
# Considering your module contains a function called my_func, you could import it:
from RoverComms import RoverComms


# start reading commands from commands log
# leaving these in for testing on automation end but should be taken out
commands_path = r"~/commands.txt"
telemetry_path = r"~/telemetry.txt"
# onboard computer comms vars
obcCommandPath = commands_path
obcTelemPath = telemetry_path
obcVideoPath = "~/video"
obcImagePath = "~/images"
#currCmdNum = 0 #not needed, automatically defined in RoverComms
# ground station comms vars
gs_ssh_password = "asen-sailr"
# gs_ip = "192.168.56.102"
gs_ip = '127.0.1.1'
gs_home_path = "/home/ground-station/asen-sailr/"
gs_telem_path = gs_home_path+"telemetry.txt"
gs_video_path = gs_home_path+"videos"
gs_image_path = gs_home_path+"images"
comms = RoverComms(obcCommandPath,obcTelemPath,obcVideoPath,obcImagePath,gs_ssh_password,gs_ip,gs_telem_path,gs_video_path,gs_image_path)

comms.liveVideoServer()
