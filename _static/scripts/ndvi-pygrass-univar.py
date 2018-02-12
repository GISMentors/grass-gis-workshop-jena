#!/usr/bin/env python

import numpy as np
from grass.pygrass import raster

ndvi = raster.RasterRow('ndvi')
ndvi.open()

min = max = None
count = ncount = 0
for row in ndvi:
    for value in row:
        if np.isnan(value):
            ncount += 1
        else:
            if min is None:
                min = max = value
            else:
                if min > value:
                    min = value
                elif max < value:
                    max = value
        count += 1

ndvi.close()

print ("min={0:.6f} max={1:.6f} count={2} (no-data: {3})".format(
    min, max, count, ncount)
)
