import pyb

''' @file motor.py
There must be a docstring at the beginning of a Python
source file with an @file [filename] tag in it! '''

class MotorDriver:
    ''' This class implements a motor driver for the ME405 board. '''
    def __init__ (self, motor_number=1):
        ''' Creates a motor driver by initializing GPIO
        pins and turning the motor off for safety. '''
        print ('Creating a motor driver')
        self.motor_number = motor_number
        if self.motor_number != 1 and self.motor_number != 2:
            print('Cannot support more than 2 motors. Enter a valid motor number')
        elif self.motor_number == 1:
            PinA10 = pyb.Pin(pyb.Pin.board.PA10, pyb.Pin.OUT_OD, pyb.Pin.PULL_UP)
            PinA10.high ()
            #PinA10.low ()
            pinB4 = pyb.Pin (pyb.Pin.board.PB4, pyb.Pin.AF_PP, af=-1)
            tim3 = pyb.Timer (3, freq=20000)
            ## timer channel corresponding to CPU Pin PB4. channel 1 on timer 3
            self.ch1 = tim3.channel (1, pyb.Timer.PWM, pin=pinB4)        
            self.ch1.pulse_width_percent(0)
            pinB5 = pyb.Pin (pyb.Pin.board.PB5, pyb.Pin.AF_PP, af=-1)
            ## timer channel corresponding to CPU Pin PB5. channel 2 on timer 3
            self.ch2 = tim3.channel (2, pyb.Timer.PWM, pin=pinB5)
            self.ch2.pulse_width_percent(0)
        elif self.motor_number == 2:
            PinC1 = pyb.Pin(pyb.Pin.board.PC1, pyb.Pin.OUT_OD, pyb.Pin.PULL_UP)
            PinC1.high ()
            #PinC1.low ()
            pinA0 = pyb.Pin (pyb.Pin.board.PA0, pyb.Pin.AF_PP, af=-1)
            tim5 = pyb.Timer (5, freq=20000)
            ## timer channel corresponding to CPU Pin PB4. channel 1 on timer 5
            self.ch1 = tim5.channel (1, pyb.Timer.PWM, pin=pinA0)        
            self.ch1.pulse_width_percent(0)
            pinA1 = pyb.Pin (pyb.Pin.board.PA1, pyb.Pin.AF_PP, af=-1)
            ## timer channel corresponding to CPU Pin PB5. channel 2 on timer 5
            self.ch2 = tim5.channel (2, pyb.Timer.PWM, pin=pinA1)
            self.ch2.pulse_width_percent(0)
        else:
            pass

    def set_duty_cycle (self, level):
        ''' This method sets the duty cycle to be sent
        to the motor to the given level. Positive values
        cause torque in one direction, negative values
        in the opposite direction.
        @param level A signed integer holding the duty
        cycle of the voltage sent to the motor. Saturated at range
        limits -100 and 100 '''
        #print ('Setting duty cycle to ' + str (level))
        self.level = level
        if self.level > 0:
            # setting B4 is positive direction, B5 is negative
            self.ch1.pulse_width_percent(0)
            self.ch2.pulse_width_percent(self.level)
    
        else:
            self.ch2.pulse_width_percent(0)
            self.ch1.pulse_width_percent(abs(self.level))
        
if __name__ == '__main__':
    print("Motor.py is Main")