import os
import json

from pywps import Process, LiteralInput, ComplexOutput, Format

__author__ = 'Martin Landa'

class ModisV2(Process):
    def __init__(self):
        inputs = [LiteralInput('coords', 'UTM coordinates',
                               data_type='string'),
                  LiteralInput('start', 'Start date (eg. 2019-03-01)',
                               data_type='string'),
                  LiteralInput('end', 'End date (eg. 2019-04-01)',
                               data_type='string')
        ]
        outputs = [ComplexOutput('stats', 'Computed LST statistics',
                                 supported_formats=[Format('application/json')])
        ]

        super(ModisV2, self).__init__(
            self._handler,
            identifier='modis-v2',
            version='0.2',
            title="Modis process (v2)",
            abstract='The process uses the GRASS GIS to compute LST ' \
            'statistics for given period in 2019 for Germany',
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
            grass_location="/home/user/grassdata/germany-modis"
        )

    def check_date(self, date_str):
        from datetime import datetime

        d = datetime.strptime(date_str, '%Y-%m-%d')
        if d.year != 2019:
            raise Exception("Only year 2019 allowed")

    def _handler(self, request, response):
        from subprocess import PIPE
        
        from grass.pygrass.modules import Module
        from grass.exceptions import CalledModuleError
        
        start = request.inputs['start'][0].data
        end = request.inputs['end'][0].data
        self.check_date(start)
        self.check_date(end)

        x, y = request.inputs['coords'][0].data.split(',')
        
        # be silent
        os.environ['GRASS_VERBOSE'] = '0'

        # need to set computation region (would be nice g.region strds or t.region)
        Module('g.region', raster='c_001')
        try:
            ret = Module('t.rast.what',
                         stdout_=PIPE,
                         strds='modis_c@PERMANENT',
                         coordinates=[x, y],
                         separator=',',
                         where="start_time > '{start}' and start_time < '{end}'".format(
                             start=start, end=end
            ))
        except CalledModuleError:
            raise Exception('Unable to compute statistics')

        tsum = 0
        stats = {
            'min' : None,
            'max' : None,
            'mean' : None,
            'count' : 0,
        }
        count = 0
        for line in ret.outputs.stdout.splitlines():
            items = line.split(',')
            if items[-1] == '*': # no data
                continue
            val = float(items[-1])
            if stats['min'] is None:
                stats['min'] = stats['max'] = stats['mean'] = val
            else:
                if val < stats['min']:
                    stats['min'] = val
                if val > stats['max']:
                    stats['max'] = val
            tsum += val
            stats['count'] += 1
                    
        stats['mean'] = tsum / stats['count']
        
        response.outputs['stats'].data = json.dumps(stats)
        
        return response
