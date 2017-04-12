import os
import uuid
import time
import socket
import logging
import tools.logger
from copy import deepcopy
from models.plant import Plant
from tools.main import MeshString, VariousTools
from multiprocessing import Process
from tools.sensor import ToolChainSensor
from models.mesh import MeshMessage, MeshObject
from settings.mesh import MULTICAST_ADDRESS, EXTERNAL_PORT
logger = logging.getLogger('mesh')


class MeshNetwork(object):
  """ response daemon for mesh network """

  def __init__(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com", 80))
    self.IP = s.getsockname()[0]
    self.basedir = os.path.dirname(os.path.realpath(__file__))
    s.close()

  @staticmethod
  def http_server(directory, port):
    import os
    import http.server
    import socketserver

    os.chdir(directory)

    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), Handler)

    logger.info("serving HTTP-server at port " + str(port) + ", for 5 requests")
    for _ in range(0, 5):
      httpd.handle_request()

  def verification(self, message, origin, raw):
    verification = False
    if (raw[0] != '<' or
        raw[-1] != '>' or
        len(message) != 6 or
        len(message[1]) != 2 or
        len(message[2]) != 2 or
        len(message[3]) != 1 or
        len(message[4]) != 4 or
        len(str(message[3][0])) != 5 or
        not str(message[3][0]).isdigit() or
        message[0] not in [0, 1] or
        message[0] != message[5] or
        not str(message[2][0]).isdigit() or
        message[2][0] > 255):

      logger.warning('potential spoofing attack - no valid package')
      return False

    code = str(message[3][0])
    database = VariousTools.verify_database()

    if database:
      target = Plant.select().where(Plant.uuid == message[1][0])

      if target.count() == 0:
        if code[0] == '4':
          # discover is crossover
          return True
        elif code[0] == '3' and int(code[1:3]) % 2 == 1:
          # plant doesn't know itself - uuid not known
          return True
        else:
          return False
      target = target[0]

      if target.ip != origin[0]:
        if code[0] == '5' and int(code[1:3]) == 2:
          # method for updating own ip - would be a bit dumb to disable that
          verification = True
        elif code[0] == '4':
          # discover is crossover
          verification = True
        else:
          return False
      elif code[0] == '3' and int(code[1:3]) % 2 == 0:
        # even code numbers indicate the recipient - therefor having a database and
        # still getting registered is not a valid method
        return False
      else:
        verification = True

    else:
      if code[0] == '4':
        # discover is crossover
        verification = True
      elif code[0] == '3' and int(code[1:3]) % 2 == 0:
        # even code numbers indicate the recipient - therefor having no databse\
        # and getting registered is only valid method
        verification = True
      else:
        return False
    # for additional extra cases testing is required, but I don't think that I forgot one
    return verification

  def daemon_process(self, received):
    message = received[0].decode('utf-8')
    logger.info('received following package: \n' + message)
    message = message.replace('<', '[').replace('>', ']')
    message = eval(message)

    verified = self.verification(message, received[1], received[0].decode('utf-8'))
    logger.info('Verification: ' + str(verified))

    if self.IP != received[1][0] and verified:
      code = str(message[3][0])
      if code[0] == '1':
        if int(code[1:3]) == 1:
          target = [message[1][0], received[1][0]]
          self.alive(target, 2, additional_information=message[4][0])
        elif int(code[1:3]) == 2:
          self.send_local(mode=1, code=1)
      elif code[0] == '2':
        target = [message[1][0], received[1][0]]
        self.slave(mode=int(code[1:3]) + 1, target=target, messages=message[4])
      elif code[0] == '3':
        target = [message[1][0], received[1][0]]
        local_uuid = message[2][1]
        self.register(int(code[1:3]) + 1, recipient=target, messages=message[4], local_uuid=local_uuid)

      elif code[0] == '4':
        if int(code[1:3]) == 1:
          self.discover(target=[message[1][0], received[1][0]], mode=2)
        elif int(code[1:3]) in [2, 3, 4, 5]:
          registered = False if int(code[1:3]) % 2 == 0 else True
          master = False if int(code[1:3]) > 3 else True

          if VariousTools.verify_database():
            status, result = MeshObject.get_or_create(
                ip=received[1][0],
                defaults={'registered': registered, 'master': master})
            status.registered = registered
            status.master = master
            status.save()
          else:
            import json
            from tools.mesh import MeshTools
            MeshTools().create_dir_if_not_exists(self.basedir + '/discover')

            if os.path.isfile(self.basedir + '/discover/main.json'):
              with open(self.basedir + '/discover/main.json', 'r') as out:
                data = json.loads(out.read())
            else:
              data = []

            data.append({'registered': registered, 'master': master, 'ip': received[1][0]})

            with open(self.basedir + '/discover/main.json', 'w') as out:
              out.write(json.dumps(data))

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
          self.deliver(3, sub=sub, recipient=target, message=message[4])

      elif code[0] == '6':
        target = [message[1][0], received[1][0]]
        self.register_lite(mode=int(code[1:3]) + 1, target=target)

      elif code[0] == '7':
        target = [message[1][0], received[1][0]]
        self.slave_update(mode=int(code[1:3]), sub=int(code[3:]) + 1, target=target)

      elif code[0] == '8':
        target = [message[1][0], received[1][0]]
        self.remove(int(code[1:3]), int(code[3:]) + 1, target, messages=message[4])

    else:
      logger.debug('not processing request - same ip')

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
        logger.warning(e)

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
           recipient=None, multicast=False, no_database=False, encryption=False,
           publickey='', port=EXTERNAL_PORT):
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
    logger.info('sending following package: \n' + str_package.decode())

    if multicast is False:
      logger.debug('package destination: ' + external_address)
      address = external_address
      sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
      logger.debug('package destination: multicast ({})'.format(MULTICAST_ADDRESS))
      address = MULTICAST_ADDRESS
      sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
      sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    if encryption:
      from Crypto.PublicKey import RSA
      from tools.mesh import MeshTools
      import re
      toolchain = MeshTools()
      publickey = toolchain.hex2bin(publickey.encode())
      crypter = RSA.importKey(publickey)

      pkg = b''
      for partial in re.findall('.{1,128}', str_package.decode()):
        partial = crypter.encrypt(partial.encode(), 'x')[0]
        pkg += toolchain.bin2hex(partial) + b'-'

      str_package = pkg[:-1]
      logger.info(str_package)

    sender.sendto(str_package, (address, port))

    sender.close()

  def alive(self, target, mode=1, additional_information=''):
    if mode > 2:
      raise ValueError('invalid mode')

    if VariousTools.verify_database():
      plant = Plant.get(localhost=True)

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
      if VariousTools.verify_database():
        no_database = False
        plant = Plant.get(localhost=True)
      else:
        no_database = True
        plant = None
      code = 40100
      self.send(code, plant=plant, recipient=None, multicast=True, no_database=no_database)
    elif mode == 2:
      if VariousTools.verify_database():
        logger.debug('discovered - database exists')
        code = 40300
        self.send(code, plant=plant, recipient=target, messages=['LOGGED', 'DATABASE', 'MASTER'])
      else:
        logger.debug('discovered - no database exists')
        code = 40200
        self.send(code, no_database=True, recipient=target, messages=['NOT_LOGGED', 'NO_DATABASE', 'MASTER'])

  def slave(self, mode=1, target=None, sensor=None, messages=[]):
    local = Plant.get(localhost=True)
    if mode != 1 and mode != 3:
      logger.warning('every mode except 1 is not implemented and allowed')
    elif mode == 1:
      code = 20100
      self.send(code, recipient=target, messages=[sensor.name], plant=local)
    elif mode == 3:
      logger.debug(messages)
      logger.debug(target)
      from models.sensor import Sensor
      sensor = Sensor.get(name=messages[1])
      slave = Plant.get(uuid=target[0])

      data = {'plant': slave,
              'sensor': sensor,
              'value': messages[0]}
      ToolChainSensor().insert_data(data)

  def slave_update(self, mode=1, sub=1, target=None, messages=[], information={}):
    local = Plant.get(localhost=True)
    if mode > 4:
      logger.warning('mode currently not supported')
    elif mode in [1, 3]:
      if sub == 2 or sub > 3:
        logger.warning('not supported sub mode')
      elif sub == 1:
        raw = 70001
        code = raw + (mode * 100)
        self.send(code, recipient=target, plant=local, messages=[information['min'], information['max']])
      elif sub == 3:
        self.send_local(1, 1)
    elif mode in [2]:
      if sub == 2 or sub > 3:
        logger.warning('not supported sub mode')
      elif sub == 1:
        if information['uuid'] == local.uuid:
          return False
        self.send(70201, recipient=target, plant=local, messages=[str(information['uuid']), information['ip']])
      else:
        self.send_local(1, 1)
    elif mode in [4]:
      if sub == 2 or sub > 3:
        logger.warning('not supported sub mode')
      elif sub == 1:
        self.send(70301, recipeint=target, plant=local)

  def register_lite(self, target=None, mode=1, messages=[], plant=None):
    local = Plant.get(localhost=True)
    if mode == 1:
      # target plant object
      if MeshObject.select().where(MeshObject.registered == False, MeshObject.ip == target.ip, MeshObject.master == False).count() > 0:
        self.send(60100, plant=local, recipient=target)

    elif mode == 3:
      plant = Plant.get(Plant.uuid == target[0])
      logger.info(plant.name)
      master = Plant.get(Plant.uuid == plant.role)
      self.send(60300, plant=local, recipient=target, messages=[str(master.uuid), master.ip, str(plant.uuid)])

    elif mode == 5:
      plant = Plant.get(Plant.uuid == target[0])
      self.send_local(mode=1, code=1)
      self.send(60500, plant=local, recipient=target)

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
        logger.warning('plant already registered')

      self.send(30100, plant=localhost, recipient=origin)

    elif mode == 2:
      from tools.mesh import MeshTools
      from Crypto.PublicKey import RSA
      from Crypto import Random
      import re
      tools = MeshTools()

      random_generator = Random.new().read
      key = RSA.generate(1024, random_generator)

      directory = self.basedir + '/keys/'
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
      public = re.findall('.{1,100}', public)
      logger.debug('generated publickey: ' + str(public))

      self.send(30200, recipient=recipient, messages=public, no_database=True)

    elif mode == 3:
      from Crypto.PublicKey import RSA
      from tools.mesh import MeshTools

      plant = Plant.get(Plant.localhost == True)
      tools = MeshTools()
      directory = self.basedir + '/keys/'

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

      directory = self.basedir + '/keys/'
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
      logger.debug('local plant uuid: {}'.format(plant.uuid))

      directory = self.basedir + '/database_serve/'
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
      logger.debug('filename of generated file: {}'.format(filename))

      # free 124 - 134
      # original_port = 128 birthday of Johannes Neubrand, yeah :D
      port = random.randint(124, 132)

      with open('./keys/' + recipient[1] + '.pub') as out:
        hex_public = out.read()
      logger.debug('received publickey: {}'.format(hex_public))

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

      directory = self.basedir + '/keys/'
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
      logger.info('source plant: {}'.format(old_plant.name))
      old_plant.localhost = False
      old_plant.save()

      plant = Plant.get(Plant.uuid == UUID(u_uuid))
      logger.info('current plant: {}'.format(plant.name))
      plant.localhost = True
      plant.save()

      os.remove(u_hash)

      self.send(30600, recipient=recipient, messages=[u_port], plant=plant)
      SensorDaemon().run()

    elif mode == 7:
      import urllib.request
      import json
      logger.info('source: ' + recipient[1])
      try:
        query = urllib.parse.urlencode({'select': 'full'})
        with urllib.request.urlopen('http://{}:2902/plants/{}?{}'.format(recipient[1], recipient[0], query)) as response:
          output = json.loads(response.read().decode('utf8'))['content']
        # with urllib.request.urlopen('http://' + recipient[1] + ':2902/get/plant/' + recipient[0]) as response:
        #   output = json.loads(response.read().decode('utf8'))

        if output['localhost'] is not True:
          logger.warning('local change not happend - reboot device')
      except:
        logger.warning('rest_api not reachable - reboot device or check nginx config')

      finished = False
      while finished is False:
        try:
          urllib.request.urlopen('http://localhost:' + messages[0])
        except:
          finished = True
      logger.info('terminated local HTTP-server')

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

  def deliver(self, mode, recipient=None, sub=None, sensor=None, message=[], change={}, origin=None):
    from models.plant import Plant
    plant = Plant.get(localhost=True)
    if mode == 1:
      if sub == 1:
        if origin is not None:
          plant = origin

        self.send(50101, recipient=recipient, messages=[sensor.name], plant=plant)
      elif sub == 2:
        import json
        import urllib.request
        from models.sensor import Sensor

        plant = Plant.get(localhost=True)
        query = urllib.parse.urlencode({'select': 'latest'})
        with urllib.request.urlopen('http://{}:2902/plants/{}/sensor/{}?{}'.format(recipient[1], recipient[0], message[0], query)) as response:
          dataset = json.loads(response.read().decode('utf8'))['content']
        # with urllib.request.urlopen('http://{0}:2902/get/plant/{1}/sensor/{2}/latest'.format(recipient[1], recipient[0], message[0])) as response:
        #   dataset = json.loads(response.read().decode('utf8'))

        rec_obj = Plant.get(uuid=recipient[0])
        sensor = Sensor.get(name=message[0])

        data = {'plant': rec_obj,
                'sensor': sensor,
                'value': dataset['value']}
        ToolChainSensor().insert_data(data, mesh=False)

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
          message = [change['object'], str(change['uuid'])]
          if 'sensor' in change:
            message.append(str(change['sensor']))
          elif 'target' in change:
            message.append(str(change['target']))

          self.send(50301, recipient=recipient, plant=plant, messages=message)
        else:
          raise ValueError('no full change object')
      if sub == 2:
        import json
        import urllib.request
        from models.plant import Plant, Person
        from models.plant import MessagePreset

        if int(message[0]) == 0:
          query = urllib.parse.urlencode({'select': 'latest'})
          with urllib.request.urlopen('http://{}:2902/plants/{}'.format(recipient[1], recipient[0], query)) as response:
            data = json.loads(response.read().decode('utf8'))['content']
          # with urllib.request.urlopen('http://{}:2902/get/plant/{}'.format(recipient[1], message[1])) as response:
            # data = json.loads(response.read().decode('utf8'), object_hook=json_util.object_hook)

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
          query = urllib.parse.urlencode({'select': 'full'})
          with urllib.request.urlopen('http://{}:2902/sensors/{}?{}'.format(recipient[1], message[1], query)) as response:
            data = json.loads(response.read().decode('utf8'))
          del data['uuid']

          sensor = Sensor.get(Sensor.uuid == message[1])
          for key in data.keys():
            setattr(sensor, key, sensor[key])
          sensor.save()

        elif int(message[0]) == 2:
          # person
          query = urllib.parse.urlencode({'select': 'full'})
          with urllib.request.urlopen('http://{}:2902/persons/{}?{}'.format(recipient[1], message[1], query)) as response:
            data = json.loads(response.read().decode('utf8'))
          del data['uuid']

          person = Person.get(Person.uuid == message[1])
          for key in data.keys():
            setattr(person, key, person[key])
          person.save()

        elif int(message[0]) == 3:
          # day/night time
          from models.context import DayNightTime
          query = urllib.parse.urlencode({'select': 'full'})
          with urllib.request.urlopen('http://{}:2902/daynight?{}'.format(recipient[1], query)) as response:
            data = json.loads(response.read().decode('utf8'))

          for dn in data:
            daynight = DayNightTime.get_or_create(uuid=dn['uuid'])

            for key in daynight.keys():
              setattr(daynight, key, daynight[key])
            daynight.save()

        elif int(message[0]) == 4:
          query = urllib.parse.urlencode({'select': 'full'})
          with urllib.request.urlopen('http://{}:2902/messages/{}?{}'.format(recipient[1], message[1], query)) as response:
            data = json.loads(response.read().decode('utf8'))
          del data['uuid']

          message_preset = MessagePreset.get(MessagePreset.uuid == message[1])
          for key in data.keys():
            setattr(message_preset, key, message_preset[key])
          message_preset.save()

        elif int(message[0]) == 5:
          current = Plant.get(host=True)
          current.host = False
          current.save()

          new = Plant.get(uuid=message[1])
          new.host = True
          new.save()

        elif int(message[0]) == 6:
          from models.sensor import SensorSatisfactionLevel, SensorSatisfactionValue
          cau_gen = SensorSatisfactionLevel.get(SensorSatisfactionLevel.name_color == 'yellow')
          opt_gen = SensorSatisfactionLevel.get(SensorSatisfactionLevel.name_color == 'green')

          caution = SensorSatisfactionValue.get(SensorSatisfactionValue.plant == plant,
                                                SensorSatisfactionValue.sensor == sensor,
                                                SensorSatisfactionValue.level == cau_gen)

          optimum = SensorSatisfactionValue.get(SensorSatisfactionValue.plant == plant,
                                                SensorSatisfactionValue.sensor == sensor,
                                                SensorSatisfactionValue.level == opt_gen)

          query = urllib.parse.urlencode({'select': 'range'})
          url = 'http://{}:2902/plants/{}/sensor/{}?{}'.format(recipient[1], message[1], message[2], query)
          with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode('utf8'))

          caution.min_value = data['yellow']['min']
          optimum.min_value = data['green']['min']
          optimum.max_value = data['green']['max']
          caution.max_value = data['yellow']['max']

          optimum.save()
          caution.save()

        elif int(message[0]) == 7:
          from mesh_network.dedicated import MeshDedicatedDispatch

          slave = Plant.get(uuid=message[1])
          target = Plant.get(uuid=message[2])

          local = Plant.get(localhost=True)
          if slave.role == str(local.uuid):
            MeshDedicatedDispatch().slave_update(1, {'uuid': target.uuid, 'ip': target.ip}, slave)

          slave.role = str(target.uuid)
          slave.save()

        self.send(50302, recipient=recipient, plant=plant)

  def remove(self, mode, sub, target, initial={}, messages=[]):
    import os
    from models.plant import Plant

    local = Plant.get(localhost=True)
    basedir = os.path.dirname(os.path.realpath(__file__))
    if mode > 2 or mode == 0:
      logger.warning('not supported mode')
    elif mode == 1:
      from tools.mesh import MeshTools
      import datetime
      import json
      from Crypto.PublicKey import RSA
      from Crypto import Random
      import re
      import random

      if sub == 1:
        MeshTools().reinit_dir(basedir + '/remove')

        if 'destination' not in initial or 'mode' not in initial:
          raise ValueError('initial not correctly provided')
        elif 'relation' not in initial['destination'] or 'uuid' not in initial['destination'] or 'ip' not in initial['destination']:
          raise ValueError('initial["target"] not correctly provided')

        else:
          initial['target'] = {'ip': target.ip,
                               'uuid': str(target.uuid)}
          with open(basedir + '/remove/transaction.json', 'w') as out:
            out.write(json.dumps(initial))

        self.send(80101, plant=local, recipient=target)

      elif sub == 2:
        toolchain = MeshTools()
        toolchain.reinit_dir(basedir + '/remove')

        information = {'target': {'uuid': target[0],
                                  'ip': target[1]},
                       'token': {'content': toolchain.random_string(100, digits=True),
                                 'uses': 0,
                                 'created_at': datetime.datetime.now().timestamp()}}
        with open(basedir + '/remove/transaction.json', 'w') as out:
          out.write(json.dumps(information))

        self.send(80102, plant=local, recipient=target, messages=[information['token']['content']])

      elif sub == 3:
        toolchain = MeshTools()
        random_generator = Random.new().read
        key = RSA.generate(1024, random_generator)

        public = key.publickey().exportKey('DER')

        with open(basedir + '/remove/transaction.json', 'r') as out:
          information = json.loads(out.read())

        information['key'] = {str(local.uuid): {'public': toolchain.bin2hex(public).decode(), 'private': toolchain.bin2hex(key.exportKey('DER')).decode()}}
        information['token'] = {'content': messages[0]}

        with open(basedir + '/remove/transaction.json', 'w') as out:
          out.write(json.dumps(information))

        public = information['key'][str(local.uuid)]['public']
        length = len(public)
        length = str(int(length / 3))
        public = re.findall('.{1,' + length + '}', public)
        logger.debug('generated publickey: ' + str(public))
        public.append(information['token']['content'])

        self.send(80103, plant=local, recipient=target, messages=public)

      elif sub == 4:
        toolchain = MeshTools()
        random_generator = Random.new().read
        key = RSA.generate(1024, random_generator)

        public = key.publickey().exportKey('DER')

        with open(basedir + '/remove/transaction.json', 'r') as out:
          information = json.loads(out.read())

        information['key'] = {str(local.uuid): {'public': toolchain.bin2hex(public).decode(),
                                                'private': toolchain.bin2hex(key.exportKey('DER')).decode()},
                              target[0]: {'public': ''.join(messages[:-1])}}

        if information['token']['content'] == messages[-1] and information['target']['uuid'] == target[0] and information['target']['ip'] == target[1]:
          information['token']['uses'] += 1
        else:
          logger.warning('not right machine')
          raise ValueError('not right machine')

        with open(basedir + '/remove/transaction.json', 'w') as out:
          out.write(json.dumps(information))

        public = information['key'][str(local.uuid)]['public']
        length = len(public)
        length = str(int(length / 4))
        public = re.findall('.{1,' + length + '}', public)
        logger.debug('generated publickey: ' + str(public))

        self.send(80104, plant=local, recipient=target, messages=public)

      elif sub == 5:
        with open(basedir + '/remove/transaction.json', 'r') as out:
          information = json.loads(out.read())
        information['key'][target[0]] = {'public': ''.join(messages)}

        if target[0] != information['target']['uuid'] or target[1] != information['target']['ip']:
          logger.warning('not locked')
          raise ValueError('not locked')

        with open(basedir + '/remove/transaction.json', 'w') as out:
          out.write(json.dumps(information))

        self.send(80105, plant=local, recipient=target, messages=[information['token']['content']])

      elif sub == 6:
        toolchain = MeshTools()
        with open(basedir + '/remove/transaction.json', 'r') as out:
          information = json.loads(out.read())

        if information['token']['content'] == messages[0] and information['target']['uuid'] == target[0] and information['target']['ip'] == target[1]:
          information['token']['uses'] += 1
        else:
          logger.warning('not right machine')
          raise ValueError('not right machine')

        public = toolchain.hex2bin(information['key'][target[0]]['public'].encode())
        crypter = RSA.importKey(public)

        token = toolchain.random_string(100, digits=True)
        information['token'] = {'content': token,
                                'uses': 0,
                                'created_at': datetime.datetime.now().timestamp()}

        token = crypter.encrypt(token.encode(), 'x')[0]
        token = toolchain.bin2hex(token).decode()
        length = len(token)
        length = str(int(length / 4))
        token = re.findall('.{1,' + length + '}', token)
        if len(token) > 4:
          token[3] = ''.join(token[3:])
        token = token[:4]

        with open(basedir + '/remove/transaction.json', 'w') as out:
          out.write(json.dumps(information))

        self.send(80106, plant=local, recipient=target, messages=token)

      elif sub == 7:
        # decrypt token
        # insert token
        # insert port
        # encrypt port
        # send

        toolchain = MeshTools()
        with open(basedir + '/remove/transaction.json', 'r') as out:
          information = json.loads(out.read())

        if target[0] != information['target']['uuid'] or target[1] != information['target']['ip']:
          raise ValueError('not locked')

        private = information['key'][str(local.uuid)]['private']
        private = MeshTools().hex2bin(private.encode())
        crypter = RSA.importKey(private)

        token = toolchain.hex2bin(''.join(messages).encode())
        token = crypter.decrypt(token).decode()

        port = random.randint(6005, 6101)
        uport = deepcopy(port)
        information['token']['content'] = token
        information['port'] = port

        public = information['key'][target[0]]['public']
        public = toolchain.hex2bin(public.encode())
        crypter = RSA.importKey(public)

        with open(basedir + '/remove/transaction.json', 'w') as out:
          out.write(json.dumps(information))

        port = crypter.encrypt(str(port).encode(), 'x')[0]
        port = toolchain.bin2hex(port).decode()
        length = len(port)
        length = str(int(length / 3))
        port = re.findall('.{1,' + length + '}', port)
        if len(port) > 3:
          port[2] = ''.join(port[2:])
        port = port[:3]
        port.append(information['token']['content'])

        self.send(80107, plant=local, recipient=target, messages=port)

        private = information['key'][str(local.uuid)]['private']
        private = toolchain.hex2bin(private.encode())
        crypter = RSA.importKey(private)

        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        host = '0.0.0.0'
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        client.bind((host, uport))
        for _ in range(3):
          try:
            received = client.recvfrom(65000)
            received = list(received)

            message = b''
            for partial in received[0].decode().split('-'):
              partial = toolchain.hex2bin(partial.encode())
              message += crypter.decrypt(partial)

            received[0] = deepcopy(message.decode())
            received[0] = received[0].encode()

            self.daemon_process(received)
          except Exception as e:
            logger.warning(e)

      elif sub == 8:
        toolchain = MeshTools()
        with open(basedir + '/remove/transaction.json', 'r') as out:
          information = json.loads(out.read())

        if information['token']['content'] == messages[-1] and information['target']['uuid'] == target[0] and information['target']['ip'] == target[1]:
          information['token']['uses'] += 1
        else:
          logger.warning('not right machine')
          raise ValueError('not right machine')

        private = information['key'][str(local.uuid)]['private']
        private = MeshTools().hex2bin(private.encode())
        crypter = RSA.importKey(private)

        port = toolchain.hex2bin(''.join(messages[:-1]).encode())
        port = crypter.decrypt(port).decode()
        port = int(port)
        information['port'] = port

        with open(basedir + '/remove/transaction.json', 'w') as out:
          out.write(json.dumps(information))

        self.send(80108, plant=local, recipient=target, encryption=True, publickey=information['key'][target[0]]['public'], port=port)

        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        host = '0.0.0.0'
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        client.bind((host, port))
        for _ in range(2):
          try:
            received = client.recvfrom(65000)
            received = list(received)

            message = b''
            for partial in received[0].decode().split('-'):
              partial = toolchain.hex2bin(partial.encode())
              message += crypter.decrypt(partial)

            received[0] = deepcopy(message.decode())
            received[0] = received[0].encode()

            self.daemon_process(received)
          except Exception as e:
            logger.warning(e)

      elif sub == 9:
        with open(basedir + '/remove/transaction.json', 'r') as out:
          information = json.loads(out.read())

        if target[0] != information['target']['uuid'] or target[1] != information['target']['ip']:
          raise ValueError('not locked')

        self.send(80109, plant=local, recipient=target, encryption=True,
                  publickey=information['key'][target[0]]['public'], port=information['port'],
                  messages=[information['mode'], information['destination']['uuid'], information['destination']['relation'], information['token']['content']])

      elif sub == 10:
        toolchain = MeshTools()

        with open(basedir + '/remove/transaction.json', 'r') as out:
          information = json.loads(out.read())

        if information['token']['content'] == messages[-1] and information['target']['uuid'] == target[0] and information['target']['ip'] == target[1]:
          information['token']['uses'] += 1
        else:
          logger.warning('not right machine')
          raise ValueError('not right machine')

        information['mode'] = messages[0]
        information['destination'] = {}
        information['destination']['uuid'] = messages[1]
        information['destination']['relation'] = messages[2]

        token = toolchain.random_string(100, digits=True)
        information['token'] = {'content': token,
                                'uses': 0,
                                'created_at': datetime.datetime.now().timestamp()}

        with open(basedir + '/remove/transaction.json', 'w') as out:
          out.write(json.dumps(information))

        self.send(80110, plant=local, recipient=target, encryption=True,
                  publickey=information['key'][target[0]]['public'], port=information['port'],
                  messages=[token])

      elif sub == 11:
        with open(basedir + '/remove/transaction.json', 'r') as out:
          information = json.loads(out.read())

        if target[0] != information['target']['uuid'] or target[1] != information['target']['ip']:
          raise ValueError('not locked')

        information['token']['content'] = messages[0]

        self.send(80111, plant=local, recipient=target, encryption=True,
                  publickey=information['key'][target[0]]['public'], port=information['port'],
                  messages=[messages[0]])

      elif sub == 12:
        with open(basedir + '/remove/transaction.json', 'r') as out:
          information = json.loads(out.read())

        if information['token']['content'] == messages[0] and information['target']['uuid'] == target[0] and information['target']['ip'] == target[1]:
          information['token']['uses'] += 1
        else:
          logger.warning('not right machine')
          raise ValueError('not right machine')

        logger.info(information)
        if information['mode'] == 'remove':
          from models.plant import Plant
          plant = Plant.get(uuid=information['destination']['uuid'])
          if plant.localhost:
            from settings.database import DATABASE_NAME
            import os
            if os.path.isdir('/local/backup'):
              for file in os.listdir('/local/backup'):
                os.remove('/local/backup/' + file)

            os.remove(DATABASE_NAME)

            from subprocess import call
            call(["reboot"])
          else:
            if plant.role != 'master' and plant.role == str(Plant.get(localhost=True).uuid):
              self.remove(2, 1, plant)

            for slave in list(Plant.select().where(Plant.role == str(plant.uuid))):
              slave.role = information['target']['uuid']
              slave.save()

            from models.sensor import SensorData, SensorStatus, SensorCount, SensorSatisfactionValue, SensorDataPrediction
            from models.plant import PlantNetworkUptime
            for model in [SensorData, SensorStatus, SensorCount, SensorSatisfactionValue, SensorDataPrediction, PlantNetworkUptime]:
              model.delete().where(model.plant == plant).execute()
            plant.delete_instance()

        elif information['mode'] == 'activate':
          plant.active = True
          plant.save()

        elif information['mode'] == 'deactivate':
          plant.active = False
          plant.save()
        else:
          logger.info('missed')

        self.send(80112, plant=local, recipient=target, encryption=True,
                  publickey=information['key'][target[0]]['public'], port=information['port'],
                  messages=['done'])
      elif sub == 13:
        self.send_local(1, 1)

    elif mode == 2:
      from tools.mesh import MeshTools
      import json

      if sub == 1:
        MeshTools().reinit_dir(basedir + '/remove')

        initial['target'] = {'ip': target.ip,
                             'uuid': str(target.uuid)}

        with open(basedir + '/remove/transaction.json', 'w') as out:
          out.write(json.dumps(initial))

        self.send(80201, recipient=target, plant=local)
      elif sub == 3:
        with open(basedir + '/remove/transaction.json', 'r') as out:
          information = json.loads(out.read())

        if target[0] != information['target']['uuid'] or target[1] != information['target']['ip']:
          raise ValueError('not locked')

        information['token'] = {}
        information['token']['content'] = messages[0]

        with open(basedir + '/remove/transaction.json', 'w') as out:
          out.write(json.dumps(information))

        self.send(80203, recipient=target, plant=local, messages=[messages[0]])
      elif sub == 5:
        with open(basedir + '/remove/transaction.json', 'r') as out:
          information = json.loads(out.read())

        if target[0] != information['target']['uuid'] or target[1] != information['target']['ip']:
          raise ValueError('not locked')

        self.send(80205, recipient=target, plant=local, messages=[information['token']['content']])
      elif sub == 7:
        with open(basedir + '/remove/transaction.json', 'r') as out:
          information = json.loads(out.read())

        if target[0] != information['target']['uuid'] or target[1] != information['target']['ip']:
          raise ValueError('not locked')

        information['token'] = {}
        information['token']['content'] = messages[0]

        with open(basedir + '/remove/transaction.json', 'w') as out:
          out.write(json.dumps(information))

        self.send(80207, recipient=target, plant=local, messages=[messages[0]])
      elif sub == 9:
        self.send_local(1, 1)

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
    logger.info('nothing selected, starting daemon')

    def startup():
      try:
        MeshNetwork().daemon()
      except KeyboardInterrupt as e:
        logger.info('Bye!')
      except Exception as e:
        logger.error(e)
        return startup()
    startup()
