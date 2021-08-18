from classes import led_rgb as rgb
#from ../classes import HBridgeWithPWM as bridge
from classes import servo_controller as servo
from classes import pwm_controller as pwm

import time

# Receiver BCM pin map
FSIA6B = { "ch1":4, "ch3":12, "ch4":16, "ch5":20, "ch6":21 }


# Initialize our HBridge for our DC Motor
#motor = bridge.MotorController(frequency = 1000,
                                   #gpioPinPWMInput = FSIA6B['ch3'],
                                   #gpioPinMotorInput1 = 13,
                                   #gpioPinMotorInput2 = 0)

def testServo():
    # Initialize our Servo    
    Servo = servo.ServoController(frequency = 50, servo_pin = 22, min_dutycycle = 2, max_dutycycle = 12)
    for i in range(0,181,45):
        Servo.SetAngle(i)
        time.sleep(1)
    

def testReceiver():
    # RF Receiver
    #SW A
    #Down = 2000, Up = 1000
    #SW C
    #Down = 2000, Middle = 1500, Up = 1000
    CH1 = pwm.PWMController(1000, FSIA6B['ch1'])
    CH5 = pwm.PWMController(1000, FSIA6B['ch5'])
    CH6 = pwm.PWMController(1000, FSIA6B['ch6'])

    CH1.start()
    CH5.start()
    CH6.start()
    
def testLED():
    led1 = rgb.Led(17,18,27)
    led1.turnOn()
    led1.setColor('red')
    led1.turnOff()

    
while True:
    print("CH1[pin: " + str(FSIA6B['ch1']) + "] Width: " + str(CH1.GetPulseWidth()))
    #print("CH5 Width: " + str(CH5.getPulseWidth()))
    #print("CH6 Width: " + str(CH6.getPulseWidth()))
#    time.sleep(2)
    print("test servo")
    testServo()
    time.sleep(5)
