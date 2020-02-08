#!/usr/bin/env python3
#
##############################################################################
#
# MODULE:       ndvi-v4
#
# AUTHOR(S):    martin
#
# PURPOSE:      NDVI model version 4
#
# DATE:         Sat Feb  3 15:45:35 2018
#
##############################################################################

#%module
#% description: NDVI script version 4 based on PyGRASS
#%end                
#%option G_OPT_V_INPUT
#% key: region
#% description: Name of input vector region map 
#%end
#%option G_OPT_V_INPUT
#% key: clouds
#% description: Name of input vector clouds map 
#% required: no
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

from grass.pygrass.modules import Module
from grass.script import parser
from grass.script.vector import vector_db_select
    
def cleanup():
    Module('g.remove', flags='f', name='region_mask', type='vector')
    Module('g.remove', flags='f', name='ndvi', type='raster')
    Module('g.remove', flags='f', name='ndvi_class', type='raster')
    Module('g.remove', flags='f', name='ndvi_class', type='vector')

def compute():

    if options["clouds"]:
        region_mask = "region_mask"
        Module("v.overlay",
               overwrite = True,
               ainput = options["region"],
               binput = options["clouds"],
               operator = "not",
               output = region_mask)
    else:
        region_mask = options["region"]

    Module("g.region",
           overwrite = True,
           vector = region_mask,
           align = options["red"])

    Module("r.mask",
           overwrite = True,
           vector = region_mask)

    Module("i.vi",
           overwrite = True,
           red = options["red"],
           output = "ndvi",
           nir = options["nir"])
                
    recode_str="""-1:0.1:1
0.1:0.5:2
0.5:1:3"""

    Module("r.recode",
           overwrite = True,
           input = "ndvi",
           output = "ndvi_class",
           rules = "-",
           stdin_ = recode_str)

    colors_str="""1 grey
2 255 255 0
3 green"""
    Module("r.colors",
           map = "ndvi_class",
           rules = "-",
           stdin_ = colors_str)
    
    Module("r.to.vect",
           flags = 'sv',
           overwrite = True,
           input = "ndvi_class",
           output = "ndvi_class",
           type = "area")

    Module("v.clean",
           overwrite = True,
           input = "ndvi_class",
           output = options["output"],
           tool = "rmarea",
           threshold = options['threshold'])

def stats():
    print ('-' * 80)
    print ('NDVI class statistics')
    print ('-' * 80)
    from subprocess import PIPE
    ret = Module('v.report', map=options["output"], option='area',
                 stdout_=PIPE)
    for line in ret.outputs.stdout.splitlines()[1:]: # skip first line (cat|label|area)
        # parse line (eg. 1||2712850)
        data = line.split('|')
        cat = data[0]
        area = float(data[-1])
        print ('NDVI class {0}: {1:.1f} ha'.format(cat, area/1e4))

    # v.to.rast: use -c flag for updating statistics if exists
    Module('v.rast.stats', flags='c', map=options["output"], raster='ndvi',
           column_prefix='ndvi', method=['minimum','maximum','average'])
    
    data = vector_db_select(options["output"])
    for vals in data['values'].values():
        # unfortunately we need to cast values by float
        print ('NDVI class {0}: {1:.4f} (min) {2:.4f} (max) {3:.4f} (mean)'.format(
            vals[0], float(vals[2]), float(vals[3]), float(vals[4])))

def main():
    compute()
    stats()

    return 0

if __name__ == "__main__":
    options, flags = parser()
    atexit.register(cleanup)
    sys.exit(main())
