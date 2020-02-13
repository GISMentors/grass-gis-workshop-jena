import os

from pywps import Process, LiteralInput, LiteralOutput

__author__ = 'Martin Landa'

class ModisV1(Process):
    def __init__(self):
        inputs = [LiteralInput('start', 'Start date (eg. 2019-03-01)',
                               data_type='string'),
                  LiteralInput('end', 'End date (eg. 2019-04-01)',
                               data_type='string')
        ]
        outputs = [LiteralOutput('stats', 'Computed LST statistics',
                                 data_type='string')
        ]

        super(ModisV1, self).__init__(
            self._handler,
            identifier='modis-v1',
            version='0.1',
            title="Modis process (v1)",
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

        import grass.script as gs
        from grass.pygrass.modules import Module
        from grass.exceptions import CalledModuleError
        
        start = request.inputs['start'][0].data
        end = request.inputs['end'][0].data
        self.check_date(start)
        self.check_date(end)

        output = 'modis_response'
        
        # be silent
        os.environ['GRASS_VERBOSE'] = '0'

        # need to set computation region (would be nice g.region strds or t.region)
        Module('g.region', raster='c_001')
        try:
            Module('t.rast.series',
                   input='modis_c@PERMANENT',
                   output=output,
                   method='average',
                   where="start_time > '{start}' and start_time < '{end}'".format(
                       start=start, end=end
            ))
        except CalledModuleError:
            raise Exception('Unable to compute statistics')

        ret = Module('r.univar',
                     flags='g',
                     map=output,
                     stdout_=PIPE
        )
        stats = gs.parse_key_val(ret.outputs.stdout)
        
        outstr = 'Min: {0:.1f};Max: {1:.1f};Mean: {2:.1f}'.format(
            float(stats['min']), float(stats['max']), float(stats['mean'])
        )
        response.outputs['stats'].data = outstr

        return response
