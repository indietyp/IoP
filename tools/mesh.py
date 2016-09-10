import string
import binascii
import os
import shutil
import random


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


if __name__ == '__main__':
  print(MeshTools().random_string(100, True, '$^%@'))
