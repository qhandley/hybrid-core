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
global Ign, Val, ERROR
ERROR = "0"
GPIO.setwarnings(False) #silence setup warnings
GPIO.setmode(GPIO.BCM)
GPIO.setup(CH1, GPIO.IN)
GPIO.setup(CH2, GPIO.OUT, initial=GPIO.HIGH)
Ign = "0"
GPIO.setup(CH4, GPIO.OUT, initial=GPIO.HIGH)
Val = "0"

#Reading/logging adc values
adc = adc.ADC(True)

def reset():
    global msg, Ign, Val
    msg = "Resetting"
    GPIO.output(CH2, GPIO.HIGH)
    Ign = "0"
    GPIO.output(CH4, GPIO.HIGH)
    Val = "0"
    print("resetting")

def SIG_ALRM_Handler(sig, frame):
    global ERROR
    print("ERROR: Connection Timeout")
    ERROR = "ERROR: Connection Timeout"
    reset()
    server.shutdown(socket.SHUT_RDWR)
    server.close()
    exit()
    #raise ValueError

def SIG_USR_Handler(sig, frame):
    print("Aborting")
    msg ="Aborting"
    reset()
    raise ValueError

def SIG_Handler(sig, frame):
    global server,csocket
    reset()
    #print("Exitting Safely")
    server.shutdown(socket.SHUT_RDWR)
    server.close()
    exit()

def server_thread():
    global threadID
    threadID = threading.get_ident()
    try:
        server.listen(1)
        clientsocket, clientAddress = server.accept()
        global csocket
        global msg
        global command
        csocket = clientsocket
        print("Connection Established")
        print("Connection from : ", clientAddress)
        print(csocket.recv(1024))
        msg = "0"
        while True:
            signal.alarm(3)
            data = csocket.recv(1024)
            signal.alarm(0)
            data = data.decode()
            data,ignore1,ignore2 = data.partition("0")
            if data == 'a':
                os.kill(os.getpid(), signal.SIGUSR1)
            elif data == 'kill':
                os.kill(os.getpid(), signal.SIGINT)
                break
            elif data != "":
                print(data)
                command = data
                data = "0"
            if GPIO.input(CH1) == GPIO.HIGH:
                Burn = "0"
            else:
                Burn = "1"
            #Pre = str(round(12.12165135, 1))
            Pre = str(round(adc.read(), 1))
            data_out =""
            data_out = msg +";"+ Ign +";"+ Val +";"+ Burn +";"+ Pre +";" + ERROR + ";"
            #print(data_out)
            csocket.send(bytes(data_out,'utf-8'))
    except SocketError:
        print("EXCEPTION")
        os.kill(os.getpid(), signal.SIGINT)
    print("Connection Broken")
    threadID = 0

def Command_Response(Command):
    global msg, Ign, Val, ERROR
    while True:
        if Command == "1":
            reset()
            if GPIO.input(CH1) == GPIO.HIGH:
                ERROR = "ERROR: Burn wire cut"
                print("ERROR: Burn wire cut")
                return
            msg= "Ten"
            print("Ten")
            time.sleep(1)
            msg= "Nine"
            print("Nine")
            time.sleep(1)
            msg= "Eight"
            print("Eight")
            time.sleep(1)
            msg= "Seven"
            print("Seven")
            time.sleep(1)
            msg= "Six"
            print("Six")
            time.sleep(1)
            msg= "Five"
            print("Five")
            time.sleep(1)
            msg= "Four"
            print("Four")
            time.sleep(1)
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
                    Ign = "1"
                else:
                    ERROR = "ERROR: Ignition timeout"
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
            adc.set_ref_time()
            while adc.read() < 100:
                pass
            msg = "Waiting for pressure drop"
            print("Waiting for pressure drop")
            temp = adc.read()
            while temp > 70 and temp < 900:
                temp = adc.read()
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
            ERROR = "ERROR invalid input"
            print("ERROR invalid input")
            break

    
    
signal.signal(signal.SIGPIPE, SIG_Handler)
signal.signal(signal.SIGALRM, SIG_ALRM_Handler)
signal.signal(signal.SIGINT, SIG_Handler)
signal.signal(signal.SIGUSR1, SIG_USR_Handler)

LOCALHOST = "192.168.1.10"
PORT = 8080
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((LOCALHOST, PORT))
print("server started")
global command, threadID
threadID = 0
command = "0"
while True:
    if threadID == 0:
        print("Waiting for client request...")
        thread = threading.Thread(target = server_thread, daemon = True)
        thread.start()
    try:
        while True:
            if command != "0":
                Command_Response(command)
                command = "0"
    except ValueError:
        command = "0"

