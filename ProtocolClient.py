from socket import *
import struct
import threading
import time
import random
import zlib


class ProtocolClient:

	def __init__(self, server_name, server_port):
		self.client_socket = socket(AF_INET, SOCK_STREAM)
		self.client_socket.connect((server_name, server_port))

		self.seq_number = 0
		self.ack_number = random.randint(0,100) # starting randomly generated sequence number
		self.window_size = 10

	def perform_handshake(self):
		# Step 1: Send SYN to server
		print("Sending SYN to server")
		self.send_data("SYN")
		
		# Step 2: Receive SYN and ACK together from server
		print("Receiving SYN-ACK from server")
		ack_packet = self.receive_data()
		print(ack_packet)
		if ack_packet != "SYN-ACK":
		    raise Exception("Handshake failed - SYN-ACK not received")

		# Step 3: Send SYN to server
		print("Sending SYN to server")
		self.send_data("SYN")
		
	def verify_checksum(self, data):
		checksum_result = zlib.crc32(data) & 0xFFFFFFFF
		return checksum_result == data # return a boolean

	def receive_data(self, bufsize=1024, timeout=None):
		
		recPacket = self.client_socket.recv(bufsize)
		recChecksum, recSequenceNumber, recAckNumber = struct.unpack(recPacket)                
		unsignedCharSize = struct.calcsize("c") # calculate size in bytes of an unsigned char
		data = struct.unpack("c", recPacket[48:48 + unsignedCharSize])[0] # take the first value in the tuple of format ([0],) --> which is a double


	def send_data(self, data):
		
		myChecksum = 0

		header = struct.pack("!HHH", myChecksum, self.seq_number, self.ack_number) 
		message = struct.pack("c", data.encode('utf-8'))
		
		myChecksum = self.verify_checksum(header + message)
		
		header = struct.pack("!HHH", myChecksum, self.seq_number, self.ack_number) 
		packet = header + message
		
		self.client_socket.sendall(packet)
		
	def close(self):
		print("Closing socket")
		self.client_socket.close()
		

if __name__ == "__main__":

    protocol = ProtocolClient("localhost", 1234)
    message = "a"
    #protocol.perform_handshake()
    protocol.send_data(message)
    #modifiedSentence = protocol.receive_data()
    #print('From Server: ', modifiedSentence)


