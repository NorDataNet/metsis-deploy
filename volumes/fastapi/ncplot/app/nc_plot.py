import numpy as np
import xarray as xr
# from bokeh.embed import json_item
import pandas as pd
# from bokeh.io import push_notebook, show, output_notebook
# from bokeh.layouts import row
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource #, Column
# from bokeh.layouts import column
from bokeh.models.tools import HoverTool
from bokeh.models.widgets import Div
# from bokeh.models.widgets import Paragraph
from bokeh.layouts import layout
from bokeh.models.widgets import Panel, Tabs

from json2html import *

def get_plottable_variables_old(nc_url):
    ds = xr.open_dataset(nc_url)
    return {"y_axis": [i for i in ds if len(ds[i].shape) == 1]}


def get_plottable_variables(nc_url):
    ds = xr.open_dataset(nc_url)
    num_dim = len(ds.dims)
    return {"y_axis": [i for i in ds if len(ds[i].shape) == num_dim]}


def get_data_old(nc_url, nc_variable, resample=None):
    ds = xr.open_dataset(nc_url)
    df = ds.to_dataframe()
    df.replace(9.96921e+36, np.NaN, inplace=True)
    data = df[nc_variable]
    if resample:
        data = data.resample(resample).mean()
    data = pd.DataFrame(data)
    data.dataset_metadata = ''
    data.dataset_metadata = ds.attrs
    data.variable_metadata = ''
    data.variable_metadata = ds[nc_variable].attrs
    return data


def get_data(nc_url, nc_variable=None, resample=None):
    ds = xr.open_dataset(nc_url)
    df = ds.to_dataframe()
    df.replace(9.96921e+36, np.NaN, inplace=True)
    if nc_variable:
        data = df[nc_variable]
    else:
        data=df
    if resample:
        data = data.resample(resample).mean()
    data = pd.DataFrame(data)
    data.dataset_metadata = ''
    data.dataset_metadata = ds.attrs
    if nc_variable:
        data.variable_metadata = ''
        data.variable_metadata = ds[nc_variable].attrs
    else:
        data.variable_metadata = ''
        data.variable_metadata = {i: ds[i].attrs for i in ds}
    return data


def create_plot(data):
    data['tooltip'] = [x.strftime("%Y-%m-%d %H:%M:%S") for x in data.index]
    source = ColumnDataSource(data)
    tools_to_show = "box_zoom, pan,save, hover, reset, wheel_zoom"
    var_label = '@'+str(data.columns[0])
    p = figure(toolbar_location="above",
               x_axis_type="datetime",
               tools=tools_to_show) #
    p.sizing_mode = 'stretch_width'
    tooltips = [('Time', '@tooltip'),
                (str(data.variable_metadata['long_name']), var_label)
               ]
    hover = p.select(dict(type=HoverTool))
    hover.formatters = {'tooltip': "datetime"}
    hover.tooltips = tooltips
    p.line(x='time',
           y=data.columns[0],
           source=source,
           color='green',
           legend_label=data.columns[0],
           )
    p.min_border_left = 80
    p.min_border_right = 80
    return p


def create_page(data):
    plot = create_plot(data)
    title = data.variable_metadata['long_name']
    summary = data.dataset_metadata['summary']
    dataset_metadata = json2html.convert(json=data.dataset_metadata,
                                         table_attributes="id=\"dataset-metadata\" ")
    variable_metadata = json2html.convert(json=data.variable_metadata,
                                          table_attributes="id=\"variable-metadata\" class=\"table table-bordered table-hover\"")
    title_div = Div(text="""<h1><b>{title}</b></h1>""".format(title=title))

    dataset_metadata_div = Div(text="""{dataset_metadata}""".format(dataset_metadata=dataset_metadata))

    variable_metadata_div = Div(text="""<p>{variable_metadata}</p>""".format(variable_metadata=variable_metadata))

    metadata_layout = layout([
        [title_div],
        [variable_metadata_div, dataset_metadata_div],
    ], sizing_mode='stretch_width')
    tab1 = Panel(child=plot, title="Plot")
    tab2 = Panel(child=metadata_layout, title="Metadata")
    tabs = Tabs(tabs=[tab1, tab2])
    return tabs
