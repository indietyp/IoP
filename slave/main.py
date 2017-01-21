import network
sta_if = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)


def establish():
  import http
  try:
    http.server()
  except:
    import machine
    machine.reset()

if sta_if.active():
  from daemon import MeshNetwork
  MeshNetwork.daemon()

elif ap_if.active():
  establish()
