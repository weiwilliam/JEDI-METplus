#!/bin/bash

echo "Loading EWOK-SKYLAB Environment Using Spack-Stack 1.8.0"

# load modules
module purge
module use /apps/contrib/spack-stack/spack-stack-1.8.0/envs/ue-gcc-12.2.0/install/modulefiles/Core
module load stack-gcc/12.2.0
module load stack-openmpi/4.1.4
module load stack-python/3.11.7

module load singularity

# This is a fix for the issue where the spack-stack-1.8.0 udunits
# module does not get loaded propery. Without this workaround, the
# udunits module from the "spack-managed" gets loaded instead and
# ecbuild on jedi-bundle fails.
#
# Setting LMOD_TMOD_FIND_FIRST gets rid of the default marking
# of modules, and the modification of MODULEPATH makes sure
# that spack-stack-1.8.0 modules are found first before same
# named modules in other directories (ie, "spack-managed")
export LMOD_TMOD_FIND_FIRST=yes
module use /apps/contrib/spack-stack/spack-stack-1.8.0/envs/ue-gcc-12.2.0/install/modulefiles/gcc/12.2.0

jedi-host-post-load() {
  module unload bufr-query
}
