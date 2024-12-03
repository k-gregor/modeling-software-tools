# Author: Konstantin Gregor (konstantin.gregor@tum.de)
# This Dockerfile creates a Docker image with Linux and all necessary libraries to run LPJ-GUESS (i.e., cmake, NetCDF, MPI, ...) and the compiled model
#
# You can create an image via:
# sudo docker build . -t kgregor-lpjguess-image

# starting from a Ubuntu 22.04 installation
FROM ubuntu:jammy

# install necessary libraries
RUN apt-get update && \
	apt-get install -y build-essential git cmake autoconf libtool pkg-config
RUN apt-get install -y libnetcdf-dev libnetcdff-dev
RUN apt-get install -y mpi libmpich-dev
# to unpack the zenodo-downloaded LPJ-GUESS code
RUN apt-get install -y unzip

# download the latest release of LPJ-GUESS and unzip
RUN wget https://zenodo.org/records/8065737/files/guess_4.1.1.zip
RUN unzip guess_4.1.1.zip

# compile LPJ-GUESS
WORKDIR /guess_4.1
RUN mkdir cmake-build-release
RUN cmake -DCMAKE_BUILD_TYPE=Release -S . -B cmake-build-release -Wno-dev
RUN cmake --build cmake-build-release --target guess -- -Wno-dev -j 8
