import json
import machine
import ubinascii
import uasyncio as asyncio

import mqtt_as.mqtt_as as mqtt_as
from primitives.aadc import AADC

from config import Config
#from local_time import LocalTime
#from magic_clock import MagicClock
#import syslog

#log = syslog.UDPClient(ip='192.168.1.9')
#log.info('Ambient is running')

#dt = LocalTime()
#lastUpdate = dt.now()
#clock = MagicClock(now=lastUpdate, gpio_pin=12, nr_of_leds=15, reverse=True, zeroIndex=0)
#clock.set((20,12,20), 0, 3600, 1, False)
#clock.update(lastUpdate)

# Get ambient light in lumens
adc = machine.ADC(machine.Pin(36))  # create ADC object on ADC pin
adc.atten(machine.ADC.ATTN_11DB)    # set 11dB input attenuation (voltage range roughly 0.0v - 3.6v)
print(adc.read())                   # read value, 0-65535 across voltage range 0.0v - 3.6v
aadc = AADC(adc)

light_sensor_values: List[int] = list()

GRANULARITY = 2048


async def foo():
    global light_sensor_values
    while True:
        value = await aadc(GRANULARITY)  # Trigger if value changes by GRANULARITY
        # TODO: convert to lumens
        light_sensor_values.append(value // 256)  # Convert value to the range 0..255
        print(value, '==>', value // 256)
        if len(light_sensor_values) > 10:
            light_sensor_values.pop(0)  # Don't grow this list like crazy...

#asyncio.run(foo())

loop = asyncio.get_event_loop()
loop.create_task(foo())

unique_id = ubinascii.hexlify(machine.unique_id()).decode('utf-8')


network_config = Config('network_config.json')

mqtt_as.config['server'] = '192.168.1.1'  # Change to suit e.g. 'iot.eclipse.org'
mqtt_as.config['ssid'] = network_config.get('ssid')
mqtt_as.config['wifi_pw'] = network_config.get('__password')


def callback(topic, msg, retained):
    print((topic, msg, retained))


async def conn_han(client: mqtt_as.MQTTClient):
    await client.subscribe('foo_topic', 1)


async def main(client: mqtt_as.MQTTClient):
    global light_sensor_values
    await client.connect()
    await client.publish(f'homeassistant/sensor/{unique_id}/config',
                         json.dumps(dict(name="ambience illuminance",
                                         unique_id=f"ambient_{unique_id}",
                                         #value_template="{{ value_json }}",
                                         device_class="illuminance",
                                         state_topic=f"ambient/{unique_id}/state",
                                         unit_of_measurement="brightness",
                                         device=dict(name="ambient",
                                                     identifiers=[f"{unique_id}"])
                                         )),
                         retain=True)
    prev_light_sensor_value = -256.0
    while True:
        # If WiFi is down the following will pause for the duration.
        print('%s' % light_sensor_values)
        if light_sensor_values:
            light_sensor_value = sum(light_sensor_values) / len(light_sensor_values)
            if abs(prev_light_sensor_value - light_sensor_value) > 4:
                print('publish', light_sensor_value)
                await client.publish(f'ambient/{unique_id}/state', f'{light_sensor_value}')
                prev_light_sensor_value = light_sensor_value
                light_sensor_values.clear()
        await asyncio.sleep(1)

mqtt_as.config['subs_cb'] = callback
mqtt_as.config['connect_coro'] = conn_han

mqtt_as.MQTTClient.DEBUG = True  # Optional: print diagnostic messages
client = mqtt_as.MQTTClient(mqtt_as.config)
loop = asyncio.get_event_loop()
loop.create_task(main(client))
try:
    #asyncio.run(main(client))
    loop.run_forever()
finally:
    client.close()  # Prevent LmacRxBlk:1 errors

if __name__ == '__main__':
    pass
