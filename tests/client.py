import socket, threading
import signal, os, time
user_input = "0"
stop_threads = 0
in_data = "0"
def SIG_Handler(sig, frame):
    print("\nExitting Safely")
    global stop_threads
    stop_threads = 1
    client.send(bytes('kill', 'utf-8'))
    client.shutdown(socket.SHUT_RDWR)
    client.close()
    exit()

def get_input():
    global user_input
    global stop_threads
    while stop_threads != 1:
        temp = input()
        if temp == "kill":
            stop_threads = 1
            user_input = temp
            break
        elif temp == "a":
            stop_threads = 1
            user_input = temp
            break
        elif temp == "1":
            user_input = temp 
        elif temp == "2":
            user_input = temp 
        elif temp == "3":
            user_input = temp 
        elif temp == "4":
            user_input = temp 
        elif temp == "5":
            user_input = temp 
        elif temp == "h":
            print("1: Ignition Sequence")
            print("2: Ignition ON")
            print("3: Ignition OFF")
            print("4: Valve OPEN")
            print("5: Valve CLOSE")
            print("a: abort process")
            print("kill: kill server")
        else:
            print("Error Invalid Input")

def ui_output():
    while stop_threads != 1:
        print("\nConnected to: ", SERVER )
        print("Last Server message: ", in_data)
        print("\nCommand: ", end ="")
        time.sleep(2)
        #os.system('clear')
signal.signal(signal.SIGINT, SIG_Handler)
signal.signal(signal.SIGPIPE, SIG_Handler)
SERVER = "192.168.0.10"
PORT = 8080
print("Connecting")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))
print("Connection Established")
client.sendall(bytes("Hello", 'utf-8'))
print(client.recv(1024))
input_thread = threading.Thread(target = get_input, daemon = True) 
#ui_thread = threading.Thread(target = ui_output, daemon = True)
input_thread.start()
#ui_thread.start()
while True:
    client.send(bytes(user_input, 'utf-8'))
    if (user_input=="a" or user_input == "kill"):
        stop_threads = 1
        break
    if user_input != "0":
        user_input = "0"
    temp = client.recv(1024)
    #print("from Server :", temp)
    if temp.decode() != "0":
        in_data = temp.decode()
        print(in_data)
client.close()
