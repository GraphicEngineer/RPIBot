"""
Basil Guevarra to be used for a reactive laser target.
Primary: This was made for fun for my kids.

Purpose -- Reactive game that moves a target based on it being hit.  
           This project also uses a RGB LED to communicate the hit and the scoring.           
Future -- Target may be able to blast back with it's own IR transmitter
          Considering multiple "game modes"
          Considering multiple units that could communicate/talk to each other for 
          capture the flag.

Parts List
* Raspberry PI 3 (or higher) -- https://amzn.to/2UCIyId 
* IR Recevier/Transmitter -- https://amzn.to/3kdaGuh
* RGB LED -- https://amzn.to/2WhshZy
* Laser Tag Guns -- https://amzn.to/3B10dJk
* 55g Servo (could use a small 9g) -- https://amzn.to/3j2hWtE
"""

import RPi.GPIO as GPIO
import re
import time
from classes import led_rgb as rgb
from classes import servo_controller as servo


# These are BCM Pins
# I used a VS1838B from Amazon: 
IR_PIN=23 #IR pin in physical Pin 12 
_LED = { "r":17, "g":18, "b":27 }
#_LED = { "r":26, "g":19, "b":6 }  #Breacdboard values

# IR Buttons on my Samsung remote seem to have LOTS of values when pressed, most likely due to the crude algorithm to "find the code"
KEY_1="0xe0e040bf, 0x706bf, 0xe040bf, 0xbf" #Samsung Power
KEY_2="0xe0c04bb4, 0xe0e04bb4, 0x38384bb4, 0xe0e04bb4, 0xe04bb4, 0x60e04bb4, 0x383812, 0x10e04bb4, 0xe0e04bb0, 0x20e04bb4" #Samsung 123
KEY_3="0x7070738c, 0xe0e0738c, 0x738c, 0x20e0738c" #Samsung Extra

# Laser Tag Gunshot Values (Handgun, Shortgun, AR-15, Bazooka)
_BLUE_TEAM = { "0xf001", "0xf011", "0xf011", "0xf012" }
_RED_TEAM = { "0xf101", "0xf112", "0x3d12" }
_GREEN_TEAM = { "0xf102", "0xf112", "0xb112", "0xf113" }
_WHITE_TEAM = { "0xf002", "0x7802", "0xf013", "0xf012", "0xf013", "0xf012" }

# Global initially needed, I'll work to improve. This is dirty.
global Servo
global led1
global points
points = {"blue":0, "red":0, "green":0, "white":0, "unknown":0}

def setup():
    GPIO.setup(IR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    #Initializing the LED usage
    global led1
    led1 = rgb.LED(_LED['r'], _LED['g'], _LED['b'])
    
    # Initialize our Servo
    global Servo    
    Servo = servo.ServoController(frequency = 50, servo_pin = 22, min_dutycycle = 2, max_dutycycle = 12)
    reset_servo()


"""
This binary_acquire() comes from Osoyoo:
https://osoyoo.com/2018/09/18/micro-bit-lesson-using-the-ir-controller/
"""
def binary_aquire(pin, duration):    
    # aquires data as quickly as possible
    t0 = time.time()
    results = []
    while (time.time() - t0) < duration:
        results.append(GPIO.input(pin))
    return results

"""
Simple reset the servo to starting position.  In this project, it will be 1 degrees
Note: This uses a simple Servo class I created to simplify the Sero usage.
"""
def reset_servo():
    global Servo
    Servo.set_angle(1)


""" 
Simple servo call to rotate the servo a set number of degrees, hold the position for 
the requested duration, then reset the servo back.  This is key to the reactive part 
of the game.
"""
def rotate_servo_then_reset(angle=65, duration=5):
    global Servo
    # Initialize our Servo
    Servo.set_angle(angle)
    time.sleep(duration)
    reset_servo()


"""
This binary_acquire() comes from Osoyoo:
https://osoyoo.com/2018/09/18/micro-bit-lesson-using-the-ir-controller/

My modification were made to reduce bounce time and thresholds for my listed equipment.
I used lots of trial and error with my boys shooting the target to get the consistent
translated codes.  Future improvement would be to consider using the LIRC method, but this 
was MUCH faster for an afternoon project.
"""
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

"""
Reusable method to blink our RGB LED for a set duration
Note: This uses the LED class I made up to simplify RGB
usage and to teach OOP to my 9yr old.
"""        
def blink(color, duration):
    global led1
    t0 = time.time()
    while (time.time() - t0) < duration:
        led1.turn_off()
        time.sleep(1)
        led1.set_color(color)
        time.sleep(1)

"""
Method is called when a recorded shot is received.
This will attempt to find the shooter and record the points.
This is not perfect as it stands, some of the codes may overlap so first
in the list here is the winner.  This can be improved by improving the 
IR detection and the IR code list defined up top.
"""        
def score(ir_code):
    global points
    global led1
    valid_shot = False
    if (re.search(str(hex(code)), ''.join(_BLUE_TEAM))):
        points["blue"] = points["blue"] + 1
        led1.set_color("blue")
        valid_shot = True    
    elif (re.search(str(hex(code)), ''.join(_RED_TEAM))):
        points["red"] = points["red"] + 1
        led1.set_color("red")
        valid_shot = True
    elif (re.search(str(hex(code)), ''.join(_GREEN_TEAM))):
        points["green"] = points["green"] + 1
        led1.set_color("green")
        valid_shot = True
    elif (re.search(str(hex(code)), ''.join(_WHITE_TEAM))):
        points["white"] = points["white"] + 1
        led1.set_color("white")
        valid_shot = True
    # If we wanted to record the shots without identified shooter, we could
    # save it here.  I opted afterwards to remove this functionality.
    #else:
    #    points["unknown"] = points["unknown"] + 1
    #    led1.set_color("purple")
            
    # Rotate our servo enough to "react", then reset after 5 seconds.
    # The duration here can be adjusted for a faster pace game
    if valid_shot:
        rotate_servo_then_reset(65, 5)    
    time.sleep(1)


"""
This method is called upon game completion to find the winner.
I just started learning Python a few days ago and I suspect there will be a MUCH
better way to do this in the future.  This down and dirty method works but I'll
probably cringe in the future when I review it again.
"""
def find_winner():
    # Yep, I realize there can't be a tie in this current logic, easy fix later.
    # This is just a proof of concept in an afternoon
    # I could also look up a python function that could get the highest value in an array and return the index...
    global points
    high_score = "unknown"
    if points["blue"] > 0:
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

"""
Obligatory clean up
"""
def destroy():
    GPIO.cleanup()


"""
Starting off the game...
"""
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
            print(str(code))
            # Doing a re.search here, might be something more efficient I'll change it to later.             
            if ((re.search(str(hex(code)), KEY_1, re.I)) or (re.search(str(hex(code)), KEY_2, re.I))):
                if (game_on == 0):
                    print("Game is on!")
                    blink("green", 5)
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
                    points = {"blue":0, "red":0, "green":0, "white":0, "unknown":0}
            
            elif (re.search(str(hex(code)), KEY_2, re.I)):
                # Used later to set different "game" options
                # For now, no impact to the play.
               led1.set_color('yellow')
            
            elif (re.search(str(hex(code)), KEY_3, re.I)):
                # Used later to set different "game" options
                # For now, no impact to the play.
                led1.set_color('purple')
            
            else:
                # Code received is not game-modification code.  Let's check to see if it's from one of
                # our players.		    
                if (game_on == 1):
                    # Record a random hit!
                    print(str(hex(code)))
                    # Now try to figure out which team gets the point...
                    score(code)
                    led1.set_color('cyan')

                # # If we're not playing yet, make it easy on the players and let the first shot
                # # activate the start sequence.  This can be commented out if you want to require
                # # the IR remote control to start/stop the game.                    
                # elif (game_on == 0):
                #     print("Game is on!")
                #     blink("green", 5)
                #     game_on = 1
                #     led1.set_color('cyan')


    except KeyboardInterrupt:
        # User pressed CTRL-C
        # Reset GPIO settings
        destroy()
        print("Ctrl-C pressed!")
    except RuntimeError:
        # this gets thrown when control C gets pressed
        # because wait_for_edge doesn't properly pass this on        
        pass
    print("Quitting")
    destroy()

