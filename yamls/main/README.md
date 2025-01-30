## README for main yaml keys
```
run_jedihofx: True
run_met_plus: False
restart: False
verbose: False
time:
  sdate: 2024082211
  edate: 2024082211
  dateint: 1 
genint:
  build: /work2/noaa/jcsda/shihwei/git/JEDI-METplus/genint-bundle/build 
  jediexec: quenchxx_hofx3d.x
  jediyaml: hofx3d_lambertCC.yaml
  obsname: tempo_no2_tropo
  bkgname: wrfchem
  simulated_varname: nitrogendioxideColumn
  tracer_name: volume_mixing_ratio_of_no2
Data:
  input: 
    obs: '/work2/noaa/jcsda/shihwei/data/jedi-data/input/obs/tempo_no2_tropo-wxaq'
    bkg: '/work2/noaa/jcsda/shihwei/data/jedi-data/input/bkg/wxaq'
    crtm: '/work2/noaa/jcsda/shihwei/data/crtm_fix'
  output: /work2/noaa/jcsda/shihwei/git/JEDI-METplus/output
  obs_template: obs.tempo_no2_tropo-wxaq.%Y%m%d%H.nc4
  obs_window_length: 1
  bkg_template: wrfgsi.out.{init_date}/subset_wrfout_d01_%Y%m%d_%H0000
  bkg_extension: .nc
  bkg_init_cyc: ['00']
jobconf:
  platform: orion
  jobname: qxxgenint_wrfchem
  n_node: 1
  n_task: 1
  account: da-cpu
  partition: orion
  walltime: 0:30:00
  qos: batch
  check_freq: -1
  memory: '112000M'
metplus:
  verify_fhours: [7,8,9,10,11,12,13,14,15,16,17,18,19]
  met_conf_temp: StatAnalysis.conf_tmpl
  ioda2metmpr: ioda2metplusmpr.py 
  mask_by: 'ObsValue<1e6'
  submit: False
```
* `run_jedihofx:` True: run genint hofx 3D 
* `run_met_plus:` True: run met plus after JEDI hofx 3D finished
* `restart`: True: no folder purging
* `verbose`: True: print out more information
* `time:`
  * `state:` first cycle (10-digit)
  * `edate:` last cycle (10-digit)
  * `dateint:` interval of each cycle (in hour)
* `genint:`
  * `build:` build path of genint-bundle
  * `jediexec:` the executable to use
  * `jediyaml:` yaml file for genint application
  * `obsname:` Name of observation, used to create output folder (obsname_bkgname)
  * `bkgname:` Name of target model, used to create output folder
  * `simulated_varname:` simulated variable name used in JEDI,
    * List: aerosolOpticalDepth, nitrogendioxideTotal, nitrogendioxideColumn, carbonmonoxideTotal
  * `tracer_name:` long name for trace gas (e.g., volume_mixing_ratio_of_no2, volume_mixing_ratio_of_co)
* `Data:`
  * `input:` the last level of path under input will be linked to Data/input/<key>
    * `obs:` observation folder, linked to workdir/Data/input/obs 
    * `bkg:` background folder, linked to workdir/Data/input/bkg
    * `crtm:` CRTM coefficient folder, linked to workdir/Data/input/crtm
  * `output:` output path, will be linked to workdir/Data/output
  * `obs_template:` obs file template, will be parsed by cdate.strptime
  * `bkg_template:` bkg file template (please include any level with date info), will be parsed by cdate.strptime
* `metplus:`
  * `verify_fhours:` List of forecast hours for verification
  * `met_conf_temp:` stat_analysis template
  * `ioda2metmpr:` python script to read IODA hofx file and provide matched paired dataset to METplus for statistics calculation
  * `mask_by`: use the group of IODA to keep data points satisfied the condition for METplus calculation
  * `submit`: True or False to run METplus on compute node or local, if it is true, please include the jobconf yaml keys under metplus section.
* `jobconf:`
  * `platform:` platform name: s4, derecho, orion, discover
  * `jobname:` jobname when it submitted
  * `n_node:` number of nodes
  * `n_task:` number of tasks, use 1 for WRF-Chem for now
  * `walltime:` time limit for job
  * `account:` account name, it will be the project ID on Derecho
  * `partition:`  the partition to be submitted, Derecho: main or develop (shared job, cheaper in core hour)
  * `qos:` queue level, Derecho: premium, regular, or economy*
  * `check_freq:` check frequency for hofx step

Derecho Core hour calculation: https://ncar-hpc-docs.readthedocs.io/en/latest/pbs/charging/#exclusive-nodes
