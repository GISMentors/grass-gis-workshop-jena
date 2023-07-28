#!/usr/bin/env python3

from grass.pygrass.vector import VectorTopo

counties = VectorTopo('counties')
counties.open('r')

for o in counties.viter('areas'):
    neighbours = set()
    for b in o.boundaries():
        for n in b.read_area_ids():
            if n != -1 and n != o.id:
                neighbours.add(n)
    if o.attrs:
        print ('{:25}: {}'.format(o.attrs['name'], len(neighbours)))

counties.close()
