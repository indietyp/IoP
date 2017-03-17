import subprocess
from tools.mesh import MeshTools
from settings.database import DATABASE_NAME


def create():
  toolchain = MeshTools()
  toolchain.create_dir_if_not_exists('/local/backup')
  toolchain.create_dir_if_not_exists('/var/log/iop')

  toolchain.create_dir_if_not_exists('/'.join(DATABASE_NAME.split('/')[:-1]))
  if 'mnt' in DATABASE_NAME.split('/'):
    with open('/etc/fstab', 'r') as out:
      cont = True if "# auto inserted by the iop interface" not in out.read() else False

    if cont:
      with open('/etc/fstab', 'a') as out:
        out.write("\n\n# auto inserted by the iop interface\ntmpfs           /mnt/ramdisk    tmpfs   nodev,nosuid,noexec,nodiratime,size=50M   0 0\n")
      subprocess.call(["mount", "-t", "tmpfs", "-o", "size=50m", "tmpfs", '/'.join(DATABASE_NAME.split('/')[:-1])])

if __name__ == '__main__':
  create()
