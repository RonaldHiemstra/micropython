"""Handle the mqtt messages.

handle_messsages()
"""
import machine      #pylint: disable=import-error
import time
from umqtt.simple import MQTTClient #pylint: disable=import-error
import ubinascii    #pylint: disable=import-error
#import micropython

mqtt_server = '192.168.1.1'
client_id = ubinascii.hexlify(machine.unique_id())

topic_sub = b'#' # subscribe to all messages

expectedData = [(b'wallpanel/mywallpanel/sensor/battery', b'{"value":100,"unit":"%","charging":true,"acPlugged":true,"usbPlugged":false}'),
                (b'wallpanel/mywallpanel/state', b'{"currentUrl":"https:\\/\\/hiemstra-fam.duckdns.org\\/lovelace\\/slideshow","screenOn":true,"brightness":34}'),
                (b'driveway-lights/status', b'1'),
                (b'milight/states/0x7981/rgbw/1', b'{"state":"ON","brightness":255,"bulb_mode":"white","color":{"r":255,"g":255,"b":255}}'),
                (b'milight/states/0x7981/rgb_cct/1', None),  #b'{"state":"OFF","color":{"r":255,"g":255,"b":255}}'),
                (b'driveway-lights/relay/0', None),  #b'1'),
                (b'driveway-lights/app', b'ESPURNA'),
                (b'driveway-lights/version', b'1.13.3'),
                (b'driveway-lights/board', b'ALLTERCO_SHELLY1'),
                (b'driveway-lights/host', b'driveway-lights'),
                (b'driveway-lights/ip', b'192.168.1.109'),
                (b'driveway-lights/mac', b'3C:71:BF:2C:8A:90'),
                (b'driveway-lights/rssi', None),  #b'-67'),
                (b'driveway-lights/uptime', None),  #b'17576260'),
                (b'driveway-lights/datetime', None),  #b'2020-01-11 23:01:15'),
                (b'driveway-lights/freeheap', None),  #b'24472'),
                (b'driveway-lights/vcc', None),  #b'3227'),
                (b'driveway-lights/loadavg', None),  #b'1'),
                (b'wallpanel/mywallpanel/sensor/light', None),  #b'{"value":0,"unit":"lx","id":"GP2A Light sensor"}'),
               ]

msg_received = False

states = dict()

def sub_cb(topic, msg):
    # print((topic, msg))
    global msg_received
    msg_received = True
    if topic in [b'distance/ronald/home', b'distance/ronald/work']:
        global states
        states[topic] = int(msg)
        return
    for (key, value) in expectedData:
        if topic == key:
            if value is None:
                break  # ignore this message
            if msg == value:
                break  # msg is as expected
            print('Unexpected msg: {1}, for topic: {0}'.format(topic, msg))
    else:
        print('Unexpected topic: {0}, msg: {1})'.format(topic, msg))


def connect_and_subscribe():
    global client_id, mqtt_server, topic_sub
    client = MQTTClient(client_id, mqtt_server)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic_sub)
    print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
    return client


def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(10)
    machine.reset()

try:
    client = connect_and_subscribe()
except OSError as e:
    restart_and_reconnect()


def SendHelloEvery5sec():
    last_message = 0
    message_interval = 5
    counter = 0
    topic_pub = b'hello'

    while True:
        try:
            client.check_msg()
            if (time.time() - last_message) > message_interval:
                msg = b'Hello #%d' % counter
                client.publish(topic_pub, msg)
                last_message = time.time()
                counter += 1
        except OSError:
            restart_and_reconnect()


def handle_messsages():
    """Handle all MQTT messages in queue."""
    global msg_received
    i=0
    while True:
        msg_received = False
        client.check_msg()
        i+=1
        if i==100:
            print('{} iterations done...'.format(i))
            return
        if not msg_received:
            # print('No more messages in queue')
            return

