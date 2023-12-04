from socket import *
import struct
import threading
import time

class ProtocolServer:
    def __init__(self, host, port):
        self.server_socket = socket(AF_INET, SOCK_STREAM) # create welcoming socket
        self.server_socket.bind((host, port))
        self.server_socket.listen(1) # server begins listening to incoming requests


    def perform_handshake(self, client_socket):
        # Step 1: Receive SYN from client
        syn_packet = self.receive_data(client_socket)
        if syn_packet != "SYN":
            raise Exception("Handshake failed - SYN not received")
        
        # Step 2: SYN_ACK from server --> add step before:  chnage it to send SYN, and then ACK
        ack_packet = self.receive_data(client_socket)
        if ack_packet != "ACK":
            raise Exception("Handshake failed - ACK not received")
        
    def handle_client(self, client_socket, client_address):
        self.perform_handshake(client_socket)

        while True:
            data = self.receive_data(client_socket, 1024, timeout=5)
            
            if data == "FIN":
                self.send_data(client_socket, "ACK")
                break

        # Server sends FIN
        self.send_data(client_socket, "FIN") #+ send ACK

        # Receive ACK from client (add timeout)
        ack_packet = self.receive_data(client_socket, timeout=5)
        if ack_packet != "ACK":
            raise Exception("Failed to received ACK after FIN")
        
        # Close connction
        self.close_connection(client_socket, client_address)

    def receive_data(self, client_socket, bufsize=1024, timeout=None):
        data = client_socket.recv(bufsize).decode('utf-8')

    def send_data(self, client_socket, data):
        message = data.encode('utf-8')
        length = len(message)
        header = struct.pack("!I", length)  # Use a 4-byte header for message length
        packet = header + message

        client_socket.sendall(packet)

    def close_connection(self, client_socket, client_address): # probably just .close() since FIN+ACK is done
        # Server get FIN packet from client
        fin_packet = self.receive_data(client_socket, timeout=5)
        if fin_packet == "FIN":
            self.send_data(client_socket, "ACK")
            # NEED TO close client socket in client side

    def start(self):
        print("Server listening")
        while True:
            client_socket, client_address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))

if __name__ == "__main__":
    protocol = ProtocolServer("localhost", 1234)
    protocol.start()