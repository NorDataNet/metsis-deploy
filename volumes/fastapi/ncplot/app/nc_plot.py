from bokeh.layouts import layout, column, Spacer
from bokeh.models import ColumnDataSource, CustomJS, Select  # , Column
from bokeh.models.tools import HoverTool
from bokeh.models.widgets import Panel, Tabs, Div, Button, Slider
from bokeh.plotting import figure
from json2html import *


def create_ts_plot(data):
    data['tooltip'] = [x.strftime("%Y-%m-%d %H:%M:%S") for x in data.index]
    source = ColumnDataSource(data)
    tools_to_show = "box_zoom, pan, save, hover, reset, wheel_zoom, crosshair"
    var_label = '@{' + str(data.columns[0] + '}')
    try:
        var_tooltip_label = str(data.variable_metadata['long_name'])
    except KeyError:
        var_tooltip_label = str(data.variable_metadata['standard_name'])
    try:
        units = list({'unit', 'units'}.intersection(data.variable_metadata))[0]
        y_axis_label = " ".join(
            [var_tooltip_label, '[', data.variable_metadata[units], ']'])
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
           line_alpha=0.6,
           color='RoyalBlue',
           )
    p.circle(x='time',
             y=data.columns[0],
             source=source,
             color='RoyalBlue',
             size=3,
             fill_alpha=0.5,
             fill_color='white',
             legend_label=var_tooltip_label,
           )
    p.min_border_left = 80
    p.min_border_right = 80
    p.background_fill_color = "SeaShell"
    p.background_fill_alpha = 0.5
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    return p


def get_datetime_string(datetime):
    date = datetime.split('T')[0]
    time = datetime.split('T')[1]
    return f"<ul style='text-align:left;'><li>Date: <b>{date}</b></li><li>Time: <b>{time}</b></li></ul>"


def create_vp_plot(data):
    ds = ColumnDataSource(data)
    # tools_to_show = "box_zoom, pan,save, hover, reset, wheel_zoom"
    var_label = '@{' + str(data.columns[0] + '}')
    try:
        var_tooltip_label = str(data.variable_metadata['long_name'])
    except KeyError:
        var_tooltip_label = str(data.variable_metadata['standard_name'])
    try:
        units = list({'unit', 'units'}.intersection(data.variable_metadata))[0]
        x_axis_label = " ".join(
            [var_tooltip_label, '[', data.variable_metadata[units], ']'])
    except IndexError:
        print('no units found')
        x_axis_label = var_tooltip_label
    p = figure(toolbar_location="above",
               tools="crosshair,box_zoom, pan,save, reset, wheel_zoom",
               x_axis_type="linear",
               x_axis_label=x_axis_label)
    p.sizing_mode = 'stretch_width'
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
    hover = HoverTool(tooltips=[("Depth", "@" + vertical_level),
                                (var_tooltip_label, var_label)])

    p.add_tools(hover)
    p.y_range.flipped = True
    p.min_border_left = 80
    p.min_border_right = 80
    p.background_fill_color = "SeaShell"
    p.background_fill_alpha = 0.5
    line_renderer = p.line(data.columns[0],
                           vertical_level,
                           source=ds,
                           line_alpha=0.6, color='RoyalBlue',
                           )
    point_renderer = p.circle(data.columns[0],
                              vertical_level,
                              source=ds,
                              color='RoyalBlue',
                              size=3,
                              fill_alpha=0.5,
                              fill_color='white',
                              legend_label=data.columns[0],
                              )
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    if len(list(data.columns)) >= 2:
        # Div
        html_text = get_datetime_string(list(data.columns)[0])
        par = Div(text=html_text)
        # Slider Labels
        end_label = Div(text=list(data.columns)[-1])
        start_label = Div(text=list(data.columns)[0])
        # Buttons
        left_btn = Button(label='<', width=30)
        right_btn = Button(label='>', width=30)
        # Spacer
        sp = Spacer(width=50)
        # Slider Labels
        end_label = Div(text=list(data.columns)[-1].split('T')[0] + \
                             '<br>' \
                             + list(data.columns)[-1].split('T')[1],
                        style={'text-align': 'right'})
        start_label = Div(text=list(data.columns)[0].split('T')[0] + \
                               '<br>' \
                               + list(data.columns)[0].split('T')[1],
                          style={'text-align': 'left'})

        select = Select(title="Profile-record:",
                        options=list(data.columns),
                        value=list(data.columns)[0])
        slider = Slider(title="Profile #",
                        value=0,
                        start=0,
                        end=len(data.columns) - 1,
                        step=1,
                        show_value=True,
                        tooltips=False)  #

        select_handler = CustomJS(args=dict(line_renderer=line_renderer,
                                            point_renderer=point_renderer,
                                            slider=slider,
                                            par=par),
                                  code="""
           line_renderer.glyph.x = {field: cb_obj.value};
           point_renderer.glyph.x = {field: cb_obj.value};
           slider.value = cb_obj.options.indexOf(cb_obj.value);
           var date_time = cb_obj.value.split("T");
           var date = date_time[0];
           var time = date_time[1];
           par.text = `<ul style="text-align:left;"><li>Date: <b>`+date+`</b></li><li>Time: <b>`+time+`</b></li></ul>`;
           console.log(date, time);
        """)
        select.js_on_change('value', select_handler)
        slider_handler = CustomJS(args=dict(select=select),
                                  code="""
           select.value = select.options[cb_obj.value];
        """)

        slider.js_on_change('value', slider_handler)

        # Left button cb
        left_btn_args = dict(slider=slider)
        left_btn_handler = """
        if(slider.value > slider.start) {
            slider.value = slider.value - 1;
            slider.change.emit();
        }
        """
        left_btn_callback = CustomJS(args=left_btn_args, code=left_btn_handler)
        left_btn.js_on_click(left_btn_callback)

        # Right button cb
        right_btn_args = dict(slider=slider)
        right_btn_handler = """
        if(slider.value <= slider.end - 1) {
            slider.value = slider.value + 1;
            slider.change.emit();
        }
        """
        right_btn_callback = CustomJS(args=right_btn_args, code=right_btn_handler)
        right_btn.js_on_click(right_btn_callback)

        # buttons = row(left_btn, right_btn)
        # inputs = row(sp,slider,buttons, par)
        # return column(select, slider, p, par, sizing_mode="stretch_width")
        # return column(p, select, inputs, sizing_mode="stretch_width")
        # Set up layouts and add to document
        # slider_wrapper = layout([
        #    [slider],
        #    [start_label, Spacer(sizing_mode="stretch_width"), end_label]
        # ])
        slider_wrapper = layout([
            [sp, sp, slider, left_btn, right_btn, par],
            [sp, start_label, sp, sp, end_label, sp, sp],
        ])
        # buttons = row(left_btn, right_btn)
        # inputs = row(sp, start_label, left_btn, sp, slider, sp, right_btn, end_label, par)

        return column(select, p, slider_wrapper, sizing_mode="stretch_width")
    else:
        return column(p, sizing_mode="stretch_width")


def create_page(data, metadata=True):
    if data.dataset_metadata['featureType'] == 'timeSeries':
        plot = create_ts_plot(data)
    if data.dataset_metadata['featureType'] == 'profile':
        plot = create_vp_plot(data)
    if data.dataset_metadata['featureType'] == 'timeSeriesProfile':
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
        dataset_metadata_div = Div(text="""{dataset_metadata}""".format(
            dataset_metadata=dataset_metadata))
        variable_metadata_div = Div(
            text="""<p>{variable_metadata}</p>""".format(variable_metadata=variable_metadata))
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
