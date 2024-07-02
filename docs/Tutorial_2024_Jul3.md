# Quick walkthrough to run on Derecho (July 3, 2024)
Major script: `pyscripts/genint_vrfy.py` \
Usage of genint_vrfy.py \
`genint_vrfy.py <main yaml file>`

## Path of existing build and sample Data
* genint-bundle build: `/glade/work/swei/Git/JEDI-METplus/genint-bundle/build`
* Wx-AQ data: `/glade/derecho/scratch/swei/Dataset/input/bkg/wxaq`
* TropOMI NO2 and CO IODA files: `/glade/derecho/scratch/swei/Dataset/input/obs/ioda_tropomi`
* VIIRS AOD IODA files (cropped to wxaq 4km domain): `/glade/derecho/scratch/swei/Dataset/input/obs/ioda_viirs_aod-wxaq`

## Input and Output of this workflow
Input: Model files and satellite observations
Output: hofx files and MET statistics in ASCII

## Basic idea
This workflow uses JEDI's forward operator to read in satellite observations and model fields to create the simulations (hofx) at observation points by model fields.
Then METplus reads hofx and obs value to calculate the statistics through Model Evaluation Tools (MET).

## Steps to run verification of Wx-AQ with respect to TropOMI NO2
1. `cd <cloned/repo/folder>`
2. `source ./ush/setup.sh <cloned/repo/folder> derecho intel`, and you should see something similar below, 
   ```
   Load modules with <cloned/repo/folder>/modulefiles/setup_derecho_intel.sh
   Loading EWOK-SKYLAB Environment Using Spack-Stack 1.7.0
   The following modules were not unloaded:
   (Use "module --force purge" to unload all):

   1) ncarenv/23.09`
   Create <cloned/repo/folder>/venv
   ```
3. Copy `yamls/main/main_wrfchem.yaml` to `yamls/main.yaml` and modify YAML keys as follow:
   * `build: /glade/work/swei/Git/JEDI-METplus/genint-bundle/build`
   * `obs: /glade/derecho/scratch/swei/Dataset/input/obs/ioda_tropomi`
   * `bkg: /glade/derecho/scratch/swei/Dataset/input/bkg/wxaq`
   * `crtm: /glade/work/swei/Git/JEDI-METplus/genint-bundle/build/crtm/test/testinput`
   * `output: </path/to/your/cloned/repo/output>`
   * `platform: derecho`
   * `jobname: <whatever you like>`
   * `account: UALB0044`
   * `qos: economy`
   * `check_freq: <whatever you like, in second>`
     * YAML key `partition` is not used in PBS jobhead
4. Copy `yamls/hofx3d/hofx3d_lambertCC.yaml` to `yamls/hofx3d_lambertCC.yaml`, and update the hofx3d YAML file as needed (Not required today)
5. `genint_vrfy.py yamls/main.yaml`

## crop IODA file for specific area
1. Create polygon csv first. Wx-AQ polygon is created `etc/polygons/wxaq_polygon.csv`
2.  
