import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gp
from shapely.geometry import *
import numpy as np
import xarray as xr

 # List of products
name = [line.rstrip("\n") for line in open("cmip_names.txt","r")]
index = int(sys.argv[1])-1
name = name[index]
print(name)
print("\n")

# CMIP data
cmip = xr.open_dataset("data/" + name)

# GMFD grid
lat = cmip.coords["lat"].values
lat_step = abs(lat[1] - lat[0])

lon = cmip.coords["lon"].values
lon_step = abs(lon[1] - lon[0])

US_lat = np.intersect1d(np.argwhere(lat > 24.),np.argwhere(lat < 50.))
US_lon = np.intersect1d(np.argwhere(lon > 360.-125.),np.argwhere(lon < 360.-66.))

# US lat/lon GeoFrame
US_geoF = gp.GeoSeries([Point(lon[US_lon[x]]-360, lat[US_lat[y]]) for x in range(len(US_lon)) for y in range(len(US_lat))])
US_geoF = gp.GeoSeries([Polygon([(lon[US_lon[x]]-360 + lon_step/2, lat[US_lat[y]] + lat_step/2),
                                       (lon[US_lon[x]]-360 + lon_step/2, lat[US_lat[y]] - lat_step/2),
                                       (lon[US_lon[x]]-360 - lon_step/2, lat[US_lat[y]] + lat_step/2),
                                       (lon[US_lon[x]]-360 - lon_step/2, lat[US_lat[y]] - lat_step/2)])
                               for x in range(len(US_lon)) for y in range(len(US_lat))])

US_geo_lon = gp.GeoSeries([US_lon[x] for x in range(len(US_lon)) for y in range(len(US_lat))])
US_geo_lat = gp.GeoSeries([US_lat[y] for x in range(len(US_lon)) for y in range(len(US_lat))])

US_geoF = gp.GeoDataFrame({"geometry": US_geoF, "latitude": US_geo_lat, "longitude": US_geo_lon})
US_geoF["geometry"] = US_geoF.geometry.envelope

US_geoF.crs = {'init' :'epsg:4269'}

# Read in county data
counties = gp.read_file("counties_contig.shp")

# Overlap
final = gp.overlay(counties, US_geoF, how="intersection")

# There are usually some spurious intersections with extremely small areas... filter them out
# Choose 10^-11
final = final[(final.geometry.area > 10e-11)]

# Add county areas
final = pd.merge(final, final.groupby("GEOID",as_index=False).sum().drop(columns = ["latitude", "longitude", "frac"]), on = "GEOID", how = "outer")

# Calculate area fractions of counties
final["area_frac"] = final["area_x"] / final["area_y"]

del final["area_x"]
del final["area_y"]

# Calculate weights within a signle county
final["county_weight"] = final["frac"] * final["area_frac"]

del final["frac"]
del final["area_frac"]

# Calculate normalisations
final = pd.merge(final, final.groupby("GEOID",as_index=False).sum().drop(columns = ["latitude", "longitude"]), on = "GEOID", how = "outer")

# Normalise
final["within_county_weight"] = final["county_weight_x"] / final["county_weight_y"]

del final["county_weight_x"]
del final["county_weight_y"]

final = final.fillna(0)

# Save csv
del final["geometry"]
del final["NAME"]
final = pd.DataFrame(final)

final.to_csv("counties_" + name[15:-3] + "_weighted.csv", index = False)
