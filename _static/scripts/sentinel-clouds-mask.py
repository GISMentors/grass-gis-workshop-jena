#!/usr/bin/env python

#%module
#% description: Creates raster mask maps based on clouds mask features.
#%end
#%option G_OPT_V_MAP
#% description: Name of AOI vector map
#%end
#%option G_OPT_F_OUTPUT
#%end

import sys
import os
from datetime import datetime, timedelta

import grass.script as gs

from grass.pygrass.gis import Mapset
from grass.pygrass.modules import Module
from grass.pygrass.vector import Vector
from grass.pygrass.utils import copy

def main():
    mapset = Mapset()
    mapset.current()

    with open(options['output'], 'w') as fd:
        for rast in mapset.glist('raster', pattern='*_B04_10m'):
            items = rast.split('_')
            d = datetime.strptime(items[2], '%Y%m%dT%H%M%S')
            ## workaround
            dd = d + timedelta(seconds=1)

            vect = '{}_{}_MSK_CLOUDS'.format(items[1], items[2])
            mask_vect = '{}_{}'.format(vect, options['map'].split('@')[0])
            if Vector(vect).exist():
                Module('v.overlay', ainput=options['map'], binput=vect, operator='not',
                       output=mask_vect)
            else:
                copy(options['map'], mask_vect, 'vector')
            Module('r.mask', vector=mask_vect, overwrite=True)
            Module('g.remove', flags='f', type='vector', name=mask_vect)
            Module('g.rename', raster=['MASK', mask_vect])
            fd.write("{0}|{1}|{2}{3}".format(
                mask_vect,
                d.strftime('%Y-%m-%d %H:%M:%S'),
                dd.strftime('%Y-%m-%d %H:%M:%S'),
                os.linesep))
        
    return 0

if __name__ == "__main__":
    options, flags = gs.parser()
    
    sys.exit(main())
