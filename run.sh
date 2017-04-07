#!/bin/bash
SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

cp /local/backup/* /mnt/ramdisk
#########
cd $SCRIPTPATH/rest_api
nohup /usr/local/bin/gunicorn -w 1 --threads 12 --capture-output --pythonpath "$SCRIPTPATH" -b unix:/tmp/iop_rest.sock --log-level=debug IoP:app >> /var/log/iop/rest.log 2>&1 &
echo "started api"
sleep 60
#########
cd $SCRIPTPATH/mesh_network
nohup env PYTHONPATH=$SCRIPTPATH python3 daemon.py >> /var/log/iop/tmp_mesh.log 2>&1 &
echo "started daemon"
sleep 5
#########
cd $SCRIPTPATH/mesh_network
nohup env PYTHONPATH=$SCRIPTPATH python3 dedicated.py >> /var/log/iop/tmp_mesh.log 2>&1 &
echo "started mesh reboot"
sleep 5
#########
cd $SCRIPTPATH/sensor_scripts/daemon
nohup env PYTHONPATH=$SCRIPTPATH python3 main.py force >> /var/log/iop/tmp_sensor.log 2>&1 &
echo "started sensor daemon"
sleep 50
########
cd $SCRIPTPATH/frontend
nohup /usr/local/bin/gunicorn -w 1 --threads 12 --capture-output --pythonpath "$SCRIPTPATH" -b unix:/tmp/iop_frontend.sock --log-level=debug IoP:app >> /var/log/iop/frontend.log 2>&1 &
echo "started frontend"
