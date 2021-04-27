# -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 16:09:26 2021

@author: Ramon Velazquez
"""

#Archivo de generación de datos de entrada al modelo de Kg

import numpy as np
import matplotlib.pyplot as plt

def lector_txt_fixed_size(file,n_dots, **kwargs):
    ''' Función de lectura de archivos.
    Inputs: archivo (nombre), n lineas a leer, kwargs plot y print'''
    
    #Seteo de opciones de ejecución
    pr_status = False
    class plot_data:
        status = False

    if 'full_print' in kwargs:
        pr_status = kwargs.get('full_print')

    if 'plot_data' in kwargs:
        plot_data = kwargs.get('plot_data')
    
    if pr_status:
        print("Lector de archivos txt")
        print("Modo full output")
        print(" ")
    
    data_lect = open(str(file.ruta)+"/"+file.name,"r")
    lineas = data_lect.readlines()
    
    if n_dots == 0:
        size = int(len(lineas))
        print("Análisis con archivo completo")
    else:
        size = n_dots
        
    data_lect.close()
    arr_gmd = []
    
    try:
        l_L_line = lineas[0][55:]
        lat, lon = l_L_line.split()
        lat = float(lat)/1e4
        lon = float(lon)/1e4
        
        if pr_status:
            print(" ")
            print("Latitud y longitud de la estación leída:")
            print(lat)
            print(lon)

    except:
        print(file.name)
        print("lat lon error on prev to this")
        raise ValueError
        
    data_counter = 0
    
    if pr_status:
        print("Size del archivo leído")
        print(len(lineas))
        
    for a in range(len(lineas)):
        if lineas[a][0] != "#":
            loc_one = float(lineas[a][46:51])/10
            loc_zero = float(lineas[a][16:21])
            loc_two = float(lineas[a][40:45])
            loc_arr = np.array([loc_zero,loc_one,loc_two])
            #filtrado
            if not any(x<0 for x in loc_arr) and not loc_arr[0]>18e3:
                arr_gmd.append(loc_arr) #lo tengo como lista
                data_counter = data_counter + 1
            if data_counter == size and not n_dots == 0:
                print("archivo finalizado")
                break
    print(file.name)
    arr_gmd = np.array(arr_gmd)

    arr_gmd = arr_gmd[arr_gmd[:,0].argsort()] #ordenar en orden creciente eje alts
    if pr_status:
        print("First")
        print(arr_gmd)
        print("Ahora, ordenado")
        print(arr_gmd)
        
    if plot_data.status:
        fig, ax = plt.subplots()
        ax.plot(arr_gmd[:,0],arr_gmd[:,1], 'ro', label = 'Velocidad viento')
        ax.set_xlabel("Alt. de cálculo [m]")
        ax.set_ylable("Wind Speed [m/s]")
        ax.set_title("Estación " + file.name + " - plot h vs WS")
        ax.legend()
        ax.grid()
        
        fig, ax = plt.subplots()
        ax.plot(arr_gmd[:,0],arr_gmd[:,1], 'ro', label = 'Velocidad viento')
        ax.set_xlabel("Alt. de cálculo [m]")
        ax.set_ylable("Wind Speed [m/s]")
        ax.set_title("Estación " + file.name + " - plot h vs WS")
        ax.legend()
        ax.grid()
        
        #if plot_data.save:
            #Guardar
        # if plot_data.closefigs:
        #     fig.close()
        
    return arr_gmd[:,0],arr_gmd[:,1], arr_gmd[:,2], lat, lon


if __name__ == "__main__":
    print("Por favor cargar archivo a leer para la info")