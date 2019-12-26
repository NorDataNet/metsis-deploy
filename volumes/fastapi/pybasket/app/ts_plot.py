from typing import Iterable, Tuple
import numpy
import datetime
import netCDF4

# import json
import bokeh.models.layouts
# from bokeh.embed import json_item
import decimal

import bokeh.palettes
import bokeh.plotting
import bokeh.layouts
import bokeh.models

from bokeh.plotting import figure
from bokeh.embed import components


def _should_skip_variable(variable: netCDF4.Variable) -> Tuple[bool, str]:
    x_dim_index = -1
    x_dim_value = -1
    x_dim_name = ""
    number_of_dimensions_with_more_than_one_value = 0
    for counter, var_shape_value in enumerate(variable.shape):
        if var_shape_value > x_dim_value:
            x_dim_index = counter
            x_dim_value = var_shape_value
            x_dim_name = variable.dimensions[counter]
            if var_shape_value > 1:
                number_of_dimensions_with_more_than_one_value = (
                        number_of_dimensions_with_more_than_one_value + 1
                )

    if x_dim_index == -1:
        return True, None

    if number_of_dimensions_with_more_than_one_value != 1:
        return True, None

    return False, x_dim_name


def get_datetimeranges(
        dataset: netCDF4.Dataset,
) -> Iterable[Tuple[str, datetime.datetime, datetime.datetime]]:
    datetimeranges = []

    for dim_name in dataset.dimensions:
        if dim_name in ["time", "metadata_time"]:
            if dim_name in dataset.variables:
                curr_variable = dataset.variables[dim_name]
                min_date = curr_variable[:][0]
                max_date = curr_variable[:][-1]

                datetimeranges.append((dim_name, min_date, max_date))

    return datetimeranges;


def get_plottable_variables(
        dataset: netCDF4.Dataset,
) -> (
        Iterable[Tuple[str, str, str, str]],
        Iterable[Tuple[str, datetime.datetime, datetime.datetime]],
):
    variables = []

    for key_var, value_var in dataset.variables.items():
        skip, x_dim_name = _should_skip_variable(value_var)
        if skip:
            continue

        data_name = value_var.name
        data_long_name = (
            value_var.long_name if hasattr(value_var, "long_name") else value_var.name
        )
        data_unit = (
            value_var.unit
            if hasattr(value_var, "unit")
            else value_var.units
            if hasattr(value_var, "units")
            else "-"
        )
        data_dimension = x_dim_name

        variables.append((data_name, data_long_name, data_unit, data_dimension))

    variables.sort(key=lambda x: x[1])

    # get datetime ranges
    datetimeranges = get_datetimeranges(dataset)

    return (variables, datetimeranges)


def get_variable_data(
        dataset: netCDF4.Dataset, variables: Iterable[str]
) -> Iterable[
    Tuple[
        numpy.ma.MaskedArray, numpy.ma.MaskedArray, str, str, bool, str, bool, str, str
    ]
]:
    plots = []

    for key_var, value_var in dataset.variables.items():
        if key_var not in variables:
            continue

        skip, x_dim_name = _should_skip_variable(value_var)
        if skip:
            continue

        dimension_var = dataset.variables[x_dim_name]
        if x_dim_name in ["time", "metadata_time"]:
            is_x_time = True
            dimension_unit = (
                dimension_var.unit
                if hasattr(dimension_var, "unit")
                else dimension_var.units
                if hasattr(dimension_var, "units")
                else "-"
            )
            x_axis_name = ""
            dimension_column = netCDF4.num2date(dimension_var[:], dimension_unit)
        else:
            is_x_time = False
            dimension_unit = (
                dimension_var.unit
                if hasattr(dimension_var, "unit")
                else dimension_var.units
                if hasattr(dimension_var, "units")
                else "-"
            )
            x_axis_name = x_dim_name + " (" + dimension_unit + ")"
            dimension_column = dimension_var[:]

        if value_var.name in ["time", "metadata_time"]:
            is_y_time = True
            data_unit = (
                value_var.unit
                if hasattr(value_var, "unit")
                else value_var.units
                if hasattr(value_var, "units")
                else "-"
            )
            y_axis_name = ""
            data_column = netCDF4.num2date(value_var[:], data_unit)
        else:
            is_y_time = False
            data_unit = (
                value_var.unit
                if hasattr(value_var, "unit")
                else value_var.units
                if hasattr(value_var, "units")
                else "-"
            )
            y_axis_name = (
                    (
                        value_var.long_name
                        if hasattr(value_var, "long_name")
                        else value_var.name
                    )
                    + " ("
                    + data_unit
                    + ")"
            )
            data_column = value_var[:]

        data_name = value_var.name
        data_long_name = (
            value_var.long_name if hasattr(value_var, "long_name") else value_var.name
        )
        data_dimension = x_dim_name

        # TODO: this requires that the dimension data is the last element in shape
        if len(value_var.shape) == 1:
            final_data_column = data_column
        elif len(value_var.shape) == 2:
            final_data_column = data_column[0]
        elif len(value_var.shape) == 3:
            final_data_column = data_column[0][0]

        extra_dimensions = []
        for counter, var_shape_value in enumerate(value_var.shape):
            if var_shape_value == 1:
                x_dim_name = value_var.dimensions[counter]
                x_dim_element = ""
                if x_dim_name in dataset.variables:
                    dataset_var = dataset.variables[x_dim_name]
                    x_dim_element = dataset_var[:][0]
                    dimension_unit = (
                        dataset_var.unit
                        if hasattr(dataset_var, "unit")
                        else dataset_var.units
                        if hasattr(dataset_var, "units")
                        else None
                    )
                    if dimension_unit is not None:
                        if x_dim_name == "time":
                            x_dim_element = netCDF4.num2date(
                                x_dim_element, dimension_unit
                            )
                        x_dim_element = str(x_dim_element) + " " + str(dimension_unit)

                extra_dimensions.append((x_dim_name, str(x_dim_element)))

        plots.append(
            (
                dimension_column,
                final_data_column,
                data_long_name,
                data_unit,
                is_x_time,
                x_axis_name,
                is_y_time,
                y_axis_name,
                extra_dimensions,
            )
        )

    return plots


def get_data(url_resource: str) -> netCDF4.Dataset:
    dataset = netCDF4.Dataset(url_resource, mode="r")
    return dataset


def create_figure(
        dataset: netCDF4.Dataset,
        nc_resource: str,
        plot_title: str,
        plot_variables: Iterable[str],
        datetime_ranges: Iterable[Tuple[str, decimal.Decimal, decimal.Decimal]],
) -> bokeh.models.layouts.Column:
    #    from .netcdf_helper import NetCDFHelper
    # get variable data from netCDF file
    #    helper = NetCDFHelper(nc_resource)
    plots = get_variable_data(dataset, plot_variables)

    # plot data
    bokeh_plots = []

    curr_color_index = 0
    for plot in plots:
        # TODO: test wrap around
        color_palette = bokeh.palettes.Spectral11
        color = color_palette[curr_color_index % len(color_palette)]

        x_axis_type = "datetime" if plot[4] else "auto"
        x_axis_label = "Time" if plot[4] else plot[5]
        y_axis_type = "datetime" if plot[6] else "auto"
        y_axis_label = "Time" if plot[6] else plot[7]

        plot_title = plot[2]
        if len(plot[8]) > 0:
            plot_title = plot_title + " ("
            for extra_dimension in plot[8]:
                plot_title = (
                        plot_title + extra_dimension[0] + "=" + extra_dimension[1] + ", "
                )
            plot_title = plot_title[:-2]
            plot_title = plot_title + ")"

        tools_to_show = "box_zoom,pan,save,hover,reset,tap,wheel_zoom"
        bokeh_plot = bokeh.plotting.figure(
            title=plot_title,
            width=800,
            height=500,
            x_axis_type=x_axis_type,
            x_axis_label=x_axis_label,
            y_axis_type=y_axis_type,
            y_axis_label=y_axis_label,
            tools=tools_to_show,
        )

        # TODO: filter on date
        # TODO: TEST
        # TODO: should we use decimal instead of float?
        #       what is the original datatype of values from netCDF library?
        dim1 = plot[0].tolist()
        dim2 = plot[1].tolist()
        for counter, item in enumerate(dim2):
            if item is None:
                dim2[counter] = float("nan")

        bokeh_plot.line(
            dim1,
            dim2,
            legend=plot[2] + " (" + plot[3] + ")",
            line_color=color_palette[curr_color_index],
            line_width=1,
        )

        # https://docs.bokeh.org/en/latest/docs/user_guide/tools.html#formatting-tooltip-fields
        hover = bokeh_plot.select(dict(type=bokeh.models.HoverTool))

        x_hover = "@x{%F}" if plot[4] else "@x"
        y_hover = "@y{%F}" if plot[6] else "@y"
        hover.tooltips = [
            (f"('Time', {plot_variables[0].replace('_', ' ')})", "(" + x_hover + ", " + y_hover + ")"),
        ]

        hover.formatters = {
            "x": "datetime" if plot[4] else "printf",
            "y": "datetime" if plot[6] else "printf",
        }

        hover.mode = "vline"

        bokeh_plots.append(bokeh_plot)

        curr_color_index = curr_color_index + 1

        print(plot_variables)

    return bokeh.layouts.column(children=bokeh_plots)


def test_splot(data_url, plot_variables, plot_datetimeranges, plot_title):
    dataset = netCDF4.Dataset(str(data_url), mode="r")
    plot = create_figure(dataset, "", plot_title, plot_variables, plot_datetimeranges)
    script, div = components(plot)
    return script, div


