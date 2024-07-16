#!/usr/bin/env python3
import os
from pathlib import Path
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import cartopy.crs as ccrs
import cartopy.feature as cft
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from functions import set_size, get_dates

# Plotting control
axe_w = 4; axe_h = 4; plot_quality = 300
# Level control
vmin = 0; vmax = 1.e-4
# Colorbar control
cb_ori = 'vertical'
cb_frac = 0.025
cb_pad = 0.04
cb_asp = 32
# Area control
minlat = 39.8; maxlat = 46.;
minlon = -81.; maxlon = -70;

plot_product = 'TEMPO_no2_tropo_wrfchem' # 'tropomi_no2_total'
polygon_file = 'wxaq_polygon.csv'

vrfy_fhr = 6
sdate = 2024060100
edate = 2024063018
hint = 6
dates = get_dates(sdate, edate, hint)

# plot_date = 2024062818
unit_str = 'mol m$^{-2}$'
# hofx_file = 'hofx_cropped_%s_%s.nc' %(plot_product,plot_date)

pltvar_mapdict = {'tropomi_no2_total':'nitrogendioxideTotal',
                  'tropomi_no2_tropo':'nitrogendioxideColumn',
                  'tropomi_co_total':'carbonmonoxideTotal',
                  'v.viirs-m_npp_wrfchem':'aerosolOpticalDepth',
                 }

plot_var = 'nitrogendioxideColumn'

srcpath = os.path.join(os.path.dirname(__file__),'..')
hofx_path = os.path.join(srcpath, 'output', plot_product, 'hofx', 'f%.3i'%(vrfy_fhr))
plts_path = os.path.join(srcpath, 'output', plot_product, 'plots','f%.3i'%(vrfy_fhr), '2dmap')
poly_path = os.path.join(srcpath, 'etc/polygons', polygon_file)

if not os.path.exists(hofx_path):
    raise Exception(f'HofX folder of {plot_product} is not available')

if not os.path.exists(plts_path):
    os.makedirs(plts_path)

# Setup projection
proj = ccrs.LambertConformal(central_longitude=-97.0,
			     central_latitude=39.0,
			     standard_parallels=[30.,60.])

map_boundary = mpath.Path(pd.read_csv(poly_path)[['Lon','Lat']].to_numpy())


for cdate in dates:
  
    plot_date = cdate.strftime('%Y%m%d%H') 
    hofx_file = 'hofx_obs.tempo_no2_tropo-wxaq.%s.nc4' %(plot_date)
    in_hofx = os.path.join(hofx_path,hofx_file)
    if not os.path.exists(in_hofx):
        print(f'WARNING: Skip {plot_date}, {hofx_file} is not available')
        continue

    meta_ds = xr.open_dataset(in_hofx,group='MetaData')
    lons = meta_ds.longitude
    lats = meta_ds.latitude
    
    obsval_ds = xr.open_dataset(in_hofx,group='ObsValue')
    hofx_ds = xr.open_dataset(in_hofx,group='hofx')
    
    obsval = obsval_ds[plot_var]
    hofx = hofx_ds[plot_var]
    
    for plot_type in ['ObsValue','HofX']:
        if plot_type=='ObsValue':
            pltdata = obsval
        if plot_type=='HofX':
            pltdata = hofx
    
        fig=plt.figure()
        ax=plt.subplot(projection=proj)
        set_size(axe_w,axe_h,l=0.1,b=0.1,r=0.8)
        # ax.set_boundary(map_boundary, transform=ccrs.PlateCarree())
        ax.set_extent((minlon,maxlon,minlat,maxlat), crs=ccrs.PlateCarree())
        gl=ax.gridlines(draw_labels=True,dms=True,x_inline=False, y_inline=False)
        gl.right_labels=False
        gl.top_labels=False
        gl.xformatter=LongitudeFormatter(degree_symbol=u'\u00B0 ')
        gl.yformatter=LatitudeFormatter(degree_symbol=u'\u00B0 ')
        sc = ax.scatter(lons, lats, marker='s', c=pltdata, s=0.2, vmin=vmin, vmax=vmax, 
                        transform=ccrs.PlateCarree())

        ax.add_feature(cft.BORDERS.with_scale('50m'), zorder=1)
        ax.add_feature(cft.STATES.with_scale('50m'), zorder=1)
        ax.add_feature(cft.LAKES.with_scale('50m'), facecolor='None', edgecolor='k', zorder=0)
   
        title_str = '%s at %s' %(plot_type,plot_date)
        cb_str = '%s (%s)' %(plot_var,unit_str)
        ax.set_title(title_str,loc='left')
        cb = plt.colorbar(sc,orientation=cb_ori,fraction=cb_frac,pad=cb_pad,aspect=cb_asp,label=cb_str)
        cb.ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0), useMathText=True)
        
        plotname = '%s_%s.%s.png' %(plot_type,plot_product,plot_date)
        outname = os.path.join(plts_path,plotname)
        fig.savefig(outname,dpi=plot_quality)
        plt.close()

