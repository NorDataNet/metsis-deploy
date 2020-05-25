import numpy as np
import xarray as xr
import pandas as pd
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


def get_plottable_data(nc_url, level):
    ds = xr.open_dataset(nc_url)
    variables = get_plottable_variables(nc_url)
    data = {i: {'dims': (level),
                'data': ds[i].values,
                'attrs': ds[i].attrs} for i in variables[list(variables.keys())[0]]}
    dataset = xr.Dataset.from_dict(data)
    dataset.attrs = ds.attrs
    dataset = dataset.assign_coords({level: ds[level]})
    return dataset


def get_nc_data(nc_url, nc_variable=None, resample=None):
    ds = xr.open_dataset(nc_url)
    # TODO: the following is an hack to bypass bad/weird dataset
    if len(ds.coords) != len(ds.dims):
        valid_levels = [i for i in ds.dims if np.unique(ds[i]).shape[0] != 1]
        ds = get_plottable_data(nc_url, valid_levels[0])
        if len(valid_levels) >= 2:
            print('WORNING, skipping:', valid_levels[1:], 'dimensions')

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
    if 'featureType' not in profile.dataset_metadata:
        profile.dataset_metadata['featureType'] = ''
        profile.dataset_metadata['featureType'] = 'profile'
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
            profile.dataset_metadata['featureType'] = 'timeSeriesProfile'
    return profile

