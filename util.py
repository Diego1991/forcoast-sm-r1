import cartopy
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
from geopy.distance import distance
import io
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from urllib.request import urlopen, Request

def image_spoof(self, tile):
    ''' This function reformats web requests from OSM for cartopy
    Heavily based on code by Joshua Hrisko at:
    https://makersportal.com/blog/2020/4/24/geographic-visualizations-in-python-with-cartopy'''

    url = self._image_url(tile)                # get the url of the street map API
    req = Request(url)                         # start request
    req.add_header('User-agent','Anaconda 3')  # add user agent to request
    fh = urlopen(req) 
    im_data = io.BytesIO(fh.read())            # get image
    fh.close()                                 # close url
    img = Image.open(im_data)                  # open image with PIL
    img = img.convert(self.desired_tile_form)  # set image format
    return img, self.tileextent(tile), 'lower' # reformat for cartopy  

def osm_image(x, y, data=None, style='satellite', notnorm=False):
    '''This function makes OpenStreetMap satellite or map image with circle and random points.
    Change np.random.seed() number to produce different (reproducable) random patterns of points.
    Also review 'scale' variable'''
  
    if style=='map': # MAP STYLE
        cimgt.OSM.get_image = image_spoof # reformat web request for street map spoofing
        img = cimgt.OSM() # spoofed, downloaded street map
    elif style =='satellite': # SATELLITE STYLE
        cimgt.QuadtreeTiles.get_image = image_spoof # reformat web request for street map spoofing
        img = cimgt.QuadtreeTiles() # spoofed, downloaded street map
    else:
        print('no valid style')
    
    # Get radius 
    x0, y0 = x.mean(), y.mean()
    cx = (x.min(), x.min(), x.max(), x.max())
    cy = (y.min(), y.max(), y.max(), y.min())
    radius = sum([distance((y0, x0), (y,x)).m for x, y in zip(cx, cy)])/4

    plt.close('all')
    # Open matplotlib figure
    fig = plt.figure(figsize=(10, 10)) 
    # Project using coordinate reference system (CRS) of street map
    ax = plt.axes(projection=img.crs) 
    data_crs = ccrs.PlateCarree()

    # Find appropriate scale
    scale = int(120/np.log(radius))
    scale = (scale<20) and scale or 19

    # Add OSM with zoom specification
    ax.add_image(img, int(scale)) 
    
    # Set grid lines
    gl = ax.gridlines(draw_labels=True, crs=data_crs,
                        color='k',lw=0.5)
    
    x, y = np.meshgrid(x, y)
    
    if data is not None:    
        ax.pcolor(x, y, data[0:-1, 0:-1], transform=ccrs.PlateCarree(), 
            cmap='YlOrRd', shading='flat')    
        # Set colorbar    
        m = plt.cm.ScalarMappable(cmap='YlOrRd')
        if notnorm:
            # This is for Local Exposure Time
            m.set_clim(0, np.nanmax(data))
            P = ax.get_position(); P = [P.x1 + .02, P.y0,  .03, P.height] 
            fig.colorbar(m, cax=fig.add_axes(P), label='hours')
        else:
            # This is for Heat Maps
            P = ax.get_position(); P = [P.x1 + .02, P.y0,  .03, P.height] 
            fig.colorbar(m, cax=fig.add_axes(P), label='')
    
    # Set axis limits        
    ax.set_extent( [x.min(), x.max(), y.min(), y.max()] ) 
    # Delete axes ticks on top and right
    gl.top_labels = False
    gl.right_labels = False
    # Format axes tick labels 
    gl.xformatter = cartopy.mpl.gridliner.LONGITUDE_FORMATTER
    gl.yformatter = cartopy.mpl.gridliner.LATITUDE_FORMATTER
    
    # Return figure and axes to be saved as .png file
    return fig, ax
