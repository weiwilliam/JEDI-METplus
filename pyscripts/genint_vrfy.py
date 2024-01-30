#!/usr/bin/env python3
import sys, os
from pathlib import Path
import shutil
import pandas as pd
import yaml 
import subprocess
import time
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
genint_build = '/data/users/swei/Git/JEDI/genint-bundle/build'
slurm_acct = 'star'
slurm_part = 's4'
slurm_qos = 'normal'
job_check_freq = 5 # seconds
#genint_build = '/work2/noaa/jcsda/shihwei/git/builds/genint'

# paths for model and observations
bkg_path = '/work2/noaa/jcsda/shihwei/git/genint-bundle/genint/test/Data/background'
bkg_file_tmpl = 'wrfout_d01_subset_%date%'
# /work2/noaa/jcsda/maryamao/garage/compare_exp/4denvar_an
obs_path = '/work2/noaa/jcsda/shihwei/git/genint-bundle/genint/test/Data/observation'
# obs_path = '/work2/noaa/jcsda/maryamao/garage/compare_exp/4denvar'
input_yaml = 'hofx3d_lambertCC.yaml'
executable = 'genint_hofx3d.x'

#
srcpath = os.path.join(os.path.dirname(__file__),'..') #'/work2/noaa/jcsda/shihwei/git/JEDI-METplus' #will replaced by path or file attributes.
wrkpath = os.path.join(srcpath,'workdir')
logpath = os.path.join(wrkpath,'logs')
outpath = os.path.join(wrkpath,'output')
crtm_coeff = os.path.join(genint_build,'test_data/crtm/3.1.0_skylab_7.0')

for dir in [wrkpath,logpath,outpath]: 
    if not os.path.exists(dir):
        os.makedirs(dir)
    else:
        shutil.rmtree(dir)
        os.makedirs(dir)
os.chdir(wrkpath)

date1 = pd.to_datetime(sdate,format='%Y%m%d%H')
date2 = pd.to_datetime(edate,format='%Y%m%d%H')
delta = timedelta(hours=hint)
dates = pd.date_range(start=date1, end=date2, freq=delta)

in_sbatch_tmpl = os.path.join(srcpath,'etc','sbatch_tmpl')
fullexec = os.path.join(genint_build,'bin',executable)
wrksbatch = os.path.join(wrkpath,'runscript')
wrkyaml = os.path.join(wrkpath,'running.yaml')

for cdate in dates:

    cdate_str1 = cdate.strftime('%Y%m%d%H')
    cdate_str2 = cdate.strftime('%Y%m%d_%H%M%S')
    cdate_str3 = cdate.strftime('%Y-%m-%dT%H:%M:%SZ')
    w_beg_str = (cdate - delta/2).strftime('%Y-%m-%dT%H:%M:%SZ')

    # execute the genint_hofx3d
    yaml_file = os.path.join(srcpath,'yamls',input_yaml)
    conf_temp = yaml.load(open(yaml_file),Loader=yaml.FullLoader)

    logfile = 'runlog.'+cdate_str1
    slurm_log = os.path.join(logpath,logfile)

    # Update time window and dump to working yaml
    conf_temp['time window']['begin'] = w_beg_str
    conf_temp['state']['date'] = cdate_str3
    conf_temp['state']['filepath'] = os.path.join(bkg_path,bkg_file_tmpl.replace('%date%',cdate_str2))

    for subobs_conf in conf_temp['observations']['observers']:
        obsin = subobs_conf['obs space']['obsdatain']['engine']['obsfile']
        obsout = subobs_conf['obs space']['obsdataout']['engine']['obsfile']
        subobs_conf['obs space']['obsdatain']['engine']['obsfile'] = obsin.replace('%date%',cdate_str1)
        subobs_conf['obs space']['obsdataout']['engine']['obsfile'] = obsout.replace('%date%',cdate_str1)

    with open(wrkyaml,'w') as f:
        yaml.dump(conf_temp,f) 

    # Update jobcard
    with open(in_sbatch_tmpl, 'r') as file:
        content = file.read()
    new_content = content.replace('%ACCOUNT%',slurm_acct)
    new_content = new_content.replace('%PARTITION%',slurm_part)
    new_content = new_content.replace('%QOS%',slurm_qos)
    new_content = new_content.replace('%LOGFILE%',slurm_log)
    with open(wrksbatch,'w') as file:
        file.write(new_content)

    cmd_str = 'srun --cpu_bind=core '+fullexec+' '+wrkyaml #+' 2> stderr.$$.log 1> stdout.$$.log'
    with open(wrksbatch,'a') as f:
        f.write(cmd_str)
    
    output = run_job(wrksbatch)
    jobid = output.split()[-1]
    status = 0
    while status == 0:
        status = check_job(jobid)
        if status == 0: time.sleep(job_check_freq)

    # Check the outputs
    hofx_file = subobs_conf['obs space']['obsdataout']['engine']['obsfile']
    if not os.path.exists(hofx_file):
        print(hofx_file+' does not exist')

# Update the StatAnalysis.conf
# Issue the METplus

# Collect the stats and plots


