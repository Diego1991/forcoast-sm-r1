from datetime import date, datetime, timedelta
from math import isnan
from matplotlib.figure import Figure
from matplotlib.path import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from netCDF4 import Dataset
import numpy as np
import os
import queue
from random import random, uniform
import re
import requests
from shapely.geometry import Polygon, Point
import threading
from tkinter import filedialog
import tkinter as tk
import tkinter.ttk as ttk
import wget
import xarray as xr

class Root(tk.Tk):   
    
    def __init__(self):
        super(Root, self).__init__()
        self.queue = queue.Queue()
        
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
        if not os.path.isdir('OUTPUT/FLOATS'):
            os.mkdir('OUTPUT/FLOATS')
        if not os.path.isdir('OUTPUT/HEAT'):
            os.mkdir('OUTPUT/HEAT')
        
        ''' Get Pilot number '''
        with open('pilot.txt', 'r') as fid:
            Pilot = int(fid.readline())
            
        self.title('FORCOAST R1 - Retrieve Sources of Contaminants - Pilot ' + str(Pilot))
        if os.path.isfile('forcoast.ico'):
            self.wm_iconbitmap('forcoast.ico')         
        self.resizable(0, 0)
               
        # Number of floats
        self.n = 10000
        
        # Initialize plotting handles
        self.point, self.points, self.polybed = [], [], []
                    
        ''' Set Pilot-specific configuration '''
        if Pilot == 1: # PORTUGAL
            tk.messagebox.showerror(title='Wrong input', 
                message='Service Module not implemented in this Pilot yet')
            self.destroy(); return      
            
        elif Pilot == 2: # SPAIN
        
            # Opendrift time step [s]
            self.dt = 600
            
            ''' Download from EuskOOS '''
            
            f = 'croco_original_exp.nc'
            # Set url to download from
            url = 'https://thredds.euskoos.eus/thredds/fileServer/testAll/' + f
            # Remove file from local filesystem if already exists. This
            # is to ensure that the latest available file is used.
            if os.path.exists('tmp/' + f):
                os.remove('tmp/' + f)
            # Download from EuskOOS
            print('Downloading ' + url + '...')  
            while True:
                try:
                    self.ocn = wget.download(url, out = 'tmp/' + f); break
                except ConnectionResetError:
                    print('Error downloading file. Trying again...')
            self.ocn = 'tmp/' + f
            # Add time units attribute for OpenDrift to be able to read the time
            with Dataset(self.ocn, 'a') as nc:
                time = nc.variables['time']
                time.units = 'seconds since 2021-01-01 00:00:00'
            with Dataset(self.ocn, 'r') as nc:
                # Read longitude
                self.x = nc.variables['lon_rho'][:]
                # Read latitude
                self.y = nc.variables['lat_rho'][:]                
                # Read time
                time = nc.variables['time'][:]  
            # Time offset                                          
            offset = datetime(2021, 1, 1)
            # Create time list
            self.time = [offset + timedelta(seconds=i) for i in time]
                
            ''' Read coastline '''
            self.coast_x, self.coast_y = self.read_coast('coast2.dat')  
            
            self.x_grid, self.y_grid = self.x[0, :], self.y[:, 0]
            
        elif Pilot == 3: # BULGARIA
            tk.messagebox.showerror(title='Wrong input', 
                message='Service Module not implemented in this Pilot yet')
            self.destroy(); return
            
        elif Pilot == 4: # BELGIUM
            
            # OpenDrift time step [s] - related to model resolution
            self.dt = 600
            
            ''' Read from the Royal Belgian Institute of 
                Natural Sciences ERDDAP Server '''
                            
            # Get present date    
            today = date.today()
            # Read from thirty days before present 
            idate = '(' + (today - timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%SZ') + ')'
            
            from erddapy.url_handling import urlopen                
            from pathlib import Path
            from urllib.parse import urlparse
            
            self.ocn = 'https://erddap.naturalsciences.be/erddap/griddap/NOS_HydroState_V1.nc?' 
            url = self.ocn + 'longitude,latitude,time' + '[' + idate + ':last]'
            data = urlopen(url=url)              
            with Dataset(Path(urlparse(url).path).name, 
                         memory=data.read()) as nc:
                # Read longitude
                self.x = nc.variables['longitude'][:]
                # Read latitude
                self.y = nc.variables['latitude'][:]
                # Read time
                time = nc.variables['time'][:]
            # Time offset
            offset = datetime(1970, 1, 1)
            # Create time list
            self.time = [offset + timedelta(seconds=i) for i in time]
            
            ''' Read coastline '''
            self.coast_x, self.coast_y = self.read_coast('coast4.dat')       
            
            self.x_grid, self.y_grid = self.x, self.y
        
        elif Pilot == 5: # IRELAND       
           
            # Opendrift time step [s]
            self.dt = 60 
           
            ''' Read from ROMS Galway Bay '''

            self.ocn = 'http://milas.marine.ie/thredds/dodsC/IMI_ROMS_HYDRO/GALWAY_BAY_NATIVE_70M_8L_1H/AGGREGATE'
            with Dataset(self.ocn, 'r') as nc:
                # Read longitude
                self.x = nc.variables['lon_rho'][:]
                # Read latitude
                self.y = nc.variables['lat_rho'][:]                
                # Read time
                time = nc.variables['ocean_time'][:]  
            # Time offset                                          
            offset = datetime(1968, 5, 23)
            # Create time list
            self.time = [offset + timedelta(seconds=i) for i in time]
                
            ''' Read coastline '''
            self.coast_x, self.coast_y = self.read_coast('coast5.dat')  
            
            self.x_grid, self.y_grid = self.x[0, :], self.y[:, 0]
            
        elif Pilot == 6: # DENMARK
        
            # Opendrift time step [s]
            self.dt = 60 
            
            ''' Read from HBM-Limfjord '''
            from ftplib import FTP
            url = 'ftp.dmi.dk'
            ftp = FTP(url)
            # Enter login details
            ftp.login('forcoast', 'DGHMTSJ.kumvvhf')
            ftp.cwd('outgoing')
            files = sorted(ftp.nlst())
            self.ocn = 'tmp/' + files[-1]
            print('Downloading ' + files[-1] + '...')  
            with open(self.ocn, 'wb') as nc:
                ftp.retrbinary('RETR ' + files[-1], nc.write)
            bathy = 'Pilot-6-seafloor-depth.nc'
            # Add bathymetry to file
            with Dataset(self.ocn, 'a') as nc, Dataset(bathy) as cdf:
                H = nc.createVariable('h', 'f8', dimensions=('lat', 'lon'))
                H.standard_name = 'sea_floor_depth_below_sea_level'
                H.units = 'meter'
                H[:] = cdf.variables['h'][:]                            
            with Dataset(self.ocn, 'r') as nc:
                # Read longitude
                self.x = nc.variables['lon'][:]
                # Read latitude
                self.y = nc.variables['lat'][:]                
                # Read time
                time = np.round(86400 * nc.variables['time'][:])
            # Time offset                                          
            offset = datetime(1900, 1, 1)
            # Create time list
            self.time = [offset + timedelta(seconds=i) for i in time]
                
            ''' Read coastline '''
            self.coast_x, self.coast_y = self.read_coast('coast6.dat')     

            self.x_grid, self.y_grid = self.x, self.y             
           
        elif Pilot == 7: # ROMANIA        
            tk.messagebox.showerror(title='Wrong input', 
                message='Service Module not implemented in this Pilot yet')
            self.destroy(); return
        
        elif Pilot == 8: # ITALY
            
            # Opendrift time step [s]
            self.dt = 600
            
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
            self.ocn = [url + dates + '/'+ i for i in ocn]            
            with xr.open_mfdataset(self.ocn, chunks={'time': 1}, concat_dim='time',
                combine='by_coords', compat='override', decode_times=False,                                   
                data_vars='minimal', coords='minimal') as nc:
                # Read longitude
                self.x = nc.variables['longitude'][:].data
                # Read latitude
                self.y = nc.variables['latitude'][:].data
                # Read time
                time = nc.variables['time'][:].data            
            # Time offset
            offset = datetime(1970, 1, 1)            
            # Create time list
            self.time = [offset + timedelta(seconds=i) for i in time]
            
            ''' Read coastline '''
            self.coast_x, self.coast_y = self.read_coast('coast8.dat') 
            
            self.x_grid, self.y_grid = self.x, self.y            
                    
        else:
            tk.messagebox.showerror(title='Wrong input', message='Non-existent Pilot')
            self.destroy(); return
            
        # Get domain geographical boundaries
        self.minx, self.maxx = self.x.min(), self.x.max()
        self.miny, self.maxy = self.y.min(), self.y.max()
                            
        ''' User's input frame '''
        frame = tk.Frame(self)
        frame.grid(row=0, column=0, rowspan=2, sticky='W', padx=5)
        #
        f0 = tk.LabelFrame(frame, text='Source type')
        f0.grid(row=0, column=0, columnspan=2, sticky='WE', padx=5, pady=5)
        self.source = tk.IntVar(value=0)
        tk.Radiobutton(f0, text='Area',  variable=self.source, value=0, 
            command=self.switch_widgets).grid(row=0, column=0, padx=5, pady=5)
        tk.Radiobutton(f0, text='Point', variable=self.source, value=1, 
            command=self.switch_widgets).grid(row=0, column=1, padx=5, pady=5)            
        # 
        f1 = tk.LabelFrame(frame, text='Point selection')
        f1.grid(row=1, column=0, columnspan=2, sticky='WE', padx=5, pady=5)
        self.lonstr, self.latstr = tk.StringVar(value=''), tk.StringVar(value='')
        self.lonstr.trace_add('write', self.plot_point)
        self.latstr.trace_add('write', self.plot_point)
        tk.Label(f1, text='Longitude').grid(row=0, column=0, sticky='WE', padx=5, pady=5)
        self.lon = tk.Entry(f1, textvariable=self.lonstr, width=18, state='disabled')
        self.lon.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(f1, text='Latitude').grid(row=1, column=0, sticky='WE', padx=5, pady=5)
        self.lat = tk.Entry(f1, textvariable=self.latstr, width=18, state='disabled')
        self.lat.grid(row=1, column=1, padx=5, pady=5)
        #
        f2 = tk.LabelFrame(frame, text='Select radius (m)')
        f2.grid(row=2, column=0, columnspan=2, sticky='WE', padx=5, pady=5)
        self.radius = tk.Scale(f2, from_=0, to=10000, orient=tk.HORIZONTAL, length=180, state='disabled')
        self.radius.grid(row=0, column=0, sticky='WE', padx=5, pady=0)
        #
        f3 = tk.LabelFrame(frame, text='Select level')
        f3.grid(row=3, column=0, columnspan=2, sticky='WE', padx=5, pady=5)
        self.level = tk.IntVar(value=1)
        r1 = tk.Radiobutton(f3, text='Bottom',  variable=self.level, value=0)
        r1. grid(row=0, column=0, padx=5, pady=5)
        tk.Radiobutton(f3, text='Surface', variable=self.level, 
                       value=1).grid(row=0, column=1, padx=5, pady=5)   
        if Pilot == 2: r1.config(state='disabled')            
        #
        f4 = tk.LabelFrame(frame, text='Select date and time')
        f4.grid(row=4, column=0, columnspan=2, sticky='WE', padx=5, pady=5)
        self.dates = ttk.Combobox(f4, values=self.time, state='readonly', width=18)
        self.dates.current(len(self.time) - 1)
        self.dates.grid(row=0, column=0, sticky='W', padx=5, pady=5)           
        tk.Label(f4, text=u'\N{PLUS-MINUS SIGN}').grid(row=0, column=1, sticky='W')
        self.time_uncertainty = tk.Entry(f4, textvariable=tk.StringVar(value='0'), width=1)
        self.time_uncertainty.grid(row=0, column=2, sticky='W')
        tk.Label(f4, text='h').grid(row=0, column=3, sticky='W', padx=5)
        #
        f5 = tk.LabelFrame(frame, text='Enter duration')
        f5.grid(row=5, column=0, columnspan=2, sticky='WE', padx=5, pady=5)
        self.duration = tk.Entry(f5, textvariable=tk.StringVar(value='72'), width=5)
        self.duration.pack(side='left', padx=5, pady=5)
        tk.Label(f5, text='hours').pack(side='left')
        #
        self.mode = tk.IntVar(value=1)
        tk.Radiobutton(frame, text='Forward',  variable=self.mode, value=0). \
            grid(row=6, column=0, padx=5, pady=5)
        tk.Radiobutton(frame, text='Backward', variable=self.mode, value=1). \
            grid(row=6, column=1, padx=5, pady=5)    
        self.start_button = tk.Button(frame, text='Start', command=self.spawn_thread)
        self.start_button.grid(row=7, column=0, columnspan=2, padx=5, pady=5)
        
        ''' Oyster bed frame '''
        browse_frame = tk.LabelFrame(self, text='Area selection', padx=5)
        browse_frame.grid(row=0, column=1, sticky='WN', padx=17, pady=5)  
        # Select input file
        self.browse_entry = tk.Entry(browse_frame, width=40)
        self.browse_entry.grid(row=0, column=1, padx=5)       
        self.browse_button = tk.Button(browse_frame, text='Select file', command=self.fileDialog)
        self.browse_button.grid(row=0, column=0, padx=5, pady=4)
                    
        ''' Map frame '''
        area = tk.Frame(self)
        area.grid(row=1, column=1, rowspan=1, sticky='WEN', padx=5)
        self.fig, self.ax, self.canvas = self.plot_map(area)       
        self.sta = tk.PhotoImage(file='sta.png') 
        tk.Button(area, image=self.sta, command=self.show_start, 
            border=0).grid(row=1, column=0, padx=5, sticky='E') 
        self.bwd = tk.PhotoImage(file='bwd.png') 
        tk.Button(area, image=self.bwd, command=self.play_backward, 
            border=0).grid(row=1, column=1, padx=5, sticky='E')      
        self.fwd = tk.PhotoImage(file='fwd.png')
        tk.Button(area, image=self.fwd, command=self.play_forward,
            border=0).grid(row=1, column=2, padx=5, sticky='W') 
        self.emd = tk.PhotoImage(file='end.png') 
        tk.Button(area, image=self.emd, command=self.show_end,
            border=0).grid(row=1, column=3, padx=5, sticky='W') 
        
        ''' Display frame '''
        display_frame = tk.LabelFrame(self, text='Display', padx=5, pady=5)
        display_frame.grid(row=2, column=0, columnspan=2, sticky='WE', padx=5, pady=5)
        # Summary display
        self.summary_display = tk.Text(display_frame, height=10, width=65, padx=5, pady=5)
        self.summary_display.grid(row=0, column=0, padx=5, pady=0)    
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(display_frame, command=self.summary_display.yview)
        self.scrollbar.grid(row=0, column=1, sticky='nsew')
        self.summary_display['yscrollcommand'] = self.scrollbar.set   
        
    def fileDialog(self):
        ''' Open oyster bed selection file dialog '''
        file = filedialog.askopenfile(mode='r',
            filetypes=[('Text Documents', '*.txt')])      
        if file is None: 
            return  
        self.process_bedfile(file.name)
        self.plot_poly()    
           
        # Enter selected file name into entry 
        self.browse_entry.delete(first=0, last=1000)
        self.browse_entry.insert('end', file.name)     
        
    def play_backward(self):
        ''' Play backward '''
        if self.M:
            self.index += 1
        else:
            self.index -= 1
        self.index = min(len(self.TIME) - 1, max(0, self.index))
        self.ax.set_title(self.TIME[self.index].strftime('%d-%b-%Y %H:%M')) 
        self.plot_points(self.LON[:, self.index], self.LAT[:, self.index])
                    
    def play_forward(self):
        ''' Play forward '''
        if self.M:
            self.index -= 1
        else:
            self.index += 1
        self.index = min(len(self.TIME) - 1, max(0, self.index))
        self.ax.set_title(self.TIME[self.index].strftime('%d-%b-%Y %H:%M')) 
        self.plot_points(self.LON[:, self.index], self.LAT[:, self.index]) 
              
    def process_bedfile(self, file):
        ''' Get farming polygons from user's input file '''
        bed, self.BED, self.npoly = [], {}, 0
                
        with open(file, 'r') as infile:
            for line in infile:
                lst = line.split()
                x, y = float(lst[0]), float(lst[1])
                pair = [x, y]
                if any([isnan(i) for i in pair]):
                    if len(bed) > 2:
                        self.npoly += 1
                        self.BED['bed_%09d' % self.npoly] = Path(bed)
                        bed = []; continue
                bed.append(pair)
            if len(bed) > 2:
               self.npoly += 1
               self.BED['bed_%09d' % self.npoly] = Path(bed)
               bed = []                        
                
    def read_coast(self, coast):
        ''' Read coastline file '''
        coast_x, coast_y = [], []
        infile = open(coast, 'r')
        for line in infile:
            lst = line.split()
            coast_x.append(float(lst[0]))
            coast_y.append(float(lst[1]))
        infile.close() 
        return coast_x, coast_y                   
        
    def show_start(self):
        ''' Show starting positions '''
        if self.M:
            self.index = len(self.TIME) - 1
        else:
            self.index = 0
        self.ax.set_title(self.TIME[self.index].strftime('%d-%b-%Y %H:%M')) 
        self.plot_points(self.LON[:, self.index], self.LAT[:, self.index])  
      
    def show_end(self):
        ''' Show end positions '''
        if self.M:
            self.index = 0
        else:
            self.index = len(self.TIME) - 1
        self.ax.set_title(self.TIME[self.index].strftime('%d-%b-%Y %H:%M')) 
        self.plot_points(self.LON[:, self.index], self.LAT[:, self.index])  
               
    def spawn_thread(self):
        self.summary_display.delete('1.0', 'end')
        self.ax.set_title('')
        if len(self.points):
            self.points.pop(0).remove()         
        self.fig.canvas.draw()
        ''' Read user's inputs '''
        status, message = self.get_input()
        if status:
            tk.messagebox.showerror(title='Wrong input', message=message); return
            
        ''' Launch a separate thread to run OpenDrift '''
        self.start_button.config(state='disabled')
        self.thread = ThreadedClient(self.queue, self.ocn, self.seed, self.L,
            self.n, self.t, self.tunc, self.time, self.D, self.M, self.dt)        
        self.thread.start()
        self.periodic_call()
        
    def periodic_call(self):
        self.check_queue()
        if self.thread.is_alive():
            self.after(100, self.periodic_call)
        else:
            self.start_button.config(state='active')
            if not hasattr(self.thread, 'file'):
                self.summary_display.insert('end', 'ERROR: OpenDrift returned no file.\n')   
                self.summary_display.yview('end')
                self.update_idletasks()
                return
            # Read from file
            with Dataset(self.thread.file, 'r') as nc:
                self.LON = nc.variables['lon'][:]
                self.LAT = nc.variables['lat'][:]
                time = nc.variables['time'][:]
            self.TIME = [datetime(1970, 1, 1) + timedelta(seconds=i) for i in time]
            # Plot
            if self.M:
                self.index = len(self.TIME) - 1                
            else:
                self.index = 0                
            self.ax.set_title(self.TIME[self.index].strftime('%d-%b-%Y %H:%M')) 
            self.plot_points(self.LON[:, self.index], self.LAT[:, self.index]) 
            
            ''' Calculate heatmaps '''            
            self.HEAT = np.zeros((len(self.TIME), len(self.y_grid), len(self.x_grid)))
            for i, t in enumerate(self.TIME):                 
                lon_t, lat_t = self.LON[:, i], self.LAT[:, i]
                for x, y in zip(lon_t, lat_t):
                    index_x = np.argmax(x < self.x_grid) - 1
                    index_y = np.argmax(y < self.y_grid) - 1
                    self.HEAT[i, index_y, index_x] += 1            
                
            ''' Calculate LET (Local Exposure Time; Du et al., 2020) '''
            cnt = np.zeros((len(self.y_grid), len(self.x_grid)))
            acm = np.zeros((len(self.y_grid), len(self.x_grid)))   
            Index_x, Index_y = -1, -1
            for i in range(self.n):
                lon_i, lat_i = self.LON[i, :], self.LAT[i, :]
                for x, y in zip(lon_i, lat_i):
                    index_x = np.argmax(x < self.x_grid) - 1
                    index_y = np.argmax(y < self.y_grid) - 1
                    if (index_x != Index_x) or (index_y != Index_y):
                        Index_x, Index_y = index_x, index_y
                        cnt[Index_y, Index_x] += 1
                    acm[Index_y, Index_x] += 1
            self.LET = np.divide(acm, cnt)                
                
            ''' Save heatmaps and LET into NetCDF '''
            file = r'./OUTPUT/HEAT/FORCOAST-SM-R1-' + \
                datetime.now().strftime('%Y%m%d%H%M%S') + '-HEAT.nc'  
            with Dataset(file, 'w', format='NETCDF4') as nc:
                # Create NetCDF dimensions
                nc.createDimension('lon', len(self.x_grid))
                nc.createDimension('lat', len(self.y_grid))
                nc.createDimension('time', len(self.TIME))                
                # Longitude
                lon = nc.createVariable('lon', 'f4', dimensions=('lon'))
                lon.standard_name = 'longitude'; lon.units = 'degree_east'
                lon[:] = self.x_grid
                # Latitude
                lat = nc.createVariable('lat', 'f4', dimensions=('lat'))
                lat.standard_name = 'latitude'; lat.units = 'degree_north'
                lat[:] = self.y_grid
                # Time
                tiempo = nc.createVariable('time', 'f8', dimensions=('time'))
                tiempo.standard_name = 'time'; tiempo.units = 'seconds since 1970-01-01'   
                tiempo[:] = time
                # Heat (number of floats per grid cell)
                heat = nc.createVariable('float_count', 'f4', 
                    dimensions=('time', 'lat', 'lon'))
                heat.long_name = 'number of floats'; heat.units = 'dimensionless'
                heat[:] = self.HEAT
                # LET
                let = nc.createVariable('LET', 'f4', dimensions=('lat', 'lon'))
                let.long_name = 'local exposure time'
                let[:] = self.LET
        
    def check_queue(self):
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                self.summary_display.insert('end', msg)   
                self.summary_display.yview('end')
                self.update_idletasks()
            except queue.Queue.Empty:
                pass
        
    def draw_shore(self, ax, x, y):
        ''' Draw the coastline '''
        # Draw the coastline
        ax.plot(x, y, 'k-')        
        # Search for missing values
        w = np.isnan(x); w = [i for i, val in enumerate(w) if val]
        # Fill  coastal polygons
        for idx in range(len(w)-1):
            X = x[w[idx]+1:w[idx+1]]
            Y = y[w[idx]+1:w[idx+1]]
            ax.fill(X, Y, '.2')          
            
    def get_input(self):
        ''' Read user's inputs from GUI '''
        status, message = 0, ''
        
        if self.source.get(): # Point source
            try:
                x = float(self.lon.get())                                
            except ValueError:
                status = 1; message = 'Please, enter a proper longitude value.'
                return status, message            
            #
            try:
                y = float(self.lat.get())                                
            except ValueError:
                status = 1; message = 'Please, enter a proper latitude value.'
                return status, message
            #
            R = self.radius.get()
            
            self.seed = ('P', x, y, R)
            
        else: # Area source
            self.seed = ('A', self.BED)
        # 
        self.t = datetime.strptime(self.dates.get(), '%Y-%m-%d %H:%M:%S')  
        try:
            self.tunc = float(self.time_uncertainty.get())
        except ValueError:
            self.tunc = 0
        #
        try:
            self.D = float(self.duration.get())
        except ValueError:
            status = 1; message = 'Please, enter a proper duration value.'
            return status, message
        # 
        self.M = self.mode.get()
        self.L = self.level.get()
        
        return status, message
    
    def plot_map(self, frame):
        ''' Create canvas showing map in the specified tab '''        
        k = 5; fig = Figure(figsize=(k, k), facecolor=(.95, .95, .95), tight_layout=True)
        ax = fig.add_subplot(111)
        ax.set_xlim(left=self.minx, right=self.maxx); ax.get_xaxis().set_ticks([])
        ax.set_ylim(bottom=self.miny, top=self.maxy); ax.get_yaxis().set_ticks([])
        self.draw_shore(ax, self.coast_x, self.coast_y)              
        fig.canvas.draw()
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, frame)        
        canvas.get_tk_widget().grid(row=0, column=0, columnspan=4, sticky='WESN')               
        return fig, ax, canvas
    
    def plot_poly(self):
        ''' Plot oyster bed polygons '''        
        while self.polybed: self.polybed.pop(0).remove() 
        for i in self.BED.keys():
            poly = self.BED[i]
            x, y = zip(*[(X, Y) for X, Y in poly.vertices])
            x, y = list(x), list(y)
            x.append(x[0]); y.append(y[0])
            self.polybed.append(self.ax.plot(x, y, 'b')[0])
        self.fig.canvas.draw()
    
    def plot_point(self, *args):        
        ''' Draw user's selected coordinates on map '''        
        if self.point: self.point.pop(0).remove()             
        try:
            x = float(self.lon.get())             
            y = float(self.lat.get())            
        except ValueError:
            return                
        self.point = self.ax.plot(x, y, 'ko', mfc='green')       
        self.fig.canvas.draw()  

    def plot_points(self, lon, lat, *args):
        ''' Draw time-varying positions of floats '''
        if len(self.points):
            self.points.pop(0).remove()
        self.points = self.ax.plot(lon, lat, 'ko', mfc='red', ms=4)
        self.fig.canvas.draw()
        
    def switch_widgets(self):
        
        ''' Enable or disable widgets based on the source selection type,
                either area-selection or point-selection '''
                
        if self.source.get():
            
            # Activate point-selection widgets (longitue, latitude, radius)
            self.lon.configure(state='normal')
            self.lat.configure(state='normal')
            self.radius.configure(state='normal')                   
            
            # Disable area-selection widgets (open file dialog button and entry)
            self.browse_button.configure(state='disabled')
            self.browse_entry.configure(state='disabled')            
            
            # Update canvas            
            self.BED, self.npoly = {}, 0         
            while self.polybed: self.polybed.pop(0).remove() 
            self.fig.canvas.draw()  
            self.plot_point()   
            
            
        else:
            
            # Disable point-selection widgets (longitue, latitude, radius)
            self.lon.configure(state='disabled')
            self.lat.configure(state='disabled')
            self.radius.configure(state='disabled')
            
            # Activate area-selection widgets (open file dialog button and entry)
            self.browse_button.configure(state='active')
            self.browse_entry.configure(state='normal')
            
            # Update canvas
            if self.point: self.point.pop(0).remove()
            self.fig.canvas.draw()
            file = self.browse_entry.get()
            if file:
                self.process_bedfile(file)
                self.plot_poly()          
        
class ThreadedClient(threading.Thread):
    
    def __init__(self, queue, ocn, seed, level, n, t, tunc, times, D, M, dt):
        threading.Thread.__init__(self)
        self.queue = queue
        self.ocn = ocn
        self.seed = seed
        self.level = level
        self.n = n
        self.t, self.tunc, self.times = t, tunc, times
        self.D, self.M, self.dt = D, M, dt
        
    def fixdate(self, date, times):
        if date > max(times):
            date = max(times)
        elif date < min(times):
            date = min(times)
        return date
                
    def run(self):
        
        # Set seeding level (either surface or bottom)    
        if self.level:
            levelstr, Z = 'surface', 0
        else:
            levelstr, Z = 'bottom', 'seafloor'
            
        ''' Get Pilot number '''
        with open('pilot.txt', 'r') as fid:
            Pilot = int(fid.readline())
        
        from opendrift.models.oceandrift import OceanDrift        
        from opendrift.readers import reader_netCDF_CF_generic        
        from opendrift.readers import reader_shape
        
        # Start Opendrift model instance
        Opendrift = OceanDrift(logtext=self.queue, loglevel=20)  
        Opendrift.set_config('general:coastline_action', 'previous')
        Opendrift.set_config('general:use_auto_landmask', False)
        Opendrift.set_config('drift:horizontal_diffusivity', 0.5) 
                
        # Pilot-specific readers
        if Pilot == 2: # Spain            
            from opendrift.readers import reader_ROMS_native            
            ocean = reader_ROMS_native.Reader(self.ocn)            
            Opendrift.add_reader(ocean)                        
        
        elif Pilot == 4: # Belgium
                        
            # Get present date    
            today = date.today()
                        
            from erddapy.url_handling import urlopen                
            from pathlib import Path
            from urllib.parse import urlparse
            
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
            ocean = reader_netCDF_CF_generic.Reader(dataset, name='NOS_HydroState',
                standard_name_mapping={levelstr + \
                '_baroclinic_eastward_sea_water_velocity': 'x_sea_water_velocity',
                                       levelstr + \
                '_baroclinic_northward_sea_water_velocity': 'y_sea_water_velocity'
                                       })
            mask = reader_shape.Reader.from_shpfiles('landmask.shp')
            Opendrift.add_reader([mask, ocean])
            
        elif Pilot == 5: # Ireland        
            from opendrift.readers import reader_ROMS_native            
            ocean = reader_ROMS_native.Reader(self.ocn)            
            Opendrift.add_reader(ocean)  

        elif Pilot == 6: # Denmark
            ocean = reader_netCDF_CF_generic.Reader(self.ocn)
            mask = reader_shape.Reader.from_shpfiles('landmask.shp')
            Opendrift.add_reader([mask, ocean])

        elif Pilot == 8: # Italy        
            mask = reader_shape.Reader.from_shpfiles('landmask.shp')           
            bathy = reader_netCDF_CF_generic.Reader('Pilot-8-seafloor-depth.nc')
            ocean = reader_netCDF_CF_generic.Reader(self.ocn)                        
            Opendrift.add_reader([mask, bathy, ocean])  
                
        # Get time range for seeding based on time uncertainty
        idate = self.t - timedelta(hours=self.tunc)
        edate = self.t + timedelta(hours=self.tunc)
        
        # Seed elements 
        idate, edate = self.fixdate(idate, self.times), self.fixdate(edate, self.times)
        if self.seed[0] == 'P': # point seeding
            x, y, R = self.seed[1:]
            Opendrift.seed_elements(lon=x, lat=y, z=Z,
                number=self.n, radius=R, time=[idate, edate], radius_type='uniform')                
        else: # area seeding
            for i in self.seed[1].values():
                points = self.random_points_within(Polygon(i.vertices), self.n)
                for p in points:
                    randomt = idate + timedelta(seconds=random()*(edate - idate).total_seconds())
                    Opendrift.seed_elements(lon=p.x, lat=p.y, z=Z, time=randomt)                        
        
        # Opendrift output file name
        self.file = r'./OUTPUT/FLOATS/FORCOAST-SM-R1-' + \
            datetime.now().strftime('%Y%m%d%H%M%S') + '.nc' 
        # Run OpenDrift
        if self.M:
            end_time = max(self.t + (1 - 2 * self.M) * timedelta(hours=self.D),
                ocean.start_time)
        else:                
            end_time = min(self.t + (1 - 2 * self.M) * timedelta(hours=self.D), 
                ocean.end_time)
        try:
            Opendrift.run(end_time=end_time,            
                          time_step=(1 - 2 * self.M) * self.dt,
                          time_step_output=timedelta(seconds=3600),
                          outfile=self.file,
                          export_variables=['time', 'lon', 'lat', 'z'])
            return
        except AttributeError as e:
            if str(e) == "'OceanDrift' object has no attribute 'environment'":               
                msg = "Unable to run OpenDrift. This usually happens when there are " + \
                  "no time steps to process (e.g. the last available time step "      + \
                  "has been selected together with a forward-in-time mode, or "       + \
                  "viceversa, the first time step together with a backward-in-time "  + \
                  "mode. Please check user's selections in the GUI, or YAML file if " + \
                  "the CLI version is being used. "
                self.queue.put(msg);  delattr(self, 'file');  return                
        
    def random_points_within(self, poly, num_points):
        ''' Get random points uniformly distributed within a polygon '''
        min_x, min_y, max_x, max_y = poly.bounds
    
        points = []
    
        while len(points) < num_points:
            random_point = Point([uniform(min_x, max_x), 
                uniform(min_y, max_y)])
            if (random_point.within(poly)):
                points.append(random_point)
    
        return points         
        
if __name__ == '__main__':          
    root = Root()
    root.mainloop()                    