# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 16:02:51 2020

@author: Ramon Velazquez

Tesis de Grado 2021 - Ing. Aeronautica FCEFyN

Modulo de exportacion e importacion de datos y tratamiento de archivos
"""

"""
------------------------------------------------------------------------------
Importar
------------------------------------------------------------------------------
"""
import numpy as np
import pickle

"""
------------------------------------------------------------------------------
Funciones
------------------------------------------------------------------------------
"""
###############################################################################################
#Funciones base
###############################################################################################

def BN_import_export(modo,opt,inp):
    '''
    Funcion basica para exportar o importar resultados mediante Pickle
    inputs:
        modo, bool - False para carga de resultados, True para exportar resultados
        opt, dict - Opciones de archivo ['ruta','filename']
        inp, obj - Objeto a exportar (solo necesario @modo True)
    returns:
        inp, obj - Objeto importado @modo False
    ''' 
    if modo:
        loc_file = open(opt['ruta']+"/"+opt['filename'],'wb')
        pickle.dump(inp,loc_file)
        loc_file.close()
        return('data saved')
    else:
        loc_file = open(opt['ruta']+"/"+opt['filename'],'rb')
        inp = pickle.load(loc_file)
        loc_file.close()
        return(inp)

    
def BASIC_save_read_data(modo, arr, opt):
    '''
    Funcion basica para exportar o importar arrays mediante archivos .txt
    inputs:
        modo, bool - False para carga, True para exportar
        arr, ndarray or list - Informacion a guardar
        opt, dict - Opciones de archivo ['ruta','filename']
    returns:
        array, ndarray or list - Informacion importada @modo False
    '''
    if modo != 0 or modo != 1:
        raise NameError('Elegir correctamente MODO: 0, read or 1, save')
    if modo:
        save_1 = open(opt['ruta']+"/"+opt['filename']+".txt", "w")
        for a in range(len(arr)):
            save_1.writelines(str(arr[a]))
            save_1.write('\n')
        save_1.close()
        print("Data saved, fname: ", opt['filename'])
    else:
        op_1 = open(opt['ruta']+"/"+opt['filename']+".txt", "r")
        lineas = op_1.readlines()
        for a in range(len(lineas)):
            lineas[a] = lineas[a].replace('\n','')
    
        values = np.zeros(len(lineas))
        for i in range(len(lineas)):
            values[i] = float(lineas[i])
        op_1.close()
        return(values)

def deleteContent(opt):
    '''
    Funcion basica para eliminar contenido de un archivo tipo txt o similar
    inputs:
        opt, dict - Opciones de archivo ['ruta','filename']
    returns:
        None        
    '''
    with open(opt['ruta']+"/"+opt['filename'], "w"):
        pass
    print("cleared")
    return()

###############################################################################################
#Definición de clases/diccionarios para la simulación
###############################################################################################

def gen_iexport_XMLs(ruta,fname):
    '''
    Funcion para la generacion de un dict con opciones necesarias para exportar/importar archivos mediante Pickle
    inputs:
        ruta, str - Folder a guardar / leer
        fname, str - Nombre de archivo a guardar / leer
    returns:
        dict - otp style para funciones que importan / exportan 
    ''' 
    return({'ruta':ruta,'fname':fname})

def gen_opt_plots(ruta,filecode,status,save,close):
    '''
    Funcion para la generacion de un dict con opciones necesarias para la configuracion de ploteo y savefigs de Matplotlib
    inputs:
        ruta, str - Folder a guardar los plots
        filecode, str - Codigo principal de los plots (no es igual al nombre final)
        status, bool - ¿?
        save, bool - True para guardar las imagenes, False para no
        close, bool - True para cerrar las imagenenes y prevenir apilamiento de ventanas (usar con save)
    returns:
        dict - Con toda la informacion anterior de input
    '''
    return({'ruta':ruta,'filecode':filecode, 'status':status, 'save':bool(save), 'close':bool(close)})


def gen_res_SIM(salida, W_f, h_prof, x_prof, Va_prof, ts_prof, Vw_prof, VD_prof, N, extras, wind_sim):
    '''
    Funcion para la generacion de un dict con los perfiles de variables de interes del simulador
    inputs: 
        salida, str - 'normal' para perfiles sin variables extras, 'full' para un output completo
        W_f, float - peso final del vuelo
        h_prof, narray - perfil de altitudes
        x_prof, narray - perfil de steps de distancia
        Va_prof, narray - perfil de velocidades aerodinamicas
        ts_prof, narray - perfil de mandos de gas
        VW_prof, narrray - perfil de velocidades (magnitudes) de viento local
        VD_prof, narray - perfil de direcciones de viento local
        N, float - M+1 segmentos considerados
        extras, dict - informacion adicional
        wind_sim, bool - True para simulaciones que consideren el efecto del viento
    returns:
        dict - Con toda la informacion anterior de input, segun tipo definido mediante 'salida'
    '''
    if salida == "normal":
        return({'W_f':W_f, 'h_prof':h_prof, 'x_prof':x_prof, 'Va_prof':Va_prof, 'ts_prof':ts_prof,'Vw_prof':Vw_prof, 'VD_prof':VD_prof, 'N':N, 'wind_sim':bool(wind_sim)})

    elif salida == "full":
        return({'extras':extras, 'W_f':W_f, 'h_prof':h_prof, 'x_prof':x_prof, 'Va_prof':Va_prof, 'ts_prof':ts_prof,'Vw_prof':Vw_prof, 'VD_prof':VD_prof, 'N':N, 'wind_sim':bool(wind_sim)})

        
def gen_sim_opciones(tipo, wind, **kwargs):
    '''
    Funcion para la generacion de opciones de ejecucion del simulador de crucero
    inputs:
        tipo, str - 'optimizar' para corridas de optimizacion, 'evaluar' para corridas de evaluacion
        wind, bool - True para corridas que consideren el viento
    kwargs puede contener:
        pen, bool - True para penalizacion, default True
        plot, bool - True para ploteo de resultados, default False
        output, str - tipo de salida de inforrmacion, default 'normal'
    '''
    if tipo == 'optimizar':
        return({'pen_flag':'none', 'wind_sim':bool(wind),'output':'only','plot':False})
    elif tipo == 'evaluar':
            pen_flag = True
            plot = False
            output = "normal"
            if 'pen' in kwargs:
                pen_flag = kwargs.get('pen')
            if 'plot' in kwargs:
                plot = kwargs.get('plot')
            if 'output' in kwargs:
                output = kwargs.get('output')   
            return({'pen_flag':pen_flag, 'wind_sim':bool(wind), 'output':output, 'plot':bool(plot)})

def gen_input_profile(N, Va_adim, ts, h_adim):
    '''Funicion para la generacion de perfiles de entrada para la funcion de simulacion de crucero
    inputs:
        N, int - Numero de puntos extremo de segmentos (M = N-1)
        Va_adim, narray or float - Velocidades aerodinamicas
        ts, narray or float - Posiciones del mando de gas
        h_adim, narray or float - Altitudes
        NOTA: Utilizar adimensionalizacion compatible
    returns:
        profile, dict {'N':N,'prof_eval':array_variables}'''
    loc_prof_eval = np.zeros((3*N)-3)
    loc_prof_eval[:N-1] = Va_adim
    loc_prof_eval[N-1:2*(N-1)] = ts
    loc_prof_eval[2*(N-1):] = h_adim
    return({'N':N, 'prof_eval':loc_prof_eval})

