def do_connect():
  import network
  import os
  import json
  sta_if = network.WLAN(network.STA_IF)
  ap_if = network.WLAN(network.AP_IF)

  if os.path.isfile('credentials.json'):
    print('found credentials.json')
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
    print('starting station interface')
    mac = ap_if.config('mac').decode()
    ap_if.config(essid='IoP slave: {}'.format(mac[:5]) + , channel=11)

    sta_if.active(False)
    ap_if.active(True)
