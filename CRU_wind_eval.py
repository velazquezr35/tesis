# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 16:17:17 2021

@author: Ramon Velazquez

Tesis de Grado 2021 - Ing. Aeronautica FCEFyN

Modulo de evaluacion de modelos de viento
"""

"""
------------------------------------------------------------------------------
Importar
------------------------------------------------------------------------------
"""
import numpy as np

"""
------------------------------------------------------------------------------
Funciones
------------------------------------------------------------------------------
"""
def wind_eval(WS_model, WD_model, h, lat, lon, head, **kwargs):
    '''
    Funcion para la evaluacion de modelos de viento y posterior determinacion de la componente local
    inputs:
        WS_model, META - modelo de magnitud
        WD_model, META - modelo de direccion
        h, float - altitud en unidades [m]
        lat, float - latitud en grados [deg]
        lon, float - longitud en grados [deg]
        head, float - heading desde el norte en grados [deg]
    kwargs puede contener:
        output_scale, float - factor de conversion de velocidad
    returns:
        proy_speed, float - velocidad proyectada
        loc_WS, float - magnitud de la velocidad (sin proyectar)
        loc_WD, float - direccion de la velocidad
        '''
    if 'output_scale' in kwargs:
        output_scale = kwargs.get('output_scale')
    else:
        output_scale = 1
    loc_WS = WS_model([h,lat,lon])[0]*output_scale
    loc_WD = WD_model([h,lat,lon])[0]
    proy_speed = loc_WS*np.cos(np.deg2rad(loc_WD-head)) #SALIDA EN ft/s
    return(proy_speed, loc_WS, loc_WD)
    