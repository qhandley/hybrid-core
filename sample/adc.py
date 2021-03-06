import smbus
import time
from datetime import datetime

class ADC:
    # i2c channel (/etc/i2c-x)
    i2c_ch = 1

    # ads1115 address on the i2c bus
    i2c_adr = 0x48

    # Internal register addresses
    ads_reg_cnv = 0x00 # Conversion register
    ads_reg_cfg = 0x01 # Config register

    # Reference timer
    start_time = 0

    def __init__(self, to_log):
        self.init_i2c()
        self.to_log = to_log

        if(self.to_log == True):
            ts = datetime.now().strftime("%Y-%m-%d_%M_%S")
            self.log_file = "../psi_data/" + ts + ".txt"
            f = open(self.log_file, "x")
            f.close()

    def init_i2c(self):
        # Initialize i2c (SMBus)
        self.bus = smbus.SMBus(self.i2c_ch)

        # Read the Config register (2 bytes)
        cur_cfg = self.bus.read_i2c_block_data(self.i2c_adr, self.ads_reg_cfg, 2)

        # Configure for continuous mode, +/-0.256V scaling, AIN2 vs AIN3 
        new_cfg = cur_cfg 
        #pressure transducer settings part 1
        #new_cfg[0] = 0b00111110 #AIN3, AIN2
        new_cfg[0] = 0b00001110 #AIN1,AIN0
        #pressure transducer settings part 2
        new_cfg[1] = 0b11100011
        self.bus.write_i2c_block_data(self.i2c_adr, self.ads_reg_cfg, new_cfg)

    def set_ref_time(self):
        self.start_time = time.perf_counter()

    def log(self, data):
        f = open(self.log_file, "a")
        #ts = time.perf_counter() - self.start_time
        ts = datetime.now().strftime("%H:%M:%S:%f")
        f.write('{0}, {1}\n'.format(ts, data))
        f.close()

    def read(self):
        val = self.bus.read_i2c_block_data(self.i2c_adr, self.ads_reg_cnv, 2)
        result = (val[0] << 8) + val[1] # MSB + LSB
        if(result >= 32768):
            result ^= ((2 ** 16) - 1)
            result = -1 *(result + 1)
        result *= (256 / 2**15) # Convert to mV 
        result *= (14.5 / 0.475) # Convert to psi
        result += 4 # Manual offset

        if(self.to_log == True):
            self.log(result)
        return result

    def read_raw(self):
        val = self.bus.read_i2c_block_data(self.i2c_adr, self.ads_reg_cnv, 2)
        return val

if __name__ == "__main__":
    adc = ADC()

    while(True):
        val = adc.read()
        print(val)
        time.sleep(1)
