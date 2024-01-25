#!/usr/bin/env python3
#
##############################################################################
#
# MODULE:       ndvi-v3
#
# AUTHOR(S):    martin
#
# PURPOSE:      NDVI computation version 3.
#
# DATE:         Tue Jan 23 23:39:32 2024
#
##############################################################################

# %module
# % description: NDVI computation version 3.
# %end
# %option
# % key: aoi
# % description: Area of interest
# % required: yes
# % type: string
# % key_desc: name
# % answer: jena_boundary
# %end
# %option
# % key: area_limit
# % description: Value option that sets the area size limit (in hectares)
# % required: yes
# % type: double
# % answer: 0.16
# %end

import sys
import os
import atexit
from subprocess import PIPE

from grass.script import parser, parse_key_val
from grass.pygrass.modules import Module

def cleanup():
    pass

def main(options, flags):
    Module("v.overlay",
           overwrite=True,
           ainput=options["aoi"],
           alayer="1",
           atype="auto",
           binput="MaskFeature",
           blayer="1",
           btype="area",
           operator="not",
           output="region_mask",
           olayer=['1', '0', '0'],
           snap=1e-8)

    Module("g.region",
           overwrite=True,
           vector="region_mask",
           align="L2A_T32UPB_20170706T102021_B04_10m")

    Module("r.mask",
           overwrite=True,
           maskcats="*",
           vector="region_mask",
           layer="1")

    Module("i.vi",
           overwrite=True,
           output="ndvi",
           viname="ndvi",
           red="L2A_T32UPB_20170706T102021_B04_10m@PERMANENT",
           nir="L2A_T32UPB_20170706T102021_B08_10m@PERMANENT",
           storage_bit=8)

    Module("r.recode",
           overwrite=True,
           input="ndvi",
           output="ndvi_class",
           rules="/home/martin/git/gismentors/grass-gis-workshop-jena/_static/models/reclass.txt")

    Module("r.reclass.area",
           overwrite=True,
           input="ndvi_class",
           output="ndvi_class_area",
           value=options["area_limit"],
           mode="greater",
           method="reclass")

    Module("r.grow.distance",
           overwrite=True,
           input="ndvi_class_area",
           value="ndvi_class_filled",
           metric="euclidean")

    Module("r.colors",
           map="ndvi_class_filled",
           rules="/home/martin/git/gismentors/grass-gis-workshop-jena/_static/models/colors.txt",
           offset=0,
           scale=1)

    m = Module('r.univar', flags='g', map='ndvi', stdout_=PIPE)
    stats = parse_key_val(m.outputs.stdout)
    print('-' * 80)
    print('NDVI value statistics')
    print('-' * 80)
    print('NDVI min value: {0:.4f}'.format(float(stats['min'])))
    print('NDVI max value: {0:.4f}'.format(float(stats['max'])))
    print('NDVI mean value: {0:.4f}'.format(float(stats['mean'])))

    print ('-' * 80)
    print ('NDVI class statistics')
    print ('-' * 80)
    ret = Module('r.stats', input='ndvi_class_filled', flags='ian', stdout_=PIPE)
    for line in ret.outputs.stdout.splitlines():
        # parse line (eg. 1 2737300.000000)
        data = line.split(' ')
        cat = data[0]
        area = float(data[-1])
        print('NDVI class {0}: {1:.1f} ha'.format(cat, area/1e4)) 

    print ('-' * 80)
    # we need integer map
    Module('r.mapcalc', expression='ndvi_class_filled_i = int(ndvi_class_filled)')
    Module('r.to.vect', flags='v', input='ndvi_class_filled_i', output='ndvi_class_filled', type='area')

    Module('v.rast.stats', flags='c', map='ndvi_class_filled', raster='ndvi',
           column_prefix='ndvi', method=['minimum','maximum','average'])
    # v.db.select: don't print column names (-c)
    ret = Module('v.db.select', flags='c', map='ndvi_class_filled', separator='comma', stdout_=PIPE)
    for line in ret.outputs.stdout.splitlines():
        # parse line (eg. 1,,-0.433962264150943,0.740350877192983,0.051388909449992)
        cat,label,min,max,mean = line.split(',')
        print ('NDVI class {0}: {1:.4f} (min) {2:.4f} (max) {3:.4f} (mean)'.format(
        cat, float(min), float(max), float(mean)))
    
    return 0

if __name__ == "__main__":
    options, flags = parser()
    atexit.register(cleanup)
    os.environ["GRASS_OVERWRITE"] = "1"
    sys.exit(main(options, flags))
