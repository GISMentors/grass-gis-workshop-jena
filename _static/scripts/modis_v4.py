#!/usr/bin/env python3

import json 
from subprocess import PIPE
from datetime import datetime

from grass.pygrass.modules import Module
from grass.script import parse_key_val
from pywps import Process, LiteralInput, ComplexInput, ComplexOutput, Format


class ModisV4(Process):

    def __init__(self):
        inputs = list()
        outputs = list()

        inputs.append(ComplexInput('region', 'Input vector region',
                    supported_formats=[
                        Format('text/xml'), # requires QGIS WPS client
                        Format('application/gml+xml')]))
        inputs.append(LiteralInput('start', 'Start date (eg. 2023-03-01)',
                                   data_type='string'))
        inputs.append(LiteralInput('end', 'End date (eg. 2023-03-01)',
                                   data_type='string'))

        outputs.append(ComplexOutput('zones', 'Output LST zones',
                                     supported_formats=[Format('application/gml+xml')])

        super(ModisV4, self).__init__(
            self._handler,
            identifier="modis-v4",
            tiotle="Modis process (v4)",
            inputs=inputs,
            outputs=outputs,
            # here you could also specify the GRASS location, for example:
            # grass_location="EPSG:5514",
            abstract="Computes LST stats for given area and period (limited to Germany and 2023).",
            verosion="0.4",
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
                output='poly')
        Module('g.region', vector='poly', align='c_001')
        Module('r.mask', vector='poly')

        Module("t.rast.series",
               overwrite=True,
               input="modis_c@PERMANENT",
               method="average",
               order="start_time",
               nprocs=1,
               memory=300,
               where="start_time > '{}' and start_time < '{}'".format(
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

        output = 'stats'
        recode_table = """{min}:{first}:1
{first}:{median}:2
{median}:{third}:3
{third}:{max}:4""".format(
    min=stats['min'], first=stats['first_quartile'],
    median=stats['median'], third=stats['third_quartile'],
    max=stats['max'])                     
        Module("r.recode",
               overwrite=True,               
               input = output,
               output = output + '_zones',
               rules = "-",
               stdin_=recode_table
        )

        Module("r.to.vect",
 97               flags = 'sv',
 98               input = output + '_zones',
 99               output = output + '_zones',
100               type = "area")
101        
102        Module('v.out.ogr',
103               input=output + '_zones',
104               output='zones.gml',
105               format='GML', overwrite=True)
106
107        response.outputs['zones'].file = 'zones.gml'

        return response


if __name__ == "__main__":
    from pywps.app.Service import Service

    processes = [ModisV4()]
    application = Service(processes)
