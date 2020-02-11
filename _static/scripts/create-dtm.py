#!/usr/bin/env python3

#%module
#% description: Creates DTM from input LAS tiles.
#%end
#%option G_OPT_M_DIR
#% required: yes
#%end
#%option G_OPT_R_ELEV
#% description: Name for output elevation raster map mosaics
#%end
#%option
#% key: resolution
#% description: Output resolution
#% type: double
#%end
#%option
#% key: nprocs
#% description: Number of processes per tile
#% answer: 1
#% type: integer
#%end

import os
import sys
import time
from copy import deepcopy

import grass.script as gs

from grass.pygrass.modules import Module, ParallelModuleQueue

def import_files(directory):
    start = time.time()

    # queue for parallel jobs
    queue = ParallelModuleQueue(int(options['nprocs']))

    import_module = Module('v.in.lidar',
                           flags='otb',
                           overwrite=True,
                           run_=False
    )

    maps = []
    for f in os.listdir(directory):
        if os.path.splitext(f)[1] != '.laz':
            continue
        fullname = os.path.join(directory, f)
        basename = os.path.basename(f)
        # '-' is not valid for vector map names
        # vector map names cannot start with number
        mapname = os.path.splitext(basename)[0].replace('-', '_')
        
        maps.append(mapname)
        gs.message("Importing <{}>...".format(fullname))
        import_task = deepcopy(import_module)
        queue.put(import_task(input=fullname, output=mapname))
    
    queue.wait()

    if not maps:
        gs.fatal("No input files found")

    return maps

def create_dtm_tiles(maps, res, nprocs, offset_multiplier=10):
    offset=res * offset_multiplier

    for mapname in maps:
        Module('g.region',
               vector=mapname,
               n='n+{}'.format(offset),
               s='s-{}'.format(offset),
               e='e+{}'.format(offset),
               w='w-{}'.format(offset)
        )
        
        Module('v.surf.rst',
               input=mapname,
               elevation=mapname,
               nprocs=nprocs,
               overwrite=True
        )

def patch_tiles(maps, output, resolution):
    gs.message("Patching tiles <{}>...".format(','.join(maps)))
    Module('g.region', raster=maps, res=resolution)
    Module('r.series', input=maps, output=output, method='average', overwrite=True)
    Module('r.colors', map=output, color='elevation')

def main():
    start = time.time()

    maps = import_files(options['input'])
    create_dtm_tiles(maps,
                     float(options['resolution']),
                     int(options['nprocs'])
    )
    patch_tiles(maps,
                options['elevation'],
                options['resolution']
    )

    gs.message("Done in {:.0f} min".format((time.time() - start) / 60.))
    
    return 0

if __name__ == "__main__":
    options, flags = gs.parser()

    sys.exit(main())
