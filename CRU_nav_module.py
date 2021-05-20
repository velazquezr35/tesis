# -*- coding: utf-8 -*-
"""
Created on Mon Apr  5 19:23:03 2021
UPDATE 0605 NEW F()

@author: Ramon Velazquez
TESIS OPTIMIZACIÓN DE VUELO CRUCERO
"""
import numpy as np
import cartopy.feature as cfeature
import cartopy
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

#UPDATE 06 05
import pyproj
geodesic = pyproj.Geod(ellps='WGS84')

def h_Di(LAT, LON):
    '''salida: dist [mi], fwd_azi [?]'''
    fwd_azi = np.array([])
    back_azi = np.array([])
    distance = np.array([])
    for i in range(1,len(LAT)):
        loc_fazi, loc_bazi,loc_dist = geodesic.inv(LON[i-1],LAT[i-1],LON[i],LAT[i], radians = False)
        fwd_azi = np.append(fwd_azi,loc_fazi)
        back_azi = np.append(back_azi,loc_bazi)
        distance = np.append(distance,loc_dist*0.000621371)
    return(fwd_azi, back_azi,distance)
    
def nav_route(loc_dR, way_D, way_H, LATs, LONs):
    '''Función que devuelva la LAT LON HEA local según % ruta realizada, vs plan \n
    way_D = Array con distancias punto a punto (o marks) de la ruta
    way_H = Array con headings punto a punto de la ruta
    loc_dR [MI] = Posición actual (en distancia) del avión respecto al recorrido total de la ruta \n
    
    OUTPUT: act_LAT, act_LON, way_H[act_pos] '''

#>>CHEQUEAR QUE dR SEA EL ACUMULADO
    su_D = np.append([0],np.copy(way_D))
    for i in range(1,len(su_D)):
        su_D[i] = su_D[i] + su_D[i-1] 
    for i in range(len(su_D)):
        if loc_dR >= su_D[i] and loc_dR <= su_D[i+1]:
            act_pos = i
            break
    rel_dist = loc_dR - su_D[act_pos]
    act_LON, act_LAT, act_bw_azi = geodesic.fwd(LONs[act_pos],LATs[act_pos],way_H[act_pos],rel_dist/0.000621371, radians = False)    
    return(act_LAT, act_LON, way_H[act_pos])

def plot_ruta(LONGs, LATs, **kwargs):
    '''Función para ploteo de rutas \n
    Inputs: LATs, array con latitudes formato . \n
    LONGs, array con longitudes formato . \n
    **kwargs, dict con figtitle e infolabel'''
 
    data_ploteo = {'figtitle':'Ploteo de ruta', 'info_label':'Ruta gen'}  
    if "plotclase" in kwargs:
        plotclase = kwargs.get("plotclase")
        data_ploteo = plotclase
    else:    
        if "label" in kwargs:
            data_ploteo['info_label'] = kwargs.get("label")
    
        if "figtitle" in kwargs:
            data_ploteo['figtitle'] = kwargs.get("figtitle")
    
    crs = ccrs.PlateCarree()
    fig, ax = plt.subplots(dpi=150)
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([-90, 0, -60, 10]) #SudamÃ©rica
    
    ax.add_feature(cartopy.feature.LAND)
    ax.add_feature(cartopy.feature.OCEAN)
    ax.add_feature(cartopy.feature.COASTLINE)
    ax.add_feature(cartopy.feature.BORDERS, linestyle='dashed')
    ax.add_feature(cartopy.feature.LAKES, alpha=0.5)
    ax.add_feature(cfeature.NaturalEarthFeature(
        'cultural', 'admin_1_states_provinces_lines', '10m',
        edgecolor='gray', facecolor='none'))

    if "extra_lL" in kwargs:
        extra_LATs = kwargs.get("extra_lL")[1]
        extra_LONGs = kwargs.get("extra_lL")[0]
        
        ax.plot(extra_LATs, extra_LONGs, 'go', label = 'extra')
        
    ax.plot(LATs,LONGs, marker = 'd',markerfacecolor='y', label=data_ploteo['info_label'], transform=crs)
    ax.plot(LATs[0],LONGs[0],'ro', label = 'Start point')
    ax.plot(LATs[-1],LONGs[-1],'bo', label = 'End point')
    ax.legend()
    ax.set_title(data_ploteo['figtitle'])
    plt.show()
    if "save" in kwargs:
        if kwargs.get('save'):
            s_name = kwargs.get('ruta') + "/"+ kwargs.get('filecode')+ "_navplot"
            plt.savefig(s_name, bbox_inches='tight')

    if "close" in kwargs:
        if kwargs.get("close"):
            plt.close()

if __name__ == "__main__":
    
    print("Validación de nuevas funciones de navegación")
    print("Simulación de ruta USU - EZE - MACA - SANTIAGO")
    
    lats = [-54.8078,0.02589]
    longs = [-68.3021,-51.06]

    print("Latitudes y longitudes ruta")
    print(lats, longs)
    
    fw_azi, bw_azi, dists = h_Di(lats,longs)
    
    print(h_Di(lats,longs))
    print(h_Di(np.flip(lats), np.flip(longs)))
