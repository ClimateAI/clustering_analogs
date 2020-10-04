import xarray as xr
import xesmf as xe
import numpy as np
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib
import cartopy

def plotter(da, cmap, title, vmin, vmax, k, mask_out_ocean=True, location=None, cbar_ylabel=None):
    """
    inputs
    ------
    
        da          (xr.DataArray) : the data array containing the field to plot
        
    returns
    -------
        None but shows the plot via plt.show
    """

    plt.figure(figsize=(21,14))
    ax = plt.axes(projection=ccrs.Miller(central_longitude=180))
    if mask_out_ocean:
        import xesmf as xe
        ds_in = xr.open_dataset("lsmask.oisst.v2.nc")
        regridder = xe.Regridder(ds_in, da, 'nearest_s2d', reuse_weights=True)
        ds_in = regridder(ds_in).squeeze()
        da.values[ds_in['lsmask'] == 1] = np.nan

    da_min = da.where(da != da.sel(lat=location[0], lon=location[1], method='nearest'))
    points = []
    for _ in range(k):
        points.append(da_min.where(da_min==da_min.min(), drop=True).squeeze())
        da_min = da_min.where(da_min!=da_min.min(), drop=True).squeeze()
    top_k=[(p.lon.item(), p.lat.item()) for p in points]

    contours = da.plot.contourf(ax=ax, transform=ccrs.PlateCarree(), cmap=cmap, vmin=vmin, vmax=vmax, extend='both')

    if cbar_ylabel:
        contours.colorbar.ax.set_ylabel(cbar_ylabel)
    plt.title(title, size=25)
    ax.set_global(); ax.coastlines(); ax.add_feature(cartopy.feature.STATES)
    if top_k:  
        ax.scatter([a[0] for a in top_k],[a[1] for a in top_k], transform=ccrs.PlateCarree(), color='purple', s=100, label = "Top-{} Analogs".format(k))
    ax.scatter(*location, transform=ccrs.PlateCarree(), color='blue', s=100, label="Location") 
    ax.legend()
    plt.show()
    return (top_k)

def reformat_X(X, long_name, method):
    """
    Reformat data input for regression (columns become model id and rows become dates)
    
    Inputs
    ------
        X (pd.Dataframe): original dataframe of original and bias corrected climate model timeframes to use for prediction
        method (String): either bias corrected or raw model time series data
        
    Inputs
    ------
        X_formatted (pd.Dataframe): reformatted and pivoted dataframe for direct input into regression
        
    """
    X_formatted = X.loc[X['Method']==method]
    del X_formatted["Method"]
    X_formatted = X_formatted.pivot(columns="Climate Model ID", values=long_name)
    #X_formatted.fillna(0, inplace=True)
    #X_formatted.replace(np.inf, 0)
    #print(X_formatted.stack().mean())
    return X_formatted