#!/usr/bin/env python
#
##############################################################################
#
# MODULE:       ndvi-v2
#
# AUTHOR(S):    martin
#
# PURPOSE:      NDVI model version 2
#
# DATE:         Sat Feb  3 15:45:35 2018
#
##############################################################################

import sys
import os
import atexit

from grass.script import parser, run_command, read_command, parse_command

def cleanup():
    pass

def compute():
    run_command("v.overlay",
                overwrite = True,
                ainput = "jena_boundary@PERMANENT",
                alayer = "1",
                atype = "auto",
                binput = "MaskFeature@PERMANENT",
                blayer = "1",
                btype = "area",
                operator = "not",
                output = "region_mask",
                olayer = "1,0,0",
                snap = 1e-8)

    run_command("g.region",
                overwrite = True,
                vector = "region_mask",
                align = "L2A_T32UPB_20170706T102021_B04_10m@PERMANENT")

    run_command("r.mask",
                overwrite = True,
                maskcats = "*",
                vector = "region_mask",
                layer = "1")

    run_command("i.vi",
                overwrite = True,
                red = "L2A_T32UPB_20170706T102021_B04_10m@PERMANENT",
                output = "ndvi",
                viname = "ndvi",
                nir = "L2A_T32UPB_20170706T102021_B08_10m@PERMANENT",
                storage_bit = 8)

    run_command("r.recode",
                overwrite = True,
                input = "ndvi",
                output = "ndvi_class",
                rules = "/home/landa/geodata/jena/models/reclass.txt")

    run_command("r.colors",
                map = "ndvi_class",
                rules = "/home/landa/geodata/jena/models/colors.txt")

    run_command("r.to.vect",
                flags = 'sv',
                overwrite = True,
                input = "ndvi_class",
                output = "ndvi_class",
                type = "area",
                column = "value")

    run_command("v.clean",
                overwrite = True,
                input = "ndvi_class",
                layer = "-1",
                type = "point,line,boundary,centroid,area,face,kernel",
                output = "ndvi_vector",
                tool = "rmarea",
                threshold = 1600)

def stats():
    print ('-' * 80)
    print ('NDVI class statistics')
    print ('-' * 80)
    ret = read_command('v.report', map='ndvi_vector', option='area')
    for line in ret.splitlines()[1:]: # skip first line (cat|label|area)
        # parse line (eg. 1||2712850)
        data = line.split('|')
        cat = data[0]
        area = float(data[-1])
        print ('NDVI class {0}: {1:.1f} ha'.format(cat, area/1e4))

    # v.to.rast: use -c flag for updating statistics if exists
    run_command('v.rast.stats', flags='c', map='ndvi_vector', raster='ndvi',
                column_prefix='ndvi', method='minimum,maximum,average')
    # v.db.select: don't print column names (-c)
    ret = read_command('v.db.select', flags='c', map='ndvi_vector', separator='comma')
    for line in ret.splitlines():
        # parse line (eg. 1,,-0.433962264150943,0.740350877192983,0.051388909449992)
        cat,label,min,max,mean = line.split(',')
        print ('NDVI class {0}: {1:.4f} (min) {2:.4f} (max) {3:.4f} (mean)'.format(
        cat, float(min), float(max), float(mean)))

def main():
    compute()
    stats()

    return 0

if __name__ == "__main__":
    options, flags = parser()
    atexit.register(cleanup)
    sys.exit(main())
