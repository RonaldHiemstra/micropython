# This file is executed on every boot (including wake-boot from deepsleep)
import esp  #pylint: disable=import-error
esp.osdebug(None)

import esp32
import json
import webrepl  #pylint: disable=import-error

import gc
gc.collect()

import network  #pylint: disable=import-error


class Config():
    """Class for serializing configuration items."""
    def __init__(self, filename):
        self.filename = filename
        with open(self.filename) as fh:
            self.__config = json.load(fh)

    def get(self, key=None):
        """Get a config item."""
        if key is None:
            # return all public config items (filter out the hidden items)
            return { key: self.__config[key] for key in self.__config if not key.startswith('__') }
        return self.__config.get(key)

    def set(self, key, value):
        """Set a config item."""
        self.__config[key] = value
        with open(self.filename, 'w') as fh:
            fh.write(json.dumps(self.__config))

system_config = Config('system_config.json')  # system configuration


station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(system_config.get('ssid'), system_config.get('__password'))
while station.isconnected() == False:
    pass
print('Connection successful')
print(station.ifconfig())


webrepl.start()


def GetRawTemperature(in_fahrenheit=False):
    temperature = esp32.raw_temperature()
    if in_fahrenheit:
        return temperature
    return (temperature - 32.0) / 1.8
