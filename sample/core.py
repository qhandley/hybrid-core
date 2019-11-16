import os, signal
import RPi.GPIO as GPIO
import time
import adc

#define variables
CH1 = 17 #17
CH2 = 27 #22
#CH3 = 19 #22
CH4 = 18 #23

#Configure Pins
GPIO.setwarnings(False) #silence setup warnings
GPIO.setmode(GPIO.BCM)
GPIO.setup(CH1, GPIO.IN)
#GPIO.setup(CH3, GPIO.IN)
GPIO.setup(CH2, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(CH4, GPIO.OUT, initial=GPIO.HIGH)

#Reading/logging adc values
adc = adc.ADC(True)

def reset(child_pid):
    print("resetting")
    if child_pid != 0:
        os.kill(child_pid, signal.SIGKILL)
    GPIO.output(CH2, GPIO.HIGH)
    GPIO.output(CH4, GPIO.HIGH)

def INT_handler(sig, frame):
    print("\nExiting Safely")
    reset(0)
    os._exit(1)

def child(Command = 0):
    while True:
        if Command == "1":
            if GPIO.input(CH1) == GPIO.HIGH:
                print("ERROR: Burn wire cut")
                os._exit(1)

            #Ignition countdown
            print("Three")
            time.sleep(1)
            print("Two")
            time.sleep(1)
            print("One")
            time.sleep(1)
            
            start_time = time.perf_counter()
            print("Start Ignition")
            while GPIO.input(CH1) == GPIO.LOW: 
                if time.perf_counter() - start_time < 5:
                    GPIO.output(CH2, GPIO.LOW)
                else:
                    print("ERROR: Ignition timeout")
                    reset(0)
                    os._exit(1)

            print("Stopping Igniter")
            GPIO.output(CH2, GPIO.HIGH)
            print("Opening the Valve")
            GPIO.output(CH4, GPIO.LOW)
            
            print("Waiting for pressure build")
            start_time = time.perf_counter()
            adc.set_ref_time()
            psi = adc.read()

            while psi < 220:
                if time.perf_counter() - start_time < 2:
                    psi = adc.read()
                else:
                    reset(0)
                    print("Pressure Build Timeout")
                    os._exit(1)
                    break

            #Reset timer
            start_time = time.perf_counter()
            print("Waiting for pressure drop")

            while psi > 200:
                if time.perf_counter() - start_time < 6 and psi < 900:
                    psi = adc.read()
                else:
                    reset(0)
                    if psi >= 900:
                        print("Over Pressure Failure")
                    else:
                        print("Pressure Drop Timeout")
                    os._exit(1)

            print("Sequence Success: Closing the Valve")
            GPIO.output(CH4, GPIO.HIGH)
            print("Command (input h for help): ")
            break

        elif Command == "2":
            print("Ignition ON")
            GPIO.output(CH2, GPIO.LOW)
            break

        elif Command == "3":
            print("Ignition OFF")
            GPIO.output(CH2, GPIO.HIGH)
            break

        elif Command == "4":
            print("Valve OPEN")
            GPIO.output(CH4, GPIO.LOW)
            break

        elif Command == "5":
            print("Valve CLOSE")
            GPIO.output(CH4, GPIO.HIGH)
            break

        elif Command == "h":
            print("1: Ignition Sequence")
            print("2: Ignition ON")
            print("3: Ignition OFF")
            print("4: Valve OPEN")
            print("5: Valve CLOSE")
            print("a: abort process")
            print("exit: exit program")
            break

        else:
            print("ERROR: invalid input")
            break
    os._exit(0)

def parent():
    newpid = 0
    while True:
        user_input = input("Command (input h for help): ")
        if user_input == "a":
            print("aborting the children")
            reset(newpid)
            newpid = 0
        elif user_input == "exit":
            reset(newpid)
            break
        else:
            if newpid == 0:
                newpid = os.fork()
                if newpid == 0:
                    child(user_input)
            else:
                result = os.waitpid(newpid, os.WNOHANG)
                #print(result)
                if result == (0,0):
                    print("ERROR: Process already underway")
                else:
                    newpid = os.fork()
                    if newpid == 0:
                        child(user_input)
        time.sleep(.1)

signal.signal(signal.SIGINT, INT_handler)
parent()
GPIO.cleanup()
