# this demo toggle's a green_led once every 10 seconds and a red_led once every 61 seconds.
from machine import Pin
from time import localtime, mktime
from machine import Timer
from Handy_DS3231 import Handy_DS3231 as DS3231
i2c=machine.I2C(0,sda=Pin(20), scl=Pin(21))
myrtc=DS3231(i2c)

alarm_pin = Pin(3,Pin.IN,Pin.PULL_UP)
green_led = Pin(14, Pin.OUT)
red_led = Pin(15, Pin.OUT)

def alarmhandler(alarm_pin):
    global green_led
    global red_led
    global myrtc
    
    if myrtc.alarm1triggered:
        d=myrtc.convert_tuple(myrtc.datetime())
        q=localtime(mktime(d)+10) #calculate a time 10 seconds in future.
        _, _, d, hr, mn, sc, _, _ =q #retrieve day, hour, minutes, seconds from the calculated time q
        myrtc.setalarm1((d, False, hr, mn, sc))
        green_led.toggle()
        
    if myrtc.alarm2triggered:
        d=myrtc.convert_tuple(myrtc.datetime())
        q=localtime(mktime(d)+61) #calculate a time 61 seconds in future.
        _, _, d, hr, mn, _, _, _ =q #retrieve day, hour, minutes from the calculated time q
        myrtc.setalarm2((d, False, hr, mn))
        red_led.toggle()
    return

alarm_pin.irq(trigger=Pin.IRQ_FALLING, handler=alarmhandler)

# set rtc time to Thursday April 13 midnight.
myrtc.datetime((2023, 4, 13, 3, 0, 0, 0, 0))

# set alarm1 2 seconds past midnight.
# the tuple for the setalarm1 consists of:
# (day, True / False*, hours, minutes, seconds)
# *The boolean value controls whether the passed through day, is a weekday or a monthday
myrtc.setalarm1((3, True, 0, 0, 2))

# set alarm2 1 minute past midnight
# note that alarm2 has no seconds register
myrtc.setalarm2((3, True, 0, 1))

