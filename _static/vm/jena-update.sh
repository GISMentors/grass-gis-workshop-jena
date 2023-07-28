#!/bin/bash

cd /opt/grass-gis-workshop-jena
sudo git pull

cd _static/vm/
# update GRASS & teaching materials
sudo bash postinstall.sh

# update GRASS extensions
grass79 --tmp-location EPSG:4326 --exec bash grass-addons.sh

exit 0
