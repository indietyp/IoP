import socket
from tools.main import MeshString


class MeshNetwork(object):
  """ response daemon for mesh network """

  def __init(self):
    pass

  def daemon(self):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    multicast_addr = '224.0.0.1'
    host = '0.0.0.0'
    port = 4012
    membership = socket.inet_aton(multicast_addr) + socket.inet_aton(host)

    client.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    client.bind((host, port))
    print(client.recvfrom(65000))

  def send(self, plant, code, messages, master=True, priority=255, recipient=None):

    len_message = len(messages)

    [messages.append('') for _ in range(0, 4 - len_message) if len_message < 4]
    [messages.pop() for _ in range(0, len_message - 4) if len_message > 4]

    messages = [x if x != '' else '-' * 256 for x in messages]

    # if len_message < 4:
    #   for _ in range(0, 4 - len_message):
    #     messages.append('')
    # elif len_message > 4:
    #   for i in range(0, len_message - 4):
    #     del messages[i + 4]

    master = int(master)
    package = [master, [], [], [], [], master]
    package[1].append(plant.uuid)

    package[2].append(priority)
    package[2].append(recipient.uuid if recipient is not None else '')

    package[3].append(code)

    package[4] = messages

    str_package = repr(package).replace('[', '<', 1)
    str_package = MeshString(str_package).rreplace(']', '>', 1).encode('utf-8')
    print(str_package)

    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = 4012
    sender.sendto(str_package, ('127.0.0.1', port))
    sender.close()

if __name__ == '__main__':
  from models.plant import Plant

  plant = Plant.get(Plant.name == 'marta')
  MeshNetwork().send(plant, 10100, ['', '', '', '', 'test'])
