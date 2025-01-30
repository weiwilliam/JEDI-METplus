# JEDI-METplus
Workflow to interface JEDI component (generic-interface) and METplus for constituents model evaluation.

## Clone the code
Clone this repo recusively with the command below
`git clone https://github.com/weiwilliam/JEDI-METplus.git <folder>`

## Supported platforms
* Platforms with JCSDA spack-stack package.
* Module loading scripts: derecho_intel.

## Supported (Tested) models 
* Lambert CC projection: WRF-Chem
* Reducing Gaussian Lat-Lon (GEFS-Aerosols)

## Supported (Tested) measurements
* TropOMI NO2 and CO
* VIIRS AOD
* TEMPO NO2, CO

## Use of this interface
* Prerequisites: observation files in IODA format and model outputs in NetCDF (GRIB2 may be supported later).
1. Create Python venv under your repo, `source ush/setup.sh </repo/path> <platform> <compiler>`
2. Based on your application, copy a main yaml file from yamls/main and a hofx3d yaml file from yamls/hofx3d.
   <e.g., evaluate wrf-chem trace gas, copy `main/main_wrfchem.yaml` and `hofx3d/hofx3d_lambertCC.yaml`>
3. Update the main and hofx3d yaml files as needed. Check README.md under `yamls/<main/hofx3d>` for details.
4. Execute `pyscripts/genint_vrfy.py <main yaml>`

## Build generic interface (genint-bundle)
1. Create the `<repo>/genint-bundle/build` folder
2. `export GENINT_BUILD=<path/to/build/genint>`
3. Create virtual python env `<repo>/venv` if you do not have one.
   `source ush/setup.sh <repo path> <platform> <compiler>`
4. `cd <path/to/build/genint>`
5. `ecbuild <path/to/genint-bundle>`
6. `make -j <n>`
7. `ctest` to check executables work properly
