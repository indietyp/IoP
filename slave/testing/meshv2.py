import socket
import select

DNS_HEADER_LENGTH = 12
IP = '192.168.178.49'

direct = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
direct.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
direct.bind(('0.0.0.0', 4012))
direct.setblocking(False)

multicast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
multicast.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
multicast.bind(('224.0.0.1', 4012))
multicast.setblocking(False)

dns = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dns.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
dns.bind(('0.0.0.0', 53))
dns.setblocking(False)

socks = [direct, multicast, dns]
while True:
    ready, _, _ = select.select(socks, [], [])
    for sock in ready:
        data, addr = sock.recvfrom(2048)
        # DNSHandler(sock, (data, addr)).handle()
        print("received message:", data)
        print("received address:", addr)
