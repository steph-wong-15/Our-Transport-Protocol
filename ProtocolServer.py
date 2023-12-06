from socket import *
import struct
import threading
import time
import zlib
import random

class ProtocolServer:
	def __init__(self, host, port):
		self.server_socket = socket(AF_INET, SOCK_STREAM) # create welcoming socket
		self.server_socket.bind((host, port))
		self.server_socket.listen(1) # server begins listening to incoming requests

		self.sequence_number = random.randint(0,100) # starting randomly generated sequence number
		self.ack_number = 0

	def perform_handshake(self, client_socket):
		# Step 1: Receive SYN from client
		syn_packet, recSequenceNumber, recAckNumber = self.receive_data(client_socket)
		if syn_packet != "SYN":
			raise Exception("Handshake failed - SYN not received")
		
		# Step 2: Send a SYN and ACK together from server
		#self.sequence_number = recAckNumber
		#self.ack_number = recSequenceNumber + len("SYN")
		print("Send SYN-ACK to client")
		self.send_data(client_socket, "SYN-ACK")
		
		# Step 3: Receive ACK from the client
		ack_packet, recSequenceNumber, recAckNumber  = self.receive_data(client_socket)
		if ack_packet != "ACK":
			raise Exception("Handshake failed - ACK not received")
		
	def handle_client(self, client_socket, client_address):
		self.perform_handshake(client_socket)
		print("Handshake done")
		while True:
					data, recSequenceNumber, recAckNumber = self.receive_data(client_socket, 1024, timeout=5)
					print(f"Received from client: {data}")
					# Received an indication to close connection from the client
					if data == "FIN":

							# Server sends FIN
							#self.sequence_number += 1
							#self.ack_number += len("FIN")
							self.send_data(client_socket, "FIN-ACK")

							# Receive ACK from client (add timeout)
							ack_packet, recSequenceNumber, recAckNumber = self.receive_data(client_socket, timeout=5)
							if ack_packet != "ACK":
									raise Exception("Failed to received ACK after FIN-ACK")
							
							# Close connection
							self.close_connection()


	def calculate_checksum(self, data):
		checksum_result = zlib.crc32(data) & 0xFFFFFFFF 
		return checksum_result

	def verify_checksum(self, data, received_checksum):
		checksum_result = self.calculate_checksum(data)
		return checksum_result == received_checksum # return a boolean

	def send_ack(self, client_socket, sequence_number):
		ack_packet = f"ACK {sequence_number}"
		self.send_data(client_socket, ack_packet, sequence_number)

	def receive_data(self, client_socket, bufsize=1024, timeout=None):
		recPacket = client_socket.recv(1024)
		recHeader = recPacket[:9]
		recChecksum, recSequenceNumber, recAckNumber, recLength = struct.unpack("!LHHB", recHeader) 
		# data = client_socket.recv(bufsize).decode()
		print(recLength)
		data = struct.unpack(f'{recLength}s', recPacket[9:9 + recLength])[0] # take the first value in the tuple of format ([0],) --> which is a double

		print(f"Checksum: {recChecksum}")
		print(f"Sequence Number: {recSequenceNumber}")
		print(f"Acknowledgment Number: {recAckNumber}")
		print(f"String: {data}")

		checksum_result = self.verify_checksum(data, recChecksum)
		data = data.decode('utf-8')
		
		self.sequence_number += 1
		self.ack_number += len(data)

		if (data == "ACK" or data == "NAK" or data == "SYN" or data == "FIN"):
			return data, recSequenceNumber, recAckNumber
		else:
			capitalizedSentence = data.upper()
			self.send_data(client_socket, capitalizedSentence)
			return data, recSequenceNumber, recAckNumber

	def send_data(self, client_socket, data):
		
		myChecksum = 0

		data_length = len(data)

		# Header is checksum (16), sequence_number (16), ack_number (16)
		header = struct.pack("!LHHB", myChecksum, self.sequence_number, self.ack_number, data_length)
		
		message = struct.pack(f'{data_length}s', data.encode('utf-8'))
		myChecksum = self.calculate_checksum(header + message)

		header = struct.pack("!LHHB", myChecksum, self.sequence_number, self.ack_number, data_length) 
		packet = header + message
		print(packet)
		client_socket.sendall(packet)

	def close_connection(self):
		self.server_socket.close()

	def start(self):
		print("Server listening")
		while True:
			client_socket, client_address = self.server_socket.accept()
			print(f"Connection from {client_address}")
			self.handle_client(client_socket,client_address)
			client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))


if __name__ == "__main__":
	protocol = ProtocolServer("localhost", 1234)
	protocol.start()
