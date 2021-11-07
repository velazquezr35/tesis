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
import igra
import numpy as np
import CRU_nav_module as nav

"""
------------------------------------------------------------------------------
Opciones globales
------------------------------------------------------------------------------
"""
sta_prefix = ['BRM', 'ARM']
sta_folder = 'station_data'
run_folder = 'station_data/run'

"""
------------------------------------------------------------------------------
Standalone
------------------------------------------------------------------------------
"""
if __name__ == '__main__':
    
    if True:
        av_files = os.listdir(run_folder) #Leer archivos disponibles
        loc_pos = []
        av_sta = igra.read.stationlist(sta_folder+'/igra2-station-list.txt')
        lats, lons = handler.read_pos(av_sta, av_files, mode = 'selective')
        extra_LATS = [
-11.0333, -14.8167,
-16.5170,
-17.8000,
-18.3167,
-17.3800,
-10.8200,
-14.4500,
-22.0300,
-22.0167,
-25.2333]
        extra_LONS = [
-68.7833,
-64.9167,
-68.1830,
-63.1833,
-59.7667,
-66.1700,
-65.3700,
-67.5300,
-63.6800,
-60.6167,
-57.5167]
        
        nav.plot_ruta(lats, lons, mode='discrete_l', extra_lL = [extra_LATS, extra_LONS],markersize=2.5,ax_extent = 'ARG', legend_ON = False, title_ON=False, save =True, ruta = sta_folder, filecode='ARBRA', savefig_dpi = 300)
    
    if False: #Generar modelo
        av_files = os.listdir(run_folder)
        X, v = handler.gen_input({'files':av_files,'folder':run_folder},'spd',5e3)
        KM, data = krg_factory.generar_modelo(X,v,{'dim':3,'scale':0.2})
        krg_factory.exp_imp_modelo(KM, 'exp', {'folder':sta_folder,'name':'ARBRA_SPD_3d_5e3'})
        
        X, v = handler.gen_input({'files':av_files,'folder':run_folder},'dir',5e3)
        KM, data = krg_factory.generar_modelo(X,v,{'dim':3,'scale':0.2})
        krg_factory.exp_imp_modelo(KM, 'exp', {'folder':sta_folder,'name':'ARBRA_DIR_3d_5e3'})
        
    if False:
        loc_alt, loc_values,lat, lon = handler.read_station(av_files,run_folder,'spd',150)
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots()
        plots.ov_plot(fig,ax,loc_alt,loc_values,'gg','dots')
        
        KM = krg_factory.exp_imp_modelo(0,'imp',{'folder':sta_folder,'name':'test_SPD'})
        
        press = np.linspace(20e3,100e3,20)
        
        sps = krg_factory.evaluar_modelo(KM,{'tipo':0,'vals':press},'one_var',y ={'tipo':1,'val':lat},z={'tipo':2,'val':lon})
        
        plots.ov_plot(fig,ax,press,sps,'gg2','normal')