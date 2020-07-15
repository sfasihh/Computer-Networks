import socket													# import socket
from collections import namedtuple								
import pickle
from time import sleep

PDU = namedtuple('PDU', ['data_type', 'data'])
port = 60000													# reserve port for service
s = socket.socket(socket.SOCK_DGRAM)							# create socket object
host = socket.gethostname()										# get local host name
s.bind(('192.168.107.1', port))									# bind to port
s.listen(5)														# listen for client connection
print('Server listening...')

Files_List = namedtuple('Files_List', ['peer_name', 'file_name', 'address'])
fList = []
print(s)
conn, addr = s.accept()											# Establish connection with client

while True:
	# receive data from client
	r = conn.recv(1024)
	# convert to binary
	r = pickle.loads(r)
	# extract data type
	type = r.data_type
	#extract data
	data = r.data
	
	# Registration
	if (type == 'R'):
		# set file_exists to boolean expression
		file_exists = False
		# iterate through list
		for i in fList:
			# If file exists
			if i[0] == data.get('peer_name') and i[1] == data.get('file_name'):
				# True
				file_exists = True 
				break 
		
		# Error PDU
		if (file_exists):
			error = PDU('E', "Error Message from server: Username and file already exists in list, please pick another username/file combination")
			conn.send(pickle.dumps(error))
		
		# ACK PDU
		else:
			fList.append((data.get('peer_name'), data.get('file_name'), data.get('address')))
			apdu = PDU('A', "ACK Message from server: Successfully registered on list")
			conn.send(pickle.dumps(apdu))
			print(fList)
			
			
	elif (type == 'T'):																# De-Register

		file_deleted = False														# Boolean expression for deleted files
		index = 0
		for i in fList:																# Iterate through fList (registered content)
			# Check if peer name and filename from fList matches inputted username of peer and filename (from peer prog)
			if i[0] == data.get('peer_name') and i[1] == data.get('file_name'):
				print("Found file to delete")										
				print(fList)						
				index = i															# index is the existing tuple of peer and file
				file_deleted = True													# file deleted
						
		if (file_deleted):															# if this file exists
			list_Flist = list(fList)												# convert tuple fList to list
			list_Flist.remove(index)												# Remove index from fList (de-register filename)
			fList = tuple(list_Flist)												# Convert back to tuple
			
			print("file deleted")
			print(fList)
			apdu = PDU ('A', "successfully removed from list")						# build A-type PDU, success case
			conn.send(pickle.dumps(apdu))											# Send to peer prog
			
		else:																		# If file does not exist
			error = PDU('E', "Error: Could not remove file")						# Build error PDU
			conn.send(pickle.dumps(error))											# Send to peer prog

	elif (type == 'S'):
		file_found = False														# Boolean expression for deleted files
		element_to_send = ""
		index = 0
		for i in fList:																# Iterate through fList (registered content)
			# Check if peer name and filename from fList matches inputted username of peer and filename (from peer prog)
			if i[1] == data.get('file_name'):
				element_to_send = i
				index = i															# index is the existing tuple of peer and file
				file_found = True													# file deleted
						
		if (file_found):															# if this file exists
			print ("file found.. sending...")
			print(element_to_send)
			spdu = PDU('S', element_to_send[2])
			print(spdu)
			conn.send(pickle.dumps(spdu))			
			
		else:
			error = PDU('E', "Error: Could not find file to download")						# Build error PDU
			conn.send(pickle.dumps(error))
	
	# On-Line list of registered files		
	elif (type == 'O'):
		print("Entered O")
		# retrieve peer name and filename from flist
		o_fList = [(i[0], i[1]) for i in fList]
		print("got list")
		# build O type PDU with the retrieved elements
		opdu = PDU('O', o_fList)
		print("sending response")
		# send to peer
		conn.sendall(pickle.dumps(opdu))
		
		print("sent o type")
		
	else:
		error = PDU('E', "Error")
		conn.send(pickle.dumps(error))
			