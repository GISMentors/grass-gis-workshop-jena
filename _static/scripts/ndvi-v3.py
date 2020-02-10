#!/usr/bin/env python3
#
##############################################################################
#
# MODULE:       ndvi-v3
#
# AUTHOR(S):    martin
#
# PURPOSE:      NDVI model version 3
#
# DATE:         Sat Feb  3 15:45:35 2018
#
##############################################################################

#%module
#% description: NDVI model version 3
#%end
#%option G_OPT_V_INPUT
#% key: region
#% description: Name of input vector region map 
#%end
#%option G_OPT_V_INPUT
#% key: clouds
#% description: Name of input vector clouds map 
#%end
#%option G_OPT_R_INPUT
#% key: red
#% description: Name of input red channel
#%end
#%option G_OPT_R_INPUT
#% key: nir
#% description: Name of input NIR channel
#%end
#%option
#% key: threshold
#% description: Threshold for removing small areas
#% answer: 1600
#%end
#%option G_OPT_V_OUTPUT
#%end

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
    Module('g.remove', flags='f', name='ndvi_class', type='vector')

def main(options, flags):
    Module("v.overlay",
           overwrite = True,
           ainput = options["region"],
           alayer = "1",
           atype = "auto",
           binput = options["clouds"],
           blayer = "1",
           btype = "area",
           operator = "not",
           output = "region_mask",
           olayer = "1,0,0",
           snap = 1e-8)

    Module("g.region",
           overwrite = True,
           vector = "region_mask",
           align = options["red"])

    Module("r.mask",
           overwrite = True,
           maskcats = "*",
           vector = "region_mask",
           layer = "1")

    Module("i.vi",
           overwrite = True,
           red = options["red"],
           output = "ndvi",
           viname = "ndvi",
           nir = options["nir"],
           storage_bit = 8)

    Module("r.recode",
           overwrite = True,
           input = "ndvi",
           output = "ndvi_class",
           rules = "-",
           stdin_ = "-1:0.1:1\n0.1:0.5:2\n0.5:1:3")

    Module("r.colors",
           map = "ndvi_class",
           rules = "-",
           stdin_ = "1 grey\n2 255 255 0\n3 green")

    Module("r.to.vect",
           flags = 'sv',
           overwrite = True,
           input = "ndvi_class",
           output = "ndvi_class",
           type = "area",
           column = "value")

    Module("v.clean",
           overwrite = True,
           input = "ndvi_class",
           layer = "-1",
           type = ["point","line","boundary","centroid","area","face","kernel"],
           output = options["output"],
           tool = "rmarea",
           threshold = options["threshold"])

    ret = Module('r.univar', flags='g', map='ndvi', stdout_=PIPE)
    stats = parse_key_val(ret.outputs.stdout)
    print ('-' * 80)
    print ('NDVI value statistics')
    print ('-' * 80)
    print ('NDVI min value: {0:.4f}'.format(float(stats['min'])))
    print ('NDVI max value: {0:.4f}'.format(float(stats['max'])))
    print ('NDVI mean value: {0:.4f}'.format(float(stats['mean'])))

    print ('-' * 80)
    print ('NDVI class statistics')
    print ('-' * 80)
    ret = Module('v.report', map=options['output'], option='area', stdout_=PIPE)
    for line in ret.outputs.stdout.splitlines()[1:]: # skip first line (cat|label|area)
        # parse line (eg. 1||2712850)
        data = line.split('|')
        cat = data[0]
        area = float(data[-1])
        print ('NDVI class {0}: {1:.1f} ha'.format(cat, area/1e4)) 

    # v.to.rast: use -c flag for updating statistics if exists
    Module('v.rast.stats', flags='c', map=options['output'], raster='ndvi',
           column_prefix='ndvi', method=['minimum','maximum','average'])
    # v.db.select: don't print column names (-c)
    ret = Module('v.db.select', flags='c', map=options['output'], separator='comma', stdout_=PIPE)
    for line in ret.outputs.stdout.splitlines():
        # parse line (eg. 1,,-0.433962264150943,0.740350877192983,0.051388909449992)
        cat,label,min,max,mean = line.split(',')
        print ('NDVI class {0}: {1:.4f} (min) {2:.4f} (max) {3:.4f} (mean)'.format(
        cat, float(min), float(max), float(mean)))

    return 0

if __name__ == "__main__":
    options, flags = parser()
    atexit.register(cleanup)
    sys.exit(main(options, flags))
