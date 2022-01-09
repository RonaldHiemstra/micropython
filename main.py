import display
import localtime
import mqtt_client
import rgb_ledstrip
import utime    #pylint: disable=import-error


dt = localtime.localtime(1)

clock = rgb_ledstrip.MagicClock(reverse=True, zeroIndex=22)

lastUpdate = dt.now()

while True:
    mqtt_client.handle_messsages()
    distance2work = mqtt_client.states.get(b'distance/ronald/work')
    distance2home = mqtt_client.states.get(b'distance/ronald/home')
    if distance2work:
        clock.set((30,30,30), distance2work, 60, 1/60, True)
    if distance2home:
        clock.set((30,255,30), distance2home, 60, 1/60, True)
    now = dt.now()
    clock.update(now)
    display.update(now)
    utime.sleep_ms(100)
