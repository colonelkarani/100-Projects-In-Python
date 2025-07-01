import socket
import threading

clients = "0.0.0.0"
port = 4200

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((clients, port))
server.listen(5)

def handler(client):
    with client as sock:
        command = input("Enter the command that you want to send:\n").encode("utf-8")
        sock.send(command)
        message = sock.recv(4096).decode("utf-8")
        if message and message.strip():
            print(f"message from the client is :\n{message.strip()}")
            handler(client)


while True:
    client, conn = server.accept()
    print(f"Received a connection from {conn[0]} : {conn[1]}")
    client_handler = threading.Thread(target=handler, args=(client, ))
    client_handler.start()
    