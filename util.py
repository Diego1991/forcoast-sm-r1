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

    x0, y0 = x.mean(), y.mean()
    cx = (x.min(), x.min(), x.max(), x.max())
    cy = (y.min(), y.max(), y.max(), y.min())
    radius = sum([distance((y0, x0), (y,x)).m for x, y in zip(cx, cy)])/4

    plt.close('all')
    fig = plt.figure(figsize=(10,10)) # open matplotlib figure
    ax = plt.axes(projection=img.crs) # project using coordinate reference system (CRS) of street map
    data_crs = ccrs.PlateCarree()

    scale = int(120/np.log(radius))
    scale = (scale<20) and scale or 19

    
    ax.add_image(img, int(scale)) # add OSM with zoom specification
    
    gl = ax.gridlines(draw_labels=True, crs=data_crs,
                        color='k',lw=0.5)
    if data is not None:
        # data = np.ma.masked_where(data==0, data)
        ax.contourf(x, y, data, transform=ccrs.PlateCarree(), cmap='YlOrRd')        
        m = plt.cm.ScalarMappable(cmap='YlOrRd')
        if notnorm:
            m.set_clim(0, np.nanmax(data))
            fig.colorbar(m, ax=ax, label='hours')
        else:
            fig.colorbar(m, ax=ax, label='')
    
        
    extent = [x.min(), x.max(), y.min(), y.max()]    
    ax.set_extent(extent) # set extents
    
    gl.top_labels = False
    gl.right_labels = False
    gl.xformatter = cartopy.mpl.gridliner.LONGITUDE_FORMATTER
    gl.yformatter = cartopy.mpl.gridliner.LATITUDE_FORMATTER

    return fig, ax

def save_image(root, fig, name, fmt, n):    
    try:
        if n:
            fig.savefig(f'{name}({n}){fmt}', dpi=300, bbox_inches='tight')
            return f'{name}({n}){fmt}'
        else:
            fig.savefig(f'{name}{fmt}', dpi=300, bbox_inches='tight')
            return f'{name}{fmt}'
    except OSError:
        n += 1; return save_image(root, fig, name, fmt, n)