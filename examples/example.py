"""
Example file to test the various module classes

FUTURE: I'll create an orchestration example combining PWM and HBridge or Servo.  Right now the HBridgeWithPWM contains its own PWMController
"""

__version__ = '0.1'
__author__ = 'Basil Guevarra'

from classes import led_rgb as rgb
#from ../classes import HBridgeWithPWM as bridge
from classes import servo_controller as servo
from classes import pwm_controller as pwm

import time

# Pin maps
_FSIA6B = { "ch1":4, "ch3":12, "ch4":16, "ch5":20, "ch6":21 }	# Channels correspond to RF Receiver used: FSIA6B
_LED = { "r":17, "g":18, "b":27 }

# Initialize our HBridge for our DC Motor
#motor = bridge.MotorController(frequency = 1000,
                                   #gpioPinPWMInput = FSIA6B['ch3'],
                                   #gpioPinMotorInput1 = 13,
                                   #gpioPinMotorInput2 = 0)

def test_servo():
    # Initialize our Servo
    Servo = servo.ServoController(frequency = 50, servo_pin = 22, min_dutycycle = 2, max_dutycycle = 12)
    for i in range(0,181,45):
        Servo.set_angle(i)
        time.sleep(1)


def test_receiver():
    # RF Receiver
    #SW A
    #Down = 2000, Up = 1000
    #SW C
    #Down = 2000, Middle = 1500, Up = 1000
    CH1 = pwm.PWMController(1000, _FSIA6B['ch1'])
    CH5 = pwm.PWMController(1000, _FSIA6B['ch5'])
    CH6 = pwm.PWMController(1000, _FSIA6B['ch6'])

    CH1.start()
    CH5.start()
    CH6.start()

def test_LED():
    led1 = rgb.LED(_LED['r'], _LED['g'], _LED['b'])
    led1.turn_on()
    led1.set_color('red')
    led1.turn_off()
    led1.test(3)

while True:
#    print("CH1[pin: " + str(FSIA6B['ch1']) + "] Width: " + str(CH1.GetPulseWidth()))
#    print("CH5 Width: " + str(CH5.getPulseWidth()))
#    print("CH6 Width: " + str(CH6.getPulseWidth()))
#    time.sleep(2)
    print("test LEDs")
    test_LED()
    print("test servo")
    test_servo()
    time.sleep(5)
