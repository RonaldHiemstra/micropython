"""Handle the mqtt messages.

handle_messsages()
"""
#TODO: use asyncio !!!
import machine
import time
from umqtt.simple import MQTTClient
import ubinascii

mqtt_server = '192.168.1.1'
client_id = ubinascii.hexlify(machine.unique_id())

topic_sub = b'#' # subscribe to all messages

msg_received = False

states = dict()

ignored_topics = set()

def sub_cb(topic, msg):
    # print((topic, msg))
    global msg_received
    msg_received = True
    if topic in [b'distance/ronald/home', b'distance/ronald/work',
                 b'distance/miranda/home',
                 b'distance/lieke/home',
                 b'distance/koen/home',
                 b'clock/intensity']:
        global states
        try:
            states[topic] = float(msg)
        except ValueError:
            print('Failed to cast {} to a float'.format(msg))
        return
    if topic not in ignored_topics:
        print('Unhandled topic: {0}, msg: {1})'.format(topic, msg))
        ignored_topics.add(topic)


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

