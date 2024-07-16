#!/usr/bin/env python3
import sys, os
import pandas as pd
import xarray as xr

hofx_file = sys.argv[1]

if os.path.exists(hofx_file):
    ioda_meta = xr.open_dataset(hofx_file,group='MetaData')
    ioda_hofx = xr.open_dataset(hofx_file,group='hofx')
    
    hofx_vars = list(ioda_hofx.keys())
    
    # use dataframes 
    ioda_df = ioda_meta.to_dataframe()
    ioda_meta.close()        
    
    for var_name in hofx_vars:
        ioda_df[var_name + '@hofx'] = ioda_hofx[var_name]
    
    # Add columns for needed attributes, for each variable present for hofx
    for attribute in ['ObsValue', 'EffectiveQC']:
        ioda_attr = xr.open_dataset(hofx_file, group = attribute)
        for var_name in hofx_vars:
            ioda_df[var_name + '@' + attribute] = ioda_attr[var_name]
    
    ioda_attr.close()
    ioda_hofx.close()
    
    nlocs = len(ioda_df.index)
    print('Number of locations in set: ' + str(nlocs)) 
    
    # Decode strings
    time = list(ioda_df['dateTime'])
    
    for i in range(0,nlocs):        
        temp = pd.to_datetime(time[i],format='%Y-%m-%d %H:%M:%S')
        time[i] = temp.strftime('%Y%m%d_%H%M%S')
        
    ioda_df['datetime'] = time
    
    #set up MPR data
    mpr_data = []
    
    for var_name in hofx_vars:
        
        # Set up the needed columns
        ioda_df_var = ioda_df[['datetime','latitude','longitude',
                            var_name+'@hofx',var_name+'@ObsValue',
                            var_name+'@EffectiveQC']]
        
        # Cute down to locations with valid ObsValues
        ioda_df_var = ioda_df_var[abs(ioda_df_var[var_name+'@ObsValue']) < 1e6] 
        nlocs = len(ioda_df_var.index)
        print(var_name+' has '+str(nlocs)+' valid obs.')
        
        # Add additional columns
        ioda_df_var['lead'] = '000000'
        ioda_df_var['obstype'] = 'NA'
        ioda_df_var['MPR'] = 'MPR'
        ioda_df_var['nobs'] = nlocs
        ioda_df_var['index'] = range(0,nlocs)
        ioda_df_var['varname'] = var_name
        ioda_df_var['vx_mask'] = 'NA'
        ioda_df_var['na'] = 'NA'
    
        # Arrange columns in MPR format
        cols = ['na','na','lead','datetime','datetime','lead','datetime',
                'datetime','varname','na','lead','varname','na','na',
                'obstype','vx_mask','na','lead','na','na','na','na','MPR',
                'nobs','index','na','latitude','longitude',
                'na','na',var_name+'@hofx',var_name+'@ObsValue',
                var_name+'@EffectiveQC','na','na']
        
        ioda_df_var = ioda_df_var[cols]
    
        #ioda_df_var.to_csv('test.out')
        # Into a list and all to strings
        mpr_data = mpr_data + [list( map(str,i) ) for i in ioda_df_var.values.tolist() ]
            
        print("Total Length:\t" + repr(len(mpr_data)))

else:
    print(f"{hofx_file} does not exist")
    sys.exit(1)
