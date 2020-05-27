from app.nc_transform import get_plottable_variables, get_plottable_data, get_nc_data, get_vp_data

from fastapi import HTTPException


def get_variables(resource_url):
    try:
        plottable_variables = get_plottable_variables(resource_url)
        return plottable_variables
    except IOError:
        raise HTTPException(
            status_code=422, detail="URL To invalid or not supported NetCDF resource")


def get_data(resource_url, variable):
    try:
        plottable_variables = get_plottable_variables(resource_url)
        axis = list(plottable_variables.keys())[0]
    except IOError:
        raise HTTPException(
            status_code=422, detail="URL To invalid or not supported NetCDF resource")
    if not variable or variable not in get_plottable_variables(resource_url)[axis]:
        raise HTTPException(status_code=404, detail="Variable not found")
    if axis == 'y_axis':
        try:
            data = get_nc_data(resource_url, variable, resample=None)
        except IOError:
            raise HTTPException(status_code=422,
                                detail="NetCDF resource is valid, but the routine failed to retrieve the timeSeries data")
    if axis == 'x_axis':
        try:
            data = get_vp_data(resource_url, variable, resample=None)
        except IOError:
            raise HTTPException(status_code=422,
                                detail="NetCDF resource is valid, but the routine failed to retrieve the timeSeries data")
    return data
