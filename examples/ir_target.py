"""
Prior from 
# tutorial url: https://osoyoo.com/2017/07/07/ir-remote/

Modified by Basil Guevarra
"""

import RPi.GPIO as GPIO
import re
from time import time
from classes import led_rgb as rgb


# These are BCM Pins
IR_PIN=23 #IR pin in physical Pin 12 
_LED = { "r":17, "g":18, "b":27 }

# IR Buttons on my Samsung remote seem to have LOTS of values when pressed, this app helped "See" the codes and I added them here to change LED color
KEY_1="0xe0e040bf, 0x706bf, 0xe040bf, 0xbf" #Samsung Power
KEY_2="0xe0c04bb4, 0xe0e04bb4, 0x38384bb4, 0xe0e04bb4, 0xe04bb4, 0x60e04bb4, 0x383812, 0x10e04bb4, 0xe0e04bb0, 0x20e04bb4" #Samsung 123
KEY_3="0x7070738c, 0xe0e0738c, 0x738c, 0x20e0738c" #Samsung Extra

# Global initially needed, I'll work to improve. This is dirty.
global led1

def setup():
    GPIO.setup(IR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    #Initializing the LED usage
    global led1
    led1 = rgb.LED(_LED['r'], _LED['g'], _LED['b'])


# No changes from Osoyoo
def binary_aquire(pin, duration):
    # aquires data as quickly as possible
    t0 = time()
    results = []
    while (time() - t0) < duration:
        results.append(GPIO.input(pin))
    return results


# Modified oyosoo's bouncetime to account for a  higher sensitivity needed for the laser guns
def on_ir_receive(pinNo, bouncetime=150):
    # when edge detect is called (which requires less CPU than constant
    # data acquisition), we acquire data as quickly as possible
    data = binary_aquire(pinNo, bouncetime/1000.0)
    #print(str(data))
    if len(data) < bouncetime:
#        print("Len Data: " + str(len(data)))
        return
    rate = len(data) / (bouncetime / 1000.0)
#    print("Rate: " + str(rate))
    pulses = []
    i_break = 0
    # detect run lengths using the acquisition rate to turn the times in to microseconds
    for i in range(1, len(data)):
        if (data[i] != data[i-1]) or (i == len(data)-1):
            pulses.append((data[i-1], int((i-i_break)/rate*1e6)))
            i_break = i
    # decode ( < 1 ms "1" pulse is a 1, > 1 ms "1" pulse is a 1, longer than 2 ms pulse is something else)
    # does not decode channel, which may be a piece of the information after the long 1 pulse in the middle
    outbin = ""
    for val, us in pulses:
        calcUs = round(us/100, 0) * 100
        print(str(us) + " => " + str(calcUs))
        us = calcUs
        if val != 1:
            continue
        if outbin and us > 1000:
            break
        elif us < 500: 	# Set this threshold to 500... the laser guns we use have short pulses
            outbin += "0"
        elif 500 <= us < 1000:
            outbin += "1"
    try:
        return int(outbin, 2)
    except ValueError:
        # probably an empty code
        return None


def destroy():
    GPIO.cleanup()


if __name__ == "__main__":
    global led1
    setup()
    try:
        print("Starting IR Listener")
        while True:
            print("Waiting for signal")
            GPIO.wait_for_edge(IR_PIN, GPIO.FALLING)
            code = on_ir_receive(IR_PIN)

            if code is None:
               continue
	    # Doing a re.search here, might be something more efficient but since Python doesn't have 
            # an array search, a figured a simple search string would suffice
            if (re.search(str(hex(code)), KEY_1, re.I)):
                led1.set_color('green')
            elif (re.search(str(hex(code)), KEY_2, re.I)):
               led1.set_color('blue')
            elif (re.search(str(hex(code)), KEY_3, re.I)):
                led1.set_color('red')
            else:
		# Couldn't find this code, let's output it here so we can add it to our lists the next time
                print(str(hex(code)))

    except KeyboardInterrupt:
        # User pressed CTRL-C
        # Reset GPIO settings
        print("Ctrl-C pressed!")
    except RuntimeError:
        # this gets thrown when control C gets pressed
        # because wait_for_edge doesn't properly pass this on
        pass
    print("Quitting")
    destroy()
