import json
import os
import subprocess
from pywps import Process, LiteralInput, LiteralOutput, UOM
from pywps.wpsserver import temp_dir


__author__ = 'Massimo'

class Transformation(Process):
    def __init__(self):
        inputs = [LiteralInput('inputfile',
                               'Input File (http://thredds.met.no/thredds/dodsC/arome25/arome_metcoop_default2_5km_latest.nc)',
                               data_type='string',
                               min_occurs=1,
                               max_occurs=1),
                  LiteralInput('inputtype',
                               'Input type (nc4 default)',
                               data_type='string',
                               min_occurs=0,
                               max_occurs=1),
                  LiteralInput('reducetimeStart',
                               'Start time as UTC iso-string (e.g. 2016-02-03 00:00:00)',
                               data_type='string',
                               min_occurs=0,
                               max_occurs=1),
                  LiteralInput('reducetimeEnd',
                               'End time as UTC iso-string (e.g. 2016-02-04 00:00:00)',
                               data_type='string',
                               min_occurs=0,
                               max_occurs=1),
                  LiteralInput('reduceboxNorth',
                               'Reduce to bounding box north (85) [degree]',
                               data_type='string',
                               min_occurs=0,
                               max_occurs=1),
                  LiteralInput('reduceboxSouth',
                               'Reduce to bounding box south (-20) [degree]',
                               min_occurs=0,
                               max_occurs=1,
                               data_type='string'),
                  LiteralInput('reduceboxEast',
                               'Reduce to bounding box east (15) [degree]',
                               data_type='string',
                               min_occurs=0,
                               max_occurs=1),
                  LiteralInput('reduceboxWest',
                               'Reduce to bounding box west (-20) [degree]',
                               data_type='string',
                               min_occurs=0,
                               max_occurs=1),
                  LiteralInput('selectVariables',
                               'Extract variables (air_temperature_2m) [standard name], up to 50',
                               data_type='string',
                               min_occurs=0,
                               max_occurs=50),
                  LiteralInput('interpolateMethod',
                               'Interpolation method (nearestneighbor,bilinear,bicubic,coord_nearestneighbor,coord_\
                               kdtree,forward_max,forward_mean,forward_median,forward_sum).',
                               min_occurs=0,
                               max_occurs=1,
                               data_type='string'),
                  LiteralInput('interpolateProjString',
                               'proj4 input string describing the new projection (without \"\") \
                               (+proj=stere +lat_0=-90 +lon_0=0 +lat_ts=-70 +a=6378273 +rf=298.2794111 +units=m). \
                               Must be provided in order to do interpolation.',
                               data_type='string',
                               min_occurs=0,
                               max_occurs=1),
                  LiteralInput('interpolateXAxisMin',
                               'Minimum value for interpolation along X axis (e.g. -1000)',
                               data_type='string',
                               min_occurs=0,
                               max_occurs=1),
                  LiteralInput('interpolateXAxisMax',
                               'Maximum value for interpolation along X axis (e.g. 200)',
                               data_type='string',
                               min_occurs=0,
                               max_occurs=1),
                  LiteralInput('interpolateYAxisMin',
                               'Minimum value for interpolation along Y axis (e.g. -1000)',
                               data_type='string',
                               min_occurs=0,
                               max_occurs=1),
                  LiteralInput('interpolateYAxisMax',
                               'Maximum value for interpolation along Y axis (e.g. 200)',
                               data_type='string',
                               min_occurs=0,
                               max_occurs=1),
                  LiteralInput('interpolateHorSteps',
                               'Number of steps in horizontal interpolation (e.g. 100)',
                               data_type='string',
                               min_occurs=0,
                               max_occurs=1),
                  LiteralInput('interpolateXAxisUnits',
                               'unit of x-Axis given as udunits string, i.e. (m or degrees_east, default m)',
                               data_type='string',
                               min_occurs=0,
                               max_occurs=1),
                  LiteralInput('interpolateYAxisUnits',
                               'unit of y-Axis given as udunits string, i.e. (m or degrees_east, default m)',
                               data_type='string',
                               min_occurs=0,
                               max_occurs=1)
                  ]
        outputs = [LiteralOutput('commout',
                                 'Fimex command',
                                 data_type='string')
                   ]

        super(Transformation, self).__init__(
            self._handler,
            identifier='transformation',
            title='Transformation',
            abstract='Transform inputfile according to specified input arguments, \
                    using fimex (https://wiki.met.no/fimex/start). \
                    Resultfile available as download from urlout.',
            version='1.0',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        command = 'fimex '
        fimex_arguments={
            'inputfile':'--input.file', 
            'inputtype':'--input.type',
            'reducetimeStart':'--extract.reduceTime.start',
            'reducetimeEnd':'--extract.reduceTime.end',
            'reduceboxNorth':'--extract.reduceToBoundingBox.north',
            'reduceboxSouth':'--extract.reduceToBoundingBox.south',
            'reduceboxEast':'--extract.reduceToBoundingBox.east',
            'reduceboxWest':'--extract.reduceToBoundingBox.west',
            'interpolateMethod':'--interpolate.method',
            'interpolateProjString':'-interpolate.projString',
            'interpolateXAxisUnits':'--interpolate.xAxisUnit',
            'interpolateYAxisUnits':'--interpolate.yAxisUnit'}
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
