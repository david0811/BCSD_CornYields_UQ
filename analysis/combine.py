import numpy as np
import pandas as pd

##################################################
#### Script to combine all individual 
#### model-output csv files into one dataframe
##################################################

#############
## Yield
#############

######## GMFD
def get_gmfd_yield():
    # Read in GMFD data
    gmfd = pd.read_csv('../ag_model/run_model/output/GMFD/res_yield_60-05_gmfd.csv')
    gmfd["GEOID"] = gmfd["GEOID"].astype(str).str.zfill(5)
    gmfd.set_index(["GEOID", "Year"], inplace = True)
    return gmfd

######### NEX-GDDP
def combine_nex_yield():
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
    gmfd = get_gmfd_yield()
    return pd.merge(nex, gmfd.reset_index(), on = ["GEOID", "Year"], how = 'inner')

########## CMIP
def combine_cmip_yield():
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
    gmfd = get_gmfd_yield()
    return pd.merge(cmip, gmfd.reset_index(), on = ["GEOID", "Year"], how = 'inner')

###############
### Ag-vars
###############

########### GMFD
def get_gmfd_agvar():
    gmfd = pd.read_csv("../agvars/GMFD/agvar_historical_gmfd.csv")
    gmfd["GEOID"] = gmfd["GEOID"].astype(str).str.zfill(5)

    # Split ag variables
    temp1 = gmfd.drop(columns = ["egdd","prcp"])
    temp1["AgVar"] = "gdd"
    temp1.rename(columns = {"gdd" : "GMFD"}, inplace = True)
    temp1.set_index(["AgVar", "GEOID", "Year"], inplace = True)

    temp2 = gmfd.drop(columns = ["gdd","prcp"])
    temp2["AgVar"] = "egdd"
    temp2.rename(columns = {"egdd" : "GMFD"}, inplace = True)
    temp2.set_index(["AgVar", "GEOID", "Year"], inplace = True)

    temp3 = gmfd.drop(columns = ["gdd","egdd"])
    temp3["AgVar"] = "prcp"
    temp3.rename(columns = {"prcp" : "GMFD"}, inplace = True)
    temp3.set_index(["AgVar", "GEOID", "Year"], inplace = True)

    # Join with updated indexing
    gmfd = temp1.append(temp2).append(temp3)
    return gmfd


######## NEX-GDDP
def combine_nex_agvar():
    # Historical hindcasts of all models
    nex_hind = ["agvar_historical_r1i1p1_ACCESS1-0.csv",
                "agvar_historical_r1i1p1_BNU-ESM.csv",
                "agvar_historical_r1i1p1_CCSM4.csv",
                "agvar_historical_r1i1p1_CESM1-BGC.csv",
                "agvar_historical_r1i1p1_CNRM-CM5.csv",
                "agvar_historical_r1i1p1_CSIRO-Mk3-6-0.csv",
                "agvar_historical_r1i1p1_CanESM2.csv",
                "agvar_historical_r1i1p1_GFDL-CM3.csv",
                "agvar_historical_r1i1p1_GFDL-ESM2G.csv",
                "agvar_historical_r1i1p1_GFDL-ESM2M.csv",
                "agvar_historical_r1i1p1_IPSL-CM5A-LR.csv",
                "agvar_historical_r1i1p1_IPSL-CM5A-MR.csv",
                "agvar_historical_r1i1p1_MIROC-ESM-CHEM.csv",
                "agvar_historical_r1i1p1_MIROC-ESM.csv",
                "agvar_historical_r1i1p1_MIROC5.csv",
                "agvar_historical_r1i1p1_MPI-ESM-LR.csv",
                "agvar_historical_r1i1p1_MPI-ESM-MR.csv",
                "agvar_historical_r1i1p1_MRI-CGCM3.csv",
                "agvar_historical_r1i1p1_NorESM1-M.csv",
                "agvar_historical_r1i1p1_bcc-csm1-1.csv",
                "agvar_historical_r1i1p1_inmcm4.csv"]
    
    nex  = pd.read_csv("../agvars/NEX-GDDP/" + nex_hind[0])
    nex["GEOID"] = nex["GEOID"].astype(str).str.zfill(5)

    # Split ag variables
    temp1 = nex.drop(columns = ["egdd","prcp"])
    temp1["AgVar"] = "gdd"
    temp1.rename(columns = {"gdd" : nex_hind[0].replace("historical_r1i1p1_","").replace(".csv","").replace("agvar_","")}, inplace = True)
    temp1.set_index(["AgVar", "GEOID", "Year"], inplace = True)

    temp2 = nex.drop(columns = ["gdd","prcp"])
    temp2["AgVar"] = "egdd"
    temp2.rename(columns = {"egdd" : nex_hind[0].replace("historical_r1i1p1_","").replace(".csv","").replace("agvar_","")}, inplace = True)
    temp2.set_index(["AgVar", "GEOID", "Year"], inplace = True)

    temp3 = nex.drop(columns = ["gdd","egdd"])
    temp3["AgVar"] = "prcp"
    temp3.rename(columns = {"prcp" : nex_hind[0].replace("historical_r1i1p1_","").replace(".csv","").replace("agvar_","")}, inplace = True)
    temp3.set_index(["AgVar", "GEOID", "Year"], inplace = True)

    # Join with updated indexing
    nex = temp1.append(temp2).append(temp3)

    for name in nex_hind[1:]:
        # Read in product
        data = pd.read_csv("../agvars/NEX-GDDP/" + name)
        data["GEOID"] = data["GEOID"].astype(str).str.zfill(5)
        model = name.replace("historical_r1i1p1_","").replace(".csv","").replace("agvar_","")
    
        # Split & join
        temp1 = data.drop(columns = ["egdd","prcp"])
        temp1["AgVar"] = "gdd"
        temp1.rename(columns = {"gdd" : model.replace("historical_r1i1p1_","").replace(".csv","").replace("agvar_","")}, inplace = True)
        temp1.set_index(["AgVar", "GEOID", "Year"], inplace = True)
    
        temp2 = data.drop(columns = ["gdd","prcp"])
        temp2["AgVar"] = "egdd"
        temp2.rename(columns = {"egdd" : model.replace("historical_r1i1p1_","").replace(".csv","").replace("agvar_","")}, inplace = True)
        temp2.set_index(["AgVar", "GEOID", "Year"], inplace = True)
    
        temp3 = data.drop(columns = ["gdd","egdd"])
        temp3["AgVar"] = "prcp"
        temp3.rename(columns = {"prcp" : model.replace("historical_r1i1p1_","").replace(".csv","").replace("agvar_","")}, inplace = True)
        temp3.set_index(["AgVar", "GEOID", "Year"], inplace = True)

        temp = temp1.append(temp2).append(temp3)
    
        # Do the merge
        #print("Now merging... " + model)
        nex = pd.merge(nex, temp, on = ["AgVar", "GEOID", "Year"], how = "outer")
        #print("Merge complete.")
        
    # Merge NEX with GMFD
    gmfd = get_gmfd_agvar()
    nex_all = pd.merge(nex.reset_index(), gmfd.reset_index(), on = ["AgVar", "GEOID", "Year"], how = 'inner')
    return nex_all
    
    
######### CMIP
def combine_cmip_agvar():
    # Hindcasts & projections of all models
    cmip_hind = ["agvar_ACCESS1-0.historical+rcp85.csv",
                 "agvar_BNU-ESM.historical+rcp85.csv",
                 "agvar_CCSM4_historical+rcp85.csv",
                 "agvar_CESM1-BGC.historical+rcp85.csv",
                 "agvar_CNRM-CM5.historical+rcp85.csv",
                 "agvar_CSIRO-Mk3-6-0.historical+rcp85.csv",
                 "agvar_CanESM2.historical+rcp85.csv",
                 "agvar_GFDL-CM3.historical+rcp85.csv",
                 "agvar_GFDL-ESM2G.historical+rcp85.csv",
                 "agvar_GFDL-ESM2M.historical+rcp85.csv",
                 "agvar_IPSL-CM5A-LR.historical+rcp85.csv",
                 "agvar_IPSL-CM5A-MR.historical+rcp85.csv",
                 "agvar_MIROC-ESM-CHEM.historical+rcp85.csv",
                 "agvar_MIROC-ESM.historical+rcp85.csv",
                 "agvar_MIROC5.historical+rcp85.csv",
                 "agvar_MPI-ESM-LR.historical+rcp85.csv",
                 "agvar_MPI-ESM-MR.historical+rcp85.csv",
                 "agvar_MRI-CGCM3.historical+rcp85.csv",
                 "agvar_NorESM1-M.historical+rcp85.csv",
                 "agvar_bcc-csm1-1_historical+rcp85.csv",
                 "agvar_inmcm4.historical+rcp85.csv"]
    
    # Get cmip models
    cmip  = pd.read_csv("../agvars/CMIP/" + cmip_hind[0])
    cmip["GEOID"] = cmip["GEOID"].astype(str).str.zfill(5)

    # Split ag variables
    temp1 = cmip.drop(columns = ["egdd","prcp"])
    temp1["AgVar"] = "gdd"
    temp1.rename(columns = {"gdd" : cmip_hind[0].replace(".historical+rcp85","").replace(".csv","").replace("agvar_","")}, inplace = True)
    temp1.set_index(["AgVar", "GEOID", "Year"], inplace = True)

    temp2 = cmip.drop(columns = ["gdd","prcp"])
    temp2["AgVar"] = "egdd"
    temp2.rename(columns = {"egdd" : cmip_hind[0].replace(".historical+rcp85","").replace(".csv","").replace("agvar_","")}, inplace = True)
    temp2.set_index(["AgVar", "GEOID", "Year"], inplace = True)

    temp3 = cmip.drop(columns = ["gdd","egdd"])
    temp3["AgVar"] = "prcp"
    temp3.rename(columns = {"prcp" : cmip_hind[0].replace(".historical+rcp85","").replace(".csv","").replace("agvar_","")}, inplace = True)
    temp3.set_index(["AgVar", "GEOID", "Year"], inplace = True)

    # Join with updated indexing
    cmip = temp1.append(temp2).append(temp3)

    for name in cmip_hind[1:]:
        # Read in product
        data = pd.read_csv("../agvars/CMIP/" + name)
        data["GEOID"] = data["GEOID"].astype(str).str.zfill(5)
        model = name.replace(".historical+rcp85","").replace(".csv","").replace("agvar_","").replace("_historical+rcp85","")
    
        # Split & join
        temp1 = data.drop(columns = ["egdd","prcp"])
        temp1["AgVar"] = "gdd"
        temp1.rename(columns = {"gdd" : model.replace("historical_r1i1p1_","").replace(".csv","").replace("agvar_","")}, inplace = True)
        temp1.set_index(["AgVar", "GEOID", "Year"], inplace = True)
    
        temp2 = data.drop(columns = ["gdd","prcp"])
        temp2["AgVar"] = "egdd"
        temp2.rename(columns = {"egdd" : model.replace("historical_r1i1p1_","").replace(".csv","").replace("agvar_","")}, inplace = True)
        temp2.set_index(["AgVar", "GEOID", "Year"], inplace = True)
    
        temp3 = data.drop(columns = ["gdd","egdd"])
        temp3["AgVar"] = "prcp"
        temp3.rename(columns = {"prcp" : model.replace("historical_r1i1p1_","").replace(".csv","").replace("agvar_","")}, inplace = True)
        temp3.set_index(["AgVar", "GEOID", "Year"], inplace = True)

        temp = temp1.append(temp2).append(temp3)
    
        # Do the merge
        #print("Now merging... " + model)
        cmip = pd.merge(cmip, temp, on = ["AgVar", "GEOID", "Year"], how = "outer")
        #print("Merge complete.")
        
    # Merge CMIP with GMFD
    gmfd = get_gmfd_agvar()
    cmip_all = pd.merge(cmip.reset_index(), gmfd.reset_index(), on = ["AgVar", "GEOID", "Year"], how = 'inner')
    return cmip_all