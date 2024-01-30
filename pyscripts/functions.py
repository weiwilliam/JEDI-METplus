#!/usr/bin/env python3
__all__ = ['run_job','check_job']
import subprocess
import os

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
