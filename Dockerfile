# See https://opendrift.github.io for usage

FROM continuumio/miniconda3

ENV DEBIAN_FRONTEND noninteractive
ENV PATH /code/opendrift/opendrift/scripts:$PATH

RUN mkdir /code
WORKDIR /code

RUN conda config --add channels noaa-orr-erd
RUN conda config --add channels conda-forge
RUN conda config --add channels opendrift

# Install opendrift environment into base conda environment
COPY environment.yml .
RUN /opt/conda/bin/conda env update -n base -f environment.yml

# Cache cartopy maps
RUN /bin/bash -c "echo -e \"import cartopy\nfor s in ('c', 'l', 'i', 'h', 'f'): cartopy.io.shapereader.gshhs(s)\" | python"

# Cache landmask generation
RUN /bin/bash -c "echo -e \"import opendrift_landmask_data as old\nold.Landmask()\" | python"

# Install opendrift
ADD . /code
RUN pip install -e .

# Test installation
RUN /bin/bash -c "echo -e \"import opendrift\" | python"

# Copy farm files into container
WORKDIR /farms

COPY ["./farms/*", "./"]

# Copy Service Module code and YAML file into container
WORKDIR /usr/src/app

COPY ["SM-R1.py", "./"]
COPY ["R1.yaml", "./"]
COPY ["Pilot-8-seafloor-depth.nc", "./"]

# Create output directories
WORKDIR /usr/src/app/OUTPUT
WORKDIR /usr/src/app/OUTPUT/FLOATS
WORKDIR /usr/src/app/OUTPUT/HEAT
WORKDIR /usr/src/app

# Run Service Module code
ENTRYPOINT ["python", "/usr/src/app/SM-R1.py"]
