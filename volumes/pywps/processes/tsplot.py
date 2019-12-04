import json
import os
import subprocess
from pywps import Process, LiteralInput, LiteralOutput, UOM
from pywps.wpsserver import temp_dir


__author__ = 'Massimo'

class TsPlot(Process):
    def __init__(self):
        inputs = [LiteralInput('input',
                               'Input File (http://thredds.met.no/thredds/dodsC/arome25/arome_metcoop_default2_5km_latest.nc)',
                               data_type='string',
                               min_occurs=1,
                               max_occurs=1),
                  LiteralInput('variable',
                               'Variable to plot',
                               data_type='string',
                               min_occurs=0,
                               max_occurs=1)
                  ]
        outputs = [LiteralOutput('plot',
                                 'bokeh plot',
                                 data_type='string')
                   ]

        super(TsPlot, self).__init__(
            self._handler,
            identifier='tsplot',
            title='TsPlot',
            abstract='Tak e a Timne series data (Variable, Time) as netcdf with known structure, \ '
                     'and return html and js to build an interactive html plot  using the bokeh llibrary.',
            version='1.0',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        command = 'fimex '
        fimex_arguments = {
            'inputfile': '--input.file',
            'inputtype': '--input.type',
            'reducetimeStart': '--extract.reduceTime.start',
            'reducetimeEnd': '--extract.reduceTime.end',
            'reduceboxNorth': '--extract.reduceToBoundingBox.north',
            'reduceboxSouth': '--extract.reduceToBoundingBox.south',
            'reduceboxEast': '--extract.reduceToBoundingBox.east',
            'reduceboxWest': '--extract.reduceToBoundingBox.west',
            'interpolateMethod': '--interpolate.method',
            'interpolateProjString': '-interpolate.projString',
            'interpolateXAxisUnits': '--interpolate.xAxisUnit',
            'interpolateYAxisUnits': '--interpolate.yAxisUnit'}
        print(request.inputs)
        base = ['interpolateXAxisMin',
                'interpolateXAxisMax',
                'interpolateYAxisMin',
                'interpolateYAxisMax',
                'interpolateHorSteps']
        if all(x in list(request.inputs.keys()) for x in base):
            xmin = float(request.inputs['interpolateXAxisMin'][0].data)
            xmax = float(request.inputs['interpolateXAxisMax'][0].data)
            ymin = float(request.inputs['interpolateYAxisMin'][0].data)
            ymax = float(request.inputs['interpolateYAxisMax'][0].data)
            if xmax < xmin:
                xmin, xmax = xmax, xmin
            dx = (xmax-xmin)/float(request.inputs['interpolateHorSteps'][0].data)
            dy = (ymax-ymin)/float(request.inputs['interpolateHorSteps'][0].data)
            command += ' --interpolate.xAxisValues=%s,%s,...,%s' % (xmin, xmin+dx, xmax)
            command += ' --interpolate.yAxisValues=%s,%s,...,%s' % (ymin, ymin+dy, ymax)
        command += ' ' + '='.join([fimex_arguments[i] + '=' + request.inputs[i][0].data for i in request.inputs if i in list(fimex_arguments.keys())])
        #command += ' --extract.selectVariables='+' --extract.selectVariables='.join(request.inputs['selectVariables'][0].data)
        #command += ' --interpolate.xAxisValues=%s,%s,...,%s' % (xmin, xmin+dx, xmax)
        # TODO: exclude from initial string the values that require special treatment
        #response.outputs['commout'].data = 'Fimex command: ' + \
        #                                 ' '.join([i.metadata + '=' + i.identifier for i in request.inputs])
        response.outputs['commout'].data = command
        response.outputs['commout'].uom = UOM('unity')
        return response
