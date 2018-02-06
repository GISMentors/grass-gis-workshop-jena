#!/bin/bash

sudo apt install subversion \
     autoconf2.13 \
     autotools-dev \
     bison \
     debhelper (>= 9) \
     dh-python \
     doxygen \
     fakeroot \
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
     lesstif2-dev \
     libmysqlclient-dev \
     libncurses5-dev \
     libnetcdf-dev \
     libpng-dev \
     libpq-dev \
     libproj-dev \
     libreadline-dev \
     libsqlite3-dev \
     libtiff-dev \
     libwxgtk2.8-dev \
     libxmu-dev \
     netcdf-bin \
     proj-bin \
     python \
     python-dev \
     python-numpy \
     python-pil \
     python-ply \
     python-wxgtk2.8 \
     unixodbc-dev \
     zlib1g-dev

sudo pip install pymodis sentinelsat pandas

function configure_grass {
    ./configure \
        --prefix=/usr/lib \
        --enable-largefile \
        --enable-socket \
        --enable-shared \
        --with-blas \
        --with-bzlib \
        --with-cairo \
        --with-cxx \
        --with-freetype \
        --with-freetype-includes=/usr/include/freetype2 \
        --with-gdal \
        --with-geos \
        --with-lapack \
        --with-motif \
        --with-mysql \
        --with-mysql-includes=$(shell mysql_config --include | sed -e 's/-I//') \
        --with-netcdf \
        --with-nls \
        --with-odbc \
        --with-postgres \
        --with-postgres-includes=$(shell pg_config --includedir) \
        --with-proj-share=/usr/share/proj \
        --with-python \
        --with-readline \
        --with-sqlite \
        --with-wxwidgets=/usr/bin/wx-config \
        --with-x
}

# GRASS 7.4
mkdir src
cd src

# wget https://grass.osgeo.org/grass74/source/grass-7.4.0.tar.gz
# tar xvzf grass-7.4.0.tar.gz
# cd grass-7.4.0
# configure_grass
# make
# sudo make install
# rm -rf grass-7.4.0

# # GRASS trunk
# svn
# cd grass7_trunk

exit 0
