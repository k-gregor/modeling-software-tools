# Explanation

This repository accompanies the paper Gregor et al. "TODO title". It shall serve as a simple example for modeling groups, highlighting key tools and concepts to create verified and reproducible scientific code.

## What does this repository do?

This repository contains an entire pipeline a modeling exercise as often done for geoscientific studies, only at a very small and simplified scale.
In this pipeline:
1. Climate data is downloaded from the ISIMIP repository 
2. This data is prepared to adhere to the input format that the model LPJ-GUESS requires
3. An instruction file to do a model run LPJ-GUESS is created from the climate data
4. A grid list is created to run the model for a specified region and resolution
5. The model LPJ-GUESS is run for two regions with simplified parameters
6. The model output is analyzed and plotted
7. The outputs are made available online via GitHub pages

All these steps will happen in a completely automated way.
Furthermore, all required software packages are noted and the model is run within LPJ-GUESS, allowing the simple installation on any machine.

## How does this repository help

1. Shows how you can use snakemake to put your pipelines into code
2. Highlights how to use `environment.yml` to provide a blueprint with the necessary packages and versions so everyone can have the exact same setup as you
3. Includes a Dockerfile to illustrate how a model could be bundled within a Docker image
4. Has unit tests to illustrate testing analysis code
5. Shows how model results can be made publicly available via GitHub pages

This allows any user to reproduce the entire modeling exercise.

# Prerequisites

A few prerequisites need to be installed
- conda
- docker

## Setup up conda environment

Run this command to create the environment from the provided file. This will ensure that the libraries on your machine will be the same versions as the one used in the creation of this repository.
```bash
conda env create -f environment.yml
conda activate model-coding-paper
```
(The environment.yml file was created with the command `conda env export > environment.yml`)

# Run

To run the entire pipeline, simply execute:
```bash
snakemake --cores 4
```
The entire process should take about 2 minutes, but depends on your machine.

When the process has finished, and you execute the command again, the output should look like this:
```bash
Assuming unrestricted shared filesystem usage.
host: <HOSTNAME>
Building DAG of jobs...
Nothing to be done (all requested files are present and up to date).
```
Nothing will be executed because everything is up to date.

Note that when you delete any intermediate file and call this command again, only the affected steps of the workflow are repeated.

## Adapt the modeling workflow

The configuration allows you to rerun the entire workflow easily for any other region. For instance, uncomment the section about `Denmark` in the config file `snakemake_config.yml`.

# Visualize the graph

You can visualize the pipeline by running `snakemake --dag | dot -Tsvg > dag.svg` and then looking at the created graph.



# Docker

The Docker image can be built via
```bash
docker build . -t <YOUR IMAGE NAME>
```

Run LPJ-GUESS with Docker:
```bash
docker run -it kgregor-lpjguess-image ls
```