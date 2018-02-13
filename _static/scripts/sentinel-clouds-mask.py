#!/usr/bin/env python

#%module
#% description: Creates raster mask maps based on clouds mask features.
#%end
#%option G_OPT_F_OUTPUT
#%end

import sys
import os
from datetime import datetime, timedelta

import grass.script as gs

from grass.pygrass.gis import Mapset
from grass.pygrass.modules import Module

def main():
    mapset = Mapset()
    mapset.current()

    with open(options['output'], 'w') as fd:
        for vect in mapset.glist('vector', pattern='*MSK_CLOUDS'):
            items = vect.split('_')
            d = datetime.strptime(items[1], '%Y%m%dT%H%M%S')
            ## workaround
            dd = d + timedelta(seconds=1)

            Module('r.mask', vector=vect, flags='i')
            Module('g.rename', raster=['MASK', vect])
            fd.write("{0}|{1}|{2}{3}".format(
                vect,
                d.strftime('%Y-%m-%d %H:%M:%S'),
                dd.strftime('%Y-%m-%d %H:%M:%S'),
                os.linesep))
        
    return 0

if __name__ == "__main__":
    options, flags = gs.parser()
    
    sys.exit(main())
