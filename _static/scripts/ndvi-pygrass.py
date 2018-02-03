#!/usr/bin/env python

#%module
#% description: Creates reclassified NDVI.
#%end
#%option G_OPT_M_MAPSET
#% required: yes
#% answer: landsat
#%end
#%option
#% key: output_postfix
#% type: string
#% description: Postfix for output maps
#% answer: ndvi
#%end
#%option G_OPT_F_INPUT
#% key: classes
#% required: no
#%end

import sys
from subprocess import PIPE

import grass.script as grass

from grass.pygrass.modules import Module
from grass.pygrass.gis import Mapset

def main():
    mapset = options['mapset']
    ndvi = options['output_postfix']
    
    # pridat mapset do vyhledavaci cesty
    Module('g.mapsets', mapset=mapset, operation='add', quiet=True)
    
    try:
        vis = Mapset(mapset).glist('raster', pattern='*B4')[0]
        nir = Mapset(mapset).glist('raster', pattern='*B5')[0]
    except IndexError:
        grass.fatal("Nelze najit vstupni kanaly")
    r_ndvi= "r_{}".format(ndvi)
    
    # nastavit vypocetni region
    Module('g.region', raster=vis)
    
    # vypocet NDIV
    grass.message("VIS: {0} ; NIR: {1}".format(vis, nir))
    Module('r.mapcalc',
           expression="{o} = float({n} - {v}) / ({n} + {v})".format(o=ndvi, v=vis, n=nir),
           overwrite=True)
    
    # reklasifikace (1,2,3)
    grass.message("Reklasifikuji...")
    # r.reclass umi reklasifikovat pouze celociselne rastry, proto pouzime
    # r.recode
    args = {}
    if options['classes']:
        args['rules'] = options['classes']
    else:
        recode = """
-1:0.05:1 
0.05:0.35:2 
0.35:1:3
        """
        args['rules'] = '-'
        args['stdin_'] = recode
    Module('r.recode', input=ndvi, output=r_ndvi,
           overwrite=True, **args)
    
    # popisky
    labels = """
1:bez vegetace, vodni plochy
2:plochy s minimalni vegetaci
3:plochy pokryte vegetaci
"""
    Module('r.category', map=r_ndvi,
           separator=':', rules='-', stdin_=labels)
    
    # tabulka barev
    colors = """
1 red
2 yellow
3 0 136 26
"""
    Module('r.colors', map=r_ndvi,
           rules='-', quiet=True, stdin_=colors)
    
    # vypsat vysledek
    grass.message("Generuji report...")
    report = Module('r.stats', flags='pl', input=r_ndvi, separator=':', stdout_=PIPE)
    
    print('-' * 80)
    for trida, label, procento in map(lambda x: x.split(':'), report.outputs.stdout.splitlines()):
        print("Trida {0} ({1:28s}): {2:>7}".format(trida, label, procento))
    print('-' * 80)

    grass.message("Hotovo!")

    return 0

if __name__ == "__main__":
    options, flags = grass.parser()
    sys.exit(main())
