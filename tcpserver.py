import socket

def tcp_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        data = client_socket.recv(1024).decode('utf-8')
        if not data:
            break

        print(f"Received from client: {data}")

        client_socket.sendall(data.encode('utf-8'))
        client_socket.close()

    server_socket.close()

if __name__ == "__main__":
    tcp_server("localhost", 12345)
