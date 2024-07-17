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

sdate = 2024060100
edate = 2024063018
vrfy_fhr = 6
vrfy_freq = 6
vrfy_product = 'TEMPO_no2_tropo_wrfchem' # 'tropomi_no2_tropo'
vrfy_stat = 'SL1L2'
unit_str = 'mol m$^{-2}$'

srcpath = os.path.join(os.path.dirname(__file__),'..')
stats_path = os.path.join(srcpath, 'output', vrfy_product, 'stats', 'f%.3i'%(vrfy_fhr))
plts_path = os.path.join(srcpath, 'output', vrfy_product, 'plots', 'f%.3i'%(vrfy_fhr))

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

    cdatefile = cdate.strftime('%Y%m%d%H.out')
    stats_file = os.path.join(stats_path, cdatefile)
    if not os.path.exists(stats_file):
        print(f'WARNING: Skip {cdatefile}, {stats_file} is not available')
        continue

    find_stats = False
    f = open(stats_file,'r')
    for line in f.readlines():
        if 'COL_NAME:' in line and col is None:
            col = line.split()[1:]
        if vrfy_stat in line:
            stats = line.split()[1:]
            find_stats = True
    f.close()
    if not find_stats:
        print(f'WARNING: Skip {cdatefile}, did not find stats: {vrfy_stat}')
        continue

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
        stat_df = outdf['FBAR'] - outdf['OBAR']
    elif stat=='RMSE':
        stat_df = np.sqrt(outdf['FFBAR'] + outdf['OOBAR'] - 2*outdf['FOBAR'])
    elif stat=='COUNT':
        stat_df = outdf['TOTAL']
    df[stat] = stat_df

ylbstr = '%s (%s)' %(stats_dict['FCST_VAR'][0],unit_str)

# Plot bias and RMSE
fig, ax = plt.subplots()
set_size(axe_w,axe_h,b=0.25,l=0.1,r=0.95,t=0.95)
ax.set_ylabel(ylbstr)
filter = (df['BIAS'].isna() & df['RMSE'].isna())
df[['BIAS','RMSE']].loc[~filter].plot.line(ax=ax, marker='*')
ax.grid()

plotname = 'BIAS_RMSE_%s.f%.3i.png' %(vrfy_product, vrfy_fhr)
outname = os.path.join(plts_path, plotname)
fig.savefig(outname,dpi=plot_quality)
plt.close()
 
# Plot HofX and ObsValue
fig, ax = plt.subplots()
set_size(axe_w,axe_h,b=0.25,l=0.1,r=0.95,t=0.95)
ax.set_ylabel(ylbstr)
outdf[['FBAR','OBAR']].plot.line(ax=ax, marker='*', color={'FBAR':'r', 'OBAR':'k'})
ax.grid()

plotname = 'F_O_%s.f%.3i.png' %(vrfy_product, vrfy_fhr)
outname = os.path.join(plts_path, plotname)
fig.savefig(outname,dpi=plot_quality)
plt.close()
