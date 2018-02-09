#!/usr/bin/env python

#%module
#% description: Creates DEM from input LAS tiles.
#%end
# overwrite: yes
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
#% description: Number of processes
#% answer: 1
#% type: integer
#%end
#%option
#% key: rst_nprocs
#% description: Number of v.surf.rst processes
#% answer: 1
#% type: integer
#%end

import os
import sys
import time
from copy import deepcopy

import grass.script as gs

from grass.pygrass.modules import Module, MultiModule, ParallelModuleQueue

def import_files(directory):
    start = time.time()

    import_module = Module('v.in.lidar', flags='otb',
                           overwrite=gs.overwrite(), run_=False
    )

    maps = []
    for f in os.listdir(directory):
        if os.path.splitext(f)[1] != '.laz':
            continue
        fullname = os.path.join(directory, f)
        basename = os.path.basename(f)
        # '-' is not valid for vector map names
        mapname = os.path.splitext(basename)[0].replace('-', '_')
        
        maps.append(mapname)
        gs.message("Importing <{}>...".format(fullname))
        import_task = deepcopy(import_module)
        queue.put(import_task(input=fullname, output=mapname))
    
    queue.wait()

    if not maps:
        gs.fatal("No input files found")

    gs.message("Import finished in {:.0f} sec".format(time.time() - start))

    return maps

def create_dmt_tiles(maps, res, rst_nprocs, offset_multiplier=10):
    offset=res * offset_multiplier

    start = time.time()

    region_module = Module('g.region', n='n+{}'.format(offset),
                           s='s-{}'.format(offset),
                           e='e+{}'.format(offset),
                           w='w-{}'.format(offset),
                           quiet=True
    )
    rst_module = Module('v.surf.rst', nprocs=rst_nprocs,
                        overwrite=gs.overwrite(), quiet=True, run_=False
    )

    for mapname in maps:
        gs.message("Interpolating <{}>...".format(mapname))
        region_task = deepcopy(region_module)
        rst_task = deepcopy(rst_module)
        mm = MultiModule([region_task(vector=mapname),
                          rst_task(input=mapname, elevation=mapname)],
                         sync=False, set_temp_region=True
        )
        queue.put(mm)
    queue.wait()

    gs.message("Interpolation finished in {:.0f} min".format(
        (time.time() - start) / 60.)
    )
    
def patch_tiles(maps, output, resolution):
    gs.message("Patching tiles <{}>...".format(','.join(maps)))
    Module('g.region', raster=maps, res=resolution)
    Module('r.series', input=maps, output=output, method='average')
    Module('r.colors', map=output, color='elevation')

def main():
    start = time.time()

    maps = import_files(options['input'])
    create_dmt_tiles(maps,
                     float(options['resolution']),
                     int(options['rst_nprocs'])
    )
    patch_tiles(maps,
                options['elevation'],
                options['resolution']
    )

    gs.message("Done in {:.0f} min".format((time.time() - start) / 60.))
    
    return 0

if __name__ == "__main__":
    options, flags = gs.parser()

    # queue for parallel jobs
    queue = ParallelModuleQueue(int(options['nprocs']))

    sys.exit(main())
