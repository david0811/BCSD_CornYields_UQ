import pandas as pd
import numpy as np
import xarray as xr
import sys

# Set time range
yearMin = 2006
yearMax = 2100

# List of downscaled products
NEXname = [line.rstrip("\n") for line in open("nex_names.txt","r")]
NEXindex = int(sys.argv[1])-1
NEXname = NEXname[NEXindex]
NEXname = NEXname.replace("_day_BCSD","")
print(NEXname)

# Specify data products
gdd="data/GDD_10-29C_gs_" + NEXname + ".nc"
egdd="data/GDD_29C_gs_" + NEXname + ".nc"
precip = "data/cuml_precip_gs_" + NEXname + ".nc"

# Read data products
gdd = xr.open_dataset(gdd)
egdd = xr.open_dataset(egdd)
precip = xr.open_dataset(precip)
print("Read in climate data successfully")

# Read in grid
final = pd.read_csv("counties_NEX_area.csv")
final["GEOID"] = final["GEOID"].astype(str).str.zfill(5)

# Build index structure for dataframe
unique_geoids = np.load("unique_geoids.npy")
years = np.arange(yearMin, yearMax+1, 1) 

unique_geoids = [[unique_geoid]*len(years) for unique_geoid in unique_geoids]
unique_geoids = np.ndarray.flatten(np.asarray(unique_geoids))

years = [years] * len(unique_geoids)
years = np.ndarray.flatten(np.asarray(years))

tuples = list(zip(*[unique_geoids, years]))

index = pd.MultiIndex.from_tuples(tuples)

# Build empty dataframe with complete indexing
proj_final = pd.DataFrame(index = index)
proj_final.index.names = ["GEOID", "Year"]
proj_final["gdd"] = 0.
proj_final["egdd"] = 0.
proj_final["prcp"] = 0.

print("Calculating...")
# Calulate projections
for geoid in proj_final.index.unique(level = "GEOID"):
    pd_temp = final[final.GEOID == geoid]
    for year in proj_final.index.unique(level = "Year"):
        temp_gdd = 0.
        temp_egdd = 0.
        temp_prcp = 0.
        for index, row in pd_temp.iterrows():
            temp_gdd += (gdd.isel(lat = row["latitude"], lon = row["longitude"], time = year-yearMin)["GDD"] * row["area_frac"])
            temp_egdd += (egdd.isel(lat = row["latitude"], lon = row["longitude"], time = year-yearMin)["GDD"] * row["area_frac"])
            temp_prcp += (precip.isel(lat = row["latitude"], lon = row["longitude"], time = year-yearMin)["prcp"] * row["area_frac"])
        
        proj_final.loc[geoid, year]["gdd"] = temp_gdd
        proj_final.loc[geoid, year]["egdd"] = temp_egdd
        proj_final.loc[geoid, year]["prcp"] = temp_prcp

# Save
proj_final.reset_index().to_csv("agvar"+NEXname+".csv", index = False)
print("DONE!")
