# Basil Guevarra
# This will be a reusable library to work with our Servos

#!/usr/bin/env python
import RPi.GPIO as GPIO
import time

class ServoController:
    
    def __init__(self, frequency, servo_pin, min_dutycycle=5, max_dutycycle=10):
        # passed in args
        self.frequency = frequency
        self.servo_pin = servo_pin
        self.min_dutycycle = min_dutycycle
        self.max_dutycycle = max_dutycycle

        # pin setup
        GPIO.setup(self.servo_pin, GPIO.OUT)
        GPIO.output(self.servo_pin, GPIO.HIGH)
        
        # servo pin pwm instance
        self.pwm = GPIO.PWM(self.servo_pin, frequency)
        self.pwm.start(0)            
    
    # use seldom, good for internal testing
    def _setDutyCycle(self, duty):
        self.pwm.ChangeDutyCycle(duty)
        
    # intended for usage
    def setAngle(self, angle):       
        # Calculation for angle in degrees to dutycycle for a current servo        
        duty = (angle / 180) * (self.max_dutycycle - self.min_dutycycle) + self.min_dutycycle 
        print("Angle" + str(angle) + " Duty: " + str(duty))
        GPIO.output(self.servo_pin, False)
        self.pwm.ChangeDutyCycle(duty)
        time.sleep(1)
        GPIO.output(self.servo_pin, True)
        self.pwm.ChangeDutyCycle(0)                
        
    def start(self):
        self.pwm.start(0)
        
    def stop(self):
        self.pwm.stop()
        