# -*- coding: utf-8 -*-
"""
Created on Tue May 25 16:05:16 2021

@author: Ramon Velazquez

Tesis de Grado 2021 - Ing. Aeronautica FCEFyN - Version comentada

Módulo para la generación de metamodels krg con inputs, casos 3D para WDDIR y WDSPEED.
Funciones para evaluación standalone individual y sobre grillas.
"""

"""
------------------------------------------------------------------------------
Importar
------------------------------------------------------------------------------
"""
import openturns as ot
import numpy as np
import time

"""
------------------------------------------------------------------------------
Funciones
------------------------------------------------------------------------------
"""
def generar_modelo(X, v, mod_opts, **kwargs):
    ''' Función para generar metamodels genérica \n
    inputs:
        X, ndarray - vector muestra de datos indep
        v, ndarray - vector muestra de datos dep
        mod_opts, dict - opciones de generacion
    kwargs puede contener:
    returns:
        KM, KM_data, META obj and info
    '''
    #Defaults
    pr_status = True
    #Lectura opciones
    if 'print_status' in kwargs:
        pr_status = kwargs.get('print_status')
        
    #Inicio
    t_in =  time.time()
    if pr_status:
        print("Iniciando corrida de KRG, t: " + time.asctime(time.localtime(t_in)))
        
    X = ot.Sample(X[:,:mod_opts['dim']])
    v = ot.Sample(v)
    basis = ot.QuadraticBasisFactory(mod_opts['dim']).build()
    covarianceModel = ot.SquaredExponential([mod_opts['scale']])
    algo = ot.KrigingAlgorithm(X,v,covarianceModel,basis)
    algo.run()
    result = algo.getResult()
    KM = result.getMetaModel()
    t_end = time.time()
    t_elapsed = round(t_end-t_in,2)
    if pr_status:
        print("Fin de la corrida KRG, t: "+ time.asctime(time.localtime(t_end)))
        print("Elapsed_time: ", t_elapsed)
    
    KM_data = {'dt':t_elapsed, 'dim': mod_opts['dim'], 'scale':mod_opts['scale']}

    return(KM, KM_data)

def evaluar_modelo(Model, X, mode, **kwargs):
    '''Función para evaluar de manera genérica un META \n
    inputs:
        Model, META obj - Modelo a evaluar
        X, ndarray - Vector de dimension deseada formato (h,lat,lon) segun convencion
        mode, str - Modo de evaluacion 'puntual', 'one_var' (dicts y, z si corresponde)
    kwargs puede contener:
    outputs:
        valor or valor + extra info'''
    
    #Defaults
    out = 'simple'
    
    if mode == 'puntual':
        dim = len(X)
        ret = Model(X)
        if out == 'simple':
            return(ret[0])
        else:
            return('xd')
    
    elif mode == 'one_var':
        res = np.array([])
        dim = 1
        
        if 'y' in kwargs:
            dim += 1
            y_fixed = kwargs.get('y')
            
        if 'z' in kwargs:
            dim += 1
            z_fixed = kwargs.get('z')
        
        ind_ord = np.array([X['tipo'],y_fixed['tipo'],z_fixed['tipo']])
        
        for i in range(len(X['vals'])):
            eval_ord = np.array([X['vals'][i], y_fixed['val'], z_fixed['val']])
            res = np.append(res,Model(eval_ord[ind_ord.argsort()])[0])

        return(res)

def exp_imp_modelo(KM, modo, file_info):
    '''Función para exportar e importar METAs \n
    inputs:
        KM, META - Modelo a guardar
        modo, str - Modo de funcionamiento 'exp' or 'imp' para exportar o importar respectivamente
        filen_info, dict - Opciones para leer/guardar {'folder', 'name', 'prefix'}
    returns:
        para 'imp', META obj leido'''
    
    KM_study = ot.Study()
    s_name = file_info['folder']+'/'+file_info['name']+'.xml'
    KM_study.setStorageManager(ot.XMLStorageManager(s_name))
    
    if modo == 'exp':
        KM_study.add('meta',KM)
        KM_study.save()
        print('META saved')
       
    elif modo == 'imp':
        KM_study.load()
        loc_fun = ot.Function()
        KM_study.fillObject('meta',loc_fun)
        return(loc_fun)
    else:
        raise ValueError('Definir correctamente si exportar o importar')

"""
------------------------------------------------------------------------------
Standalone
------------------------------------------------------------------------------
"""
if __name__ == '__main__':
    pass

    
