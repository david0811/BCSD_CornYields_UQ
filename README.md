# Statistically bias-corrected and downscaled climate models underestimate the severity of U.S. maize yield shocks

This respository contains all data and code required to reproduce the analysis in:<br />
*Lafferty et. al., Statistically bias-corrected and downscaled climate models underestimate the severity of U.S. maize yield shocks (2021)*.

![alt text](https://github.com/david0811/BCSD_CornYields_UQ/blob/master/figs/figure2.png)

To run the analysis start to finish, run all cells in each notebook in the following order:
1. `usda/usda_records.ipynb`
2. `ag_model/fit_model/ag_model_fit.ipynb`
3. `ag_model/run_model/ag_model_run.ipynb`
4. `analysis/national.ipynb` (this notebook produces Figures 1 & 4)
5. `analysis/county_yield.ipynb` (this notebook produces Figure 2)
6. `analysis/county_agvar.ipynb` (this notebook produces Figure 3)

***Note:*** The `agvars` and `plotting_tools` directories were stored with [Git LFS](https://git-lfs.github.com) but can also be accessed [here](https://uillinoisedu-my.sharepoint.com/:f:/g/personal/davidcl2_illinois_edu/EgrWzY0BfhpFrUhqRmLFUXEBwHk84o_eWusCtMqyfsGJww?e=G9ofNy). The calculation of county-level degree days from the native NEX-GDDP and CMIP netcdf files was performed offline, but you can find scripts showing the basic structure in `other`.

For the conda environment used throughout the analysis, see `environment.yml`. Python packages required:
- `numpy`
- `matplotlib`
- `pandas`
- `geopandas`
- `scipy`
- `statsmodels`
- `scikit-learn`
- `jupyterlab`<br />
