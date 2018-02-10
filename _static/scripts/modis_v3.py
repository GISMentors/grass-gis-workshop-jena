import os

from pywps import Process, LiteralInput, LiteralOutput, ComplexInput, Format

__author__ = 'Martin Landa'

class ModisV3(Process):
    def __init__(self):
        inputs = [ComplexInput('region', 'Input vector region',
                               supported_formats=[Format('application/gml+xml')]),
                  LiteralInput('start', 'Start date (eg. 2017-03-01)',
                               data_type='string'),
                  LiteralInput('end', 'End date (eg. 2017-04-01)',
                               data_type='string')]
        outputs = [LiteralOutput('stats', 'Computed LST statistics',
                                 data_type='string')]

        super(ModisV3, self).__init__(
            self._handler,
            identifier='modis-v3',
            version='0.3',
            title="Modis process (v3)",
            abstract='The process uses the GRASS GIS to compute LST ' \
            'statistics for given period in 2017 for Germany',
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
            grass_location="/opt/grassdata/germany-modis"
        )

    def check_date(self, date_str):
        from datetime import datetime

        d = datetime.strptime(date_str, '%Y-%m-%d')
        if d.year != 2017:
            raise Exception("Only year 2017 allowed")

    def _handler(self, request, response):
        import grass.script as gs
        from grass.exceptions import CalledModuleError
        
        start = request.inputs['start'][0].data
        end = request.inputs['end'][0].data
        self.check_date(start)
        self.check_date(end)

        output = 'modis_pywps'
        
        # be silent
        os.environ['GRASS_VERBOSE'] = '0'

        gs.run_command('v.import',
                       input=request.inputs['region'][0].file,
                       output='poly')
        gs.run_command('g.region', vector='poly', align='c_001')
        gs.run_command('r.mask', vector='poly')
        try:
            gs.run_command('t.rast.series',
                           input='modis_c@PERMANENT',
                           output=output,
                           method='average',
                           where="start_time > '{start}' and start_time < '{end}'".format(
                               start=start, end=end
            ))
        except CalledModuleError:
            raise Exception('Unable to compute statistics')

        stats = gs.parse_command('r.univar',
                                 flags='g',
                                 map=output
        )
        
        outstr = ''
        outstr += 'Min: {0:.1f};'.format(float(stats['min']))
        outstr += 'Max: {0:.1f};'.format(float(stats['max']))
        outstr += 'Mean: {0:.1f}'.format(float(stats['mean']))

        response.outputs['stats'].data = outstr

        return response
