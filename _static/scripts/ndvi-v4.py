#!/usr/bin/env python3
#
##############################################################################
#
# MODULE:       ndvi-v4
#
# AUTHOR(S):    martin
#
# PURPOSE:      NDVI computation version 4.
#
# DATE:         Tue Jan 23 23:39:32 2024
#
##############################################################################

# %module
# % description: NDVI computation version 4.
# %end
# %option G_OPT_V_INPUT
# % key: region
# % description: Name of input vector region map 
# %end
# %option G_OPT_V_INPUT
# % key: clouds
# % description: Name of input vector clouds map 
# %end
# %option G_OPT_R_INPUT
# % key: red
# % description: Name of input red channel
# %end
# %option G_OPT_R_INPUT
# % key: nir
# % description: Name of input NIR channel
# %end
# %option
# % key: min_area
# % description: Threshold for removing small areas in m2
# %type: integer
# % answer: 1600
# %end
# %option G_OPT_V_OUTPUT
# %end

import sys
import os
import atexit
from subprocess import PIPE

from grass.script import parser, parse_key_val
from grass.pygrass.modules import Module

def cleanup():
    Module('g.remove', flags='f', name='region_mask', type='vector')
    Module('g.remove', flags='f', name='ndvi', type='raster')
    Module('g.remove', flags='f', name='ndvi_class', type='raster')
    Module('g.remove', flags='f', name='ndvi_class_area', type='raster')
    Module('g.remove', flags='f', name='ndvi_class_filled_i', type='raster')
    Module('g.remove', flags='f', name='ndvi_class_filled', type='vector')
    
def main(options, flags):
    Module("v.overlay",
           overwrite=True,
           ainput=options["region"],
           alayer="1",
           atype="auto",
           binput=options["clouds"],
           blayer="1",
           btype="area",
           operator="not",
           output="region_mask",
           olayer=['1', '0', '0'],
           snap=1e-8)

    Module("g.region",
           overwrite=True,
           vector="region_mask",
           align=options["red"])

    Module("r.mask",
           overwrite=True,
           maskcats="*",
           vector="region_mask",
           layer="1")

    Module("i.vi",
           overwrite=True,
           output="ndvi",
           viname="ndvi",
           red=options["red"],
           nir=options["nir"],
           storage_bit=8)

    Module("r.recode",
           overwrite=True,
           input="ndvi",
           output="ndvi_class",
           rules="-",
           stdin_="-1:0.1:1\n0.1:0.5:2\n0.5:1:3")

    Module("r.reclass.area",
           overwrite=True,
           input="ndvi_class",
           output="ndvi_class_area",
           value=int(options["min_area"]) / 1e4,
           mode="greater",
           method="reclass")

    Module("r.grow.distance",
           overwrite=True,
           input="ndvi_class_area",
           value=options["output"],
           metric="euclidean")

    Module("r.colors",
           map=options["output"],
           rules="-",
           stdin_="1 grey\n2 255 255 0\n3 green",
           offset=0,
           scale=1)

    m = Module('r.univar', flags='g', map='ndvi', stdout_=PIPE)
    stats = parse_key_val(m.outputs.stdout, val_type=float)
    print('-' * 80)
    print('NDVI value statistics')
    print('-' * 80)
    print('NDVI min value: {0:.4f}'.format(stats['min']))
    print('NDVI max value: {0:.4f}'.format(stats['max']))
    print('NDVI mean value: {0:.4f}'.format(stats['mean']))

    print('-' * 80)
    print('NDVI class statistics')
    print('-' * 80)
    ret = Module('r.stats', input=options["output"], flags='ian', stdout_=PIPE)
    for line in ret.outputs.stdout.splitlines():
        # parse line (eg. 1 2737300.000000)
        data = line.split(' ')
        cat = data[0]
        area = float(data[-1])
        print('NDVI class {0}: {1:.1f} ha'.format(cat, area/1e4)) 

    print('-' * 80)
    # we need integer map
    Module('r.mapcalc', expression='ndvi_class_filled_i = int({})'.format(options['output']))
    Module('r.to.vect', flags='v', input='ndvi_class_filled_i', output='ndvi_class_filled', type='area')

    Module('v.rast.stats', flags='c', map='ndvi_class_filled', raster='ndvi',
           column_prefix='ndvi', method=['minimum','maximum','average'])
    # v.db.select: don't print column names (-c)
    ret = Module('v.db.select', flags='c', map='ndvi_class_filled', separator='comma', stdout_=PIPE)
    for line in ret.outputs.stdout.splitlines():
        # parse line (eg. 1,,-0.433962264150943,0.740350877192983,0.051388909449992)
        cat,label,min,max,mean = line.split(',')
        print('NDVI class {0}: {1:.4f} (min) {2:.4f} (max) {3:.4f} (mean)'.format(
        cat, float(min), float(max), float(mean)))
    
    return 0

if __name__ == "__main__":
    options, flags = parser()
    atexit.register(cleanup)
    os.environ["GRASS_OVERWRITE"] = "1"
    sys.exit(main(options, flags))
