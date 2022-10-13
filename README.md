This is "FORCOAST-SM-R1: Retrieve Sources of Contaminants" Repository.

This code is entirely written in Python and it is currently implemented
for Pilots 4 (Belgium), 5 (Ireland) and 8 (Italy). The code is available
in two different versions: the CLI version and the GUI version.

The GUI version is in the GUI folder and there is more information about
it in the README document inside. The CLI version includes the following 
files: (a) SM-R1.py is the Python code, which acccepts arguments from 
the command line; these arguments are all listed in the (b) R1.yaml file.
Enter "python SM-R1.py -h" for a description of the available arguments.
In addition, in order to run the code in the Adriatic Sea, a bathymetry
file (c) Pilot-8-seafloor-depth.nc is also supplied.

The code is based on the OpenDrift (https://opendrift.github.io/) particle-
tracking model. Contaminants are assumed to be perfect passive tracers. 
The procedure consists of entering a number of numerical drifters into the
model domain and track its motion. There are two ways available to the user
for seeding numerical drifters: either (1) "point" seeding and (2) "area"
seeding. 

"Point" seeding consists of selecting latitude and longitude coordinates and
a uniform radius of dispersion around the selected location to add for some
uncertainty.

"Area" seeding consists of entering farming areas or polygons from a file. 
Then, numerical drifters are seeded following a random uniform distribution
inside these areas. Farming files should be plain text files and a very
simple example is provided at the "farms" folder. 

Other options available to the user are the seeding time, the seeding level
(either surface or bottom) and whether the model should run forward or 
backward in time. The backward capability is oriented towards retrieving 
the origin of the contamination detected in a farm, following the definition
of this Service Module.

There are currently two outputs from this Service Module, both are NetCDF
files. First file is the immediate output from the OpenDrift module: a 
NetCDF file showing the path followed by the numerical drifters. However,
quite often this is not enough information to the user, since it is not 
easy to appreciate where there is a higher concentration of pollution.
For this reason, there is a post-processing step in which a concentration
of pollution is determined by counting the number of numerical floats at
each grid cell for every time step. This information can be used to 
display heatmaps of water pollution. 

Licensed under GPL2.0
