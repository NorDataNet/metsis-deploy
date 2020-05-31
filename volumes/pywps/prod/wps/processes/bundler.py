'''
Process to that takes a list of URIs and packages them together, 
returning a link to a zip file.

Should work with a request that looks like this:

normap-dev.met.no/cgi-bin/pywps.cgi?request=execute
&service=wps
&version=1.0.0
&identifier=bundler
&datainputs=[inputfiles="http%3A%2F%2Fthredds.met.no%2Fthredds%2FfileServer%2Fcryoclim%2Fmet.no%2Fosisaf-nh%2Fosisaf-nh_aggregated_ice_concentration_nh_polstere-100_197810010000.nc
";
useremail="cristina.luis%40met.no";
userid=1234]
&status=true
&storeExecuteResponse=true
'''

''' This works from commandline for testing:
(from the cgi-bin directory, in this case)
export REQUEST_METHOD=POST; cat ../requests/wps_execute_request-bundler.xml | ./pywps.cgi

or on server (cgi-bin is located at /usr/lib/cgi-bin)
export REQUEST_METHOD=POST; cat /usr/local/wps/requests/wps_execute_request-bundler.xml | ./pywps.cgi

or from anywhere using curl:
curl -X POST -d @wps_execute_request-bundler.xml http://normap-dev.met.no/cgi-bin/pywps.cgi
'''

# use urllib.quote_plus('url') to encode for GET parameters
#http://i.imgur.com/8ovwZ4V.jpg
#http%3A%2F%2Fi.imgur.com%2F8ovwZ4V.jpg

# TODO: use tempfile: https://docs.python.org/2/library/tempfile.html
# TODO: use @asreference for the output link
# TODO: figure out asynchronous get/status

import os
import types
import urllib
import urlparse
import logging
from zipfile import ZipFile
import datetime as dt

import pywps.config
from pywps.Process import WPSProcess

from utils import UserData, send_email

class Process(WPSProcess):

    def __init__(self):
        WPSProcess.__init__(self,
            identifier = "bundler", 
            title="File Bundler",
            version = "0.1",
            storeSupported = "true",
            statusSupported = "true",
            abstract='''This process will accept a list of URIs and will return a link 
                            to a zip file containing them bundled together.''',
            grassLocation =False)

        # TODO: unicode type? String types? list type?
        self.inputfiles = self.addLiteralInput(
                            identifier = 'inputfiles',
                            title = 'Input URIs',
                            type=types.StringType,
                            minOccurs=1,
                            maxOccurs=50
                            )
        self.userid = self.addLiteralInput(
                        identifier = 'userid',
                        title = 'User ID',
                        type = types.StringType,
                        minOccurs=1,
                        maxOccurs=1
                        )
        self.useremail = self.addLiteralInput(
                        identifier = 'useremail',
                        title = 'User email',
                        type = types.StringType,
                        minOccurs=1,
                        maxOccurs=1
                        )

        self.useridout = self.addLiteralOutput(identifier="useridout",
                                            title="User ID return",
                                            type=types.StringType)
        self.useremailout = self.addLiteralOutput(identifier="useremailout",
                                            title="User email return",
                                            type=types.StringType)

    def execute(self):
        logging.info('Trying to execute: {}'.format(self.inputfiles.getValue()))

        userid = self.userid.getValue()
        user = UserData(userid)

        output_path_base = pywps.config.getConfigValue("server", "outputPath") 
        output_filename_base = '{}_{:%Y%m%d%H%M%S}_bundle.zip'.format(userid, dt.datetime.now())           
        output_filename = os.path.join(output_path_base, output_filename_base)    

        self.status.set('Testing status', 10)

        request_info = {}
        data_sources = []

        for sourcefile in self.inputfiles.getValue():
            try:
                # Pull out the base part of the url and then just the final base path
                localfilename = urlparse.urlsplit(sourcefile)[2].split('/')[-1]
                filename, headers = urllib.urlretrieve(sourcefile)
            except Exception as e:
                # TODO: report that there was a problem getting that file
                logging.info('Problem here: {}'.format(e))
            else:
                with ZipFile(output_filename, 'a') as myzip:
                    myzip.write(filename, localfilename)

        output_url_base = pywps.config.getConfigValue("server", "outputUrl")
        output_url = urlparse.urljoin(output_url_base, output_filename_base)

        self.status.set('More testing status', 90)

        self.useridout.setValue(self.userid.getValue())
        self.useremailout.setValue(self.useremail.getValue())

        #user.write_to_xml()

        process_info = 'Your request is now available for download at: \n\n' + output_url
        send_email(self.useremail.getValue(), process_info)
        return

def data_source_from_uri(uri):
    ''' Return data source based on the uri of a file. '''


