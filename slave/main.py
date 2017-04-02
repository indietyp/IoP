import network
from communication import CommunicationMainFrame
sta_if = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)


communication = CommunicationMainFrame()
communication.daemon(wifi=False)
# if sta_if.active():
#   communication.daemon(http=False, dns=False)
# elif ap_if.active():
#   communication.daemon(iop=False, multicast=False)
