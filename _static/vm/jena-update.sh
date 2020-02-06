#!/bin/bash

cd /opt/grass-gis-workshop-jena/_static/vm/

grass79 --tmp-location EPSG:4326 --exec bash grass-addons.sh

sudo bash postinstall.sh

exit 0
