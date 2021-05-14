# -*- coding: utf-8 -*-
"""
Created on Thu Mar 25 14:24:52 2021

@author: Ramon Velazquez
"""

#Módulo de manejo de archivos para análisis de viento

#Funciones útiles para listar lo que se necesite, con info y datos

import os

#Lector filtrador comparador de estaciones disponibles en el listado de base
def LFC_archivos(ruta):
    loc_fl_lines = open(ruta+"/igra2-station-list.txt",'r')
    loc_fl_list = loc_fl_lines.readlines()
    loc_fl_lines.close()
    loc_fl_arr = []
    for a in loc_fl_list:
        loc_fl_arr.append(a.split())
    return(loc_fl_arr)

#Listador de estaciones disponibles en la ruta, nombres código IGRAA
def listar_estaciones(ruta):
    loc_stat_list = os.listdir(ruta) #listamos archivos disponibles en la ruta
    if 'igra2-station-list.txt' in loc_stat_list:
        loc_stat_list.remove('igra2-station-list.txt') #eliminamos el índice
    return(loc_stat_list) #devolvemos lo que nos interesa, los nombres


if __name__ == "__main__":
    print(listar_estaciones("station_data"))