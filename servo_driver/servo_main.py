import ServoControl
import time
import ctypes


servo = ServoControl.Servo()

#servo.id = 1
servo.begin('/dev/ttyUSB0', 115200, 1)

#servo.set_action_mode(0b0000000001111101)
#servo.set_deadband(5)

servo.set_position_start(2200)
servo.set_position_end(3200)
#servo.set_position(900)
servo.set_position_neutral(3200)
servo.set_vel_time(4095)
servo.set_torque(4095)


print("Status: " + str(servo.get_status()))
print("Rotate 360: " + str(servo.get_rotate_360()))
print("Commanded Position: " + str(servo.get_set_position()))
print("Deadband: " + str(servo.get_deadband()))
print("Action Mode: " + str(bin(servo.get_action_mode())))
print("Input Voltage: " + str(servo.get_input_voltage()))
print("Voltage Min: " + str(servo.get_voltage_min()))
print("Torque Max: " + str(servo.get_torque_max()))
print("Start Position: " + str(servo.get_position_start()))
print("End Postiion: " + str(servo.get_position_end()))
print("Neutral Position: " + str(servo.get_position_neutral()))
print("Current Position: " + str(servo.get_cur_position()))


print(servo.get_cur_torque())

while(1):
	pos = input("TARGET POSITION: ")
	#pos = (4095 * int(pos)) / 360
	servo.set_position(ctypes.c_short(int(pos)).value)
	#print("Input Voltage: " + str(servo.get_input_voltage()))
	#time.sleep(1)
	#print(servo.get_cur_torque())
servo.end()
