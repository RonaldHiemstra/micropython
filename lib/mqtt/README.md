# MQTT

There seems to be (known) issues with the default MQTT implementation in micropython.

Those issues are solved by [Peter Hinch's MQTT version](https://github.com/peterhinch/micropython-mqtt).
TVE did rewrite this library which be found here <https://github.com/tve/mqboard>

I will go for Peter's version, since this seems more straight forward and is more used. [See its readme](https://github.com/peterhinch/micropython-mqtt/blob/master/mqtt_as/README.md)

TVE's version contains a complete framework around MQTT which seems very nice. Drawback is that it also requires TVE's micropython version which is lacking behind...

## public brokers

* [list of public brokers](https://github.com/mqtt/mqtt.org/wiki/public_brokers)
