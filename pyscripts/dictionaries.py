#!/usr/bin/env python3

jedivar_dict = {
    'PM2p5': 'particulatematter2p5Insitu',
    'Ozone': 'ozoneInsitu',
}

# EPA AQI breakpoints 
epa_reg_dict = {
    'PM2p5': ">0&&<=9.,>9&&<=35.4,>35.4",  # 24 hours avg PM2.5 (ug/m3)
    'Ozone': ">0&&<=5.4e-8,>5.4e-8&&<=7e-8,>7e-8", # 8 hour running mean O3 (mol/mol)
}
