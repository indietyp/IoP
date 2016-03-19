import socket
import time
import sys
import array
import logging
import pymongo

from daemonize import Daemonize
from pymongo import MongoClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False
fh = logging.FileHandler("/tmp/response_daemon.log", "w")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
keep_fds = [fh.stream.fileno()]

def response_daemon():
    INIT = {'MM': 1, 'MS': 2}
    MODE = {'ALIVE': 1, 'SEND': 2, 'REGISTER': 3, 'SUCCESS': 254, 'FAIL': 255}

    ALIVE = {'ASK': {'ASK': 1, 'ALIVE': 2}}
    SEND  = {'STATE': {'REQUEST': 1, 'SEND': 2}, 'SENSOR': {'TEMPERATURE': 1, 'HUMIDITY': 2, 'LIGHT': 3, 'MOISTURE': 4}}
    REGISTER = {'PROCESS': {'MULTICAST': 1, 'SEND': 2, 'SIGNAL': 3, 'CHECK': 4}}


    socketLocal = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socketLocal.connect(('8.8.8.8', 80))
    LOCALHOST = socketLocal.getsockname()[0]
    socketLocal.close()

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    multicast_addr = '224.0.0.1'
    host = '0.0.0.0'
    port = 4012
    membership = socket.inet_aton(multicast_addr) + socket.inet_aton(host)

    client.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    client.bind((host, port))

    while True:
      receivedData = client.recvfrom(1024)
      data = array.array('B')
      data.fromstring(receivedData[0])

      answer = False
      redirect = False

      if data[0] == INIT['MM']:

        if data[1] == MODE['ALIVE']:

          if data[2] == ALIVE['ASK']['ASK']:
            returnData = [INIT['MM'], MODE['ALIVE'], ALIVE['ASK']['ALIVE'], 0, 0]
            answer = True

          if data[2] == ALIVE['ASK']['ALIVE']:
            ipAdress = receivedData[1][0].split('.')
            ipAdress = [int(i) for i in ipAdress]
            returnData = [INIT['MM'], MODE['ALIVE']] + ipAdress
            redirect = True

        elif data[1] == MODE['REGISTER']:

          if data[2] == REGISTER['PROCESS']['MULTICAST']:
            if receivedData[1][0] != LOCALHOST:
              dbClient = MongoClient()
              db = dbClient.pot
              plant = db.Plant.find_one({'ip': receivedData[1][0]})
              if plant == None:
                STATUS = 1
              else:
                STATUS = 203

              returnData = [INIT['MM'], MODE['REGISTER'], REGISTER['PROCESS']['SEND'], STATUS]
              answer = True;

          if data[2] == REGISTER['PROCESS']['SEND']:
            ipAdress = receivedData[1][0].split('.')
            ipAdress = [int(i) for i in ipAdress]
            returnData = [INIT['MM'], MODE['REGISTER']] + ipAdress
            redirect = True

          if data[2] == REGISTER['PROCESS']['SIGNAL']:
            dbClient = MongoClient()
            db = dbClient.pot
            plant = db.Plant.find_one({'ip': receivedData[1][0]})
            if plant != None:
              if plant['name'] != None:
                STATUS = 1
              else:
                STATUS = 211
            else:
              STATUS = 212

            returnData = [INIT['MM'], MODE['REGISTER'], REGISTER['PROCESS']['CHECK'], STATUS]
            answer = True;

          if data[2] == REGISTER['PROCESS']['CHECK']:
            returnData = [INIT['MM'], MODE['REGISTER'], 100]
            redirect = True

          if data[2] == MODE['SUCCESS']:
            print('HAI')
            # MAIL TO ADMIN! (planned)

      elif data[0] == INIT['MS']:
        # TO BE CONTINUED (Facharbeit?)
        if data[1] == MODE['ALIVE']:

          if data[2] == ALIVE['ASK']['ASK']:
            returnData = [INIT['MS'], MODE['ALIVE'], ALIVE['ASK']['ALIVE'], 0, 0]
            answer = True

          if data[2] == ALIVE['ASK']['ALIVE']:
            ipAdress = receivedData[1][0].split('.')
            ipAdress = [int(i) for i in ipAdress]
            returnData = [INIT['MS'], MODE['ALIVE']] + ipAdress
            redirect = True

        if data[1] == MODE['SEND']:

          if data[2] == SEND['STATE']['REQUEST']:
            # GOT REQUEST
            print('Hi')
          if data[2] == SEND['STATE']['SEND']:
            # GOT DATA
            print('Ho')
        # VALUE REQUEST
        # GET VALUE

        # REGISTER
        # GET VALUES AND ENTRY, NOT LET ARDUINO DO!
        # NEED:
        #   MODE, NAME

        # FETCH multicast
        # ASK mode
        # ASK name
        # INSERT IN DATABASE
        # SEND MAIL to admin


        # NEW RESPONSIBLE FIELD: ADMIN

        # GET, RESPONSE, CHECK

        # TO BE CONTINUED

        # ASK IF IN DATABASE
        # TRUE OR FALSE
        # IF TRUE NOT PROCEED
        # IF FALSE PROCEED REGISTER

      if answer:
        localClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        localHost = receivedData[1][0]
        localPort = 4012

        localClient.sendto(bytes(returnData), (localHost, localPort))
        localClient.close()

      if redirect:
        localClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        localHost = '127.0.0.1'
        localPort = 2311

        localClient.sendto(bytes(returnData), (localHost, localPort))
        localClient.close()

if __name__ == "__main__":
  daemon = Daemonize(app='response_daemon', pid='/tmp/response_daemon.pid', action='response_daemon')
  if len(sys.argv) == 2:
          if 'start' == sys.argv[1]:
                  daemon.start()
          elif 'stop' == sys.argv[1]:
                  daemon.exit()
          elif 'restart' == sys.argv[1]:
                  daemon.exit()
                  daemon.start()
          else:
                  print("Unknown command")
                  sys.exit(2)
          sys.exit(0)
  else:
          print("usage: %s start|stop|restart").format(sys.argv[0])
          sys.exit(2)

