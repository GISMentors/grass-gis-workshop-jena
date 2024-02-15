#!/usr/bin/env python3

import json 
from subprocess import PIPE
from datetime import datetime

from grass.pygrass.modules import Module
from grass.script import parse_key_val
from pywps import Process, LiteralInput, ComplexOutput, Format


class ModisV2(Process):

    def __init__(self):
        inputs = list()
        outputs = list()

        inputs.append(LiteralInput('coordinates', 'ETRS-89 coordinates',
                                  data_type='string'))
        inputs.append(LiteralInput('start', 'Start date (eg. 2023-03-01)',
                                   data_type='string'))
        inputs.append(LiteralInput('end', 'End date (eg. 2023-03-01)',
                                   data_type='string'))

        outputs.append(ComplexOutput('output', 'Computed LST statistics',
                                     supported_formats=[Format('application/json')]))

        super(ModisV2, self).__init__(
            self._handler,
            identifier="modis-v2",
            title="Modis process (v2)",
            inputs=inputs,
            outputs=outputs,
            # here you could also specify the GRASS location, for example:
            # grass_location="EPSG:5514",
            abstract="Computes LST stats for given location and period (limited to Germany and 2023).",
            version="0.2",
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

        x, y = request.inputs['coordinates'][0].data.split(',')

        m = Module('t.rast.what',
                   strds='modis_c@PERMANENT',
                   coordinates=[x, y],
                   separator=',',
                   where="start_time > '{}' and start_time < '{}'".format(
                   request.inputs["start"][0].data,
                   request.inputs["end"][0].data),
                   stdout_=PIPE)

        stats = {
            'min' : None,
            'max' : None,
            'mean' : None,
        }
        tsum = 0
        count = 0
        for line in m.outputs.stdout.splitlines():
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
            count += 1
        stats['mean'] = tsum / count
        
        response.outputs['output'].data = json.dumps(stats)

        return response


if __name__ == "__main__":
    from pywps.app.Service import Service

    processes = [ModisV2()]
    application = Service(processes)
