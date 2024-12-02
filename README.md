# Explanation

## What does this repository do?

- download isimip data
- prepare this data for LPJ-GUESS
- run LPJ-GUESS in Docker container
- provide jupyter notebook with simple output data analysis


# Prerequisites
- conda
- cdo: `sudo apt install cdo`

# Setup up conda environment
TODO: currently working with isimip_forestry2 kernel, but later replace it with env.yaml with only necessary things!
conda create -n model-coding-paper -c conda-forge -c bioconda rasterio rioxarray xarray snakemake numpy pandas geotiff netcdf4 matplotlib ipykernel geopandas cartopy dask psutil



# Run

# Visualize
`snakemake --dag | dot -Tsvg > dag.svg`