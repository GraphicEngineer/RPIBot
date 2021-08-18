# Basil Guevarra
# This will be a reusable library to work with RGB LEDs
# Usage:
#   init(R,G,B) to set the targeted GPIO pins
#   setRGBColor() to set the RGB color
#   turnOff() to turn off the LED
#   turnOn() to turn on the LED to white
#   test() to run the R,G,B,White,Off test

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class LED:
    # English color map
    _COLOR_MAP = {
	'red':(1,0,0),
        'green':(0,1,0),
        'blue':(0,0,1),
        'yellow':(1,1,0),
        'cyan':(0,1,1),
        'purple':(1,0,1),
        'white':(1,1,1)
	}

    def __init__(self, pin_R, pin_G, pin_B):
        self.pins = { }
        self.pins['pin_R'] = pin_R
        self.pins['pin_G'] = pin_G
        self.pins['pin_B'] = pin_B

        for pin in self.pins:
            GPIO.setup(self.pins[pin], GPIO.OUT)

    def set_color(self, color):
        print('Color requested: ' + color)
        rgbTuple = LED._COLOR_MAP[color]
        GPIO.output(self.pins['pin_R'], rgbTuple[0])
        GPIO.output(self.pins['pin_G'], rgbTuple[1])
        GPIO.output(self.pins['pin_B'], rgbTuple[2])

    def set_rgb_color(self,R,G,B):
        print('Received R,G,B: ' + str(R) + str(G) + str(B))
        GPIO.output(self.pins['pin_R'], R)
        GPIO.output(self.pins['pin_G'], G)
        GPIO.output(self.pins['pin_B'], B)

    def turn_off(self):
        print('LED Off')
        for pin in self.pins:
            GPIO.output(self.pins[pin], 0)

    def turn_on(self):
        print('LED On - White')
        for pin in self.pins:
            GPIO.output(self.pins[pin], 1)

    def test(self, speed):
        print('LED Test with speed: ' + str(speed))
        for r in range(2):
            for g in range(2):
                for b in range(2):
                    print('R: ' + str(r) + ' G: ' + str(g) + ' B: ' + str(b))
                    GPIO.output(self.pins['pin_R'], r)
                    GPIO.output(self.pins['pin_G'], g)
                    GPIO.output(self.pins['pin_B'], b)
                    time.sleep(speed)
