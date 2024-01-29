#!/usr/bin/env python3
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

# %module
# % description: NDVI TGRASS script version 1
# %end
# %option G_OPT_STRDS_INPUT
# % key: b4
# % description: Name of input 4th band space time raster dataset
# %end
# %option G_OPT_STRDS_INPUT
# % key: b8
# % description: Name of input 8th band space time raster dataset
# %end
# %option G_OPT_STRDS_INPUT
# % key: mask
# % description: Name of input mask space time raster dataset
# %end
# %option G_OPT_F_OUTPUT
# %end
# %option
# % key: basename
# % description: Basename for output raster maps
# % required: yes
# %end
# %option
# % key: min_area
# % description: Threshold for removing small areas in m2
# % answer: 1600
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

def compute(b4, b8, msk, min_area_ha, output):
    Module("g.region",
           overwrite=True,
           raster=msk,
           align=b4)

    Module("r.mask",
           overwrite=True,
           maskcats="*",
           raster=msk,
           layer="1")

    Module("i.vi",
           overwrite=True,
           output="ndvi",
           viname="ndvi",
           red=b4,
           nir=b8,
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
           value=min_area_ha,
           mode="greater",
           method="reclass")

    Module("r.grow.distance",
           overwrite=True,
           input="ndvi_class_area",
           value=output,
           metric="euclidean")

    Module("r.colors",
           map=output,
           rules="-",
           stdin_="1 grey\n2 255 255 0\n3 green",
           offset=0,
           scale=1)
    
def stats(output, date, fd):
    fd.write('-' * 80)
    fd.write('\n')
    fd.write('NDVI class statistics ({0}: {1})'.format(output, date))
    fd.write('\n')
    fd.write('-' * 80)
    fd.write('\n')

    ret = Module('r.stats', input=output, flags='ian', stdout_=PIPE)
    for line in ret.outputs.stdout.splitlines():
        # parse line (eg. 1 2737300.000000)
        data = line.split(' ')
        cat = data[0]
        area = float(data[-1])
        fd.write('NDVI class {0}: {1:.1f} ha\n'.format(cat, area/1e4)) 

    fd.write('-' * 80)
    fd.write('\n')
    # we need integer map
    Module('r.mapcalc', expression='ndvi_class_filled_i = int({})'.format(output))
    Module('r.to.vect', flags='v', input='ndvi_class_filled_i', output='ndvi_class_filled', type='area')

    Module('v.rast.stats', flags='c', map='ndvi_class_filled', raster='ndvi',
           column_prefix='ndvi', method=['minimum','maximum','average'])
    # v.db.select: don't print column names (-c)
    ret = Module('v.db.select', flags='c', map='ndvi_class_filled', separator='comma', stdout_=PIPE)
    for line in ret.outputs.stdout.splitlines():
        # parse line (eg. 1,,-0.433962264150943,0.740350877192983,0.051388909449992)
        cat,label,min,max,mean = line.split(',')
        fd.write('NDVI class {0}: {1:.4f} (min) {2:.4f} (max) {3:.4f} (mean)\n'.format(
        cat, float(min), float(max), float(mean)))
        
def main():
    import grass.temporal as tgis

    tgis.init()

    sp4=tgis.open_old_stds(options['b4'], 'raster')
    sp8=tgis.open_old_stds(options['b8'], 'raster')
    msk=tgis.open_old_stds(options['mask'], 'raster')

    min_area = int(options['min_area']) / 1e4
    idx=1
    fd=open(options['output'], 'w')
    for item in sp4.get_registered_maps(columns='name,start_time'):
        b4=item[0]
        date=item[1]
        b8=sp8.get_registered_maps(columns='name',
                                     where="start_time='{}'".format(date))[0][0]
        ms=msk.get_registered_maps(columns='name',
                                     where="start_time='{}'".format(date))[0][0]
        output='{}_{}'.format(options['basename'], idx)
        compute(b4, b8, ms, min_area, output)
        stats(output, date, fd)
        cleanup()
        idx += 1

    fd.close()
    
    return 0

if __name__ == "__main__":
    options, flags=parser()
    sys.exit(main())
