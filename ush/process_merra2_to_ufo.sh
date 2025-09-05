#!/bin/bash -l
#PBS -N process_m2 
#PBS -A UALB0028
#PBS -l select=1:ncpus=4:mem=128GB
#PBS -l walltime=12:00:00
#PBS -q casper
#PBS -j oe
#PBS -V

# --------------------------------------------------------------------------------- 
# This script download MERRA-2 meterological conditions and aerosol mixing ratios
# and combine them for JEDI/UFO/AodCRTM operator.
# This can be run interactively or submitted to PBS system (e.g., NCAR Derecho)
# 

M2_srclink='https://goldsmr5.gesdisc.eosdis.nasa.gov/data/MERRA2'
met_file_cat='M2I3NVASM.5.12.4'
met_file_tag='inst3_3d_asm_Nv'
aer_file_cat='M2I3NVAER.5.12.4'
aer_file_tag='inst3_3d_aer_Nv'
extract_timedim_list="0 2 4 6"

wrktmp=/glade/derecho/scratch/swei/tmp_process_m2
#desdir=/glade/campaign/ncar/nmmm0072/Data/MERRA-2
desdir=/glade/derecho/scratch/swei/Dataset/input/bkg/MERRA-2

sdate=2019072200
edate=2019072300

func_ndate (){
    hrinc=$1
    syear=${2:0:4}
    smon=${2:4:2}
    sday=${2:6:2}
    shr=${2:8:2}

    datein=`date -u --date="$smon/$sday/$syear $shr:00:00"`
    dateout=`date +%Y%m%d%H -u -d "$datein $hrinc hours"`
    echo $dateout
}

[[ ! -d $wrktmp ]] && mkdir -p $wrktmp 
cdate=$sdate
while [ $cdate -le $edate ];
do
  y4=${cdate:0:4}
  m2=${cdate:4:2}
  pdy=${cdate:0:8}
  met_file=MERRA2_400.${met_file_tag}.${pdy}.nc4
  aer_file=MERRA2_400.${aer_file_tag}.${pdy}.nc4
  met_filelink=$M2_srclink/$met_file_cat/$y4/$m2/${met_file}
  aer_filelink=$M2_srclink/$aer_file_cat/$y4/$m2/${aer_file}

  # Download MERRA-2 met and aer data
  cd $wrktmp; rm aer_file.* met_file.*
  if [ ! -s $met_file ]; then
    wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --auth-no-challenge=on --keep-session-cookies --content-disposition $met_filelink
  fi
  if [ ! -s $aer_file ]; then
    wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --auth-no-challenge=on --keep-session-cookies --content-disposition $aer_filelink
  fi
  
  if [ ! -d $desdir/$y4/$m2 ]; then
     mkdir -p $desdir/$y4/$m2
  fi
  # Split the file and combine needed variables
  for t in $extract_timedim_list
  do
    for filetype in "met_file" "aer_file"
    do
      infile=${!filetype}
      hh=$(printf %02i $((t*3)))
      hhfile=$filetype.${pdy}${hh}.nc4
      echo "Extracting $hhfile from $infile"
      ncks -d time,$t,$t $infile $hhfile
    done
    echo "Appending variables to aer_file.${pdy}${hh}.nc4"
    ncks -A -v PL,QV,T met_file.${pdy}${hh}.nc4 aer_file.${pdy}${hh}.nc4

    rc=$?
    [[ $rc -eq 0 ]] && mv aer_file.${pdy}${hh}.nc4 $desdir/$y4/$m2/MERRA2_400.ufo.${pdy}${hh}.nc4
  done

  cdate=`func_ndate 24 $cdate`
done
