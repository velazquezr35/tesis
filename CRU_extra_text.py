# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 16:02:51 2020

@author: Ramon Velazquez

Archivo para guardar / importar datos
"""
import numpy as np

def export_otop(output, ruta, name):
    #Incluir pickle
    pass
    
def save_data(arr, name):

    save_1 = open(str(name)+".txt", "w")
    
    for a in range(0, len(arr)):
        save_1.writelines(str(arr[a]))
        save_1.write('\n')

    save_1.close()
    print("Data saved")


def readata(name):
    leer = open(str(name)+".txt", "r")
    leido = leer.readlines()
    for a in range(0, len(leido)):
        leido[a] = leido[a].replace('\n','')
    
    values = np.zeros(len(leido))
    # print(leido)
    for i in range(0, len(leido)):
        values[i] = float(leido[i])
    leer.close()
    return(values)

def deleteContent(fName):
    
    with open(fName, "w"):
        pass
    print("cleared")


