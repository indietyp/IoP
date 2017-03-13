echo "Installing main programming language"
# python3
apt install -y python3 python3-dev python3-pip

echo "Installing crypto requirements"
# cryptography, pycrypto
apt install -y build-essential libssl-dev libffi-dev

echo "Installing NumPy requirements"
# numpy requirements
apt install -y build-essential gfortran libatlas-base-dev libatlas3gf-base libjpeg-dev libxml2-dev libfreetype6-dev libpng-dev


echo "Installing python3 packages"
# required python packages
pip3 install -r requirements.txt
