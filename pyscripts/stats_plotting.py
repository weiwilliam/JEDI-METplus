#!/usr/bin/env python3
import os,sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from functions import get_dates, set_size, find_stats

# plotting adjustment
plot_quality = 300
axe_w = 7
axe_h = 3

sdate = 2024082200
edate = 2024083123
vrfy_fhr_beg = 11
vrfy_fhr_end = 23
vrfy_freq = 1
vrfy_product = 'v.viirs-m_npp_gefs-aer'
vrfy_stat = 'SL1L2'
unit_str = '' # 'mol m$^{-2}$'

vrfy_fhrs = list(range(vrfy_fhr_beg, vrfy_fhr_end+1))

sys.exit()

srcpath = os.path.join(os.path.dirname(__file__),'..')
stats_path = os.path.join(srcpath, 'output', vrfy_product, 'stats', 'f%.2i'%(vrfy_fhr))
plts_path = os.path.join(srcpath, 'output', vrfy_product, 'plots', 'f%.2i'%(vrfy_fhr))

if not os.path.exists(stats_path):
    raise Exception(f'Stats of {stats_path} is not available')

if not os.path.exists(plts_path):
    os.makedirs(plts_path)

wrk_dates = get_dates(sdate, edate, vrfy_freq)

dfdata = {'datetime':wrk_dates}
df = pd.DataFrame(data=dfdata)
df.set_index('datetime',inplace=True)

col = None
stats_dict = {}
i = 0
for cdate in wrk_dates:
    cdatefile = cdate.strftime('%Y%m%d%H.out')
    stats_file = os.path.join(stats_path, cdatefile)
    print(f'Processing {stats_file}')
    if not os.path.exists(stats_file):
        print(f'WARNING: Skip {cdatefile}, {stats_file} is not available')
        continue

    if not find_stats(stats_file):
        print(f'WARNING: Skip {cdatefile}, did not find stats: {vrfy_stat}')
        continue
    
    tmpdf = pd.read_csv(stats_file, skiprows=1, delim_whitespace=True)


    tmpdf['datetime'] = cdate
    
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

ylbstr = '%s (%s)' %(outdf['FCST_VAR'][0],unit_str)

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
