#!/usr/bin/env python3
__all__ = ['run_job','check_job']
import subprocess

def run_job(script):
    return subprocess.check_output(["sbatch", script])

def check_job():
    return subprocess.check_output(["squeue", "-u", getuser()])[-1]
