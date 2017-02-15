import platform
DATABASE_NAME = '/tmp/data.db'

if platform.system() == 'Windows':
  DATABASE_NAME = 'C:\\Users\\bmahmoud\\Dropbox\\thesis\\IoP\\data.db'
elif platform.system() == 'Darwin':
  DATABASE_NAME = '/Users/admin/Dropbox/thesis/IoP/data.db'
  # DATABASE_NAME = '/local/db/data.db'
else:
  DATABASE_NAME = '/mnt/ramdisk/data.db'
  # DATABASE_NAME = '/local/db/data.db'
  # DATABASE_NAME = '/media/sf_Dropbox/thesis/IoP/data.db'
