import numpy as np
import pandas as pd
import xarray as xr
import os
# from mpl_toolkits.basemap import Basemap
import xesmf as xe
import matplotlib as mpl
import matplotlib.pyplot as plt
from glob import glob
from utils import reformat_X
import intake
mpl.rcParams.update({'font.size' : 22})


def load_LENS_dataset(catalog_url):
    col = intake.open_esm_datastore(catalog_url)
    col_subset = col.search(frequency=["monthly"], component="atm", variable=["TREFHT", "PRECC"], 
                            experiment=["RCP85", "HIST", "20C"])
    dsets = col_subset.to_dataset_dict(zarr_kwargs={"consolidated": True}, storage_options={"anon": True})
    print("\nDataset dictionary keys:\n", dsets.keys())
    
    ds_HIST = dsets['atm.20C.monthly']
    ds_RCP85 = dsets['atm.RCP85.monthly']
    
    t_hist = ds_HIST["TREFHT"].resample(time="AS").mean("time")
    t_rcp = ds_RCP85["TREFHT"].resample(time="AS").mean("time")
    p_hist = ds_HIST["PRECC"].resample(time="AS").mean("time")
    p_rcp = ds_RCP85["PRECC"].resample(time="AS").mean("time")
    
    tref = xr.concat([t_hist, t_rcp], dim='time')
    prec = xr.concat([p_hist, p_rcp], dim='time')
    return xr.merge([tref, prec])
    

def calculate_analogs(focal_ds, focal_lat, focal_lon, var_list, future_ds, historical_start_date,
                      historical_end_date, change_start_date, change_end_date):
    """
    calculates the global climate analogs of a location, called a focal point
    
    inputs
    ------
        focal_lat               (float) : latitude of the focal point
        focal_lon               (float) : longitude of the focal point (0-360)
        historical_ds   (xr.DataArray)  : the ds with the historical data
        month                   (int)  : the month for which to caclulate analogs (Jan is 1)
        var_list               (month) : list of strings corresponding to the variables on which
                                         to base the analogs
        future_ds          (xr.Dataset):the dataset with the future climate data
    
    outputs
    -------
        xr.DataArray showing the similarity of each of each grid cell to the focal point 
    """
    assert focal_lon >= 0 and focal_lon <= 360, "longitude must be defined from 0 to 360!"
    focal_data = focal_ds.sel(lat=focal_lat, lon=focal_lon, method='nearest')
    focal_climate_normals = focal_data[var_list].sel(time=slice(historical_start_date, 
                                historical_end_date)).mean('time')
    future_climate_normals = future_ds[var_list].sel(time=slice(change_start_date, 
                                change_end_date)).mean('time')
    #calculate the year-to-year variance at the focal point
    focal_icv = focal_data.var(dim='time')
    #Calculate the standardized euclidean distance (sed)
    sed = (future_climate_normals - focal_climate_normals)**2/focal_icv
    sed_vals = sed[var_list].to_array().sum(axis=0)**0.5
    sed['Standardized Euclidean Distance'] = sed_vals
    sed.drop(var_list)
    
    return sed

def plot_analog_validation(top_K_coords, lat, lon, var, long_name, start, end):
    plt.figure(figsize=(21,14))
    if var == "t2m":
        ds = xr.open_dataset('regridded_ERA5_T2M.nc').sel(expver=1,time=slice(start, end))-273.15
    else:
        ds = xr.open_dataset('precip.mon.total.1x1.v2018.nc').sel(time=slice(start, end))
    location = ds[var].sel(lat=lat, lon=lon, method='nearest').resample(time="AS").mean("time")
    location = pd.Series(location,index=location.time.values)
    location.plot(label="Location")
    for i, coord in enumerate(top_K_coords):
        coord = ds[var].sel(lat=coord[1], lon=coord[0], method='nearest').resample(time="AS").mean("time")
        coord = pd.Series(coord,index=coord.time.values)
        coord.plot(label="Closest Analog {}".format(i+1))
    plt.xlabel("Date", size = 35)
    plt.ylabel(long_name, size = 35)
    plt.legend(loc='best', prop={'size': 20})
    plt.show()

def plot_analog(LENS_dataset, top_K_coords, lat, lon, var, long_name, start, end):
    plt.figure(figsize=(21,14))
    if var == "t2m":
        ds = LENS_dataset.sel(time=slice(start, end)).mean('member_id')['TREFHT']-273.15
    else:
        ds = LENS_dataset.sel(time=slice(start, end)).mean('member_id')['PRECC']
    location = ds.sel(lat=lat, lon=lon, method='nearest')
    timeframe = [a.year for a in location.time.values]
    location = pd.Series(location,index=timeframe)
    location.plot(label="Location")
    for i, coord in enumerate(top_K_coords):
        coord = ds.sel(lat=coord[1], lon=coord[0], method='nearest')
        coord = pd.Series(coord,index=timeframe)
        coord.plot(label="Closest Analog {}".format(i+1))
    plt.xlabel("Date", size = 35)
    plt.ylabel(long_name, size = 35)
    plt.legend(loc='best', prop={'size': 20})
    plt.show()

def print_analog_stats(bc_hist_models, long_name):
    """
    Print mean, std, min, and max of yearly averages across models
    """
    analog_stack = reformat_X(bc_hist_models, long_name, 'BC Climate Projection')
    print("Mean of Yearly Average across Models {}".format(analog_stack.mean(axis=1).mean()))
    print("STD of Yearly Average across Models {}".format(analog_stack.std(axis=1).mean()))
    print("Maximum of Yearly Average across Models {}".format(analog_stack.max(axis=1).mean()))
    print("Minimum of Yearly Average across Models: {}".format(analog_stack.min(axis=1).mean()))