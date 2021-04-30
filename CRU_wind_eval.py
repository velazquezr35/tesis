# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 16:17:17 2021

@author: Ramon Velazquez
"""

#WIND MODEL PARA EL CRUCERO
import numpy as np

def wind_eval(WS_model, WD_model, h, lat, lon):
    
    '''WS_model, WD_model, h, lat, lon \n
    Salida en FT/S '''
    
    #Evaluamos la velocidad del viento local
    loc_WS = WS_model([h,lat,lon])[0]*3.28 #m/s to ft/s
    #Evaluamos la dirección del viento local
    loc_WD = WD_model([h,lat,lon])[0]
    
    latlon = [(-68.31591,-54.81084),(-51.06639,0.03889)]
    
    op = latlon[1][1] - latlon[0][1]
    ad = latlon[1][0] - latlon[0][0]
    angle = np.arctan(ad/op)
    
    N_angle = np.degrees(angle)    
    delta_alfa = loc_WD - N_angle

    proy_speed = loc_WS*np.cos(np.deg2rad(delta_alfa)) #SALIDA EN 
    # print(loc_WS, proy_speed)
    # print(proy_speed, loc_WS, loc_WD)
    # print(proy_speed, np.cos(np.deg2rad(delta_alfa)), loc_WS, loc_WD-N_angle, loc_WD)   
    return(proy_speed, loc_WS, loc_WD)
    