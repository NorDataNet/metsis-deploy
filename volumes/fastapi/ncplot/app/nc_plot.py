import numpy as np
import xarray as xr
from bokeh.embed import json_item
import pandas as pd
from bokeh.io import push_notebook, show, output_notebook
from bokeh.layouts import row
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource #, Column
from bokeh.layouts import column
from bokeh.models.tools import HoverTool
from bokeh.models.widgets import Div
# from bokeh.models.widgets import Paragraph
# import bokeh.layouts
from json2html import *

def get_plottable_variables(nc_url):
    DS = xr.open_dataset(nc_url)
    return {"y_axis": [i for i in DS if len(DS[i].shape) == 1]}


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

    abstract_text = Div(text="""<summary>Summary</summary>
                                <p>{summary}</p>
                                """.format(summary=summary),
                        width=400,
                        height=100,
                        style={'font-size': '100%', 'color': 'blue'})

    dataset_metadata_div = Div(text="""<p>{dataset_metadata}</p>""".format(dataset_metadata=dataset_metadata),
                               style={'visibility': 'hidden'})

    variable_metadata_div = Div(text="""<p>{variable_metadata}</p>""".format(variable_metadata=variable_metadata),
                                style={'visibility': 'hidden'})

    #plot_caption = Paragraph(text="""This text can be a figure caption.""",
    #                         width=200,
    #                         height=100)
    widget = column(title_div, abstract_text, plot, variable_metadata_div, dataset_metadata_div) # plot_caption
    widget.sizing_mode="stretch_width"
    return widget
