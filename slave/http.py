def server():
  import socket
  import network
  sta_if = network.WLAN(network.STA_IF)
  active = sta_if.active()

  if not active:
    sta_if.active(True)
  networks = sta_if.scan()
  if not active:
    sta_if.active(False)
  networks = [x[0].decode() for x in networks]
  html_networks = """"""

  for nw in networks:
   html_networks += """<option value="{}">{}</option>""".format(nw, nw)

  html = """<!DOCTYPE html>
  <html>
     <head>
       <title>Network Configuration</title>
     </head>
     <body>
       {}
     </body>
  </html>"""

  main = """<h1>please select the network you desire and enter the password</h1>
         <form action="/update" method="post">
           Network Name:<br>
           <select name="ssid">{}</select><br />
           Last name:<br />
           <input type="password" name="password"><br /><br />
           <input type="submit" value="Submit">
         </form>""".format(html_networks)

  blocked = """sry! That's not what I want"""

  addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

  s = socket.socket()
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  s.bind(addr)
  s.listen(1)

  print('listening on', addr)

  def unescape(string):
    index = string.find("%")
    if index == -1:
      string = string.replace('[PERCENT]', '%')
      return string
    else:
      import ubinascii
      replacement = ubinascii.unhexlify(string[index + 1:index + 3]).decode()
      if replacement == '%':
        replacement = '[PERCENT]'
      string = string.replace(string[index:index + 3], replacement)
      return unescape(string)

  def whitelist(request):
    if len(list(request.keys())) > 0:
      whitelist = ['/', '/update']
      if request['path'] in whitelist:
        code = '200 OK'
        whitelisted = True
      else:
        code = '406 Not Acceptable'
        whitelisted = False
    else:
      code = '406 Not Acceptable'
      whitelisted = False

    return code, whitelisted

  while True:
    cl, addr = s.accept()
    print('client connected from', addr)
    data = b''

    while True:
      data += cl.recv(1024)
      if data.find(b'\r\n\r\n') != -1:
        break

    data = data.split(b'\r\n')
    data = [x.decode() for x in data if x != b'']
    request = {}

    if data[0][:3] == 'GET':
      request['mode'] = 'get'
      request['path'] = data[0][3:].split(' ')[1]
    elif data[0][:4] == 'POST':
      request['mode'] = 'post'
      request['path'] = data[0][4:].split(' ')[1]

    if request['mode'] == 'post':
      print(data[-1])

    bound = len(data) if request['mode'] == 'get' else len(data) - 1
    for line in data[1:bound]:
      line = line.split(': ')
      request[line[0].lower()] = line[1]
    print(request)

    code, whitelisted = whitelist(request)

    if request['path'] == '/update' and request['mode'] == 'post':
      print('processing update')
      credentials = {}
      raw = data[-1].split('&')
      print(raw)
      for information in raw:
        info = information.split('=')
        info = [unescape(x.replace('+', ' ')) for x in info]
        credentials[info[0]] = info[1]

      if len(list(credentials.keys())) == 2:
        if 'ssid' in credentials.keys() and 'password' in credentials.keys():
          import json
          with open('credentials.json', 'w') as out:
            out.write(json.dumps(credentials))

          import machine
          machine.reset()

        else:
          whitelisted = False
          code = '400 Bad Request'
      else:
        whitelisted = False
        code = '400 Bad Request'

    body = html
    if whitelisted:
      body = body.format(main)
    else:
      body = body.format(blocked)

    headers = [
        'HTTP/1.1 {}'.format(code),
        'Content-Type: text/html; encoding=utf8',
        # 'Content-Length: {}'.format(len(body)),
        'Connection: close']
    headers = '\n'.join(headers)

    print(code)
    body = headers + '\n\n' + body
    cl.sendall(body.encode())

    cl.close()
