#!/usr/bin/env python3
import os
from pathlib import Path
import numpy as np
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import cartopy.crs as ccrs
import cartopy.feature as cft
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from functions import set_size, get_dates, set_area

# Plotting control
axe_w = 8; axe_h = 5; plot_quality = 300
# Level control
vmin = 0; vmax = 1.e-4
# Colorbar control
cb_ori = 'vertical'
cb_frac = 0.025
cb_pad = 0.04
cb_asp = 32
# Area control
area = 'wxaq'
minlon, maxlon, minlat, maxlat = set_area(area)
plotqc = -1

obs_name = 'obs.tempo_no2_tropo-wxaq'
plot_product = 'tempo_no2_tropo_wrfchem'
# JEDI variable name, var:channel 
plot_var = 'nitrogendioxideColumn'

vrfy_fhr_beg = 35
vrfy_fhr_end = 47
vrfy_fhrs = list(range(vrfy_fhr_beg, vrfy_fhr_end+1))
vrfy_fhr_string = f'f{vrfy_fhr_beg}_to_f{vrfy_fhr_end}'

sdate = 2024082211
edate = 2024083123
hint = 1
dates = get_dates(sdate, edate, hint)

unit_str = 'mol m$^{-2}$'

srcpath = os.path.join(os.path.dirname(__file__),'..')
plts_path = os.path.join(srcpath, 'output', plot_product, 'plots', vrfy_fhr_string, '2dmap')

if not os.path.exists(plts_path):
    os.makedirs(plts_path)

# Setup projection
if area == 'wxaq':
    proj = ccrs.LambertConformal(central_longitude=-97.0,
                                 central_latitude=39.0,
                                standard_parallels=[30.,60.])
if area == 'glb':
    proj = ccrs.PlateCarree()

for cdate in dates:
    plot_date = cdate.strftime('%Y%m%d%H') 
    hofx_file = f'hofx_{obs_name}.{plot_date}.nc4'

    hofx_exists = False
    for tmp_vrfy_fhr in vrfy_fhrs:
        hofx_path = os.path.join(srcpath, 'output', plot_product, 'hofx', 'f%.2i'%(tmp_vrfy_fhr))
        in_hofx = os.path.join(hofx_path,hofx_file)
        if not os.path.exists(in_hofx):
            print(f'WARNING: Skip {plot_date}, {hofx_file} from f{tmp_vrfy_fhr} is not available')
            continue
        else:
            print(f'Processing: {in_hofx}')
            hofx_exists = True
            break

    if not hofx_exists:
        continue

    raw_ds = xr.open_dataset(in_hofx)
    meta_ds = xr.open_dataset(in_hofx,group='MetaData')
    lons = meta_ds.longitude
    lats = meta_ds.latitude
    
    obsval_ds = xr.open_dataset(in_hofx,group='ObsValue')
    hofx_ds = xr.open_dataset(in_hofx,group='hofx')
    preqc_ds = xr.open_dataset(in_hofx,group='PreQC')
   
    if ':' in plot_var:
        obsval_ds = obsval_ds.assign_coords(Channel=raw_ds.Channel)
        hofx_ds = hofx_ds.assign_coords(Channel=raw_ds.Channel)
        preqc_ds = preqc_ds.assign_coords(Channel=raw_ds.Channel)
        plot_ch = int(plot_var[plot_var.index(':') + 1:])
        varname = plot_var[:plot_var.index(':')]
        obsval = obsval_ds[varname].sel(Channel=plot_ch)
        hofx = hofx_ds[varname].sel(Channel=plot_ch)
        qc = preqc_ds[varname].sel(Channel=plot_ch)
    else:
        varname = plot_var
        obsval = obsval_ds[varname]
        hofx = hofx_ds[varname]
        qc = preqc_ds[varname]

    if plotqc != -1:
        pltmsk = qc == plotqc
    else:
        pltmsk = ~np.isnan(lons)
    cnts = np.count_nonzero(pltmsk)
    
    for plot_type in ['ObsValue','HofX']:
        if plot_type=='ObsValue':
            pltdata = obsval
        if plot_type=='HofX':
            pltdata = hofx
    
        fig=plt.figure()
        ax=plt.subplot(projection=proj)
        set_size(axe_w,axe_h,l=0.1,b=0.1,r=0.9)
        ax.set_extent((minlon,maxlon,minlat,maxlat), crs=ccrs.PlateCarree())
        gl=ax.gridlines(draw_labels=True,dms=True,x_inline=False, y_inline=False)
        gl.right_labels=False
        gl.top_labels=False
        gl.xformatter=LongitudeFormatter(degree_symbol=u'\u00B0 ')
        gl.yformatter=LatitudeFormatter(degree_symbol=u'\u00B0 ')
        sc = ax.scatter(lons[pltmsk], lats[pltmsk], marker='s', c=pltdata[pltmsk], s=0.8,
                        vmin=vmin, vmax=vmax, transform=ccrs.PlateCarree())

        ax.add_feature(cft.BORDERS.with_scale('50m'), zorder=1)
        if area == 'glb':
            ax.coastlines(resolution='50m')
        if area == 'wxaq':
            ax.add_feature(cft.STATES.with_scale('50m'), zorder=1)
            ax.add_feature(cft.LAKES.with_scale('50m'), facecolor='None', edgecolor='k', zorder=0)
   
        title_str = f'{plot_type} at {plot_date} size: {cnts}'
        cb_str = f'{plot_var} ({unit_str})'
        ax.set_title(title_str,loc='left')
        cb = plt.colorbar(sc,orientation=cb_ori,fraction=cb_frac,pad=cb_pad,aspect=cb_asp,label=cb_str)
        cb.ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0), useMathText=True)
        
        if ':' in plot_var:
            plotname = f'{plot_type}_{varname}_ch{plot_ch}.{plot_date}.f{tmp_vrfy_fhr}.png'
        else:
            plotname = f'{plot_type}_{varname}.{plot_date}.f{tmp_vrfy_fhr}.png'
        outname = os.path.join(plts_path,plotname)
        fig.savefig(outname,dpi=plot_quality)
        plt.close()

