# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None)
import gc
# import webrepl
# webrepl.start()
gc.collect()


def do_connect():
  import network
  import os
  import json
  sta_if = network.WLAN(network.STA_IF)
  ap_if = network.WLAN(network.AP_IF)

  if 'credentials.json' in os.listdir():
    print('found credentials.json')
    if not sta_if.isconnected():
      credentials = None
      with open('credentials.json') as out:
        credentials = json.loads(out.read())

      ap_if.active(False)
      sta_if.active(True)
      sta_if.connect(credentials['ssid'], credentials['password'])

      while sta_if.status() == network.STAT_CONNECTING:
        pass

      if sta_if.status() in [network.STAT_WRONG_PASSWORD, network.STAT_CONNECT_FAIL, network.STAT_NO_AP_FOUND]:
        os.remove('credentials.json')

        import machine
        machine.reset()
    else:
      print('already connected')

  else:
    print('starting ad-hoc interface')
    sta_if.active(False)
    ap_if.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.4.1', '192.168.4.1'))
    ap_if.active(True)
    import ubinascii
    mac = ubinascii.hexlify(ap_if.config('mac')).decode()
    ap_if.config(essid='IoP slave: {}'.format(mac[:5]), channel=11, password='IoPslave')
do_connect()
gc.collect()
