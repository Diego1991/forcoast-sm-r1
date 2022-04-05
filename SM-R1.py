import argparse
import cartopy.crs as ccrs
from datetime import date, datetime, timedelta
from imageio import imread, mimsave
from math import isnan
import matplotlib
from matplotlib.path import Path
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import numpy as np
from opendrift.models.oceandrift import OceanDrift
from opendrift.readers import reader_netCDF_CF_generic, reader_shape
import os
from random import random, uniform
import re
import requests
from shapely.geometry import Polygon, Point
from shapely.geos import TopologicalError
import wget
import util
import xarray as xr
import yaml

font = {'size' : 18}; matplotlib.rc('font', **font)

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

def fixdate(date, times, tipo):
    if date > max(times):
        print(tipo + ' seeding time is after the latest available time step. Setting it equal to the latest available time step {}'.format(max(times)))
        date = max(times)
    elif date < min(times):
        print(tipo + ' seeding time is before the earliest available time step. Setting it equal to the earliest available time step {}'.format(min(times)))
        date = min(times)
    return date
 
def main():
    
    ''' Create output directories, if needed '''
    if not os.path.isdir('tmp'):
        os.mkdir('tmp')
    else:            
        tmp = [f for f in os.listdir('tmp') if f.endswith('.tmp')]
        for file in tmp:                
            os.remove(os.path.join('tmp', file))
    if not os.path.isdir('OUTPUT'):
        os.mkdir('OUTPUT')
        os.mkdir('OUTPUT/FLOATS')
        os.mkdir('OUTPUT/HEAT')
        os.mkdir('OUTPUT/BULLETIN')
    if not os.path.isdir('OUTPUT/FLOATS'):
        os.mkdir('OUTPUT/FLOATS')
    if not os.path.isdir('OUTPUT/HEAT'):
        os.mkdir('OUTPUT/HEAT')
    if not os.path.isdir('OUTPUT/BULLETIN'):
        os.mkdir('OUTPUT/BULLETIN')
    
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
        help="Seeding time with format 'yyyy-mm-ddTHH:MM:SS'")
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
    
    ''' Get starting and end dates for seeding as datetime objects '''
    time = datetime.strptime(options['time'], '%Y-%m-%dT%H:%M:%S')
    uncertainty = float(options['uncertainty'])
    idate = time - timedelta(hours=uncertainty)
    edate = time + timedelta(hours=uncertainty)
     
    # Number of floats. This number largely determines the amount of 
    # computational effort required to run the particle-tracking
    # simulation. In a powerful server, I'd suggest to use 100,000.
    n = 10000
    
    # If area seeding has been selected, process farming areas file.
    if options['seed'] == 'area': bed = process_bedfile(options['file'])                  
    
    ''' OpenDrift configuration '''    
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
    # Use prescribed land/sea mask
    Opendrift.set_config('general:use_auto_landmask', False)
    
    # Get seeding level (either surface of bottom)
    if options['level'] == 'bottom':
        levelstr, Z = 'bottom', 'seafloor'
    else:
        levelstr, Z = 'surface', 0
        
    ''' Pilot-specific code '''
    if int(options['pilot']) == 1: # PORTUGAL
        raise ValueError('Service Module R1 not implemented for this Pilot yet')           
        
    elif int(options['pilot']) == 2: # SPAIN
        
        Z = 0
                
        # Opendrift time step [s] - depends on model resolution
        dt = 600 
        
        ''' Read from EuskOOS '''        
        f = 'croco_original_exp.nc'
        # Set url to download from
        url = 'https://thredds.euskoos.eus/thredds/fileServer/testAll/' + f
        # Remove file from local filesystem if already exists. This
        # is to ensure that the latest available file is used.
        if os.path.exists('tmp/' + f):
            os.remove('tmp/' + f)
        # Download from EuskOOS       
        while True:
            try:
                ocn = wget.download(url, out = 'tmp/' + f); break
            except ConnectionResetError:
                pass    
        with Dataset(ocn, 'a') as nc:
            timenc = nc.variables['time']
            timenc.units = 'seconds since 2021-01-01 00:00:00'
        with Dataset(ocn, 'r') as nc:
            # Read longitude
            x = nc.variables['lon_rho'][:]
            # Read latitude
            y = nc.variables['lat_rho'][:]   
            # Read time
            times = nc.variables['time'][:]  
        # Time offset                                          
        offset = datetime(date.today().year, 1, 1)
        # Create time list
        times = [offset + timedelta(seconds=i) for i in times]                         
        # Generate reader for physics         
        from opendrift.readers import reader_ROMS_native
        ocean = reader_ROMS_native.Reader(ocn)  
        # Add readers          
        Opendrift.add_reader(ocean)          
        # Grid for heatmap calculation
        x_grid, y_grid = x[0, :], y[:, 0]
        
    elif int(options['pilot']) == 3: # BULGARIA
        raise ValueError('Service Module R1 not implemented for this Pilot yet')
        
    elif int(options['pilot']) == 4: # BELGIUM
    
        from erddapy.url_handling import urlopen                
        from pathlib import Path
        from urllib.parse import urlparse
        
        # Opendrift time step [s] - depends on model resolution
        dt = 600       
       
        ''' Read from North Sea '''
        today = date.today()
        # Read from last 30 days to latest forecast
        itime = '(' + (today - timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%SZ') + ')'        
        # Get url to ERDDAP
        root = 'https://erddap.naturalsciences.be/erddap/griddap/NOS_HydroState_V1.nc?'
        url = root + levelstr + '_baroclinic_eastward_sea_water_velocity' + \
            '[' + itime + ':last][(48.5):1:(57.0)][(-4.0):1:(9.0)],' + \
                     levelstr + '_baroclinic_northward_sea_water_velocity' + \
            '[' + itime + ':last][(48.5):1:(57.0)][(-4.0):1:(9.0)]'                  
        # Start request
        data = urlopen(url=url)  
        # Open as NetCDF dataset
        nc = Dataset(Path(urlparse(url).path).name, memory=data.read())
        # Open xarray dataset
        dataset = xr.open_dataset(xr.backends.NetCDF4DataStore(nc))
        # Add time units attribute
        dataset.variables['time'].attrs['units'] = 'seconds since 1970-01-01T00:00:00Z'

        # Generate reader for landmask
        mask = reader_shape.Reader.from_shpfiles('landmask.shp')
        # Generate reader for currents
        ocean = reader_netCDF_CF_generic.Reader(dataset, name='NOS_HydroState',
              standard_name_mapping={'surface_baroclinic_eastward_sea_water_velocity': 'x_sea_water_velocity',
                                     'surface_baroclinic_northward_sea_water_velocity': 'y_sea_water_velocity'
                                   })
        # Add reader to OpenDrift model instance
        Opendrift.add_reader([mask, ocean])     
        
        # Read longitude
        x_grid = nc.variables['longitude'][:]
        # Read latitude
        y_grid = nc.variables['latitude'][:]
        # Read time
        times = nc.variables['time'][:]
        # Time offset
        offset = datetime(1970, 1, 1)
        # Create time list
        times = [offset + timedelta(seconds=i) for i in times]
           
    elif int(options['pilot']) == 5: # IRELAND   
        
        # Opendrift time step [s] - depends on model resolution
        dt = 60 
        
        ''' Read from Galway Bay '''
        ocn = 'http://milas.marine.ie/thredds/dodsC/IMI_ROMS_HYDRO/GALWAY_BAY_NATIVE_70M_8L_1H/COMBINED_AGGREGATION'
        with Dataset(ocn, 'r') as nc:
            # Read longitude
            x = nc.variables['lon_rho'][:]
            # Read latitude
            y = nc.variables['lat_rho'][:]   
            # Read time
            times = nc.variables['ocean_time'][:]  
        # Time offset                                          
        offset = datetime(1968, 5, 23)
        # Create time list
        times = [offset + timedelta(seconds=i) for i in times]
        # Generate reader for physics 
        from opendrift.readers import reader_ROMS_native
        ocean = reader_ROMS_native.Reader(ocn)  
        # Add readers          
        Opendrift.add_reader(ocean)          
        # Grid for heatmap calculation
        x_grid, y_grid = x[0, :], y[:, 0]
        
    elif int(options['pilot']) == 6: # DENMARK
    
        # Opendrift time step [s]
        dt = 60 
        
        ''' Read from HBM-Limfjord '''
        from ftplib import FTP
        url = 'ftp.dmi.dk'
        ftp = FTP(url)
        # Enter login details
        ftp.login('forcoast', 'DGHMTSJ.kumvvhf')
        ftp.cwd('outgoing')
        files = sorted(ftp.nlst())
        ocn = 'tmp/' + files[-1]
        with open(ocn, 'wb') as nc:
            ftp.retrbinary('RETR ' + files[-1], nc.write)
        bathy = 'Pilot-6-seafloor-depth.nc'
        # Add bathymetry to file
        with Dataset(ocn, 'a') as nc, Dataset(bathy) as cdf:
            H = nc.createVariable('h', 'f8', dimensions=('lat', 'lon'))
            H.standard_name = 'sea_floor_depth_below_sea_level'
            H.units = 'meter'
            H[:] = cdf.variables['h'][:]                        
        with Dataset(ocn, 'r') as nc:
            # Read longitude
            x_grid = nc.variables['lon'][:]
            # Read latitude
            y_grid = nc.variables['lat'][:]  
            # Read time
            times = np.round(86400 * nc.variables['time'][:])
        # Time offset                                          
        offset = datetime(1900, 1, 1)
        # Create time list
        times = [offset + timedelta(seconds=i) for i in times]                          
        # Generate reader for physics        
        ocean = reader_netCDF_CF_generic.Reader(ocn)
        # Generate reader for landmask
        mask = reader_shape.Reader.from_shpfiles('landmask.shp')
        # Add readers
        Opendrift.add_reader([mask, ocean])
       
    elif int(options['pilot']) == 7: # ROMANIA
        raise ValueError('Service Module R1 not implemented for this Pilot yet')   
        
    elif int(options['pilot']) == 8: # ITALY
    
        # Opendrift time step [s] - depends on model resolution
        dt = 600     
        
        ''' Read from OGS '''
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
        with xr.open_mfdataset(ocn, chunks={'time': 1}, concat_dim='time',
            combine='by_coords', compat='override', decode_times=False,                                   
            data_vars='minimal', coords='minimal') as nc:
            # Read longitude
            x_grid = nc.variables['longitude'][:].data
            # Read latitude
            y_grid = nc.variables['latitude'][:].data
            # Read time
            times = nc.variables['time'][:].data            
        # Time offset
        offset = datetime(1970, 1, 1)            
        # Create time list
        times = [offset + timedelta(seconds=i) for i in times]
        # Generate reader for bathymetry          
        bathy = reader_netCDF_CF_generic.Reader('Pilot-8-seafloor-depth.nc')
        # Generate reader for physics
        ocean = reader_netCDF_CF_generic.Reader(ocn)   
        # Generate reader for landmask
        mask = reader_shape.Reader.from_shpfiles('landmask.shp')
        # Add readers                  
        Opendrift.add_reader([mask, bathy, ocean]) 
        
    else:
        raise ValueError('Service Module R1 not implemented for this Pilot yet')    
          
    ''' Seed elements '''
    idate, edate = fixdate(idate, times, 'Start'), fixdate(edate, times, 'End')    
    if options['seed'] == 'point': # point seeding
        lon, lat = float(options['lon']), float(options['lat'])
        # Check user-selected coordinates are within model boundaries
        if lon < x_grid.min() or lon > x_grid.max():
            raise ValueError('Selected coordinates are outside the valid domain.\n' + 
            f'Please enter a longitude between {x_grid.min()} and {x_grid.max()}')
        if lat < y_grid.min() or lat > y_grid.max():
            raise ValueError('Selected coordinates are outside the valid domain.\n' + 
            f'Please enter a latitude between {y_grid.min()} and {y_grid.max()}')
        Opendrift.seed_elements(lon=lon,
                                lat=lat,
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
                lon, lat = p.x, p.y
                # Check user-selected coordinates are within model boundaries
                if lon < x_grid.min() or lon > x_grid.max():
                    raise ValueError('Selected coordinates are outside the valid domain.\n' + 
                    f'Please enter a longitude between {x_grid.min()} and {x_grid.max()}')
                if lat < y_grid.min() or lat > y_grid.max():
                    raise ValueError('Selected coordinates are outside the valid domain.\n' + 
                    f'Please enter a latitude between {y_grid.min()} and {y_grid.max()}')
                Opendrift.seed_elements(lon=lon, lat=lat, z=Z, time=randomt)                        
    
    else:
        raise ValueError("Seed must be either 'point' or 'area'")
    
    ''' Get mode (either forward or backward in time) '''
    mode = [-1 if float(options['mode']) < 0 else 1][0]
    
    ''' Run OpenDrift '''
    if mode < 0:
        end_time = max(time - timedelta(hours=float(options['duration'])),
            ocean.start_time)
    else:                
        end_time = min(time + timedelta(hours=float(options['duration'])), 
            ocean.end_time)
    try:
        Opendrift.run(end_time=end_time,
                      time_step= mode * dt,
                      time_step_output=timedelta(seconds=3600),
                      outfile=file,
                      export_variables=['time', 'lon', 'lat', 'z'])
    except AttributeError as e:
        if str(e) == "'OceanDrift' object has no attribute 'environment'":
            print("Unable to run OpenDrift. This usually happens when there are "     + \
                  "no time steps to process (e.g. the last available time step "      + \
                  "has been selected together with a forward-in-time mode, or "       + \
                  "viceversa, the first time step together with a backward-in-time "  + \
                  "mode. Please check user's selections in the GUI, or YAML file if " + \
                  "the CLI version is being used. "); return
                        
    ''' Read from OpenDrift output file '''    
    with Dataset(file, 'r') as nc:        
        LON = nc.variables['lon'][:]
        LAT = nc.variables['lat'][:]        
        TIME = nc.variables['time'][:]
    
    ''' NEW SECTION TO ZOOM IN THE DRIFTING AREA '''
    # Define map boundaries based on trajectories bounding box
    minimum_longitude = LON.min() - 0.025
    maximum_longitude = LON.max() + 0.025
    minimum_latitude = LAT.min()  - 0.025
    maximum_latitude = LAT.max()  + 0.025
    
    # Create grid within the new boundaries
    x_grid = np.linspace(minimum_longitude, maximum_longitude, num=100)
    y_grid = np.linspace(minimum_latitude, maximum_latitude, num=100)

    ''' END OF NEW SECTION TO ZOOM IN THE DRIFTING AREA ''' 

    ''' Graphical output: floats '''  
    fig, ax = util.osm_image(x_grid, y_grid)  
    images = []
    if mode < 0:
        for i, t in reversed(list(enumerate(TIME))):        
            lon_t, lat_t = LON[:, i], LAT[:, i]
            floats = ax.plot(lon_t, lat_t, 'ko', mfc='red', ms=6,
                transform=ccrs.PlateCarree())
            fecha = datetime.fromtimestamp(t).strftime('%d-%b-%Y %H:%M')
            ax.set_title(fecha)
            print('   Saving floats figure for time ' + fecha)
            imagename = f'OUTPUT/FLOATS/F{fecha}.png'.replace('-', '').replace(':', '').replace(' ', '')
            plt.savefig(imagename, dpi=300, bbox_inches='tight')
            images.append(imread(imagename))
            line = floats.pop(0)
            line.remove()
    else:
        for i, t in enumerate(TIME):        
            lon_t, lat_t = LON[:, i], LAT[:, i]
            floats = ax.plot(lon_t, lat_t, 'ko', mfc='red', ms=6,
                transform=ccrs.PlateCarree())
            fecha = datetime.fromtimestamp(t).strftime('%d-%b-%Y %H:%M')
            ax.set_title(fecha)
            print('   Saving floats figure for time ' + fecha)
            imagename = f'OUTPUT/FLOATS/F{fecha}.png'.replace('-', '').replace(':', '').replace(' ', '')
            plt.savefig(imagename, dpi=300, bbox_inches='tight')
            images.append(imread(imagename))
            line = floats.pop(0)
            line.remove()
    mimsave('OUTPUT/FLOATS/F.gif', images, duration=.5)

    print(' ')
    ''' Graphical output: density maps '''
    HEAT = np.zeros((len(TIME), len(y_grid), len(x_grid)))
    images = []
    if mode < 0:
        for i, t in reversed(list(enumerate(TIME))):        
            # Get longitude and latitude of floats for the i-th time step
            lon_t, lat_t = LON[:, i], LAT[:, i]
            for x, y in zip(lon_t, lat_t):
                index_x = np.argmax(x < x_grid) - 1
                index_y = np.argmax(y < y_grid) - 1
                HEAT[i, index_y, index_x] += 1  
            # Processing i-th heat map
            heat = HEAT[i, :, :]
            # Mask where there are no floats to keep it transparent and 
            # show the underlying background satellite image beneath
            heat = np.ma.masked_where(heat == 0, heat)
            try:
                fig, ax = util.osm_image(x_grid, y_grid, data=heat)           
            except TopologicalError:
                continue
            # Add date and time as title
            fecha = datetime.fromtimestamp(t).strftime('%d-%b-%Y %H:%M')
            ax.set_title(fecha)
            # Save and close figure
            print('   Saving heatmap figure for time ' + fecha)
            imagename = f'OUTPUT/HEAT/H{fecha}.png'.replace('-', '').replace(':', '').replace(' ', '')
            plt.savefig(imagename, dpi=300, bbox_inches='tight')
            images.append(imread(imagename))
            plt.close(fig)
    else:
        for i, t in enumerate(TIME):        
            # Get longitude and latitude of floats for the i-th time step
            lon_t, lat_t = LON[:, i], LAT[:, i]
            for x, y in zip(lon_t, lat_t):
                index_x = np.argmax(x < x_grid) - 1
                index_y = np.argmax(y < y_grid) - 1
                HEAT[i, index_y, index_x] += 1  
            # Processing i-th heat map
            heat = HEAT[i, :, :]
            # Mask where there are no floats to keep it transparent and 
            # show the underlying background satellite image beneath
            heat = np.ma.masked_where(heat == 0, heat)
            try:
                fig, ax = util.osm_image(x_grid, y_grid, data=heat)           
            except TopologicalError:
                continue
            # Add date and time as title
            fecha = datetime.fromtimestamp(t).strftime('%d-%b-%Y %H:%M')
            ax.set_title(fecha)
            # Save and close figure
            print('   Saving heatmap figure for time ' + fecha)
            imagename = f'OUTPUT/HEAT/H{fecha}.png'.replace('-', '').replace(':', '').replace(' ', '')
            plt.savefig(imagename, dpi=300, bbox_inches='tight')
            images.append(imread(imagename))
            plt.close(fig)
    mimsave('OUTPUT/HEAT/H.gif', images, duration=.5)
        
    print(' ')
    ''' Calculate LET (Local Exposure Time; Du et al., 2020) '''
    cnt = np.zeros((len(y_grid), len(x_grid)))
    acm = np.zeros((len(y_grid), len(x_grid)))   
    Index_x, Index_y = -1, -1
    for i in range(n):
        lon_i, lat_i = LON[i, :], LAT[i, :]
        for x, y in zip(lon_i, lat_i):
            index_x = np.argmax(x < x_grid) - 1
            index_y = np.argmax(y < y_grid) - 1
            if (index_x != Index_x) or (index_y != Index_y):
                Index_x, Index_y = index_x, index_y
                cnt[Index_y, Index_x] += 1
            acm[Index_y, Index_x] += 1
    LET = np.divide(acm, cnt)  
    # Highlight only areas where LET is above 75% of maximum LET
    maxlet = np.nanmax(LET)
    # Get 75% of maximum LET
    minlet = .75 * maxlet
    # Find areas where LET is above 75% of maximum LET
    where = LET >= minlet
    # Create new figure
    fig, ax = util.osm_image(x_grid, y_grid)
    # Create grid
    [X_grid, Y_grid] = np.meshgrid(x_grid, y_grid)
    # Transpose to match LET array dimensions
    X_grid, Y_grid = X_grid.T, Y_grid.T    
    # Susset grid only where LET is above 75% of maximum LET
    xlet, ylet = X_grid[where], Y_grid[where]
    # Plot
    ax.plot(xlet, ylet, 'ko', mfc='red', ms=12, 
            transform=ccrs.PlateCarree())
    ax.set_title(f'Areas where Local Exposure Time longer than {minlet} hours')
    print('   Saving figure for Local Exposure Time')
    plt.savefig('OUTPUT/HEAT/LET.png', dpi=300, bbox_inches='tight')
    plt.close(fig)
                        
    ''' Save heatmaps and LET into NetCDF '''
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
        heat = nc.createVariable('float_count', 'f4', 
            dimensions=('time', 'lat', 'lon'))
        heat.long_name = 'number of floats'; heat.units = 'dimensionless'
        heat[:] = HEAT
        # LET
        let = nc.createVariable('LET', 'f4', dimensions=('lat', 'lon'))
        let.long_name = 'local exposure time'
        let[:] = LET
            
if __name__ == "__main__":
    main()
