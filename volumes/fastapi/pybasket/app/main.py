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
from pydantic.types import EmailStr

from app import status
from app.fimex import Fimex
from app.solr_client import SolrClient
from app.status import Status
from app.transaction import Transaction
from app.ts_plot import get_plottable_variables, create_figure

import netCDF4
from bokeh.embed import components, json_item
# from bokeh.core import json_encoder as jse
# import json

app = FastAPI()

MAX_PROCESSING_SECOND = 600

@app.get("/basket/conf")
async def basket_conf():
    config = confuse.Configuration('Basket', __name__)
    test = str(config)
    return test


@app.get("/basket/tsplot")
async def tsplot(*,
                 resource_url: str = None,
                 get: str = None,
                 variable: str = None):
    if get == 'param':
        variables, datetimeranges = get_plottable_variables(netCDF4.Dataset(str(resource_url), mode="r"))
        return {"y_axis": [i[0] for i in variables]}

    if get == 'plot':
        json_plot = create_figure(netCDF4.Dataset(str(resource_url),
                                                               mode="r"),
                                               "",
                                               'plot_title',
                                               [variable],
                                               [])


        return json_item(json_plot, target='tsplot')



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
