#!/usr/bin/env python

import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

from grass.pygrass.vector import VectorTopo

counties = VectorTopo('Fylke')
counties.open('r')

for o in counties.viter('areas'):
    neighbours = set()
    for b in o.boundaries():
        for n in b.read_area_ids():
            if n != -1 and n != o.id:
                neighbours.add(n)
    
    print (u'{:25}: {}'.format(o.attrs['navn'].split(':', 1)[1][:-1], len(neighbours)))

counties.close()
