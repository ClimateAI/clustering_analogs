import os.path

import numpy as np
import pandas as pd
import xarray as xr
import xesmf as xe
from sklearn import preprocessing
from sklearn.cluster import KMeans


def check_params(lat, lon):
    if lat > 90 or lat < -90:
        return (f'Lat provided:{lat} is out of -90 to 90 bounds')
    if lon > 180 or lon < -180:
        return (f'Lon provided:{lon} is out of -180 to 180 bounds')
    return None


def get_analogs(lat, lon, k=5, quan=0.9):
    problem = check_params(lat, lon)
    if problem:
        return problem

    nc_file = f'./temp/{lat},{lon}_cesm.nc'
    print(nc_file)
    if not os.path.isfile(nc_file):
        return "Not available"
    else:
        curr_analogs = xr.load_dataset(nc_file)

    curr_distances = curr_analogs['Standardized Euclidean Distance'].mean(
        dim='member_id')
    da = curr_distances

    ds_in = xr.open_dataset("./temp/lsmask.oisst.v2.nc")
    regridder = xe.Regridder(ds_in, da, 'nearest_s2d', reuse_weights=True)
    ds_in = regridder(ds_in).squeeze()
    da.values[ds_in['lsmask'] == 1] = np.nan

    da_min = da.where(da != da.sel(lat=lat, lon=lon, method='nearest'))

    df = da_min.to_dataframe().dropna()
    df.reset_index(inplace=True)

    df['inverse_sed'] = 1/df['Standardized Euclidean Distance']

    x = df[['inverse_sed']].values  # returns a numpy array

    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(x)
    df['inverse_sed'] = pd.DataFrame(x_scaled)

    df.loc[df['inverse_sed'] < df['inverse_sed'].quantile(
        quan), 'inverse_sed'] = np.nan
    df = df.dropna()
    df = df.drop(columns=['Standardized Euclidean Distance'])

    X = np.array(df.drop(['inverse_sed'], 1).astype(float))
    Y = np.array(df['inverse_sed'].astype(float))

    kmeans = KMeans(n_clusters=k, random_state=0, max_iter=1000)
    wt_kmeansclus = kmeans.fit(X, sample_weight=Y)

    centers = wt_kmeansclus.cluster_centers_
    return centers
