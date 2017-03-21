import gc
import micropython
import socket
import select
from http import HTTPServer
from mesh import MeshNetwork
from dns import DNSHandler
gc.collect()
micropython.mem_info(1)


class CommunicationMainFrame:
  def __init__(self):
    pass

  def daemon(self, wifi=False):
    connect = ('0.0.0.0', 80) if not wifi else ('', 4012)

    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(connect)
    sock.settimeout(0.3)
    sock.listen(1)

    http_process = HTTPServer()
    mesh_process = MeshNetwork()

    while True:
      print('triggered')
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
            print(partial)
            data += partial
        except Exception as e:
          print(e)
          break

      print("received message:", data)
      print("received address:", addr)

      if not wifi:
        http_process.process(cl, data)
      else:
        mesh_process.daemon_process(data)

      cl.close()
