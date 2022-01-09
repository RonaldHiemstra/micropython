# Complete project details at https://RandomNerdTutorials.com
import machine
import neopixel
import random
import time

NR_OF_LEDS = 60
GPIO_PIN = 15
MAX_BRIGHTNESS = 10 # 256

RED = 1
GREEN = 0
BLUE = 2

np = neopixel.NeoPixel(machine.Pin(GPIO_PIN), NR_OF_LEDS)


def Lights(leds, color, duration):
    for led in leds:
        np[led] = color
        np.write()

    time.sleep_ms(duration)

    for led in leds:
        np[led] = (0, 0, 0)


def loop(color, delay=100):
    for i in range(NR_OF_LEDS):
        np[i] = color
        np.write()
        if delay:
            time.sleep_ms(delay)
        np[i] = (0,0,0)
    np.write()


def Random():
    while True:
        leds = {random.randrange(0, NR_OF_LEDS) for a in range(random.randrange(1, 10))}
        Lights(leds, (random.randrange(0, MAX_BRIGHTNESS), random.randrange(0, MAX_BRIGHTNESS), random.randrange(0, MAX_BRIGHTNESS)), random.randrange(0, 1000))


def RGBLoop():
    for a in range(3):
        for b in range(0, 256, 8):
            loop((b if a==0 else 0, b if a==1 else 0, b if a==2 else 0), 0)


def FullLoop():
    while True:
        for x in range(0,256,8):
            for y in range(0,256,8):
                for z in range(0,256,8):
                    loop((x, y, z), 10)


# Random()

class MagicClock():
    def __init__(self, reverse=False, zeroIndex=0):
        self.np = np
        self.reverse=reverse
        self.zeroIndex = zeroIndex % NR_OF_LEDS
        self.blinkIntensity = 0.5

    def set(self, color, value, max_value, width, blink=False):
        value = value % max_value
        width = max(width, 1 / NR_OF_LEDS) # minimum width of at least 1 pixel
        width *= NR_OF_LEDS  # width in pixels
        halfwidth = width / 2  # half width in pixels
        pixel = value * NR_OF_LEDS / max_value
        if self.reverse:
            pixel = NR_OF_LEDS - pixel
        pixel += self.zeroIndex

        for curpix in range(int(0.5 + pixel - halfwidth), 1 + int(0.5 + pixel + halfwidth)):
            intensity = (width - abs(curpix - pixel)) / width
            curpix = curpix % NR_OF_LEDS
            if intensity >= 1:
                intensity = 1
            i_color = [int(primary * intensity) for primary in color]

            if blink:
                i_color = [int(primary * self.blinkIntensity) for primary in i_color]
            self.np[curpix] = tuple([min(primary[0] + primary[1], 255)
                                     for primary in zip(self.np[curpix], i_color)])

    def update(self, now):
        second = now.second + (now.millisecond / 1e6)
        self.set((0,255,0), second, 60, 1/60)
        minute = now.minute + (second / 60)
        self.set((0,0,255), minute, 60, 1/60)
        hour = now.hour + (minute / 60)
        self.set((255,0,0), hour, 12, 1/18)

        self.np.write()
        self.blinkIntensity = abs((second % 2) - 1)  # blink @.5Hz

        # reset all pixels for next update
        for i in range(NR_OF_LEDS):
            self.np[i] = (0, 0, 0)