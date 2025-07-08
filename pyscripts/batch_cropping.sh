#!/usr/bin/env bash

pyhomedir="/glade/work/swei/Git/JEDI-METplus/pyscripts"
pyscript="${pyhomedir}/crop_iodafile.py"
polygon="${pyhomedir}/../etc/polygons/reuires_polygon.csv"

cropped_suffix='ryan'
obs_folder='/glade/derecho/scratch/swei/Dataset/input/obs'
out_folder='/glade/derecho/scratch/swei/Dataset/input/obs/reu-ires'
target_list="tropomi_s5p_co_total" # tropomi_s5p_no2_troposphere viirs_aod_db_n20 viirs_aod_dt_n20"

for target in $target_list
do
    cropped_name="${target}-${cropped_suffix}"
    if [ ! -d $out_folder/$cropped_name ]; then 
        mkdir -p $out_folder/$cropped_name
    fi
    for file in `ls ${obs_folder}/${target}`
    do
        echo "Cropping $file"
        nobs=`ncdump -h ${obs_folder}/${target}/${file} | grep "Location" | grep UNLIMITED | sed 's/(/ /g' | awk '{print $6}'`
        if [ $nobs != 0 ]; then
            echo "    $nobs available"
            python3 $pyscript -i ${obs_folder}/$target/$file -o ${out_folder}/${cropped_name}/${file} -p $polygon 
        else
            echo "    Skip: no observations available"
            continue
        fi 
    done

    cd ${out_folder}/${cropped_name}
    rename $target $cropped_name *${target}*.*

done
