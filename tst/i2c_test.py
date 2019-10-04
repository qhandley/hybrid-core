import smbus

channel = 1

address = 0x40

cmd = 0x00

bus = smbus.SMBus(channel)

while(True):
    val = bus.read_i2c_block_data(address, cmd)
    print(val)
    
