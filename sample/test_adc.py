import smbus
import time

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
            ts = time.gmtime()
            self.log_file = time.strftime("%Y-%m-%d_%H:%M", ts) + ".txt"
            f = open(self.log_file, "x")
            f.close()

    def init_i2c(self):
        # Initialize i2c (SMBus)
        self.bus = smbus.SMBus(self.i2c_ch)

        # Read the Config register (2 bytes)
        cur_cfg = self.bus.read_i2c_block_data(self.i2c_adr, self.ads_reg_cfg, 2)

        # Configure for continuous mode, +/-0.256V scaling, AIN2 vs AIN3 
        new_cfg = cur_cfg 
        new_cfg[0] = 0b00111110 
        self.bus.write_i2c_block_data(self.i2c_adr, self.ads_reg_cfg, new_cfg)

    def set_ref_time(self):
        self.start_time = time.perf_counter()

    def log(self, data):
        f = open(self.log_file, "a")
        ts = time.perf_counter() - self.start_time
        f.write('{0}, {1}\n'.format(ts, data))
        f.close()

    def read(self):
        val = self.bus.read_i2c_block_data(self.i2c_adr, self.ads_reg_cnv, 2)
        result = (val[0] << 8) + val[1] # MSB + LSB
        result *= (256 / 2**15) # Convert to mV 
        result *= (14.5 / 0.475) # Convert to psi
        #result -= 30 # Manual offset
        if(self.to_log == True):
            self.log(result)
        return result

if __name__ == "__main__":
    adc = ADC(True)

    while(True):
        val = adc.read()
        print(val)
        time.sleep(1)
