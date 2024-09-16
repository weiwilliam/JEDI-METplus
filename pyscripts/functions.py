#!/usr/bin/env python3
__all__ = ['get_dates','set_size','setup_cmd', 'set_area', 'find_stats']
import subprocess
import os
import pandas as pd
import matplotlib.pyplot as plt
from shutil import which

def get_dates(sdate,edate,hint):
    from datetime import datetime, timedelta
    date1 = pd.to_datetime(sdate,format='%Y%m%d%H')
    date2 = pd.to_datetime(edate,format='%Y%m%d%H')
    delta = timedelta(hours=hint)
    dates = pd.date_range(start=date1, end=date2, freq=delta)
    return dates

def find_stats(statsfile):
    f = open(statsfile, 'r')
    find = len(f.readlines()) > 1
    f.close()
    return find

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

def set_area(areaname):
    if areaname == 'glb':
        minlon = -180.; maxlon = 180.; minlat = -90.; maxlat = 90.
    elif areaname == 'wxaq':
        minlon = -81.; maxlon = -70; minlat = 39.8; maxlat = 46.
    return minlon, maxlon, minlat, maxlat

class setup_job(object):

    def __init__(self, conf):
        self.platform = conf['platform']
        self.jobname = conf['jobname']
        self.n_node = conf['n_node']
        self.n_task = conf['n_task']
        self.walltime = conf['walltime']
        self.account = conf['account']
        self.partition = conf['partition']
        self.qos = conf['qos']
        self.memory = conf['memory']
        self.check_freq = conf['check_freq']
        self._setcmds()

    def _setcmds(self):
        slurm_list = ['s4', 'orion', 'discover']
        pbs_list = ['derecho']
        if self.platform in slurm_list:
            self.submit_cmd = which('sbatch')
            self.search_cmd = which('squeue')
            self.search_arg = '-j'
            self.header = 'jobhead_slurm'
        elif self.platform in pbs_list:
            self.submit_cmd = which('qsub')
            self.search_cmd = which('qstat')
            self.search_arg = '-w'
            self.header = 'jobhead_pbs'
        else:
           raise Exception(f'Platform {self.platform} not supported')
        
        if self.platform == 's4':
            self.execcmd = which('mpiexec')+' -n %s' % (self.n_task)
        elif self.platform in ['orion', 'discover']:
            self.execcmd = which('mpirun')
        elif self.platform == 'derecho':
            self.execcmd = which('mpiexec')+' -n %s -ppn %s' % (self.n_node,str(self.n_task / self.n_node))
     
    def create_job(self, **args):
        with open(args['in_jobhdr'], 'r') as file:
            content = file.read()
        new_content = content.replace('%ACCOUNT%', self.account)
        new_content = new_content.replace('%JOBNAME%', self.jobname)
        new_content = new_content.replace('%PARTITION%', self.partition)
        new_content = new_content.replace('%WALLTIME%', self.walltime)
        new_content = new_content.replace('%QOS%', self.qos)
        new_content = new_content.replace('%N_NODE%', str(self.n_node))
        new_content = new_content.replace('%N_TASK%', str(self.n_task))
        new_content = new_content.replace('%LOGFILE%', args['logfile'])
        new_content = new_content.replace('%MEMORY%', str(self.memory))
        with open(args['jobcard'], 'w') as file:
            file.write(new_content)
    
    def submit(self, script):
        output = subprocess.run([self.submit_cmd, script], capture_output=True)
        stdout = output.stdout.decode('utf-8')
        print(stdout, flush=1)
        stderr = output.stderr.decode('utf-8')
        print(stderr, flush=1)
        return stdout

    def check(self, jobid):
        output = subprocess.run([self.search_cmd, self.search_arg, jobid], check=False, capture_output=True)
        stdout = output.stdout.decode('utf-8')
        if jobid in stdout:
            status = 0
            print(stdout, flush=1)
        else:
            status = 1
            print('JOB ID: '+jobid+' Finished', flush=1)
        return status
