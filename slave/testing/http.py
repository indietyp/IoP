import socket

html = """<!DOCTYPE html>
<html>
    <head>
      <title>Network Configuration</title>
    </head>
    <body>
      {}
    </body>
</html>
"""

main = """<h1>please select the network you desire and enter the password</h1>
        <form action="/update" method="post">
          Network Name:<br>
          <input type="text" name="ssid" value="please select"><br />
          Last name:<br />
          <input type="password" name="password"><br /><br />
          <input type="submit" value="Submit">
        </form>
"""

blocked = """sry! That's not what I want"""

addr = socket.getaddrinfo('0.0.0.0', 81)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)


def unescape(string):
  index = string.find("%")
  if index == -1:
    string = string.replace('[PERCENT]', '%')
    return string
  else:
    import binascii
    replacement = binascii.unhexlify(string[index + 1:index + 3]).decode()
    if replacement == '%':
      replacement = '[PERCENT]'
    string = string.replace(string[index:index + 3], replacement)
    return unescape(string)


def whitelist(request):
  if len(request.keys()) > 0:
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
  data = cl.recv(4096)
  data = data.split(b'\r\n')
  data = [x.decode() for x in data if x is not b'']
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

  code, whitelisted = whitelist(request)

  if request['path'] == '/update' and request['mode'] == 'post':
    credentials = {}
    raw = data[-1].split('&')
    for information in raw:
      info = information.split('=')
      info = [unescape(x.replace('+', ' ')) for x in info]
      credentials[info[0]] = info[1]

    if len(credentials.keys()) == 2:
      if 'ssid' in credentials.keys() and 'password' in credentials.keys():
        import json
        with open('credentials.json', 'w') as out:
          out.write(json.dumps(credentials))

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
      'Content-Length: {}'.format(len(body)),
      'Connection: close']
  headers = '\n'.join(headers)

  body = headers + '\n\n' + body
  cl.send(body.encode())

  cl.close()
