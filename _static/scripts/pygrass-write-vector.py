#!/usr/bin/env python3

from grass.pygrass.vector import VectorTopo
from grass.pygrass.vector.geometry import Point

# create the columns definition
cols = [(u'cat',   'INTEGER PRIMARY KEY'),
        (u'name',  'VARCHAR')]
# start new vector with columns definition
new = VectorTopo('pois')
new.open('w', tab_cols=cols, overwrite=True)
# add points
point = Point(681671.15,5644545.63)
new.write(point, ('Jena',))
# commit attributes, otherwise they will be not saved
new.table.conn.commit()
# close the vector
new.close()
