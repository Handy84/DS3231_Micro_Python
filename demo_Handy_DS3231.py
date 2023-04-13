from machine import Pin, RTC
from Handy_DS3231 import Handy_DS3231 as DS3231

i2c=machine.I2C(0,sda=Pin(20), scl=Pin(21), freq=400000)
myrtc=DS3231(i2c)
onboardrtc=RTC()
# sync external RTC with PICO RTC :
# myrtc.datetime(onboardrtc.datetime())
print(f"Today is {myrtc.weekday} the {myrtc.day}. of {myrtc.monthname} {myrtc.year}.")
print(f"time        : {myrtc.hour}:{myrtc.minute}:{myrtc.second}")
print(f"temperature : {myrtc.temp} C")

