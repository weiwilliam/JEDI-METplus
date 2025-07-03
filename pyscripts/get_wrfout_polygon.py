#!/usr/bin/env python3
import sys
import netCDF4 as nc
import pandas as pd

wrffile = sys.argv[1]
latvar = sys.argv[2]
lonvar = sys.argv[3]

wrfout = './wrfout_d01_20240117_180000.nc'

ncd = nc.Dataset(wrffile, 'r')

lat = ncd.variables[latvar][:].data
lon = ncd.variables[lonvar][:].data

if lat.ndim==3:
   lat = lat[0,:,:]
   lon = lon[0,:,:]

latlist = []
lonlist = []
for outlat, outlon in zip(lat[0,:],lon[0,:]):
    latlist.append(outlat)
    lonlist.append(outlon)
for outlat, outlon in zip(lat[1:,-1],lon[1:,-1]):
    latlist.append(outlat)
    lonlist.append(outlon)
for outlat, outlon in zip(lat[-1,-2::-1],lon[-1,-2::-1]):
    latlist.append(outlat)
    lonlist.append(outlon)
for outlat, outlon in zip(lat[-2::-1,0],lon[-2::-1,0]):
    latlist.append(outlat)
    lonlist.append(outlon)

df = pd.DataFrame({'Lat':latlist,'Lon':lonlist})

df.to_csv('domain_polygon.csv',index=False)
