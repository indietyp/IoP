import os
import uuid
import json
import socket
EXTERNAL_PORT = 4012
MULTICAST_ADDRESS = '224.0.0.1'


class MeshString(str):
  import sys

  def rreplace(self, old, new, maxcount=sys.maxsize):
    """ reverse replace
        reverses string and runs replace at reversed old and new
        returns reversed reversed string
    """
    self = self[::-1].replace(old[::-1], new[::-1], maxcount)[::-1]
    return self


class MeshNetwork(object):
  """ response daemon for mesh network """

  def __init__(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com", 80))
    self.IP = s.getsockname()[0]
    s.close()

  def daemon_process(self, received):
    message = received[0].decode('utf-8')
    print('received following package: \n' + message)
    message = message.replace('<', '[').replace('>', ']')
    message = eval(message)

    if self.IP != received[1][0]:
      code = str(message[3][0])
      if code[0] == '1':
        if int(code[1:3]) == 1:
          target = [message[1][0], received[1][0]]
          self.alive(target, 2, additional_information=message[4][0])
      elif code[0] == '2':
        target = [message[1][0], received[1][0]]
        self.register_lite(int(code[1:3]) + 1, recipient=target, messages=message[4])
      elif code[0] == '4':
        if int(code[1:3]) == 1:
          self.discover(target=[message[1][0], received[1][0]], mode=2)
      elif code[0] == '6':
        target = [message[1][0], received[1][0]]
        self.register_lite(int(code[1:3]) + 1, recipient=target, messages=[message[4]])
    else:
      print('not processing request - same ip')

  def daemon(self):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    multicast_addr = MULTICAST_ADDRESS
    port = EXTERNAL_PORT
    host = '0.0.0.0'
    membership = socket.inet_aton(multicast_addr) + socket.inet_aton(host)

    client.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    client.bind((host, port))
    while True:
      try:
        received = client.recvfrom(65000)

        self.daemon_process(received)
      except Exception as e:
        print(e)

  def send_local(self, mode, code, port=2311):
    """ method for communication between daemon and other scripts """
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender.sendto(str([mode, code]).encode(), ('127.0.0.1', port))
    sender.close()

  def send(self, code, plant=True, messages=[], master=True, priority=255,
           recipient=None, multicast=False, no_database=False):
    """ main method for sending information in the mesh_network
        code - 5 digit number for mode
        plant - optional (origin, plant object)
        messages - 4len array with additional information to be sended
                  -> auto cut to 4 existing
        master - mode of sended information - currently only Master supportet
        priority - 0-255 higher mor priority (not implemented fully yet)
        recipient - [str with UUID, ip] or peewee plant object or None if multicast
        multicast - sending with multicast
        no_database - function does not use database
    """
    configured = plant
    if configured and 'config.json' in os.listdir():
      with open('config.json') as out:
        plant = json.dumps(out.read())

    if type(recipient) == list:
      recipient_uuid = recipient[0]
      external_address = recipient[1]
    elif recipient is None:
      recipient_uuid = ''
      external_address = ''
    else:
      recipient_uuid = str(recipient.uuid)
      external_address = recipient.ip

    len_message = len(messages)
    [messages.append('') for _ in range(0, 4 - len_message) if len_message < 4]
    [messages.pop() for _ in range(0, len_message - 4) if len_message > 4]

    messages = [x if x != '' else '-' * 256 for x in messages]

    master = int(master)
    package = [master, [], [], [], [], master]

    if configured:
      package[1].append(plant['uuid'])
    else:
      package[1].append('')

    package[1].append('')

    package[2].append(priority)
    package[2].append(recipient_uuid)
    package[3].append(code)
    package[4] = messages

    str_package = repr(package).replace('[', '<', 1)
    str_package = MeshString(str_package).rreplace(']', '>', 1).encode('utf-8')
    print('sending following package: \n' + str_package.decode())

    if multicast is False:
      print('package destination: ' + external_address)
      address = external_address
      sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
      print('package destination: multicast ({})'.format(MULTICAST_ADDRESS))
      address = MULTICAST_ADDRESS
      sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
      sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    sender.sendto(str_package, (address, EXTERNAL_PORT))

    sender.close()

  def alive(self, target, mode=1, additional_information=''):
    if mode > 2:
      raise ValueError('invalid mode')

    if mode == 1:
      code = 10100
    elif mode == 2:
      code = 10200

    self.send(code, recipient=target, messages=[additional_information])

  def discover(self, target=None, mode=1):
    """ if mode is 1 - target == peewee plant object
        if mode is 2 - target == list [UUID, IP]
    """
    if mode == 1:
      print('not supported in slave module')
    elif mode == 2:
      code = 40200

      if 'config.json' in os.listdir():
        print('discovered - slave not registered')
        code += 3
        self.send(code, plant=False, recipient=target, messages=['NOT_LOGGED', 'NOT_CONFIGURED', 'SLAVE'])
      else:
        print('discovered - slave registered')
        code += 4
        self.send(code, recipient=target, messages=['NOT_LOGGED', 'CONFIGURED', 'SLAVE'])

  def slave(self, target=None, mode=2):
    if mode != 2:
      print('mode not supported')
    else:
      if 'config.json' in os.listdir():
        with open('config.json') as out:
          config = json.dumps(out.read())

        if target[1] == config['uuid']:
          code = 20200
          from sensor import measure
          current = measure()

          self.send(code, recipient=target, messages=[str(current)])

  def register_lite(self, target=None, mode=1, messages=[]):
    if mode == 2:
      if 'config.json' not in os.listdir():
        code = 60200
        self.send(code, recipient=target)
    elif mode == 4:
      code = 60400
      with open('config.json') as out:
        out.write(json.dumps({'uuid': messages[2],
                              'master': {
                                  'ip': messages[1],
                                  'uuid': messages[0]}
                              }))
      self.send(code, recipient=target)

if __name__ == '__main__':
  MeshNetwork().daemon()
