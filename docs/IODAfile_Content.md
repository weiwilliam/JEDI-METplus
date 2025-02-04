## IODA file contents ##
A IODA file typically has following contents:\
Groups:
  - *MetaData:* dateTime, latitude, longitude
  - *ObsValue, ObsError, and PreQC:* [variableName] (e.g., aerosolOpticalDepth)
  - *hofx, EffectiveError, and EffectiveQC:* Similar to above. Normally, it will be added after running JEDI hofx appilication.

### Example of a IODA file ###
```
netcdf viirs_db_npp_aod.2018080818 {
dimensions:
        Channel = 1 ;
        Location = UNLIMITED ; // (315992 currently)
variables:
        int Channel(Channel) ;
                Channel:suggested_chunk_dim = 1LL ;
        int64 Location(Location) ;
                Location:suggested_chunk_dim = 10000LL ;

// global attributes:
                string :_ioda_layout = "ObsGroup" ;
                :_ioda_layout_version = 0 ;
                string :ioda_object_type = "AOD" ;
                string :retrievalMethod = "DeepBlue" ;
                string :platform = "suomi_npp" ;
                string :sensor = "v.viirs-m_npp" ;
                string :errorMethod = "Pixel-level Uncertainty Estimates (PUE)" ;
                string :datetimeRange = "2018-08-08T15:12:00Z", "2018-08-08T20:24:00Z" ;

group: MetaData {
  variables:
        int64 dateTime(Location) ;
                dateTime:_FillValue = -9223372036854775806LL ;
                string dateTime:units = "seconds since 1970-01-01T00:00:00Z" ;
        float latitude(Location) ;
                latitude:_FillValue = 9.96921e+36f ;
                string latitude:units = "degrees_north" ;
        float longitude(Location) ;
                longitude:_FillValue = 9.96921e+36f ;
                string longitude:units = "degrees_east" ;
  } // group MetaData

group: ObsError {
  variables:
        float aerosolOpticalDepth(Location, Channel) ;
                aerosolOpticalDepth:_FillValue = 9.96921e+36f ;
                string aerosolOpticalDepth:coordinates = "longitude latitude" ;
                string aerosolOpticalDepth:units = "1" ;
  } // group ObsError

group: ObsValue {
  variables:
        float aerosolOpticalDepth(Location, Channel) ;
                aerosolOpticalDepth:_FillValue = 9.96921e+36f ;
                string aerosolOpticalDepth:coordinates = "longitude latitude" ;
                string aerosolOpticalDepth:units = "1" ;
  } // group ObsValue

group: PreQC {
  variables:
        int aerosolOpticalDepth(Location, Channel) ;
                aerosolOpticalDepth:_FillValue = -2147483647 ;
                string aerosolOpticalDepth:coordinates = "longitude latitude" ;
  } // group PreQC
}
```
