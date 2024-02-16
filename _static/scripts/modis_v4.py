#!/usr/bin/env python3

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
                        Format('text/xml'),
                        Format('application/gml+xml')]))
        inputs.append(LiteralInput('start', 'Start date (eg. 2023-03-01)',
                                   data_type='string'))
        inputs.append(LiteralInput('end', 'End date (eg. 2023-03-01)',
                                   data_type='string'))

        outputs.append(ComplexOutput('output', 'Output LST zones',
                     supported_formats=[
                         Format('text/xml'),
                         Format('application/gml+xml')]))

        super(ModisV4, self).__init__(
            self._handler,
            identifier="modis-v4",
            title="Modis process (v4)",
            inputs=inputs,
            outputs=outputs,
            # here you could also specify the GRASS location, for example:
            # grass_location="EPSG:5514",
            abstract="Computes LST stats for given area and period (limited to Germany and 2023).",
            version="0.4",
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

        output_map = "lst_zones"
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
               output=output_map,
               file_limit=1000)

        m = Module("r.univar",
                   flags="ge",
                   overwrite=True,
                   map=output_map,
                   percentile=90,
                   nprocs=1,
                   separator="pipe",
                   stdout_=PIPE)

        stats = parse_key_val(m.outputs.stdout, val_type=float)

        recode_table = """{min}:{first}:1
{first}:{median}:2
{median}:{third}:3
{third}:{max}:4""".format(
    min=stats['min'], first=stats['first_quartile'],
    median=stats['median'], third=stats['third_quartile'],
    max=stats['max'])                     
        Module("r.recode",
               overwrite=True,               
               input = output_map,
               output = output_map + '_zones',
               rules = "-",
               stdin_=recode_table)

        Module("r.to.vect",
               overwrite=True,
               flags = 'v',
               input = output_map + '_zones',
               output = output_map + '_zones',
               type = "area")

        Module('v.out.ogr',
               overwrite=True,
               input=output_map + '_zones',
               output=output_map + '.gml',
               format='GML')

        response.outputs['output'].file = output_map + '.gml'

        return response


if __name__ == "__main__":
    from pywps.app.Service import Service

    processes = [ModisV4()]
    application = Service(processes)
