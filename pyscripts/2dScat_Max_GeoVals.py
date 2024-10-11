#!/usr/bin/env python3
import os, sys
import argparse
from pathlib import Path
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cft
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

from plot_utils import set_size

proj = ccrs.PlateCarree()

# Area control
area_dict = {'minlat': -90.,
             'maxlat': 90.,
             'minlon': -180.,
             'maxlon': 180.,
             }
colorbar = {'cb_ori': 'vertical',
            'cb_frac': 0.025,
            'cb_pad': 0.04,
            'cb_asp': 32,
            }

image_spec = {'axe_w': 8,
              'axe_h': 5,
              'axe_l': 0.1,
              'axe_r': 0.9,
              'axe_b': 0.1,
              'axe_t': 0.9,
              'dpi': 300,
              'x': 'state',
              'y': 'level',
              }

states_name = {'mass_fraction_of_dust001_in_air':'du001',
               'mass_fraction_of_dust002_in_air':'du002',
               'mass_fraction_of_dust003_in_air':'du003',
               'mass_fraction_of_dust004_in_air':'du004',
               'mass_fraction_of_dust005_in_air':'du005',
               'mass_fraction_of_sea_salt001_in_air':'ss001',
               'mass_fraction_of_sea_salt002_in_air':'ss002',
               'mass_fraction_of_sea_salt003_in_air':'ss003',
               'mass_fraction_of_sea_salt004_in_air':'ss004',
               'mass_fraction_of_sea_salt005_in_air':'ss005',
               'mass_fraction_of_hydrophobic_black_carbon_in_air':'bc1',
               'mass_fraction_of_hydrophilic_black_carbon_in_air':'bc2',
               'mass_fraction_of_hydrophobic_organic_carbon_in_air':'oc1',
               'mass_fraction_of_hydrophilic_organic_carbon_in_air':'oc2',
               'mass_fraction_of_sulfate_in_air':'sulf',
               }

plot_conf = {'image_spec': image_spec,
             'area': area_dict,
             'states': states_name,
             'cb_spec': colorbar,
             }

class read_ioda(object):
    def __init__(self, in_dict, conf):
        self.iodafile = in_dict['iodafile']
        self.gvalfile = in_dict['gvalfile']

        print(self.iodafile)

        # area boundary
        minlon = conf['area']['minlon']
        maxlon = conf['area']['maxlon']
        minlat = conf['area']['minlat']
        maxlat = conf['area']['maxlat']

        dim_ds = xr.open_dataset(self.iodafile)
        channel = dim_ds.Channel.values.astype(np.int32)

        meta_ds = xr.open_dataset(self.iodafile,group='MetaData')
        lons = meta_ds.longitude.data
        lats = meta_ds.latitude.data
        area_mask = (lons<maxlon)&(lons>minlon)&(lats<maxlat)&(lats>minlat)
        lons_m = lons[area_mask]
        lats_m = lats[area_mask]

        data_dict = {}
        gv_ds = xr.open_dataset(self.gvalfile) 
        gv_ds = gv_ds.rename_dims({'nlocs':'Location'})
        gv_ds = gv_ds.sel(Location=area_mask==1)
        nlocs = gv_ds.Location.size
        tmpdim = '%s_nval' % (list(conf['states'].keys())[0])
        nlevs = gv_ds[tmpdim].size
        gv_data = np.zeros((nlocs, nlevs, len(conf['states'])), dtype='float32')
        for v in range(len(conf['states'])):
            gvname = list(conf['states'].keys())[v]
            gv_data[:, :, v] = gv_ds[gvname].values
            print('%i %s, max=%.3e, min=%.3e' %(v, gvname, gv_ds[gvname].values.max(), gv_ds[gvname].values.min() ))
        data_dict['geovals'] = (['Location', 'Level', 'States'], gv_data)
        data_dict['lon'] = (['Location'], lons_m)
        data_dict['lat'] = (['Location'], lats_m)

        states = []
        for var in conf['states'].keys():
            states.append(conf['states'][var])
 
        coords_dict = {'Location':range(nlocs), 'Level':range(nlevs), 'States':states}
    
        tmp_ds = xr.Dataset(data_dict, coords=coords_dict)
        self.plotdict = {'varname':'geovals',
                         'dataset':tmp_ds,
                         }

        dim_ds.close()
        meta_ds.close()

def plot_2dscat(input_dict, outpng, conf):
    varname = input_dict['varname']
    ds = input_dict['dataset']
   
    axe_w = conf['image_spec']['axe_w']
    axe_h = conf['image_spec']['axe_h']
    axe_l = conf['image_spec']['axe_l']
    axe_r = conf['image_spec']['axe_r']
    axe_b = conf['image_spec']['axe_b']
    axe_t = conf['image_spec']['axe_t']
    pdpi = conf['image_spec']['dpi']
    minlat, maxlat, minlon, maxlon = conf['area'].values()
    cb_ori, cb_frac, cb_pad, cb_asp = conf['cb_spec'].values()

    for var in ds.States.data:
        print(f'plotting max for {var}')
        tmpda = ds[varname].sel(States=var)
        tmpda = xr.where((tmpda < -1e+15), np.nan, tmpda)
        tmpda = tmpda.max(dim='Level',skipna=True)
        #print(tmpda)

        fig=plt.figure()
        ax=plt.subplot(projection=proj)
        set_size(axe_w, axe_h, l=axe_l, b=axe_b, r=axe_r, t=axe_t)
        ax.set_extent((minlon,maxlon,minlat,maxlat), crs=ccrs.PlateCarree())
        gl=ax.gridlines(draw_labels=True,dms=True,x_inline=False, y_inline=False)
        gl.right_labels=False
        gl.top_labels=False
        gl.xformatter=LongitudeFormatter(degree_symbol=u'\u00B0 ')
        gl.yformatter=LatitudeFormatter(degree_symbol=u'\u00B0 ')
        sc = ax.scatter(ds.lon.data, ds.lat.data, marker='s', c=tmpda.data, s=0.1,
                        # vmin=vmin, vmax=vmax,
                        transform=ccrs.PlateCarree())

        ax.add_feature(cft.BORDERS.with_scale('50m'), zorder=1)
        ax.coastlines(resolution='50m')

        cb_str = f'{var}'
        cb = plt.colorbar(sc,orientation=cb_ori,fraction=cb_frac,pad=cb_pad,aspect=cb_asp,label=cb_str)
        cb.ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0), useMathText=True)

        ax.set_title(input_dict['varname'],loc='left')

        pngfile = f'{outpng}_{var}.png'
        fig.savefig(pngfile,dpi=pdpi)
        plt.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description=('')
    )
    parser.add_argument(
        '-i', '--iodafile',
        help="path of ioda file",
        type=str, required=True)

    parser.add_argument(
        '-g', '--gvalfile',
        help="geovals file to be read",
        type=str, required=True)

    parser.add_argument(
        '-o', '--outpng',
        help="image name",
        type=str, required=True)

    args = parser.parse_args()
    
    in_dict = {'iodafile': args.iodafile,
               'gvalfile': args.gvalfile,
               }

    print(in_dict)

    pltvar = read_ioda(in_dict, plot_conf) 

    plot_2dscat(pltvar.plotdict, args.outpng, plot_conf)
