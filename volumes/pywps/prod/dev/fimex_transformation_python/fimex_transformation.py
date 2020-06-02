#!/usr/bin/python3

""" Script containing class and methods for using the python wrapper for
    FIMEX (i.e. pyfimex0) for file manipulation. The availible methods are

    Extraction:
        - Reduction of temporal and spatial dimension(s)
        - Reduction of latitude/longitude bounding box
        - Extraction of desired variables

    Interpolation:
        - Interpolate data in a given projection and spatial resolution

    File writing:
		- Write file to supported format. Supporting NetCDF and GeoTiff
          at the moment

	USAGE:
		Either use regular fimex commands* or provide arguments as:

        fimex_transformation.py [-h]
                                -f INPUT.FILE - MANDATORY
								-o OUTPUT.FILE - MANDATORY
                                [-ft INPUT.TYPE]
                                [-erts [EXTRACT.REDUCETIME.START [EXTRACT.REDUCETIME.START ...]]]
                                [-erte [EXTRACT.REDUCETIME.END [EXTRACT.REDUCETIME.END ...]]]
                                [-ertbbn EXTRACT.REDUCETOBOUNDINGBOX.NORTH]
                                [-ertbbe EXTRACT.REDUCETOBOUNDINGBOX.EAST]
                                [-ertbbs EXTRACT.REDUCETOBOUNDINGBOX.SOUTH]
                                [-ertbbw EXTRACT.REDUCETOBOUNDINGBOX.WEST]
                                [-esvar EXTRACT.SELECTVARIABLES]
                                [-intxau INTERPOLATE.XAXISUNIT]
                                [-intyau INTERPOLATE.YAXISUNIT]
                                [-intmeth INTERPOLATE.METHOD]
                                [-intproj INTERPOLATE.PROJSTRING [INTERPOLATE.PROJSTRING ...]]
                                [-intxaval INTERPOLATE.XAXISVALUES]
                                [-intyaval INTERPOLATE.YAXISVALUES]
								[-ot OUTPUT.TYPE]

		 * NOTE: if using regular fimex commands, any input argument containing whitespaces must
		   either be given as e.g.:
				--extract.reduceTime.start 2017-06-09 10:30:21
		   or
				--extract.reduceTime.start="2017-06-09 10:30:21"
		   and NOT as
				--extract.reduceTime.start=2017-06-09 10:30:21

	COMMENTS:
		- Method for reducing dimensions is not implemented yet, since this
		  is not an option in the "transform" site/panel in ADC (Arctic Data Center).
		- Write to GeoTIFF: Parses dimensions based NetCDF CF convention.
		- Only reads NetCDF products at the moment
		- If -intproj (i.e. proj4 string) is not given, then no projection information
		  is provided in GeoTIFF. But if stored as NetCDF, this information is kept.
        - Reformatting to GeoTiff does not work for rasterbands with more than two
          dimensions.

===========================================================
Name:          fimex_transformation.py
Author(s):     Trygve Halsne 25.09.2017 (dd.mm.YYYY)
Modifications:
Copyright:     (c) Norwegian Meteorological Institute, 2017
===========================================================
"""

import pyfimex0
import argparse
import numpy as np
from osgeo import gdal, osr, gdal_array
import sys

class Transform:
    """ Class utilizing the pyfimex0 module for file manipulation."""
    def __init__(self, inputFile, outputFile, inputType=None, reduceTimeStart=None,
                 reduceTimeEnd=None, reduceBBNorth=None,
                 reduceBBEast=None, reduceBBSouth=None, reduceBBWest=None,
                 selectVariables=None, interpolateXAxisUnit=None, interpolateYAxisUnit=None,
                 interpolateMethod=None, interpolateProjString=None,
                 interpolateXAxisValues=None, interpolateYAxisValues=None, outputType=None):
        self.inputFile = inputFile
        self.outputFile = outputFile
        self.inputType = inputType
        self.reduceTimeStart = reduceTimeStart
        self.reduceTimeEnd =  reduceTimeEnd
        self.reduceBBNorth =reduceBBNorth
        self.reduceBBEast = reduceBBEast
        self.reduceBBSouth =reduceBBSouth
        self.reduceBBWest =reduceBBWest
        self.selectVariables =selectVariables
        self.interpolateXAxisUnit =interpolateXAxisUnit
        self.interpolateYAxisUnit =interpolateYAxisUnit
        self.interpolateMethod = interpolateMethod
        self.interpolateProjString =interpolateProjString
        self.interpolateXAxisValues =interpolateXAxisValues
        self.interpolateYAxisValues =interpolateYAxisValues
        self.outputType = outputType

        #========================================================
        # Read file using pyfimex0
		# NOTE: should be self.inputType instead of 'netcdf'...
        #========================================================

        try:
            self.fimex_reader = pyfimex0.createFileReader('netcdf', self.inputFile)
            print("\nStart manipulating file")
        except:
            print("\nCould not open file in fimex_reader. Hence terminating")
            sys.exit([1])

        #========================================================
        # Extract values using pyfimex0 by means of reducing
        # dimension(s) and/or extraxting variables
        #========================================================
        self.extractor = self.extractFromFile()

        #========================================================
        # Parse the time, x, y and/or z (NOTE: z not implemented)
        #========================================================
        cdm = self.extractor.getCDM() # get Common Data Model
        time_dimensions = ['time', 't']
        east_dimensions = ['x', 'X', 'xc','xtrack','ncols','pixel']
        north_dimensions = ['y', 'Y', 'yc','atrack','nrows', 'line']
        for dimension in cdm.getDimensionNames():
            if dimension in time_dimensions:
                self.time_dim = dimension
            elif dimension in east_dimensions:
                self.east_dim = dimension
            elif dimension in north_dimensions:
                self.north_dim = dimension

        #========================================================
        # Interpolate to preferred projection
        #========================================================
        self.interpolator = self.interpolateFile()

        #========================================================
        # Write manipulated input file to disk
        #========================================================
        write_ok = self.writeToFile()
        if write_ok:
            print('\nSuccessful writing of input file:' +
                  ' %s to: %s, using %s format' %(self.inputFile, self.outputFile, self.outputType))
        else:
            print('\nWriting of input file:' +
                  ' %s to: %s (format: %s ), did not work.' %(self.inputFile, self.outputFile, self.outputType))


    #========================================================
    # Class methods
    #========================================================
    def writeToFile(self):
        """ Method for writing data to file. NetCDF is default method."""
        if self.outputType == 'GeoTIFF':
            print('Writing input file to GeoTiff.')
            cdm = self.interpolator.getCDM() #Common Data Model

            # Get dimensions
            dims = {}
            for dimension in cdm.getDimensionNames():
                try:
                    dims[dimension] = self.interpolator.getDataSlice(dimension,0)
                except RuntimeError as e:
                    print(e)
                    dims[dimension] = cdm.getDimension(dimension)

            # Get output variables datasets
            var_ds = {}

            if self.selectVariables:
                nBands = len(self.selectVariables)
                for variable in self.selectVariables:
                    var_ds[variable] = self.interpolator.getDataSlice(variable,0)
            else:
                nBands = 0
                for variable in cdm.getVariableNames():
                    if not cdm.hasDimension(variable) and not variable=='lon' and not variable=='lat':
                        if self.interpolator.getDataSlice(variable,0).size() > 1:
                            #print(variable)
                            var_ds[variable] = self.interpolator.getDataSlice(variable,0)
                            nBands += 1

            # Get projection for output datasets
            gdal_projection = osr.SpatialReference()
            gdal_projection.ImportFromProj4(self.interpolateProjString)
            # Get geo transform for output datasets
            try:
                x = dims[self.east_dim].values()
                y = dims[self.north_dim].values()
                dx = abs(x[0]-x[1])
                dy = abs(y[0]-y[1])
                geoTransform = (x.min(), dx, 0.0, y.max(), 0.0, -dy)
                got_geoTransform = True
            except Exception as e:
                print(e)
                got_geoTransform = False
            print([self.east_dim])

            # write to file
            #xn = dims[self.east_dim].size()
            #yn = dims[self.north_dim].size()
            xn = cdm.getDimension(self.east_dim).getLength()
            yn = cdm.getDimension(self.north_dim).getLength()
            #yn = dims[self.north_dim].size()

            if hasattr(var_ds[list(var_ds)[0]].values(), 'dtype'):
                arrayType = var_ds[list(var_ds)[0]].values().dtype
                dataType = gdal_array.NumericTypeCodeToGDALTypeCode(arrayType)
            else:
                dataType = gdal.GDT_Float32

            driver = gdal.GetDriverByName('GTiff')
            driver_metadata = driver.GetMetadata()


            dst_ds = driver.Create(self.outputFile, xn, yn, nBands, dataType)
            if got_geoTransform:
                dst_ds.SetGeoTransform(geoTransform)
            dst_ds.SetProjection(gdal_projection.ExportToWkt())
            for i, variable in enumerate(list(var_ds)):
                tmp_attrib_dict = {}
                #print(i,variable,xn,yn)
                band_attrib = cdm.getAttributeNames(variable)
                for attr in band_attrib:
                    tmp_attrib = cdm.getAttribute(variable,attr)
                    tmp_attrib_dict[attr] = tmp_attrib.getStringValue()
                #print(band_attrib)
                #print(variable)
                #print(var_ds[variable].values().shape)
                #print(xn, yn)
                #print(var_ds[variable].values())
                array = np.flipud(var_ds[variable].values().reshape(yn,xn))
                #print(array.shape)
                #print(dst_ds.RasterXSize,dst_ds.RasterYSize)
                dst_ds.GetRasterBand(i+1).WriteArray(array)
                dst_ds.GetRasterBand(i+1).SetMetadata(tmp_attrib_dict)
                #dst_ds.GetRasterBand(i+1).SetMetadata(sd_ds.GetRasterBand(1).GetMetadata())

            dst_ds.FlushCache()  # Write to disk.

            # Closing all opened products
            dst_ds = None
            return True

        elif self.outputType == 'NetCDF' or self.outputType == 'NetCDF-4':
            print('Writing input file to NetCDF.')

            # Parsing outputType to nc or nc4 to be compliant with fimex
            if self.outputType == 'NetCDF':
                ot = 'nc'
            elif self.outputType == 'NetCDF-4':
                ot = 'nc4'

            try:
                pyfimex0.createFileWriter(self.interpolator, ot, self.outputFile)
                return True
            except:
                print('Did not manage to write %s to NetCDF' % self.outputFile)
                return False
        else:
            print('Output type/format: %s , is not supported at the moment' % self.outputType)
            return False

    def extractFromFile(self):
        """ Method for reducing dimension, i.e. temporal and/or spatial in
            addition to reduce number of variables."""
        extractor = pyfimex0.createExtractor(self.fimex_reader)

        # Check reductions to be made based on input values
        if self.reduceBBNorth and self.reduceBBEast and self.reduceBBSouth and self.reduceBBWest:
            reduce_latLonBoundingBox = True
        else:
            reduce_latLonBoundingBox = False

        if self.selectVariables:
            reduce_variables = True
        else:
            reduce_variables = False

        # Reduce temporal extent #NOTE COMMENTED OUT!
        if self.reduceTimeStart and self.reduceTimeEnd:
            print('Reducing temporal extent does not work at the moment')
            #extractor.reduceTimeStartEnd(self.reduceTimeStart, self.reduceTimeEnd)

        # Reduce dimension - NOTE: Not implemented..
        reduce_dim = False
        if reduce_dim:
            extractor.reduceDimensionStartEnd('time', [self.reduceTimeStart, self.reduceTimeEnd])
            extractor.reduceDimension('x', [0, 1, 3])
            extractor.reduceDimension('y', 1, 2)

        # Reduce latitude/longitude Bounding Box
        if reduce_latLonBoundingBox:
            print('Reducing latitude and longitude bounding box')
            extractor.reduceLatLonBoundingBox(self.reduceBBSouth, self.reduceBBNorth,
                self.reduceBBWest, self.reduceBBEast)
        #print("DEBUG",extractor.getDataSlice('B2',0).values())

        # Reduce number of variables
        if reduce_variables:
            print('Reducing number of variables from:')
            print(extractor.getCDM().getVariableNames())
            print('to')
            print(self.selectVariables)
            extractor.selectVariables(self.selectVariables)

        return extractor

    def interpolateFile(self):
        """ Method for interpolating selected bands to desired resolution"""

        # Parsing interpolation method nearestneighbor to nearest_neighbor
        if self.interpolateMethod == 'nearestneighbor':
            self.interpolateMethod = 'nearest_neighbor'

        validInterpolationMethods = {'BICUBIC':pyfimex0.InterpolationMethod.BICUBIC,
        'BILINEAR':pyfimex0.InterpolationMethod.BILINEAR,
        'COORD_NN':pyfimex0.InterpolationMethod.COORD_NN,
        'COORD_NN_KD':pyfimex0.InterpolationMethod.COORD_NN_KD,
        'FORWARD_MAX':pyfimex0.InterpolationMethod.FORWARD_MAX,
        'FORWARD_MEAN':pyfimex0.InterpolationMethod.FORWARD_MEAN,
        'FORWARD_MEDIAN':pyfimex0.InterpolationMethod.FORWARD_MEDIAN,
        'FORWARD_MIN':pyfimex0.InterpolationMethod.FORWARD_MIN,
        'FORWARD_SUM':pyfimex0.InterpolationMethod.FORWARD_SUM,
        'FORWARD_UNDEF_MAX':pyfimex0.InterpolationMethod.FORWARD_UNDEF_MAX,
        'FORWARD_UNDEF_MEAN':pyfimex0.InterpolationMethod.FORWARD_UNDEF_MEAN,
        'FORWARD_UNDEF_MEDIAN':pyfimex0.InterpolationMethod.FORWARD_UNDEF_MEDIAN,
        'FORWARD_UNDEF_MIN':pyfimex0.InterpolationMethod.FORWARD_UNDEF_MIN,
        'FORWARD_UNDEF_SUM':pyfimex0.InterpolationMethod.FORWARD_UNDEF_SUM,
        'NEAREST_NEIGHBOR':pyfimex0.InterpolationMethod.NEAREST_NEIGHBOR}

        interpolator = pyfimex0.createInterpolator(self.extractor)

        if self.interpolateProjString:
            if (self.interpolateXAxisValues and self.interpolateXAxisUnit) or (self.interpolateYAxisValues and self.interpolateYAxisUnit):
                interpolate = True
            else:
                interpolate = False
        else:
            interpolate = False

        if interpolate: # NOTE - should have two options, i.e. change proj and extr lat/lon array
            print('INTERPOLATING file')

            # Parse input values
            if self.interpolateXAxisValues:
                xAxisValues = self.interpolateXAxisValues.split(',')
                x0 = (float(xAxisValues[0]))
                x1 = (float(xAxisValues[-1]))
                dx = (float(xAxisValues[1])-x0)
                nx = round((x1-x0)/dx)
            else:
                cdm = interpolator.getCDM()
                # Get dimensions
                dims = {}
                for dimension in cdm.getDimensionNames():
                    try:
                        dims[dimension] = interpolator.getDataSlice(dimension,0)
                    except RuntimeError as e:
                        print(e)
                        dims[dimension] = cdm.getDimension(dimension)

                 # Get geo transform for output datasets
                x = dims[self.east_dim].values()
                x0 = (float(x[0]))
                x1 = (float(x[-1]))
                dx = (float(abs(x[0]-x[1])))
                nx = round((x1-x0)/dx)


            if self.interpolateYAxisValues:
                yAxisValues = self.interpolateYAxisValues.split(',')
                y0 = (float(yAxisValues[0]))
                y1 = (float(yAxisValues[-1]))
                dy = (float(yAxisValues[1])-y0)
                ny = round((y1-y0)/dy)
            else:
                cdm = interpolator.getCDM()
                # Get dimensions
                dims = {}
                for dimension in cdm.getDimensionNames():
                    try:
                        dims[dimension] = interpolator.getDataSlice(dimension,0)
                    except RuntimeError as e:
                        print(e)
                        dims[dimension] = cdm.getDimension(dimension)

                 # Get geo transform for output datasets
                y = dims[self.east_dim].values()
                y0 = (float(y[0]))
                y1 = (float(y[-1]))
                dy = (float(abs(y[0]-y[1])))
                ny = round((y1-y0)/dy)

            print(np.linspace(x0,x1+dx,nx))
            print(np.linspace(y0,y1+dy,ny))
            try:
                #print(x0,x1,dx,y0,y1,dy)
                interpolator.changeProjection(validInterpolationMethods[self.interpolateMethod.upper()],
                                      self.interpolateProjString,
                                      #range(x0,x1+dx,dx),   # x-axis values
                                      #range(y0,y1+dy,dy), # y-axis values
                                      np.linspace(x0,x1+dx,nx),   # x-axis values
                                      np.linspace(y0,y1+dy,ny), # y-axis values
                                      self.interpolateXAxisUnit, # x-axis unit
                                      self.interpolateYAxisUnit# y-axis unit
								      )
            except Exception as e:
                print(e)
        return interpolator




#========================================================
# Class methods
    #========================================================
class MyAction(argparse.Action):
    """ Class for parsing input argumets through argparse."""
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, ' '.join(values))

def main():
    """ Main method parsing input arguments and running Transform class."""

    # Read input values from command line using argparser
    parser = argparse.ArgumentParser(description='Transform NetCDF file using fimex.')
    parser.add_argument("-f", "--input.file", help='Input file name', type=str, required=True)
    parser.add_argument("-ft", '--input.type', help=('Input file type, e.g. nc, nc4, ncml,' +
        'felt, grib1, grib2, wdb'), type=str , default="nc4")
    parser.add_argument("-erts", '--extract.reduceTime.start', help=('Start-time as ISO-string'),
        type=str , default=None, nargs='*', action=MyAction)
    parser.add_argument("-erte", '--extract.reduceTime.end', help=('End-time by ISO-string'),
        type=str , default=None, nargs='*', action=MyAction)
    parser.add_argument("-ertbbn", '--extract.reduceToBoundingBox.north',
        help=('geographical bounding-box in degree'), type=float , default=None)
    parser.add_argument("-ertbbe", '--extract.reduceToBoundingBox.east',
        help=('geographical bounding-box in degree'), type=float , default=None)
    parser.add_argument("-ertbbs", '--extract.reduceToBoundingBox.south',
        help=('geographical bounding-box in degree'), type=float , default=None)
    parser.add_argument("-ertbbw", '--extract.reduceToBoundingBox.west',
        help=('geographical bounding-box in degree'), type=float , default=None)
    parser.add_argument("-esvar", '--extract.selectVariables',
        help=('select only those variables'), type=str , default=None, action='append')
    parser.add_argument("-intxau", '--interpolate.xAxisUnit',
        help=('unit of x-Axis given as udunits string, i.e. m or degrees_east'),
        type=str , default='m')
    parser.add_argument("-intyau", '--interpolate.yAxisUnit',
        help=('unit of y-Axis given as udunits string, i.e. m or degrees_east'),
        type=str , default='m')
    parser.add_argument("-intmeth", '--interpolate.method',
        help=('interpolation method, one of nearestneighbor,'+
        ' bilinear, bicubic, coord_nearestneighbor, coord_kdtree,'+
        ' forward_max, forward_min, forward_mean, forward_median,'+
        ' forward_sum or forward_undef_*'),
        type=str , default='nearestneighbor')
    parser.add_argument("-intproj", '--interpolate.projString',
        help=('proj4 input string describing the new projection'),
        type=str , default=None, nargs='+', action=MyAction)
    parser.add_argument("-intxaval", '--interpolate.xAxisValues',
        help=('string with values on x-Axis, use ... to continue, i.e. 10.5,11,...,29.5,'+
        ' see Fimex::SpatialAxisSpec for full definition'), type=str , default=None)
    parser.add_argument("-intyaval", '--interpolate.yAxisValues',
        help=('string with values on y-Axis, use ... to continue, i.e. 10.5,11,...,29.5,'+
        ' see Fimex::SpatialAxisSpec for full definition'), type=str , default=None)
    parser.add_argument("-o", '--output.file', help='Output file name', type=str ,
        default=None, required=True)
    parser.add_argument("-ot", '--output.type', help=('filetype of output file, e.g. NetCDF, NetCDF-4,' +
    ' GeoTIFF'), type=str , default='NetCDF-4')

    # Parse input arguments and run Transform class
    args = parser.parse_args()

    inputFile = getattr(args,'input.file')
    inputType = getattr(args,'input.type')
    reduceTimeStart = getattr(args,'extract.reduceTime.start')
    reduceTimeEnd = getattr(args,'extract.reduceTime.end')
    reduceBBNorth = getattr(args,'extract.reduceToBoundingBox.north')
    reduceBBEast = getattr(args,'extract.reduceToBoundingBox.east')
    reduceBBSouth = getattr(args,'extract.reduceToBoundingBox.south')
    reduceBBWest = getattr(args,'extract.reduceToBoundingBox.west')
    selectVariables = getattr(args,'extract.selectVariables')
    interpolateXAxisUnit = getattr(args,'interpolate.xAxisUnit')
    interpolateYAxisUnit = getattr(args,'interpolate.yAxisUnit')
    interpolateMethod = getattr(args,'interpolate.method')
    interpolateProjString = getattr(args,'interpolate.projString')
    interpolateXAxisValues = getattr(args,'interpolate.xAxisValues')
    interpolateYAxisValues = getattr(args,'interpolate.yAxisValues')
    outputFile = getattr(args,'output.file')
    outputType = getattr(args,'output.type')

    transformer = Transform(inputFile, outputFile, inputType, reduceTimeStart,
                     reduceTimeEnd, reduceBBNorth,
                     reduceBBEast, reduceBBSouth, reduceBBWest,
                     selectVariables, interpolateXAxisUnit, interpolateYAxisUnit,
                     interpolateMethod, interpolateProjString,
                     interpolateXAxisValues, interpolateYAxisValues, outputType)


if __name__ == '__main__':
    main()



"""
Usage example:

# run 
# python3 fimex_transformation.py --input.file=S1B_IW_GRDM_1SDV_20171117T053116_20171117T053148_008317_00EB7D_AFEE.nc --input.type=nc4 --output.file=test.tif --output.type=GTIFF --extract.selectVariables=Amplitude_VH
# run 
pythoin3 fimex_transformation.py --input.file=https://nbstds.met.no/thredds/dodsC/NBS/S2B/2018/02/08/S2B_MSIL1C_20180208T124259_N0206_R095_T28WFU_20180208T131236.nc --input.type=nc4 --output.file=test.tif --output.type=GTIFF --extract.selectVariables=Amplitude_VH

# https://thredds.met.no/thredds/dodsC/aromearcticlatest/arome_arctic_pp_2_5km_latest.nc
# run 
python3 fimex_transformation.py --input.file=https://thredds.met.no/thredds/dodsC/aromearcticlatest/arome_arctic_pp_2_5km_latest.nc --input.type=nc --extract.selectVariables=wind_speed_of_gust --extract.selectVariables=air_temperature_2m --interpolate.method=nearestneighbor --interpolate.projString="+proj=stere +lat_0=-90 +lon_0=0 +lat_ts=-71 +ellps=WGS84 +datum=WGS84 +units=m" --interpolate.xAxisValues=16207098.2916,16506161.1418,...,46113383.3163 --interpolate.yAxisValues=26623574.2709,27276488.7471,...,91915021.8897 --interpolate.xAxisUnit=m --interpolate.yAxisUnit=m --output.file=aromeArcticTransformed.nc --output.type=nc4

# run 
python3 fimex_transformation.py --input.file=https://thredds.met.no/thredds/dodsC/aromearcticlatest/arome_arctic_pp_2_5km_latest.nc --input.type=nc --extract.reduceToBoundingBox.north=75 --extract.reduceToBoundingBox.south=64 --extract.red
uceToBoundingBox.east=10 --extract.reduceToBoundingBox.west=60 --extract.selectVariables=wind_speed_of_gust --extract.selectVariables=air_temperature_2m --output.file=aromeArcticTransformed_2.nc --output.type=nc4 --extract.reduceTime.start='2018-02-16T04:00:00' --extract.reduceTime.end='2018-02-17T20:30:00'
"""
