#!/usr/bin/env python
#
##############################################################################
#
# MODULE:       ndvi-tgrass-v1
#
# AUTHOR(S):    martin
#
# PURPOSE:      NDVI TGRASS version 1
#
# DATE:         Sat Feb  3 15:45:35 2018
#
##############################################################################

#%module
#% description: NDVI TGRASS script version 1
#%end                
#%option G_OPT_V_INPUT
#% key: region
#% description: Name of input vector region map 
#% answer: jena_boundary@PERMANENT
#%end
#%option G_OPT_STRDS_INPUT
#% key: b4
#% description: Name of input 4th band space time raster dataset
#%end
#%option G_OPT_STRDS_INPUT
#% key: b8
#% description: Name of input 8th band space time raster dataset
#%end
#%option G_OPT_STRDS_INPUT
#% key: clouds
#% description: Name of input clouds space time raster dataset
#%end
#%option G_OPT_F_OUTPUT
#%end
#%option
#% key: basename
#% description: Basename for output raster maps
#% required: yes
#%end
#%option
#% key: threshold
#% description: Threshold for removing small areas
#% answer: 1600
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

def compute(b4, b8, cl, output):

    if cl:
        region_mask = "region_mask"
        Module("v.overlay",
               overwrite = True,
               ainput = options["region"],
               binput = cl,
               operator = "not",
               output = region_mask)
    else:
        region_mask = options["region"]

    Module("g.region",
           overwrite = True,
           vector = region_mask,
           align = b4)

    Module("r.mask",
           overwrite = True,
           vector = region_mask)

    Module("i.vi",
           overwrite = True,
           red = b4,
           output = "ndvi",
           nir = b8)
                
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
           output = output,
           tool = "rmarea",
           threshold = options['threshold'])

def stats(output, date, fd):
    fd.write('-' * 80)
    fd.write(os.linesep)
    fd.write('NDVI class statistics ({0}: {1})'.format(output, date))
    fd.write(os.linesep)
    fd.write('-' * 80)
    fd.write(os.linesep)
    from subprocess import PIPE
    ret = Module('v.report', map=output, option='area',
                 stdout_=PIPE)
    for line in ret.outputs.stdout.splitlines()[1:]: # skip first line (cat|label|area)
        # parse line (eg. 1||2712850)
        data = line.split('|')
        cat = data[0]
        area = float(data[-1])
        fd.write('NDVI class {0}: {1:.1f} ha'.format(cat, area/1e4))
        fd.write(os.linesep)

    # v.to.rast: use -c flag for updating statistics if exists
    Module('v.rast.stats', flags='c', map=output, raster='ndvi',
           column_prefix='ndvi', method=['minimum','maximum','average'])
    
    data = vector_db_select(output)
    for vals in data['values'].itervalues():
        # unfortunately we need to cast values by float
        fd.write('NDVI class {0}: {1:.4f} (min) {2:.4f} (max) {3:.4f} (mean)'.format(
            vals[0], float(vals[2]), float(vals[3]), float(vals[4])))
        fd.write(os.linesep)
        
def main():
    import grass.temporal as tgis

    tgis.init()

    sp4 = tgis.open_old_stds(options['b4'], 'raster')
    sp8 = tgis.open_old_stds(options['b8'], 'raster')
    spc = tgis.open_old_stds(options['clouds'], 'raster')

    idx = 1
    fd = open(options['output'], 'w')
    for item in sp4.get_registered_maps(columns='name,start_time'):
        b4 = item[0]
        date=item[1]
        b8 = sp8.get_registered_maps(columns='name',
                                     where="start_time = '{}'".format(date))[0][0]
        cl = spc.get_registered_maps(columns='name',
                                     where="start_time = '{}'".format(date))[0][0]
        output = '{}_{}'.format(options['basename'], idx)
        compute(b4, b8, cl, output)
        stats(output, date, fd)
        cleanup()
        idx += 1

    fd.close()
    
    return 0

if __name__ == "__main__":
    options, flags = parser()
    sys.exit(main())
