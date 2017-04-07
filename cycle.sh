#!/bin/bash
SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

sleep 120
cd $SCRIPTPATH/mesh_network
nohup env PYTHONPATH=$SCRIPTPATH python3 dedicated.py alive >> /var/log/iop/tmp_mesh.log 2>&1 &
sleep 10
cp /mnt/ramdisk/* /local/backup/
