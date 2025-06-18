#
# Daniel Pflueger, created on 2021-29-11 
# d.pfluger@uu.nl
#
# Modified by Jasper de Jong (2021-02-12)
# j.dejong3@uu.nl
#
# Licensed under Creative Commons - Attribution-NonCommercial-ShareAlike 4.0 International
# CC BY-NC-SA 4.0 https://creativecommons.org/licenses/by-nc-sa/4.0/
#

import xarray as xr
import numpy as np

def global_mean(da,**kwargs):
    """
    Takes an xarray DataArray defined over a lat(+lon optionally) field and returns global mean 
    computed with correct weighting factors.

    Parameters:
    ---
    da (xr.DataArray): DataArray containing a field defined over latitudes (lat) and longitudes (lon) and optionally time
    kwargs (optional): Kept for backwards compatibility ('zonal' keyword-argument used in old versions).
    
    Note 02-12-21 (Jasper): The latitude weights are now calculated using latitude bounds, making them more precise
    especially at the poles. I compared them using the 'gw' variable in my dataset and it is consistent except for a
    factor of two. I've concluded that the gw variable in my data is wrong, as the sum of gw is 2 instead of 1, explaining
    the difference! I left some assert statements that will check if the data is okay to use. Feel free 
    to remove them if the code works. 

    Returns:
    ---
    float or DataArray: Global mean of the field (over time)
    """
    assert da.lat.diff(dim='lat').std() < 1e-12, "latitudes should be equally spaced"
    assert all(da.lat.diff(dim='lat') > 0), "latitude should be ascending"
    
    if 'lon' in list(da.dims): # take zonal average
        assert da.lon.diff(dim='lon').std() < 1e-12, "longitudes should be equally spaced"
        da = da.mean(dim='lon') 
    
    lat_bnds = np.deg2rad([-90, *(da.lat.data[1:]+da.lat.data[:-1])/2, 90])
    gw = xr.DataArray(data=0.5*np.diff(np.sin(lat_bnds)),dims='lat') # latitude grid weights

    return da.weighted(gw).mean(dim='lat')
