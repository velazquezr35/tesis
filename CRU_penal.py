# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 21:09:38 2020

@author: Ramon Velazquez

Función de penalización para el consumo del crucero, considerando distintos parámetros del vuelo
"""
pen_aportes = {'c_CL':0, 'c_POWER_rec':0, 'c_climb':0, 'c_dist': 0, 'c_ts_MAX':0, 'c_ts_min':0, 'c_trepa': 0, 'c_f':0, 'c_acc':0}

def penalizacion(W_f, h_prof, CL, P_av, P_req, ts, Drg, Thr, d_h, x_step, x_climb, d_t,Va, pen_status,mode):
        
    #Control de h negativo
    log_h = h_prof < 0
    # pen_aportes['c_hprof'] = -sum(log_h*h_prof)
    
    log2 = abs(d_h)>8000
    # pen_aportes['c_bighstep'] = sum(log2*abs(d_h))
    
    log3 = d_h < 0
    # pen_aportes['c_godown'] = -sum(log3*d_h)
    
    #Control de CL menor al máximo del avión
    diff_CL = 1.6-CL
    log_CL = diff_CL <0
    pen_aportes['c_CL'] = -sum(diff_CL*log_CL)*100 #factor
    
    #Potencia disponible en vuelo recto debe ser mayor a la req
    diff_POWER_rec = P_av - P_req
    log_POWER_rec = P_av<P_req
    
    pen_aportes['c_POWER_rec'] = -sum(diff_POWER_rec*log_POWER_rec)*100 #factor
    
    #Mando gas debe ser entre 1 y 0
    log_ts_min = ts<0
    pen_aportes['c_ts_min'] = -sum(ts*log_ts_min)*1e3 #factor
    
    diff_ts = 1 - ts
    log_ts_MAX = diff_ts<0
    pen_aportes['c_ts_MAX'] = -sum(log_ts_MAX*diff_ts)*1e8
    
    #Empuje en trepada > drag si o si
    log_dh = d_h > 0 #si trepa
    
    log_dh_neg = d_h < 0
    
    
    #TEST: Penalizar descensos
    pen_aportes['c_trepa'] = -sum(log_dh_neg*d_h)*0
    
    log_Drg = log_dh * Drg
    log_Thr = log_dh * Thr
    
    log_TtC = log_Drg > log_Thr
    diff_TD = log_Thr-log_Drg
    
    #Si hay diff:
    
    pen_aportes['c_climb'] = -sum(diff_TD*log_TtC)*5e2
    
    #La distancia recorrida en trepada no puede ser mayor que el step
    
    diff_dist = x_step-x_climb
    log_dist = diff_dist < 0

    
    pen_aportes['c_dist'] = -sum(diff_dist*log_dist)*5
    
    #TEST el consumo calculado no puede ser mayor a la masa del avión
    log_wf = W_f>400e3
    pen_aportes['c_f'] = log_wf*2*W_f*0
    
    if log_wf:
        print("Alerta consumo total")
        print(W_f)

    if pen_status=='norm' or pen_status == 'full':
        print(pen_aportes)
    
    W_f = W_f + sum(pen_aportes.values())
    if mode == 'normal':
        return(W_f)
    elif mode == 'cperfil':
        return(W_f, pen_aportes)