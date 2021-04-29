# -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 17:24:37 2021

@author: Ramon Velazquez
"""
#test_evaluador

import META_generador_datos as gen
import META_mods_utiles as mods
import META_main_kringing as krg
import META_OS_module as OS
import numpy as np
import matplotlib.pyplot as plt
import os

main_ruta = "station_data"


def generar_3DMETA(mode):
    '''mode 1 para WD, 0 para WS'''
    
    if mode == 'speed':
        print("Generación META para módulo de velocidad")
        data_req = 0
    elif mode == 'dir':
        print("Generación META para dirección local")
        data_req = 1
    else:
        return("SELECCIONAR speed OR dir")
    
    #parámetros
    cov_scale = 0.5
    #cantidad de lineas per file
    lineas = int(2e3/65)
    
    #archivos
    file = OS.listar_estaciones(main_ruta)
    
    #generamos input
    loc_X,loc_y = mods.generar_input(file,lineas,data_req, dim=3,ruta=main_ruta)
    
    #ejecutamos krg
    loc_model, loc_time = krg.analisis_23D(loc_X,loc_y,3,cov_scale)
    
    alts = np.linspace(1e3,14e3,50)
    
    res = mods.evaluar_param_3DMod(loc_model,alts,-31,-64) #evaluar en cordoba
    
    mods.plotear(alts,res, "test cba", "test")
    return loc_model, loc_time

def test_individual():
    files = OS.listar_estaciones(main_ruta)
    for a in files:
        loc_h, loc_w, lat, lon = gen.lector_txt_fixed_size(main_ruta,a,0)
        if max(loc_h) < 15e3:
            os.replace(main_ruta+"/"+a,"movidos/"+a)
            print(a)
            print("ojo")
            fig,ax = plt.subplots()
            ax.plot(loc_h,loc_w, 'ro')
            fig.suptitle(a)
            s_name = "figuras/"+ a.split(".")[0] + " " + str(len(loc_h))+" puntos"
            plt.savefig(s_name,dpi=200)
            plt.close()
    


    
def comparar(loaded_model):
    alts = np.linspace(1e3,14e3,50)
    res_cba = mods.evaluar_param_3DMod(loaded_model,alts,-31,-64) #evaluar en cordoba
    res_eze = mods.evaluar_param_3DMod(loaded_model, alts, -34.8167,  -58.5333) #ezeiza
    mods.plotear(alts,res_cba, "test cba", "test")
    mods.plotear(alts,res_eze, "test eze", "test")
    
    t_latis = np.linspace(-31,-35,50)
    t_longs = np.linspace(-64,-59,50)
    res_mov = []
    for a in range(50):
        res_mov.append(loaded_model([10e3,t_latis[a],t_longs[a]])[0])
        
    diag = np.sqrt(t_latis**2 + t_longs**2)
    fig,ax = plt.subplots()
    ax.plot(diag,res_mov)
    


def lat_lon_disps(a):
    loc_file = open(main_ruta+"/"+a,'r')
    loc_lines = loc_file.readlines()
    loc_file.close()
    
    try:
        loc_lL = loc_lines[0][55:]
        loc_lat, loc_lon = loc_lL.split()
        loc_lat = float(loc_lat)/1e4
        loc_lon = float(loc_lon)/1e4

    except:
        print(a)
        print("lat lon error on prev to this")
        raise ValueError

    return(loc_lat,loc_lon)

if __name__ == "__main__":
    #Generamos meta del caso para WD
    WD_model, WD_tiempo = generar_3DMETA('dir')







# CORRIDAS VIEJAS
    
    # # modelo, tiempo = test_3D()
    # # save_meta(modelo,1, "salida_full_BR_AR")
    # modelo = mods.exp_imp_meta(0,0,'16_04_wind_models/full_BR_AR')
    
    # import nav_module_2203 as nav
    
    # a,b = nav.calc_pend([-68.31,-54.81],[-51,0.02])
    
    # delR = np.linspace(0,3900,50)
    # R2 = np.linspace(0,2.0592e7,50)
    
    # # rute = np.zeros(50)
    # # lts = np.zeros(50)
    
    
    # longitudes = -54.81 + 54.81/3900 *delR
    # latitudes = -68.31 + 17.31/3900*delR
    # longitudes2 = -54.81 + 54.81/3900 *R2*0.000189394
    # latitudes2 = -68.31 + 17.31/3900*R2*0.000189394
    # vel_ruta = []
    # vel_ruta2 = []
    
    # for i in range(len(delR)):
    #     vel_ruta.append(modelo([30e3/3.28,latitudes[i],longitudes[i]])[0])
    #     vel_ruta2.append(modelo([30e3/3.28,latitudes2[i],longitudes2[i]])[0])
    
    # modelo_importado = cargar()
    
    # fig, ax = plt.subplots()
    # ax.plot(delR,vel_ruta,label='mi')
    # ax.plot(R2,vel_ruta2,label='ft')
    # ax.legend()
    
    
    
    # #Obtener mapa de color
    
    # # h = 10000
    # # n_puntos_graf = 1000
    
    # # lat = np.linspace(-20.3167,-35.5800,n_puntos_graf)
    # # lon = np.linspace(-68,-50,n_puntos_graf)
    
    # # lat, lon = np.meshgrid(lat,lon)
    
    # # resultado = np.ones((n_puntos_graf,n_puntos_graf))
    
    # # for i in range(n_puntos_graf):
    # #     for j in range(n_puntos_graf):
    # #         resultado[i,j] = modelo_importado([h,lat[i,j],lon[i,j]])[0]
    
    # crs = ccrs.PlateCarree()
    # fig, ax = plt.subplots(dpi=100)
    # ax = plt.axes(projection=ccrs.PlateCarree())
    
    # loc_listado_est = OS.listar_estaciones(main_ruta)
    
    
    # ax.set_extent([-90, 0, -60, 10])
    
    # ax.add_feature(cartopy.feature.LAND)
    # ax.add_feature(cartopy.feature.OCEAN)
    # ax.add_feature(cartopy.feature.COASTLINE)
    # ax.add_feature(cartopy.feature.BORDERS, linestyle='dashed')
    # ax.add_feature(cartopy.feature.LAKES, alpha=0.5)
    # ax.add_feature(cfeature.NaturalEarthFeature(
    #     'cultural', 'admin_1_states_provinces_lines', '10m',
    #     edgecolor='gray', facecolor='none'))
    
    # for a in loc_listado_est:
    #     l_lat, l_lon = lat_lon_disps(a)
    #     ax.plot(l_lon,l_lat,'ro')
        
    
    # ax.plot(latitudes,longitudes,label='nav - 3900 [mi]',transform=crs)
    # ax.legend()
    # # tt = plt.pcolor(lon,lat,resultado,transform=crs)
    # # cbar = fig.colorbar(tt, ax=ax)
    # # cbar.ax.set_ylabel('velocidad del viento [m/s]')
    # # ax.set_title('Módulo velocidad del viento, alt = 10e3 [m]')
    # plt.show()
    
    
    
    
    ############### Evaluador de tiempos
    # lats =0
    
        # return(loc_h)
    # def gen_3d(archs,lats,longs):
        
    
    #     cov_scale = 0.2
        
    #     line_points = [200,750, 1500, 3000,7000]
    #     t_points = []
    #     r_points = []
        
    #     ev_lat = lats[0]
    #     ev_lon = longs[0]
        
    #     alts = np.linspace(1e3,14e3,50)
    
    #     for i in range(len(line_points)):
    #             loc_X, loc_y = an.generar_input(archs,line_points[i],lats = lats, longs = longs,dim=3)
    #             loc_model, loc_time = an.analisis_23D(loc_X,loc_y,3,cov_scale)
    #             r_points.append(len(loc_X[:,0]))
    #             t_points.append(loc_time)
    #             res = an.evaluar_param_3DMod(loc_model,alts,ev_lat,ev_lon)
    #             name_2_plot = str(cov_scale) + " - cba 3D"
    #             an.plotear(alts,res, loc_time,name_2_plot,*dat.lector_txt("cba.txt",line_points[i]),save=True,close = "true",carp="figs3d", tipo = "3D s"+str(len(archs)), loc=archs[0])
        
    #     t_plot(r_points,t_points,"figs3d/tc02", stat_n = len(archs))
    #     return(r_points,t_points)
