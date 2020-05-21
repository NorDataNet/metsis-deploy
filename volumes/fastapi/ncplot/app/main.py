import requests
from fastapi import FastAPI, HTTPException, Query  # BackgroundTasks
from pathlib import Path
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

try:
    from pydantic.networks import EmailStr
except ImportError:
    from pydantic.types import EmailStr

from app.nc_plot import get_plottable_variables, create_page
from app.utils import get_data
from bokeh.embed import json_item  # components
import json

from typing import List
from fastapi import File, UploadFile, Response
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

import os
# from fastapi.responses import StreamingResponse
import csv
from json2html import *
import zipfile
from itsdangerous import TimestampSigner
from itsdangerous import BadSignature, SignatureExpired

import re
import uuid
import base64

import pandas as pd
from functools import reduce

from fastapi import Request
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse


def getstaticfolder():
    current_file = Path(__file__)
    current_file_dir = current_file.parent
    project_root = current_file_dir.parent
    project_root_absolute = project_root.resolve()
    static_root_absolute = project_root_absolute / "static"
    return static_root_absolute

class Item(BaseModel):
    url: str
    get: str
    variable: str = None


app = FastAPI(title="NC Plot",
              description="Prototype API for plotting, sub-setting and download of NetCDF time-series and 1D profiles.",
              version="0.0.1",
              )


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_PROCESSING_SECOND = 600

app.mount("/static", StaticFiles(directory="./app/static"), name="static")
templates = Jinja2Templates(directory="/app/templates")

@app.get("/download/{id}")
async def read_item(request: Request, id: str):
    # TODO: check that the file  exist, if yes ..
    s = TimestampSigner('secret-key')
    try:
        filename = s.unsign(id, max_age=50).decode()
        return templates.TemplateResponse("download.html", {"request": request, "id": filename})
    except SignatureExpired:
        try:
            os.remove(Path(os.environ['DOWNLOAD_DIR'], str(id.rsplit('.', 2)[0])))
        except OSError:
            pass
        return templates.TemplateResponse("expired.html", {"request": request, "id": id})
    except BadSignature:
        return templates.TemplateResponse("error.html", {"request": request, "id": id})


@app.get("/ncplot/download")
async def download(*,
                   resource_url: str = Query(...,
                                             title="Resource URL",
                                             description="URL to a NetCDF resource"),
                   variable: List[str] = Query(None,
                                               title="Variable name",
                                               description="List of NetCDF Variable names"),
                   output_format: str = Query(None,
                                              title="output format",
                                              description="output format",
                                              regex='^(csv|nc)$')):
    # list of variables
    variables_items = {'variables': variable}
    # check if the user provided valid parameters
    valid_vars = []
    for i in variables_items['variables']:

        plottable_variables = get_plottable_variables(resource_url)
        axis = list(plottable_variables.keys())[0]
        if i in plottable_variables[axis]:
            valid_vars.append(i)
        else:
            print('removed:', i)
    # create an empty list to append one dataframe for each variables
    print(valid_vars)
    data = []
    for i in valid_vars:
        # get_data is handling only variable selection at the moment
        # TODO: add an option in get_data to allow time-selection
        #  a good candidate for this is by using pandas time-range slicing
        #  it will require one extra parameters in the URL request,
        #  to handle start/end time selection
        data.append(get_data(resource_url, i))
    # merge the requested data in a single dataframe
    # suffixes = ['_'+i.variable_metadata['standard_name'] for i in data]
    try:
        df_final = reduce(lambda left, right: pd.merge(left, right, suffixes=(False, False), on=data[0].index.name), data)
    except ValueError:
        suffixes = ['_' + i.variable_metadata['standard_name'] for i in data]
        df_final = reduce(lambda left, right: pd.merge(left, right, suffixes=suffixes, on=data[0].index.name), data)
    # generate a uuid for the filename
    if output_format == 'csv':
        rv = base64.b64encode(uuid.uuid4().bytes).decode('utf-8')
        unique = re.sub(r'[\=\+\/]', lambda m: {'+': '-', '/': '_', '=': ''}[m.group(0)], rv)
        filename = str(unique) + '.' + str(output_format) + '.zip'
        # TODO: read the secret-key from a configuration file
        s = TimestampSigner('secret-key')
        download_token = s.sign(filename).decode()
        # this stores the data in the 'DOWNLOAD_DIR' which is set in the docker-compose.yml instruction
        outfile = Path(os.environ['DOWNLOAD_DIR'], str(filename))
        compression_opts = dict(method='zip', archive_name='dataset' + '.csv')
        df_final.to_csv(outfile, compression=compression_opts)
        with open('metadata.csv', 'w', newline="") as csv_file:
            writer = csv.writer(csv_file)
            for key, value in data[0].dataset_metadata.items():
                writer.writerow([key, value])
        with open('metadata.html', 'w') as f:
            f.write(json2html.convert(json={**data[0].dataset_metadata},
                                      table_attributes="id=\"metadata\" "))
        zip = zipfile.ZipFile(outfile, 'a')
        zip.write('metadata.html', os.path.basename('metadata.html'))
        zip.write('metadata.csv', os.path.basename('metadata.csv'))
        zip.close()
        # the line below will return a direct download
        # return FileResponse(path=outfile, filename='dataset.csv.zip')
        return RedirectResponse(url='/download/%s' % str(download_token))
    if output_format == 'nc':
        filename = str(uuid.uuid5(uuid.NAMESPACE_URL, 'download')) + '.' + str(output_format)
        s = TimestampSigner('secret-key')
        download_token = s.sign(filename).decode()
        # this stores the data in the 'DOWNLOAD_DIR' which is set in the docker-compose.yml instruction
        outfile = Path(os.environ['DOWNLOAD_DIR'], str(filename))
        ds = df_final.to_xarray()
        ds.attrs = data[0].dataset_metadata
        for i in data:
            ds[i.columns.values[0]].attrs = i.variable_metadata
        ds.to_netcdf(outfile)
        return RedirectResponse(url='/download/%s' % str(download_token))
        # the line below will return a direct download
        # return FileResponse(path=outfile, filename='out.nc')


@app.get("/ncplot/plot")
async def plot(*,
                 resource_url: str = Query(...,
                                           title="Resource URL",
                                           description="URL to a NetCDF resource"),
                 get: str = Query(...,
                                  title="Query string",
                                  description="Receive list of parameters or get the plot, specifying the variable name",
                                  regex='^(param|plot)$'),
                 variable: str = Query(None,
                                       title="Variable name",
                                       description="String with the NetCDF Variable name")):
    if get == 'param':
        return get_plottable_variables(resource_url)

    if get == 'plot':
        data = get_data(resource_url, variable)
        # json_plot = create_plot(data)
        json_plot = create_page(data)
        json_data = json_item(json_plot, target='tsplot')
        return json_data
