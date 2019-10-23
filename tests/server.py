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
CH2 = 27 #18
CH4 = 18 #23

#Configure Pins
global Ign, Val
GPIO.setwarnings(False) #silence setup warnings
GPIO.setmode(GPIO.BCM)
GPIO.setup(CH1, GPIO.IN)
GPIO.setup(CH2, GPIO.OUT, initial=GPIO.HIGH)
Ign = "0"
GPIO.setup(CH4, GPIO.OUT, initial=GPIO.HIGH)
Val = "0"

#Reading/logging adc values
#adc = adc.ADC(True)

def reset():
    global msg, Ign, Val
    msg = "Resetting"
    GPIO.output(CH2, GPIO.HIGH)
    Ign = "0"
    GPIO.output(CH4, GPIO.HIGH)
    Val = "0"
    print("resetting")

def SIG_Handler(sig, frame):
    reset()
    print("\nExitting Safely")
    global server
    server.shutdown(socket.SHUT_RDWR)
    server.close()
    exit()

def server_thread():
    server.listen(1)
    clientsocket, clientAddress = server.accept()
    global csocket
    global msg
    global threadID
    global stop_threads
    stop_threads = 0
    threadID = 0
    csocket = clientsocket
    print("Connection Established")
    print("Connection from : ", clientAddress)
    print(csocket.recv(1024))
    msg = "0"
    while True:
        data = csocket.recv(2048)
        data = data.decode()
        print(data)
        if data == 'a':
            if threadID != 0:
                stop_threads = 1
                reset()
                #signal.pthread_kill(threadID, signal.SIGINT)
            break
        elif data == 'kill':
            print("Exitting Safely")
            reset()
            server.shutdown(socket.SHUT_RDWR)
            server.close()
            exit()
        elif data != "0":
            print(data)
            newthread = threading.Thread(target = Command_Response,args = (data), daemon = True)
            newthread.start()
            data = "0"
        if GPIO.input(CH1) == GPIO.HIGH:
            Burn = "0"
        else:
            Burn = "1"
        Pre = "12"
        data_out =""
        data_out = msg +";"+ Ign +";"+ Val +";"+ Burn +";"+ Pre +";"
        print(data_out)
        csocket.send(bytes(data_out,'utf-8'))
    print("Connection Broken")

def Command_Response(Command):
    global msg, Ign, Val
    global threadID
    global stop_threads
    threadID = threading.get_ident()
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
            if stop_threads == 1:
                print("ERROR: Aborted")
                stop_threads = 0
                return
            start_time = time.perf_counter()
            msg = "Start Ignition"
            print("Start Ignition")
            while GPIO.input(CH1) == GPIO.LOW:
                if time.perf_counter() - start_time < 10:
                    GPIO.output(CH2, GPIO.LOW)
                    Ign = "1"
                else:
                    msg = "ERROR: Ignition timeout"
                    print("ERROR: Ignition timeout")
                    reset()
                    return
            msg = "Stop Ignition"
            print("Stop Ignition")
            GPIO.output(CH2, GPIO.HIGH)
            Ign = "0"
            msg = "Opening the Valve"
            print("Opening the Valve")
            GPIO.output(CH4, GPIO.LOW)
            Val = "1"

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
            Val = "0"
            msg = "Ignition Sequence Complete"
            print("Ignition Sequence Complete")
            break

        elif Command == "2":
            msg = "Ignition ON"
            print("Ignition ON")
            GPIO.output(CH2, GPIO.LOW)
            Ign = "1"
            break

        elif Command == "3":
            msg = "Ignition OFF"
            print("Ignition OFF")
            GPIO.output(CH2, GPIO.HIGH)
            Ign = "0"
            break

        elif Command == "4":
            msg = "Valve OPEN"
            print("Valve OPEN")
            GPIO.output(CH4, GPIO.LOW)
            Val = "1"
            break

        elif Command == "5":
            msg = "Valve CLOSE"
            print("Valve CLOSE")
            GPIO.output(CH4, GPIO.HIGH)
            Val = "0"
            break
        else:
            msg = "ERROR invalid input"
            print("ERROR invalid input")
            break
    threadID = 0

    
    
signal.signal(signal.SIGPIPE, SIG_Handler)
signal.signal(signal.SIGINT, SIG_Handler)
LOCALHOST = "192.168.0.10"
PORT = 8080
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server.settimeout(10)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((LOCALHOST, PORT))
print("server started")
while True:
    print("Waiting for client request...")
    try:
        server_thread()
    except SocketError:
        print("EXCEPTION")
        GPIO.output(CH2, GPIO.HIGH)
        Ign = "0"    
        GPIO.output(CH4, GPIO.HIGH)
        Val = "0"
        print("resetting")
