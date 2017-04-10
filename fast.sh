#!/bin/bash
SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

cp /local/backup/* /mnt/ramdisk
#########
cd $SCRIPTPATH/rest_api
nohup /usr/local/bin/gunicorn -w 1 --threads 12 --capture-output --pythonpath "$SCRIPTPATH" -b unix:/tmp/iop_rest.sock --log-level=debug IoP:app >> /var/log/iop/rest.log 2>&1 &
echo "started api"
sleep 120
#########
cd $SCRIPTPATH/frontend
nohup /usr/local/bin/gunicorn -w 1 --threads 12 --capture-output --pythonpath "$SCRIPTPATH" -b unix:/tmp/iop_frontend.sock --log-level=debug IoP:app >> /var/log/iop/frontend.log 2>&1 &
echo "started frontend"
