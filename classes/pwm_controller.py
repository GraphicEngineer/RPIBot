# Basil Guevarra
# This will be a reusable library to work with our RF Receiver
# Usage:
#   init(R,G,B) to set the targeted GPIO pins
#   setRGBColor() to set the RGB color
#   turnOff() to turn off the LED
#   turnOn() to turn on the LED to white
#   test() to run the R,G,B,White,Off test

#!/usr/bin/env python
import pigpio
import time

class PWMController:
    
    def __init__(self, frequency, gpioPinPWMInput):        
        self.frequency = frequency
        self.pin = gpioPinPWMInput
        
        # Instance Variables
        self.falling = 0
        self.rising = 0        
        self.pulseWidth = 0

        # PIGPIO to listen to 
        self.pi = pigpio.pi()
        self.pi.set_mode(self.pin, pigpio.INPUT)
        self.pi.set_pull_up_down(self.pin, pigpio.PUD_DOWN)
        self.pi.read(self.pin) 
            
    def start(self):
        # Set callback listeners
        cbrise = self.pi.callback(self.pin, pigpio.RISING_EDGE, self.cbrise)
        cbfall = self.pi.callback(self.pin, pigpio.FALLING_EDGE, self.cbfall)       
        
    def cbrise(self, gpio, level, tick):        
            self.rising = tick
            #print(rising)           
            return

    def cbfall(self, gpio, level, tick):        
        self.falling = tick
        self.pulseWidth = self.falling - self.rising;
        #print("Width: " + str(falling - rising))                        
        return
    
    def getPin(self):
        return self.pin
    
    def getPigPIO(self):
        return self.pi
                
    def getPulseWidth(self):
        return round((self.pulseWidth/1000),1)*1000