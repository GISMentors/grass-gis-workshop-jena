#!/usr/bin/env python3

import numpy

from grass.pygrass.raster import RasterRow

b04 = RasterRow('L2A_T32UPB_20170706T102021_B04_10m')
b04.open()
b08 = RasterRow('L2A_T32UPB_20170706T102021_B08_10m')
b08.open()
ndvi = RasterRow('ndvi_pyrass')
ndvi.open('w', mtype='FCELL', overwrite=True)

for i in range(len(b04)):
    row_b04 = b04[i]
    row_b08 = b08[i]
    rowb04 = row_b04.astype(numpy.float32)
    rowb08 = row_b08.astype(numpy.float32)
    row_new = (rowb08 - rowb04) / (rowb08 + rowb04)
    ndvi.put_row(row_new)
    
ndvi.close() 
b04.close()
b08.close()
