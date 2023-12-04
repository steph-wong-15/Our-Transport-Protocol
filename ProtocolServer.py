from socket import *
import struct
import threading
import time
import zlib

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
        
        # Step 2: Send a SYN and ACK together from server
        self.send_data(client_socket, "SYN-ACK")
        
        # Step 3: Receive ACK from the client
        ack_packet = self.receive_data(client_socket)
        if ack_packet != "ACK":
            raise Exception("Handshake failed - ACK not received")
        
    def handle_client(self, client_socket, client_address):
        self.perform_handshake(client_socket)

        data = self.receive_data(client_socket, 1024, timeout=5)
        
        # Received an indication to close connection from the client
        if data == "FIN":

            # Server sends FIN
            self.send_data(client_socket, "FIN-ACK")

            # Receive ACK from client (add timeout)
            ack_packet = self.receive_data(client_socket, timeout=5)
            if ack_packet != "ACK":
                raise Exception("Failed to received ACK after FIN-ACK")
            
            # Close connection
            self.close_connection()

        else:
            if self.verify_checksum(data):
                print("Checksum verified")
                self.send_data(client_socket, "ACK")

            else:
                print("Failed to verify checksum")

    def close_connection(self):
        self.server_socket.close()

    def verify_checksum(self, data):
        checksum_result = zlib.crc32(data.encode('utf-8')) & 0xFFFFFFFF 
        return checksum_result == data # return a boolean

    def receive_data(self, client_socket, bufsize=1024, timeout=None):
        data = client_socket.recv(bufsize).decode('utf-8')

        if (data == "ACK" or data == "NAK" or data == "SYN" or data == "FIN"):
            return data
        else:
            capitalizedSentence = data.upper()
            client_socket.send_data(client_socket, capitalizedSentence)
            return data

    def send_data(self, client_socket, data):
        message = data.encode('utf-8')
        length = len(message)
        header = struct.pack("!I", length)  # Use a 4-byte header for message length
        packet = header + message

        client_socket.sendall(packet)

    def start(self):
        print("Server listening")
        while True:
            client_socket, client_address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))

if __name__ == "__main__":
    protocol = ProtocolServer("localhost", 1234)
    protocol.start()