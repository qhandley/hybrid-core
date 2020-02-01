import sys
import os, signal
import time
import adc_propane as adc
import RPi.GPIO as GPIO
import ctypes
sys.path.append("../servo_driver/")
import ServoControl

#CTRL+C handler
def INT_handler(sig, frame):
    print("\nExiting Safely")
    reset()
    os._exit(1)
#initalize CTRL+C handler
signal.signal(signal.SIGINT, INT_handler)

CH1 = 24 #glow plug
CH2 = 22 #propane valve

#initialize I/O
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(CH1, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(CH2, GPIO.OUT, initial=GPIO.HIGH)
#setup Servo
servo = ServoControl.Servo()
servo.begin('/dev/ttyUSB0', 115200, 1)
servo.set_position_start(2200)
servo.set_position_end(3200)
#servo.set_position(900)
servo.set_position_neutral(3200)
servo.set_vel_time(4095)
servo.set_torque(4095)


def reset():
    print("resetting")
    GPIO.output(CH1, GPIO.LOW)
    GPIO.output(CH2, GPIO.LOW)
    servo.set_position(3200)

if __name__ == "__main__":
    #reset I/O
    reset()
    #setup ADC
    #adc = adc.ADC(True)
    #adc.set_ref_time()
    #initalize counter
    counter = 0
    #count down
    print("Three")
    time.sleep(1)
    print("Two")
    time.sleep(1)
    print("One")
    time.sleep(1)
    #initalize timer1
    timer1 = time.perf_counter() 
    print("Turning On Glow Plug")
    GPIO.output(CH1, GPIO.HIGH)
    #wait for glow plug to heat up
    time.sleep(20)
    #initalize timer2
    timer2 = time.perf_counter()
    print("Opening Propane Valve")
    GPIO.output(CH2, GPIO.HIGH)
    print("Cracking Nitrous Valve")
    servo.set_position(3000)
    while True:
        #temperature = adc.read()
        if time.perf_counter() - timer2 > 1:
            #print("ERROR: Ignition Timeout")
            print("Ignition Complete")
            reset()
            os._exit(1)
        #if temperature > 60:
        #    counter += 1
        #    if counter >= 5:
        #        break
        #else:
        #    counter = 0
    reset()
    print("Time to Ignite: " + str(time.perf_counter() - timer2))
    print("Total Time: " + str(time.perf_counter() - timer1))
             

