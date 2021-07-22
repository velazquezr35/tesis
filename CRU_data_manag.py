# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 16:02:51 2020

@author: Ramon Velazquez

Archivo para guardar / importar datos
"""
import numpy as np
import pickle

def BN_import_export(modo,opt,inp):
    ''' modo 0: cargar resultados \n
        modo 1: exportar resultados'''
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
    ''' modo 1: exportar resultados simples a array .txt \n
        modo 2: importar resultados simples de array .txt \n
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

def deleteContent(fName):
    
    with open(fName, "w"):
        pass
    print("cleared")

###############################################################################################

#Definición de clases/diccionarios para la simulación

###############################################################################################

def gen_iexport_XMLs(ruta,fname):
    '''Opciones de exportar/importar archivos con Pickle'''   
    return({'ruta':ruta,'fname':fname})

def gen_opt_plots(ruta,filecode,status,save,close):
    '''Opciones para ploteo y savefigs con Matplotlib \n
    ruta, filecode, status, b(save), b(close)'''
    return({'ruta':ruta,'filecode':filecode, 'status':status, 'save':bool(save), 'close':bool(close)})


def gen_res_SIM(salida, W_f, h_prof, x_prof, Va_prof, ts_prof, Vw_prof, VD_prof, N, extras, wind_sim):
    if salida == "normal":
        return({'W_f':W_f, 'h_prof':h_prof, 'x_prof':x_prof, 'Va_prof':Va_prof, 'ts_prof':ts_prof,'Vw_prof':Vw_prof, 'VD_prof':VD_prof, 'N':N, 'wind_sim':bool(wind_sim)})

    elif salida == "full":
        return({'extras':extras, 'W_f':W_f, 'h_prof':h_prof, 'x_prof':x_prof, 'Va_prof':Va_prof, 'ts_prof':ts_prof,'Vw_prof':Vw_prof, 'VD_prof':VD_prof, 'N':N, 'wind_sim':bool(wind_sim)})

        
def gen_sim_opciones(tipo, wind, **kwargs):
    ''' Dict para opciones de ejecución del simulador \n
    optimizar = Corrida sin salidas \n
    evaluar = Corrida con salidas \n
    kwargs: pen, plot, output \n
    Opciones por default 1,1,normal
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
    '''Clase para definir inputs'''
    loc_prof_eval = np.zeros((3*N)-3)
    loc_prof_eval[:N-1] = Va_adim
    loc_prof_eval[N-1:2*(N-1)] = ts
    loc_prof_eval[2*(N-1):] = h_adim
    return({'N':N, 'prof_eval':loc_prof_eval})

