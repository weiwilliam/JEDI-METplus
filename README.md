# JEDI-METplus
Workflow to interface JEDI component (generic-interface) and METplus for constituents model evaluation.

## Clone the code
Clone this repo recusively with the command below
`git clone --recurse-submodules`

## Supported platforms
* Platforms with JCSDA spack-stack package, now provide derecho_intel module loading script.

## Supported (Tested) models 
* Lambert CC projection: WRF-Chem

## Supported (Tested) measurements
* TropOMI NO2 and CO 

## Installation of generic interface
1. Create the `build/genint` folder
2. `export GENINT_BUILD=<path/to/build/genint>`
3. `source modulefiles/setup_<platform>_<compiler>`
4. `cd <path/to/build/genint>`
5. `ecbuild <path/to/genint-bundle>`
6. `make -j<n>`
7. ``

## Use of this interface
* prerequisites: observation files in IODA format and model outputs in NetCDF.


