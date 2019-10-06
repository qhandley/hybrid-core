import sys
import time
sys.path.append("../sample/")
import adc
import RPi.GPIO as GPIO

CH4 = 23

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(CH4, GPIO.OUT, initial=GPIO.LOW)

if __name__ == "__main__":
    ads1115 = adc.ADC(True)

    print("Opening valve")
    GPIO.output(CH4, GPIO.HIGH)

    while ads1115.read() > 1.5:
        print("Still open")
        #time.sleep(1)

    print("Closing valve")
    GPIO.output(CH4, GPIO.LOW)
        
