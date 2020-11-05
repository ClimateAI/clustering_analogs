import os.path

import numpy as np
import pandas as pd
import xarray as xr
import xesmf as xe
from sklearn import preprocessing
from sklearn.cluster import KMeans

from analogs import calculate_analogs, load_LENS_dataset, print_analog_stats


def check_params(lat, lon):
    if lat > 90 or lat < -90:
        return (f'Lat provided:{lat} is out of -90 to 90 bounds')
    if lon > 180 or lon < -180:
        return (f'Lon provided:{lon} is out of -180 to 180 bounds')
    return None


def load_file(lat, lon):
    today = str(date.today())
    os.makedirs(data_dir, exist_ok=True)
    file_name = f'{lat},{lon}-{today}-{var}-Meteoblue.txt'
    fn = f'{data_dir}/{file_name}'
    blob_path = f'Data/Models/Meteoblue/raw/{var}/{today}/{file_name}'

    print(f'Try to download from Google Storage. Save as: {fn}')
    is_downloaded = download_from_storage(file_name, blob_path, data_dir)
    
    if is_downloaded:
        with open(fn, 'r') as json_file:
            data = json.load(json_file)
            return 


def get_analogs(lat, lon, k=5, quan=0.9):
    problem = check_params(lat, lon)
    if problem:
        return problem

    url = "/home/jhexr/code/clustering_analogs/data/aws-cesm1-le.json"
    if not os.path.isfile(url):
        url = "https://ncar-cesm-lens.s3-us-west-2.amazonaws.com/\
            catalogs/aws-cesm1-le.json"
        lens_dataset = load_LENS_dataset(url)
        lens_dataset.to_netcdf("./data/Lens_dataset.nc")
    else:
        lens_dataset = xr.open_dataset('./data/Lens_dataset.nc')

    nc_file = './data/gto_cesm.nc'
    if not os.path.isfile(nc_file):
        curr_analogs = calculate_analogs(
            lens_dataset, lat, lon,
            ['TREFHT', 'PRECC'], lens_dataset,
            '2000-01-01', '2009-12-31',
            '2000-01-01', '2009-12-31')
        curr_analogs = curr_analogs.load()
        curr_analogs.to_netcdf('./data/gto_cesm.nc')
    else:
        curr_analogs = xr.load_dataset('./data/gto_cesm.nc')

    curr_distances = curr_analogs['Standardized Euclidean Distance'].mean(
        dim='member_id')
    da = curr_distances

    ds_in = xr.open_dataset("./data/lsmask.oisst.v2.nc")
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
