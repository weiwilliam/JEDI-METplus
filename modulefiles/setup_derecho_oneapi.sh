#!/bin/bash

echo "Loading EWOK-SKYLAB Environment Using Spack-Stack 1.9.1"

# load modules
module purge
# ignore that the sticky module ncarenv/... is not unloaded
export LMOD_TMOD_FIND_FIRST=yes
module load ncarenv/23.09
module use /glade/work/epicufsrt/contrib/spack-stack/derecho/modulefiles

module use /glade/work/epicufsrt/contrib/spack-stack/derecho/spack-stack-1.9.1/envs/ue-oneapi-2024.2.1/install/modulefiles/Core
module load stack-oneapi/2024.2.1
module load stack-cray-mpich/8.1.29
module load stack-python/3.11.7

module load jedi-fv3-env
module load ewok-env
module load metplus

# See README.md
export LD_LIBRARY_PATH="${GENINT_BUILD}/lib:${LD_LIBRARY_PATH}"

