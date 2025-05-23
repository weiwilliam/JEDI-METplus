#!/usr/bin/env bash

echo "Loading EWOK-SKYLAB Environment Using Spack-Stack 1.8.0"

# load modules
module purge
# ignore that the sticky module ncarenv/... is not unloaded
export LMOD_TMOD_FIND_FIRST=yes
module load ncarenv/23.09
module use /glade/work/epicufsrt/contrib/spack-stack/derecho/modulefiles

module use /glade/work/epicufsrt/contrib/spack-stack/derecho/spack-stack-1.8.0/envs/ue-intel-2021.10.0/install/modulefiles/Core
module load stack-intel/2021.10.0
module load stack-cray-mpich/8.1.25
module load stack-python/3.11.7

module load jedi-fv3-env
module load ewok-env
module load metplus

# See README.md
export LD_LIBRARY_PATH="${GENINT_BUILD}/lib:${LD_LIBRARY_PATH}"

