#!/bin/bash

sudo apt -y install geany
cd /home/user/pywps-flask
sudo pip install -e git+https://github.com/geopython/pywps.git@master#egg=pywps-dev
