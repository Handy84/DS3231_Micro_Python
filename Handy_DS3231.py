
class Handy_DS3231:

    """
        Example usage: a i2c object is needed.
            # Read time
            from Handy_DS3231 import Handy_DS3231 as DS3231
            myrtc=DS3231(i2c) #after a call to datetime() you can use myrtc.hour myrtc.minute and so on.
            myrtc.datetime()  #returns a tuple with 8 values (just as the PICO RTC)
            (year, month, day, weekday, hour, minute, second, subsecond) subsecond always 0
            # Set time, just pass a tuple with above mentioned values.
            myrtc.datetime((2023, 4, 11, 1, 17, 18, 51, 0))
    """

    __i2c_object: object
    __buffer: tuple
    
    def __init__(self, i2c_object):
        self.__i2c_object = i2c_object
        self.datetime()

    @property
    def temp(self):
        temp=self.__i2c_object.readfrom_mem(0x68, 0x11, 2)
        out=temp[0]<<2
        out|=temp[1]>>6
        return out*0.25
    
    def datetime(self, parameter=None):
        if parameter!=None:
            if type(parameter)==tuple:
                if len(parameter)==8: #only when a tuple of 8 values is passed set time/date registers.
                    yr, mt, dt, wd, hr, mn, sec, _ = parameter #sub seconds not used.
                    buffer = list(self.__i2c_object.readfrom_mem(0x68, 0x00, 7))
                    # make buffer a list so we can modify the contents.
                    if yr!=None:
                        yr%=100 # limit range from year to 99
                        buffer[6]=(yr//10)<<4
                        buffer[6]|=yr%10
                    if mt!=None: # calc. month
                        buffer[5]=(mt//10)<<4
                        buffer[5]&=0x10
                        buffer[5]|=mt%10
                    if dt!=None: # calc. date
                        buffer[4]=(dt//10)<<4
                        buffer[4]&=0x30
                        buffer[4]|=dt%10
                    if wd!=None and wd<7: # calc. weekday add one !
                        buffer[3]|=wd+1
                    if hr!=None: # calc. hour
                        buffer[2]=(hr//10)<<4
                        buffer[2]&=0x30
                        buffer[2]|=hr%10
                    if mn!=None: # calc minute
                        buffer[1]=(mn//10)<<4
                        buffer[1]&=0x70
                        buffer[1]|=mn%10
                    if sec!=None: # calc second
                        buffer[0]=(sec//10)<<4
                        buffer[0]&=0x70
                        buffer[0]|=sec%10                    
                    self.__i2c_object.writeto_mem(0x68, 0x00, bytes(buffer))
        else:
            
            data=self.__i2c_object.readfrom_mem(0x68, 0x00, 7) # read 7 bytes from register 00h ... 06h
            sec=(data[0]&0x70)>>4 # calculate seconds
            sec*=10
            sec+=data[0]&0x0F
            mn=(data[1]&0x70)>>4 # calculate minutes
            mn*=10
            mn+=data[1]&0x0F
            hr=(data[2]&0x30)>>4 # calculate hours
            hr*=10
            hr+=data[2]&0x0F
            wd=(data[3]&0x07)-1  # calculate weekday returns 0...6 DS3231 uses 1...7 !
            dt=(data[4]&0x30)>>4 # calculate date
            dt*=10
            dt+=data[4]&0x0F
            mt=(data[5]>>4)&0x01 # calculate month
            mt*=10
            mt+=data[5]&0x0F
            yr=(data[6]>>4)*10   # calculate year
            yr+=data[6]&0x0F
            self.__buffer=(yr+2000,mt,dt,wd,hr,mn,sec,0)
            return self.__buffer #return a tuple same as machine.RTC.datetime()           
    
    def setalarm1(self, alarm1data, enable=True, amask1=0x08):
        controlreg=list(self.__i2c_object.readfrom_mem(0x68, 0x0E, 1)) #read controlreg
        controlreg[0]&=0xFE #disable alarm1
        self.__i2c_object.writeto_mem(0x68, 0x0E, bytes(controlreg)) #update controlreg.
        self.resetalarm1() # reset alarm1flag otherwise the interupt pin will fire immediately.
        if type(alarm1data)!=tuple:
            return #invalid parameter! leave...
        
        else:
            if len(alarm1data)==5:
                dy, wd, hr, mn, sec = alarm1data
                buffer = list(self.__i2c_object.readfrom_mem(0x68, 0x07, 4))
                buffer[0]=(sec//10)<<4 #handle seconds
                buffer[0]&=0x70 # limit range !
                buffer[0]|=sec%10
                maskbit = amask1 & 0x1 #put mask bit in place.
                buffer[0]|=maskbit<<7
                buffer[1]=(mn//10)<<4 #handle minutes
                buffer[1]&=0x70 # limit range !
                buffer[1]|=mn%10
                maskbit = (amask1>>1) & 0x1
                buffer[1]|=maskbit<<7               
                buffer[2]=(hr//10)<<4 # handle hours
                buffer[2]&=0x30
                buffer[2]|=hr%10
                maskbit = (amask1>>2) & 0x1
                buffer[2]|=maskbit<<7
                buffer[3]=(dy//10)<<4
                buffer[3]&=0x30
                buffer[3]|=dy%10
                maskbit=wd&0x01 # get wd /dt bit passed on in this function. 
                buffer[3]|=maskbit<<6 # put wd /dt bit in place.
                maskbit = (amask1>>3) & 0x01 #get last mask bit
                buffer[3]|=maskbit<<7 # and put in place.
                self.__i2c_object.writeto_mem(0x68, 0x7, bytes(buffer))
                controlreg=list(self.__i2c_object.readfrom_mem(0x68, 0x0E, 1)) #read controlreg
                controlreg[0]|=enable&0x01 #enable alarm1 to trigger a interupt
                controlreg[0]|=0x04 # make sure the interrupt control bit is set!
                self.__i2c_object.writeto_mem(0x68, 0x0E, bytes(controlreg)) #update controlreg.
        return

    def setalarm2(self, alarm2data, enable=True, amask2=0x04):
        controlreg=list(self.__i2c_object.readfrom_mem(0x68, 0x0E, 1)) #read controlreg
        controlreg[0]&=0xFD #disable alarm1
        self.__i2c_object.writeto_mem(0x68, 0x0E, bytes(controlreg)) #update controlreg.
        self.resetalarm2()
        if type(alarm2data)!=tuple:
            return #invalid parameter! leave...
        
        else:
            if len(alarm2data)==4:
                dy, wd, hr, mn = alarm2data
                buffer = list(self.__i2c_object.readfrom_mem(0x68, 0x0B, 3))
                buffer[0]=(mn//10)<<4 #handle minutes alarm2 has no seconds !
                buffer[0]&=0x70 # limit range !
                buffer[0]|=mn%10
                maskbit = amask2 & 0x1 # get maskbit
                buffer[0]|=maskbit<<7
                buffer[1]=(hr//10)<<4 #handel hours
                buffer[1]&=0x30 # limit range !
                buffer[1]|=hr%10
                maskbit = (amask2>>1) & 0x1
                buffer[1]|=maskbit<<7               
                buffer[2]=(dy//10)<<4 #handle days or weekdays
                buffer[2]&=0x30
                buffer[2]|=dy%10
                maskbit = wd&0x01 # get the wd /dt bit. this bit decides if alarm triggers on weekday or date.
                buffer[2]|=maskbit<<6
                maskbit = (amask2>>2) & 0x1
                buffer[2]|=maskbit<<7
                self.__i2c_object.writeto_mem(0x68, 0x0B, bytes(buffer))
                controlreg=list(self.__i2c_object.readfrom_mem(0x68, 0x0E, 1)) #read controlreg
                controlreg[0]|=(enable&0x01)<<1 #enable alarm2 to trigger a interupt
                controlreg[0]|=0x04 # make sure the interrupt control bit is set!
                self.__i2c_object.writeto_mem(0x68, 0x0E, bytes(controlreg)) #update controlreg.
        return
    
    @property
    def isweekday(self):
        return self.__buffer[3] not in (5, 6)
    
    @property
    def weekday(self):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saterday", "Sunday"]
        return days[self.__buffer[3]]
    
    @property
    def second(self):
        return self.__buffer[6]
    
    @property
    def minute(self):
        return self.__buffer[5]
    
    @property
    def hour(self):
        return self.__buffer[4]
    
    @property
    def year(self):
        return self.__buffer[0]
    
    @property
    def month(self):
        return self.__buffer[1]
    
    @property
    def monthname(self):
        mnts=["January","February","March","April","May","June","July","August","September","October","November","December"]
        return mnts[self.__buffer[1]-1]
    
    @property
    def day(self):
        return self.__buffer[2]
    
    @property
    def alarm1triggered(self):
        statusreg=self.__i2c_object.readfrom_mem(0x68, 0x0F, 1) #read statusreg
        return statusreg[0]&0x01==1
        
    def resetalarm1(self):
        statusreg=list(self.__i2c_object.readfrom_mem(0x68, 0x0F, 1)) #read statusreg
        statusreg[0]&=0xFE
        self.__i2c_object.writeto_mem(0x68, 0x0F, bytes(statusreg)) #update statusreg
        return

    @property
    def alarm2triggered(self):
        statusreg=self.__i2c_object.readfrom_mem(0x68, 0x0F, 1) #read statusreg
        return statusreg[0]&0x02==2
        
    def resetalarm2(self):
        statusreg=list(self.__i2c_object.readfrom_mem(0x68, 0x0F, 1)) #read statusreg
        statusreg[0]&=0xFD
        self.__i2c_object.writeto_mem(0x68, 0x0F, bytes(statusreg)) #update statusreg
        return

    @staticmethod
    def convert_tuple(datain):
        bfl=list(datain)
        bfl.pop(7)
        bfl.pop(3)
        bfl.append(datain[3])
        bfl.append(0)
        bfl.append(0)
        return tuple(bfl)
        
        