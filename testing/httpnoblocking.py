import socket
import select

http = socket.socket()
# socket.AF_INET, socket.SOCK_DGRAM
http.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
http.bind(('0.0.0.0', 80))
http.settimeout(0.3)
http.listen(1)
http.setblocking(False)

socks = [http]
while True:
  ready, _, _ = select.select(socks, [], [])
  for sock in ready:
    cl, addr = sock.accept()
    cl.setblocking(False)
    cl.settimeout(0.3)

    data = b''
    while True:
      try:
        partial = cl.recv(1024)

        if not partial:
          break
        else:
          data += partial
      except:
        break

    print("received message:", data)
    print("received address:", addr)

    if data[:15] in [b'POST / HTTP/1.1', b'GET / HTTP/1.1\r']:
      print('http')
