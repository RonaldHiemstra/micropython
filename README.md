# micropython

Support tools and libraries for my micropython projects

## Magic Clock

Show distance to work on the clock (only if I am at home)

```yaml
data_template:
  payload: "{{ states(sensor.ronald2work) }}"
  topic: distance/ronald/work
service: mqtt.publish
```

Not sure yet if this code work

```yaml
- id: '1558647997872'
  alias: send travel time to work to MQTT server
  trigger:
  - entity_id: sensor.ronald2work
    platform: state
  condition: []
  action:
  - data:
      payload_template: '{% if is_state(''person.ronald_hiemstra'', ''home'') and
        now().isoweekday() <= 5 and now().hour >= 6 and now().hour < 9 %} {{ states.sensor.ronald2work.state }} {%else%} 0 {%endif%}'
      topic: distance/ronald/work
    service: mqtt.publish
```