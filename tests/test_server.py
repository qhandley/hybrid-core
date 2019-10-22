import signal
import sys
import threading
import socket
import os
import RPi.GPIO as GPIO
import time
sys.path.append("../sample/")
import adc
from socket import error as SocketError
import errno

#define variables
CH1 = 17 #17
CH2 = 22 #18
CH3 = 18 #22
CH4 = 23 #23

#Configure Pins
GPIO.setwarnings(False) #silence setup warnings
GPIO.setmode(GPIO.BCM)
GPIO.setup(CH1, GPIO.IN)
GPIO.setup(CH2, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(CH3, GPIO.IN)
GPIO.setup(CH4, GPIO.OUT, initial=GPIO.HIGH)

#Reading/logging adc values
#adc = adc.ADC(True)

#Reset IO
def reset():
    csocket.send(bytes("Resetting",'utf-8'))
    GPIO.output(CH2, GPIO.HIGH)
    GPIO.output(CH4, GPIO.HIGH)
    print("resetting")

#Handle Signals
def SIG_Handler(sig, frame):
    reset()
    print("\nExitting Safely")
    global server
    #close socket
    server.shutdown(socket.SHUT_RDWR)
    server.close()
    exit()

def SIG_USR_Handler(sig, frame):
    raise ValueError
    
#Function used for server thread
def server_thread():
    server.listen(1)
    clientsocket, clientAddress = server.accept()
    global csocket
    global msg
    global command
    csocket = clientsocket
    print("Connection Established")
    print("Connection from : ", clientAddress)
    print(csocket.recv(1024))
    csocket.send(bytes("What up", 'utf-8'))
    msg = "0"
    while True:
        data = csocket.recv(2048)
        data = data.decode()
        if data == 'a':
            os.kill(os.getpid(),signal.SIGUSR1)
            break
        elif data == 'kill':
            os.kill(os.getpid(),signal.SIGINT)
            exit()
        elif data != "0":
            print(data)
            command = data
            data = "0"
        csocket.send(bytes(msg,'utf-8'))
        msg = "0"
    print("Connection Broken")

def Command_Response(Command):
    global msg
    while True:
        if Command == "1":
            if GPIO.input(CH1) == GPIO.HIGH:
                msg = "ERROR: Burn wire cut"
                print("ERROR: Burn wire cut")
                return
            msg= "Three"
            print("Three")
            time.sleep(1)
            msg = "Two"
            print("Two")
            time.sleep(1)
            msg = "One"
            print("One")
            time.sleep(1)
            start_time = time.perf_counter()
            msg = "Start Ignition"
            print("Start Ignition")
            while GPIO.input(CH1) == GPIO.LOW:
                if time.perf_counter() - start_time < 10:
                    GPIO.output(CH2, GPIO.LOW)
                else:
                    msg = "ERROR: Ignition timeout"
                    print("ERROR: Ignition timeout")
                    reset()
                    return
            msg = "Stop Ignition"
            print("Stop Ignition")
            GPIO.output(CH2, GPIO.HIGH)
            msg = "Opening the Valve"
            print("Opening the Valve")
            GPIO.output(CH4, GPIO.LOW)

            msg = "Waiting for pressure build"
            print("Waiting for pressure build")
            #adc.set_ref_time()
            while False: #adc.read() < 100:
                pass
            msg = "Waiting for pressure drop"
            print("Waiting for pressure drop")
            while False: #adc.read() > 70:
                pass
            msg = "Closing the Valve"
            print("Closing the Valve")
            GPIO.output(CH4, GPIO.HIGH)
            msg = "Ignition Sequence Complete"
            print("Ignition Sequence Complete")
            break

        elif Command == "2":
            msg = "Ignition ON"
            print("Ignition ON")
            GPIO.output(CH2, GPIO.LOW)
            break

        elif Command == "3":
            msg = "Ignition OFF"
            print("Ignition OFF")
            GPIO.output(CH2, GPIO.HIGH)
            break

        elif Command == "4":
            msg = "Valve OPEN"
            print("Valve OPEN")
            GPIO.output(CH4, GPIO.LOW)
            break

        elif Command == "5":
            msg = "Valve CLOSE"
            print("Valve CLOSE")
            GPIO.output(CH4, GPIO.HIGH)
            break
        else:
            msg = "ERROR invalid input"
            print("ERROR invalid input")
            break

    
#Initialze Signal Handlers    
signal.signal(signal.SIGPIPE, SIG_Handler)
signal.signal(signal.SIGINT, SIG_Handler)
#Define IP and Port
LOCALHOST = "192.168.0.10"
PORT = 8080
#Create Server Socket using IPV4 and TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Add Socket Options: reuse Socket
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((LOCALHOST, PORT))
print("server started")
#command used to share messages from client between threads
global command
#Keep Connecting using Socket as long as program running
while True:
    print("Waiting for client request...")
    data ="0"
    try:
        thread = threading.Thread(target = server_thread(), daemon = True)
        thread.start()
    except SocketError:
        print("EXCEPTION")
        GPIO.output(CH2, GPIO.HIGH)
        GPIO.output(CH4, GPIO.HIGH)
        print("Resetting")
    while True:
        if command != "0":
            try:
                Command_Response(command)
            except:
                reset()
                break
            finally:
                command = "0"
        else:
            pass
