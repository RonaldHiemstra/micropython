import uasyncio as asyncio
import json
import machine
import ubinascii
from mqtt_as import MQTTClient

UNIQUE_DEVICE_ID = ubinascii.hexlify(machine.unique_id()).decode('utf-8')


class _Sensor:
    """A sensor can have multiple values (eg. temperature & humidity).
    Each measurement will be exposed by a _SensorClass instance.
    """

    def __init__(self, device_id: str, name: str, sensor_class: str, unit: str) -> None:
        self.device_id = device_id
        self._state_topic = f"sensor/{self.device_id}/state"

        self.name = name
        self.sensor_id = f'{device_id}_{self.name.lower().replace(" ", "_")}'
        self.sensor_class = sensor_class
        self.unit = unit
        self.config_payload = json.dumps({"name": self.name,
                                          "device_class": self.sensor_class,
                                          "state_topic": self._state_topic,
                                          "value_template": "{{ value_json.%s }}" % self.sensor_class,
                                          "unit_of_measurement": self.unit,
                                          "device": {"ids": [device_id]}
                                          })
        self.send_config()

    def send_config(self, topic: str, payload: str) -> None:
        MQTTClient.publish(f'homeassistant/sensor/{self.sensor_id}/config',
                           self.config_payload)

        self.classes: _SensorClass = list()
        self.classes.append(_SensorClass(device_id, name, sensor_class, unit))

    async def update(self, **kwargs):
        await MQTTClient.publish(self._state_topic,
                                 json.dumps(**kwargs))


class Device:
    """This device class provides functionality to communicate with a MQTT server."""

    def __init__(self, unique_device_id: str) -> None:
        """Create a MQTT device instance.

        Arguments:
            unique_device_id: ubinascii.hexlify(machine.unique_id()).decode('utf-8')
        """
        self.device_id = unique_device_id
        loop = asyncio.get_event_loop()
        loop.create_task(self._control())

    def create_sensor(self, name: str, sensor_class: str, unit: str) -> _Sensor:
        return _Sensor(self.device_id, name, sensor_class, unit)


device = Device(unique_device_id=ubinascii.hexlify(machine.unique_id()).decode('utf-8'))

if __name__ == '__main__':
    kettle_temperature = device.create_sensor('Kettle temperature', 'temperature', '°C')
    f'homeassistant/sensor/{UNIQUE_DEVICE_ID}_kettle_heater/config'
    f'homeassistant/sensor/{UNIQUE_DEVICE_ID}_fridge_temperature/config'
    f'homeassistant/sensor/{UNIQUE_DEVICE_ID}_fridge_cooler/config'
    f'homeassistant/sensor/{UNIQUE_DEVICE_ID}_fridge_heater/config'
    f'homeassistant/sensor/{UNIQUE_DEVICE_ID}_environment_temperature/config'
    f'homeassistant/sensor/{UNIQUE_DEVICE_ID}_environment_humidity/config'
    f'homeassistant/sensor/{UNIQUE_DEVICE_ID}_control_switch/config'

    kettle_temperature.update(temperature=20)
