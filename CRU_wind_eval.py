# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 16:17:17 2021

@author: Ramon Velazquez
"""

#WIND MODEL PARA EL CRUCERO
import numpy as np

def wind_eval(WS_model, WD_model, h, lat, lon, head, **kwargs):
    
    '''Input: WS_model, WD_model, h[m], lat [deg], lon [deg], heading from N [deg]\n
       Output: Wproy [m/s] escalada a kwargs.output_scale '''
    
    out_scale = kwargs.get('output_scale')
    loc_WS = WS_model([h,lat,lon])[0]*out_scale
    loc_WD = WD_model([h,lat,lon])[0]
    proy_speed = loc_WS*np.cos(np.deg2rad(loc_WD-head)) #SALIDA EN ft/s
    return(proy_speed, loc_WS, loc_WD)
    