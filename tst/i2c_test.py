import smbus
import time

i2c_ch = 1

# ADS1115 address on the i2c bus
i2c_adr = 0x48

# Internal register addresses
reg_cnv = 0x00 # Conversion register
reg_cfg = 0x01 # Config register

# Initialize i2c (SMBus)
bus = smbus.SMBus(i2c_ch)

def init_i2c():
    # Read the Config register (2 bytes)
    val = bus.read_i2c_block_data(i2c_adr, reg_cfg, 2)
    print("Current configuration:", val)

    # Configure for continuous mode, set input mux
    val[0] = 0b01000100
    bus.write_i2c_block_data(i2c_adr, reg_cfg, val)

def read_adc():
    val = bus.read_i2c_block_data(i2c_adr, reg_cnv, 2)
    result = val[1] + (val[0] << 8)
    return result

init_i2c()

while(1):
    adc_val = read_adc()
    print(adc_val)
    time.sleep(1)

bus.close()
    
