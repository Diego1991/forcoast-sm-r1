import argparse
from datetime import date, datetime, timedelta
from math import isnan
from matplotlib.path import Path
from netCDF4 import Dataset
import numpy as np
from opendrift.models.oceandrift import OceanDrift
from opendrift.readers import reader_netCDF_CF_generic, reader_global_landmask
from random import random, uniform
import re
import requests
from shapely.geometry import Polygon, Point
import xarray as xr
import yaml

def process_bedfile(file):
    ''' Get farming polygons from user's input file '''
    bed, BED, npoly = [], {}, 0
            
    with open(file, 'r') as infile:
        for line in infile:
            lst = line.split()
            x, y = float(lst[0]), float(lst[1])
            pair = [x, y]
            if any([isnan(i) for i in pair]):
                if len(bed) > 2:
                    npoly += 1
                    BED['bed_%09d' % npoly] = Path(bed)
                    bed = []; continue
            bed.append(pair)
        if len(bed) > 2:
           npoly += 1
           BED['bed_%09d' % npoly] = Path(bed)
           bed = []  
           
    return BED

def random_points_within(poly, num_points):
    ''' Get uniformly distributed random points within a farming area.
    These points will be used during seeding in OpenDrift '''
    min_x, min_y, max_x, max_y = poly.bounds

    points = []

    while len(points) < num_points:
        random_point = Point([uniform(min_x, max_x), 
            uniform(min_y, max_y)])
        if (random_point.within(poly)):
            points.append(random_point)

    return points         
 
def main():
    
    ''' Argument parser '''
    ap = argparse.ArgumentParser()
    ap.add_argument('-o', '--options',  
        help="options (YAML) file")
    ap.add_argument('-p', '--pilot',    
        help="Pilot number")
    ap.add_argument('-s', '--seed',     
        help="Seeding method: either 'area' or 'point'")
    ap.add_argument('-f', '--file',     
        help="Farming areas file, used only if 'area' seeding has been selected")
    ap.add_argument('-x', '--lon',      
        help="Seeding longitude, used only if 'point' seeding has been selected")
    ap.add_argument('-y', '--lat',      
        help="Seeding latitude, used only if 'point' seeding has been selected")
    ap.add_argument('-l', '--level',    
        help="Seeding level: either 'surface' or 'bottom'")
    ap.add_argument('-r', '--radius',   
        help="Uncertainty radius, used only if 'point' seeding has been selected")
    ap.add_argument('-t', '--time',
        help="Seeding time with format 'yyyy-mm-dd HH:MM:SS'")
    ap.add_argument('-u', '--uncertainty',
        help="Time uncertainty [h] before and after the selected time")
    ap.add_argument('-d', '--duration',
        help="Tracking time span [h]")
    ap.add_argument('-m', '--mode',     
        help="Tracking mode: either -1 (backward in time) or +1 (forward in time)")
     
    # Parse arguments from the command line
    argv = vars(ap.parse_args())
    
    optfile = argv['options'] 
    # Set name of default options file (YAML) if not specified through the command line
    if not optfile: optfile = 'R1.yaml'
    
    # Parse arguments from yaml file '''
    with open(optfile) as f:
        options = yaml.load(f, Loader=yaml.Loader) 
    
    # Replace with arguments from command line
    for key, val in zip(argv.keys(), argv.values()):
         if val: options[key] = val
    
    # Get starting and end dates for seeding as datetime objects
    time = datetime.strptime(options['time'], '%Y-%m-%d %H:%M:%S')
    uncertainty = float(options['uncertainty'])
    idate = time - timedelta(hours=uncertainty)
    edate = time + timedelta(hours=uncertainty)
     
    # Number of floats. This number largely determines the amount of 
    # computational effort required to run the particle-tracking
    # simulation. In a powerful server, I'd suggest to use 100,000.
    n = 1000    
    
    # If area seeding has been selected, process farming areas file.
    if options['seed'] == 'area': bed = process_bedfile(options['file'])                  
        
    # Set OpenDrift output NetCDF file name. This file is an ouput from this SM.
    file = r'./OUTPUT/FLOATS/FORCOAST-SM-R1-' + \
        datetime.now().strftime('%Y%m%d%H%M%S') + '.nc'      
    # Start Opendrift model instance
    Opendrift = OceanDrift(loglevel=20)   
    # Prevent floats from stranding and being removed from the run. In other
    # words, allow floats hitting the coastline to get back to the sea. 
    Opendrift.set_config('general:coastline_action', 'previous')
    # Add some diffusivity
    Opendrift.set_config('drift:horizontal_diffusivity', 0.5) 
    
    # Get seeding level (either surface of bottom)
    if options['level'] == 'bottom':
        levelstr, Z = 'bottom', 'seafloor'
    else:
        levelstr, Z = 'surface', 0
        
    # Pilot-specific code 
    if int(options['pilot']) == 1: # PORTUGAL
        raise ValueError('Service Module R1 not implemented for this Pilot yet')           
        
    elif int(options['pilot']) == 2: # SPAIN
        raise ValueError('Service Module R1 not implemented for this Pilot yet')
        
    elif int(options['pilot']) == 3: # BULGARIA
        raise ValueError('Service Module R1 not implemented for this Pilot yet')
        
    elif int(options['pilot']) == 4: # BELGIUM
        from erddapy.url_handling import urlopen                
        from pathlib import Path
        from urllib.parse import urlparse
        
        # Opendrift time step [s] - depends on model resolution
        dt = 600
        # Get high resolution landmask from GSHHG database
        landmask = reader_global_landmask.Reader(extent=[-4.5, 9.5, 48, 57.5])
        # Get present date    
        today = date.today()
        # Read from the Royal Belgian Institute of Natural Sciences ERDDAP Server 
        idate = '(' + (today - timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%SZ') + ')'            
        root = 'https://erddap.naturalsciences.be/erddap/griddap/NOS_HydroState_V1.nc?'
        url = root + levelstr + '_baroclinic_eastward_sea_water_velocity' + \
            '[' + idate + ':last][(48.5):1:(57.0)][(-4.0):1:(9.0)],' + \
                          levelstr + '_baroclinic_northward_sea_water_velocity' + \
             '[' + idate + ':last][(48.5):1:(57.0)][(-4.0):1:(9.0)]'
        data = urlopen(url=url)  
        nc = Dataset(Path(urlparse(url).path).name, memory=data.read())
        dataset = xr.open_dataset(xr.backends.NetCDF4DataStore(nc))
        dataset.variables['time'].attrs['units'] = 'seconds since 1970-01-01T00:00:00Z'
        # Generate reader for physics
        phys = reader_netCDF_CF_generic.Reader(dataset, name='NOS_HydroState',
            standard_name_mapping={levelstr + \
            '_baroclinic_eastward_sea_water_velocity': 'x_sea_water_velocity',
                                   levelstr + \
            '_baroclinic_northward_sea_water_velocity': 'y_sea_water_velocity'
                                   })
        # Add readers
        Opendrift.add_reader([landmask, phys])
        
        # Set domain limits to create heatmap (pollution density) grid
        minx, maxx, miny, maxy = -4, 9, 48.5, 57
    
    elif int(options['pilot']) == 5: # IRELAND   
        from opendrift.readers import reader_ROMS_native
        
        # Opendrift time step [s] - depends on model resolution
        dt = 60 
        # Read from ROMS Galway Bay 
        ocn = 'http://milas.marine.ie/thredds/dodsC/IMI_ROMS_HYDRO/GALWAY_BAY_NATIVE_70M_8L_1H/AGGREGATE'
        # Generate reader for physics 
        phys = reader_ROMS_native.Reader(ocn)  
        # Add readers          
        Opendrift.add_reader(phys)          
        # Use ROMS land/sea mask
        Opendrift.set_config('general:use_auto_landmask', False)
        
        # Set domain limits to create heatmap (pollution density) grid
        minx, maxx, miny, maxy = -9.2120, -8.8804, 53.1134, 53.2806
        
    elif int(options['pilot']) == 6: # DENMARK
        raise ValueError('Service Module R1 not implemented for this Pilot yet')
       
    elif int(options['pilot']) == 7: # ROMANIA
        raise ValueError('Service Module R1 not implemented for this Pilot yet')   
        
    elif int(options['pilot']) == 8: # ITALY
    
        # Opendrift time step [s] - depends on model resolution
        dt = 600        
        # Read from OGS         
        url = 'https://dsecho.inogs.it/thredds/catalog/pilot8/model_OGS/RFVL/'
        text = requests.get(url + 'catalog.html').text
        out = re.findall(r'20\d{2}\d{2}\d{2}', text)
        out = list(dict.fromkeys(out))
        fechas = [datetime.strptime(i, '%Y%m%d') for i in out]
        dates = max(fechas).strftime('%Y%m%d')
        text = requests.get(url + dates + '/catalog.html').text
        name = '_h-OGS--RFVL-MITgcmBFM-pilot8-b'
        suf = '_sm-v01.nc'
        out = re.findall(r'20\d{2}\d{2}\d{2}' + name + r'20\d{2}\d{2}\d{2}' + suf, text)
        sm = list(dict.fromkeys(out))
        suf = '_fc-v01.nc'
        out = re.findall(r'20\d{2}\d{2}\d{2}' + name + r'20\d{2}\d{2}\d{2}' + suf, text)
        fc = list(dict.fromkeys(out))
        ocn = sm + fc
        url = 'https://dsecho.inogs.it/thredds/dodsC/pilot8/model_OGS/RFVL/'
        ocn = [url + dates + '/'+ i for i in ocn]  
        
        # Get high resolution landmask from GSHHG database
        landmask = reader_global_landmask.Reader(extent=[12.2, 43.4, 16.1, 45.9]) 
        # Generate reader for bathymetry          
        bathy = reader_netCDF_CF_generic.Reader('Pilot-8-seafloor-depth.nc')
        # Generate reader for physics
        phys = reader_netCDF_CF_generic.Reader(ocn)      
        # Add readers                  
        Opendrift.add_reader([landmask, bathy, phys]) 
        
        # Set domain limits to create heatmap (pollution density) grid
        minx, maxx, miny, maxy = 12.2227, 16.0742, 43.4727, 45.8086
        
    else:
        raise ValueError('Service Module R1 not implemented for this Pilot yet')    
          
    # Seed elements 
    if options['seed'] == 'point': # point seeding
        Opendrift.seed_elements(lon=float(options['lon']),
                                lat=float(options['lat']),
                                z=Z,
                                number=n,
                                radius=float(options['radius']),
                                radius_type='uniform',
                                time=[idate, edate])                
    
    elif options['seed'] == 'area': # area seeding
        for i in bed.values():
            points = random_points_within(Polygon(i.vertices), n)
            for p in points:
                randomt = idate + timedelta(seconds=random()*(edate - idate). \
                    total_seconds())
                Opendrift.seed_elements(lon=p.x, lat=p.y, z=Z, time=randomt)                        
    
    else:
        raise ValueError("Seed must be either 'point' or 'area'")
    
    # Run OpenDrift
    Opendrift.run(duration=timedelta(hours=float(options['duration'])),
                  time_step= int(options['mode']) * dt,
                  time_step_output=timedelta(seconds=3600),
                  outfile=file,
                  export_variables=['time', 'lon', 'lat', 'z'])
    
    # Generate grid to calculate heatmaps (water pollution density    
    dh = .01 # Grid resolution
    # x-coordinate of grid
    x_grid = np.arange(minx, maxx + dh, dh)
    # y-coordinate of grid
    y_grid = np.arange(miny, maxy + dh, dh)
    
    # Read from OpenDrift output file
    with Dataset(file, 'r') as nc:
        LON = nc.variables['lon'][:]
        LAT = nc.variables['lat'][:]
        TIME = nc.variables['time'][:]
    
    # Compute heatmaps
    print('\n\nComputing density maps...')   
    HEAT = np.zeros((len(TIME), len(y_grid), len(x_grid)))
    for i, t in enumerate(TIME): 
        print('\n\t' + datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M'))           
        lon_t, lat_t = LON[:, i], LAT[:, i]
        for x, y in zip(lon_t, lat_t):
            index_x = np.argmax(x < x_grid) - 1
            index_y = np.argmax(y < y_grid) - 1
            HEAT[i, index_y, index_x] += 1
    # Save heatmaps into NetCDF. This file is the second output from this SM.
    file = r'./OUTPUT/HEAT/FORCOAST-SM-R1-' + \
        datetime.now().strftime('%Y%m%d%H%M%S') + '-HEAT.nc'  
    with Dataset(file, 'w', format='NETCDF4') as nc:
        # Create NetCDF dimensions
        nc.createDimension('lon', len(x_grid))
        nc.createDimension('lat', len(y_grid))
        nc.createDimension('time', len(TIME))                
        # Longitude
        lon = nc.createVariable('lon', 'f4', dimensions=('lon'))
        lon.standard_name = 'longitude'; lon.units = 'degree_east'
        lon[:] = x_grid
        # Latitude
        lat = nc.createVariable('lat', 'f4', dimensions=('lat'))
        lat.standard_name = 'latitude'; lat.units = 'degree_north'
        lat[:] = y_grid
        # Time
        tiempo = nc.createVariable('time', 'f8', dimensions=('time'))
        tiempo.standard_name = 'time'; tiempo.units = 'seconds since 1970-01-01'   
        tiempo[:] = TIME
        # Heat (number of floats per grid cell)
        heat = nc.createVariable('water_pollution', 'f4', 
            dimensions=('time', 'lat', 'lon'))
        heat.long_name = 'number of floats'; heat.units = 'dimensionless'
        heat[:] = HEAT
    
if __name__ == "__main__":
    main()    