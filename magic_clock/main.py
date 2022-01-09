import utime  # pylint: disable=import-error

import display
from local_time import LocalTime
import mqtt_client
from magic_clock import MagicClock
import syslog


log = syslog.UDPClient(ip='192.168.1.9')
log.info('MAGIC Clock is running')

dt = LocalTime()

lastUpdate = dt.now()
clock = MagicClock(now=lastUpdate, reverse=True, zeroIndex=22)

# list of travelers to home or work. tuple containing:
# * mqtt key
# * color
# * expected nr of seconds to travel per unit
travelers = [(b'distance/ronald/work', 'set', (30,255,30), 60),
             (b'distance/ronald/home', 'countdown', (30,255,30), 60),
             (b'distance/koen/home', 'countdown', (200,0,200), 60),
             (b'distance/miranda/home', 'countdown', (200,200,0), 180),
             (b'distance/lieke/home', 'countdown', (0,200,200), 180)]
cache = dict()

while True:
  try:
    mqtt_client.handle_messsages()

    for traveler, command, color, sec_per_unit in travelers:
      if command == 'set':
        distance = mqtt_client.states.get(traveler)
        if distance:
          clock.set(color, distance * sec_per_unit, 3600, 1/60, True)
      elif command == 'countdown':
        distance = mqtt_client.states.pop(traveler, None)
        if distance is not None and distance != cache.get(traveler, None):
          cache[traveler] = distance
          clock.countdown(traveler, color, distance * sec_per_unit, 3600, 1/60, True, sec_per_unit * 6)
      else:
        log.critical('command {} not supported!'.format(command))
    # distance = mqtt_client.states.get(b'distance/miranda/home')
    # if distance:
    #   clock.set((200,200,0), distance, 20, 1/60, True)
    # distance = mqtt_client.states.get(b'distance/lieke/home')
    # if distance:
    #   clock.set((0,200,200), distance, 20, 1/60, True)

    intensity = mqtt_client.states.pop(b'clock/intensity', None)
    if intensity is not None:
      clock.set_intensity(intensity)

    now = dt.now()
    clock.update(now)
    display.update(now)
    utime.sleep_ms(50)
  except Exception as ex:
    with open('errors.txt', 'w') as fh:
      fh.write('%s\n' % ex)
