import numpy as np
import pandas as pd

##################################################
#### Script to combine all individual 
#### model-output csv files into one dataframe
##################################################

# Read in GMFD data
gmfd = pd.read_csv('../ag_model/run_model/output/GMFD/res_yield_60-05_gmfd.csv')
gmfd["GEOID"] = gmfd["GEOID"].astype(str).str.zfill(5)
gmfd.set_index(["GEOID", "Year"], inplace = True)

# NEX-GDDP
nex_hist = ["yield_historical_r1i1p1_ACCESS1-0.csv",
"yield_historical_r1i1p1_BNU-ESM.csv",
"yield_historical_r1i1p1_CCSM4.csv",
"yield_historical_r1i1p1_CESM1-BGC.csv",
"yield_historical_r1i1p1_CNRM-CM5.csv",
"yield_historical_r1i1p1_CSIRO-Mk3-6-0.csv",
"yield_historical_r1i1p1_CanESM2.csv",
"yield_historical_r1i1p1_GFDL-CM3.csv",
"yield_historical_r1i1p1_GFDL-ESM2G.csv",
"yield_historical_r1i1p1_GFDL-ESM2M.csv",
"yield_historical_r1i1p1_IPSL-CM5A-LR.csv",
"yield_historical_r1i1p1_IPSL-CM5A-MR.csv",
"yield_historical_r1i1p1_MIROC-ESM-CHEM.csv",
"yield_historical_r1i1p1_MIROC-ESM.csv",
"yield_historical_r1i1p1_MIROC5.csv",
"yield_historical_r1i1p1_MPI-ESM-LR.csv",
"yield_historical_r1i1p1_MPI-ESM-MR.csv",
"yield_historical_r1i1p1_MRI-CGCM3.csv",
"yield_historical_r1i1p1_NorESM1-M.csv",
"yield_historical_r1i1p1_bcc-csm1-1.csv",
"yield_historical_r1i1p1_inmcm4.csv"]

def combine_nex():
    # Get nex models
    nex  = pd.read_csv("../ag_model/run_model/output/NEX-GDDP/res_60-05_" + nex_hist[0])
    nex["GEOID"] = nex["GEOID"].astype(str).str.zfill(5)
    nex = nex.query('Year <= 2005')
    nex.rename(columns = {"yield" : nex_hist[0].replace("historical_r1i1p1_","").replace(".csv","").replace("yield_","")}, inplace = True)

    for name in nex_hist[1:]:
        # Read in product
        data = pd.read_csv("../ag_model/run_model/output/NEX-GDDP/res_60-05_" + name)
        data = data.query('Year <= 2005')
        data["GEOID"] = data["GEOID"].astype(str).str.zfill(5)
        # Model name
        model = name.replace("historical_r1i1p1_","").replace(".csv","").replace("yield_","")
        data.rename(columns = {"yield" : model}, inplace = True)
        # Do the merge
        #print("Read in: " + model + ". Shape: " + str(data.shape) + ". Merging now...")
        nex = pd.merge(nex, data, on = ["GEOID", "Year"], how = "outer")
        #print("Merge complete. New shape: " + str(nex.shape))
    
    # Drop NaNs and zeros (they are all at the same location)
    nex.dropna(inplace = True)
    nex = nex[nex.inmcm4 != 0]
    
    # Merge CMIP with GMFD
    return pd.merge(nex, gmfd.reset_index(), on = ["GEOID", "Year"], how = 'outer').dropna()


# CMIP
cmip_names = ["yield_ACCESS1-0.historical+rcp85.csv",
"yield_BNU-ESM.historical+rcp85.csv",
"yield_CCSM4_historical+rcp85.csv",
"yield_CESM1-BGC.historical+rcp85.csv",
"yield_CNRM-CM5.historical+rcp85.csv",
"yield_CSIRO-Mk3-6-0.historical+rcp85.csv",
"yield_CanESM2.historical+rcp85.csv",
"yield_GFDL-CM3.historical+rcp85.csv",
"yield_GFDL-ESM2G.historical+rcp85.csv",
"yield_GFDL-ESM2M.historical+rcp85.csv",
"yield_IPSL-CM5A-LR.historical+rcp85.csv",
"yield_IPSL-CM5A-MR.historical+rcp85.csv",
"yield_MIROC-ESM-CHEM.historical+rcp85.csv",
"yield_MIROC-ESM.historical+rcp85.csv",
"yield_MIROC5.historical+rcp85.csv",
"yield_MPI-ESM-LR.historical+rcp85.csv",
"yield_MPI-ESM-MR.historical+rcp85.csv",
"yield_MRI-CGCM3.historical+rcp85.csv",
"yield_NorESM1-M.historical+rcp85.csv",
"yield_bcc-csm1-1_historical+rcp85.csv",
"yield_inmcm4.historical+rcp85.csv"]


def combine_cmip():
    # Get cmip models
    cmip  = pd.read_csv("../ag_model/run_model/output/CMIP/res_60-05_" + cmip_names[0])
    cmip["GEOID"] = cmip["GEOID"].astype(str).str.zfill(5)
    cmip = cmip.query('Year >= 1960 and Year <= 2005')
    cmip.rename(columns = {"yield" : cmip_names[0].replace(".historical+rcp85","").replace(".csv","").replace("yield_","")}, inplace = True)

    for name in cmip_names[1:]:
        # Read in product
        data = pd.read_csv("../ag_model/run_model/output/CMIP/res_60-05_" + name)
        data["GEOID"] = data["GEOID"].astype(str).str.zfill(5)
        data = data.query('Year >= 1960 and Year <= 2005')
        # Model name
        model = name.replace(".historical+rcp85","").replace("_historical+rcp85","").replace(".csv","").replace("yield_","")
        data.rename(columns = {"yield" : model}, inplace = True)
        # Do the merge
        #print("Read in: " + model + ". Shape: " + str(data.shape) + ". Merging now...")
        cmip = pd.merge(cmip, data, on = ["GEOID", "Year"], how = "outer")
        #print("Merge complete. New shape: " + str(cmip.shape))
    
    # Drop NaNs and zeros (they are all at the same location)
    cmip.dropna(inplace = True)
    cmip = cmip[cmip.inmcm4 != 0]
    
    # Merge CMIP with GMFD
    return pd.merge(cmip, gmfd.reset_index(), on = ["GEOID", "Year"], how = 'outer').dropna()