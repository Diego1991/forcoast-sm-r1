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

# Install opendrift
ADD . /code
RUN pip install -e .

# Test installation
RUN /bin/bash -c "echo -e \"import opendrift\" | python"

# Install wget and erddapy
RUN pip install --user -r required.txt

# Add Service Module files
WORKDIR /usr/src/app
COPY ["SM-R1.py", "./"]
COPY ["R1.yaml", "./"]
COPY ["Pilot-*-seafloor-depth.nc", "./"]
COPY ["landmask.*", "./"]

# Replace OpenDrift's code with Service Module's code
COPY ["basemodel.py", "/code/opendrift/models/"]
COPY ["reader_netCDF_CF_generic.py", "/code/opendrift/readers/"]

ENTRYPOINT ["python", "/usr/src/app/SM-R1.py"]
