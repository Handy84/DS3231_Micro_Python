#This demo uses a timer intterupt to poll the alarmflagbits
#to determine or a alarm1 and/or alarm2 has ocurred.
#the Pico led is toggled each time the timer interrupt-handler is called.
# Used pins: i2c SDA Pin(20)  i2c SCL Pin(21) and the Pico led Pin(25)
from Handy_DS3231 import Handy_DS3231 as DS3231
from time import localtime, mktime
from machine import Pin, Timer
# prepare rtc /i2c object
i2c=machine.I2C(0,sda=Pin(20), scl=Pin(21), freq=400000)
myrtc=DS3231(i2c)
pico_led = Pin(25, Pin.OUT)
# prepare timer object
tim = Timer()
# need two boolean vars
aflag1 : bool = False
aflag2 : bool = False

def tick(tim): # handler timer tim interrupt
    global aflag1
    global aflag2
    global myrtc
    global pico_led
    pico_led.toggle()
    aflag1 = myrtc.alarm1triggered
    aflag2 = myrtc.alarm2triggered

# set rtc time to Thursday April 13 midnight.
myrtc.datetime((2023, 4, 13, 3, 0, 0, 0, 0))
# myrtc.datetime()
# set alarm1 3 seconds past midnight.
# the tuple for the setalarm1 consists of:
# (day, True / False*, hours, minutes, seconds)
# *The boolean value controls whether the passed through day, is a weekday or a monthday
myrtc.setalarm1((3, True, 0, 0, 3))

# set alarm2 1 minute past midnight
# note that alarm2 has no seconds register
myrtc.setalarm2((3, True, 0, 1))

tim.init(freq=4, mode=Timer.PERIODIC, callback=tick)

while True:
    if aflag1:
        aflag1=False
        current_time=myrtc.datetime() #1st read the registers from the RTC !
        print(f"Alarm1 triggered !  {myrtc.hour:02d}:{myrtc.minute:02d}:{myrtc.second:02d}")
        p=myrtc.convert_tuple(current_time) #convert current time, so we can use mktime
        q=localtime(mktime(p)+10) #calculate a time 10 seconds in future.
        _, _, d, hr, mn, sc, _, _ =q #retrieve day, hour, minutes, seconds from the calculated time q
        myrtc.setalarm1((d, False, hr, mn, sc))
    
    if aflag2:
        aflag2=False
        current_time=myrtc.datetime() #1st read the registers from the RTC !
        print(f"Alarm2 triggered !  {myrtc.hour:02d}:{myrtc.minute:02d}:{myrtc.second:02d}")
        p=myrtc.convert_tuple(current_time)
        q=localtime(mktime(p)+61) #calculate a time 61 seconds in future.
        _, _, d, hr, mn, _, _, _ =q #retrieve day, hour, minutes from the calculated time q
        myrtc.setalarm2((d, False, hr, mn))