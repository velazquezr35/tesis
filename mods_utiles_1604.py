# -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 16:21:33 2021

@author: Ramon Velazquez
"""

#Módulo 3D Kringing con OpenTurns

#importar
import openturns as ot
import numpy as np
import generador_datos_1604 as gen
import matplotlib.pyplot as plt
import OS_module_1604 as OS
plt.rcParams.update({'font.size': 14})
import time
import cartopy.feature as cfeature
import cartopy
import cartopy.crs as ccrs

#Función principal: Generador de input para el modelo de Kringing WS & WD
#########################################################################################

#Generación de input al modelo con los datos del lector de .txt's

def generar_input(lista_nombres,n_dots,data_req,**kwargs):
    
    if "dim" in kwargs:
        dim = kwargs.get("dim")
    else:
        dim = 3
    
    ruta = kwargs.get("ruta")
    h_data = []
    y_data = []
    lat_data = []
    lon_data = []
    n_points = []
    lats = []
    longs = []

    for a in range(len(lista_nombres)):

        loc_h,loc_ws, loc_wd, loc_lat, loc_lon = gen.lector_txt_fixed_size(ruta,lista_nombres[a],n_dots)

        lats.append(loc_lat)
        longs.append(loc_lon)
        
        h_data = np.append(h_data,loc_h)
        
        print(len(loc_h))
        print("largo h_data local")
        print(len(h_data))
        print("------")
        
        if data_req:
            y_data = np.append(y_data, loc_wd)
        else:
            y_data = np.append(y_data, loc_ws)

        n_points = np.append(n_points,len(loc_h))
    
    for i in range(len(lats)):
        lat_data = np.append(lat_data,[lats[i]]*int(n_points[i]))
        lon_data = np.append(lon_data,[longs[i]]*int(n_points[i]))
        
    p1 = np.ones((len(h_data),dim))
    y = np.ones((len(y_data),1))
    p1[:,0] = h_data
    p1[:,1] = lat_data
    p1[:,2] = lon_data
    y[:,0] = y_data
    print("Dimensión input p1")
    print(len(p1))
    print("Tipo: "+str(data_req))
    return(p1,y)


#Otras funciones que nos sirven para análisis intermedios
#########################################################################################


def evaluador_completo_1parametrico(dim,modelo,alt,lat,lon,**args):
    res = []
    var = args.get('var')
    if var == 'alt':
        for a in alt:
            res.append(modelo([a,lat,lon])[0])
        print(var)
        return(res)
    elif var == 'lat':
        for a in lat:
            res.append(modelo([alt,a,lon])[0])
        print(var)
        return(res)
    elif var == 'lon':
        for a in lon:
            res.append(modelo([alt,lat,a])[0])
        print(var)
        return(res)
    else:
        print("Error - Definir correctamente")
        2/0

def evaluar_param_3DMod(IM,alts,lat,lon):   
    res = []
    for a in range(len(alts)):
        res.append(IM([alts[a],lat,lon])[0])
    return(res)

def evaluar_1D(IM,alts):
    res = []
    for a in range(len(alts)):
        res.append(IM([alts[a]])[0])
    return(res)


#Análisis global 1v1 prolijo

def analisis_1D(h_data, y_data, scale):
    start = time.time()
    x = np.ones((len(h_data),1))
    y = np.ones((len(y_data),1))
    x[:,0] = h_data
    y[:,0] = y_data
    
    x = ot.Sample(x)
    y = ot.Sample(y)
    
    dimension = 1
    # basis = ot.QuadraticBasisFactory(dimension).build()
    basis = ot.LinearBasisFactory(dimension).build()
    covarianceModel = ot.SquaredExponential([scale])
    algo = ot.KrigingAlgorithm(x,y,covarianceModel,basis)
    algo.run()
    result = algo.getResult()
    KM = result.getMetaModel()
    end = time.time()
    dt = end-start
    return(KM,dt)

def plotear(h_data,y_data, model_label, name, **args):
        
    fig,ax = plt.subplots(dpi=200)
    ax.plot(h_data,y_data, label = model_label)
    ax.set_xlabel("alt. [m]")
    ax.set_ylabel("WS [m/s]")
    ax.grid()
    
    title_name = name
    
    if "h_raw" in args:
        h_raw, y_raw = args.get("h_raw","y_raw")
        ax.plot(h_raw, y_raw, 'ro', label = 'raw data')
    
    if "cov_scale" in args:
        title_name = title_name + " cov_s = " + args.get("cov_scale")
    
    
    if "dt" in args:
        dt = args.get("dt")
        ax.legend(title=str(round(dt,2))+" [s] elapsed")
    else:
        ax.legend()
    
    fig.suptitle(name)
    if "save" in args:
        if args.get("save"):
            s_name = args.get("carp")+"/"+str(len(h_data))+" puntos - " + args.get("tipo") + " " + args.get("loc")
            plt.savefig(s_name,dpi=200)
    if args.get("close"):
        plt.close()


def exp_imp_meta(analisis,modo,nombre):
    study = ot.Study()
    fileName = nombre+".xml"
    study.setStorageManager(ot.XMLStorageManager(fileName))
    if modo:
        study.add('meta',analisis)
        study.save()
    else:
        study.load()
        loc_f = ot.Function()
        study.fillObject('meta',loc_f)
        return(loc_f)


def plot_estaciones_disp(ruta_files,**kwargs):
    '''Ploteo puntual de las estaciones disponibles en archivo de info especificado'''
    
    #Imports necesarios
    from matplotlib.lines import Line2D
    
    #Info ploteo
    class data_ploteo():
        figtitle = 'Estaciones contenidas en carpeta de data'
        info_label = 'Estaciones con info'
      
    #Subpasos de ploteo y opciones
    
    if "plotclase" in kwargs:
        plotclase = kwargs.get("plotclase")
        data_ploteo = plotclase
    else:
        
        if "label" in kwargs:
            data_ploteo.info_label = kwargs.get("label")
    
        if "figtitle" in kwargs:
            data_ploteo.figtitle = kwargs.get("figtitle")
            
    crs = ccrs.PlateCarree()
    fig, ax = plt.subplots()
    ax = plt.axes(projection=ccrs.PlateCarree())
    
    ax.set_extent([-90, 0, -60, 10]) #Sudamérica
    
    ax.add_feature(cartopy.feature.LAND)
    ax.add_feature(cartopy.feature.OCEAN)
    ax.add_feature(cartopy.feature.COASTLINE)
    ax.add_feature(cartopy.feature.BORDERS, linestyle='dashed')
    ax.add_feature(cartopy.feature.LAKES, alpha=0.5)
    ax.add_feature(cfeature.NaturalEarthFeature(
        'cultural', 'admin_1_states_provinces_lines', '10m',
        edgecolor='gray', facecolor='none'))
    
    loc_listado_est = OS.listar_estaciones(ruta_files) #Esta no considera el archivo global con toda la info, sino una a una
    
    for a in loc_listado_est:
        loc_file = open(ruta_files+"/"+a,'r')
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

        ax.plot(loc_lon,loc_lat,'ro')
    ax.gridlines()
    ax.set_title(data_ploteo.figtitle)
    
    custom_lab = [Line2D([0], [0], marker='o', color='r', label='Scatter')]
    ax.legend(custom_lab, [data_ploteo.info_label])
    plt.show() 

# Rutina para standalone
#########################################################################################

# IF NAME == MAIN:
    
# name_list = ["cba_filt.txt"]

# alts = np.linspace(550,15e3,50)

# for a in name_list:
#     h_a, s_a = gen.llamame_gil(a)
#     MOD, el_tim = analisis_1D(h_a, s_a)
#     res = []
#     for i in range(len(alts)):
#         res.append(MOD([alts[i]])[0])
#     plotear(alts,res,el_tim,a, h_a,s_a)
    

# #2D Análisis

# d_names = ["cba_filt","bom_jesus", "mendoza_filt"]
# d_lats = [22, 220, -50]

# X,y = generar_input(d_names,d_lats)
# modelo_d, ejec_time = analisis_2D(X,y)


# for i in range(0,len(d_lats)):
#     h_loc,y_loc = gen.llamame_gil(d_names[i]+".txt")
#     plotear(alts,evaluar_2D(modelo_d,alts,d_lats[i]),ejec_time,d_names[i]+" 2D - stats: " + str(len(d_names)),h_loc,y_loc)
