#!/usr/bin/env python3
#
##############################################################################
#
# MODULE:       ndvi-tgrass-v2
#
# AUTHOR(S):    martin
#
# PURPOSE:      NDVI TGRASS version 2
#
# DATE:         Sat Feb  3 15:45:35 2018
#
##############################################################################

#%module
#% description: NDVI TGRASS script version 2
#%end                
#%option G_OPT_STRDS_INPUT
#% key: b4
#% description: Name of the input 4th band space time raster dataset
#%end
#%option G_OPT_STRDS_INPUT
#% key: b8
#% description: Name of the input 4th band space time raster dataset
#%end
#%option G_OPT_STRDS_INPUT
#% key: mask
#% description: Name of the input mask space time raster dataset
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
#%option
#% key: nprocs
#% description: Number of processes
#% answer: 1
#% type: integer
#%end

import sys
import os
import atexit

from grass.pygrass.modules import Module, MultiModule, ParallelModuleQueue
from grass.script import parser
from grass.script.vector import vector_db_select
    
def cleanup(idx):
    Module('g.remove', flags='f', name='mask' + idx, type='raster')
    Module('g.remove', flags='f', name='ndvi' + idx, type='raster')
    Module('g.remove', flags='f', name='ndvi_class' + idx, type='raster')
    Module('g.remove', flags='f', name='ndvi_class' + idx, type='vector')

def compute(b4, b8, msk, output, idx):

    modules = []
    modules.append(
        Module("g.region",
               overwrite = True,
               raster = msk,
               align = b4,
               run_ = False)
    )
    modules.append(
        Module("r.mapcalc",
               overwrite = True,
               expression = "ndvi{idx} = if(isnull({clouds}), null(), float({b8} - {b4}) / ({b8} + {b4}))".format(
                   idx=idx, clouds=msk, b8=b8, b4=b4),
               run_ = False)
    )
                
    recode_str="""-1:0.1:1
0.1:0.5:2
0.5:1:3"""

    modules.append(
        Module("r.recode",
               overwrite = True,
               input = "ndvi" + idx,
               output = "ndvi_class" + idx,
               rules = "-",
               stdin_ = recode_str,
               run_ = False)
    )
    
    colors_str="""1 grey
2 255 255 0
3 green"""
    modules.append(
        Module("r.colors",
               map = "ndvi_class" + idx,
               rules = "-",
               stdin_ = colors_str,
               run_ = False)
    )

    modules.append(
        Module("r.to.vect",
               flags = 'sv',
               overwrite = True,
               input = "ndvi_class" + idx,
               output = "ndvi_class" + idx,
               type = "area",
               run_ = False)
    )

    modules.append(
        Module("v.clean",
               overwrite = True,
               input = "ndvi_class" + idx,
               output = output,
               tool = "rmarea",
               threshold = options['threshold'],
               run_ = False)
    )

    modules.append(
        Module('v.rast.stats',
               flags='c',
               map=output,
               raster='ndvi'+idx,
               column_prefix='ndvi',
               method=['minimum','maximum','average'],
               run_ = False)
    )

    queue.put(MultiModule(modules, sync=False, set_temp_region=True))

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

    data = vector_db_select(output)
    for vals in data['values'].values():
        # unfortunately we need to cast values by float
        fd.write('NDVI class {0}: {1:.4f} (min) {2:.4f} (max) {3:.4f} (mean)'.format(
            vals[0], float(vals[2]), float(vals[3]), float(vals[4])))
        fd.write(os.linesep)
        
def main():
    import grass.temporal as tgis

    tgis.init()

    sp4 = tgis.open_old_stds(options['b4'], 'raster')
    sp8 = tgis.open_old_stds(options['b8'], 'raster')
    msk = tgis.open_old_stds(options['mask'], 'raster')

    idx = 1
    data = []
    for item in sp4.get_registered_maps(columns='name,start_time'):
        b4 = item[0]
        date=item[1]
        b8 = sp8.get_registered_maps(columns='name',
                                     where="start_time = '{}'".format(date))[0][0]
        ms = msk.get_registered_maps(columns='name',
                                     where="start_time = '{}'".format(date))[0][0]
        output = '{}_{}'.format(options['basename'], idx)
        compute(b4, b8, ms, output, str(idx))

        data.append(
            (output, date)
        )
            
        idx += 1

    queue.wait()

    idx = 1
    fd = open(options['output'], 'w')
    for output, date in data:
        stats(output, date, fd)
        cleanup(str(idx))
        idx += 1

    fd.close()
    
    return 0

if __name__ == "__main__":
    options, flags = parser()

    # queue for parallel jobs
    queue = ParallelModuleQueue(int(options['nprocs']))

    sys.exit(main())
