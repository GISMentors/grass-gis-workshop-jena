#!/usr/bin/env python

#%module
#% description: Computes LST stats for given period (limited to Germany and 2017).
#%end
#%option G_OPT_STRDS_INPUT
#%end
#%option 
#% key: start
#% description: Start date (eg. 2017-03-01)
#% type: string
#% required: yes
#%end
#%option 
#% key: end
#% description: End date (eg. 2017-04-01)
#% type: string
#% required: yes
#%end

import os
import sys
import atexit
from datetime import datetime

import grass.script as gs
from grass.exceptions import CalledModuleError
    
def check_date(date_str):
    d = datetime.strptime(date_str, '%Y-%m-%d')
    if d.year != 2017:
        gs.fatal("Only year 2017 allowed")

def cleanup():
    try:
        gs.run_command('g.remove', flags='f', type='raster', name=output)
    except CalledModuleError:
        pass
    
def main():
    check_date(options['start'])
    check_date(options['end'])

    # be silent
    os.environ['GRASS_VERBOSE'] = '0'
    
    try:
        gs.run_command('t.rast.series',
                       input=options['input'],
                       output=output,
                       method='average',
                       where="start_time > '{start}' and start_time < '{end}'".format(
                           start=options['start'], end=options['end']
        ))
    except CalledModuleError:
        gs.fatal('Unable to compute statistics')
        
    stats = gs.parse_command('r.univar',
                             flags='g',
                             map=output
    )
    print('Min: {0:.1f}'.format(float(stats['min'])))
    print('Max: {0:.1f}'.format(float(stats['max'])))
    print('Mean: {0:.1f}'.format(float(stats['mean'])))
        
if __name__ == "__main__":
    options, flags = gs.parser()
    output = '{}_{}'.format(options['input'], os.getpid())
    
    atexit.register(cleanup)
    sys.exit(main())
