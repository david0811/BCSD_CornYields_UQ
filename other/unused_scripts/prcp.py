import numpy as np
from netCDF4 import Dataset
import sys

# Set time range
yearMin = 2006 
yearMax = 2099

seasonMin = 60      # March 1st
seasonMax = 243     # August 31st

# Specify data directories
dirMin=""
dirMax=""

# List of downscaled products
NEXname = [line.rstrip("\n") for line in open("nex_names_rcp.txt","r")]
NEXindex = int(sys.argv[1])-1
NEXname = NEXname[NEXindex]
print(NEXname)

# Read in single file to record coordinate variables for mapping
fileCheck = Dataset(dirMin+NEXname+"_2009.nc")
lats = fileCheck.variables["lat"][:]
lons = fileCheck.variables["lon"][:]

# Create gridded map to store results using same lat/lon as data
prcp = np.zeros((1+yearMax-yearMin,len(lats),len(lons)))

# Loop over each year
for year in range(yearMin,yearMax+1):
    print("Now calculating: "+str(year))

    dat = Dataset(dirMin+NEXname+"_"+str(year)+".nc")
    prcp_temp = dat.variables["pr"][seasonMin:seasonMax,:]
    print("Precip values read in")
    
    prcp_temp = np.ma.masked_values(prcp_temp, 1.e+20)
    prcp_temp = prcp_temp.filled(0)
    prcp_temp = prcp_temp * 60. * 60. * 24. / 1000. # s^-1 to day^-1 + unit conversion
    
    prcp_temp = np.sum(prcp_temp, axis=0)
    
    prcp[year - yearMin] = prcp_temp

print("All years finished! Writing netCDF file now...")
# Write final CDF file
NEXname = NEXname.replace("_day_BCSD","")
dataFinal = Dataset("data/cuml_precip_gs_"+NEXname+".nc", "w",format="NETCDF4")

dataFinal.createDimension("lat", len(lats))
dataFinal.createDimension("lon", len(lons))
dataFinal.createDimension('time', 1+yearMax-yearMin)

lat = dataFinal.createVariable("lat",np.float64,("lat",))
lon = dataFinal.createVariable("lon",np.float64,("lon",))
time = dataFinal.createVariable("time",np.int32,("time",))
precip = dataFinal.createVariable("prcp",np.float64,("time","lat","lon"))

dataFinal.description = "Growing season total precipitation"
lat.units = "Degrees North"
lat.standard_name = "Latitude"
lon.units = "Degrees East"
lon.standard_name = "Longitude"
time.units = "Years"
time.standard_name = "Year"
precip.units = "m m-2"
precip.standard_name = "Precipitation"

lat[:] = lats
lon[:] = lons
time[:] = np.linspace(yearMin,yearMax,1+yearMax-yearMin,dtype=int)
precip[:] = prcp

dataFinal.close()
print("DONE!")
