import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gp
import warnings
warnings.simplefilter("ignore", RuntimeWarning) # Ignore invalid arcsin() in EDD calculation
import xagg as xa

##########################################################
### Calculate variables at grid cell level
##########################################################

# degree day function
def above_threshold_each(mins, maxs, threshold):
    """Use a sinusoidal approximation to estimate the number of Growing
    Degree-Days above a given threshold, using daily minimum and maximum
    temperatures.
    mins and maxs are numpy arrays; threshold is in the same units."""

    """
    Code from James Rising (https://github.com/jrising/research-common/blob/master/python/gdd.py)
    """

    # Determine crossing points, as a fraction of the day
    plus_over_2 = (mins + maxs)/2
    minus_over_2 = (maxs - mins)/2
    two_pi = 2*np.pi
    # d0s is the times of crossing above; d1s is when cross below
    d0s = np.arcsin((threshold - plus_over_2) / minus_over_2) / two_pi
    d1s = .5 - d0s

    # If always above or below threshold, set crossings accordingly
    aboves = mins >= threshold
    belows = maxs <= threshold

    d0s[aboves] = 0
    d1s[aboves] = 1
    d0s[belows] = 0
    d1s[belows] = 0

    # Calculate integral
    F1s = -minus_over_2 * np.cos(2*np.pi*d1s) / two_pi + plus_over_2 * d1s
    F0s = -minus_over_2 * np.cos(2*np.pi*d0s) / two_pi + plus_over_2 * d0s
    return F1s - F0s - threshold * (d1s - d0s)

# ufunc for dask
def edd_ufunc_annual(tasmin, tasmax, threshold = 29.0 + 273.0):
    return xr.apply_ufunc(above_threshold_each,
                          tasmin, tasmax, threshold,
                          dask = 'allowed')

# Read in all
NEX_obs_tmin = xr.open_mfdataset('PATH_TO_DATA/tmin*.nc', parallel=True, chunks='auto')
NEX_obs_tmax = xr.open_mfdataset('PATH_TO_DATA/tmax*.nc', parallel=True, chunks='auto')
NEX_obs_prcp = xr.open_mfdataset('PATH_TO_DATA/prcp*.nc', parallel=True, chunks='auto')

# Select growing season (Mar - Aug)
NEX_obs_tmin = NEX_obs_tmin.sel(time=NEX_obs_tmin.time.dt.month.isin([3, 4, 5, 6, 7, 8]))
NEX_obs_tmax = NEX_obs_tmax.sel(time=NEX_obs_tmax.time.dt.month.isin([3, 4, 5, 6, 7, 8]))
NEX_obs_prcp = NEX_obs_prcp.sel(time=NEX_obs_prcp.time.dt.month.isin([3, 4, 5, 6, 7, 8]))

# Combine tmin/tmax
NEX_obs = xr.combine_by_coords([NEX_obs_tmin['tmin'].to_dataset(name = 'tmin'),
                                NEX_obs_tmax['tmax'].to_dataset(name = 'tmax')])

# Calculate annual EDD
NEX_obs_EDD = edd_ufunc_annual(NEX_obs['tmin'], NEX_obs['tmax'])
NEX_obs_EDD = NEX_obs_EDD.resample(time='Y').sum().compute()

# Calculate annual GDD
NEX_obs_GDD = edd_ufunc_annual(NEX_obs['tmin'], NEX_obs['tmax'], threshold = 273.0 + 10.0)
NEX_obs_GDD = NEX_obs_GDD.resample(time='Y').sum().compute()
NEX_obs_GDD = NEX_obs_GDD - NEX_obs_EDD

# Calculate annual precip
NEX_obs_P = NEX_obs_prcp.resample(time='Y').sum().compute()
NEX_obs_P = NEX_obs_P * 60. * 60. * 24. # convert to mm

##########################################################
### Aggregate to county level (area weighted)
### (only shown for EDD)
##########################################################

# US county shapeful
us_county = gp.read_file('../plotting_tools/counties_contig_plot.shp')
us_county = us_county.to_crs("EPSG:4326")

# Area weight and aggregate
weightmap = xa.pixel_overlaps(NEX_obs_EDD, us_county)
aggregated = xa.aggregate(NEX_obs_EDD, weightmap)

# Convert to pandas
ds_out = aggregated.to_dataset().to_dataframe()
ds_out = ds_out.reset_index().set_index(['fips','time']).drop(columns='pix_idx')
