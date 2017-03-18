import socket
import select
from http import HTTPServer
from mesh import MeshNetwork
from dns import DNSHandler

DNS_HEADER_LENGTH = 12
IP = '192.168.178.49'

direct = socket.socket()
direct.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
direct.bind(('0.0.0.0', 4012))
direct.settimeout(0.3)
direct.listen(1)
direct.setblocking(False)

multicast = socket.socket()
multicast.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
multicast.bind(('224.0.0.1', 4012))
multicast.settimeout(0.3)
multicast.listen(1)
multicast.setblocking(False)

http = socket.socket()
http.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
http.bind(('0.0.0.0', 80))
http.settimeout(0.3)
http.listen(1)
http.setblocking(False)

dns = socket.socket()
dns.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
dns.bind(('0.0.0.0', 53))
dns.settimeout(0.3)
dns.listen(1)
dns.setblocking(False)

http_process = HTTPServer()
mesh_process = MeshNetwork()

socks = [direct, multicast, dns, http]
while True:
  ready, _, _ = select.select(socks, [], [])
  for sock in ready:
    cl, addr = sock.accept()
    cl.setblocking(False)
    cl.settimeout(0.3)

    data = b''
    while True:
      try:
        partial = cl.recv(2024)

        if not partial:
          break
        else:
          data += partial
      except:
        break

    print("received message:", data)
    print("received address:", addr)

    if data[:15] in [b'POST / HTTP/1.1', b'GET / HTTP/1.1\r']:
      http_process.process(cl, data)
    elif mesh_process.verification():
      mesh_process.daemon_process(data)
    else:
      dns_process = DNSHandler(cl, data, addr)
      dns_process.handle()
