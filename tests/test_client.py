import socket
import time
SERVER = "192.168.1.110"
PORT = 8080
print("Connecting")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))
print("Connected")
while(1):
        client.sendall(bytes("Hello There!;234;1254;2312", 'UTF-8'))
        time.sleep(.5)
        
