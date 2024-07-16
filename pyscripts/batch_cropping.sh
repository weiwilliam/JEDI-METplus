#!/usr/bin/env bash

pyscript='./crop_iodafile.py'

obs_folder='/data/users/swei/Dataset/jedi-data/input/obs'
target='tempo_no2_tropo-full'
cropped='tempo_no2_tropo-wxaq'
polygon='/data/users/swei/Git/JEDI/JEDI-METplus/etc/polygons/wxaq_polygon.csv'

for file in `ls ${obs_folder}/${target}`
do
    echo "Cropping $file"
    nobs=`ncdump -h ${obs_folder}/${target}/${file} | grep "Location" | grep UNLIMITED | sed 's/(/ /g' | awk '{print $6}'`
    if [ $nobs != 0 ]; then
        echo "    $nobs available"
        python3 $pyscript -i ${obs_folder}/$target/$file -o ${obs_folder}/$cropped/$file -p $polygon 
    else
        echo "    Skip: no observations available"
        continue
    fi 
done

cd ${obs_folder}/$cropped
rename $target $cropped ${target}*.nc
