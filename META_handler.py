# -*- coding: utf-8 -*-
"""
Created on Mon May 24 22:44:59 2021

@author: Ramon Velazquez

Versión comentada

Módulo para el manejo general de los distintos files que requiere el eco META.

"""
import numpy as np
import igra
import os
### Funciones para manejo de archivos

def determine_files(prefix, folder, **kwargs):
    for av_files in os.listdir(folder):
        if av_files == 'igra2-station-list.txt':
            print('Archivo de estaciones ya disponible')
            sta_down = False
            break
        else:
            sta_down = True
    if sta_down:
        #Se listan las estaciones disp. en el repo de IGRAA y se descarga
        av_sta = igra.download.stationlist(os.path.abspath(folder))
    else:
        av_sta = igra.read.stationlist(folder+'/igra2-station-list.txt')
    
    des_ind = {}
    for pre in prefix:
        des_ind[pre] = []
    for ind in av_sta.index:
        for pre in prefix:
            if ind[:3] == pre[:3]:
                des_ind[pre].append(ind)
    return(des_ind)

def prepare_stations(desired, opt_folder, **kwargs):
    #Ver si ya están para ahorrar el download
    av_files = os.listdir(opt_folder)
    l_desired = merge_dict(desired)
    
    for disp_file in av_files:
        for des_ind in l_desired:
            if disp_file[:-13] == des_ind:
                l_desired.pop(l_desired.index(des_ind))

    return(l_desired)

def dwn_stations(required,opt_folder,**kwargs):
    for r in required:
        igra.download.station(r,opt_folder)

def read_station(fname, folder, data_req, size, **kwargs):
    '''Función que recibe nombre y ubicación de archivo ZIP.\n
    Se asume que el archivo ya fue filtrado y está OK. \n
    [INPUT] dict file (name, folder), tipo de dato (WDD o WDSP), n lineas INT \n
    [RETURN] 'size' datos con info solicitada, sorted en alt creciente'''
    
    file_loc = folder+'/'+fname
    print(file_loc)
    
    bulk_data, lects = igra.read.ascii_to_dataframe(file_loc)
    
    loc_alt = np.array([])
    loc_values = np.array([])
    
    if size == 0:
        size = len(bulk_data)
    
    data_count = 0
    while len(loc_alt) < size:
        if data_count >= len(bulk_data):
            break
        if not np.isnan([bulk_data.pres[data_count],bulk_data.windd[data_count],bulk_data.winds[data_count]]).any():
            if not bulk_data.pres[data_count] < 0:
                loc_alt = np.append(loc_alt, bulk_data.pres[data_count])
                if data_req == 'spd':
                    if not bulk_data.winds[data_count] < 0:
                        loc_values = np.append(loc_values,bulk_data.winds[data_count])
                elif data_req == 'dir':
                    loc_values = np.append(loc_values,bulk_data.windd[data_count])
                else:
                    return('Error, definir data_req spd or dir')
        data_count += 1

    for i in range(len(lects)):
        if not np.isnan(lects.lat[i]) and not np.isnan(lects.lon[i]):
            lat = lects.lat[i]
            lon = lects.lon[i]
            break
    
    loc_values = loc_values[loc_alt.argsort()]
    loc_alt = np.sort(loc_alt)
    if len(loc_alt) == 0:
        raise ValueError('Set vacío. Verificar archivo')
    return(loc_alt, loc_values, lat, lon)

def gen_input(stations_info, data_req, glob_size, **kwargs):
    '''Función para generar el vector input X, v de dim n \n
    [INPUTS]: Station filelist, tipo de dato spd or dir, size global \n
    [RETURNS]: Vectores X, v para Krg'''
    
    #Defaults
    pr_status = True
    if 'pr_status' in kwargs:
        pr_status = kwargs.get('pr_status')
    if type(stations_info['files'])==str:
        stations_info['files'] = [stations_info['files']]

    #Calc
    ind_size = int(glob_size/len(stations_info['files']))
    alt_data = np.array([])
    values_data = np.array([])
    lat_data = np.array([])
    lon_data = np.array([])
    control_data = {}
    for sta in stations_info['files']:
        loc_alt, loc_values, loc_lat, loc_lon = read_station(sta,stations_info['folder'],data_req,ind_size)
        if len(loc_alt) == len(loc_values):
            n_dots = len(loc_alt)
            control_data[sta] = n_dots
            alt_data = np.append(alt_data,loc_alt)
            values_data = np.append(values_data, loc_values)
            lat_data = np.append(lat_data, n_dots*[loc_lat])
            lon_data = np.append(lon_data, n_dots*[loc_lon])
        else:
            raise ValueError('Size alt y values distintos. Verificar archivo ' + sta)
        
    if pr_status:   
        print('Size vector global: ', len(alt_data))
    
    X = np.append([alt_data],[lat_data],axis=0)
    X = np.append(X, [lon_data], axis = 0)
    X = np.transpose(X)
    v = np.transpose([values_data])
    return(X,v)

###Funciones generales para manejo de estructuras de datos

def merge_dict(dct):
    ret = []
    for d in dct:
        for loc in dct[d]:
            ret.append(loc)
    return(ret)

###Estructuras de datos

def gen_plot_opts(xlabel,ylabel, save, **kwargs):
    '''xlabel, ylabel, save \n
    [RETURN]: dict con opciones para plots
    kwargs: ruta, filecode, grid '''
    d_plot_opts = {'xlabel':xlabel, 'ylabel':ylabel, 'save': bool(save)}
    
    #Defaults
    d_plot_opts['grid'] = True
    d_plot_opts['close'] = False
    if bool(save):
        d_plot_opts['ruta']=kwargs.get('ruta')
        d_plot_opts['filecode'] = kwargs.get('filecode')
    if 'grid' in kwargs:
        d_plot_opts['grid'] = bool(kwargs.get('grid'))
    if 'close' in kwargs:
        d_plot_opts['close'] = bool(kwargs.get('close'))
    return(d_plot_opts)

###Standalone
    
if __name__ == '__main__':
    
    sta_prefix = ['ARM', 'BRM']
    sta_folder = 'station_data'
    run_folder = 'station_data/run'

    read = False
    if read:
        av_files = determine_files(sta_prefix,sta_folder)
        dwn_files = prepare_stations(av_files,run_folder)
        dwn_stations(dwn_files,run_folder)
    

