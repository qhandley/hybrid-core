import os, signal
import time
import RPi.GPIO as GPIO
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

#define variables
CH1 = 4 #7
CH2 = 14 #8
CH3 = 2 #3
CH4 = 15 #10

#Configure Pins
GPIO.setwarnings(False) #silence setup warnings
GPIO.setmode(GPIO.BCM)
GPIO.setup(CH1, GPIO.IN)
GPIO.setup(CH2, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(CH3, GPIO.IN)
GPIO.setup(CH4, GPIO.OUT, initial=GPIO.LOW)

def reset(child_pid):
    print("resetting")
    if child_pid != 0:
        os.kill(child_pid, signal.SIGKILL)
    GPIO.output(CH2, GPIO.LOW)
    GPIO.output(CH4, GPIO.LOW)

def child(Command = 0):
    while True:
        if Command == "1":
            '''
            if GPIO.input(CH1) == GPIO.LOW:
                print("ERROR: Burn wire cut")
                os._exit(1)
            '''
            start_time = time.perf_counter()
            print("Start Ignition")
            while GPIO.input(CH1) == GPIO.HIGH: 
                if time.perf_counter() - start_time < 20:
                    GPIO.output(CH2, GPIO.HIGH)
                else:
                    print("ERROR: Ignition timeout")
                    reset(0)
                    os._exit(1)
            GPIO.output(CH4, GPIO.HIGH)
            i2c = busio.I2C(board.SCL, board.SDA)
            ads = ADS.ADS1115(i2c)
            chan = AnalogIn(ads, ADS.P0)
            while chan.value > 512:
                print("Reading pressure sensor value!")
                #log files
            GPIO.output(CH4, GPIO.LOW)
            break

        elif Command == "2":
            print("Ignition On")
            GPIO.output(CH2, GPIO.HIGH)
            break
        elif Command == "3":
            print("Ignition OFF")
            GPIO.output(CH2, GPIO.LOW)
            break
        elif Command == "4":
            print("Valve Open")
            GPIO.output(CH4, GPIO.HIGH)
            break
        elif Command == "5":
            print("Valve Closed")
            GPIO.output(CH4, GPIO.LOW)
            break
        elif Command == "h":
            print("1: Ignition Sequence")
            print("2: Ignition ON")
            print("3: Ignition OFF")
            print("4: Open Valve")
            print("5: Close Valve")
            print("abort: kill process")
            print("exit: exit program")
            break
        else:
            print("ERROR: Invalid Input")
            break
    os._exit(0)

def parent():
    newpid = 0
    while True:
        user_input = input("Command (input h for help): ")
        if user_input == "abort":
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
parent()
GPIO.cleanup()
