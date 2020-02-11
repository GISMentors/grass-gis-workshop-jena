#!/usr/bin/env python3

import numpy

from grass.pygrass.raster import RasterRow

newscratch = RasterRow('newscratch')
newscratch.open('w', overwrite=True)

# get computational region info
from grass.pygrass.gis.region import Region
reg = Region()

# import buffer and create empty row
from grass.pygrass.raster.buffer import Buffer
newrow = Buffer((reg.cols,), mtype='CELL')

# we create a raster to fill all the GRASS GIS region
for r in range(reg.rows):
    newrow[:] = numpy.random.random_integers(0, 1000, size=newrow.size)
    newscratch.put_row(newrow)
          
newscratch.close()
