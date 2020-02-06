#!/bin/bash -e

echo "deb-src http://ro.archive.ubuntu.com/ubuntu/ bionic universe" >> /etc/apt/sources.list
apt -y update
apt -y build-dep grass

sudo apt -y install \
     python3 \
     python3-dev \
     python3-numpy \
     python3-pil \
     python3-ply \
     python3-six \
     python3-wxgtk4.0 \
     libwxgtk3.0-gtk3-dev \
     python3-flask \
     geany \
     subversion \
     mc \
     python3-sphinx \
     python3-pip \
     liblas-dev

sudo pip3 install pymodis sentinelsat pandas pywps

# laszip
wget https://github.com/LASzip/LASzip/releases/download/v2.2.0/laszip-src-2.2.0.tar.gz
tar xvzf laszip-src-2.2.0.tar.gz
(
cd laszip-src-2.2.0/
./configure --prefix=/usr/local --includedir=/usr/local/include/laszip
make
sudo make install
)
rm -r laszip-src-2.2.0 laszip-src-2.2.0.tar.gz

# liblas
wget http://download.osgeo.org/liblas/libLAS-1.8.1.tar.bz2
tar xvjf libLAS-1.8.1.tar.bz2
(cd libLAS-1.8.1
mkdir makefiles
cd makefiles
cmake -G "Unix Makefiles" ../ -DWITH_LASZIP=YES
make
sudo make install
)
rm -r libLAS-1.8.1 libLAS-1.8.1.tar.bz2

# pywps flask
cd /home/user
git clone https://github.com/geopython/pywps-flask.git
chown user:user pywps-flask -R

# GRASS
cd /opt/grass-gis-workshop-jena/_static/vm/
bash grass-install.sh
grass79 --tmp-location EPSG:4326 --exec bash grass-addons.sh

# update script
cp jena-update.sh /home/user/bin/
chown user:user /home/user/bin/jena-update.sh
chmod +x /home/user/bin/jena-update.sh

# build materials
(cd /opt ; git clone https://github.com/gismentors/sphinx-template; cd sphinx-template; git checkout en)
(cd /opt/grass-gis-workshop-jena; make html)

# Desktop links
dir="/home/user/Desktop/GRASS Jena Workshop"
mkdir "$dir"
chown user:user "$dir"
cd "$dir"
ln -s /home/user/pywps-flask .
ln -s /opt/grass-gis-workshop-jena/_build/html/index.html .
ln -s /home/user/geodata .
cp /home/user/Desktop/Desktop\ GIS/qgis.desktop .
cp /home/user/Desktop/Desktop\ GIS/grass76.desktop grass79.desktop
sed -i 's#/usr/bin/grass76#/home/user/bin/grass79#g' grass79.desktop
sed -i 's#grass76#grass79#g' grass79.desktop

exit 0
