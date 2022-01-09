import ssd1306
import machine
import math

i2c = machine.I2C(scl=machine.Pin(4), sda=machine.Pin(5))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

lastUpdate = -1

def update(dt):
    global lastUpdate
    if lastUpdate != dt.sec:
        lastUpdate = dt.sec
        oled.fill(0)  # set background to black
        oled.text('{}-{:02d}-{} ({})'.format(dt.day, dt.mon, dt.year, dt.dow), 0, 0)
        oled.text('{}-{:02d}-{} ({})'.format(dt.day, dt.mon, dt.year, dt.dow), 0, 11)
        oled.text('{:02d}:{:02d}:{:02d}'.format(dt.hour, dt.min, dt.sec), 0, 30)
        oled.text('{:02d}:{:02d}:{:02d}'.format(dt.hour, dt.min, dt.sec), 0, 41)
        #oled.line(31, 31, 50, 25, 1)
        oled.show() 