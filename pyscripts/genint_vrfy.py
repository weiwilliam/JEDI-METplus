#!/usr/bin/env python3
import sys
import os
import shutil
import pandas as pd
import yaml 
import subprocess
sys.path.insert(0, os.environ['metplus_ROOT'])
import produtil.setup
from datetime import datetime, timedelta
from metplus.util import metplus_check
from metplus.util import pre_run_setup, run_metplus, post_run_cleanup
from metplus import __version__ as metplus_version
from functions import run_job,check_job

sdate = 2024012000
edate = 2024012000
hint = 6
srcpath = '/work2/noaa/jcsda/shihwei/git/JEDI-METplus' #will replaced by path or file attributes.
wrkpath = os.path.join(srcpath,'workdir')

genint_build = '/work2/noaa/jcsda/shihwei/git/builds/genint'
crtm_coeff = os.path.join(genint_build,'test_data/crtm/3.1.0_skylab_7.0')

# paths for model and observations
model_path = '/work2/noaa/jcsda/shihwei/git/genint-bundle/genint/test/Data/background'
# /work2/noaa/jcsda/maryamao/garage/compare_exp/4denvar_an
obs_path = '/work2/noaa/jcsda/shihwei/git/genint-bundle/genint/test/Data/observation'
# obs_path = '/work2/noaa/jcsda/maryamao/garage/compare_exp/4denvar'
input_yaml = 'hofx3d_lambertCC.yaml'
executable = 'genint_hofx3d.x'

if not os.path.exists(wrkpath):
    os.makedirs(wrkpath)
else:
    shutil.rmtree(wrkpath)
    os.makedirs(wrkpath)
os.chdir(wrkpath)

date1 = pd.to_datetime(sdate,format='%Y%m%d%H')
date2 = pd.to_datetime(edate,format='%Y%m%d%H')
delta = timedelta(hours=hint)
dates = pd.date_range(start=date1, end=date2, freq=delta)

in_sbatch_tmpl = os.path.join(srcpath,'etc','sbatch_tmpl')
wrksbatch = os.path.join(wrkpath,'runscript')
wrkyaml = os.path.join(wrkpath,'running.yaml')

for cdate in dates:
    # execute the genint_hofx3d
    yaml_file = os.path.join(srcpath,'yamls',input_yaml)
    conf_temp = yaml.load(open(yaml_file),Loader=yaml.FullLoader)

    cdate_str = cdate.strftime('%Y-%m-%dT%H:%M:%SZ')
    # Update time window and dump to working yaml
    conf_temp['time window']['begin'] = cdate_str

    with open(wrkyaml,'w') as f:
        yaml.dump(conf_temp,f) 

    shutil.copyfile(in_sbatch_tmpl,wrksbatch)
    fullexec = os.path.join(genint_build,'bin',executable)
    cmd_str = 'srun --cpu_bind=core '+fullexec+' '+wrkyaml+' 2> stderr.$$.log 1> stdout.$$.log'
    with open(wrksbatch,'a') as f:
        f.write(cmd_str)


# Check the outputs
#hofx_file

# Update the StatAnalysis.conf
# Issue the METplus

# Collect the stats and plots


