# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 21:09:38 2020

@author: Ramon Velazquez

Tesis de Grado 2021 - Ing. Aeronautica FCEFyN

Modulo de penalizacion para la funcion de costo del problema
"""

"""
------------------------------------------------------------------------------
Opciones globales
------------------------------------------------------------------------------
"""
pen_aportes = {'c_CL':0, 'c_POWER_rec':0, 'c_climb':0, 'c_dist': 0, 'c_ts_MAX':0, 'c_ts_min':0, 'c_trepa': 0, 'c_f':0, 'c_acc':0}

"""
------------------------------------------------------------------------------
Funciones
------------------------------------------------------------------------------
"""
def penalizacion(W_f, h_prof, CL, P_av, P_req, ts, Drg, Thr, d_h, x_step, x_climb, pen_status,mode):
    '''
    Funcion de penalizacion para la funcion de costo del vuelo crucero. Agrega combustible segun el incumplimiento de una serie de condiciones
    inputs: 
        W_f, float - Peso final de crucero (unidades correspondientes)
        h_prof, narray - Perfil de altitudes (unidades correspondientes)
        CL, narray - Perfil de coeficientes de sustentacion
        P_av, narray - Perfil de potencias disponibles (unidades correspondientes)
        P_req, narray - Perfil de potencias requeridas (unidades correspondientes)
        t_s, narray - Perfil de mando de gas
        Drg, narray - Perfil de resistencias (unidades correspondientes)
        Thr, narray - Perfil de empujes (unidades correspondientes)
        d_h, narray - Perfil de steps en altitud (unidades correspondientes)
        x_step, narray - Perfil de steps en distancia (unidades correspondientes)
        x_climb, narray - Perfil de distancias consumidas en trepada (unidades correspondientes)
        d_t, narray - Perfil de tiempos consumidos en trepada (unidades correspondientes)
        Va, narray - Perfil de velocidades aerodinamicas (unidades correspondientes)
        pen_status, str - Indicador de prints y salida: #VER SI DEJAR
            'norm' - Normal return mode
            'full' - IN PROGRESS
        mode, str - Indicador de return

    returns: 
        segun valor de mode:
            'normal' - return only del Wf penalizado
            'cperfil' - return Wf penalizado y {dict} perfil de coeficientes de penalizacion
    '''
    
    #Control de altitud negativa
    log_h = h_prof < 0
    pen_aportes['c_hprof'] = -sum(log_h*h_prof)
    
    #Tentativo penalizar bajadas:
    # log3 = d_h < 0
    # pen_aportes['c_godown'] = -sum(log3*d_h)
    
    #Control de CL maximo
    #(Asumiendo 1.6)
    diff_CL = 1.6-CL
    log_CL = diff_CL <0
    pen_aportes['c_CL'] = -sum(diff_CL*log_CL)*100
    
    #Control de potencia disponible mayor a la requerida
    diff_POWER_rec = P_av - P_req
    log_POWER_rec = P_av<P_req
    pen_aportes['c_POWER_rec'] = -sum(diff_POWER_rec*log_POWER_rec)*100
    
    #Control de posicion del mando de gas
    log_ts_min = ts<0
    pen_aportes['c_ts_min'] = -sum(ts*log_ts_min)*1e3
    diff_ts = 1 - ts
    log_ts_MAX = diff_ts<0
    pen_aportes['c_ts_MAX'] = -sum(log_ts_MAX*diff_ts)*1e8
    
    #Control de empuje en trepada mayor a la resistencia
    log_dh = d_h > 0
    log_Drg = log_dh * Drg
    log_Thr = log_dh * Thr
    log_TtC = log_Drg > log_Thr
    diff_TD = log_Thr-log_Drg
    pen_aportes['c_climb'] = -sum(diff_TD*log_TtC)*5e2
    
    #Control distancia recorrida en trepada no mayor al step en x
    diff_dist = x_step-x_climb
    log_dist = diff_dist < 0
    pen_aportes['c_dist'] = -sum(diff_dist*log_dist)*5
    
    #Tentativo penalizar h > s.c. del avión
    diff_hSC = h_prof - 39.5e3 #asumiendo 39500 ft
    log_hSC = diff_hSC > 0
    pen_aportes['c_hSC'] = sum(diff_hSC*log_hSC)
    
    #Tentativo penalizar consumo maximo calculado no mayor a la masa inicial del avion
    # log_wf = W_f>400e3
    # pen_aportes['c_f'] = log_wf*2*W_f*0 
    # if log_wf:
    #     print("Alerta consumo total")
    #     print(W_f)

    if pen_status=='norm' or pen_status == 'full':
        print(pen_aportes)
    
    W_f = W_f + sum(pen_aportes.values())
    if mode == 'normal':
        return(W_f)
    elif mode == 'cperfil':
        return(W_f, pen_aportes)