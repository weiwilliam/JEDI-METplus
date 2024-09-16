#!/usr/bin/env python3

import sys, os
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cft
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from functions import set_size, get_dates, set_area

# Plotting control
axe_w = 8; axe_h = 4; plot_quality = 300
# Level control
vmin = 0; vmax = 1.5 # vmax = 1.e-4
# Colorbar control
cb_ori = 'vertical'
cb_frac = 0.025
cb_pad = 0.04
cb_asp = 32

plot_max = 1
area = 'glb'
minlon, maxlon, minlat, maxlat = set_area(area)
variables = ['dust1', 'dust2', 'dust3', 'dust4', 'dust5',
             'seas1', 'seas2', 'seas3', 'seas4', 'seas5',
             'sulf', 'oc1', 'oc2', 'bc1', 'bc2',
             ]


if area == 'wxaq':
    proj = ccrs.LambertConformal(central_longitude=-97.0,
                                 central_latitude=39.0,
                                standard_parallels=[30.,60.])
if area == 'glb':
    proj = ccrs.PlateCarree()

infile = sys.argv[1]
outpng = sys.argv[2]

ds = xr.open_dataset(infile)

# delp = ds.dpres
# ugkg_kgm2 = 

if plot_max:

    for var in variables:
        print(f'plotting {var}')
        plot_data = ds[var].isel(time=0).max(dim='pfull')

        fig = plt.figure()
        ax = plt.subplot(projection=proj)
        set_size(axe_w,axe_h,l=0.1,b=0.1,r=0.9)
        ax.set_extent((minlon,maxlon,minlat,maxlat), crs=ccrs.PlateCarree())
        plot_data.plot.contourf(ax=ax, vmin=0, vmax=100, transform=proj,
                           cbar_kwargs={'orientation':cb_ori,'fraction':cb_frac,'pad':cb_pad,'aspect':cb_asp,'label':var})
 
        if area == 'glb':
            ax.coastlines(resolution='50m')

        title_str = f'{var} maximum'
        ax.set_title(title_str,loc='left')

        outname = f'{outpng}_{var}.png'
        fig.savefig(outname,dpi=plot_quality)
        plt.close()
