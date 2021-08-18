# Basil Guevarra
# This will be a reusable library to work with our HBridge
# Usage:
#   init(R,G,B) to set the targeted GPIO pins
#   setRGBColor() to set the RGB color
#   turnOff() to turn off the LED
#   turnOn() to turn on the LED to white
#   test() to run the R,G,B,White,Off test

#!/usr/bin/env python
import pigpio
import RPi.GPIO as GPIO
import time
import os, sys
from RoboModules.Motor import PWM as pwm

#GPIO.setmode(GPIO.BOARD)
#GPIO.setwarnings(False)

class MotorController:
    
    #speeds = [0,10,25,50,75,100] #0 Is full speed, 100 is stopped    
    
    def __init__(self, frequency, gpioPinPWMInput, gpioPinMotorInput1, gpioPinMotorInput2):        
        self.CH = pwm.PWMController(frequency = frequency, gpioPinPWMInput = gpioPinPWMInput)
        self.pins = { 'input1': gpioPinMotorInput1, 'input2': gpioPinMotorInput2 }
        self.isMotorInput1InUse = gpioPinMotorInput1 > 0;
        self.isMotorInput2InUse = gpioPinMotorInput2 > 0;
        self.listening = False;
        #self.gpioPinPWMInput = gpioPinPWMInput

        # Initialize PINS
        for i in self.pins:
           # if self.pins[i] > 0:
            GPIO.setup(self.pins[i], GPIO.OUT)   # Set pins' mode is output
            GPIO.output(self.pins[i], GPIO.HIGH) # Set pins to high(+3.3V) to off

        # Set the initial PWM based on frequency
        #if self.isMotorInput1InUse:
        self.motorInput1 = GPIO.PWM(self.pins['input1'], frequency)
        self.setSpeed(100)
        self.motorInput1.start(0)
        

        #if self.isMotorInput2InUse:
        #    self.motorInput2 = GPIO.PWM(self.pins['input2'], frequency)
        #    self.motorInput2.start(0)
                                        
    def convertPulseWidthToRelativeSpeed(self, pulseWidth):
        #print('Width: ' + str(pulseWidth))
        speed = (pulseWidth - 1000)/10
        if speed < 2:
            speed = 0
        if speed > 98:
            speed = 100
        speed = 100 - speed
            
        # Speed for human understanding it really 100 - the calculated speed
        #print('Setting speed to: ' + str(100 - speed))
        return speed;
        
    def setSpeed(self, speed):
        self.motorInput1.ChangeDutyCycle(speed)
        # To Do - no accounting for the second input?!?!?
        
    def startListening(self, msToCheck):
        self.listening = True;
        while self.listening:
            pulseWidth = self.CH.getPulseWidth()
            speed = self.convertPulseWidthToRelativeSpeed(pulseWidth)
            self.setSpeed(speed)
            time.sleep(1)
            
    def stopListening(self):
        self.listening = False
       #     speed = convertPulseWidthToRelativeSpeed(width)
       #     setSpeed(self,speed)
       
  
    def stopHBridge(self):
        #print("Stop HBrdige")
        if self.isMotorInput1InUse:
            self.motorInput1.stop()
        #if self.isMotorInput2InUse:
        #    self.motorInput2.stop()
        for i in self.pins:
            GPIO.output(self.pins[i], GPIO.HIGH)    # Turn off all HBRIDGE    
  
