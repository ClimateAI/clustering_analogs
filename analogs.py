import numpy as np
import pandas as pd
import xarray as xr
import os
# from mpl_toolkits.basemap import Basemap
import xesmf as xe
from utils import reformat_X
import intake


def load_LENS_dataset(catalog_url):
    col = intake.open_esm_datastore(catalog_url)
    col_subset = col.search(
        frequency=["monthly"], 
        component="atm",
        variable=["TREFHT", "PRECC"],
        experiment=["RCP85", "HIST", "20C"])
    dsets = col_subset.to_dataset_dict(
        zarr_kwargs={"consolidated": True}, 
        storage_options={"anon": True})
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
    

def calculate_analogs(
    focal_ds, focal_lat, focal_lon,
    var_list, future_ds, 
    historical_start_date, historical_end_date,
    change_start_date, change_end_date):
    """
    calculates the global climate analogs of a location, called a focal point
    
    inputs
    ------
        focal_ds         (xr.DataArray) : xarray data set
        focal_lat               (float) : latitude of the focal point
        focal_lon               (float) : longitude of the focal point (0-360)
        var_list                (month) : list of strings corresponding 
                                          to the variables on which to base the analogs
        future_ds          (xr.Dataset) : the dataset with the future climate data
        historical_start_date
        historical_end_data
        change_start_date
        change_end_date
    
    outputs
    -------
        xr.DataArray showing the similarity of each of 
        each grid cell to the focal point 
    """
    assert (focal_lon >= 0 and focal_lon <= 360,
        "longitude must be defined from 0 to 360!")
    focal_data = focal_ds.sel(lat=focal_lat, lon=focal_lon, method='nearest')
    focal_climate_normals = focal_data[var_list].sel(
        time=slice(historical_start_date, 
        historical_end_date)).mean('time')
    future_climate_normals = future_ds[var_list].sel(
        time=slice(change_start_date, 
        change_end_date)).mean('time')
    #calculate the year-to-year variance at the focal point
    focal_icv = focal_data.var(dim='time')
    #Calculate the standardized euclidean distance (sed)
    sed = (future_climate_normals - focal_climate_normals)**2/focal_icv
    sed_vals = sed[var_list].to_array().sum(axis=0)**0.5
    sed['Standardized Euclidean Distance'] = sed_vals
    sed.drop(var_list)
    
    return sed
