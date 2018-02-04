#!/usr/bin/env python
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

from grass.script import parser, run_command, read_command, parse_command, feed_command
from grass.script.vector import vector_db_select
    
def cleanup():
    run_command('g.remove', flags='f', name='region_mask', type='vector')
    run_command('g.remove', flags='f', name='ndvi', type='raster')
    run_command('g.remove', flags='f', name='ndvi_class', type='raster')
    run_command('g.remove', flags='f', name='ndvi_class', type='vector')

def compute():

    if options["clouds"]:
        region_mask = "region_mask"
        run_command("v.overlay",
                    overwrite = True,
                    ainput = options["region"],
                    binput = options["clouds"],
                    operator = "not",
                    output = region_mask)
    else:
        region_mask = options["region"]

    run_command("g.region",
                overwrite = True,
                vector = region_mask,
                align = options["red"])

    run_command("r.mask",
                overwrite = True,
                vector = region_mask)

    run_command("i.vi",
                overwrite = True,
                red = options["red"],
                output = "ndvi",
                nir = options["nir"])
                
    p1 = feed_command("r.recode",
                      overwrite = True,
                      input = "ndvi",
                      output = "ndvi_class",
                      rules = "-")
    p1.stdin.write("""-1:0.1:1
0.1:0.5:2
0.5:1:3""")
    p1.stdin.close()
    p1.wait()

    p2 = feed_command("r.colors",
                      map = "ndvi_class",
                      rules = "-")
    p2.stdin.write("""1 grey
2 255 255 0
3 green""")
    p2.stdin.close()
    p2.wait()

    run_command("r.to.vect",
                flags = 'sv',
                overwrite = True,
                input = "ndvi_class",
                output = "ndvi_class",
                type = "area")

    run_command("v.clean",
                overwrite = True,
                input = "ndvi_class",
                output = options["output"],
                tool = "rmarea",
                threshold = options['threshold'])

def stats():
    print ('-' * 80)
    print ('NDVI class statistics')
    print ('-' * 80)
    ret = read_command('v.report', map=options["output"], option='area')
    for line in ret.splitlines()[1:]: # skip first line (cat|label|area)
        # parse line (eg. 1||2712850)
        data = line.split('|')
        cat = data[0]
        area = float(data[-1])
        print ('NDVI class {0}: {1:.1f} ha'.format(cat, area/1e4))

    # v.to.rast: use -c flag for updating statistics if exists
    run_command('v.rast.stats', flags='c', map=options["output"], raster='ndvi',
                column_prefix='ndvi', method='minimum,maximum,average')
    
    data = vector_db_select(options["output"])
    for vals in data['values'].itervalues():
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
