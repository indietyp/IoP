import socket
import time
import uuid
from tools.main import MeshString
from models.mesh import MeshMessage, MeshObject
from settings.mesh import MULTICAST_ADDRESS, EXTERNAL_PORT
from settings.database import DATABASE_NAME
from tools.mesh import MeshTools


class MeshNetwork(object):
  """ response daemon for mesh network """

  def __init__(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com", 80))
    self.IP = s.getsockname()[0]
    s.close()

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
      received = client.recvfrom(65000)
      print(received)
      message = received[0].decode('utf-8')
      message = message.replace('<', '[').replace('>', ']')
      message = eval(message)

      # origin = Plant.get(Plant.uuid == uuid.UUID(message[1][0]))
      # target = Plant.get(Plant.uuid == uuid.UUID(message[2][1]))

      # if target.id != Plant.get(Plant.localhost == True).id:
        # raise ValueError('target & local plant not the same')

      if self.IP != received[1][0]:
        code = str(message[3][0])
        if code[0] == '1':
          if int(code[1:3]) == 1:
            self.alive(origin, 2)
          else:
            self.send_local()
        elif code[0] == '2':
          if int(code[1:3]) == 1:
            pass
        elif code[0] == '3':
          pass
        elif code[0] == '4':
          if int(code[1:3]) == 1:
            self.discover(target=[message[1][0], received[1][0]], mode=2)
          elif int(code[1:3]) == 2:
            registered = False if message[1][0] == '' else True

            status, result = MeshObject.get_or_create(
                ip=received[1][0],
                defaults={'registered': registered})
            status.registered = registered
            status.save()
      else:
        print('same IP')

  def create_message_object(self, plant, code, messages, received=False,
                            recipient=None, muuid=None, priority=255):
    message = MeshMessage()
    message.plant = plant
    message.sender = recipient
    message.uuid = muuid if muuid is not None else uuid.uuid4()

    message.received = received
    message.priority = priority
    message.code = code

    message.a_message = messages[0]
    message.b_message = messages[1]
    message.c_message = messages[2]
    message.d_message = messages[3]
    message.save()

    return message.uuid

  def send(self, code, plant=None, messages=[], master=True, priority=255,
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
    if type(recipient) == list:
      recipient_uuid = recipient[0]
      external_address = recipient[1]
      create_message_object_recipient = None
    elif recipient is None:
      recipient_uuid = ''
      external_address = ''
      create_message_object_recipient = None
    else:
      recipient_uuid = recipient.uuid
      external_address = recipient.ip

    len_message = len(messages)
    [messages.append('') for _ in range(0, 4 - len_message) if len_message < 4]
    [messages.pop() for _ in range(0, len_message - 4) if len_message > 4]

    if no_database is False:
      muuid = self.create_message_object(plant, code, messages, True,
                                         create_message_object_recipient, None, priority)

    messages = [x if x != '' else '-' * 256 for x in messages]

    master = int(master)
    package = [master, [], [], [], [], master]

    if plant is not None:
      package[1].append(str(plant.uuid))
      package[1].append(str(muuid))
    else:
      package[1].append('')
      package[1].append(str(uuid.uuid4()))

    package[2].append(priority)
    package[2].append(recipient_uuid)
    package[3].append(code)
    package[4] = messages

    str_package = repr(package).replace('[', '<', 1)
    str_package = MeshString(str_package).rreplace(']', '>', 1).encode('utf-8')
    print(str_package)

    if multicast is False:
      print(external_address)
      address = external_address
      sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
      print('MULTICAST')
      address = MULTICAST_ADDRESS
      sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
      sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    sender.sendto(str_package, (address, EXTERNAL_PORT))

    sender.close()

  def alive(self, target, mode=1):
    if mode > 2:
      raise ValueError('invalid mode')
    plant = Plant.get(Plant.localhost == True)

    if mode == 1:
      code = 10100
      # self.send(plant, code, recipient=target)
    elif mode == 2:
      code = 10200

    self.send(code, plant=plant, recipient=target)

  def discover(self, target=None, mode=1):
    """ if mode is 1 - target == peewee plant object
        if mode is 2 - target == list [UUID, IP]
    """
    if mode == 1:
      plant = Plant.get(Plant.localhost == True)
      code = 40100
      self.send(code, plant=plant, recipient=None, multicast=True)
    elif mode == 2:
      code = 40200
      try:
        print('DISCOVER: 1')
        plant = Plant.get(Plant.localhost == True)
        code += 1
        self.send(code, plant=plant, recipient=target, messages=['LOGGED', 'DATABASE'])
      except:
        print('DISCOVER: 2')
        code += 2
        self.send(code, no_database=True, recipient=target, messages=['NOT_LOGGED', 'NO_DATABASE'])

  def register(self, mode, ip=None, recipient=None, message=None, origin=None):
    """ MODES:
      [1] DISCOVER AND ASK PUBLICKEY
      [2] GENERATE PUBLICKEY AND SEND
      [3] OPEN HTTP AND ESTABLISH
      [4] DOWNLOAD FILE, DECRYPT, RENAME
      [5] SIGNAL FINISHED
      [6] SIGNAL WORKING
      [7] SINGAL DONE
      [8] SINGAL DONE

      RECIPIENT = [UUID, IP]
    """

    if mode == 1:
      localhost = Plant.get(Plant.localhost == True)
      try:
        plant = MeshObject.get(MeshObject.registered == False, MeshObject.ip == ip)
      except:
        raise 'plant already registered'

      self.send(30100, plant=localhost, recipient=['', plant.ip])

    elif mode == 2:
      import binascii
      import os
      from Crypto.PublicKey import RSA
      from tools.mesh import MeshTools
      from Crypto import Random
      import re
      tools = MeshTools()

      random_generator = Random.new().read
      key = RSA.generate(1024, random_generator)

      directory = './keys/'
      tools.create_dir_if_not_exists(directory)

      public = key.publickey().exportKey('DER')

      for i in [['.pub', public],
                ['.priv', key.exportKey('DER')]]:

        filename = directory + 'localhost' + i[0]
        hex_key = tools.bin2hex(i[1])
        hex_key = hex_key.decode()
        with open(filename, 'w') as out:
          out.write(hex_key)

      public = tools.bin2hex(public)
      public = public.decode()
      print(len(public))
      public = re.findall('.{1,100}', public)
      print(str(public))

      self.send(30200, recipient=recipient, messages=public, no_database=True)

    elif mode == 3:
      from Crypto.PublicKey import RSA
      from tools.mesh import MeshTools

      plant = Plant.get(Plant.localhost == True)
      tools = MeshTools()
      directory = './keys/'

      public_key = ''.join(message)
      public_key = tools.hex2bin(public_key)
      crypter = RSA.importKey(public_key)

      key = tools.random_string(32)
      iv = tools.random_string(10, True)

      for i in [['.key', key], ['.iv', iv]]:
        filename = directory + 'localhost' + i[0]
        with open(filename, 'w') as out:
          out.write(i[1])

      e_key = crypter.encrypt(key.encode(), 'x')[0]
      e_iv = crypter.encrypt(iv.encode(), 'x')[0]

      e_key = tools.bin2hex(e_key)
      e_iv = tools.bin2hex(e_iv)

      filename = directory + origin + '.pub'
      hex_key = tools.bin2hex(public_key.encode())
      hex_key = hex_key.decode()
      with open(filename, 'w') as out:
        out.write(hex_key)

      self.send(30300, recipient=recipient, messages=[e_key.decode(), e_iv.decode(), '', 'NON_STANDARD_LENGTH'], plant=plant)

    elif mode == 4:
      # READ FILE PRIVATE KEY -> DECRYPT
      # SAVE KEY IV
      # (IP . replaced with _)
      pass

    elif mode == 5:
      import http.server
      import socketserver
      import os
      import shutil
      tools = MeshTools()

      directory = './database_serve/'
      tools.reinit_dir(directory)

      filename = directory + 'index.html'
      with open(filename, 'w') as out:
        out.write(tools.random_string(20) + 'PRAISE THE ALL MIGHTY UNICORN' + tools.random_string(20))

      filename = directory + tools.random_string(100, True)
      shutil.copyfile(DATABASE_NAME, filename)
      print(filename)

      os.chdir(directory)
      PORT = 8000

      Handler = http.server.SimpleHTTPRequestHandler

      httpd = socketserver.TCPServer(("", PORT), Handler)

      print("serving at port", PORT)
      httpd.serve_forever()


if __name__ == '__main__':
  from models.plant import Plant

  # plant = Plant.get(Plant.name == 'marta')
  # MeshNetwork().send(plant, 10100, ['', '', '', ''])
  # MeshNetwork().daemon()
  # MeshNetwork().discover(1)
  # import re
  key = ['30819f300d06092a864886f70d010101050003818d0030818902818100dbb6652a142ee8a36375c77a84c51f3410762486bf', 'c754e7c57d087ac5e61ca8a68847715d19493ee03fe6a52f2ab452fc067e21d186c84596bc3ef33211b6a291e4c1300e1d3b', 'dddf4086558b18c3331d8660063286b034307380abba3dd30774f83404662267f97b0765aca03e82d6accfa5026254c31da9', '8822dec0e131490203010001']
  MeshNetwork().register(3, origin='192.168.178.54', recipient=['', '192.168.178.54'], message=key)
  # MeshNetwork().discover(['91c9280b-76c1-42a3-93eb-85250065230f', '192.168.178.54'], mode=2)
