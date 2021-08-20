"""
Prior from 
# tutorial url: https://osoyoo.com/2017/07/07/ir-remote/

Modified by Basil Guevarra to be used for a laser gun (IR gun) reaction
Purpose -- this will be used to move a servo-connected target to respond.
Future -- target will be able to blast back with it's own IR transmitter

Secondary fun for kids, we'll tie this reaction response to our robot to "pause" 
before shooting back
"""

import RPi.GPIO as GPIO
import re
import time
from classes import led_rgb as rgb


# These are BCM Pins
IR_PIN=23 #IR pin in physical Pin 12 
_LED = { "r":17, "g":18, "b":27 }

# IR Buttons on my Samsung remote seem to have LOTS of values when pressed, this app helped "See" the codes and I added them here to change LED color
KEY_1="0xe0e040bf, 0x706bf, 0xe040bf, 0xbf" #Samsung Power
KEY_2="0xe0c04bb4, 0xe0e04bb4, 0x38384bb4, 0xe0e04bb4, 0xe04bb4, 0x60e04bb4, 0x383812, 0x10e04bb4, 0xe0e04bb0, 0x20e04bb4" #Samsung 123
KEY_3="0x7070738c, 0xe0e0738c, 0x738c, 0x20e0738c" #Samsung Extra

_BLUE_TEAM = { "0xf001", "0xf011", "0xf011", "0xf012" }
_RED_TEAM = { "0xf101", "0xf112", "0x3d12" }
_GREEN_TEAM = { "0xf102", "0xf112", "0xb112", "0xf113" }
_WHITE_TEAM = { "0xf002", "0x7802", "0xf013", "0xf012", "0xf013", "0xf012" }

# Global initially needed, I'll work to improve. This is dirty.
global led1
global points
points = {"blue":0, "red":0, "green":0, "white":0, "unknown":0}

def setup():
    GPIO.setup(IR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    #Initializing the LED usage
    global led1
    led1 = rgb.LED(_LED['r'], _LED['g'], _LED['b'])


# No changes from Osoyoo
def binary_aquire(pin, duration):
    # aquires data as quickly as possible
    t0 = time.time()
    results = []
    while (time.time() - t0) < duration:
        results.append(GPIO.input(pin))
    return results


# Modified oyosoo's bouncetime to account for a higher sensitivity needed for the laser guns
# and reduced the pulse detection so < 0.5ms is a 0, > 0.5ms is a 1
def on_ir_receive(pinNo, bouncetime=150):
    # when edge detect is called (which requires less CPU than constant
    # data acquisition), we acquire data as quickly as possible
    data = binary_aquire(pinNo, bouncetime/1000.0)    
    if len(data) < bouncetime:
        return
    rate = len(data) / (bouncetime / 1000.0)
    pulses = []
    i_break = 0
    # detect run lengths using the acquisition rate to turn the times in to microseconds
    for i in range(1, len(data)):
        if (data[i] != data[i-1]) or (i == len(data)-1):
            pulses.append((data[i-1], int((i-i_break)/rate*1e6)))
            i_break = i
    # decode ( < 0.5 ms "1" pulse is a 0, > 0.5 ms "1" pulse is a 1, longer than 2 ms pulse is something else)
    # IMPORTANT: Currently, this does not decode channel, which may be a piece of the information after the long 1 pulse in the middle
    outbin = ""
    for val, us in pulses:
	# I added this rounding calculation in an attempt to smoothen the results
        calcUs = round(us/100, 0) * 100
        #print(str(us) + " => " + str(calcUs))
        us = calcUs
        if val != 1:
            continue
        if outbin and us > 1000:
            break
        elif us < 500: 	
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


def blink(color, duration):
    global led1
    t0 = time.time()
    while (time.time() - t0) < duration:
        led1.turn_off()
        time.sleep(1)
        led1.set_color(color)
        time.sleep(1)

def score(ir_code):
    global points
    global led1
    if (re.search(str(hex(code)), ''.join(_BLUE_TEAM))):
        points["blue"] = points["blue"] + 1
        led1.set_color("blue")
    elif (re.search(str(hex(code)), ''.join(_RED_TEAM))):
        points["red"] = points["red"] + 1
        led1.set_color("red")
    elif (re.search(str(hex(code)), ''.join(_GREEN_TEAM))):
        points["green"] = points["green"] + 1
        led1.set_color("green")
    elif (re.search(str(hex(code)), ''.join(_WHITE_TEAM))):
        points["white"] = points["white"] + 1
        led1.set_color("white")
    else:
        points["unknown"] = points["unknown"] + 1
        led1.set_color("purple")
    time.sleep(1)


def find_winner():
    # Yep, I realize there can't be a tie in this current logic, easy fix later.
    # This is just a proof of concept in an afternoon
    # I could also look up a python function that could get the highest value in an array and return the index...
    global points
    high_score = "unknown"
    if points["blue"] > points[high_score]:
        high_score = "blue"
    if points["red"] > points[high_score]:
        high_score = "red"
    if points["green"] > points[high_score]:
        high_score = "green"
    if points["white"] > points[high_score]:
        high_score = "white"

    if high_score == "unknown":
        high_score = "yellow" 

    return high_score



if __name__ == "__main__":
    # Initially set the "game" off, make the LED red to signify we're not live yet.
    global led1

    setup()
    game_on = 0
    led1.set_color('red')

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
            if ((re.search(str(hex(code)), KEY_1, re.I)) or (re.search(str(hex(code)), KEY_2, re.I))):
                if (game_on == 0):
                    print("Game is on!")
                    blink("green", 10)
                    game_on = 1
                    led1.set_color('cyan')
                elif (game_on == 1):
                    print("Timeout!")
                    game_on = 0
                    blink("red", 5)
                    winner_color = find_winner()
                    blink(winner_color, 10)
                    led1.set_color("red")
                    # Reset the scores
                    points = {"blue":0, "red":0, "green":0, "white":0, "uknown":0}
            elif (re.search(str(hex(code)), KEY_2, re.I)):
                # Used later to set different "game" options
                # For now, no impact to the play.
               led1.set_color('yellow')
            elif (re.search(str(hex(code)), KEY_3, re.I)):
                # Used later to set different "game" options
                # For now, no impact to the play.
                led1.set_color('purple')
            else:
		        # Couldn't find this code, let's output it here so we can add it to our lists the next time
                if (game_on == 1):
                    # Record a random hit!
                    print(str(hex(code)))
                    # Now try to figure out which team gets the point...
                    score(code)
                    led1.set_color('cyan')


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

