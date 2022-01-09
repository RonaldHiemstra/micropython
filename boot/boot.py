# This file is executed on every boot (including wake-boot from deepsleep)
from config import Config
import webrepl
import network
import gc
import esp
esp.osdebug(None)


gc.collect()

network_config = Config('network_config.json')

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

if wlan.status() != network.STAT_GOT_IP:
    ssid = network_config.get('ssid')
    ssid_s: Set[bytes] = set()
    while not ssid_s:
        ssid_s = set([s[0] for s in wlan.scan()])
    print('Available networks:\n\t{}'.format(b'\n\t'.join(ssid_s).decode()))
    print('Connecting to{}: {}'.format('' if ssid.encode() in ssid_s else ' hidden???', ssid))

    wlan.connect(ssid, network_config.get('__password'))
    while wlan.isconnected() == False:
        pass
    print('Connection successful')
print(wlan.ifconfig())

webrepl.start()
