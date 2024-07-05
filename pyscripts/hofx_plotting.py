#!/usr/bin/env python3
import os
from pathlib import Path
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from functions import set_size

# Plotting control
axe_w = 4; axe_h = 4; plot_quality = 300
# Level control
vmin = 0; vmax = 1
# Colorbar control
cb_ori = 'vertical'
cb_frac = 0.025
cb_pad = 0.04
cb_asp = 32
# Area control
minlat = 40.2; maxlat = 45.;
minlon = -80.; maxlon = -71.5;

plot_date = 2024012118
plot_product = 'v.viirs-m_npp_wrfchem' # 'tropomi_no2_total'
unit_str = ' ' #'mol m$^{-2}$'
hofx_file = 'hofx_wxaq-VIIRS_NPP_%s.nc' %(plot_date)
# hofx_file = 'hofx_cropped_%s_%s.nc' %(plot_product,plot_date)

pltvar_mapdict = {'tropomi_no2_total':'nitrogendioxideTotal',
                  'tropomi_no2_tropo':'nitrogendioxideColumn',
                  'tropomi_co_total':'carbonmonoxideTotal',
                  'v.viirs-m_npp_wrfchem':'aerosolOpticalDepth',
                 }

plot_var = pltvar_mapdict[plot_product]

srcpath = os.path.join(os.path.dirname(__file__),'..')
hofx_path = os.path.join(srcpath,'output',plot_product,'hofx')
plts_path = os.path.join(srcpath,'output',plot_product,'plots','2dmap')

if not os.path.exists(hofx_path):
    raise Exception(f'HofX of {plot_product} is not available')

if not os.path.exists(plts_path):
    os.makedirs(plts_path)

in_hofx = os.path.join(hofx_path,hofx_file)

# Setup projection
proj = ccrs.LambertConformal(central_longitude=-97.0,
                             central_latitude=39.0,
                             standard_parallels=[30.,60.])

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
    ax.set_extent((minlon,maxlon,minlat,maxlat))
    ax.coastlines(resolution='110m')
    gl=ax.gridlines(draw_labels=True,dms=True,x_inline=False, y_inline=False)
    gl.right_labels=False
    gl.top_labels=False
    gl.xformatter=LongitudeFormatter(degree_symbol=u'\u00B0 ')
    gl.yformatter=LatitudeFormatter(degree_symbol=u'\u00B0 ')
    sc = ax.scatter(lons, lats, c=pltdata, s=0.8, vmin=vmin, vmax=vmax, 
                    transform=ccrs.PlateCarree())
    
    title_str = '%s at %s' %(plot_type,plot_date)
    cb_str = '%s (%s)' %(plot_var,unit_str)
    ax.set_title(title_str,loc='left')
    cb = plt.colorbar(sc,orientation=cb_ori,fraction=cb_frac,pad=cb_pad,aspect=cb_asp,label=cb_str)
    cb.ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0), useMathText=True)
    
    plotname = '%s_%s.%s.png' %(plot_type,plot_product,plot_date)
    outname = os.path.join(plts_path,plotname)
    fig.savefig(outname,dpi=plot_quality)
    plt.close()

