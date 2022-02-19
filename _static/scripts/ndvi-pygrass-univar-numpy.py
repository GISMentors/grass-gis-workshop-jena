#!/usr/bin/env python3

import numpy

from grass.pygrass.raster import RasterRow

ndvi = RasterRow('ndvi')
ndvi.open()
array = numpy.array(ndvi)
ndvi.close()

print("min={0:.6f} max={1:.6f} count={2} (no-data: {3})".format(
    array.min(), array.max(), array.size,
    numpy.count_nonzero(numpy.isnan(array)))
)
