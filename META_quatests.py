# -*- coding: utf-8 -*-
"""
Created on Wed May 26 14:41:02 2021

@author: Ramon Velazquez

Submódulo para tests y pruebas sobre archivos de datos y metamodels
"""

#Librerías
import META_handler as handler
import numpy as np
import os
from skaero.atmosphere import coesa

#Defaults

out_folder = 'station_data/apartados'
glob_log = {'filename':'quatests_log', 'folder':'station_data'}

#Funciones de tests

def station_test(sta,limits, **kwargs):
    '''Función que lee individualmente una estación y determina si sirve para generar modelos. \n
    El principal limitante es el h máx. \n
    [INPUT]: dict sta, 'file', 'folder'. dict limits 'h_lim' c/ cond. de encendido. '''
    #Defaults
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
    '''Función para llevar un seguimiento de la utilidad de las estaciones. Una suerte de white/black list \n
    kwargs for save: filename, fecha, Nsize, hlim, N_over_hlim '''
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
    
#Funciones para la generación de estructuras y condiciones 
def gen_ok_conds(h_lim):
    #Defaults
    h_lim_cond = True
    min_lim_cond = False
    tot_val_cond = False   
    #Gen
    conds = {'h_lim_cond':h_lim_cond,'h_lim_val':h_lim, 'min_lim_cond':min_lim_cond,'tot_val_cond':tot_val_cond}
    return(conds)
    
    
if __name__ == '__main__':
    print('Tests')
    fold = 'station_data/run'
    filelist = os.listdir(fold)
    for file in filelist:
        station_test({'filename':file, 'folder':fold},gen_ok_conds(15e3))
    a = control_report(0,glob_log)