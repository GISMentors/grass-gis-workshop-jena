#!/usr/bin/env python3

#%module
#% description: Creates raster mask maps based on clouds mask features.
#%end
#%option G_OPT_V_MAP
#% description: Name of AOI vector map
#%end
#%option G_OPT_STRDS_INPUT
#% description: Name of input 4th band space time raster dataset
#%end
#%option G_OPT_F_OUTPUT
#%end

import sys
import os
from datetime import datetime, timedelta

import grass.script as gs

from grass.pygrass.gis import Mapset
from grass.pygrass.modules import Module
from grass.pygrass.vector import VectorTopo
from grass.pygrass.utils import copy
import grass.temporal as tgis

def main():
    mapset = Mapset()
    mapset.current()

    tgis.init()
    sp4 = tgis.open_old_stds(options['input'], 'raster')
    
    with open(options['output'], 'w') as fd:
        for t_item in sp4.get_registered_maps(columns='name,start_time'):
            items = t_item[0].split('_')
            d = t_item[1]

            vect = '{}_{}_MSK_CLOUDS'.format(items[0], items[1])
            mask_vect = '{}_{}'.format(vect, options['map'].split('@')[0])
            n_clouds = 0
            with VectorTopo(vect) as v:
                if v.exist():
                    n_clouds = v.num_primitive_of('centroid')
            if n_clouds > 0:
                Module('v.overlay', ainput=options['map'], binput=vect, operator='not',
                       output=mask_vect, overwrite=True)
            else:
                copy(options['map'], mask_vect, 'vector')
            Module('r.mask', vector=mask_vect, overwrite=True)
            Module('g.remove', flags='f', type='vector', name=mask_vect)
            Module('g.rename', raster=['MASK', mask_vect])
            fd.write("{}|{}\n".format(
                mask_vect,
                d.strftime('%Y-%m-%d %H:%M:%S.%f'),
            ))
        
    return 0

if __name__ == "__main__":
    options, flags = gs.parser()
    
    sys.exit(main())
