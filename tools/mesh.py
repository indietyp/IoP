import string
import binascii
import os
import shutil
import random
from Crypto.Cipher import AES
import os
import struct


class MeshTools:
  def __init__(self):
    pass

  def bin2hex(self, string):
    return binascii.hexlify(string)

  def hex2bin(self, string):
    return binascii.unhexlify(string)

  def create_dir_if_not_exists(self, directory):
    if not os.path.exists(directory):
      os.makedirs(directory)
      return True
    return False

  def delete_dir_if_exists(self, directory):
    if os.path.exists(directory):
      shutil.rmtree(directory)
      return True
    return False

  def reinit_dir(self, directory):
    self.delete_dir_if_exists(directory)
    self.create_dir_if_not_exists(directory)
    return True

  def random_string(self, length, digits=False, custom=''):
    alphabet = string.ascii_uppercase
    alphabet += string.digits if digits is True else ''
    alphabet += custom

    output = ''
    for _ in range(0, length):
      output += random.choice(alphabet)

    return output


class MeshAES:
  """ modified, but original source:
        http://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto
        [9/10/2016, 7:20pm]
  """

  def __init__(self):
    pass

  @staticmethod
  def encrypt_file(src, dst, key, iv, chunksize=64 * 1024):
    """ Encrypts file using AES (CBC) with given key and iv

        src [string]
          path to source file

        dst [string]
          path to destiny file

        key [string]
          pycrypto key, can be 16, 24 or 32 bytes long, longer -> better

        iv [string]
          salt key

        chunksize [float]
          to be readable chunk -> divisible of 16
          for not blowing memory c:
    """
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(src)

    with open(src, 'rb') as infile:
        with open(dst, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                  break
                elif len(chunk) % 16 != 0:
                  print('CHUNK')
                  chunk += (' ' * (16 - len(chunk) % 16)).encode()

                outfile.write(encryptor.encrypt(chunk))

  @staticmethod
  def decrypt_file(src, dst, key, iv, chunksize=24 * 1024):
      """ Decrypts a file using AES (CBC mode) with the
          given key. Parameters are similar to encrypt_file,
          with one difference: out_filename, if not supplied
          will be in_filename without its last extension
          (i.e. if in_filename is 'aaa.zip.enc' then
          out_filename will be 'aaa.zip')
      """

      decryptor = AES.new(key, AES.MODE_CBC, iv)
      with open(src, 'rb') as infile:
          origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]

          with open(dst, 'wb') as outfile:
              while True:
                  chunk = infile.read(chunksize)
                  if len(chunk) == 0:
                      break
                  outfile.write(decryptor.decrypt(chunk))

              outfile.truncate(origsize)

if __name__ == '__main__':
  print(MeshTools().random_string(100, True, '$^%@'))
