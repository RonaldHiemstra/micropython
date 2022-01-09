# MAGIC CLOCK

The magic clock will show the time using an RGB LED strip.

The design is to control a LED strip containing 60 RGB LEDs, but it should also work with more LEDs.

The clock can show a number of information:

* clock with 3 hands: (hour: GREEN (~5 pixel), minute: BLUE (~1 pixel), second: (~1 pixel)
* Travel time to work or home (every person has its own color)

The clock is connected to WiFi and synchronized with a NTP server every night at 4 a.m.
The clock is connected with a MQTT server to retrieve the distance information.

Some information is also shown on a OLED display.

## TODO

### If connecting to the configured AP, start own AP and webpage to configure AP

Check <https://docs.micropython.org/en/latest/library/network.WLAN.html>

### Send logging data to a syslog server

Configure a syslog server to receive UDP syslog messages from external sources:
Uncomment the configuration lines containing `imudp` in `/etc/rsyslog.conf`

### solve glitches

Fix the glitches as described here: [Tips for Troubleshooting ‘NeoPixel glitches’](https://blog.adafruit.com/2016/10/28/tips-for-troubleshooting-neopixel-glitches/)

* ~~A simple solution can be found here: [Cheating At 5V WS2812 Control To Use 3.3V Data](https://hackaday.com/2017/01/20/cheating-at-5v-ws2812-control-to-use-a-3-3v-data-line/)~~
* ~~A proper solution is to use a level shifter. See [Taking It To Another Level: Making 3.3V Speak With 5V](https://hackaday.com/2016/12/05/taking-it-to-another-level-making-3-3v-and-5v-logic-communicate-with-level-shifters/)~~
* The solution I implemented is using this simple level shifter: [Single transistor level up shifter](https://electronics.stackexchange.com/questions/82104/single-transistor-level-up-shifter)

## Home Assistant configuration

I use Home Assistant to send the required data to the MQTT server. This of course can be any kind of home automation service.

### Show distance to work on the clock (only if I am at home)

```yaml
data_template:
  payload: "{{ states(sensor.ronald2work) }}"
  topic: distance/ronald/work
service: mqtt.publish
```

Not sure yet if this code work

```yaml
- id: '1558647997872'
  alias: time to work to MQTT
  trigger:
  - entity_id: sensor.ronald2work
    platform: state
  condition: []
  action:
  - data_template:
      payload: '{% if is_state(''device_tracker.life360_ronald_hiemstra'', ''home'')
        and now().isoweekday() <= 5 and now().hour >= 6 and now().hour < 9 %} {{
        states.sensor.ronald2work.state }} {%else%} 0 {%endif%}'
      topic: distance/ronald/work
    service: mqtt.publish

```
