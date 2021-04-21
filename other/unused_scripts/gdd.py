import numpy as np
from netCDF4 import Dataset
import sys

# Set time range
yearMin = 2006 
yearMax = 2100

seasonMin = 60      # March 1st
seasonMax = 243     # August 31st

# Specify data directories
dirMin=""
dirMax=""

# List of downscaled products
NEXname = [line.rstrip("\n") for line in open("data/nex_names_rcp.txt","r")]
NEXindex = int(sys.argv[1])-1
NEXname = NEXname[NEXindex]
print(NEXname)

# Read in single file to record coordinate variables for mapping
fileCheck = Dataset(dirMin+NEXname+"_2009.nc")
lats = fileCheck.variables["lat"][:]
lons = fileCheck.variables["lon"][:]

# Create gridded map to store results using same lat/lon as data
map = np.zeros((1+yearMax-yearMin,len(lats),len(lons)))

# Specify critical threshold
a = 10.0 + 273.15
b = 29.0 + 273.15

# Loop over each year
for year in range(yearMin,yearMax+1):
    print("Now calculating: "+str(year))

    datMin = Dataset(dirMin+NEXname+"_"+str(year)+".nc")
    tempMin = datMin.variables["tasmin"][seasonMin:seasonMax,:]
    print("Minimum temperature values read in")

    datMax = Dataset(dirMax+NEXname+"_"+str(year)+".nc")
    tempMax = datMax.variables["tasmax"][seasonMin:seasonMax,:]
    print("Maximum temperature values read in")
    
    # Add days > 10C
    # Case a < Tmin
    tminMask = np.ma.masked_less_equal(tempMin, a)
    tmaxMask = np.ma.masked_less_equal(tempMax, a)
    gdd1 = (tminMask + tmaxMask)/2 - a
    gdd1 = gdd1.filled(0)
    gdd1 = np.sum(gdd1, axis=0)
    # Case Tmin < a < Tmax
    tminMask = np.ma.masked_greater(tempMin, a)
    tmaxMask = np.ma.masked_less(tempMax, a)
    tbar = np.arccos((2*a - tminMask - tmaxMask)/(tmaxMask - tminMask))
    gdd2 = (tbar/3.14159)*((tmaxMask + tminMask)/2 - a) + (tmaxMask-tminMask)*np.sin(tbar)/(2*3.14159)
    gdd2 = gdd2.filled(0)
    gdd2 = np.sum(gdd2, axis=0)

    gdd = gdd1 + gdd2

    # Subtract days > 29C
    # Case b < Tmin
    tminMask = np.ma.masked_less_equal(tempMin, b)
    tmaxMask = np.ma.masked_less_equal(tempMax, b)
    gdd1 = (tminMask + tmaxMask)/2 - b
    gdd1 = gdd1.filled(0)
    gdd1 = np.sum(gdd1, axis=0)
    # Case Tmin < b < Tmax
    tminMask = np.ma.masked_greater(tempMin, b)
    tmaxMask = np.ma.masked_less(tempMax, b)
    tbar = np.arccos((2*b - tminMask - tmaxMask)/(tmaxMask - tminMask))
    gdd2 = (tbar/3.14159)*((tmaxMask + tminMask)/2 - b) + (tmaxMask-tminMask)*np.sin(tbar)/(2*3.14159)
    gdd2 = gdd2.filled(0)
    gdd2 = np.sum(gdd2, axis=0)

    gdd = gdd - gdd1 - gdd2
    
    # Store
    map[year - yearMin] = gdd

print("All years finished! Writing netCDF file now...")
# Write final CDF file
NEXname = NEXname.replace("_day_BCSD","")
dataFinal = Dataset("data/GDD_10-29C_gs_"+NEXname+".nc", "w",format="NETCDF4")

dataFinal.createDimension("lat", len(lats))
dataFinal.createDimension("lon", len(lons))
dataFinal.createDimension('time', 1+yearMax-yearMin)

lat = dataFinal.createVariable("lat",np.float64,("lat",))
lon = dataFinal.createVariable("lon",np.float64,("lon",))
time = dataFinal.createVariable("time",np.int32,("time",))
GDD = dataFinal.createVariable("GDD",np.float64,("time","lat","lon"))

dataFinal.description = "Growing degree days"
lat.units = "Degrees North"
lat.standard_name = "Latitude"
lon.units = "Degrees East"
lon.standard_name = "Longitude"
time.units = "Years"
time.standard_name = "Year"

lat[:] = lats
lon[:] = lons
time[:] = np.linspace(yearMin,yearMax,1+yearMax-yearMin,dtype=int)
GDD[:] = map

dataFinal.close()
print("DONE!")
