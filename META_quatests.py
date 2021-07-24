# -*- coding: utf-8 -*-
"""
Created on Wed May 26 14:41:02 2021

@author: Ramon Velazquez

Tesis de Grado 2021 - Ing. Aeronautica FCEFyN

Módulo para tests y pruebas sobre archivos de datos y metamodels
"""

"""
------------------------------------------------------------------------------
Importar
------------------------------------------------------------------------------
"""
import META_handler as handler
import numpy as np
import os
from skaero.atmosphere import coesa

"""
------------------------------------------------------------------------------
Opciones globales
------------------------------------------------------------------------------
"""
out_folder = 'station_data/apartados'
glob_log = {'filename':'quatests_log', 'folder':'station_data'}

"""
------------------------------------------------------------------------------
Funciones
------------------------------------------------------------------------------
"""
def station_test(sta,limits, **kwargs):
    '''Filtro sencillo para determinar la utilidad de estaciones
    inputs:
        sta, dict - Informacion de la estacion {'file', 'folder'}
        limits, dict - Filtro {'h_lim', coming soon...}
    kwargs puede contener:
        
    returns:
        none - Cambia de lugar archivo file si corresponde
        '''
    data_req = 'two'
    try:
        bulk_alt, bulk_spd, bulk_dir, lat, lon = handler.read_station(sta['filename'],sta['folder'],data_req,0)
    except:
        return('File not found or read error  - Retry', sta['filename'])
    up_counter = 0
    
    if limits['h_lim_cond']:
        lim_pres = coesa.table(limits['h_lim_val'])[2]
        log_up = bulk_alt < lim_pres
        up_counter += sum(log_up)
    
    if not up_counter:
        print('Archivo para remoción, count h OK: ',up_counter)
        print(sta['filename'])
        os.replace(sta['folder']+'/'+sta['filename'],out_folder+'/'+sta['filename'])
        control_report(True,glob_log, filename=sta['filename'], h_lim = limits['h_lim_val'], N_size = len(bulk_alt), N_over_hlim = up_counter)
        return('Done')

def control_report(modo, log_file, **kwargs):
    '''
    Funcion para llevar un seguimiento de la utilidad de las estaciones, una suerte de white/black lst
    inputs:
        modo, bool - 
        log_gile, 
    kwargs puede contener:
        filename, fecha, Nsize, hlim, N_over_hlim
    returns:
        if not modo, -
    '''
    if modo:
        
        data = {}
        if 'fecha' in kwargs:
            fecha = kwargs.get('fecha')
        else:
            from datetime import date
            fecha = date.today()
        data['fecha'] = fecha
        
        if 'N_size' in kwargs:
            data['N_size'] = kwargs.get('N_size')
        
        if 'h_lim' in kwargs:
            data['h_lim'] = kwargs.get('h_lim')
        if 'N_over_hlim' in kwargs:
            data['N_over_hlim'] = kwargs.get('N_over_hlim')

        glob_data = {kwargs.get('filename'): data}
        handler.BN_import_export(True, log_file, glob_data)
        print('Done')
    
    else:
        return(handler.BN_import_export(False,log_file,0))
    

def gen_ok_conds(h_lim):
    '''
    Funcion para la generacion de estructuras y condiciones (dicts usuales)
    inputs:
        h_lim, float - Limite minimo de altitud deseado
    returns:
        conds, dict - Diccionario que contiene un paquete para el test
    '''
    #Defaults hardcoded
    h_lim_cond = True
    min_lim_cond = False
    tot_val_cond = False   
    #Gen
    conds = {'h_lim_cond':h_lim_cond,'h_lim_val':h_lim, 'min_lim_cond':min_lim_cond,'tot_val_cond':tot_val_cond}
    return(conds)
    
"""
------------------------------------------------------------------------------
Funciones
------------------------------------------------------------------------------
""" 
if __name__ == '__main__':
    '''
    Tests manuales sencillos
    '''
    print('Tests')
    fold = 'station_data/run'
    filelist = os.listdir(fold)
    for file in filelist:
        station_test({'filename':file, 'folder':fold},gen_ok_conds(15e3))
    a = control_report(0,glob_log)