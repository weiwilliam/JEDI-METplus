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
from functions import setup_job, get_dates

# Load the configuration defined by main yaml file
main_yaml = sys.argv[1]
conf = yaml.load(open(main_yaml),Loader=yaml.FullLoader)

run_jedihofx = conf['run_jedihofx']
run_met_plus = conf['run_met_plus']
verbose = conf['verbose']
restart = conf['restart']
timeconf = conf['time']
metconf = conf['metplus']
jobconf = conf['jobconf']
genintconf = conf['genint']
dataconf = conf['Data']

# Create work and output folders
casename = genintconf['obsname'] + '_' + genintconf['bkgname']
srcpath = os.path.join(os.path.dirname(__file__), '..') 
wrkpath = os.path.join(srcpath, 'workdir')
datapath =  os.path.join(wrkpath, 'Data')
metplus_runpath = os.path.join(wrkpath, 'run_metplus')
inpath = os.path.join(datapath, 'input')

outpath = os.path.join(dataconf['output'], casename)
statsout_path = os.path.join(outpath, 'stats')
hofxout_path = os.path.join(outpath, 'hofx')
gvalout_path = os.path.join(outpath, 'geovals')

logpath = os.path.join(srcpath, 'logs', casename)

os.environ['runworkdir'] = wrkpath
os.environ['runmetplusdir'] = metplus_runpath

pathlist = [wrkpath, logpath, datapath, inpath, outpath,
            metplus_runpath, statsout_path, hofxout_path,
            gvalout_path,
            ]

if restart:
    for dir in pathlist:
        if not os.path.exists(dir):
            os.makedirs(dir)
else:
    for dir in pathlist:
        if not os.path.exists(dir):
            os.makedirs(dir)
        else:
            shutil.rmtree(dir)
            os.makedirs(dir)
    for fhr in metconf['verify_fhours']:
        subfhr_hofx = os.path.join(hofxout_path, 'f%.2i'%(fhr))
        os.makedirs(subfhr_hofx)

    # Create symbolic links of needed input/output folders
    os.symlink(outpath, wrkpath+'/Data/output')
    for dir in ['bkg','obs','crtm']:
        os.symlink(dataconf['input'][dir], os.path.join(inpath,dir))

os.chdir(wrkpath)

if run_jedihofx:
   
    window_length = dataconf['obs_window_length']
    wlnth = timedelta(hours=window_length)
    dates = get_dates(timeconf['sdate'], timeconf['edate'], timeconf['dateint'])

    # Setup job confs    
    job = setup_job(jobconf)
    in_jobhead = os.path.join(srcpath, 'etc', job.header)
    
    fullexec = os.path.join(genintconf['build'], 'bin', genintconf['jediexec'])
    wrkjobcard = os.path.join(wrkpath, 'runscript')
    wrkyaml = os.path.join(wrkpath, 'running.yaml')
    
    for cdate in dates:
        cdate_str1 = cdate.strftime('%Y%m%d%H')
        cdate_str2 = cdate.strftime('%Y%m%d_%H%M%S')
        cdate_str3 = cdate.strftime('%Y-%m-%dT%H:%M:%SZ')
        w_beg_str = (cdate - wlnth/2).strftime('%Y-%m-%dT%H:%M:%SZ')
    
        obsinfile = os.path.join(datapath,'input/obs',cdate.strftime(dataconf['obs_template']))
        if not os.path.exists(obsinfile):
            print(f'{obsinfile} not available')
            print('')
            continue
    
        ds = xr.open_dataset(obsinfile)
        if ds.Location.size==0:
            print('No observation available at %s' %(cdate_str1))
            ds.close()
            continue
        else:
            if genintconf['simulated_varname'] != 'aerosolOpticalDepth':
                ret_nlev = ds.Layer.size
    
        for fhr in metconf['verify_fhours']:
            init_date = cdate - timedelta(hours=fhr)
            init_dstr = init_date.strftime('%Y%m%d%H')
            init_cyc = init_date.strftime('%H')
            if init_cyc not in dataconf['bkg_init_cyc']:
                if verbose: print(f'{init_cyc} is not in bkg init cycle list')
                continue
            print('Processing %s f%.2i' %(cdate_str1, fhr))
    
            # execute the genint_hofx3d
            yaml_file = os.path.join(srcpath,'yamls',genintconf['jediyaml'])
            conf_temp = yaml.load(open(yaml_file),Loader=yaml.FullLoader)
    
            logfile = os.path.join(logpath, 'runlog.%s_f%.2i' %(init_dstr, fhr))
    
            # Update time window and dump to working yaml
            conf_temp['time window']['begin'] = w_beg_str
            conf_temp['time window']['length'] = f'PT{window_length}H'
            conf_temp['state']['date'] = cdate_str3
            if '{init_date}' in dataconf['bkg_template']:
                bkg_file = cdate.strftime(dataconf['bkg_template'].format(init_date=init_dstr))
            else:
                bkg_file = cdate.strftime(dataconf['bkg_template'])

            conf_temp['state']['filepath'] = os.path.join(datapath,'input/bkg/',bkg_file)
            if not os.path.exists(conf_temp['state']['filepath'] + dataconf['bkg_extension']):
                print(f'{bkg_file} is not available for fcst={fhr}hr from {init_dstr}')
                continue
    
            obsoutfile = os.path.join(datapath,'output/hofx','f%.2i' %(fhr), 'hofx_%s' %(cdate.strftime(dataconf['obs_template'])))
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
            #if 'GOMSaver' in subobs_conf['obs filter'][]
    
            with open(wrkyaml,'w') as f:
                yaml.dump(conf_temp,f) 
    
            # Update jobcard
            job.create_job(in_jobhdr=in_jobhead, jobcard=wrkjobcard, logfile=logfile)
    
            cmd_str = job.execcmd+' '+fullexec+' '+wrkyaml #+' 2> stderr.$$.log 1> stdout.$$.log'
            with open(wrkjobcard,'a') as f:
                f.write(cmd_str)
        
            output = job.submit(wrkjobcard)
            jobid = output.split()[-1]
            if jobconf['platform']=='derecho': time.sleep(15)
            if jobconf['check_freq'] != -1:
                status = 0
                while status == 0:
                    status = job.check(jobid)
                    if status == 0: time.sleep(jobconf['check_freq'])
    
            # Check the outputs
            hofx_file = subobs_conf['obs space']['obsdataout']['engine']['obsfile']
            if not os.path.exists(hofx_file):
                print(hofx_file+' does not exist')
                continue

if run_met_plus:
    print(f"run METplus for {timeconf['sdate']} to {timeconf['edate']}")
    
    # Setup METplus related variables
    in_statanalysis_conf = os.path.join(srcpath,'etc',metconf['met_conf_temp'])
    wk_statanalysis_conf = os.path.join(wrkpath,'statanalysis.conf')
    embedded_py = os.path.join(srcpath, 'pyscripts', metconf['ioda2metmpr'])

    # Update the StatAnalysis.conf
    leadtime_liststr = ''
    for fhr in metconf['verify_fhours']:
        leadtime_liststr += str(fhr)+', '
    
    py_input = '%s/f{lead_hour}/hofx_%s' %(hofxout_path, dataconf['obs_template'].replace('%Y%m%d%H','{valid?fmt=%Y%m%d%H}'))
    
    with open(in_statanalysis_conf,'r') as file:
        tmp_mp_confs = file.read()
    mp_confs = tmp_mp_confs.replace('@INPUT_BASE@', wrkpath)
    mp_confs = mp_confs.replace('@OUTPUT_BASE@', metplus_runpath )
    mp_confs = mp_confs.replace('@PARM_BASE@', os.environ['metplus_ROOT'])
    mp_confs = mp_confs.replace('@valid_begin@', str(timeconf['sdate']))
    mp_confs = mp_confs.replace('@valid_end@', str(timeconf['edate']))
    mp_confs = mp_confs.replace('@valid_inc@', '%iH'%(timeconf['dateint']))
    mp_confs = mp_confs.replace('@leadtime@', leadtime_liststr)
    mp_confs = mp_confs.replace('@embedded_py@', embedded_py)
    mp_confs = mp_confs.replace('@embedded_input@', py_input)
    #mp_confs = mp_confs.replace('@OBSTYPE@',obs_type)
    with open(wk_statanalysis_conf, 'w') as file:
        file.write(mp_confs)
    
    # Running METplus
    mp_jobcard = os.path.join(wrkpath, 'run_metplus.batch')
    mp_logfile = os.path.join(logpath, 'runmp.%s_%s.log' %(str(timeconf['sdate']), str(timeconf['edate'])))

    # Setup job confs    
    mpjob = setup_job(metconf)
    in_jobhead = os.path.join(srcpath, 'etc', mpjob.header)

    mpjob.create_job(in_jobhdr=in_jobhead, jobcard=mp_jobcard, logfile=mp_logfile)

    cmd_str = 'run_metplus.py -c ' + wk_statanalysis_conf
    with open(mp_jobcard,'a') as f:
        f.write(cmd_str)

    output = mpjob.submit(mp_jobcard)
    jobid = output.split()[-1]
    if metconf['platform']=='derecho': time.sleep(15)
    if metconf['check_freq'] != -1:
        status = 0
        while status == 0:
            status = mpjob.check(jobid)
            if status == 0: time.sleep(metconf['check_freq'])

    #metplus_conf = pre_run_setup(wk_statanalysis_conf)
    #total_errors = run_metplus(metplus_conf)
    #post_run_cleanup(metplus_conf, 'METplus', total_errors)
