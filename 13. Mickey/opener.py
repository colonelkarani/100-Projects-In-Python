import socket
host = "0.0.0.0"
port = 80

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(5)
while True:
    client, addr = server.accept()
    print(f"received a ocnnection from {addr[0]}: {addr[1]}")
    command = "dir"
    client.send(command.encode("utf-8"))
    message = client.recv(4096).decode("utf-8")
    print(message)
    client.close()
    break