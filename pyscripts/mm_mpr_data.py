#!/usr/bin/env python
# This code uses MELODIES-MONET to read in a .yaml file 
# and produces plots. For an interactive script see 
# jupyter notebooks in main directory.

from melodies_monet import driver
import os,sys
import dask
import xarray as xr
import pandas as pd

print(sys.argv)

argslen = len(sys.argv)
control_yaml = sys.argv[1]
fcstvar = sys.argv[2]
obsvar = sys.argv[3]
validtime = sys.argv[4]
leadtime = sys.argv[5]
fcstfile = sys.argv[6]
obsfile = sys.argv[7]

vldt = pd.to_datetime(validtime,format="%Y%m%d%H")
vld_str = vldt.strftime(format="%Y%m%d_%H%M%S")
vld_pdy = vldt.strftime(format="%Y%m%d")

an = driver.analysis()
# -- Update the yaml file below
an.control = control_yaml #'/glade/work/swei/Git/mmm/control_wrfchem_mech-0905_2.yaml'
an.read_control()

mpr_data = []

if os.path.exists(fcstfile) and os.path.exists(obsfile):
    # Replace the model and obs files
    an.control_dict['model']['wxaq']['files'] = fcstfile
    an.control_dict['obs']['airnow']['filename'] = obsfile
else:
    print('Files are not available')
    sys.exit()

modelname=list(an.control_dict['model'].keys())[0]
obsdict=an.control_dict['obs']
obsname=list(an.control_dict['obs'].keys())[0]
obstype=obsdict[obsname]['obs_type']
print(obstype)

# -- Lines below make a copy of the namelist in the plot directory for reference later
#cmd = 'cp ' + an.control + ' ' + an.control_dict['analysis']['output_dir']
#os.system(cmd)
dask.config.set(**{'array.slicing.split_large_chunks': True})
an.open_models()
an.open_obs()
an.pair_data()

crop_var_dict = {fcstvar,obsvar,'latitude','longitude','siteid'}

pairstr = '%s_%s' %(obsname,modelname)
pairds = an.paired[pairstr].obj
pairds_t = pairds[crop_var_dict].sel(time=vldt)
pairdf = pairds_t.to_dataframe()

pairdf['datetime'] = validtime
pairdf['fcstvar'] = fcstvar
pairdf['obsvar'] = obsvar
pairdf['obstype'] = obstype
pairdf['MPR'] = 'MPR'
pairdf['lead'] = leadtime
pairdf['na'] = 'NA'
pairdf['vx_mask'] = 'FULL,EAST'
pairdf.reset_index(inplace=True)

cols = ['na','na','lead','datetime','datetime','lead','datetime',
        'datetime','fcstvar','na','lead','obsvar','na','na',
        'obstype','vx_mask','na','lead','na','na','na','na','MPR',
        'na','na','siteid','latitude','longitude',
        'na','na',fcstvar,obsvar,
        'na','na','na']

pairdf = pairdf[cols]

print(pairdf)

mpr_data = mpr_data + [list( map(str,i) ) for i in pairdf.values.tolist() ]

print("Total Length:\t" + repr(len(mpr_data)))

