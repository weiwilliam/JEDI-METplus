#!/usr/bin/env python3
import os,sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from functions import get_dates, set_size, find_stats

# plotting adjustment
plot_quality = 300
axe_w = 8
axe_h = 3

sdate = 2024082200
edate = 2024083123
vrfy_fhr_beg = 35
vrfy_fhr_end = 46
vrfy_freq = 1
vrfy_product = 'tempo_no2_tropo_wrfchem'
vrfy_stat = 'SL1L2'
unit_str = 'mol m$^{-2}$'

vrfy_fhrs = list(range(vrfy_fhr_beg, vrfy_fhr_end+1))
vrfy_fhr_string = f'f{vrfy_fhr_beg}_to_f{vrfy_fhr_end}'

srcpath = os.path.join(os.path.dirname(__file__),'..')
plts_path = os.path.join(srcpath, 'output', vrfy_product, 'plots', 'f%.2i_to_f%.2i'%(vrfy_fhr_beg, vrfy_fhr_end))

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

    stats_exist = False
    for tmp_vrfy_fhr in vrfy_fhrs:
        stats_path = os.path.join(srcpath, 'output', vrfy_product, 'stats', 'f%.2i'%(tmp_vrfy_fhr))
        stats_file = os.path.join(stats_path, cdatefile)

        if not os.path.exists(stats_file):
            print(f'WARNING: Skip {cdatefile}, {stats_file} is not available')
            continue
    
        if not find_stats(stats_file):
            print(f'WARNING: Skip {cdatefile}, did not find stats: {vrfy_stat} from {tmp_vrfy_fhr}')
            continue
        else:
            stats_exist = True
            break

    if stats_exist:
        print(f'Processing {stats_file}')
        tmpdf = pd.read_csv(stats_file, skiprows=1, delim_whitespace=True)
        tmpdf['datetime'] = cdate
        
        if i==0:
            outdf = tmpdf
        else:
            outdf = pd.concat([outdf,tmpdf])
        i+=1 
print(outdf)

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
set_size(axe_w,axe_h,b=0.25,l=0.1,r=0.95,t=0.9)
ax.set_ylabel(ylbstr)
ax.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
filter = (df['BIAS'].isna() & df['RMSE'].isna())
df[['BIAS','RMSE']].loc[~filter].plot.line(ax=ax, marker='*', ls='')
meanbias = df['BIAS'].mean(skipna=True)
meanrmse = df['RMSE'].mean(skipna=True)
titlestr = 'BIAS Ave.= %.4e, RMSE Ave.= %.4e' %(meanbias, meanrmse)
ax.set_title(titlestr, loc='left')
ax.grid()

plotname = f'BIAS_RMSE_{vrfy_product}.{vrfy_fhr_string}.png'
outname = os.path.join(plts_path, plotname)
fig.savefig(outname,dpi=plot_quality)
plt.close()
 
# Plot HofX and ObsValue
fig, ax = plt.subplots()
set_size(axe_w,axe_h,b=0.25,l=0.1,r=0.95,t=0.9)
ax.set_ylabel(ylbstr)
ax.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
outdf[['FBAR','OBAR']].plot.line(ax=ax, marker='*', ls='', color={'FBAR':'r', 'OBAR':'k'})
meanfbar = outdf['FBAR'].mean(skipna=True)
meanobar = outdf['OBAR'].mean(skipna=True)
titlestr = 'FBAR Ave.= %.4e, OBAR Ave.= %.4e' %(meanfbar, meanobar)
ax.set_title(titlestr, loc='left')
ax.grid()

plotname = f'F_O_{vrfy_product}.{vrfy_fhr_string}.png'
outname = os.path.join(plts_path, plotname)
fig.savefig(outname,dpi=plot_quality)
plt.close()
