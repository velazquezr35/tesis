# -*- coding: utf-8 -*-
"""
Created on Tue May 25 16:05:16 2021

@author: Ramon Velazquez

Módulo para la generación de metamodels krg con inputs, casos 3D para WDDIR y WDSPEED.
Funciones para evaluación standalone individual y sobre grillas.
"""

import openturns as ot
import numpy as np
import time

def generar_modelo(X, v, mod_opts, **kwargs):
    ''' Función para generar metamodels genérica \n
    [INPUT]: X, muestra de datos indep. v, muestra de datos dep. \n
    mod_otps: dict 'dim', 'scale' \n
    [RETURNS]: KM, metamodel. data, dict con info de ejecución.
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
    [INPUT]: Modelo, vector X de dim deseada formato h,lat,lon según convención \n
    mode: 'puntual', 'one_var' (dicts y, z si corresponde)
    [OUTPUT]: Valor o Valor + extra info de OP'''
    
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
    [INPUT]: KM: metamodel modo: 'exp','imp',\n
    file_info: dict 'folder', 'name', 'prefix'
    [RETURNS]: En caso de carga, META'''
    
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

if __name__ == '__main__':
    
    X = {'vals':np.linspace(0,10,10),'tipo':0}
    a = {'val':2, 'tipo':2}
    b = {'val':3, 'tipo':1}
    evaluar_modelo(0,X,'one_var',y=a,z=b)
    
