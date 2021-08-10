# -*- coding: utf-8 -*-
"""
Created on Tue May 25 16:05:03 2021

@author: Ramon Velazquez

Tesis de Grado 2021 - Ing. Aeronautica FCEFyN - Version comentada

Módulo principal de los archivos META
"""
"""
------------------------------------------------------------------------------
Importar
------------------------------------------------------------------------------
"""
import META_krg_factory as krg_factory
import META_handler as handler
import META_plots as plots
import os

"""
------------------------------------------------------------------------------
Opciones globales
------------------------------------------------------------------------------
"""
sta_prefix = ['ARM', 'BRM']
sta_folder = 'station_data'
run_folder = 'station_data/run'

"""
------------------------------------------------------------------------------
Standalone
------------------------------------------------------------------------------
"""
if __name__ == '__main__':

    av_files = os.listdir(run_folder)
    av_files = av_files[1]
    X, v = handler.gen_input({'files':av_files,'folder':run_folder},'spd',150)
    KM, data = krg_factory.generar_modelo(X,v,{'dim':1,'scale':0.2})
    krg_factory.exp_imp_modelo(KM, 'exp', {'folder':sta_folder,'name':'test_SPD'})
    
    loc_alt, loc_values,lat, lon = handler.read_station(av_files,run_folder,'spd',150)
    
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots()
    plots.ov_plot(fig,ax,loc_alt,loc_values,'gg','dots')
    
    KM = krg_factory.exp_imp_modelo(0,'imp',{'folder':sta_folder,'name':'test_SPD'})
    
    import numpy as np
    press = np.linspace(20e3,100e3,20)
    
    sps = krg_factory.evaluar_modelo(KM,{'tipo':0,'vals':press},'one_var',y ={'tipo':1,'val':lat},z={'tipo':2,'val':lon})
    
    plots.ov_plot(fig,ax,press,sps,'gg2','normal')