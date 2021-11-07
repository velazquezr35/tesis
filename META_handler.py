# -*- coding: utf-8 -*-
"""
Created on Mon May 24 22:44:59 2021

@author: Ramon Velazquez

Tesis de Grado 2021 - Ing. Aeronautica FCEFyN - Version comentada

Módulo para el manejo general de los distintos files que requiere el eco META.

"""

"""
------------------------------------------------------------------------------
Importar
------------------------------------------------------------------------------
"""
import numpy as np
import igra
import os
import pickle
from skaero.atmosphere import coesa

"""
------------------------------------------------------------------------------
Funciones
------------------------------------------------------------------------------
"""
def determine_files(prefix, folder, **kwargs):
    '''Funcion para determinar los archivos de estaciones disponibles para su uso
    inputs:
        prefix, - Codigo prefijos a usar (paises, zonas)
        folder, str - Carpeta
    kwargs pueden contener:
    returns: des_ind, dict - Indices deseados
    '''
    if not folder in os.listdir():
        os.makedirs(folder)
    
    if not os.listdir(folder) == []:
        for av_files in os.listdir(folder):
            if av_files == 'igra2-station-list.txt':
                print('Archivo de estaciones ya disponible')
                sta_down = False
                break
            else:
                sta_down = True
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

def name_prep(filename, sufix, **kwargs):
    '''
    DOC
    '''
    name = filename[:-len(sufix)]
    return(name)

def read_pos(av_sta, des_sta, **kwargs):
    '''
    DOC
    '''
    if 'mode' in kwargs:
        mode = kwargs.get('mode')
    else:
        mode = 'selective'
    lats = []
    lons = []
    if mode == 'selective':
        for loc_sta in des_sta:
            loc_sta = name_prep(loc_sta, '-data.txt.zip')
            lats.append(av_sta['lat'][loc_sta])
            lons.append(av_sta['lon'][loc_sta])
    elif mode == 'full':
        for loc_sta in av_sta['wmo'].keys():
            lats.append(av_sta['lat'][loc_sta])
            lons.append(av_sta['lon'][loc_sta])
    return(lats,lons)

def prepare_stations(desired, opt_folder, **kwargs):
    '''
    Funcion que comprueba la disponibilidad de archivos en la carpeta local, de modo de evitar re descargarlos
    inputs:
        desired, dict - Archivos posibles de descargar y que requieren verificacion
        opt_folder, str - Carpeta de guardado
    kwargs puede contener:
    returns:
        l_desired, dict - Los que restan
    '''
    #Ver si ya están para ahorrar el download
    av_files = os.listdir(opt_folder)
    l_desired = merge_dict(desired)
    
    for disp_file in av_files:
        for des_ind in l_desired:
            if disp_file[:-13] == des_ind:
                l_desired.pop(l_desired.index(des_ind))
    return(l_desired)

def dwn_stations(required,opt_folder,**kwargs):
    '''
    Funcion que descarga estaciones de IGRA
    inputs:
        required, list - Estaciones requeridas
        opt_folder, str - Carpeta destino
    kwargs puede contener:
    returns: none
    '''
    for r in required:
        igra.download.station(r,opt_folder)

def read_station(fname, folder, data_req, size, **kwargs):
    '''Función que recibe nombre y ubicación de archivo ZIP, asumiendo que ya fue filtrado y está OK.
    inputs: 
        fname-folder - Informacion del archivo a leer
        data_req - Tipo de datos a leer (spd, dir or two)
        size, int - Tamaño a leer / Cantidad de datos
    kwargs puede contener:
    returns: loc_alt, loc_values, lat, lon (segun el indicador data_req)'''
    file_loc = folder+'/'+fname
    print(file_loc)
    
    bulk_data, lects = igra.read.ascii_to_dataframe(file_loc)
    
    loc_alt = np.array([])
    loc_values = np.array([])
    if data_req == 'two':
        loc_values2 = np.array([])
    
    if size == 0:
        size = len(bulk_data)
    print('Size: ', size)
    data_count = 0
    if not data_req == 'latlon':
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
                    elif data_req == 'two':
                        loc_values = np.append(loc_values,bulk_data.winds[data_count])
                        loc_values2 = np.append(loc_values2,bulk_data.windd[data_count])
                    else:
                        return('Error, definir data_req spd or dir')
            data_count += 1

    for i in range(len(lects)):
        if not np.isnan(lects.lat[i]) and not np.isnan(lects.lon[i]):
            lat = lects.lat[i]
            lon = lects.lon[i]
            break
    if data_req == 'latlon':
        return(lat,lon)
    else:
        if data_req == 'two':
            loc_values2 = loc_values2[loc_alt.argsort()]
        loc_values = loc_values[loc_alt.argsort()]
        loc_alt = np.sort(loc_alt)
        if len(loc_alt) == 0:
            raise ValueError('Set vacío. Verificar archivo: ' + fname)
        if data_req == 'two':
            return(loc_alt, loc_values, loc_values2, lat, lon)
        else:
            return(loc_alt, loc_values, lat, lon)

def gen_input(stations_info, data_req, glob_size, **kwargs):
    '''Función para generar el vector input X, v de dim n \n
    inputs:
        station_info, filelist - Informacion de estacion
        data_req, indicador - Tipo de informacion solicitada
        glob_size - Tamaño total del vector muestra
    kwargs puede contener:
    returns:
        X, v vectors para KRG META gen'''
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
        loc_alt = coesa.p_table(loc_alt)
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

def BN_import_export(modo,opt,inp):
    ''' Funcion para leer o guardar archivos BIN con Pickle
    inputs: 
        modo, bool - True para exportar, False para leer
        opt, dict - Opciones (filename, folder)
        inp, objeto - Informacion a guardar
    returns: 
        inp, objeto - Si corresponde al leer'''
    if modo:
        loc_file = open(opt['folder']+"/"+opt['filename'],'wb')
        pickle.dump(inp,loc_file)
        loc_file.close()
        return('data saved')
    else:
        loc_file = open(opt['folder']+"/"+opt['filename'],'rb')
        inp = pickle.load(loc_file)
        loc_file.close()
        return(inp)

def merge_dict(dct):
    '''Funcion para hacer merge de diccionarios
    inputs:
        dct, lista de diccionarios
    returns:
        ret, dct - un unico dict
        '''
    ret = []
    for d in dct:
        for loc in dct[d]:
            ret.append(loc)
    return(ret)

def gen_plot_opts(xlabel,ylabel, save, **kwargs):
    ''' Funcion para la generacion de dicts de opciones para el ploteo
    inputs:
        xlabel, str - Label para eje x
        ylabel, str - Label para eje y
        save, bool - Condicion para guardar imagen
    kwargs puede contener:
    returns: 
        d_plot, dict - Opciones para el ploteo
    '''
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
    if 'fig_title' in kwargs:
        d_plot_opts['fig_title'] = kwargs.get('fig_title')
    return(d_plot_opts)


"""
------------------------------------------------------------------------------
Standalone
------------------------------------------------------------------------------
"""
if __name__ == '__main__':
    
    sta_prefix = ['ARM', 'BRM']
    sta_folder = 'station_data'
    run_folder = 'station_data/run'
    if True: #READ
        av_files = determine_files(sta_prefix,sta_folder)
        dwn_files = prepare_stations(av_files,run_folder)
        dwn_stations(dwn_files,run_folder)
    

