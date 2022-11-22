"""
client console application that takes three args (addr, port, filename)
to query a server following the same protocol.
"""
import socket, os, sys

MAX_PACKET_SIZE = 4096
TIMEOUT = 15

ARGUEMENTS = sys.argv[1:]
if len(ARGUEMENTS) != 3:
    print("invalid arguements given, enter arguements in the form below")
    print("hostname/IP address port_number(1024-64000) filename")
    sys.exit()

class Client():
    server_address = None
    port_number = None
    filename = None
    port_range = (1024, 64000)
    socket = None
    file = None

    def close(self):
        if self.socket:
            self.socket.close()
        if self.file:
            self.file.close()
        sys.exit()
    
    def init_server_address(self, server_input):
        try:
            self.server_address = socket.gethostbyname(server_input)
        except:
            try:
                self.server_address = socket.getaddrinfo(server_input) #linux
            except:
                print("invalid server address. ")
                self.close()
        print(self.server_address)

    def init_port_number(self, port_number):
        port_number = int(port_number)
        if self.port_range[1] >= port_number >= self.port_range[0]:
            self.port_number = port_number
            return
        print("port number:", port_number, "out of range", self.port_range)
        self.close()

    def init_filename(self, filename):
        if os.path.isfile(filename):
            print(filename, "already exists. ")
            self.close()
        self.filename = filename

    def create_socket(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            self.socket.settimeout(TIMEOUT)
        except:
            print("failed to create socket.")
            self.close()

    def connect(self):
        try:
            self.socket.connect((self.server_address, self.port_number))
        except Exception as e:
            print('error connecting.', e)
            self.close()

    def create_file_request(self, name):
        magic_number = 0x497E.to_bytes(2, 'big')#file request number
        type_code = int(1).to_bytes(1, 'big')
        filename = name.encode('utf-8')
        if len(filename) > 1024:
            print('filename too large (> 1024 bytes)')
            self.close()
        filename_length = len(filename).to_bytes(2, 'big')
        print("created file request:", magic_number,type_code,filename_length,filename)
        return bytearray(magic_number + type_code + filename_length + filename)

    def send_file_request(self, file_request):
        try:
            self.socket.send(file_request)
        except socket.timeout:
            print("socket timed out while sending the file request")
            self.close()    
    
    def process_file_response(self):
        try:
            header = self.socket.recv(8)
        except socket.timeout:
            print('socket.timeout: timed out receiving header')
            self.close()
        
        magic_number = int.from_bytes(header[0:2], 'big')
        type_code = header[2]
        status_code = header[3]
        if status_code == 0:
            print('server could not access file')
            return
        data_length = int.from_bytes(header[4:8], 'big')
        print("file response decoded:", magic_number, type_code, status_code, data_length)
        
        try:
            self.file = open(self.filename, 'wb')
        except:
            print(f"error creating file {self.filename}.")
            return
            
        data_written = 0
        try:
            while data_written < data_length:
                data = self.socket.recv(MAX_PACKET_SIZE)#read in next chunk if applicable
                if len(data) == 0:
                    print("error, data received is less than expected.")
                    break
                self.file.write(data)
                data_written += len(data)
        except:
            print('socket.timeout: timed out')
            return
        #print(self.filename, f"created, {data_written} bytes")


    def __init__(self, address, port, filename):
        self.init_server_address(address)
        self.init_port_number(port)
        self.init_filename(filename)
        self.create_socket()
        self.connect()
        file_request = self.create_file_request(self.filename)
        self.send_file_request(file_request)
        self.process_file_response()
        self.close()

def main():
    address = ARGUEMENTS[0]
    port = ARGUEMENTS[1]
    filename = ARGUEMENTS[2]
    client = Client(address, port, filename)

main()

















