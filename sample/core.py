import os, signal
import RPi.GPIO as GPIO
import time
import adc

#define variables
Burn_Wire = 17 #Burn Wire
Igniter = 18 #Igniter
Deluge = 24 #Deluge
Valve = 23 #Valve
Propane = 22 #Spare Relay (Propane solenoid)

#Configure Pins
GPIO.setwarnings(False) #silence setup warnings
GPIO.setmode(GPIO.BCM)
GPIO.setup(Burn_Wire, GPIO.IN)
GPIO.setup(Igniter, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Deluge, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Valve, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Propane, GPIO.OUT, initial=GPIO.LOW)

#Reading/logging adc values
adc = adc.ADC(True)

def reset(child_pid):
    print("resetting")
    if child_pid != 0:
        os.kill(child_pid, signal.SIGKILL)
    GPIO.output(Igniter, GPIO.LOW)
    GPIO.output(Deluge, GPIO.LOW)
    GPIO.output(Valve, GPIO.LOW)
    GPIO.output(Propane, GPIO.LOW)

def INT_handler(sig, frame):
    print("\nExiting Safely")
    reset(0)
    os._exit(1)

def child(Command = 0):
    while True:
        if Command == "1":
            if GPIO.input(Burn_Wire) == GPIO.HIGH:
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
            Deluge_timer = time.perf_counter()
            Deluge_on = False
            print("Start Ignition")
            while GPIO.input(Burn_Wire) == GPIO.LOW: 
                if time.perf_counter() - start_time < 10:
                    GPIO.output(Igniter, GPIO.HIGH)
                    if time.perf_counter() - Deluge_timer > 1 and Deluge_on == False:
                        print("Starting Deluge")
                        Deluge_on = True
                        GPIO.output(Deluge, GPIO.HIGH)
                else:
                    print("ERROR: Ignition timeout")
                    reset(0)
                    os._exit(1)

            print("Stopping Igniter")
            GPIO.output(Igniter, GPIO.LOW)
            print("Starting Deluge")
            GPIO.output(Deluge, GPIO.HIGH)
            #print("Time to Ignite: " + str(time.perf_counter() - start_time))
            print("Opening the Valve")
            GPIO.output(Valve, GPIO.HIGH)
            
            print("Waiting for pressure build")
            start_time = time.perf_counter()
            adc.set_ref_time()
            psi = adc.read()

            while psi < 220:
                if time.perf_counter() - start_time < 3:
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
                if time.perf_counter() - start_time < 6 and psi < 1000:
                    psi = adc.read()
                else:
                    reset(0)
                    if psi >= 900:
                        print("Over Pressure Failure")
                    else:
                        print("Pressure Drop Timeout")
                    os._exit(1)

            print("Sequence Success: Closing the Valve")
            GPIO.output(Valve, GPIO.LOW)
            print("Command (input h for help): ")
            break

        elif Command == "2":
            print("Ignition ON")
            GPIO.output(Igniter, GPIO.HIGH)
            break

        elif Command == "3":
            print("Ignition OFF")
            GPIO.output(Igniter, GPIO.LOW)
            break

        elif Command == "4":
            print("Valve OPEN")
            GPIO.output(Valve, GPIO.HIGH)
            break

        elif Command == "5":
            print("Valve CLOSE")
            GPIO.output(Valve, GPIO.LOW)
            break

        elif Command == "6":
            print("Deluge ON")
            GPIO.output(Deluge, GPIO.HIGH)
            break

        elif Command == "7":
            print("Deluge OFF")
            GPIO.output(Deluge, GPIO.LOW)
            break
        
        elif Command == "8":
            print("Propane ON")
            GPIO.output(Propane, GPIO.HIGH)
            break

        elif Command == "9":
            print("Propane OFF")
            GPIO.output(Propane, GPIO.LOW)
            break

        elif Command == "h":
            print("1: Ignition Sequence")
            print("2: Ignition ON")
            print("3: Ignition OFF")
            print("4: Valve OPEN")
            print("5: Valve CLOSE")
            print("6: Deluge ON")
            print("7: Deluge OFF")
            print("8: Propane ON")
            print("9: Propane OFF")
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
