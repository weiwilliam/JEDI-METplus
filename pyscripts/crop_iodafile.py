#!/usr/bin/env python3
import argparse
from datetime import datetime
import netCDF4 as nc
import numpy as np
import os

import pyiodaconv.ioda_conv_engines as iconv
from collections import defaultdict, OrderedDict
from pyiodaconv.orddicts import DefaultOrderedDict

def isinside(lat_arr, lon_arr, poly_file):
    import numpy as np
    import pandas as pd
    from shapely.geometry import Point, Polygon
    df = pd.read_csv(poly_file)
    minlat = np.floor(df['Lat'].min()).astype(np.int32) 
    maxlat = np.ceil(df['Lat'].max()).astype(np.int32)
    minlon = np.floor(df['Lon'].min()).astype(np.int32)
    maxlon = np.ceil(df['Lon'].max()).astype(np.int32)
    print(f'min/max lat, min/max lon: {minlat}/{maxlat}, {minlon}/{maxlon}')   

    polygon_coords = list(zip(df['Lat'].values, df['Lon'].values))
    # Create a shapely Polygon object
    polygon = Polygon(polygon_coords)
    out_mask = np.zeros_like(lat_arr, dtype=bool)
    near_mask = ((lat_arr > minlat) & (lat_arr < maxlat) &
                 (lon_arr > minlon) & (lon_arr < maxlon))

    for i, (plat, plon) in enumerate(zip(lat_arr, lon_arr)):
        if near_mask[i]:
            point = Point(plat, plon)
            out_mask[i] = polygon.contains(point)
    del(df)

    return out_mask

locationKeyList = [
    ("latitude", "float"),
    ("longitude", "float"),
    ("dateTime", "long")
]

AttrData = {}
VarDims = {}
DimDict = {}

metaDataName = iconv.MetaDataName()
obsValName = iconv.OvalName()
obsErrName = iconv.OerrName()
qcName = iconv.OqcName()

class cropioda(object):
    def __init__(self, filename, varname, polygon):
        self.file = filename
        self.var = varname
        self.polyfile = polygon
        self.varDict = defaultdict(lambda: defaultdict(dict))
        self.outdata = defaultdict(lambda: DefaultOrderedDict(OrderedDict))
        self.varAttrs = DefaultOrderedDict(lambda: DefaultOrderedDict(dict))
        self._read()

    def _read(self):

        iodavar = self.var
        self.varDict[iodavar]['valKey'] = iodavar, obsValName
        self.varDict[iodavar]['errKey'] = iodavar, obsErrName
        self.varDict[iodavar]['qcKey'] = iodavar, qcName

        ncd = nc.Dataset(self.file, 'r')

        for attr in ncd.ncattrs():
            if 'ioda' in attr:
                continue
            AttrData[attr] = getattr(ncd, attr)

        VarDims[iodavar] = list(ncd.groups['ObsValue'].variables[iodavar].dimensions)

        lat = ncd.groups[metaDataName].variables['latitude'][:].ravel()
        lon = ncd.groups[metaDataName].variables['longitude'][:].ravel()
        dt = ncd.groups[metaDataName].variables['dateTime'][:].ravel()
       
        mask = isinside(lat, lon, self.polyfile)
        #mask = ((lat > self.minlat) & (lat < self.maxlat) &
        #        (lon > self.minlon) & (lon < self.maxlon))

        if np.count_nonzero(mask)==0:
            raise Exception('no obs available in the target area')

        out_lats = lat[mask]
        out_lons = lon[mask]
        out_dts = dt[mask]

        for grp in ncd.groups.keys():
            if grp==metaDataName:
                continue
            print('Process group %s' % (grp))
            vars = ncd.groups[grp].variables[iodavar]
            for attr in vars.ncattrs():
                print('   Process attr %s = %s' %(attr, getattr(vars, attr)) ) 
                self.varAttrs[iodavar, grp][attr] = getattr(vars, attr)
 
        self.outdata[('latitude', metaDataName)] = np.array(out_lats, dtype=np.float32)
        self.outdata[('longitude', metaDataName)] = np.array(out_lons, dtype=np.float32)
        self.outdata[('dateTime', metaDataName)] = np.array(out_dts, dtype=np.int64)
        dt_units = getattr(ncd.groups[metaDataName].variables['dateTime'], 'units')
        self.varAttrs[('dateTime', metaDataName)]['units'] = dt_units

        obs = ncd.groups[obsValName].variables[iodavar][:].data
        err = ncd.groups[obsErrName].variables[iodavar][:].data
        qc = ncd.groups[qcName].variables[iodavar][:].data

        out_obs = obs[mask, :]
        out_err = err[mask, :]
        out_qc = qc[mask, :]

        self.outdata[self.varDict[iodavar]['valKey']] = np.array(out_obs.ravel(), dtype=np.float32)
        self.outdata[self.varDict[iodavar]['errKey']] = np.array(out_err.ravel(), dtype=np.float32)
        self.outdata[self.varDict[iodavar]['qcKey']] = np.array(out_qc.ravel(), dtype=np.int32)

        DimDict['Location'] = len(self.outdata[('latitude', metaDataName)])
        DimDict['Channel'] = ncd.variables['Channel'][:].data

def main():

    parser = argparse.ArgumentParser(
        description=('Read an IODA file and crop based on lat/lon')
    )
    parser.add_argument(
        '-i', '--input',
        help="path of input ioda file",
        type=str, required=True)
    parser.add_argument(
        '-o', '--output',
        help="name of output ioda file",
        type=str, required=True)
    parser.add_argument(
        '-v', '--variable',
        help="variable name to process",
        type=str, required=True)
    parser.add_argument(
        '-p', '--polygon',
        help="masking polygon file",
        type=str, required=True)

    args = parser.parse_args()

    # Read in the AOD data
    cropped = cropioda(args.input, args.variable, args.polygon)

    # write everything out
    writer = iconv.IodaWriter(args.output, locationKeyList, DimDict)
    writer.BuildIoda(cropped.outdata, VarDims, cropped.varAttrs, AttrData)

if __name__ == '__main__':
    main()    
