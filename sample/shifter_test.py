import RPi.GPIO as GPIO
import time 

class ShiftRegister:
    DATA_CH = 23
    CLK_CH = 22
    LATCH_CH = 17 

    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.DATA_CH, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.CLK_CH, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.LATCH_CH, GPIO.OUT, initial=GPIO.LOW)

    def shift_16(self, data):
        if len(data) != 16:
            print("Error: 16 data elements needed to shift") 
            return

        for i in range(16):
            GPIO.output(self.DATA_CH, data[i])
            time.sleep(0.01)
            GPIO.output(self.LATCH_CH, GPIO.LOW)
            GPIO.output(self.CLK_CH, GPIO.HIGH)
            time.sleep(0.01)
            GPIO.output(self.LATCH_CH, GPIO.HIGH)
            GPIO.output(self.CLK_CH, GPIO.LOW)

if __name__ == "__main__":
    shifty = ShiftRegister()
    test_data = [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]

    shifty.shift_16(test_data)
