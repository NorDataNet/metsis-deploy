import numpy as np
import xarray as xr
# from bokeh.embed import json_item
import pandas as pd
# from bokeh.io import push_notebook, show, output_notebook
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, CustomJS, Select  #, Column
from bokeh.models.tools import HoverTool
from bokeh.layouts import layout, column #, row
from bokeh.models.widgets import Panel, Tabs, Div

from json2html import *

def get_plottable_variables(nc_url):
    ds = xr.open_dataset(nc_url)
    num_dims = len(ds.dims)
    if num_dims >= 2:
        axis_name = 'x_axis'
    else:
        axis_name = 'y_axis'
    var_dict = {axis_name: [i for i in ds if len(ds[i].shape) == num_dims]}
    if len(var_dict[axis_name]) <= 0:
        var_dict = {axis_name: [i for i in ds if len(ds[i].values.shape) != 0]}
    return var_dict


def get_plottable_data(nc_url):
    ds = xr.open_dataset(nc_url)
    variables = get_plottable_variables(nc_url)
    data = {i: {'dims': ('n_levels'),
                'data': ds[i].values,
                'attrs': ds[i].attrs} for i in variables[list(variables.keys())[0]]}
    dataset = xr.Dataset.from_dict(data)
    dataset.attrs = ds.attrs
    return dataset


def get_nc_data(nc_url, nc_variable=None, resample=None):
    ds = xr.open_dataset(nc_url)
    # TODO: the following is an hack to bypass bad/wird dataset
    if 1 in [np.unique(ds[i]).shape[0] for i in ds.dims]:
        ds = get_plottable_data(nc_url)
    data = ds.to_dataframe()
    data.replace(9.96921e+36, np.NaN, inplace=True)
    if nc_variable:
        data = data[nc_variable]
    if resample:
        data = data.resample(resample).mean()
    data = pd.DataFrame(data)
    data.dataset_metadata = ''
    data.dataset_metadata = ds.attrs
    data.dataset_metadata['dimension'] = list(ds.dims)

    if nc_variable:
        data.variable_metadata = ''
        data.variable_metadata = ds[nc_variable].attrs
    else:
        data.variable_metadata = ''
        data.variable_metadata = {i: ds[i].attrs for i in ds}
    return data


def get_vp_data(nc_url, nc_variable='sal', resample=None):
    profile = get_nc_data(nc_url, nc_variable=nc_variable)

    if len(profile.index.names) == 2:
        vertical_level, time_level = profile.index.names
        df = profile.swaplevel()
        profile_dict = {str(v): df.loc[[df.index.get_level_values(0)[i]]].reset_index(level=time_level, drop=True)[
            nc_variable].values for i, v in enumerate(df.index.unique(level=time_level))}
        flat_df = pd.DataFrame.from_dict(profile_dict)
        flat_df.index = df.index.unique(level=vertical_level)
        flat_df.variable_metadata = ""
        flat_df.dataset_metadata = ""
        flat_df.variable_metadata = profile.variable_metadata
        flat_df.dataset_metadata = profile.dataset_metadata
        profile = flat_df

    if 'featureType' not in profile.dataset_metadata:
        profile.dataset_metadata['featureType'] = ''
        profile.dataset_metadata['featureType'] = 'profile'
    return profile


def create_ts_plot(data):
    data['tooltip'] = [x.strftime("%Y-%m-%d %H:%M:%S") for x in data.index]
    source = ColumnDataSource(data)
    tools_to_show = "box_zoom, pan,save, hover, reset, wheel_zoom"
    var_label = '@{'+str(data.columns[0]+'}')
    try:
        var_tooltip_label = str(data.variable_metadata['long_name'])
    except KeyError:
        var_tooltip_label = str(data.variable_metadata['standard_name'])
    p = figure(toolbar_location="above",
               x_axis_type="datetime",
               tools=tools_to_show)  #
    p.sizing_mode = 'stretch_width'
    tooltips = [('Time', '@tooltip'),
                (var_tooltip_label, var_label)
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


def create_vp_plot(data):
    ds = ColumnDataSource(data)
    #tools_to_show = "box_zoom, pan,save, hover, reset, wheel_zoom"
    var_label = '@{' + str(data.columns[0] + '}')
    p = figure(toolbar_location="above",
               x_axis_type="linear")
    p.sizing_mode = 'stretch_width'
    select = Select(title="Profile-record:", options=list(data.columns))
    try:
        vertical_level, time_level = data.dataset_metadata['dimension']
    except KeyError:
        vertical_level, time_level = ('obsdepth', 'time')
    try:
        var_tooltip_label = str(data.variable_metadata['long_name'])
    except KeyError:
        var_tooltip_label = str(data.variable_metadata['standard_name'])
    hover = HoverTool(tooltips=[("Depth", "@"+vertical_level),
                                (var_tooltip_label, '@{' + var_label + '}')])

    p.add_tools(hover)
    p.y_range.flipped = True
    line_renderer = p.line(data.columns[0],
                           vertical_level,
                           source=ds,
                           color='green',
                           )

    handler = CustomJS(args=dict(line_renderer=line_renderer),
                       code="""
       line_renderer.glyph.x = {field: cb_obj.value};       
    """)
    select.js_on_change('value', handler)
    p.min_border_left = 80
    p.min_border_right = 80
    return column(select, p, sizing_mode="stretch_width")


def create_page(data):
    if data.dataset_metadata['featureType'] == 'timeSeries':
        plot = create_ts_plot(data)
    if data.dataset_metadata['featureType'] == 'profile':
        plot = create_vp_plot(data)
    try:
        title = data.variable_metadata['long_name']
    except KeyError:
        title = data.variable_metadata['standard_name']
    # summary = data.dataset_metadata['summary']
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
