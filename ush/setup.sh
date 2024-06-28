#!/usr/bin/env bash
topdir=$1
platform=$2
compiler=$3

modules_setup_script=$topdir/modulefiles/setup_${platform}_${compiler}.sh
echo $modules_setup_script

if [ -s $topdir/venv/bin/activate ]; then
    source $topdir/venv/bin/activate
else
    if [ -f $modules_setup_script ]; then
        source $modules_setup_script
    else
        echo "$modules_setup_script is not available for $platform and $complier"
    fi
    python3 -m venv $topdir/venv
    source $topdir/venv/bin/activate
fi
