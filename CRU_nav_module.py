# -*- coding: utf-8 -*-
"""
Created on Mon Apr  5 19:23:03 2021
UPDATE 0605 NEW F()

@author: Ramon Velazquez

Tesis de Grado 2021 - Ing. Aeronautica FCEFyN

Modulo de navegacion y calculo de rutas
"""

"""
------------------------------------------------------------------------------
Importar
------------------------------------------------------------------------------
"""
import numpy as np
import cartopy.feature as cfeature
import cartopy
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import pyproj

"""
------------------------------------------------------------------------------
Opciones globales
------------------------------------------------------------------------------
"""
geodesic = pyproj.Geod(ellps='WGS84')

"""
------------------------------------------------------------------------------
Funciones
------------------------------------------------------------------------------
"""

def h_Di(LAT, LON): #AMPLIAR EL TEMA DE LAS ESCALAS Y UNIDADES
    '''
    Funcion que calcula rumbos y distancia para una ruta planteada
    inputs:
        LAT, list - Latitudes
        LON, list - Longitudes
    returns:
        fwd_azi, back_azi - Azimuts delantero y trasero
        distance, distancias entre WP [UNIDADES: ¿?]
    '''
    fwd_azi = np.array([])
    back_azi = np.array([])
    distance = np.array([])
    for i in range(1,len(LAT)):
        loc_fazi, loc_bazi,loc_dist = geodesic.inv(LON[i-1],LAT[i-1],LON[i],LAT[i], radians = False)
        fwd_azi = np.append(fwd_azi,loc_fazi)
        back_azi = np.append(back_azi,loc_bazi)
        distance = np.append(distance,loc_dist*0.000621371) #OJO CON ESTO!
    return(fwd_azi, back_azi,distance)
    
def nav_route(loc_dR, way_D, way_H, LATs, LONs): #OJO CON UNIDADES
    '''Función que devuelve el conjunto (LAT LON HEA) local según un porcentaje de ruta realizada versus la distancia completa
    inputs:
        way_D, narray - Distancias punto a punto (o marks) de la ruta
        way_H, narrray - Headings puto a punto de la ruta
        loc_dR [MI], posicion actual del avion (en distancia) respecto a la longitud total a recorrer
    output:
        actual_LAT, actual_LON, actual_heading'''

    #CHEQUEAR QUE dR SEA EL ACUMULADO
    su_D = np.append([0],np.copy(way_D))
    for i in range(1,len(su_D)):
        su_D[i] = su_D[i] + su_D[i-1] 
    for i in range(len(su_D)):
        if loc_dR >= su_D[i] and loc_dR <= su_D[i+1]:
            act_pos = i
            break
    rel_dist = loc_dR - su_D[act_pos]
    act_LON, act_LAT, act_bw_azi = geodesic.fwd(LONs[act_pos],LATs[act_pos],way_H[act_pos],rel_dist/0.000621371, radians = False)  #OJO CON UNIDADES  
    return(act_LAT, act_LON, way_H[act_pos])

def plot_ruta(LONGs, LATs, **kwargs):
    '''Funcion para el ploteo de rutas mediante Cartopy
    inputs:
        LATs, narray - Latitudes
        LONGs, narray - Longitudes
    kwargs puede contener:
        data_ploteo, dict - Informacion para customizar grafico ['figtitle','info_label']
        keys anteriores por separado, str
    returns: 
        None
    '''
 
    data_ploteo = {'figtitle':'Ploteo de ruta', 'info_label':'Ruta gen'}  
    
    if 'mode' in kwargs:
        mode = kwargs.get('mode')
    else:
        mode = 'clasic_r'
    
    if 'legend_ON' in kwargs:
        legend_ON = kwargs.get('legend_ON')
    else:
        legend_ON = True
    
    if 'title_ON' in kwargs:
        title_ON = kwargs.get('title_ON')
    else:
        title_ON = True
    if 'fig_dpi' in kwargs:
        fig_dpi = kwargs.get('fig_dpi')
    else:
        fig_dpi = 200
    if 'savefig_dpi' in kwargs:
        savefig_dpi = kwargs.get('savefig_dpi')
    else:
        savefig_dpi = 200
    
    if 'ax_extent' in kwargs:
        ax_extent = kwargs.get('ax_extent')
    else:
        ax_extent = 'default'
    if ax_extent == 'auto': #Beta
        mn_lat = min(LATs)
        max_lat = max(LATs)
        mn_lon = min(LONGs)
        max_lon = max(LONGs)
        lat_factor = 20
        lon_factor = 10
        ax_extent = [np.sign(mn_lat)*(abs(mn_lat)+lat_factor),np.sign(max_lat)*(abs(max_lat)+lat_factor),np.sign(mn_lon)*(abs(mn_lon)+lon_factor),np.sign(max_lon)*(abs(max_lon)+lon_factor)]
    
    elif ax_extent == 'USA':
        ax_extent = [-133,-67,10,60]
    elif ax_extent == 'ARG':
        ax_extent = [-32,-85,15,-55]
    else:
        ax_extent = [-179,179,-90,90]
    
    if 'markersize' in kwargs:
        markersize = kwargs.get('markersize')
    else:
        markersize = 2.5
    
    if "plotclase" in kwargs:
        plotclase = kwargs.get("plotclase")
        data_ploteo = plotclase
    else:    
        if "label" in kwargs:
            data_ploteo['info_label'] = kwargs.get("label")
    
        if "figtitle" in kwargs:
            data_ploteo['figtitle'] = kwargs.get("figtitle")
    
    crs = ccrs.PlateCarree()
    if 'figsize' in kwargs:
        fig, ax = plt.subplots(figsize=kwargs.get('figsize'),dpi=fig_dpi)
    else:
       fig, ax = plt.subplots(dpi=fig_dpi) 
    ax = plt.axes(projection=ccrs.PlateCarree())
    if not ax_extent == None:
        ax.set_extent(ax_extent)
    
    ax.add_feature(cartopy.feature.LAND)
    ax.add_feature(cartopy.feature.OCEAN)
    ax.add_feature(cartopy.feature.COASTLINE)
    ax.add_feature(cartopy.feature.BORDERS, linestyle='dashed')
    ax.add_feature(cartopy.feature.LAKES, alpha=0.5)
    ax.add_feature(cfeature.NaturalEarthFeature(
        'cultural', 'admin_1_states_provinces_lines', '10m',
        edgecolor='gray', facecolor='none', linewidth=0.25))

    if "extra_lL" in kwargs:
        extra_LATs = kwargs.get("extra_lL")[1]
        extra_LONGs = kwargs.get("extra_lL")[0]
        ax.plot(extra_LATs, extra_LONGs, 'ro', markersize = markersize, label = 'extra')
    
    if mode == 'clasic_r':
        ax.plot(LATs,LONGs, marker = 'd',markerfacecolor='y', label=data_ploteo['info_label'])#, transform=crs)
        ax.plot(LATs[0],LONGs[0],'ro', label = 'Start point')
        ax.plot(LATs[-1],LONGs[-1],'bo', label = 'End point')
    elif mode == 'discrete_l':
        for loc_lat, loc_lon in zip(LATs, LONGs):
            ax.plot(loc_lat, loc_lon,markersize=markersize, marker = 'o',color = 'r', label=data_ploteo['info_label'], transform=crs)
    if legend_ON:
        ax.legend(fontsize=5, loc = 'upper center', ncol = 3)
    if title_ON:
        ax.set_title(data_ploteo['figtitle'])
    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    if "save" in kwargs:
        if kwargs.get('save'):
            s_name = kwargs.get('ruta') + "/"+  "navplot_" +kwargs.get('filecode')
            plt.savefig(s_name, dpi = savefig_dpi)

    if "close" in kwargs:
        if kwargs.get("close"):
            plt.close()

if __name__ == "__main__":
    '''
    Simple test
    '''
    
    print("Validación de nuevas funciones de navegación")
    lats =  [40.640752, 33.948668]
    longs = [-73.777911, -118.410450]
    print("Latitudes y longitudes ruta")
    print(lats, longs)
    fw_azi, bw_azi, dists = h_Di(lats,longs)
    print(h_Di(lats,longs))
    print(h_Di(np.flip(lats), np.flip(longs)))
    plot_ruta(lats,longs,ax_extent='f')