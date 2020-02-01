#HITEC SG33BL driver by Richard I. Smith 2020

import serial
from serial import STOPBITS_ONE
from serial import PARITY_NONE
import time
import binascii
import ctypes

class Servo():

	device = None #serial port object to interact with servo
	id = 0 #Servo ID number
	debug = False

	def begin(self, port, baud, id):
		self.device = serial.Serial(port, baud, stopbits=STOPBITS_ONE, parity=PARITY_NONE)
		self.id = id
	
	def end(self):
		if(self.device is not None):
			self.device.close()
	
	def read_register(self, address):
		packet = bytearray()
		packet.append(0x96) #transmit header
		packet.append(self.id) #ID of servo
		packet.append(address) #register address
		packet.append(0x00) #register len (always 0 for read)
		packet.append((self.id + address) % 256) #compute checksum
		self.device.write(packet) #send it
		return self.device.read(8)

	def write_register16(self, address, data):
		packet = bytearray()
		packet.append(0x96) #transmit header
		packet.append(self.id) #ID of servo
		packet.append(address) #register address
		packet.append(0x02) #register len of 2
		data_l = data & 0xFF
		data_h = (data & 0xFF00) >> 8
		packet.append(data_l) #little endian data low first
		packet.append(data_h)
		packet.append((self.id + address + 0x02 + data_l + data_h) % 256) # compute checksum
		if(self.debug):
			print(hex(packet[0]))
			print(hex(packet[1]))
			print(hex(packet[2]))
			print(hex(packet[3]))
			print(hex(packet[4]))
			print(hex(packet[5]))
			print(hex(packet[6]))
		else:
			self.device.write(packet)

	def write_config_register16(self, address, data):
		self.write_register16(address, data) #write the config register
		self.write_register16(0x70, 0xFFFF) #send the config update command
		
	def dump_response16(self, response):
		print("--------------------")
		print("Header: " + str(hex(response[1]))) 
		print("Servo ID: " + str(hex(response[2]))) 
		print("Register Address: " + str(hex(response[3]))) 
		print("Register Length: " + str(hex(response[4]))) 
		data = response[6] << 8
		data |= response[5]
		print("Data: " + str(hex(data)))
		print("Data Signed: " + str(ctypes.c_short(data).value))
		print("Data Unsigned: " + str(ctypes.c_ushort(data).value))
		print("Data Binary: " + str(format(data, '#018b')))
		print("Checksum: " + str(hex(response[7])))
		print("--------------------")
		
	def read_register_data(self, address):
		response = self.read_register(address)
		data = response[6] << 8
		data |= response[5]
		return data
		
	def get_status(self):
		return self.read_register_data(0x0A)
	
	def get_cur_position(self):
		data = self.read_register_data(0x0C)
		return ctypes.c_short(data).value
	
	def get_cur_velocity(self):
		data = self.read_register_data(0x0E)
		return ctypes.c_short(data).value
		
	def get_cur_torque(self):
		data = self.read_register_data(0x10)
		return ctypes.c_short(data).value
		
	def get_input_voltage(self):
		data = self.read_register_data(0x12)
		return ctypes.c_ushort(data).value * 0.1
	
	def get_mcu_temp(self):
		data = self.read_register_data(0x14)
		return ctypes.c_ushort(data).value * 0.1
		
	def get_motor_temp(self):
		data = self.read_register_data(0x16)
		return ctypes.c_ushort(data).value * 0.1
		
	def get_humidity(self):
		data = self.read_register_data(0x3C)
		return ctypes.c_ushort(data).value
		
	def set_position(self, position):
		self.write_register16(0x1E, position)
		
	def get_set_position(self):
		pos = self.read_register_data(0x1E)
		return ctypes.c_short(pos).value
		
	def set_vel_time(self, vel_time):
		self.write_register16(0x20, vel_time)
		
	def set_torque(self, torque):
		self.write_register16(0x22, torque)
		
	def set_rotate_360(self, rt360):
		self.write_register16(0x24, rt360)
		
	def get_rotate_360(self):
		rt360 = self.read_register_data(0x24)
		return ctypes.c_ushort(rt360).value
		
	def set_id(self, id):
		self.write_config_register16(0x32, id)
				
	def set_baud(self, baud):
		self.write_config_register16(0x34, baud)
		
	def set_return_delay(self, delay):
		self.write_config_register16(0x3A, delay)
		
	def set_power_cfg(self, cfg):
		self.write_config_register16(0x46, cfg)
		
	def set_estop_cfg(self, cfg):
		self.write_config_register16(0x48, cfg)
		
	def set_action_mode(self, mode):
		self.write_config_register16(0x4A, mode)
		
	def get_action_mode(self):
		data = self.read_register_data(0x4A)
		return ctypes.c_ushort(data).value
		
	def set_position_slope(self, slope):
		self.write_config_register16(0x4C, slope)
	
	def set_deadband(self, band):
		self.write_config_register16(0x4E, band)
	
	def get_deadband(self):
		band = self.read_register_data(0x4E)
		return ctypes.c_ushort(band).value
	
	def set_velocity_max(self, velocity):
		self.write_config_register16(0x54, velocity)
		
	def set_torque_max(self, torque):
		self.write_config_register16(0x56, torque)
		
	def get_torque_max(self):
		data = self.read_register_data(0x56)
		return ctypes.c_ushort(data).value

	def set_voltage_max(self, volts):
		self.write_config_register16(0x58, volts)
		
	def set_voltage_min(self, volts):
		self.write_config_register16(0x5A, volts)
		
	def get_voltage_min(self):
		data = self.read_register_data(0x5A)
		return ctypes.c_ushort(data).value * 0.1
		
	def set_temp_max(self, temp):
		self.write_config_register16(0x5C, temp)
		
	def set_temp_min(self, temp):
		self.write_config_register16(0x5E, temp)
		
	def set_position_start(self, pos):
		self.write_config_register16(0x96, pos)
		
	def get_position_start(self):
		data = self.read_register_data(0x96)
		return ctypes.c_short(data).value
		
	def set_position_end(self, pos):
		self.write_config_register16(0x94, pos)
		
	def get_position_end(self):
		data = self.read_register_data(0x94)
		return ctypes.c_short(data).value
		
	def set_position_neutral(self, pos):
		self.write_config_register16(0xC2, pos)
		
	def get_position_neutral(self):
		data = self.read_register_data(0xC2)
		return ctypes.c_short(data).value
		
	def factory_reset(self):
		self.write_config_register16(0x6E, 0x1515)
		
	
	
		
	
	


'''
dump_response16(read_register(servo, 0x01, 0x00))
dump_response16(read_register(servo, 0x01, 0x02))
dump_response16(read_register(servo, 0x01, 0x04))
dump_response16(read_register(servo, 0x01, 0x06))
dump_response16(read_register(servo, 0x01, 0x08))
dump_response16(read_register(servo, 0x01, 0x0A))
dump_response16(read_register(servo, 0x01, 0x0C))
dump_response16(read_register(servo, 0x01, 0x0E))
dump_response16(read_register(servo, 0x01, 0x10))
dump_response16(read_register(servo, 0x01, 0x12))
dump_response16(read_register(servo, 0x01, 0x14))
dump_response16(read_register(servo, 0x01, 0x16))
dump_response16(read_register(servo, 0x01, 0x1A))
dump_response16(read_register(servo, 0x01, 0x3C))
dump_response16(read_register(servo, 0x01, 0x40))
dump_response16(read_register(servo, 0x01, 0x42))
dump_response16(read_register(servo, 0x01, 0x1E))
dump_response16(read_register(servo, 0x01, 0x20))
dump_response16(read_register(servo, 0x01, 0x22))
dump_response16(read_register(servo, 0x01, 0x24))
dump_response16(read_register(servo, 0x01, 0x32))
dump_response16(read_register(servo, 0x01, 0x34))
dump_response16(read_register(servo, 0x01, 0x3A))
dump_response16(read_register(servo, 0x01, 0x46))
dump_response16(read_register(servo, 0x01, 0x48))
dump_response16(read_register(servo, 0x01, 0x4A))
dump_response16(read_register(servo, 0x01, 0x4C))
dump_response16(read_register(servo, 0x01, 0x4E))
dump_response16(read_register(servo, 0x01, 0x54))
dump_response16(read_register(servo, 0x01, 0x56))
dump_response16(read_register(servo, 0x01, 0x58))
dump_response16(read_register(servo, 0x01, 0x5A))
dump_response16(read_register(servo, 0x01, 0x5C))
dump_response16(read_register(servo, 0x01, 0x5E))
dump_response16(read_register(servo, 0x01, 0x96))
dump_response16(read_register(servo, 0x01, 0x94))
dump_response16(read_register(servo, 0x01, 0xC2))
'''

  