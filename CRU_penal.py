# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 21:09:38 2020

@author: Ramon Velazquez

Función de penalización para el consumo del crucero, considerando distintos parámetros del vuelo
"""

def nueva_penalizacion(W_f, CL, P_av, P_req, ts, Drg, Thr, d_h, x_step, x_climb, d_t,pen_status, Va):
    #Control de CL menor al máximo del avión
    diff_CL = 1.85-CL
    log_CL = diff_CL <0
    c_CL = -sum(diff_CL*log_CL)*100 #factor
    
    #Potencia disponible en vuelo recto debe ser mayor a la req
    diff_POWER_rec = P_av - P_req
    log_POWER_rec = P_av<P_req
    
    c_POWER_rec = -sum(diff_POWER_rec*log_POWER_rec)*100 #factor
    
    #Mando gas debe ser entre 1 y 0
    log_ts_min = ts<0
    c_ts_min = -sum(ts*log_ts_min)*1e3 #factor
    
    diff_ts = 1 - ts
    log_ts_MAX = diff_ts<0
    c_ts_MAX = -sum(log_ts_MAX*diff_ts)*1e8
    
    #Empuje en trepada > drag si o si
    log_dh = d_h > 0 #si trepa
    
    log_dh_neg = d_h < 0
    
    
    #TEST: Penalizar descensos
    c_trepa = -sum(log_dh_neg*d_h)*0
    
    log_Drg = log_dh * Drg
    log_Thr = log_dh * Thr
    
    log_TtC = log_Drg > log_Thr
    diff_TD = log_Thr-log_Drg
    
    
    if pen_status:
        
        print("logica trepda")
        print(log_TtC)
        
        print("Penalización por thr Drg en trepada")
        print(diff_TD*log_TtC)
    
    #Si hay diff:
    
    c_climb = -sum(diff_TD*log_TtC)*5e2
    
    #La distancia recorrida en trepada no puede ser mayor que el step
    
    diff_dist = x_step-x_climb
    log_dist = diff_dist < 0

    
    c_dist = -sum(diff_dist*log_dist)*5
    
    #TEST el consumo calculado no puede ser mayor a la masa del avión
    log_wf = W_f>400e3
    c_f = log_wf*2*W_f
    
    if log_wf:
        print("Alerta consumo total")
        print(W_f)
        
    #TEST Impedir altas velocidades
    # log_Va = Va > 1000
    
    # c_Va = sum(Va*log_Va)*0
    
    if pen_status:
        print(c_CL, c_POWER_rec, c_climb, c_dist, c_ts_MAX, c_ts_min)
    W_f = W_f + c_CL + c_POWER_rec + c_climb + c_dist + c_ts_MAX + c_ts_min + c_trepa + c_f
    return(W_f)