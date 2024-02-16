#!/usr/bin/env python3

import json 
from subprocess import PIPE
from datetime import datetime

from grass.pygrass.modules import Module
from grass.script import parse_key_val
from pywps import Process, LiteralInput, ComplexInput, ComplexOutput, Format


class ModisV3(Process):

    def __init__(self):
        inputs = list()
        outputs = list()

        inputs.append(ComplexInput('region', 'Input vector region',
                    supported_formats=[
                        Format('text/xml'),
                        Format('application/gml+xml')]))
        inputs.append(LiteralInput('start', 'Start date (eg. 2023-03-01)',
                                   data_type='string'))
        inputs.append(LiteralInput('end', 'End date (eg. 2023-03-01)',
                                   data_type='string'))

        outputs.append(ComplexOutput('output', 'Computed LST statistics',
                                     supported_formats=[Format('application/json')]))

        super(ModisV3, self).__init__(
            self._handler,
            identifier="modis-v3",
            title="Modis process (v3)",
            inputs=inputs,
            outputs=outputs,
            # here you could also specify the GRASS location, for example:
            # grass_location="EPSG:5514",
            abstract="Computes LST stats for given area and period (limited to Germany and 2023).",
            version="0.3",
            store_supported=True,
            status_supported=True)

    @staticmethod
    def _handler(request, response):
        def check_date(date_str):
            d = datetime.strptime(date_str, '%Y-%m-%d')
            if d.year != 2023:
                raise Exception("Only year 2023 allowed")

        check_date(request.inputs['start'][0].data)
        check_date(request.inputs['end'][0].data)

        Module('v.import',
                input=request.inputs['region'][0].file,
                output='poly', overwrite=True)
        Module('g.region', vector='poly', align='c_001')
        Module('r.mask', vector='poly', overwrite=True)

        Module("t.rast.series",
               overwrite=True,
               input="modis_c@PERMANENT",
               method="average",
               order="start_time",
               nprocs=1,
               memory=300,
               where="start_time >= '{}' and start_time < '{}'".format(
                   request.inputs["start"][0].data,
                   request.inputs["end"][0].data),
               output="t_rast_series_out",
               file_limit=1000)

        m = Module("r.univar",
                   flags="g",
                   overwrite=True,
                   map="t_rast_series_out",
                   percentile=90,
                   nprocs=1,
                   separator="pipe",
                   stdout_=PIPE)

        stats = parse_key_val(m.outputs.stdout, val_type=float)

        response.outputs['output'].data = json.dumps(stats)

        return response


if __name__ == "__main__":
    from pywps.app.Service import Service

    processes = [ModisV3()]
    application = Service(processes)
