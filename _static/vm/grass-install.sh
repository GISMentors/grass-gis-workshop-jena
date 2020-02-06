#!/bin/bash

function configure_grass {
    ./configure \
        --prefix=/usr/local \
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
        --with-mysql-includes=$(mysql_config --include | sed -e 's/-I//') \
        --with-netcdf \
        --with-nls \
        --with-odbc \
        --with-postgres \
        --with-postgres-includes=$(pg_config --includedir) \
        --with-proj-share=/usr/share/proj \
        --with-python \
        --with-readline \
        --with-sqlite \
        --with-wxwidgets=/usr/bin/wx-config \
        --with-x \
        --with-liblas \
        --with-openmp
}

# GRASS 7.9
cd /opt
if [ ! -d grass ] ; then
    git clone https://github.com/landam/grass.git
    (cd grass; git checkout jena-workshop; git pull)
else
    (cd grass ; git pull)
fi
cd grass
make distclean
configure_grass
make
ln -sf /opt/grass/bin.x86_64-pc-linux-gnu/grass79 /home/user/bin

exit 0
