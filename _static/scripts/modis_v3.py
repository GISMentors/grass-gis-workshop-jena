import os
import json

from pywps import Process, LiteralInput, LiteralOutput, ComplexInput, ComplexOutput, Format

__author__ = 'Martin Landa'

class ModisV3(Process):
    def __init__(self):
        inputs = [ComplexInput('region', 'Input vector region',
                               supported_formats=[
                                   Format('text/xml'), # requires QGIS WPS client
                                   Format('application/gml+xml')]),
                  LiteralInput('start', 'Start date (eg. 2019-03-01)',
                               data_type='string'),
                  LiteralInput('end', 'End date (eg. 2019-04-01)',
                               data_type='string')
        ]
        outputs = [ComplexOutput('stats', 'Computed LST statistics',
                                 supported_formats=[Format('application/json')])
        ]

        super(ModisV3, self).__init__(
            self._handler,
            identifier='modis-v3',
            version='0.3',
            title="Modis process (v3)",
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

        output = 'modis_pywps'
        
        # be silent
        os.environ['GRASS_VERBOSE'] = '0'

        Module('v.import',
               input=request.inputs['region'][0].file,
               output='poly')
        Module('g.region', vector='poly', align='c_001')
        Module('r.mask', vector='poly')
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
        # cast dict values to float
        stats = dict(zip(stats.keys(), [float(value) for value in stats.values()]))

        response.outputs['stats'].data = json.dumps(stats)

        return response
