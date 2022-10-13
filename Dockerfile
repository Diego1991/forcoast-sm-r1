#(C) Copyright FORCOAST H2020 project under Grant No. 870465. All rights reserved.

# Copyright notice
#   --------------------------------------------------------------------
#   Copyright (C) 2022 Marine Institute, Deltares
#       Diego Pereiro, Gido Stoop
#
#       diego.pereiro@marine.ie, gido.stoop@deltares.nl
#
#   This library is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this library.  If not, see <http://www.gnu.org/licenses/>.
#   --------------------------------------------------------------------

# See https://opendrift.github.io for usage

FROM continuumio/miniconda3

RUN apt-get update && apt-get -y install imagemagick

ENV DEBIAN_FRONTEND noninteractive
ENV PATH /code/opendrift/opendrift/scripts:$PATH

RUN mkdir /code
WORKDIR /code

RUN conda config --add channels noaa-orr-erd
RUN conda config --add channels conda-forge
RUN conda config --add channels opendrift

# Install opendrift environment into base conda environment
# Copy following from opendrift repo:
# - opendrift folder
# - environment.yml
# - setup.py
COPY environment.yml /code

RUN /opt/conda/bin/conda env update -n base -f environment.yml

# Install opendrift
ADD . /code
RUN pip install -e .

# Test installation
RUN /bin/bash -c "echo -e \"import opendrift\" | python"

# Install wget and erddapy

COPY ["required.txt", "/usr/src/app/"]

RUN apt-get update && apt-get install libgl1 -y 
RUN pip install -r /usr/src/app/required.txt

# Add Service Module files
WORKDIR /usr/src/app
COPY ["SM-R1.py", "./"]
COPY ["send_bulletin.py", "./"]
COPY ["run_diego.sh", "./"]
COPY ["run.sh", "./"]
COPY ["R1.yaml", "./"]
COPY ["Pilot-*-seafloor-depth.nc", "./"]
COPY ["landmask.*", "./"]
COPY ["*.png", "./"]
COPY ["*.ttf", "./"]
COPY ["area.txt", "./"]
COPY ["bulletin_script.py", "./"]
COPY ["policy.xml", "/etc/ImageMagick-6/policy.xml"]

RUN chmod 755 /usr/src/app/run.sh
RUN chmod 755 /usr/src/app/run_diego.sh

# Replace OpenDrift's code with Service Module's code
COPY ["basemodel.py", "/code/opendrift/models/"]
COPY ["reader_netCDF_CF_generic.py", "/code/opendrift/readers/"]

ENTRYPOINT ["/usr/src/app/run.sh"]
# ENTRYPOINT ["bash", "-c"]
