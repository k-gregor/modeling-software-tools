# Explanation

This repository accompanies the paper Gregor et al. "TODO title". It shall serve as a simple example for modeling groups, highlighting key tools and concepts to create verified and reproducible scientific code.

## What does this repository do?

This repository contains an entire pipeline a modeling exercise as often done for geo-scientific studies, only at a very small and simplified scale.
In this pipeline:
1. Climate data is downloaded from the ISIMIP repository 
2. This data is prepared to adhere to the input format that the model LPJ-GUESS requires
3. An instruction file to do a model run LPJ-GUESS is created from the climate data
4. A grid list is created to run the model for a specified region, and a graphic is created to visualize this region, see `lpjguess_instruction_files/chelsa-w5e5_1800arcsec_bavaria_gridlist.txt.png`
4. The model LPJ-GUESS is run with this climate data for a region in Germany with simplified parameters
5. The model output is analyzed and plotted

All these steps will happen in a completely automated way.
Furthermore, all required software packages are noted, allowing the simple installation on any machine.

TODO Docker once included

## How does this repository help

1. Shows how you can use snakemake to put your pipelines into code
2. Highlights how to use `environment.yml` to provide a blueprint with the necessary packages and versions so everyone can have the exact same setup as you
3. Docker...

This allows any user to reproduce the entire modeling exercise.

# Prerequisites

A few prerequisites need to be
- conda

## Setup up conda environment

Run this command to create the environment from the provided file. This will ensur that the libraries on your machine will be the same versions as the one used in the creation of this repository.
```bash
conda env create -f environment.yml
conda activate model-coding-paper
```


TODO, maybe everything should go into a Docker container??


# Run

To run the entire pipeline, simply execute:
```bash
snakemake --cores 12
```
The entire process should take about 2 minutes, but depends on your machine.

When the process has finished, and you execute the command again, the output should look like this:
```bash
Assuming unrestricted shared filesystem usage.
host: konni-tum
Building DAG of jobs...
Nothing to be done (all requested files are present and up to date).
```
Nothing will be executed because everything is up to date.


Note that when you delete any intermediate file and call this command again, only the affected steps of the workflow are repeated.

Note that this simulation is highly simplified! TODO mention npatch, nyear_spinup, cycled climate data.

## Adapt the modeling workflow

The configuration allows you to rerun the entire workflow easily for any other region. For instance, uncomment the section about `Denmark` in the config file `snakemake_config.yml`.


# Visualize
You can visualize the pipeline by running `snakemake --dag | dot -Tsvg > dag.svg` and then looking at the created graph.



# Docker stuff

Create the image:
```bash
sudo docker build . -t kgregor-lpjguess-image
```

Run LPJ-GUESS with Docker:
```bash
sudo docker run -it kgregor-lpjguess-image ls
```