""" @file main.py
    This file contains a demonstration program that runs some tasks, an
    inter-task shared variable, and some queues. 

    @author JR Ridgely

    @copyright (c) 2015-2020 by JR Ridgely and released under the Lesser GNU
        Public License, Version 3. 
"""

import pyb
from micropython import const, alloc_emergency_exception_buf
import gc

import cotask
import task_share
#import print_task
import controller
import motor
import utime

# Allocate memory so that exceptions raised in interrupt service routines can
# generate useful diagnostic printouts
alloc_emergency_exception_buf (100)

'''##object corresponding to Timer 1
time1 = pyb.Timer(1, prescaler = 79, period = 65535)      
#prescaler=79 means every timer overflow happens every period * (1 micro-sec)
#period=65535 means the timer overflows at 65535
pinA8 = pyb.Pin(pyb.Pin.board.PA8, pyb.Pin.IN)
time1.channel(1, pyb.Timer.IC, pin=pinA8, callback=Interrupt, polarity=pyb.Timer.BOTH)
'''

# Set any and all interrupts here:
def irInterrupt(time1):
    if not InterruptQueue.full():
        InterruptQueue.put(time1.counter(), in_ISR=True)
def Encoder1Interrupt(time4):
    #duty_cycle1 = DutyCycle1.get(in_ISR=True)
    if DutyCycle1.get(in_ISR=True) > 0:   
        Encoder1Counter.put(int(Encoder1Counter.get(in_ISR=True)) + 1, in_ISR=True)
    else:
        Encoder1Counter.put(int(Encoder1Counter.get(in_ISR=True)) - 1, in_ISR=True)
def Encoder2Interrupt(time8):
    #duty_cycle2 = DutyCycle2.get(in_ISR=True)
    if DutyCycle2.get(in_ISR=True) > 0:
        Encoder2Counter.put(int(Encoder2Counter.get(in_ISR=True)) + 1, in_ISR=True)
    else:
        Encoder2Counter.put(int(Encoder2Counter.get(in_ISR=True)) - 1, in_ISR=True)

# Declare some constants to make state machine code a little more readable.
# This is optional; some programmers prefer to use numbers to identify tasks
DataLimit = const (100)
MaxSpeed = const (35)

def IR_command_sensor():
    #Empty the Queue
    InterruptQueue._wr_idx = 0
    InterruptQueue._rd_idx = 0
    InterruptQueue._num_items = 0
    # DataPacket is the full list of Timer 1 counts.
    DataPacket = []
    # TimeDiffs is the list of differences in time from DataPacket 
    TimeDiffs = []
    # LogicList is the list of binary data converted from TimeDiffs
    LogicList = []
    # RepeatFlag is the flag that tells if a repeat code has been recieved
    RepeatFlag = False
    # Found is the flag that tells if a full complete Data Packet is found
    Found = False
    # ShutDown is the flag that tells the motors to stop working
    # We are starting the bot in the shutdown position
    ShutDownFlag.put(True)
    while True:
        #print('IR')
        '''Test if the Queue has been filled'''
        if InterruptQueue._num_items >= 68 or InterruptQueue.full():
            while not InterruptQueue.empty(): 
                if InterruptQueue._num_items == 1:
                    #If queue has only 1 term left, just store the Time Difference
                    DataPacket[-1] += InterruptQueue.get()
                    #The queue should now be empty
                else: 
                    #Store a term from the queue
                    DataPacket.append(-InterruptQueue.get())
                    #If there are atleast 2 terms already:
                    if len(DataPacket) > 1:
                        #Calculate the Time Difference between terms
                        DataPacket[-2] -= DataPacket[-1]
                        while DataPacket[-2] < 0:
                            #Correct for overflow
                            DataPacket[-2] += 65535
                if len(DataPacket) > 1 and DataPacket[-1] > 1850 and DataPacket[-1] < 3000 and DataPacket[-2] > 8000 and DataPacket[-2] < 10000 and RepeatFlag == False:
                    #If a repeat code is read:
                    DataPacket = DataPacket[:-2] #Ignore the last 2 Time Differences
                    RepeatFlag = True #Repeat code recognized
                    #print_task.put('Repeat Code Found\n')
            #Turn interrupts off while processing data
            irq_state = pyb.disable_irq ()
            #Found is the flag that indicates that an entire valid data packet is found
            TimeDiffs = DataPacket
            for i in range(len(TimeDiffs)):
                #For every time difference:
                if TimeDiffs[i] >= 3800 and TimeDiffs[i] <= 5200:
                    #If an initial pulse is found:
                    try:
                        TimeDiffs[i+64] #Test if enough data exists
                        Found = True #Raise the valid data packet flag
                        TimeDiffs = TimeDiffs[i+1:i+65] #Ignore everything except the current data packet
                        #0->64 represents data package
                        #65->66 represents trailing pulse and wait time
                        break
                    except:
                        for x in DataPacket:
                            #Put the data packet back into the queue
                            InterruptQueue.put(x)
            if Found:
                #ignore down edges for reading binary
                TimeDiffs = [TimeDiffs[x] for x in range(len(TimeDiffs)) if x%2]
                #print(TimeDiffs)
                for time in TimeDiffs:
                    if time > 450 and time < 700:
                        LogicList.append(0)
                    elif time > 1500 and time < 1800:
                        LogicList.append(1)
                    else:
                        LogicList.append('ERROR')
                if not 'ERROR' in LogicList:
                    #RAW = (''.join(map(str,LogicList)))
                    #ADDR = (''.join(map(str,LogicList[0:8])))
                    #nADDR = (''.join(map(str,LogicList[8:16])))
                    CMD = int(''.join(map(str,LogicList[16:24])), 2)
                    nCMD = int(''.join(map(str,LogicList[24:32])), 2)
                    #If the start signal is recieved:
                    if (CMD^nCMD) == 255 and CMD == 48:
                        ShutDownFlag.put(False)
                        print(CMD)
                    elif (CMD^nCMD) == 255 and CMD != 48:
                        ShutDownFlag.put(True)
                        print(CMD)
                    else:
                        pass
                else:
                    pass
            #Clear all flags and lists    
            Found = False        
            DataPacket = []         
            TimeDiffs = []
            LogicList = []
            RepeatFlag = False
            #ShutDownFlag.put(False)
            #Empty the Queue
            InterruptQueue._wr_idx = 0
            InterruptQueue._rd_idx = 0
            InterruptQueue._num_items = 0
            #Turn interrupts back on
            irq_state = pyb.enable_irq (irq_state)
            InterruptQueue.get()
        yield(0)
"""def Test1():       
    while True:
        if ShutDownFlag.get():
            print_task.put('\nA' + str(Encoder1Counter.get()))
            yield(0)
        else:
            print_task.put('\nA STOPPED')
            yield(0)
def Test2():      
    while True:
        if ShutDownFlag.get():
            print_task.put('\nB' + str(Encoder2Counter.get()))
            yield(0)
        else:
            print_task.put('\nB STOPPED')
            yield(0)"""
def Turning():
    '''#@brief   Runs a closed loop motor controller from @controller.py'''
    while True:
        print(Encoder1Counter.get())
        #If the bot isn't shutdown, and the Strategy says to turn some angle:
        if not ShutDownFlag.get():
            #Change the setpoint on both controllers to turn in place
            LeftController.set_setPoint(TurnAngle.get()/9)
            RightController.set_setPoint(-TurnAngle.get()/9)
            #Grab the next duty_cycles for the motors
            duty_cycle1 = LeftController.controller_update(Encoder1Counter.get(),DataLimit)
            duty_cycle2 = RightController.controller_update(Encoder1Counter.get(),DataLimit)
            #Store the duty_cycles in a share
            DutyCycle1.put(duty_cycle1)
            DutyCycle2.put(duty_cycle2)
            #Set the motors at their new duty_cycles
            Left.set_duty_cycle(duty_cycle1)
            Right.set_duty_cycle(duty_cycle2)
            #print('we out here')
        yield(0)
        
def MotorShutDown():
    #Motors start in off position
    #Left = motor.MotorDriver(1)
    #Right = motor.MotorDriver(2)
    #print('now we really outta here')
    while True:
        #print('M')
        #If the ShutDownFlag is True:
        if ShutDownFlag.get():
            #turn off the motors
            Left.set_duty_cycle(0)
            Right.set_duty_cycle(0)
        yield(0)
def EdgeSensor1():
    '''This just reads the edge sensor and raises a flag if it senses the edge'''
    #The Side Edge sensor uses pin A5, aka PC0
    pinB0 = pyb.Pin(pyb.Pin.board.PB0, pyb.Pin.IN)
    EdgeSensor1Flag.put(False)
    while True:
        if not ShutDownFlag.get() and not PB0.value():
            #print(PB0.value())
            EdgeSensor1Flag.put(True)
        yield(0)
"""def EdgeSensor2():
   '''This just reads the edge sensor and raises a flag if it senses the edge'''
    #The Side Edge sensor uses pin A5, aka PC0
    #pinB0 = pyb.Pin(pyb.Pin.board.PB0, pyb.Pin.IN)
    EdgeSensor2Flag.put(False)
    while True:
        if not ShutDownFlag.get() and not PB0.value():
            #print(PB0.value())
            EdgeSensor2Flag.put(True)  
        yield(0)"""
def OpticalSensor1():
    '''This just reads the optical sensor and stores the distance it finds.'''
    #pinB0 = pyb.Pin(pyb.Pin.board.PB0, pyb.Pin.IN)
    Range1 = pyb.ADC(pinB0)
    #From Excel: Distance[in] =~ (-3.2)*Voltage[V] + 12.4
    #From ADC: Voltage[V] = (Reading/4095)*5[V]
    while True:
        #If the bot isn't shut down:
        if not ShutDownFlag.get():
            #Read the optical sensor,
            Distance1 = (-3.2)*(5*Range1.read()/4095) + 12.4
            SensorRange1.put(Distance1)
        yield(0)
"""def OpticalSensor2():
    '''This just reads the optical sensor and stores the distance it finds.'''
    #pinB0 = pyb.Pin(pyb.Pin.board.PB0, pyb.Pin.IN)
    Range2 = pyb.ADC(pinB0)
    #From Excel: Distance[in] =~ (-3.2)*Voltage[V] + 12.4
    #From ADC: Voltage[V] = (Reading/4095)*5[V]
    while True:
        #If the bot isn't shut down:
        if not ShutDownFlag.get():
            #Read the optical sensor,
            Distance2 = (-3.2)*(5*Range2.read()/4095) + 12.4
            SensorRange2.put(Distance1)
        yield(0)"""
def Strategy():
    '''AKA MasterMind
    All Thinking should probably happen here'''
    #First, turn the bot 90 deg and drive towards the edge of the ring
    TurnAngle.put(90)
    #For the next 2-1/2 minutes, run around the edge of the ring
    #Next, rotate 90 deg and drive to the center of the ring

def Garbage_Day():
    '''This just clears out memory every so often, no big deal'''
    counter = 0
    while True:    
        #print('GD')
        # Periodically check and/or clean up memory
        counter += 1
        if counter >= 100:
            counter = 0
            gc.collect ()
        yield(0)
# =============================================================================

if __name__ == "__main__":

    print ('\033[2JTesting scheduler in cotask.py\n')
    time1 = pyb.Timer(1, prescaler=79, period = 65535)      
    pinA8 = pyb.Pin(pyb.Pin.board.PA8, pyb.Pin.IN)       
    time1.channel(1, pyb.Timer.IC, pin=pinA8, polarity=pyb.Timer.BOTH, callback=irInterrupt)
    #irq_state = pyb.enable_irq ()
    
    time4 = pyb.Timer(4, prescaler = 79, period = 65535)      
    pinB7 = pyb.Pin(pyb.Pin.board.PB7, pyb.Pin.IN)
    time4.channel(2, pyb.Timer.IC, pin=pinB7, polarity=pyb.Timer.BOTH, callback=Encoder1Interrupt)       

    time8 = pyb.Timer(8, prescaler = 79, period = 65535)      
    pinC7 = pyb.Pin(pyb.Pin.board.PC7, pyb.Pin.IN)
    time8.channel(2, pyb.Timer.IC, pin=pinC7, polarity=pyb.Timer.BOTH, callback=Encoder2Interrupt)

    Left = motor.MotorDriver(1)
    Right = motor.MotorDriver(2)
    LeftController = controller.Controller(1)   
    RightController = controller.Controller(2)

    """Tasks"""
    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
    turning = cotask.Task (Turning, name = 'Turn', priority = 1, 
                         period = 200, profile = True, trace = False)
    garbage_collection = cotask.Task (Garbage_Day, name = 'Trash', priority = 5, 
                         period = 200, profile = True, trace = False)  
    ir_command = cotask.Task (IR_command_sensor, name = 'IR_command', priority = 1, 
                         period = 50, profile = True, trace = False)
    shutdown = cotask.Task (MotorShutDown, name = 'Shutdown', priority = 1, 
                         period = 100, profile = True, trace = False)
    '''encoder_init = cotask.Task (EncoderInitialization, name = 'Encoder', priority = 1, 
                         period = 100, profile = True, trace = False) '''   
    mastermind = cotask.Task (Strategy, name = 'strategy', priority = 1, 
                         period = 100, profile = True, trace = False)
    edge1 = cotask.Task (EdgeSensor1, name = 'Edge1', priority = 1, 
                         period = 100, profile = True, trace = False)
    optics1 = cotask.Task (OpticalSensor1, name = 'Optics1', priority = 1, 
                         period = 100, profile = True, trace = False)
    '''edge2 = cotask.Task (EdgeSensor2, name = 'Edge2', priority = 1, 
                         period = 100, profile = True, trace = False)
    optics2 = cotask.Task (OpticalSensor2, name = 'Optics2', priority = 1, 
                         period = 100, profile = True, trace = False)'''
    """Shares"""
    #Flag that determines if the bot is in shutdown mode or not
    ShutDownFlag = task_share.Share ('h', thread_protect = True, name = "ShutDown")
    #Flag that determines if the encoders have been properly initialized or not
    EncoderInitFlag = task_share.Share ('h', thread_protect = True, name = "EncoderInit") 

    DutyCycle1 = task_share.Share ('h', thread_protect = True, name = "DC1")

    DutyCycle2 = task_share.Share ('h', thread_protect = True, name = "DC2")

    Encoder1Counter = task_share.Share ('h', thread_protect = True, name = "counter_1")
    
    Encoder2Counter = task_share.Share ('h', thread_protect = True, name = "counter_2")
    
    TurnAngle = task_share.Share ('h', thread_protect = True, name = "Angle")

    EdgeSensor1Flag = task_share.Share ('h', thread_protect = True, name = "SideEdge")
    
    EdgeSensor2Flag = task_share.Share ('h', thread_protect = True, name = "FrontEdge")

    SensorRange1 = task_share.Share ('h', thread_protect = True, name = "SideRange1")
    
    SensorRange2 = task_share.Share ('h', thread_protect = True, name = "SideRange2")
    
    """Queues"""
    InterruptQueue = task_share.Queue ('H', 200, thread_protect = False, 
                                       overwrite = False, name = "Interrupt_Queue")
    
    """Task List"""
    cotask.task_list.append (mastermind)
    cotask.task_list.append (turning)
    cotask.task_list.append (ir_command)
    cotask.task_list.append (shutdown)
    cotask.task_list.append (edge1)
    cotask.task_list.append (optics1)
    '''cotask.task_list.append (edge2)
    cotask.task_list.append (optics2)'''
    '''cotask.task_list.append (encoder_init)'''
    # A task which prints characters from a queue has automatically been
    # created in print_task.py; it is accessed by print_task.put_bytes()

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect ()

    # Run the scheduler with the chosen scheduling algorithm. Quit if any 
    # character is sent through the serial port
    vcp = pyb.USB_VCP ()
    while not vcp.any ():
        cotask.task_list.pri_sched ()

    # Empty the comm port buffer of the character(s) just pressed
    vcp.read ()

    # Print a table of task data and a table of shared information data
    print ('\n' + str (cotask.task_list) + '\n')
    print (task_share.show_all ())
    print ('\r\n')

