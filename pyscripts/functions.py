#!/usr/bin/env python3
__all__ = ['run_job','check_job','get_dates','set_size','setup_cmd']
import subprocess
import os
import pandas as pd
import matplotlib.pyplot as plt

def run_job(script):
    stdout = subprocess.check_output(["sbatch", script]).decode('utf-8')
    print(stdout,flush=1)
    return stdout

def check_job(jobid):
    stdout = subprocess.check_output(["squeue", "-j", jobid]).decode('utf-8')
    if jobid in stdout:
        status = 0
        print(stdout,flush=1)
    else:
        status = 1
        print('JOB ID: '+jobid+' Finished',flush=1)
    return status

def get_dates(sdate,edate,hint):
    from datetime import datetime, timedelta
    date1 = pd.to_datetime(sdate,format='%Y%m%d%H')
    date2 = pd.to_datetime(edate,format='%Y%m%d%H')
    delta = timedelta(hours=hint)
    dates = pd.date_range(start=date1, end=date2, freq=delta)
    return dates

def set_size(w,h, ax=None, l=None, r=None, t=None, b=None):
    """ w, h: width, height in inches """
    if not ax: ax=plt.gca()
    if not l:
       l = ax.figure.subplotpars.left
    else:
       ax.figure.subplots_adjust(left=l)
    if not r:
       r = ax.figure.subplotpars.right
    else:
       ax.figure.subplots_adjust(right=r)
    if not t:
       t = ax.figure.subplotpars.top
    else:
       ax.figure.subplots_adjust(top=t)
    if not b:
       b = ax.figure.subplotpars.bottom
    else:
       ax.figure.subplots_adjust(bottom=b)

    figw = float(w)/(r-l)
    figh = float(h)/(t-b)
    ax.figure.set_size_inches(figw, figh)

def setup_cmd(conf):
    from shutil import which

    if conf['platform'] == 's4':
        execcmd = which('srun')+' --cpu_bind=core'
    elif conf['platform'] == 'orion':
        execcmd = which('mpirun')
    elif conf['platform'] == 'derecho':
        execcmd = which('mpiexec')+' -n %s -ppn %s' % (conf['n_nodes'],str(conf['n_tasks']/conf['n_nodes']) )
    else:
        raise Exception('Not supported platform')

    return execcmd
