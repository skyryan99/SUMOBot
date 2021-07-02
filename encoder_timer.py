import pyb

'''@file encoder_timer.py'''

class EncoderTimer:
    '''This class implements an encoder timer on the ME 405 board.
    Encoder values are read to measure the movement of a motor.'''
    
    def __init__(self, encoderNumber=1):
        '''Initializes encoder timer to measure the position of the motor'''       
        print("Creating an Encoder Timer") 
        ##Attribute corresponding to the designated motor
        self.encoderNumber = encoderNumber
        if self.encoderNumber == 1:
            ##object corresponding to Timer 4 on port B
            self.time4 = pyb.Timer(4, prescaler = 0, period = 65535)      
            pinB6 = pyb.Pin(pyb.Pin.board.PB6, pyb.Pin.OUT_PP)
            #pinB7 = pyb.Pin(pyb.Pin.board.PB7, pyb.Pin.OUT_PP)        
            ##channel 1 on Timer 4. Corresponds to pin PB6 on CPU
            self.time4.channel(1, pyb.Timer.ENC_AB, pin=pinB6)       
            ##channel 2 on Timer 4. Corresponds to pin PB7 on CPU
            #self.time4.channel(2, pyb.Timer.ENC_B, pin=pinB7)        

        if self.encoderNumber == 2:   
            ##object corresponding to Timer 8 on port C
            self.time8 = pyb.Timer(8, prescaler = 0, period = 65535)      
            pinC6 = pyb.Pin(pyb.Pin.board.PC6, pyb.Pin.OUT_PP)
            #pinC7 = pyb.Pin(pyb.Pin.board.PC7, pyb.Pin.OUT_PP)        
            ##channel 1 on Timer 8. Corresponds to pin PC6 on CPU
            self.time8.channel(1, pyb.Timer.ENC_AB, pin=pinC6)       
            ##channel 2 on Timer 8. Corresponds to pin PC7 on CPU
            #self.time8.channel(2, pyb.Timer.ENC_AB, pin=pinC7)        
        ##encoder reading saved from last time self.read() function was called
        self.lastVal = 0        
        ##integer holding cumulative position of motor, after over/underflow correction
        self.totPosition = 0
        ##counter that stores the most updated encoder reading
        self.EncoderCounter = 0
        '''Because we only have 1 encoder channel, we can have to use interrupts to increment the motor position. But because we use interrupts, we can't use the timer.counter() method. Instead, we can use the current EncoderCounter (Offset) value as an argument in the read() method and replace timer.counter() with self.EncoderCounter.'''
    def read(self, Offset=None):
        '''This method reads the encoder of the motor to determine
        the overall position. The motor spinning in the CCW direction adds
        to the total, and spinning CW subtracts from it. The issue of our
        encoder reader overflowing at 65535 is solved by running self.read()
        at a rate of 16Hz or greater in the main file in which the
        EncoderTimer object is located'''
        #If no Offset is given, then the last EncoderCounter value is used (which means that the motor didn't move)
        #If an Offset is given, then the offset is stored as the new EncoderCounter
        if Offset != None:
            self.EncoderCounter = Offset
        newVal = self.EncoderCounter
        ans = newVal - self.lastVal
        self.lastVal = newVal      
        
        if ans >= 32767:
            ans -= 65536
        elif ans <= -32768:
            ans += 65536   
        self.totPosition += ans
        #I'm not sure if we have to worry about overflow with our new interrupt method, but our encoder has only ~40 ticks per rotation, so it would take more than 10,000 rotations to cause overflow
        return self.totPosition
    
    def zero(self):
        '''This method zeros all '''
        self.EncoderCounter = 0
        self.totPosition = 0
        self.lastVal = 0
        #Call this method as: Encoder(1/2)Counter.put(self.zero())
        return 0
if __name__ == '__main__':
    print("encoder_timer.py is Main")