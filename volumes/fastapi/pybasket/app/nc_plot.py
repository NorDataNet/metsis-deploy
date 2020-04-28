import numpy as np
import xarray as xr
#import holoviews as hv
from bokeh.embed import json_item
#import hvplot.pandas
import pandas as pd
from bokeh.io import push_notebook, show, output_notebook
from bokeh.layouts import row
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Column
from bokeh.models.tools import HoverTool
from bokeh.models.widgets import Div
from bokeh.models.widgets import Paragraph
from json2html import *

# resource_url = 'http://epinux.com:9090/opendap/SN99938.nc'

def get_plottable_variables(nc_url):
    DS = xr.open_dataset(nc_url)
    return {"y_axis": [i for i in DS if len(DS[i].shape) == 1]}


def get_data1(nc_url, nc_variable, resample=None):
    DS = xr.open_dataset(nc_url)
    df = DS.to_dataframe()
    df.replace(9.96921e+36, np.NaN, inplace=True)
    data = df[nc_variable]
    metadata = DS.attrs
    metadata['variable'] = DS[nc_variable].attrs
    if resample:
        data = data.resample(resample).mean()
    return {'data': pd.DataFrame(data), 'metadata': metadata}

def get_data(nc_url, nc_variable, resample=None):
    DS = xr.open_dataset(nc_url)
    df = DS.to_dataframe()
    df.replace(9.96921e+36, np.NaN, inplace=True)
    data = df[nc_variable]
    if resample:
        data = data.resample(resample).mean()
    data=pd.DataFrame(data)
    data.dataset_metadata = ''
    data.dataset_metadata = DS.attrs
    data.variable_metadata = ''
    data.variable_metadata = DS[nc_variable].attrs
    return data


def create_plot(data):
    data['tooltip'] = [x.strftime("%Y-%m-%d %H:%M:%S") for x in data.index]
    source = ColumnDataSource(data)
    tools_to_show = "box_zoom, pan,save, hover, reset, wheel_zoom"
    var_label = '@'+str(data.columns[0])
    p = figure(toolbar_location="above",
               x_axis_type="datetime",
               tools=tools_to_show) #
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
    return p


def create_page(data):
    plot = create_plot(data)
    title = data.variable_metadata['long_name']
    summary = data.dataset_metadata['summary']
    dataset_metadata = json2html.convert(json=data.dataset_metadata)
    variable_metadata = json2html.convert(json=data.variable_metadata)
    title_div = Div(text="""<h1>
                                <b>
                                    {title}
                                </b>
                            </h1>""".format(title=title))

    abstract_text = Div(text="""<details>
                                    <summary>
                                        Summary
                                    </summary>
                                    <p>
                                        {summary}
                                    </p>
                                </details>""".format(summary=summary),
                        width=400,
                        height=200)

    dataset_metadata_div = Div(text="""<details>
                                           <summary>
                                               Dataset Metadata
                                           </summary>
                                           <p>
                                               {dataset_metadata}
                                           </p>
                                        </details>""".format(dataset_metadata=dataset_metadata),
                               width=300,
                               height=100)

    variable_metadata_div = Div(text="""<details>
                                            <summary>
                                                Variable Metadata
                                            </summary>
                                            <p>
                                                {variable_metadata}
                                            </p>
                                        </details>""".format(variable_metadata=variable_metadata),
                                width=200,
                                height=100)

    plot_caption = Paragraph(text="""This text can be a figure caption.""",
                             width=200,
                             height=100)
    return Column(title_div, abstract_text, plot, plot_caption, variable_metadata_div, dataset_metadata_div)


def create_figure(nc_url, nc_variable, ylabel=None, xlabel='Time'):
    if not ylabel:
        ylabel=nc_variable
    DS = xr.open_dataset(nc_url)
    df = DS.to_dataframe()
    df.replace(9.96921e+36, np.NaN, inplace=True)
    subset = df[nc_variable]
    p = hv.render(subset.hvplot().opts(title="", ylabel=ylabel, xlabel=xlabel), backend="bokeh")
    return subset
    # p = hv.render(subset.hvplot().opts(title="", ylabel=ylabel, xlabel=xlabel), backend="bokeh")
    # return json_item(p, target='tsplot')


def create_plot1(resource):
    data = resource['data']
    metadata = json2html.convert(json=resource['metadata'])
    data['tooltip'] = [x.strftime("%Y-%m-%d %H:%M:%S") for x in data.index]
    source = ColumnDataSource(data)
    tools_to_show = "box_zoom, pan,save, hover, reset, wheel_zoom"
    y_tooltip = '@'+str(data.columns[0])
    p = figure(toolbar_location="above",
               x_axis_type="datetime",
               tools=tools_to_show) #
    tooltips = [('Time', '@tooltip'),
                (data.columns[0], y_tooltip)
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
    return p

# get_plottable_variables(resource_url)
