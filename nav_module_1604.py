# -*- coding: utf-8 -*-
"""
Created on Mon Apr  5 19:23:03 2021

@author: Ramon Velazquez
"""
import cartopy.geodesic as c
from shapely.geometry import LineString
import numpy as np
import cartopy.feature as cfeature
import cartopy
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

#Módulo para cálculos y ploteos de rutas

def distancia(latlon):
    '''Función calculadora de distancia WGS84 flattening entre dos puntos \n
    Formato: [LONGITUD, LATITUD] \n
    Salida: [m]'''
    
    #defining the geoid on which to make calculations
    myGeod = c.Geodesic(6378137.0,1 / 298.257223563)
    shapelyObject = LineString(list(latlon))
    return(myGeod.geometry_length(np.array(shapelyObject.coords)))


def plot_ruta(lats, longs, **kwargs):
    class data_ploteo():
        figtitle = 'Ploteo de ruta genérica'
        info_label = 'Ruta genérica'
    '''Función para ploteo de mapa de ruta genérico'''
    
    crs = ccrs.PlateCarree()
    fig, ax = plt.subplots(dpi=100)
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
    
    #Subpasos de ploteo y opciones
    
    if "plotclase" in kwargs:
        plotclase = kwargs.get("plotclase")
        data_ploteo = plotclase
    else:
        
        if "label" in kwargs:
            data_ploteo.info_label = kwargs.get("label")
    
        if "figtitle" in kwargs:
            data_ploteo.figtitle = kwargs.get("figtitle")

    ax.plot(lats,longs, label=data_ploteo.info_label, transform=crs)
    ax.plot(lats[0],longs[0],'ro', label = 'Start point')
    ax.plot(lats[-1],longs[-1],'bo', label = 'End point')
    ax.legend()
    ax.set_title(data_ploteo.figtitle)
    plt.show()

def calc_pend(d1,d2):
    a = (d2[1]-d1[1]*d2[0]/d1[0])/(1-d2[0]/d1[0])
    b = (d1[1]-a)/d1[0]
    return(a,b)

if __name__ == "__main__":

    latlon = [(-68.31591,-54.81084), (-51.06639,0.03889)]
    dist = distancia(latlon)
    
    delR = np.linspace(0,3900,50)
    R2 = np.linspace(0,2.0592e7,50)
    longitudes = -54.81 + 54.81/3900 *delR
    latitudes = -68.31 + 17.31/3900*delR
    
    plot_ruta(latitudes,longitudes)