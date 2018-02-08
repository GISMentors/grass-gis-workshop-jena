#!/bin/bash

sudo apt install subversion \
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
     python \
     python-dev \
     python-numpy \
     python-pil \
     python-ply \
     python-wxgtk3.0 \
     unixodbc-dev \
     zlib1g-dev \
     python-ply \
    python-flask

sudo pip install pymodis sentinelsat pandas pywps

# liblas
wget https://github.com/LASzip/LASzip/releases/download/v2.2.0/laszip-src-2.2.0.tar.gz
tar xvzf laszip-src-2.2.0.tar.gz
cd laszip-src-2.2.0/
./configure --prefix=/usr/local --includedir=/usr/local/include/laszip
make
sudo make install

wget http://download.osgeo.org/liblas/libLAS-1.8.1.tar.bz2
tar xvjf libLAS-1.8.1.tar.bz2
mkdir makefiles
cd makefiles
cmake -G "Unix Makefiles" ../ -DWITH_LASZIP=YES
make
sudo make install

cd /home/user
git clone https://github.com/geopython/pywps-flask.git
chown user:user pywps-flask -R
exit 0
