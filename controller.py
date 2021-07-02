import encoder_timer
import utime

'''@file controller.py'''

class Controller:
    """This class implements a motor controller for the ME 405 board.
    This class uses an EncoderTimer object to read encoder values
    and update the controller as needed to reach the setPoint value"""
    
    def __init__(self, controllerNumber=1, setPoint=30000, controlGain=0.02):
        ## corresponds to controller number
        self.controllerNumber = controllerNumber
        if controllerNumber != 1 and controllerNumber != 2:
            print('ME 405 Board can only support 2 encoders. \
                  Please select a valid controller number.')
        elif controllerNumber == 1:
             ## an EncoderTimer Object for reading motor information
            self.encoder1 = encoder_timer.EncoderTimer(1)
            # restores the total encoder position to zero
            self.EncoderCounter = self.encoder1.zero()
        elif controllerNumber == 2:
             ## an EncoderTimer Object for reading motor information
            self.encoder2 = encoder_timer.EncoderTimer(2)
            # restores the total encoder position to zero
            self.EncoderCounter = self.encoder2.zero()
        else:
            pass
        ## corresponds to controller gain for proportional controller
        self.kp = controlGain
        ## corresponds to total desired change in encoder value
        self.setPoint = setPoint
       
        ## corresponds to the list of data values in a step response
        self.dataList = []
        ## corresponds to the list of time values in a step response
        self.timeList = []

    def controller_update(self,EncoderUpdate=None,DataLimit=100,Overwrite=0):
        """Overwrite determines if new data over the DataLimit should be saved,
        DataLimit decides how many Data and Time points to save,
        and EncoderUpdate stores the new value of EncoderCounter. """
        if EncoderUpdate != None:
            self.EncoderCounter = EncoderUpdate
        if self.controllerNumber == 1:
            # reads the current encoder value
            encoderVal = self.encoder1.read(self.EncoderCounter)
        if self.controllerNumber == 2:
            # reads the current encoder value
            encoderVal = self.encoder2.read(self.EncoderCounter)        
        # calculates the error from the setpoint and encoder
        error = self.setPoint - encoderVal
        actVal = self.kp * error
        #saturates the actuation value at -100 and 100
        if actVal > 100:
            actVal = 100
        if actVal < -100:
            actVal = -100
        if self.controllerNumber == 1:
            #adds the most recent data value to the dataList
            if len(self.dataList) < DataLimit:
                #append the dataList with the most recent data
                self.dataList.append(self.encoder1.read(self.EncoderCounter))
            elif Overwrite == 1:
                #shift the entire list over by 1 data point
                self.dataList[: -1] = self.datalist[1 :]
                #add the newest data point to the list
                self.dataList[-1] = self.encoder1.read(self.EncoderCounter)
            #adds the most recent time value to timeList
        if self.controllerNumber == 2:
            #adds the most recent data value to the dataList
            if len(self.dataList) < DataLimit:
                #append the dataList with the most recent data
                self.dataList.append(self.encoder2.read(self.EncoderCounter))
            elif Overwrite == 1:
                #shift the entire list over by 1 data point
                self.dataList[: -1] = self.datalist[1 :]
                #add the newest data point to the list
                self.dataList[-1] = self.encoder2.read(self.EncoderCounter)
            #adds the most recent time value to timeList
        if len(self.timeList) < DataLimit:
            if len(self.timeList) == 0:
                ## corresponds to an initial time
                self.initTime = utime.ticks_ms()
                self.timeList.append(0)
            else:
                self.timeList.append(utime.ticks_diff(utime.ticks_ms(), self.initTime))       
        elif Overwrite == 1:
            #shift the entire list over by 1 time point
            self.timeList[: -1] = self.timelist[1 :]
            #add the newest time point to the list
            self.timeList[-1] = utime.ticks_diff(utime.ticks_ms(), self.initTime)
        return actVal
             
    def set_setPoint(self, setPoint):
        self.setPoint = setPoint
        
    def set_controlGain(self, controlGain):
        self.kp = controlGain
    
    def get_lists(self,size=1):
        """Size is the number of most recent data points to return"""
        #conjoin time value and data value into tuples representing individual data points
        lines = [str(x) + ', ' + str(y) for x,y in zip(self.timeList[-size :],self.dataList[-size :])]
        nextLine = '\n'
        lines = nextLine.join(lines)        
        return(lines)
        
if __name__ == '__main__':
    print("MAIN")        