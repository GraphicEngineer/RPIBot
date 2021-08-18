"""
This class allows you to control various types of servos. It's required the setup requires frequency, and duty cycle specs.
The angle calculation will dyanmically account for the servo requirements. 

FUTURE: __init__() should intake the range of motion, at the moment, 180 degrees is assumed in the calculations.
"""

__version__ = '0.1'
__author__ = 'Basil Guevarra'

# This will be a reusable library to work with our Servos

#!/usr/bin/env python
import RPi.GPIO as GPIO
import time

class ServoController:

    def __init__(self, frequency, servo_pin, min_dutycycle=5, max_dutycycle=10, debug=0):
        # passed in args
        self.frequency = frequency
        self.servo_pin = servo_pin
        self.min_dutycycle = min_dutycycle
        self.max_dutycycle = max_dutycycle
        self.debug = debug;

        # pin setup
        GPIO.setup(self.servo_pin, GPIO.OUT)
        GPIO.output(self.servo_pin, GPIO.HIGH)

        # servo pin pwm instance
        self.pwm = GPIO.PWM(self.servo_pin, frequency)
        self.pwm.start(0)

    # use seldom, good for internal testing
    def set_duty_cycle(self, duty):
        self.pwm.ChangeDutyCycle(duty)

    # intended for usage
    def set_angle(self, angle):
        # Calculation for angle in degrees to dutycycle for a current servo
        duty = (angle / 180) * (self.max_dutycycle - self.min_dutycycle) + self.min_dutycycle
        if self.debug:
            print("ServoController.set_angle(): Angle=" + str(angle) + " Duty=" + str(duty))
        GPIO.output(self.servo_pin, False)
        self.pwm.ChangeDutyCycle(duty)
        time.sleep(1)
        GPIO.output(self.servo_pin, True)
        self.pwm.ChangeDutyCycle(0)

    def Start(self):
        self.pwm.start(0)

    def Stop(self):
        self.pwm.stop()

