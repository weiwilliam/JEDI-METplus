#!/usr/bin/env python3
import sys, os
from pathlib import Path
import shutil
import pandas as pd
import xarray as xr
import yaml 
import subprocess
import time
from datetime import datetime, timedelta
# Add metplus_ROOT to access METplus wrappers and utilities
sys.path.insert(0, os.environ['metplus_ROOT'])
import produtil.setup
from metplus.util import metplus_check
from metplus.util import pre_run_setup, run_metplus, post_run_cleanup
from metplus import __version__ as metplus_version
from functions import run_job,check_job

sdate = 2024011718
edate = 2024012318
dateint = 24
window_length = 6
verif_fhr_list = [6]
genint_build = '/data/users/swei/Git/JEDI/genint-bundle/build'
slurm_acct = 'star'
slurm_part = 's4'
slurm_qos = 'normal'
job_check_freq = 10 # seconds
#genint_build = '/work2/noaa/jcsda/shihwei/git/builds/genint'

# paths for model and observations
bkg_path_tmpl = '/data/users/swei/Dataset/Wx-AQ/wrfgsi.out.%Y%m%d%H'
bkg_file_tmpl = 'wrfout_d01_%Y%m%d_%H0000'
obs_path = '/data/users/swei/Dataset/S5P_TROPOMI'
sensor = 'tropomi'
obsvar = 'no2'
obtype = 'tropo'
obs_product = '%s_%s_%s' %(sensor,obsvar,obtype)
obs_file_tmpl = 'cropped_'+obs_product+'_%Y%m%d%H.nc'
input_yaml = 'hofx3d_lambertCC.yaml'
executable = 'genint_hofx3d.x'
metplus_conf_tmpl = 'StatAnalysis.conf_tmpl' 
ioda2mprscript = 'ioda2metplusmpr.py'

# io name varies with model
io_jedi_mapdict = {'no2':'nitrogendioxide',
                   'co':'carbonmonoxide'}
if obtype=='total':
   simulated_varname = io_jedi_mapdict[obsvar]+'Total'
elif obtype=='tropo':
   simulated_varname = io_jedi_mapdict[obsvar]+'Column'

# /work2/noaa/jcsda/maryamao/garage/compare_exp/4denvar_an
# obs_path = '/work2/noaa/jcsda/maryamao/garage/compare_exp/4denvar'
#
srcpath = os.path.join(os.path.dirname(__file__),'..') #'/work2/noaa/jcsda/shihwei/git/JEDI-METplus' #will replaced by path or file attributes.
wrkpath = os.path.join(srcpath,'workdir')
logpath = os.path.join(wrkpath,'logs')
outpath = os.path.join(wrkpath,'output')
statsout_path = os.path.join(srcpath,'stats',obs_product)
crtm_coeff_path = os.path.join(genint_build,'test_data/3.1.0/fix_REL-3.1.0.1_01252024/fix')
metplus_runpath = os.path.join(wrkpath,'metplus')
os.environ['runworkdir'] = wrkpath
os.environ['runmetplusdir'] = metplus_runpath

for dir in [wrkpath,logpath,outpath,metplus_runpath]: 
    if not os.path.exists(dir):
        os.makedirs(dir)
    else:
        shutil.rmtree(dir)
        os.makedirs(dir)

if not os.path.exists(statsout_path):
    os.makedirs(statsout_path)

if os.path.exists(crtm_coeff_path):
    os.symlink(crtm_coeff_path,os.path.join(wrkpath,'CRTM'))

os.chdir(wrkpath)

wlnth = timedelta(hours=window_length)
date1 = pd.to_datetime(sdate,format='%Y%m%d%H')
date2 = pd.to_datetime(edate,format='%Y%m%d%H')
delta = timedelta(hours=dateint)
dates = pd.date_range(start=date1, end=date2, freq=delta)

in_sbatch_tmpl = os.path.join(srcpath,'etc','sbatch_tmpl')
fullexec = os.path.join(genint_build,'bin',executable)
wrksbatch = os.path.join(wrkpath,'runscript')
wrkyaml = os.path.join(wrkpath,'running.yaml')

for cdate in dates:
    cdate_str1 = cdate.strftime('%Y%m%d%H')
    cdate_str2 = cdate.strftime('%Y%m%d_%H%M%S')
    cdate_str3 = cdate.strftime('%Y-%m-%dT%H:%M:%SZ')
    w_beg_str = (cdate - wlnth/2).strftime('%Y-%m-%dT%H:%M:%SZ')

    obsinfile = os.path.join(obs_path,cdate.strftime(obs_file_tmpl))
    ds = xr.open_dataset(obsinfile)
    if ds.Location.size==0:
        print('No observation available at %s' %(cdate_str1))
        ds.close()
        continue
    else:
        ret_nlev = ds.Layer.size
    obsoutfile = os.path.join(outpath,'hofx_%s' %(cdate.strftime(obs_file_tmpl)))

    for fhr in verif_fhr_list:
        print('Processing %s f%.3i' %(cdate_str1,fhr))
        init_date = cdate - timedelta(hours=fhr)
        init_dstr = init_date.strftime('%Y%m%d%H')

        # execute the genint_hofx3d
        yaml_file = os.path.join(srcpath,'yamls',input_yaml)
        conf_temp = yaml.load(open(yaml_file),Loader=yaml.FullLoader)

        logfile = 'runlog.%s_f%.3i' %(init_dstr,fhr)
        slurm_log = os.path.join(logpath,logfile)

        # Update time window and dump to working yaml
        conf_temp['time window']['begin'] = w_beg_str
        conf_temp['state']['date'] = cdate_str3
        if '%' in bkg_path_tmpl:
            bkg_path = init_date.strftime(bkg_path_tmpl)
        else:
            bkg_path = bkg_path_tmpl
        bkg_file = cdate.strftime(bkg_file_tmpl)
        conf_temp['state']['filepath'] = os.path.join(bkg_path,bkg_file)

        for subobs_conf in conf_temp['observations']['observers']:
            subobs_conf['obs space']['obsdatain']['engine']['obsfile'] = obsinfile
            subobs_conf['obs space']['obsdataout']['engine']['obsfile'] = obsoutfile
            subobs_conf['obs space']['simulated variables'] = [simulated_varname]
            subobs_conf['obs operator']['nlayers_retrieval'] = ret_nlev
            subobs_conf['obs operator']['tracer variables'] = [obsvar]

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
            continue

        # Update the StatAnalysis.conf
        in_statanalysis_conf = os.path.join(srcpath,'etc',metplus_conf_tmpl)
        wk_statanalysis_conf = os.path.join(wrkpath,'statanalysis.conf')
        embedded_py = os.path.join(srcpath,'pyscripts',ioda2mprscript)
        py_input = '%s' %(hofx_file)
        with open(in_statanalysis_conf,'r') as file:
            tmp_mp_confs = file.read()
        mp_confs = tmp_mp_confs.replace('@INPUT_BASE@',wrkpath)
        mp_confs = mp_confs.replace('@OUTPUT_BASE@',metplus_runpath)
        mp_confs = mp_confs.replace('@PARM_BASE@',os.environ['metplus_ROOT'])
        mp_confs = mp_confs.replace('@valid_begin@',cdate_str1)
        mp_confs = mp_confs.replace('@valid_end@',cdate_str1)
        mp_confs = mp_confs.replace('@embedded_py@',embedded_py)
        mp_confs = mp_confs.replace('@embedded_input@',py_input)
        #mp_confs = mp_confs.replace('@OBSTYPE@',obs_type)
        with open(wk_statanalysis_conf,'w') as file:
            file.write(mp_confs)

        #   Running METplus
        metplus_conf = pre_run_setup(wk_statanalysis_conf)
        total_errors = run_metplus(metplus_conf)
        post_run_cleanup(metplus_conf, 'METplus', total_errors)

        # Collect the stats and plots
        stat_file = os.path.join(metplus_runpath,'statanalysis_output',cdate_str1+'.out')
        if not os.path.exists(stat_file):
            print(stat_file+' does not exist')
            continue

