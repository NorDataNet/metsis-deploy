""" Process to call fimex using user-submitted input.
    Return new netcdf file, or text 

    EXAMPLE USAGE:

    BROWSER:
    http://localhost:8000/cgi-bin/pywps.cgi?service=wps
    &version=1.0.0
    &request=execute
    &identifier=useFimex
    &datainputs=[fimexcommand="fimex --input.file=blabla.nc"]

    BASH TERMINAL:
    curl "localhost:8000/cgi-bin/pywps.cgi?service=wps&version=1.0.0&request=execute&identifier=transformation&datainputs=\[fimexcommand=\"Dette%20er%20en%20test\"\]"
    
    Curl post works but must Ctrl-C out on localhost (works on normap. why?):
    curl -X POST -d @wps_execute_request-transformation.xml localhost:8000/cgi-bin/pywps.cgi 
    
    Best option for offline testing:
    export REQUEST_METHOD=POST; cat ../requests/wps_execute_request-transformation.xml | ./pywps.cgi


    TODO:
        - Generate proj4 string via GDAL, see phab.met.no/T2270
        - File types; grib (ec,wmo,ncep tables) 
        - Option for full command line? 
        - Output type as argument
        - interpolateVerticalSteps as argument


    Which variables do I need (generate example from normap.met.no/metamod by setting start and end date really late):
    --input.file
    --input.type
    --extract.reduceTime.end ('2016-02-03 00:00:00')
    --extract.reduceTime.start
    --extract.reduceToBoundingBox.north (85); also south,east,west
    --extract.selectVariables (repeat for all variables - how do I do this?)
    --interpolate.method (nearestneighbor,bilinear,bicubic,coord_nearestneighbor,coord_kdtree,forward_max,forward_mean,forward_median,forward_sum)
    --interpolate.projString (EPSG:3031,32633,32661,32761,3411,3412,3413,3995,4326) .. do I need entire string?
    --interpolate.xAxisValues (-2734375,-2673808.39646465,...,3261718.75)
    --interpolate.xAxisUnit (m) .. needed? Not necessarily correct
    --interpolate.yAxisValues (-2526855.46875,-2466288.86521465,...,3078613.28125)
    --interpolate.yAxisUnit (m) .. needed? Not necessarily correct
    --output.file
    --output.type

===========================================================
Name:          fimex_transformation.py
Author(s):     Trygve Halsne, Eivind Stoylen 
Modifications:
Copyright:     (c) Norwegian Meteorological Institute, 2017
===========================================================
"""

import time
import os
import types 
import urllib
import urlparse
import logging
import datetime as dt
import sys 
import re
import subprocess

import pywps.config
from pywps.Process import WPSProcess


class Process(WPSProcess):
    def __init__(self):
        # init process
        WPSProcess.__init__(
            self,
            identifier = "transformation", # must be same, as filename
            title="Transformation",
            version = "0.1",
            storeSupported = "true",
            statusSupported = "true",
            abstract="Transform inputfile according to specified input arguments, using fimex (https://wiki.met.no/fimex/start). Resultfile available as download from urlout.",
            grassLocation =False)

        self.inputfile = self.addLiteralInput(
            identifier = 'inputfile',
            title = 'Input File (http://thredds.met.no/thredds/dodsC/arome25/arome_metcoop_default2_5km_latest.nc)',
            type=types.StringType,
            minOccurs=1,
            maxOccurs=1
            )
        self.inputtype = self.addLiteralInput(
            identifier = 'inputtype',
            title = 'Input type (nc4 default)',
            type=types.StringType,
            minOccurs=0,
            maxOccurs=1
            )
        self.outputType = self.addLiteralInput(
            identifier = 'outputType',
            title = 'Output type (e.g. NetCDF, NetCDF-4, GeoTIFF). NetCDF-4 default',
            type=types.StringType,
            minOccurs=0,
            maxOccurs=1
            )
        self.reducetimeStart = self.addLiteralInput(
            identifier = 'reducetimeStart',
            title = 'Start time as UTC iso-string (e.g. 2016-02-03 00:00:00)',
            type=types.StringType,
            minOccurs=0,
            maxOccurs=1
            )
        self.reducetimeEnd = self.addLiteralInput(
            identifier = 'reducetimeEnd',
            title = 'End time as UTC iso-string (e.g. 2016-02-04 00:00:00)',
            type=types.StringType,
            minOccurs=0,
            maxOccurs=1
            )
        self.reduceboxNorth = self.addLiteralInput(
            identifier = 'reduceboxNorth',
            title = 'Reduce to bounding box north (85) [degree]',
            type=types.StringType,
            minOccurs=0,
            maxOccurs=1
            )
        self.reduceboxSouth = self.addLiteralInput(
            identifier = 'reduceboxSouth',
            title = 'Reduce to bounding box south (-20) [degree]',
            type=types.StringType,
            minOccurs=0,
            maxOccurs=1
            )
        self.reduceboxEast = self.addLiteralInput(
            identifier = 'reduceboxEast',
            title = 'Reduce to bounding box east (15) [degree]',
            type=types.StringType,
            minOccurs=0,
            maxOccurs=1
            )
        self.reduceboxWest = self.addLiteralInput(
            identifier = 'reduceboxWest',
            title = 'Reduce to bounding box west (-20) [degree]',
            type=types.StringType,
            minOccurs=0,
            maxOccurs=1
            )
        self.selectVariables = self.addLiteralInput(
            identifier = 'selectVariables',
            title = 'Extract variables (air_temperature_2m) [standard name], up to 50',
            type=types.StringType,
            minOccurs=0,
            maxOccurs=50
            )
        self.interpolateMethod = self.addLiteralInput(
            identifier = 'interpolateMethod',
            title = 'Interpolation method (nearestneighbor,bilinear,bicubic,coord_nearestneighbor,coord_kdtree,forward_max,forward_mean,forward_median,forward_sum).',
            type=types.StringType,
            minOccurs=0,
            maxOccurs=1
            )
        self.interpolateProjString = self.addLiteralInput(
            identifier = 'interpolateProjString',
            title = 'proj4 input string describing the new projection (without \"\") (+proj=stere +lat_0=-90 +lon_0=0 +lat_ts=-70 +a=6378273 +rf=298.2794111 +units=m). Must be provided in order to do interpolation.',
            type=types.StringType,
            minOccurs=0,
            maxOccurs=1
            )
        self.interpolateXAxisMin = self.addLiteralInput(
            identifier = "interpolateXAxisMin",
            title = 'Minimum value for interpolation along X axis (e.g. -1000)',
            type=types.StringType,
            minOccurs=0,
            maxOccurs=1
            )
        self.interpolateXAxisMax = self.addLiteralInput(
            identifier = "interpolateXAxisMax",
            title = 'Maximum value for interpolation along X axis (e.g. 200)',
            type=types.StringType,
            minOccurs=0,
            maxOccurs=1
            )
        self.interpolateYAxisMin = self.addLiteralInput(
            identifier = "interpolateYAxisMin",
            title = 'Minimum value for interpolation along Y axis (e.g. -1000)',
            type=types.StringType,
            minOccurs=0,
            maxOccurs=1
            )
        self.interpolateYAxisMax = self.addLiteralInput(
            identifier = "interpolateYAxisMax",
            title = 'Maximum value for interpolation along Y axis (e.g. 200)',
            type=types.StringType,
            minOccurs=0,
            maxOccurs=1
            )
        self.interpolateHorSteps = self.addLiteralInput(
            identifier = "interpolateHorSteps",
            title = 'Number of steps in horisontal interpolation (e.g. 100)',
            type=types.StringType,
            minOccurs=0,
            maxOccurs=1
            )
        self.interpolateVerSteps = self.addLiteralInput(
            identifier = "interpolateVerSteps",
            title = 'Number of steps in vertical interpolation (e.g. 100)',
            type=types.StringType,
            minOccurs=0,
            maxOccurs=1
            )
        self.interpolateXAxisUnits = self.addLiteralInput(
            identifier = 'interpolateXAxisUnits',
            title = 'unit of x-Axis given as udunits string, i.e. (m or degrees_east, default m)',
            type=types.StringType,
            minOccurs=0,
            maxOccurs=1
            )
        self.interpolateYAxisUnits = self.addLiteralInput(
            identifier = 'interpolateYAxisUnits',
            title = 'unit of y-Axis given as udunits string, i.e. (m or degrees_east, default m)',
            type=types.StringType,
            minOccurs=0,
            maxOccurs=1
            )


        self.urlout=self.addLiteralOutput(
            identifier = "urlout",
            title = "Download URL", 
            type=types.StringType
            )
        self.commout=self.addLiteralOutput(
            identifier = "commout",
            title = "Fimex command", 
            type=types.StringType
            )
        #self.interpolateXAxisValues = self.addLiteralInput(
        #    identifier = 'interpolateXAxisValues',
        #    title = 'string with values on x-Axis, use ... to continue, i.e. (10.5,11,...,29.5)',
        #    type=types.StringType,
        #    minOccurs=0,
        #    maxOccurs=1
        #    )
        #self.interpolateYAxisValues = self.addLiteralInput(
        #    identifier = 'interpolateYAxisValues',
        #    title = 'string with values on y-Axis, use ... to continue, i.e. (10.5,11,...,29.5)',
        #    type=types.StringType,
        #    minOccurs=0,
        #    maxOccurs=1
        #    )
        # self.errout=self.addLiteralOutput(
        #     identifier = "errout",
        #     title = "Error output", 
        #     type=types.StringType
        #     )



        

    def execute(self):
        #self.storeExecuteResponse("true")
        #self.status("true")

        #output = subprocess.check_output("pwd")
        #sys.stderr.write(output_filename) #Diagnosis

        #inCommand="time fimex --input.file=http://thredds.met.no/thredds/dodsC/arome25/arome_metcoop_default2_5km_latest.nc --input.type=nc4 --output.file=/home/eivinds/test/test.nc --output.type=nc4 --extract.selectVariables=air_temperature_2m --interpolate.latitudeValues=60 --interpolate.longitudeValues=10"
        #inCommand=inCommand.split()
        #self.testoutput.setValue(self.inputfile.getValue())
    

        #========================================
        #Collect input
        #========================================
        #inCommand=["fimex"]
        inCommand=["python3"]
        inCommand.append("/usr/local/dev/fimex_transformation_python/fimex_transformation.py")

        inCommand.append("--input.file="+self.inputfile.getValue())
        try:
            inType=self.inputtype.getValue()
            inCommand.append("--input.type="+inType)
        except: 
            inType="nc4"
            inCommand.append("--input.type="+inType)
        try:
            outType=self.outputType.getValue()
            inCommand.append("--output.type="+outType)
        except: 
            outType="nc4"
            inCommand.append("--output.type="+outType)
        try:
            inCommand.append("--extract.reduceTime.start="+self.reducetimeStart.getValue())
        except:
            pass
        try:
            inCommand.append("--extract.reduceTime.end="+self.reducetimeEnd.getValue())
        except:
            pass
        try:
            inCommand.append("--extract.reduceToBoundingBox.north="+self.reduceboxNorth.getValue())
        except:
            pass
        try:
            inCommand.append("--extract.reduceToBoundingBox.south="+self.reduceboxSouth.getValue())
        except:
            pass
        try:
            inCommand.append("--extract.reduceToBoundingBox.east="+self.reduceboxEast.getValue())
        except:
            pass
        try:
            inCommand.append("--extract.reduceToBoundingBox.west="+self.reduceboxWest.getValue())
        except:
            pass
        try:
            for variable in self.selectVariables.getValue():
                inCommand.append("--extract.selectVariables="+variable)
        except:
            pass
        try:
            inCommand.append("--interpolate.method="+self.interpolateMethod.getValue())
        except:
            pass
        try:
            inCommand.append("--interpolate.projString="+self.interpolateProjString.getValue())
        except:
            pass
        try:
            xmin=float(self.interpolateXAxisMin.getValue())
            xmax=float(self.interpolateXAxisMax.getValue())
            if xmax<xmin:
                xmin,xmax=xmax,xmin
            dx=(xmax-xmin)/float(self.interpolateHorSteps.getValue())
            inCommand.append("--interpolate.xAxisValues="+str(xmin)+","+str(xmin+dx)+",...,"+str(xmax))
        except:
            pass
        try:
            ymin=float(self.interpolateYAxisMin.getValue())
            ymax=float(self.interpolateYAxisMax.getValue())
            if ymax<ymin:
                ymin,ymax=ymax,ymin
            dy=(ymax-ymin)/float(self.interpolateHorSteps.getValue())
            inCommand.append("--interpolate.yAxisValues="+str(ymin)+","+str(ymin+dy)+",...,"+str(ymax))
        except:
            pass
        try:
            inCommand.append("--interpolate.xAxisUnit="+self.interpolateXAxisUnits.getValue())
        except:
            inCommand.append("--interpolate.xAxisUnit=m")
        try:
            inCommand.append("--interpolate.yAxisUnit="+self.interpolateYAxisUnits.getValue())
        except:
            inCommand.append("--interpolate.yAxisUnit=m")


        #========================================
        #Create output
        #========================================
        output_path_base = pywps.config.getConfigValue("server", "outputPath")
        if outType=="GeoTIFF":
            output_filename_base =  '{:%Y%m%d%H%M%S}_transform.tif'.format(dt.datetime.now())
        else:
            output_filename_base =  '{:%Y%m%d%H%M%S}_transform.nc'.format(dt.datetime.now())

        output_filename = os.path.join(output_path_base, output_filename_base)
        
        #========================================
        # CREATING fimex command for showing size of outputfile
        #========================================
	sizecom = inCommand[:] #For file size testing
        sizecom.remove("python3")
        sizecom.remove("/usr/local/dev/fimex_transformation_python/fimex_transformation.py")
        sizecom.insert(0,'fimex')
        sizecom.append("--output.printSize")
        logging.info("Size command: "+" ".join(sizecom))

        inCommand.append("--output.file="+output_filename)
        #inCommand.append("--output.type="+outType)

        #========================================
        # Run Fimex
        #========================================
        self.status.set("Fimex started")
        logging.info("inCommand: "+" ".join(inCommand))


        while True:
            self.commout.setValue(" ".join(inCommand))
	    try:
	        # Make sure file output is not too large
	        fileSizeMax=30000 #Size in MB (before compression)
	        fileSize=subprocess.check_output(sizecom,stderr=subprocess.STDOUT) 
	        fileSize=int(re.search(r'\d+',fileSize).group())
	        if fileSize>fileSizeMax:
		    return "Approximate file size "+str(fileSize)+" MB too big. Please stay below "+str(fileSizeMax)+" MB"
                sys.stdout.flush()
                #time.sleep(30)
                subprocess.check_output(inCommand,stderr=subprocess.STDOUT)
            except Exception as err:
                #return err  #TEST
	        if (hasattr(err,"returncode") and err.returncode==-6) and not ("unlimitedTime.ncml" in " ".join(inCommand)):
		    # Aggregated files fix, see https://wiki.met.no/fimex/faq -> "OpENDAP and slicing"
                    # NOTE: "--input.config" is not implemented in fimex_transformation.py, hence swithcing to use fimex natively
                    inCommand.remove("python3")
                    inCommand.remove("/usr/local/dev/fimex_transformation_python/fimex_transformation.py")
                    inCommand.insert(0,'fimex')
		    inCommand.append("--input.config=/usr/local/wps/etc/unlimitedTime.ncml")	   
 		    sizecom.append("--input.config=/usr/local/wps/etc/unlimitedTime.ncml")
		    continue
           	self.status.set('{}'.format(err.output,))
            	return "Fimex error: {}".format(err.output,)+"\n From fimex command: {}".format(" ".join(err.cmd),)
            else:
            	self.urlout.setValue("http://157.249.177.189"+output_filename[13:])
            	self.status.set("Fimex completed successfully")
            	return 0
