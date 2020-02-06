#!/bin/bash

sudo apt -y install git \
     autoconf2.13 \
     autotools-dev \
     bison \
     flex \
     graphviz \
     libblas-dev \
     libbz2-dev \
     libcairo2-dev \
     libfftw3-dev \
     libfreetype6-dev \
     libgdal-dev \
     libgeos-dev \
     libglu1-mesa-dev \
     libjpeg-dev \
     liblapack-dev \
     libmotif-dev \
     libmysqlclient-dev \
     libncurses5-dev \
     libnetcdf-dev \
     libpng-dev \
     libpq-dev \
     libproj-dev \
     libreadline-dev \
     libsqlite3-dev \
     libtiff-dev \
     libwxgtk3.0-dev \
     libxmu-dev \
     netcdf-bin \
     proj-bin \
     python3 \
     python3-dev \
     python3-numpy \
     python3-pil \
     python3-ply \
     python3-wxgtk4.0 \
     unixodbc-dev \
     zlib1g-dev \
     python3-ply \
     python3-flask \
     geany \
     subversion \
     mc \
     python3-sphinx


sudo pip install pymodis sentinelsat pandas pywps

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
./grass-install.sh

# build materials
(cd /opt/grass-gis-workshop-jena; make html)

# Desktop links
dir="/home/user/Desktop/GRASS Jena Workshop"
mkdir $dir
chown user:user $dir
cd $dir
ln -s /home/user/pywps-flask .
ln -s /opt/grass-gis-workshop-jena/_build/html/index.html .
ln -s /home/user/geodata .

cp jena-update.sh /home/user/bin/

exit 0
