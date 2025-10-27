#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

import os
import glob
import time

BtnPin = 11 #GPIO 17
BuzzPin   = 12 #GPIO 27
Rpin   = 13
VibPin = 35 #GPIO 19
TempPin = 7 #GPIO 4

# These tow lines mount the device:
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
# Get all the filenames begin with 28 in the path base_dir.
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

press_count = []
buzzing = False

def setup():
	GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
	GPIO.setup(BuzzPin, GPIO.OUT)     # Set Green Led Pin mode to output
	GPIO.setup(Rpin, GPIO.OUT)     # Set Red Led Pin mode to output
	GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V)
	GPIO.setup(VibPin, GPIO.OUT)
#	GPIO.add_event_detect(BtnPin, GPIO.BOTH, callback=detect, bouncetime= 100)
	GPIO.add_event_detect(BtnPin, GPIO.FALLING, callback=detect, bouncetime=100)

def Alarm(x):
	global buzzing
	if buzzing:
		print("not buzzing")
		GPIO.output(Rpin, 1)
		GPIO.output(BuzzPin, 0)
		buzzing = False
	else:
		print("buzzing")
		GPIO.output(Rpin, 0)
		GPIO.output(BuzzPin, 1)
		buzzing = True

def detect(chn):
	global press_count
	now = time.time()
	x = GPIO.input(BtnPin)
	if(x == 1):
		press_count.append(now)


	#print("Pressed")
	print(press_count)
	press_count = [t for t in press_count if now - t <= 3]
	if len(press_count) >= 3:
		print("Buzzed")
		Alarm(x)
		press_count = []
	#print("out")

def read_rom():
    name_file=device_folder+'/name'
    f = open(name_file,'r')
    return f.readline()
 
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp():
    lines = read_temp_raw()
    # Analyze if the last 3 characters are 'YES'.
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    # Find the index of 't=' in a string.
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        # Read the temperature .
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_f	

def checkTemp():
	print('F=%3.3f'% read_temp())
	if(read_temp() > 77):
		GPIO.output(VibPin, 1)
	else:
		GPIO.output(VibPin,0)

def loop():
	while True:
		checkTemp()
		#time.sleep(0.02)
		pass

def destroy():
	GPIO.output(BuzzPin, GPIO.HIGH)       # Green led off
	GPIO.cleanup()                     # Release resource

if __name__ == '__main__':     # Program start from here
	setup()
	try:
		loop()
	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
		destroy()

