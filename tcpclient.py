import socket

def tcp_client(host, port, message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    client_socket.sendall(message.encode('utf-8'))

    data = client_socket.recv(1024).decode('utf-8')
    print(f"Received from server: {data}")

    client_socket.close()

if __name__ == "__main__":
    message_to_send = "Hello, Server!"
    tcp_client("localhost", 12345, message_to_send)
