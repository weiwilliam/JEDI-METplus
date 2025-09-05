# JEDI-METplus
Workflow to use VIND interface JEDI components and METplus for constituents model evaluation.

## Clone the code
Clone this repo recusively with the command below
`git clone https://github.com/weiwilliam/JEDI-METplus.git <folder>`

## Supported platforms
* Platforms with JCSDA spack-stack package.
* Module loading scripts: derecho_intel (v1.8.0) and derecho_gnu (v1.9.1)

## Tested models 
* Lambert CC projection: WRF-Chem
* Reducing Gaussian Lon-Lat: GEFS-Aerosols
* Regular Lon-Lat: MERRA-2

## Tested measurements
* TropOMI NO2 and CO
* AOD from MODIS, VIIRS, OCI (PACE), AERONET
* TEMPO NO2, CO
* PANDORA NO2
* AirNow O3 and PM2.5

## Use of this interface
* Prerequisites: observation files in IODA format and model outputs in NetCDF (GRIB2 may be supported later).
1. Create Python venv under your repo, `source ush/setup.sh </repo/path> <platform> <compiler>`
2. Based on your application, update the main yaml file under yamls/main and the hofx3d yaml file from yamls/hofx3d.
   <e.g., evaluate wrf-chem trace gas, use `main/main_wrfchem.yaml` and `hofx3d/hofx3d_lambertCC.yaml`>
3. Update the main and hofx3d yaml files as needed. Check README.md under `yamls/<main, hofx3d>` for details.
4. Execute `pyscripts/genint_vrfy.py <main yaml>`

## Build VIND (VIND-bundle)
1. Create the `<repo>/genint-bundle/build` folder
2. Create virtual python env `<repo>/venv` if you do not have one.
   `source ush/setup.sh <repo path> <platform> <compiler>`
3. `cd <repo>/genint-bundle/build`
4. `ecbuild <path/to/genint-bundle>`
5. `make -j <n>`
6. `ctest` to check executables work properly

## Using existing build on Derecho
`/glade/work/swei/Git/JEDI-METplus/genint-bundle/build`  
1. Update `GENINT_BUILD` in `ush/setup.sh` to `/glade/work/swei/Git/JEDI-METplus/genint-bundle/build`
2. `source ush/setup.sh <your/repo/path> derecho gnu`\
   It will create venv for you and point your executables to my build.

## Using existing build on Orion
`/work2/noaa/jcsda/shihwei/git/caliop_opr/genint-bundle/build`  
1. Update `GENINT_BUILD` in `ush/setup.sh` to `/work2/noaa/jcsda/shihwei/git/caliop_opr/genint-bundle/build`
2. `source ush/setup.sh <your/repo/path> orion gnu`\
   It will create venv for you and point your executables to my build.

## Preprocesses for use case of WRF
1. Create air pressure and potential temperature:\
   `ncap2 -O -s "air_potential_temperature=T+300" <wrfout> <new wrfout>`\
   Create `air_potential_temperature` for JEDI application.   
2. Cropping IODA file:\
   Use `pyscripts/get_wrfout_polygon.py` to create a polygon .csv file for your domain boundary.\
   Run `pyscripts/crop_iodafile.py -i <global/IODA/file> -o <WRF/domain/IODA/file> -p <WRF/domain/polygon/csv>`
3. Use `P_HYD` to represent `air_pressure`.\
   The `PSFC` is a diagnostic variable derived through hydrostatic function, so the `air_pressure_levels` based on akbk, ptop, and PSFC are more close to hydrostatic.
   It may cause half level pressure from `PB+P` is not between two adjacent full level.

## Reference links
UFO operators: [JEDI document/UFO](https://jointcenterforsatellitedataassimilation-jedi-docs.readthedocs-hosted.com/en/latest/inside/jedi-components/ufo/index.html)
