#!/usr/bin/env python3
import os,sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from functions import get_dates, set_size

# plotting adjustment
plot_quality = 300
axe_w = 7
axe_h = 3

sdate = 2024011718
edate = 2024012318
vrfy_freq = 24
vrfy_product = 'v.viirs-m_npp_wrfchem' # 'tropomi_no2_tropo'
vrfy_stat = 'SL1L2'
unit_str = '' # 'mol m$^{-2}$'

srcpath = os.path.join(os.path.dirname(__file__),'..')
stats_path = os.path.join(srcpath,'output',vrfy_product,'stats')
plts_path = os.path.join(srcpath,'output',vrfy_product,'plots')

if not os.path.exists(stats_path):
    raise Exception('Stats of '+vrfy_product+' is not available')

if not os.path.exists(plts_path):
    os.makedirs(plts_path)

wrk_dates = get_dates(sdate,edate,vrfy_freq)

dfdata = {'datetime':wrk_dates}
df = pd.DataFrame(data=dfdata)
df.set_index('datetime',inplace=True)

col = None
stats_dict = {}
i = 0
for cdate in wrk_dates:
    stats_file = os.path.join(stats_path,cdate.strftime('%Y%m%d%H.out'))
    if not os.path.exists(stats_file):
        continue

    f = open(stats_file,'r')
    for line in f.readlines():
        if 'COL_NAME:' in line and col is None:
            col = line.split()[1:]
        if vrfy_stat in line:
            stats = line.split()[1:]
    f.close()

    stats_dict['datetime'] = cdate
    for icol in range(len(col)):
        if col[icol]=='FCST_VAR':
            stats_dict[col[icol]] = [stats[icol]]
        elif col[icol]=='TOTAL':
            stats_dict[col[icol]] = [int(stats[icol])]
        else:
            stats_dict[col[icol]] = [float(stats[icol])]

    tmpdf = pd.DataFrame(stats_dict)

    if i==0:
        outdf = tmpdf
    else:
        outdf = pd.concat([outdf,tmpdf])
    i+=1 

outdf = outdf.set_index('datetime')
for stat in ['COUNT','BIAS','RMSE']:
    if stat=='BIAS':
        stat_df = outdf['FOBAR']
    elif stat=='RMSE':
        stat_df = np.sqrt(outdf['FFBAR'] + outdf['OOBAR'] - 2*outdf['FOBAR'])
    elif stat=='COUNT':
        stat_df = outdf['TOTAL']
    df[stat] = stat_df

ylbstr = '%s (%s)' %(stats_dict['FCST_VAR'][0],unit_str)
fig, ax = plt.subplots()
set_size(axe_w,axe_h,b=0.2,l=0.15,r=0.95,t=0.95)
ax.set_ylabel(ylbstr)
df[['BIAS','RMSE']].plot(ax=ax,marker='*')
ax.grid()

plotname = '%s.png' %(vrfy_product)
outname = os.path.join(plts_path,plotname)
fig.savefig(outname,dpi=plot_quality)
plt.close()
 

