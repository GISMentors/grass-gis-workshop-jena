#!/usr/bin/env python3

import os
from subprocess import PIPE
from datetime import datetime

from grass.pygrass.modules import Module
from grass.script import parse_key_val
from pywps import Process, LiteralInput, LiteralOutput, Format


class ModisV1(Process):

    def __init__(self):
        os.environ["GRASS_OVERWRITE"] = "1"

        inputs = list()
        outputs = list()

        inputs.append(LiteralInput('start', 'Start date (eg. 2023-03-01)',
                                   data_type='string'))
        inputs.append(LiteralInput('end', 'End date (eg. 2023-03-01)',
                                   data_type='string'))

        outputs.append(LiteralOutput('output', 'Computed LST statistics',
                                     data_type='string'))

        super(ModisV1, self).__init__(
            self._handler,
            identifier="modis-v1",
            title="Modis process (v1)",
            inputs=inputs,
            outputs=outputs,
            # here you could also specify the GRASS location, for example:
            # grass_location="EPSG:5514",
            abstract="Computes LST stats for given period (limited to Germany and 2023).",
            version="0.1",
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
        outstr = 'Min: {0:.1f};Max: {1:.1f};Mean: {2:.1f}'.format(
            stats['min'], stats['max'], stats['mean']
        )
        response.outputs['output'].data = outstr

        return response


if __name__ == "__main__":
    from pywps.app.Service import Service

    processes = [ModisV1()]
    application = Service(processes)
