from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

LOGLEVEL = WARNING

PATH = '/var/log/iop/'
LOCATIONS = {
    'exception': PATH + 'exception.log',
    'mesh': PATH + 'mesh.log',
    'sensor_scripts': PATH + 'sensor_daemon.log'
}
