import sys
import time
sys.path.append("../sample/")
import adc
import RPi.GPIO as GPIO

CH4 = 23

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(CH4, GPIO.OUT, initial=GPIO.HIGH)

if __name__ == "__main__":
    ads1115 = adc.ADC(True)
    ads1115.set_ref_time()

    #print("Opening valve")
    #GPIO.output(CH4, GPIO.HIGH)

    while True:
        print(ads1115.read())
        time.sleep(1)

    #print("Closing valve")
    #GPIO.output(CH4, GPIO.LOW)
        
