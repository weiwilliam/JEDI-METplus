#!/usr/bin/env python3
import os, platform
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import matplotlib.colors as mpcrs
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


def get_dates(sdate, edate, hint):
    """
      Create a series of Pandas datetime based on
        sdate: start date in YYYYMMDDHH
        edate: end date in YYYYMMDDHH
        hint: interval in hours
    """
    date1 = pd.to_datetime(sdate,format='%Y%m%d%H')
    date2 = pd.to_datetime(edate,format='%Y%m%d%H')
    delta = timedelta(hours=hint)
    dates = pd.date_range(start=date1, end=date2, freq=delta)
    return dates


def set_size(w,h, ax=None, l=None, r=None, t=None, b=None):
    """
      Control the axes location
        w, h: width, height in inches
        l, r, t, b: left, right, top, and bottom location between 0 to 1
    """
    if not ax: ax=plt.gca()
    if not l:
       l = ax.figure.subplotpars.left
    else:
       ax.figure.subplots_adjust(left=l)
    if not r:
       r = ax.figure.subplotpars.right
    else:
       ax.figure.subplots_adjust(right=r)
    if not t:
       t = ax.figure.subplotpars.top
    else:
       ax.figure.subplots_adjust(top=t)
    if not b:
       b = ax.figure.subplotpars.bottom
    else:
       ax.figure.subplots_adjust(bottom=b)
       
    figw = float(w)/(r-l)
    figh = float(h)/(t-b)
    ax.figure.set_size_inches(figw, figh)


def setupax_2dmap(cornerlatlon, proj, lbsize=20):
    """
    Setup fig, ax, and gl (gridlines) objects with 
      cornerlatlon: list in [minlat, maxlat, minlon, maxlon]
      proj: Cartopy projection
      lbsize: control the size of xlabel and ylabel
    """

    minlon = cornerlatlon[0]
    maxlon = cornerlatlon[1]
    minlat = cornerlatlon[2]
    maxlat = cornerlatlon[3]
    fig = plt.figure()
    ax = plt.subplot(projection=proj)
    ax.coastlines(resolution='110m')
    if maxlon - minlon == 360 and maxlat - minlat == 180:
        ax.set_global()
    else:
        ax.set_extent((minlon, maxlon, minlat, maxlat), crs=proj)
    gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    gl.right_labels = False
    gl.top_labels = False
    gl.xlabel_style = {'size':lbsize}
    gl.ylabel_style = {'size':lbsize}

    return fig, ax, gl


def setup_cmap(cmapname, idxlst):
    """
    Set colormap based on NCL colormaps files and index
      name: colormap file name
      idxlst: the list of color indice
    """
    rootpath = Path(__file__).parent
    nclcmap = str(rootpath.resolve())+'/../etc/colormaps'

    f = open(nclcmap + '/' + cmapname + '.rgb', 'r')
    a = []
    for line in f.readlines():
        if ('ncolors' in line):
            clnum = int(line.split('=')[1])
        a.append(line)
    f.close()
    # values = [x/(valuelst[-1]-valuelst[0]) for x in valuelst]
    b = a[-clnum:]
    c = []
    if 'MPL' in cmapname or 'GMT' in cmapname:
        for idx in idxlst:
            if (idx == 0):
                c.append(tuple(float(y) for y in [1, 1, 1]))
            elif (idx == 1):
                c.append(tuple(float(y) for y in [0, 0, 0]))
            elif (idx == -1):
                c.append(tuple(float(y) for y in [0.5, 0.5, 0.5]))
            else:
                c.append(tuple(float(y) for y in b[idx - 2].split('#', 1)[0].split()))
    else:
        for idx in idxlst:
            if (idx == 0):
                c.append(tuple(float(y)/255. for y in [255, 255, 255]))
            elif (idx == 1):
                c.append(tuple(float(y)/255. for y in [0, 0, 0]))
            elif (idx == -1):
                c.append(tuple(round(float(y)/255., 4) for y in [128, 128, 128]))
            else:
                c.append(tuple(round(float(y)/255., 4)
                               for y in b[idx - 2].split('#', 1)[0].split()))

    d = mpcrs.LinearSegmentedColormap.from_list(cmapname, c, len(idxlst))
    return c, d
