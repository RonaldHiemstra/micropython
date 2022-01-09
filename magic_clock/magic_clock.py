from machine import Pin
from neopixel import NeoPixel
import random

NR_OF_LEDS = 60
GPIO_PIN = 15

RED = 1
GREEN = 0
BLUE = 2

class _Timer():
  def __init__(self, start, end, color, value, max_value, width, blink):
    self.start = start
    self.end = end
    self.color = color
    self.value = value
    self.max_value = max_value
    self.width = width
    self.blink = blink
    print('start =', self.start, ', end =', self.end, ', max_value =', max_value)

class MagicClock():
  def __init__(self, now, gpio_pin=GPIO_PIN, nr_of_leds=NR_OF_LEDS, intensity=0.25,
               reverse=False, zeroIndex=0):
    self.np = NeoPixel(Pin(gpio_pin), nr_of_leds)
    self.nr_of_leds = nr_of_leds
    self.set_intensity(intensity)
    self.reverse=reverse
    self.zeroIndex = zeroIndex % self.nr_of_leds
    self.blinkIntensity = 0.5
    self._last_update = now
    self.timers = dict()

  def set(self, color, value, max_value, width, blink=False):
    if value > max_value:
      self.set([int(primary * 0.5) for primary in color], value - (max_value * 1.1), max_value, width, blink)
    value = value % max_value
    width = max(width, 1 / self.nr_of_leds) # minimum width of at least 1 pixel
    width *= self.nr_of_leds  # width in pixels
    halfwidth = width / 2  # half width in pixels
    pixel = value * self.nr_of_leds / max_value
    if self.reverse:
      pixel = self.nr_of_leds - pixel
    pixel += self.zeroIndex

    for curpix in range(int(0.5 + pixel - halfwidth), 1 + int(0.5 + pixel + halfwidth)):
      intensity = (width - abs(curpix - pixel)) / width
      curpix = curpix % self.nr_of_leds
      if intensity >= 1:
        intensity = 1
      i_color = [int(primary * intensity) for primary in color]

      if blink:
        i_color = [int(primary * self.blinkIntensity) for primary in i_color]
      self.np[curpix] = tuple([min(primary[0] + primary[1], 255) for primary in zip(self.np[curpix],
                              i_color)])

  def countdown(self, id, color, value, max_value, width, blink=False, timeout=5):
    value = int(value)
    print('timeout =', timeout, ', value =', value, ', max_value =', max_value)
    self.timers[id] = _Timer(start=self._last_update.get_time(),
                             end=self._last_update.get_time() + min(timeout, int(value * max_value / 60)),
                             color=color, value=value, max_value=max_value, width=width, blink=blink)

  def _update_countdown(self):
    for id, timer in self.timers.items():
      if timer.end < self._last_update.get_time():
        del self.timers[id]
      else:
        self.set(timer.color, timer.value -
                 ((self._last_update.get_time() - timer.start) * 60 / timer.max_value),
                 timer.max_value, timer.width, timer.blink)

  def set_intensity(self, intensity):
    self._intensity = min(max(1, int(intensity * 255)), 255)

  def update(self, now):
    self._update_countdown()
    second = now.sec + (now.msec / 1e6)
    self.set((0, self._intensity, 0), second, 60, 1/60)
    minute = now.min + (second / 60)
    self.set((0, 0, self._intensity), minute, 60, 1/60)
    hour = (now.hour + (minute / 60)) % 12
    self.set((self._intensity, 0, 0), hour, 12, 1/18)

    intensity = self._intensity / 16
    for i in range(0, 60, 5):  # show indicators every 5 minutes
      self.set((intensity, intensity, intensity), i, 60, 1/60)
    intensity = self._intensity / 4
    for i in range(0, 60, 15):  # brighten indicators every 15 minutes
      self.set((intensity, intensity, intensity), i, 60, 1/60)

    self.np.write()
    self.blinkIntensity = abs((second % 2) - 1)  # blink @.5Hz
    self._last_update = now

    # reset all pixels for next update
    for i in range(self.nr_of_leds):
      self.np[i] = (0, 0, 0)
