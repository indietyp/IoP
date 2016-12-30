import socket
from multiprocessing import Process
import time
import uuid
from models.plant import Plant
from tools.main import MeshString
from models.mesh import MeshMessage, MeshObject
from settings.mesh import MULTICAST_ADDRESS, EXTERNAL_PORT
from settings.database import DATABASE_NAME
from tools.sensor import ToolChainSensor
from tools.mesh import MeshTools
from bson import json_util


class MeshNetwork(object):
  """ response daemon for mesh network """

  def __init__(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com", 80))
    self.IP = s.getsockname()[0]
    s.close()

  @staticmethod
  def http_server(directory, port):
    import os
    import http.server
    import socketserver

    os.chdir(directory)

    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), Handler)

    print("serving at port " + str(port) + ", for 5 requests")
    for _ in range(0, 5):
      httpd.handle_request()

  def daemon_process(self, received):
    # print(received)
    message = received[0].decode('utf-8')
    message = message.replace('<', '[').replace('>', ']')
    message = eval(message)
    print(message[4][0].zfill(5))

    if self.IP != received[1][0]:
      code = str(message[3][0])
      if code[0] == '1':
        if int(code[1:3]) == 1:
          target = [message[1][0], received[1][0]]
          self.alive(target, 2, additional_information=message[4][0])
        elif int(code[1:3]) == 2:
          self.send_local(mode=1, code=1)
      elif code[0] == '2':
        if int(code[1:3]) == 1:
          pass
      elif code[0] == '3':
        target = [message[1][0], received[1][0]]
        local_uuid = message[2][1]
        self.register(int(code[1:3]) + 1, recipient=target, messages=message[4], local_uuid=local_uuid)

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
      elif code[0] == '5':
        target = [message[1][0], received[1][0]]
        if int(code[1:3]) == 1:
          sub = int(code[3:]) + 1
          self.deliver(1, sub=sub, recipient=target, message=message[4])
        elif int(code[1:3]) == 2:
          sub = int(code[3:]) + 1
          self.deliver(2, sub=sub, recipient=target)
        elif int(code[1:3]) == 3:
          sub = int(code[3:]) + 1
          self.deliver(3, sub=sub, recipient=target, message=message)
    else:
      print('same IP')

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

        p = Process(target=self.daemon_process, args=(received, ))
        p.daemon = True
        p.start()
      except Exception as e:
        print(e)

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

  def send_local(self, mode, code, port=2311):
    """ method for communication between daemon and other scripts """
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender.sendto(str([mode, code]).encode(), ('127.0.0.1', port))
    sender.close()

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
      recipient_uuid = str(recipient.uuid)
      external_address = recipient.ip
      create_message_object_recipient = recipient

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

  def alive(self, target, mode=1, additional_information=''):
    if mode > 2:
      raise ValueError('invalid mode')

    plant = Plant.get(Plant.localhost == True)

    if mode == 1:
      code = 10100
    elif mode == 2:
      code = 10200

    self.send(code, plant=plant, recipient=target, messages=[additional_information])

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

  def register(self, mode, ip=None, recipient=None, messages=None, origin=None, local_uuid=None):
    """ MODES:
      [1][ORIGIN] ASK PUBLICKEY
      [2][RECIPIENT] GENERATE PUBLICKEY AND SEND
      [3][RECIPIENT, MESSAGES] SAVE AND SEND AES (ENCRYPTED)
      [4][RECIPIENT, MESSAGES] SAVE AND SEND OK
      [5][RECIPIENT] ESTABLISH WEBSERVER
      [6][RECIPIENT, MESSAGES, LOCAL_UUID] DOWNLOAD
      [7][RECIPIENT] CANCEL HTTP SERVER AND TEST REST
      [8][RECIPIENT] SEND DONE
      [9][RECIPIENT] SEND DONE

      RECIPIENT = [UUID, IP]
    """

    if mode == 1:
      localhost = Plant.get(Plant.localhost == True)
      try:
        plant = MeshObject.get(MeshObject.registered == False, MeshObject.ip == origin.ip)
      except:
        print('plant already registered')

      self.send(30100, plant=localhost, recipient=origin)

    elif mode == 2:
      from tools.mesh import MeshTools
      from Crypto.PublicKey import RSA
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

      public_key = ''.join(messages)
      public_key = tools.hex2bin(public_key)
      crypter = RSA.importKey(public_key)

      key = tools.random_string(32)
      iv = tools.random_string(16, True)

      for i in [['.key', key], ['.iv', iv]]:
        filename = directory + 'localhost' + i[0]
        with open(filename, 'w') as out:
          out.write(i[1])

      e_key = crypter.encrypt(key.encode(), 'x')[0]
      e_iv = crypter.encrypt(iv.encode(), 'x')[0]

      e_key = tools.bin2hex(e_key)
      e_iv = tools.bin2hex(e_iv)

      filename = directory + recipient[1] + '.pub'
      hex_key = tools.bin2hex(public_key)
      hex_key = hex_key.decode()
      with open(filename, 'w') as out:
        out.write(hex_key)

      self.send(30300, recipient=recipient, messages=[e_key.decode(), e_iv.decode(), '', 'NON_STANDARD_LENGTH'], plant=plant)

    elif mode == 4:
      from Crypto.PublicKey import RSA
      from tools.mesh import MeshTools
      tools = MeshTools()

      with open('./keys/localhost.priv') as out:
        private_key = out.read()

      private_key = tools.hex2bin(private_key.encode())
      crypter = RSA.importKey(private_key)

      directory = './keys/'
      for i in [['.key', messages[0]], ['.iv', messages[1]]]:
        filename = directory + recipient[1] + i[0]
        i[1] = tools.hex2bin(i[1].encode())
        output = crypter.decrypt(i[1])
        with open(filename, 'w') as out:
          out.write(output.decode())

      self.send(30400, recipient=recipient, no_database=True)

    elif mode == 5:
      # ENCRYPT
      from Crypto.PublicKey import RSA
      from settings.database import DATABASE_NAME
      import random
      from tools.mesh import MeshAES
      from tools.mesh import MeshTools
      import time

      tools = MeshTools()
      plant = Plant.get(Plant.localhost == True)
      print(plant.uuid)

      directory = './database_serve/'
      tools.reinit_dir(directory)

      filename = directory + 'index.html'
      with open(filename, 'w') as out:
        out.write(tools.random_string(20) + 'PRAISE THE ALL MIGHTY UNICORN' + tools.random_string(20))

      hashed_filename = tools.random_string(100, True)
      filename = directory + hashed_filename

      with open('./keys/localhost.iv') as out:
        iv = out.read()
      with open('./keys/localhost.key') as out:
        key = out.read()

      MeshAES.encrypt_file(DATABASE_NAME, filename, key, iv)
      print(filename)

      # free 124 - 134
      # original_port = 128 birthday of Johannes Neubrand, yeah :D
      port = random.randint(124, 132)

      with open('./keys/' + recipient[1] + '.pub') as out:
        hex_public = out.read()
      print(hex_public)

      public_key = tools.hex2bin(hex_public.encode())
      crypter = RSA.importKey(public_key)

      e_port = crypter.encrypt(str(port).encode(), 'x')[0]
      e_hash = crypter.encrypt(hashed_filename.encode(), 'x')[0]

      rec_uuid = Plant.get(Plant.ip == recipient[1])
      e_uuid = crypter.encrypt(str(rec_uuid.uuid).encode(), 'x')[0]

      e_port = tools.bin2hex(e_port).decode()
      e_hash = tools.bin2hex(e_hash).decode()
      e_uuid = tools.bin2hex(e_uuid).decode()


      # p = Process(target=self.http_server, args=('./database_serve/', port, ))
      # p.daemon = True
      # p.start()
      # time.sleep(2)

      localhost = Plant.get(Plant.localhost == True)
      self.send(30500, recipient=recipient, messages=[e_port, e_hash, e_uuid], plant=localhost)
      self.http_server('./database_serve/', port)

    elif mode == 6:
      import urllib.request
      import time
      from Crypto.PublicKey import RSA
      from tools.mesh import MeshAES
      from tools.mesh import MeshTools
      from settings.database import DATABASE_NAME
      from sensor_scripts.daemon.main import SensorDaemon
      from uuid import UUID
      import os
      tools = MeshTools()
      time.sleep(2)

      directory = './keys/'
      with open(directory + 'localhost.priv') as out:
        private_key = out.read()

      private_key = MeshTools().hex2bin(private_key.encode())
      crypter = RSA.importKey(private_key)

      messages[0] = tools.hex2bin(messages[0].encode())
      messages[1] = tools.hex2bin(messages[1].encode())
      messages[2] = tools.hex2bin(messages[2].encode())

      u_port = crypter.decrypt(messages[0]).decode()
      u_hash = crypter.decrypt(messages[1]).decode()
      u_uuid = crypter.decrypt(messages[2]).decode()

      urllib.request.urlretrieve('http://{0}:{1}/{2}'.format(recipient[1], u_port, u_hash), u_hash)

      with open(directory + recipient[1] + '.iv') as out:
        iv = out.read()
      with open(directory + recipient[1] + '.key') as out:
        key = out.read()

      MeshAES.decrypt_file(u_hash, DATABASE_NAME, key, iv)

      old_plant = Plant.get(Plant.localhost == True)
      print(old_plant.name)
      old_plant.localhost = False
      old_plant.save()

      plant = Plant.get(Plant.uuid == UUID(u_uuid))
      print(plant.name)
      plant.localhost = True
      plant.save()

      os.remove(u_hash)

      self.send(30600, recipient=recipient, messages=[u_port], plant=plant)
      SensorDaemon().run()

    elif mode == 7:
      import urllib.request
      import json
      print(recipient[1])
      try:
        with urllib.request.urlopen('http://' + recipient[1] + ':2902/get/plant/' + recipient[0]) as response:
          output = json.loads(response.read().decode('utf8'))

        if output['localhost'] is not True:
          print('WARNING -> local change not happend')
      except:
        print('WARNING -> rest_api not affected - restart needed')

      finished = False
      while finished is False:
        try:
          urllib.request.urlopen('http://localhost:' + messages[0])
        except:
          finished = True

      plant = Plant.get(Plant.localhost == True)
      self.send(30700, recipient=recipient, plant=plant)

    elif mode == 8:
      plant = Plant.get(Plant.localhost == True)
      self.send_local(mode=4, code=1)
      self.send(30800, recipient=recipient, plant=plant)

    elif mode == 9:
      plant = Plant.get(Plant.localhost == True)
      self.send_local(mode=4, code=1)
      self.send(30900, recipient=recipient, plant=plant)

  def deliver(self, mode, recipient=None, sub=None, sensor=None, message=[], change={}):
    from models.plant import Plant
    plant = Plant.get(Plant.localhost == True)
    if mode == 1:
      if sub == 1:
        self.send(50101, recipient=recipient, messages=[sensor.name], plant=plant)
      elif sub == 2:
        import json
        import urllib.request
        from models.sensor import Sensor
        # from tools.sensor import ToolChainSensor

        plant = Plant.get(Plant.localhost == True)
        # print('http://{0}:2902/get/plant/{1}/sensor/{2}/latest'.format(recipient[1], recipient[0], message[0]))
        with urllib.request.urlopen('http://{0}:2902/get/plant/{1}/sensor/{2}/latest'.format(recipient[1], recipient[0], message[0])) as response:
          dataset = json.loads(response.read().decode('utf8'))

        # consider insert_sensor? - created_at only differs and predication not needed! - would solve a load of problems
        # tesing!

        rec_obj = Plant.get(Plant.uuid == recipient[0])
        sensor = Sensor.get(Sensor.name == message[0])

        # new_data = SensorData()
        # new_data.plant = rec_obj
        # new_data.sensor = sensor
        # new_data.created_at = dataset['created_at']
        # new_data.value = dataset['value']
        # new_data.persistant = dataset['persistant']
        # new_data.save()

        data = {'plant': rec_obj,
                'sensor': sensor,
                'value': dataset['value']}
        ToolChainSensor().insert_data(data, mesh=False)
        # ToolChainSensor().modify_sensor_status(data)

        self.send(50102, recipient=recipient, plant=plant)

    elif mode == 2:
      if sub == 1:
        self.send(50201, recipient=recipient, plant=plant)
      if sub == 2:
        message = ''
        external = Plant.get(Plant.uuid == recipient[0])
        if external.ip != recipient[1]:
          message = 'CHANGED'
          external.ip = recipient[1]
          external.save()
        else:
          message = 'NOT_CHANGED'

        self.send(50202, recipient=recipient, plant=plant, messages=['', '', '', message])
    elif mode == 3:
      if sub == 1:
        if 'object' in change and 'uuid' in change:
          self.send(50301, recipient=recipient, plant=plant, messages=[change['object'], str(change['uuid'])])
        else:
          raise ValueError('no full change object')
      if sub == 2:
        import json
        import urllib.request
        from bson import json_util
        from models.plant import Plant, Person
        from models.plant import MessagePreset

        if int(message[0]) == 0:
          with urllib.request.urlopen('http://{}:2902/get/plant/{}'.format(recipient[1], message[1])) as response:
            data = json.loads(response.read().decode('utf8'), object_hook=json_util.object_hook)

          del data['uuid']
          del data['person']
          del data['preset']
          del data['localhost']
          del data['created_at']

          plant = Plant.get(Plant.uuid == message[1])
          for key in data.keys():
            setattr(plant, key, plant[key])
          plant.save()

        elif int(message[0]) == 1:
          with urllib.request.urlopen('http://{}:2902/get/sensor/{}'.format(recipient[1], message[1])) as response:
            data = json.loads(response.read().decode('utf8'))
          del data['uuid']

          sensor = Sensor.get(Sensor.uuid == message[1])
          for key in data.keys():
            setattr(sensor, key, sensor[key])
          sensor.save()

        elif int(message[0]) == 2:
          # person
          with urllib.request.urlopen('http://{}:2902/get/responsible/{}'.format(recipient[1], message[1])) as response:
            data = json.loads(response.read().decode('utf8'))
          del data['uuid']

          person = Person.get(Person.uuid == message[1])
          for key in data.keys():
            setattr(person, key, person[key])
          person.save()
        elif int(message[0]) == 3:
          # sensor satisfaction
          pass
        elif int(message[0]) == 4:
          with urllib.request.urlopen('http://{}:2902/get/message/{}'.format(recipient[1], message[1])) as response:
            data = json.loads(response.read().decode('utf8'))
          del data['uuid']

          message_preset = MessagePreset.get(MessagePreset.uuid == message[1])
          for key in data.keys():
            setattr(message_preset, key, message_preset[key])
          message_preset.save()
        elif int(message[0]) == 5:
          current = Plant.get(Plant.host == True)
          current.host = False
          current.save()

          new = Plant.get(Plant.uuid == message[1])
          new.host = True
          current.save()
        # notify


if __name__ == '__main__':
  import sys
  if len(sys.argv) > 1:
    if sys.argv[1] == 'daemon':
      MeshNetwork().daemon()
    elif sys.argv[1] == 'register':
      plant = Plant.get(Plant.name == 'Holger')
      MeshNetwork().register(1, origin=plant)
    elif sys.argv[1] == 'alive':
      plant = Plant.get(Plant.name == 'marta')
      # i = 0
      # import datetime
      # now = datetime.datetime.now()
      # try:
      #   while True:
      #     i += 1
      MeshNetwork().alive(plant, 1)
      # except KeyboardInterrupt:
      #   print(datetime.datetime.now() - now)

    elif sys.argv[1] == 'notify':
      if sys.argv[2] == 'ip':
        plant = Plant.get(Plant.name == 'Holger')
        MeshNetwork().deliver(2, sub=1, recipient=plant)
      elif sys.argv[2] == 'data':
        pass
  else:
    print('nothing selected, starting daemon')

    def startup():
      try:
        MeshNetwork().daemon()
      except KeyboardInterrupt as e:
        print(e)
      except Exception as e:
        print(e)
        return startup()
    startup()
