import network


class DNSHandler:
  def __init__(self, socket, data, addr):
    self.socket = socket
    self.data = data
    self.client_address = addr
    self.DNS_HEADER_LENGTH = 12

  def handle(self):
    socket = self.socket
    data = self.data.strip()

    if len(data) < self.DNS_HEADER_LENGTH:
      return

    try:
      all_questions = self.dns_extract_questions(data)
    except IndexError:
      return

    # Filter only those questions, which have QTYPE=A and QCLASS=IN
    accepted_questions = []
    for question in all_questions:
      if question['qtype'] == b'\x00\x01' and question['qclass'] == b'\x00\x01':
        accepted_questions.append(question)

    response = (
        self.dns_response_header(data) +
        self.dns_response_questions(accepted_questions) +
        self.dns_response_answers(accepted_questions)
    )
    socket.sendto(response, self.client_address)

  def dns_extract_questions(self, data):
      """
      Extracts question section from DNS request data.
      See http://tools.ietf.org/html/rfc1035 4.1.2. Question section format.
      """
      questions = []
      n = (data[4] << 8) + data[5]

      # skip id
      pointer = self.DNS_HEADER_LENGTH
      for i in range(n):
          question = {
              'name': [],
              'qtype': '',
              'qclass': '',
          }
          length = data[pointer]

          while length != 0:
              start = pointer + 1
              end = pointer + length + 1
              question['name'].append(data[start:end])
              pointer += length + 1
              length = data[pointer]

          question['qtype'] = data[pointer + 1:pointer + 3]
          question['qclass'] = data[pointer + 3:pointer + 5]

          pointer += 5
          questions.append(question)
      return questions

  def dns_response_header(self, data):
      """
      Generates DNS response header.
      See http://tools.ietf.org/html/rfc1035 4.1.1. Header section format.
      """
      header = b''
      # ID - copy it from request
      header += data[:2]
      # QR     1    response
      # OPCODE 0000 standard query
      # AA     0    not authoritative
      # TC     0    not truncated
      # RD     0    recursion not desired
      # RA     0    recursion not available
      # Z      000  unused
      # RCODE  0000 no error condition
      header += b'\x80\x00'
      # QDCOUNT - question entries count, set to QDCOUNT from request
      header += data[4:6]
      # ANCOUNT - answer records count, set to QDCOUNT from request
      header += data[4:6]
      # NSCOUNT - authority records count, set to 0
      header += b'\x00\x00'
      # ARCOUNT - additional records count, set to 0
      header += b'\x00\x00'
      return header

  def dns_response_questions(self, questions):
      """
      Generates DNS response questions.
      See http://tools.ietf.org/html/rfc1035 4.1.2. Question section format.
      """
      sections = b''
      for question in questions:
          section = b''
          for label in question['name']:
              # Length octet
              section += bytes([len(label)])
              section += label
          # Zero length octet
          section += b'\x00'
          section += question['qtype']
          section += question['qclass']
          sections += section
      return sections

  def dns_response_answers(self, questions):
      """
      Generates DNS response answers.
      See http://tools.ietf.org/html/rfc1035 4.1.3. Resource record format.
      """
      records = b''
      for question in questions:
          record = b''
          for label in question['name']:
              # Length octet
              record += bytes([len(label)])
              record += label
          # Zero length octet
          record += b'\x00'
          # TYPE - just copy QTYPE
          # TODO QTYPE values set is superset of TYPE values set, handle different QTYPEs, see RFC 1035 3.2.3.
          record += question['qtype']
          # CLASS - just copy QCLASS
          # TODO QCLASS values set is superset of CLASS values set, handle at least * QCLASS, see RFC 1035 3.2.5.
          record += question['qclass']
          # TTL - 32 bit unsigned integer. Set to 0 to inform, that response
          # should not be cached.
          record += b'\x00\x00\x00\x00'
          # RDLENGTH - 16 bit unsigned integer, length of RDATA field.
          # In case of QTYPE=A and QCLASS=IN, RDLENGTH=4.
          record += b'\x00\x04'
          # RDATA - in case of QTYPE=A and QCLASS=IN, it's IPv4 address.

          ap_if = network.WLAN(network.AP_IF)
          IP = ap_if.ifconfig()[0]
          record += b''.join(map(
              lambda x: bytes([int(x)]),
              IP.split('.')
          ))
          records += record
      return records
