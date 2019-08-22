class Fimex:
    '''
    wps_url: str
    reducetime_start: str
    reducetime_end: str
    interpolate_proj_string: str
    interpolate_method: str
    select_variables: str
    interpolate_xaxis_min: str
    interpolate_xaxis_max: str
    interpolate_yaxis_min: str
    interpolate_yaxis_max: str
    interpolate_xaxis_units: str
    interpolate_yaxis_units: str
    reducebox_east: str
    reducebox_south: str
    reducebox_west: str
    reducebox_north: str
    interpolate_hor_steps: str
    inputtype: str
    outputtype: str
    '''

    def __init__(
            self,
            wps_url: str,
            input_file: str,
            reducetime_start: str,
            reducetime_end: str,
            interpolate_proj_string: str,
            interpolate_method: str,
            select_variables: str,
            interpolate_xaxis_min: str,
            interpolate_xaxis_max: str,
            interpolate_yaxis_min: str,
            interpolate_yaxis_max: str,
            interpolate_xaxis_units: str,
            interpolate_yaxis_units: str,
            reducebox_east: str,
            reducebox_south: str,
            reducebox_west: str,
            reducebox_north: str,
            interpolate_hor_steps: str,
            inputtype: str,
            outputtype: str):
        self.wps_url = wps_url
        self.input_file = input_file
        self.reducetime_start = reducetime_start
        self.reducetime_end = reducetime_end
        self.interpolate_proj_string = interpolate_proj_string
        self.interpolate_method = interpolate_method
        self.select_variables = select_variables
        self.interpolate_xaxis_min = interpolate_xaxis_min
        self.interpolate_xaxis_max = interpolate_xaxis_max
        self.interpolate_yaxis_min = interpolate_yaxis_min
        self.interpolate_yaxis_max = interpolate_yaxis_max
        self.interpolate_xaxis_units = interpolate_xaxis_units
        self.interpolate_yaxis_units = interpolate_yaxis_units
        self.reducebox_east = reducebox_east
        self.reducebox_south = reducebox_south
        self.reducebox_west = reducebox_west
        self.reducebox_north = reducebox_north
        self.interpolate_hor_steps = interpolate_hor_steps
        self.inputtype = inputtype
        self.outputtype = outputtype

    def input_map(self):
        inputs = []
        if self.input_file is not None:
            inputs.append(("inputfile", self.input_file))
        if self.reducetime_start is not None:
            inputs.append(("reducetimeStart", self.reducetime_start))
        if self.reducetime_end is not None:
            inputs.append(("reducetimeEnd", self.reducetime_end))
        if self.interpolate_proj_string is not None:
            inputs.append(("interpolateProjString", self.interpolate_proj_string))
        if self.interpolate_method is not None:
            inputs.append(("interpolateMethod", self.interpolate_method))
        if self.select_variables is not None:
            inputs.append(("selectVariables", self.select_variables))
        if self.interpolate_xaxis_min is not None:
            inputs.append(("interpolateXAxisMin", self.interpolate_xaxis_min))
        if self.interpolate_xaxis_max is not None:
            inputs.append(("interpolateXAxisMax", self.interpolate_xaxis_max))
        if self.interpolate_yaxis_min is not None:
            inputs.append(("interpolateYAxisMin", self.interpolate_yaxis_min))
        if self.interpolate_yaxis_max is not None:
            inputs.append(("interpolateYAxisMax", self.interpolate_yaxis_max))
        if self.interpolate_xaxis_units is not None:
            inputs.append(("interpolateXAxisUnits", self.interpolate_xaxis_units))
        if self.interpolate_yaxis_units is not None:
            inputs.append(("interpolateYAxisUnits", self.interpolate_yaxis_units))
        if self.reducebox_east is not None:
            inputs.append(("reduceboxEast", self.reducebox_east))
        if self.reducebox_south is not None:
            inputs.append(("reduceboxSouth", self.reducebox_south))
        if self.reducebox_west is not None:
            inputs.append(("reduceboxWest", self.reducebox_west))
        if self.reducebox_north is not None:
            inputs.append(("reduceboxNorth", self.reducebox_north))
        if self.interpolate_hor_steps is not None:
            inputs.append(("interpolateHorSteps", self.interpolate_hor_steps))
        if self.inputtype is not None:
            inputs.append(("inputtype", self.inputtype))
        if self.outputtype is not None:
            inputs.append(("outputType", self.outputtype))

        return inputs

    def output_map(self):
        outputs = "urlout"
        return outputs
