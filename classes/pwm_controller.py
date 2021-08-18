# Basil Guevarra
# This will be a reusable library to work with PWM
# Usage:
#   init(frequency, pwm_input_pin)


#!/usr/bin/env python
import pigpio
import time

class PWMController:
    
    def __init__(self, frequency, pwm_input_pin, debug=0):        
        self.frequency = frequency
        self.pin = pwm_input_pin
        self.debug = debug
        
        # Instance Variables
        self.falling = 0
        self.rising = 0        
        self.pulse_width = 0

        # PIGPIO to listen to 
        self.pi = pigpio.pi()
        self.pi.set_mode(self.pin, pigpio.INPUT)
        self.pi.set_pull_up_down(self.pin, pigpio.PUD_DOWN)
        self.pi.read(self.pin) 
            
    def Start(self):
        # Set callback listeners
        cbrise = self.pi.callback(self.pin, pigpio.RISING_EDGE, self._cbrise)
        cbfall = self.pi.callback(self.pin, pigpio.FALLING_EDGE, self._cbfall)       
        
    def _cbrise(self, gpio, level, tick):        
            self.rising = tick            
            return

    def _cbfall(self, gpio, level, tick):        
        # Calculate pulse width
        self.falling = tick
        self.pulse_width = self.falling - self.rising;
        if debug:
            print("Width: " + str(falling - rising))                        
        return
                    
    def GetPulseWidth(self):
        # Get the rounded pulse width
        # The calculation and rounding here remove some noise
        pulse_width = round((self.pulse_width/1000),1)*1000
        if self.debug:
            print("GetPulseWidth(): pulse_width=" + str(pulse_width))
        return pulse_width

   