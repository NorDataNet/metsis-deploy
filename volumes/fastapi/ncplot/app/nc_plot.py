# from bokeh.embed import json_item
# from bokeh.io import push_notebook, show, output_notebook
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, CustomJS, Select  #, Column
from bokeh.models.tools import HoverTool
from bokeh.layouts import layout, column #, row
from bokeh.models.widgets import Panel, Tabs, Div
from json2html import *


def create_ts_plot(data):
    data['tooltip'] = [x.strftime("%Y-%m-%d %H:%M:%S") for x in data.index]
    source = ColumnDataSource(data)
    tools_to_show = "box_zoom, pan, save, hover, reset, wheel_zoom, crosshair"
    var_label = '@{'+str(data.columns[0]+'}')
    try:
        var_tooltip_label = str(data.variable_metadata['long_name'])
    except KeyError:
        var_tooltip_label = str(data.variable_metadata['standard_name'])
    try:
        units = list({'unit', 'units'}.intersection(data.variable_metadata))[0]
        y_axis_label = " ".join([var_tooltip_label, '[', data.variable_metadata[units], ']'])
    except IndexError:
        print('no units found')
        y_axis_label = var_tooltip_label
    p = figure(toolbar_location="above",
               x_axis_type="datetime",
               tools=tools_to_show,
               x_axis_label='Date-Time',
               y_axis_label=y_axis_label)  #
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
           legend_label=var_tooltip_label,
           )
    p.min_border_left = 80
    p.min_border_right = 80
    return p


def create_vp_plot(data):
    ds = ColumnDataSource(data)
    # tools_to_show = "box_zoom, pan,save, hover, reset, wheel_zoom"
    var_label = '@{' + str(data.columns[0] + '}')
    p = figure(toolbar_location="above",
               x_axis_type="linear")
    p.sizing_mode = 'stretch_width'
    print(data.dataset_metadata['dimension'])
    if len(data.dataset_metadata['dimension']) == 2:
        try:
            vertical_level, time_level = data.dataset_metadata['dimension']
        except KeyError:
            vertical_level, time_level = ('obsdepth', 'time')
    else:
        vertical_level = data.dataset_metadata['dimension'][0]
    try:
        var_tooltip_label = str(data.variable_metadata['long_name'])
    except KeyError:
        var_tooltip_label = str(data.variable_metadata['standard_name'])
    # if " " in var_label:
    #     var_label = '@{' + var_label + '}'
    # else:
    #     var_label = var_label
    # var_label = var_label
    hover = HoverTool(tooltips=[("Depth", "@"+vertical_level),
                                (var_tooltip_label, var_label)])

    p.add_tools(hover)
    p.y_range.flipped = True
    p.min_border_left = 80
    p.min_border_right = 80
    line_renderer = p.line(data.columns[0],
                           vertical_level,
                           source=ds,
                           color='green',
                           )
    if len(list(data.columns)) >= 2:
        select = Select(title="Profile-record:", options=list(data.columns))
        handler = CustomJS(args=dict(line_renderer=line_renderer),
                           code="""
           line_renderer.glyph.x = {field: cb_obj.value};       
        """)
        select.js_on_change('value', handler)
        return column(select, p, sizing_mode="stretch_width")
    else:
        return column(p, sizing_mode="stretch_width")


def create_page(data, metadata=True):
    if data.dataset_metadata['featureType'] == 'timeSeries':
        plot = create_ts_plot(data)
    if data.dataset_metadata['featureType'] == 'profile':
        plot = create_vp_plot(data)
    # return here if do not want metadata tab
    if metadata:
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
    else:
        return plot
