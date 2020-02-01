import sys
import time
import adc
import RPi.GPIO as GPIO

CH1 = 17 #burn wire
#CH4 = 23

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(CH1, GPIO.IN)
#GPIO.setup(CH4, GPIO.OUT, initial=GPIO.HIGH)

if __name__ == "__main__":
    ads1115 = adc.ADC(True)
    ads1115.set_ref_time()

    #print("Opening valve")
    #GPIO.output(CH4, GPIO.HIGH)

    while True:
        if(GPIO.input(CH1) == GPIO.HIGH):
            print("Burn wire is cut")
        else:
            print("Burn wire is connected")

        print(ads1115.read())
        time.sleep(1)

    #print("Closing valve")
    #GPIO.output(CH4, GPIO.LOW)
        
