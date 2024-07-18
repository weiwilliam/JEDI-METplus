#!/usr/bin/env bash

pyscript='./crop_iodafile.py'
polygon='../etc/polygons/wxaq_polygon.csv'

obs_folder='/glade/derecho/scratch/swei/Dataset/input/obs'
target='tropomi_no2_tropo'
cropped='tropomi_no2_tropo-wxaq'

if [ ! -d $obs_folder/$cropped ]; then 
    mkdir -p $obs_folder/$cropped 
fi

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
