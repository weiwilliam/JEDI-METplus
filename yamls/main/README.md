## README for main yaml keys
```
run_jedihofx: True
run_met_plus: True
time:
  sdate: 2024011718
  edate: 2024012418
  dateint: 24
genint:
  build: /data/users/swei/Git/JEDI/qxx-genint/build
  jediexec: quenchxx_hofx3d.x
  jediyaml: AOD_hofx3d_lambertCC.yaml
  obsname: v.viirs-m_npp
  bkgname: wrfchem
  simulated_varname: aerosolOpticalDepth
  tracer_name: no2
Data:
  input: 
    obs: '/data/users/swei/Dataset/VIIRS_NPP/ioda_viirs_aod-wxaq'
    bkg: '/data/users/swei/Dataset/Wx-AQ'
    crtm: '/data/users/swei/Git/JEDI/qxx-genint/build/crtm/test/testinput'
  output: /data/users/swei/Git/JEDI/JEDI-METplus/output
  obs_template: wxaq-VIIRS_NPP_%Y%m%d%H.nc
  bkg_template: wrfgsi.out.%Y%m%d%H/wrfout_d01_%Y%m%d_%H0000
metplus:
  verify_fhours: [6]
  met_conf_temp: StatAnalysis.conf_tmpl
  ioda2metmpr: ioda2metplusmpr.py 
jobconf:
  platform: s4
  jobname: qxxgenint_wrfchem
  n_node: 1
  n_task: 1
  walltime: '0:30:00'
  account: star
  partition: s4
  qos: normal
  check_freq: 10
```
* `run_jedihofx:` True: run genint hofx 3D 
* `run_met_plus:` True: run met plus after JEDI hofx 3D finished
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
* `jobconf:`
  * `platform:` platform name: s4, derecho, orion, discover
  * `jobname:` jobname when it submitted
  * `n_node:` number of nodes
  * `n_task:` number of tasks, use 1 for WRF-Chem for now
  * `walltime:` time limit for job
  * `account:` account name, it will be the project ID on Derecho
  * `partition:`  run on which partition if applicable
  * `qos:` queue level, Derecho: premium, regular, or economy*
  * `check_freq:` check frequency for hofx step
