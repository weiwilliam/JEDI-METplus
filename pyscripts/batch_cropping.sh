#!/usr/bin/env bash

pyscript='./copy_iodafile.py'

obs_folder='/data/users/swei/Dataset/jedi-data/input/obs'
target='tropomi_no2_tropo-full'
cropped='tropomi_no2_tropo-wxaq'
polygon='/data/users/swei/Git/JEDI/JEDI-METplus/etc/polygons/wxaq_polygon.csv'

for file in `ls ${obs_folder}/$target`
do
  python3 $pyscript -i ${obs_folder}/$target/$file -o ${obs_folder}/$cropped/$file -p $polygon 
done

cd ${obs_folder}/$cropped
rename $target $cropped ${target}*.nc
