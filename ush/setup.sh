#!/usr/bin/env bash
topdir=$1
platform=$2
compiler=$3

export GENINT_BUILD=$topdir/genint-bundle/build
modules_setup_script=$topdir/modulefiles/setup_${platform}_${compiler}.sh

if [ -f $modules_setup_script ]; then
    echo "Load modules with $modules_setup_script"
    source $modules_setup_script
else
    echo "$modules_setup_script is not available for $platform and $complier"
fi

if [ -s $topdir/venv/bin/activate ]; then
    source $topdir/venv/bin/activate
else
    echo "Create $topdir/venv"
    python3 -m venv $topdir/venv
    source $topdir/venv/bin/activate
fi
