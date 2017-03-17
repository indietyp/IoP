SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

echo "Installing main programming language"
# python3
apt install -y python3 python3-dev python3-pip

echo "Installing web server"
# nginx
apt install -y nginx

echo "Installing crypto requirements"
# cryptography, pycrypto
apt install -y build-essential libssl-dev libffi-dev

echo "Installing NumPy requirements"
# numpy requirements
apt install -y build-essential gfortran libatlas-base-dev libatlas3gf-base libjpeg-dev libxml2-dev libfreetype6-dev libpng-dev

echo "Installing python3 packages"
# required python packages
pip3 install -r requirements.txt

echo "creating folders necessary"
python3 $SCRIPTPATH/setup/create_folders.py

echo "appending crontab"
startup="@reboot sh $SCRIPTPATH/run.sh >> /var/log/iop/startup.log 2>&1"
periodic="*/5 * * * * sh $SCRIPTPATH/cycle.sh >> /var/log/iop/tmp_mesh.log 2>&1"
(crontab -u root -l; echo "$startup" ) | crontab -u root -
(crontab -u root -l; echo "$periodic" ) | crontab -u root -

echo "create logrotate"
cp $SCRIPTPATH/setup/logrotate /etc/logrotate.d/iop

echo "moving nginx config"
cp $SCRIPTPATH/setup/nginx-frontend /etc/nginx/sites-enabled/frontend
cp $SCRIPTPATH/setup/nginx-rest /etc/nginx/sites-enabled/rest
service nginx restart
