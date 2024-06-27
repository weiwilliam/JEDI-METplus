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
from functions import run_job, check_job, setup_cmd, get_dates

# Load the configuration defined by main yaml file
control_yaml = sys.argv[1]
conf = yaml.load(open(control_yaml),Loader=yaml.FullLoader)
timeconf = conf['time']
metconf = conf['metplus']
jobconf = conf['jobconf']
genintconf = conf['genint']
dataconf = conf['Data']

window_length = 6

# Construct the work and output folders
casename = genintconf['obsname'] + '_' + genintconf['bkgname']
srcpath = os.path.join(os.path.dirname(__file__), '..') 
wrkpath = os.path.join(srcpath, 'workdir')
datapath =  os.path.join(wrkpath, 'Data')
metplus_runpath = os.path.join(wrkpath, 'run_metplus')
inpath = os.path.join(datapath, 'input')

outpath = os.path.join(dataconf['output'], casename)
statsout_path = os.path.join(outpath, 'stats')
hofxout_path = os.path.join(outpath, 'hofx')

logpath = os.path.join(srcpath, 'logs', casename)

os.environ['runworkdir'] = wrkpath
os.environ['runmetplusdir'] = metplus_runpath

pathlist = [wrkpath, logpath, datapath, inpath, outpath,
            metplus_runpath, statsout_path, hofxout_path]

if os.path.exists(wrkpath):
    shutil.rmtree(wrkpath)

for dir in pathlist:
    if not os.path.exists(dir):
        os.makedirs(dir)
    else:
        shutil.rmtree(dir)
        os.makedirs(dir)

os.chdir(wrkpath)

for dir in ['bkg','obs','crtm']:
    os.symlink(dataconf['input'][dir], os.path.join(inpath,dir))
os.symlink(outpath, 'Data/output')

wlnth = timedelta(hours=window_length)
dates = get_dates(timeconf['sdate'], timeconf['edate'], timeconf['dateint'])

slurm_platforms = ['s4', 'orion', 'discover']
pbs_platforms = ['derecho']
if jobconf['platform'] in slurm_platforms:
    in_jobhead = os.path.join(srcpath,'etc','jobhead_slurm')
elif jobconf['platform'] in pbs_platforms:
    in_jobhead = os.path.join(srcpath,'etc','jobhead_pbs')

fullexec = os.path.join(genintconf['build'], 'bin', genintconf['jediexec'])
wrksbatch = os.path.join(wrkpath,'runscript')
wrkyaml = os.path.join(wrkpath,'running.yaml')

# Setup METplus related variables
in_statanalysis_conf = os.path.join(srcpath,'etc',metconf['met_conf_temp'])
wk_statanalysis_conf = os.path.join(wrkpath,'statanalysis.conf')
embedded_py = os.path.join(srcpath, 'pyscripts', metconf['ioda2metmpr'])

for cdate in dates:
    cdate_str1 = cdate.strftime('%Y%m%d%H')
    cdate_str2 = cdate.strftime('%Y%m%d_%H%M%S')
    cdate_str3 = cdate.strftime('%Y-%m-%dT%H:%M:%SZ')
    w_beg_str = (cdate - wlnth/2).strftime('%Y-%m-%dT%H:%M:%SZ')

    obsinfile = os.path.join('Data/input/obs',cdate.strftime(dataconf['obs_template']))
    obsoutfile = os.path.join('Data/output/hofx','hofx_%s' %(cdate.strftime(dataconf['obs_template'])))
    ds = xr.open_dataset(obsinfile)
    if ds.Location.size==0:
        print('No observation available at %s' %(cdate_str1))
        ds.close()
        continue
    else:
        if genintconf['simulated_varname'] != 'aerosolOpticalDepth':
            ret_nlev = ds.Layer.size

    for fhr in metconf['verify_fhours']:
        print('Processing %s f%.3i' %(cdate_str1,fhr))
        init_date = cdate - timedelta(hours=fhr)
        init_dstr = init_date.strftime('%Y%m%d%H')

        # execute the genint_hofx3d
        yaml_file = os.path.join(srcpath,'yamls',genintconf['jediyaml'])
        conf_temp = yaml.load(open(yaml_file),Loader=yaml.FullLoader)

        logfile = os.path.join(logpath, 'runlog.%s_f%.3i' %(init_dstr, fhr))

        # Update time window and dump to working yaml
        conf_temp['time window']['begin'] = w_beg_str
        conf_temp['state']['date'] = cdate_str3
        bkg_file = cdate.strftime(dataconf['bkg_template'])
        conf_temp['state']['filepath'] = os.path.join('Data/input/bkg/',bkg_file)

        for subobs_conf in conf_temp['observations']['observers']:
            subobs_conf['obs space']['name'] = genintconf['simulated_varname']
            subobs_conf['obs space']['obsdatain']['engine']['obsfile'] = obsinfile
            subobs_conf['obs space']['obsdataout']['engine']['obsfile'] = obsoutfile
            if genintconf['simulated_varname'] == 'aerosolOpticalDepth':
                subobs_conf['obs operator']['obs options']['Sensor_ID'] = genintconf['obsname'] 
            else:
                subobs_conf['obs space']['simulated variables'] = [genintconf['simulated_varname']]
                subobs_conf['obs operator']['nlayers_retrieval'] = ret_nlev
                subobs_conf['obs operator']['tracer variables'] = [genintconf['tracer_name']]

        with open(wrkyaml,'w') as f:
            yaml.dump(conf_temp,f) 

        # Update jobcard
        with open(in_jobhead, 'r') as file:
            content = file.read()
        new_content = content.replace('%ACCOUNT%',jobconf['account'])
        new_content = new_content.replace('%JOBNAME%',jobconf['jobname'])
        new_content = new_content.replace('%PARTITION%',jobconf['partition'])
        new_content = new_content.replace('%WALLTIME%',jobconf['walltime'])
        new_content = new_content.replace('%QOS%',jobconf['qos'])
        new_content = new_content.replace('%N_NODE%',str(jobconf['n_node']))
        new_content = new_content.replace('%N_TASK%',str(jobconf['n_task']))
        new_content = new_content.replace('%LOGFILE%',logfile)
        with open(wrkjobcard,'w') as file:
            file.write(new_content)

        execcmd = setup_cmd(jobconf)
        cmd_str = execcmd+' '+fullexec+' '+wrkyaml #+' 2> stderr.$$.log 1> stdout.$$.log'
        with open(wrkjobcard,'a') as f:
            f.write(cmd_str)
    
        output = run_job(wrkjobcard)
        jobid = output.split()[-1]
        status = 0
        while status == 0:
            status = check_job(jobid)
            if status == 0: time.sleep(jobconf['check_freq'])

        # Check the outputs
        hofx_file = subobs_conf['obs space']['obsdataout']['engine']['obsfile']
        if not os.path.exists(hofx_file):
            print(hofx_file+' does not exist')
            continue

        # Update the StatAnalysis.conf
        py_input = '%s' %(hofx_file)
        with open(in_statanalysis_conf,'r') as file:
            tmp_mp_confs = file.read()
        mp_confs = tmp_mp_confs.replace('@INPUT_BASE@', wrkpath)
        mp_confs = mp_confs.replace('@OUTPUT_BASE@', metplus_runpath )
        mp_confs = mp_confs.replace('@PARM_BASE@', os.environ['metplus_ROOT'])
        mp_confs = mp_confs.replace('@valid_begin@', cdate_str1)
        mp_confs = mp_confs.replace('@valid_end@', cdate_str1)
        mp_confs = mp_confs.replace('@embedded_py@', embedded_py)
        mp_confs = mp_confs.replace('@embedded_input@', py_input)
        #mp_confs = mp_confs.replace('@OBSTYPE@',obs_type)
        with open(wk_statanalysis_conf, 'w') as file:
            file.write(mp_confs)

        #   Running METplus
        metplus_conf = pre_run_setup(wk_statanalysis_conf)
        total_errors = run_metplus(metplus_conf)
        post_run_cleanup(metplus_conf, 'METplus', total_errors)

        # Collect the stats and plots
        stat_file = os.path.join(wrkpath, 'Data/output/stats', cdate_str1+'.out')
        if not os.path.exists(stat_file):
            print(stat_file+' does not exist')
            continue
