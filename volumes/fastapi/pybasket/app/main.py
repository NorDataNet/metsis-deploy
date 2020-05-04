import smtplib
import time
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import confuse
import requests
from fastapi import FastAPI, HTTPException, BackgroundTasks
from owslib.util import log
from owslib.wps import WebProcessingService, WPSExecution
from pydantic.networks import EmailStr

from app import status
from app.fimex import Fimex
from app.solr_client import SolrClient
from app.status import Status
from app.transaction import Transaction
#from app.ts_plot import get_plottable_variables, create_figure
from app.nc_plot import get_plottable_variables, get_data, create_plot, create_page

from fastapi.responses import JSONResponse, PlainTextResponse

import netCDF4
from bokeh.embed import components, json_item
# from bokeh.core import json_encoder as jse
import json


from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import FastAPI, Query, HTTPException

# Adding import for file upload
from typing import List
from fastapi import File, UploadFile
from fastapi.responses import HTMLResponse


class Item(BaseModel):
    url: str
    get: str
    variable: str = None

app = FastAPI(title="PyBasket",
              description="Prototype API for time-series plot and METSIS basket functionality",
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




# files - this method will print the size of uploaded files
@app.post("/files/")
async def create_files(files: List[bytes] = File(...)):
    return {"file_sizes": [len(file) for file in files]}

# uploadfiles - this method will print the name of uploaded files
@app.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    return {"filenames": [file.filename for file in files]}

# exe=ample form 'connected' to the files and 'uploadfiles' API
@app.get("/")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)



@app.get("/basket/conf")
async def basket_conf():
    config = confuse.Configuration('Basket', __name__)
    test = str(config)
    return test

@app.get("/basket/plot")
async def plot(*,
                 resource_url: str = Query(...,title="Resource URL",
                                  description="URL to a netcdf resource"),
                 get: str = Query(...,title="Query string",
                                  description="Receive list of parameters or get the plot, specifying the variable name",
                                  regex='^(param|plot)$'),
                 variable: str = Query(None,
                                       title="Variable name",
                                       description="String with the NetCDF Variable name")):
    if get == 'param':
        #variables, datetimeranges = get_plottable_variables(netCDF4.Dataset(str(resource_url), mode="r"))
        #return {"y_axis": [i[0] for i in variables]}
        return get_plottable_variables(resource_url)

    if get == 'plot':
        if not variable or variable not in get_plottable_variables(resource_url)["y_axis"]:
            raise HTTPException(status_code=404, detail="Variable not found")
        data = get_data(resource_url, variable, resample=None)
        #json_plot = create_plot(data)
        json_plot = create_page(data)
        json_data = json_item(json_plot, target='tsplot')
        #json_data['test'] = "<b>BOLD</b>"
        return json_data
    if get == 'data':
        if not variable or variable not in get_plottable_variables(resource_url)["y_axis"]:
            raise HTTPException(status_code=404, detail="Variable not found")
        data = get_data(resource_url, variable, resample=None)
        return data


@app.get("/basket/ncplot")
async def ncplot(item: Item):
    if item.get == 'param':
        #variables, datetimeranges = get_plottable_variables(netCDF4.Dataset(str(resource_url), mode="r"))
        #return {"y_axis": [i[0] for i in variables]}
        return get_plottable_variables(item.url)

    if item.get == 'plot':
        data = get_data(item.url, item.variable, resample=None)
        #json_plot = create_plot(data)
        json_plot = create_page(data)
        json_data = json_item(json_plot, target='tsplot')
        #json_data['test'] = "<b>BOLD</b>"
        return json_data

@app.get("/basket/tsplot")
async def tsplot(*,
                 resource_url: str,
                 get: str,
                 variable: str = None):
    if get == 'param':
        #variables, datetimeranges = get_plottable_variables(netCDF4.Dataset(str(resource_url), mode="r"))
        #return {"y_axis": [i[0] for i in variables]}
        return get_plottable_variables(resource_url)

    if get == 'plot':
        data = get_data(resource_url, variable, resample=None)
        #json_plot = create_plot(data)
        json_plot = create_page(data)
        json_data = json_item(json_plot, target='tsplot')
        #json_data['test'] = "<b>BOLD</b>"
        return json_data

'''
@app.get("/basket/transfer2")
async def fimex_transfer2(*,
                          user_id: str,
                          email: EmailStr,
                          uri: str,
                          wps_url: str,
                          reducetime_start: str = None,
                          reducetime_end: str = None,
                          interpolate_proj_string: str = None,
                          interpolate_method: str = None,
                          select_variables: str,
                          interpolate_xaxis_min: str = None,
                          interpolate_xaxis_max: str = None,
                          interpolate_yaxis_min: str = None,
                          interpolate_yaxis_max: str = None,
                          interpolate_xaxis_units: str = None,
                          interpolate_yaxis_units: str = None,
                          reducebox_east: str,
                          reducebox_south: str,
                          reducebox_west: str,
                          reducebox_north: str,
                          interpolate_hor_steps: str = None,
                          inputtype: str,
                          outputtype: str,
                          background_tasks: BackgroundTasks):
    input_files = uri.split(",")
    fimex_list = []
    for input_file in input_files:
        print(input_file)
        fimex_list.append(
            Fimex(
                wps_url,
                input_file,
                reducetime_start,
                reducetime_end,
                interpolate_proj_string,
                interpolate_method,
                select_variables,
                interpolate_xaxis_min,
                interpolate_xaxis_max,
                interpolate_yaxis_min,
                interpolate_yaxis_max,
                interpolate_xaxis_units,
                interpolate_yaxis_units,
                reducebox_east,
                reducebox_south,
                reducebox_west,
                reducebox_north,
                interpolate_hor_steps,
                inputtype,
                outputtype
            )
        )
    # wps=http://localhost:5000/wps?request=GetCapabilities&service=WPS
    # input_file = 'http://OpeDAP-server/thredds/dodsC/NBS/S2B/2018/02/18/S2B_MSIL1C_20180218T110109_N0206_R094_T33WWS_20180218T144023.nc'
    # wps=http://localhost:5000/cgi-bin/pywps.cgi?service=wps&version=1.0.0&request=getcapabilities
    wps = WebProcessingService(
        wps_url,
        verbose=False,
        skip_caps=True
    )
    config = confuse.Configuration('Basket', __name__)
    transaction = Transaction(str(uuid.uuid4()), user_id, email, status.Status.ORDERED, "nordatanet", fimex_list)
    solr_client = SolrClient(config['solr']['endpoint'].get(), "basket")
    solr_client.update(transaction.toSolrDocument())

    try:
        for fimex in fimex_list:
            execution = wps.execute('transformation', fimex.input_map(), output=fimex.output_map())
            background_tasks.add_task(doFinal, execution, email, transaction)
            print(execution.statusLocation)

    except requests.exceptions.ConnectionError as ce:
        raise HTTPException(status_code=502, detail="Failed to establish a connection")

    return transaction.toJson()
'''

@app.get("/basket/transfer")
async def fimex_transfer(*,
                         user_id: str,
                         email: EmailStr,
                         uri: str,
                         wps_url: str,
                         reducetime_start: str = None,
                         reducetime_end: str = None,
                         interpolate_proj_string: str = None,
                         interpolate_method: str = None,
                         select_variables: str,
                         interpolate_xaxis_min: str = None,
                         interpolate_xaxis_max: str = None,
                         interpolate_yaxis_min: str = None,
                         interpolate_yaxis_max: str = None,
                         interpolate_xaxis_units: str = None,
                         interpolate_yaxis_units: str = None,
                         reducebox_east: str,
                         reducebox_south: str,
                         reducebox_west: str,
                         reducebox_north: str,
                         interpolate_hor_steps: str = None,
                         inputtype: str,
                         outputtype: str,
                         background_tasks: BackgroundTasks):
    input_files = uri.split(",")
    fimex_list = []
    for input_file in input_files:
        print(input_file)
        fimex_list.append(
            Fimex(
                wps_url,
                input_file,
                reducetime_start,
                reducetime_end,
                interpolate_proj_string,
                interpolate_method,
                select_variables,
                interpolate_xaxis_min,
                interpolate_xaxis_max,
                interpolate_yaxis_min,
                interpolate_yaxis_max,
                interpolate_xaxis_units,
                interpolate_yaxis_units,
                reducebox_east,
                reducebox_south,
                reducebox_west,
                reducebox_north,
                interpolate_hor_steps,
                inputtype,
                outputtype
            )
        )
    # wps=http://localhost:5000/wps?request=GetCapabilities&service=WPS
    # input_file = 'http://OpeDAP-server/thredds/dodsC/NBS/S2B/2018/02/18/S2B_MSIL1C_20180218T110109_N0206_R094_T33WWS_20180218T144023.nc'
    # wps=http://localhost:5000/cgi-bin/pywps.cgi?service=wps&version=1.0.0&request=getcapabilities
    wps = WebProcessingService(
        wps_url,
        verbose=False,
        skip_caps=True
    )
    config = confuse.Configuration('Basket', __name__)
    transaction = Transaction(str(uuid.uuid4()), user_id, email, status.Status.ORDERED, "nordatanet", fimex_list)
    solr_client = SolrClient(config['solr']['endpoint'].get(), "basket")
    solr_client.update(transaction.toSolrDocument())

    try:
        for fimex in fimex_list:
            execution = wps.execute('transformation', fimex.input_map(), output=fimex.output_map())
            background_tasks.add_task(doFinal, execution, email, transaction)
            print(execution.statusLocation)

    except requests.exceptions.ConnectionError as ce:
        raise HTTPException(status_code=502, detail="Failed to establish a connection")

    return transaction.toJson()


def doFinal(execution: WPSExecution, to, transaction: Transaction):
    log.info('Fimex Transfermation ordered ' + execution.statusLocation)

    status = check_process_status(execution)

    transaction.set_status(status)

    # TODO: React based on status
    config = confuse.Configuration('Basket', __name__)
    solr_client = SolrClient(config['solr']['endpoint'].get(), "basket")
    solr_client.update(transaction.toSolrDocument())

    # send email to user
    send_email(to)


def send_email(to):
    config = confuse.Configuration('Basket', __name__)
    message = MIMEMultipart("alternative")
    message["Subject"] = config['mail']['subject'].get()
    message["From"] = config['mail']['from'].get()
    message["To"] = to

    text = config['mail']['body']['content'].get()
    part1 = MIMEText(text, "plain")

    message.attach(part1)

    # Create secure connection with server and send email
    # context = ssl.create_default_context()
    try:
        server = smtplib.SMTP(config['mail']['smtp']['host'].get(), config['mail']['smtp']['port'].get())
        server.sendmail(
            config['mail']['from'].get(), to, message.as_string()
        )
    except:
        log.info('something wrong ......')
    finally:
        server.quit()


def check_process_status(execution, sleepSecs=3):
    startTime = time.time()
    while execution.isComplete() is False:
        if time.time() >= startTime + MAX_PROCESSING_SECOND:
            return Status.EXCEEDED
        execution.checkStatus(sleepSecs=sleepSecs)

    if execution.isSucceded():
        return Status.SUCCEEDED

    else:
        if execution.errors:
            for ex in execution.errors:
                log.error('Error: code=%s, locator=%s, text=%s' %
                          (ex.code, ex.locator, ex.text))
            return Status.FAILED
