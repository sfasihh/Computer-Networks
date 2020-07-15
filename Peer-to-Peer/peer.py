import socket														# Import socket module
from collections import namedtuple									# namedtuple from collections
import os
import pickle
import sys, select

s = socket.socket(socket.SOCK_DGRAM)								# Create socket object
host = socket.gethostname()											# get local host name
port = 60000														# REserver port for service
addr = (('192.168.107.1', port))									# Address: IP address + port
print("connecting to adddr")
s.connect((addr))													# connect 
PDU = namedtuple('PDU', ['data_Type', 'data'])						# Build PDU
#print("sending tuple")
#msg = s.recv(100)

#print(msg)


def reset_connection():
	s = socket.socket(socket.SOCK_DGRAM)
	host = socket.gethostname()
	port = 60000
	addr = (('192.168.107.1', port))
	s.connect((addr))	

def select_name():
	return input('Please enter preferred username: ')
	
def file_name():
	return input('Filename: ')
	
def de_register(username, file_name):
	# Build T-PDU for de-registration
	t = PDU(data_Type = 'T', data = {'peer_name': username, 'file_name': file_name, 'address': addr})
	# Convert T-PDU to binary
	t = pickle.dumps(t)
	# send to index server
	s.send(t)
	print("Done sending T PDU")
	# Receive response from index server
	rec = s.recv(1024)
	# Convert to original from binary
	sp = pickle.loads(rec)
	# assign data_type to sr
	sr = sp.data_Type
	# assign data to sd
	sd = sp.data
	ft = pickle.loads(t)
	type = ft.data_Type
	# Retrieve file name from data
	f = ft.data.get('file_name')
	print('Filename: ', str(f))
	print(sd)
	
def download_file(file_name, address, destination):
	# establish new TCP connection
	s1 = socket.socket()
	# Build D type PDU with target file
	dpdu = PDU(data_Type = 'D', data = {'peer_name': username, 'file_name': file_name})
	# Connect to peer address
	s1.connect(address)
	# convert pdu to binary
	pdu = pickle.dumps(dpdu)
	
	print("sending Type D request")
	# Send to peer
	s1.send(pickle.dumps(pdu))
	
		
# Select username
username = select_name()
#file_name = file_name()

# create new TCP connection (for peer to peer)
ss = socket.socket()
# Peer's port address
serverPort = int(input('Please enter listening port number: '))
paddr = (('192.168.107.1', serverPort))

try:
	ss.bind((paddr))
except Exception:
	pass
ss.listen(5)

inputs = []
outputs = []
exp = []

inputs.append(ss)
exp.append(ss)

timeout = 1
#s.setblocking(1)

# Service loop
while True:
	#reset_connection()
	print('waiting for the next event', file=sys.stderr)
	readable, writable, exceptional = select.select(inputs, outputs, exp, timeout)	
	for sock in readable:
		if sock is ss:
			print('3')
			# Accept connection
			fileReq_Socket, fileReq_addr = ss.accept()
			print('Connection from', fileReq_addr,
                 file=sys.stderr)
			# Receive data from client peer
			#f = fileReq_Socket.recv(1024)
			file = fileReq_Socket.recv(1024)
			print(file)
			# convert to binary
			pdu_rec = pickle.loads(file)
			print(pdu_rec)
			#type = pdu_rec.data_Type
			#file_name = file.data.get("file_name")				
			print("Determined File to get content")
			
			if (type == 'D'):					# check if type is D
				print("type is D")
				print(filename)
				if os.path.exists(filename):	# check if filename exists
					print('file exists')
					f = open(filename, 'r')		# open file
					l = f.read(100)				# read file
					info = l
					print("BREAK")
					
					type = 'C'					# change type to C
					if (l==""):					# check if EOF
						type = 'F'				# change type to F	
					
					pdu_o1 = PDU(type, l)		# build pdu object
					b_pdu = pickle.dumps(pdu_o1)	# change to binary
					print("sending initial file content")
					fileReq_Socket.send(b_pdu)				# send to client
					print("data sent")
					
					while(l != ""):				# check if not EOF
						print ("entered loop")
						l = f.read(100)			# read in 100 bytes
						print("printing l at the beginning")
						
						type = 'C' 				# type = C
						if (l==""):				# check if EOF
							print("setting type to F")	
							type = 'F'			# change type to F
						
						pdu_o1 = PDU(type, l)	# build pdu object
						b_pdu = pickle.dumps(pdu_o1)	# convert to binary
									
						fileReq_Socket.send(b_pdu)			# send to client	
					f.close()					# close file
									
			else:
				# Send peer an Error PDU if file doesn't exist
				err = PDU('E', 'Error: File does not exist')				
				err_bin = pickle.dumps(err)
				fileReq_Socket.send(err_bin)
				
	#else: # there is no incoming connection request, so go to the menu and ask the user for command			
				
	command = str(input('Please choose from the list below:\n'
                            '[O] Get On-line list\n'
                            '[L] List local files\n'
                            '[R] Register a file\n'
                            '[T] De-register a file\n'
                            '[Q] Quit the program\n'))	
	
	
	if (command == 'O'):
		# build list to retrieve files list from index server
		list = []
		# Build O type PDU
		pdu = PDU('O', list)
		# Send O-Type PDU to index server
		s.send(pickle.dumps(pdu))
		# Recieve response from server
		rec_pdu = s.recv(1024)
		# convert pdu to binary
		bin_pdu = pickle.loads(rec_pdu)
		# extract data/list from pdu
		list = bin_pdu.data
		# Print on-line registered files list
		print(list)
				
		# Ask peer for target file
		target = str(input("Enter file you wish to obtain from list: "))
				
		# Build S PDU with target file
		spdu = PDU(data_Type='S', data={'peer_name': username, 'file_name':target})
		# Convert to binary
		pdu = pickle.dumps(spdu)
		# Send to server index
		s.send(pdu)
		# Receive Response from server
		rec = s.recv(1024)
		
		# Convert to original
		s_type_response = pickle.loads(rec)
		# Find data type
		type = s_type_response.data_Type
		# Extract data/address
		peer_data = s_type_response.data
		print(type)
		
		# If S type pdu
		if (type == 'S'):
			# Store destination as local directory for download
			destination = 'C:\\Users\\samiy\\Desktop\\a\\content'+target
			print(peer_data)
			print(peer_data[0])
			# Call download function
			download_file(target, peer_data, destination)
			
		else:
			# Print error message if file cannot be found
			error = s_type_response.data
			print(error)
			
	if (command == 'L'):
		list = []
		l = PDU('O', list)
		l = pickle.dumps(l)
		print("sending request")
		print(s)
		s.send(l)
		print("done sending O pdu")
		l1 = pickle.loads(s.recv(1024))
		print("Printing list of registered elements...")
		ls = l1.data
		
		# iterate through list of on-line registered files
		for item in ls:
			# Check files that are registered under peer's name
			if item[0] == username:
				# Print them
				print(item)	
	
	if ( command == 'R'):
		print("To register a file, please enter filename below: " )
		filename = input('filename: ')
		# Get file name
		file_name = filename
		# Build R type PDU with peer name, file namen and peer address
		r = PDU(data_Type = 'R', data = {'peer_name': username, 'file_name': file_name, 'address': paddr})
		# convert to binary
		r = pickle.dumps(r)
		# send to index server
		s.send(r)
		print("Done sending R-type PDU to Server")
		# receive response from server
		s_recv = pickle.loads(s.recv(1024))
		# extract data type
		sr = s_recv.data_Type
		# extract data
		sd = s_recv.data
		print(sd)
		# If A type PDU
		if (sr == 'A'):
			# done
			print("File registration acknowledged! File registered!")
		# if Error type
		else:
			# while loop: re-try as many times until success to register
			while sr == 'E':
				# ask for another user name to register under
				username = select_name()
				# build R type PDU
				r = PDU(data_Type = 'R', data = {'peer_name': username, 'file_name': file_name, 'address': paddr})
				# convert to binary
				r = pickle.dumps(r)
				# send to index server
				s.send(r)
				print("Done sending R-Type PDU to server")
				# receive response
				s_recv = s.recv(1024)
				# convert to original
				ord = pickle.loads(s_recv)
				# extract data type
				sr = ord.data_Type
				sd = ord.data
				print(sd)
	
	# De-Register
	if (command == 'T'):											# De-Register a File
		print("Enter filename you wish to de-register below: ")		# Ask peer to enter file
		filename = input('filename: ')
		file_name = filename										# Inputted file name by peer
		de_register(username, file_name)							# Call de-register function
		
	if (command == 'Q'):											# Quit and de-register all of peer's files
		list = []													# empty list to retain fList from server
		l = PDU('O', list)											# O type to gain online registered files list
		l = pickle.dumps(l)											# Convert to binary
		s.send(l)													# Send to server
		print("done sending O pdu")			
		l1 = pickle.loads(s.recv(1024))								# Receive response from server
		flist = l1.data												# Extract data (list) from PDU
		print("printing files list")
		print("Registered files before [Q]: ")
		print(flist)
		
		for item in flist:											# Iterate through the list
			if item[0] == username:									# check elements that share peer's name
				de_register(item[0], item[1])
		s.close()
		exit()
		