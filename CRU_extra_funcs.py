# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 08:45:46 2020

@author: Ramon Velazquez

Tesis de Grado 2021 - Ing. Aeronautica FCEFyN

Modulo de funciones extra y avion (ACOMODAR)
"""

"""
------------------------------------------------------------------------------
Importar
------------------------------------------------------------------------------
"""
import numpy as np
from skaero.atmosphere import coesa
from openap import prop
from openap import Thrust
from openap import Drag
from openap import FuelFlow

"""
------------------------------------------------------------------------------
Clases
------------------------------------------------------------------------------
"""
class plane():
    '''Clase genérica para utilizar los distintos aviones disponibles en OpenAP. Contiene propiedades generales y funciones particulares del avión \n
    inputs:
        'model', str - Modelo de avion
        'eng', str - Modelo de motor para 'model'
        '''
    
    def __init__(self,model, engine):
        self.model = model
        self.engine = engine
        self.general_props = prop.aircraft(model)
        self.drag_props = Drag(model)
        self.engine_thr = Thrust(ac=model, eng=engine)
        self.engine_fflow = FuelFlow(ac=model, eng=engine)


    def _Drag_(self, mass, VTAS, h, **kwargs):
        '''Clean config \n
        input: mass: [KG], VTAS: [knots], h: [ft] \n
        output: D [N]'''
        D_model = Drag(ac=self.model)
        return(D_model.clean(mass=mass, tas = VTAS, alt = h))
    
    def _fflow_model_(self, acthr, h, **kwargs):
        '''Cruise engine model \n
        input: alt [ft], TAS [knots] \n
        ouput: cts [kg/s] \n
        El modelo determina automáticamente la cantidad de motores del avión. Devuelve el total.'''
        if h<0:
            h = 0
        loc_CT = self.engine_fflow.at_thrust(acthr=acthr, alt = h)
        if 'ct_factor' in kwargs:
            loc_CT = loc_CT*kwargs.get('ct_factor')
        return(loc_CT)
        
    def _engine_T_(self, VTAS, h, **kwargs):
        '''Cruise engine model \n
        input: alt [ft], TAS [knots] \n
        ouput: MAX T [N]  \n
        El modelo determina automáticamente la cantidad de motores del avión. Devuelve el total.'''
        loc_T = self.engine_thr.cruise(tas=VTAS, alt = h)
        if 'T_factor' in kwargs:
            loc_T = loc_T*kwargs.get('T_factor')
        return(loc_T)
    
    def _CD0_WDrg(self, Ma):
        '''Función de incremento de CD0 con Mach. Copiada de Drag OPENAP'''
        base_cd0 = self.drag_props.polar['clean']['cd0']
        wave_Mach = self.drag_props.polar['mach_crit']
        if (Ma<=wave_Mach):
            CD0 = base_cd0
        else:
            CD0 = base_cd0 + 20*np.power(Ma-wave_Mach,4)
        return(CD0)
"""
------------------------------------------------------------------------------
Dicts de escalas y unidades
------------------------------------------------------------------------------
"""
#Info aire
SI_air = {'R': 287, 'g':9.81, 'gamma': 1.4}
#Conversión de unidades // Info aire
SI_2_EN = {'R_air': 5.979094077, 'area': 10.7639, 'lon':3.28084, 'temp': 1.8, 'den':0.0019577143, 'pres':0.020885434273039, 'spd':3.28084, 'mass':2.20462}
OTH_2_EN = {'mi_ft':5280}
OPEN_2_EN = {'mass': 2.20462, 'area':10.7639, 'speed':1.68781, 'force':0.2248}

"""
------------------------------------------------------------------------------
Funciones
------------------------------------------------------------------------------
"""
def isa_ATM(h, output_un): #ingreso input en FT, paso a metros
    '''Función atmosférica en SI basada en modelo U.S. 1976 Standard Atmosphere
    inputs:
        h, float - En unidades [SI]
        output_un, str - Define el sistema de unidades de salida: 'EN_tesis' sistema ingles de tesis ejempli, 'SI', sistema internacional
        '''
    if h < 0:
        h = 0
    eco, T, p, rho = coesa.table(h)
    a = np.sqrt(SI_air['gamma']*SI_air['R']*T)
    if output_un=='EN_tesis':
        T = T*SI_2_EN['temp']
        rho = rho*SI_2_EN['den']
        a = a*SI_2_EN['spd']
        p = p*SI_2_EN['pres']
    elif output_un =='SI':
        pass
    else:
        return(0)        
    return([rho,T,a,p])

def inv_conversion(factores):
    '''
    Funcion basica para la inversion de factores de conversion, para pasar de un sistema a otro
    inputs:
        factores, dict - Contiene los factores a invertir
    output:
        loc_inv, dict - Factores de escala invertidos
        '''
    loc_inv = {}
    for i in factores:
        loc_inv[str(i)] = 1/factores[str(i)]
    return(loc_inv)



if __name__ == "__main__":
    '''
    Ploteo muy basico de un modelo de motor testeando la libreria
    '''
    miavion = plane('A320','V2500-A1')
    alts = [0, 25e3]
    spd = np.linspace(0,800,50)
    spd = spd/OPEN_2_EN['speed']
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    fig2, ax2 = plt.subplots()
    for a in alts:
        thr = []
        ct  = []
        for V in spd:
            loc_thr = miavion._engine_T_(V, a)
            ct.append(miavion._fflow_model_(loc_thr, a))
            thr.append(loc_thr)
        ax.plot(spd, thr, label = str(a))
        ax2.plot(spd,ct, label = str(a))
    ax.legend()
    ax2.legend()
    ax.grid()
    ax2.grid()