#!/bin/sh

apt update
apt install libgtk-3-dev
pip3 install --upgrade wxpython==4.0.7

cd /opt

# update GRASS
(
    cd grass;
    git pull;
    make
)

# update materials
(
    cd grass-gis-workshop-jena;
    git pull;
    make html
)

exit 0
