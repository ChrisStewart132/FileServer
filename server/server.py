"""
server console application that takes one arg (port)
to host and send files when queried by clients following the same protocol.
"""
import socket, time, sys, os

TIMEOUT = 5

ARGUEMENTS = sys.argv[1:]
if len(ARGUEMENTS) != 1:
    print("invalid arguements given, enter a port number.")
    sys.exit()
    
class Server():
    name = None
    address = None
    port_number = None
    port_range = (1024, 64000)
    socket = None
    connection = None
    file = None

    def close(self):
        if self.socket:
            self.socket.close()
        if self.file:
            self.file.close()
        if self.connection:
            self.connection.close()
        sys.exit()

    def init_port_number(self, port_number):
        if self.port_range[1] >= port_number >= self.port_range[0]:
            self.port_number = port_number
            return True
        print("port number:", port_number, "out of range", self.port_range)
        self.close()

    def create_socket(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            self.name = socket.gethostname()
            self.address = socket.gethostbyname(self.name)
            self.address = ''   
            self.socket.bind((self.address, self.port_number))
     
        except:
            print("failed to create socket.")
            self.close()

    def run(self):
        while True:
            try:
                self.socket.listen()
            except:
                print('socket.listen() error.')
                self.close()
                
            self.connection, address = self.socket.accept()
            self.connection.settimeout(TIMEOUT)
            t = time.localtime()
            current_time = time.strftime("\n%H:%M:%S", t)
            print(current_time, address)

            if not self.process_file_request(self.connection, address):
                print("failed to send file.")
            else:
                print("file sent succesfully.")
            self.connection.close() 

    def process_file_request(self, connection, address):
        '''read and validate data from received packet'''
        try:
            header = connection.recv(5)
        except socket.timeout:
            print("connection timed out while receiving request.")
            return False
        
        magic_number = int.from_bytes(header[0:2], 'big')#file request number
        type_code = header[2]
        if magic_number != 0x497E or type_code != 1:
            print("invalid file request (magic no. or type code incorrect).")
            return False
        
        filename_length = int.from_bytes(header[3:5], 'big')
        if filename_length > 1024 or filename_length < 1:
            print('filename size invalid (must be > 0 and <= 1024')
            return False
        
        filename_bytes = connection.recv(filename_length)
        if len(filename_bytes) != filename_length:
            #print(f"given filename length was incorrect {filename_length}\
                  #indicated but {len(filename_bytes)} received")
            print("file len error")
            return False
        
        filename = filename_bytes.decode()
        #print(f"{filename} requested.")

        if not self.send_file_data(connection, filename):
            print("send file error")
            return False
        return True

    def send_file_data(self, connection, filename):
        '''get file data and send file response packet(s)'''        
        self.file = None
        if os.path.isfile(filename):
            try:
                self.file = open(filename, 'rb')
            except:
                #print(f'error opening and/or reading file: {filename}')
                print("couldnt open", filename)
                self.file = None
                return False
            data_len = os.path.getsize(filename)
            print("file size:{} bytes".format(data_len))
            file_response_header = self.create_file_response_header(data_len)  
            MAX_PACKET_SIZE = 4096
            data_read = 0
            connection.send(file_response_header)
            while data_read < data_len:
                data = self.file.read(MAX_PACKET_SIZE)
                try:
                    connection.send(data)
                    #print(f'{len(file_response)-8} bytes sent.')
                except socket.timeout:
                    print("failed to send file, connection timed out.")
                data_read += len(data)
        else:
            #print(f"couldn't open file {filename}")
            print("couldnt find", filename)
            data = None
            file_response_header = self.create_file_response_header(0)   
            connection.send(file_response_header)
        
         
        if self.file:
            self.file.close()
            return True
        print('unk send err')
        return False
                 
    def create_file_response_header(self, file_len):
        magic_number = 0x497E.to_bytes(2, 'big')#file request number
        type_code = int(2).to_bytes(1, 'big')
        if file_len == 0:
            status_code = int(0).to_bytes(1, 'big')
            data_length = int(0).to_bytes(4, 'big')
            return bytearray(magic_number + type_code + status_code
                         + data_length)
        status_code = int(1).to_bytes(1, 'big')
        data_length = file_len.to_bytes(4, 'big')
        return bytearray(magic_number + type_code + status_code
                         + data_length)

    def __init__(self, port_number):
        self.init_port_number(port_number)
        self.create_socket()
        self.run()
        self.socket.close()
        self.close()
            
def main():
    port = int(ARGUEMENTS[0])
    server = Server(port)

main()
