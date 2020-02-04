#!/bin/sh

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
