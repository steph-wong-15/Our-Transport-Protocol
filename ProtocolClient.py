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

		self.seq_number = random.randint(0,100) # starting randomly generated sequence number
		self.ack_number = self.seq_number
		self.window_size = 10

	def perform_handshake(self):
		# Step 1: Send SYN to server
		# self.seq_number = self.seq_number
		# self.ack_number += len(data)
		print("Sending SYN to server")
		self.send_data("SYN", 0, 0)
		
		# Step 2: Receive SYN and ACK together from server
		print("Receiving SYN-ACK from server")
		ack_packet, recSequenceNumber, recAckNumber, recLength = self.receive_data()

		if ack_packet != "SYN-ACK":
			raise Exception("Handshake failed - SYN-ACK not received")

		# Step 3: Send ACK to server
		print("Sending ACK to server")
		self.sequence_number = recAckNumber
		self.ack_number = recSequenceNumber + len("SYN-ACK")
		self.send_data("ACK", recAckNumber, recLength)
		
	def calculate_checksum(self, data):
		checksum_result = zlib.crc32(data) & 0xFFFFFFFF 
		return checksum_result

	def verify_checksum(self, data, received_checksum):
		checksum_result = self.calculate_checksum(data)
		return checksum_result == received_checksum # return a boolean

	def receive_data(self, bufsize=1024, timeout=None):
		
		recPacket = self.client_socket.recv(bufsize)
		print(recPacket)
		recHeader = recPacket[:9]
		recChecksum, recSequenceNumber, recAckNumber, recLength = struct.unpack("!LHHB", recHeader)
		print(recLength)
		data = struct.unpack(f'{recLength}s',recPacket[9:9 + recLength])[0] # take the first value in the tuple of format ([0],) --> which is a double

		checksum_result = self.verify_checksum(data, recChecksum)
		data = data.decode('utf-8')

		return data, recSequenceNumber, recAckNumber, recLength
	
	def send_data(self, data, recAckNumber, recLength):
		
		if recAckNumber == 0:
			self.ack_number = self.ack_number
			self.seq_number = self.seq_number
		else:
			self.ack_number = self.seq_number + recLength
			self.seq_number = recAckNumber
		
		myChecksum = 0
		
		data_length = len(data)
		print("Send data: ", type(data))
		header = struct.pack("!LHHB", myChecksum, self.seq_number, self.ack_number, data_length)
		
		message = struct.pack(f'{data_length}s',  data.encode('utf-8'))
		myChecksum = self.calculate_checksum(header + message)

		header = struct.pack("!LHHB", myChecksum, self.seq_number, self.ack_number, data_length) 
		packet = header + message
		print(packet)
		self.client_socket.sendall(packet)
		
	def close(self):
		print("Closing socket")
		self.client_socket.close()

	def start(self):
		protocol.perform_handshake()

		message = input("Type here: ")
		protocol.send_data(message, 0, 0)
		modifiedSentence, recSequenceNumber, recAckNumber, recLength = protocol.receive_data()

		while True:
			message = input("Type here: ")
			protocol.send_data(message, recAckNumber, recLength)
			modifiedSentence, recSequenceNumber, recAckNumber, recLength = protocol.receive_data()
		
			print('From server: ', modifiedSentence)


if __name__ == "__main__":

	protocol = ProtocolClient("localhost", 1234)
	protocol.start()


