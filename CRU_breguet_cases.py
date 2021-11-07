# -*- coding: utf-8 -*-
"""
Created on Wed Aug 11 10:28:07 2021

@author: Ramon
"""
import matplotlib.pyplot as plt
import numpy as np
import CRU_extra_funcs as funcs
import CRU_plot_module as plotter

def multi_VaCL(profile, N, otp, mod_aeronave,dist):
    '''
    inputs:
        profile, dict: {CL_i, h_i} para vuelo Va-CL constante. V_i se obtiene por 
        equlibrio para el CL_i y h_i informados.
        N, int
        mod_aeronave, funcs.plane obj
        dist, float - Distancia en [mi]
    '''
    #Set up del modelo de aeronave
    S = mod_aeronave.general_props['wing']['area']*funcs.OPEN_2_EN['area']
    W0 = mod_aeronave.general_props['limits']['MTOW']*funcs.OPEN_2_EN['mass']
    k = mod_aeronave.drag_props.polar['clean']['k']
    
    M = N-1
    dist = dist*funcs.OTH_2_EN['mi_ft']
    
    x_step = dist/M
    x = np.arange(0,dist+x_step,x_step)
    W = np.zeros(N)
    h = np.zeros(N)
    rho = np.zeros(N)
    Temp, a = np.zeros((2,M))
    E_i = np.zeros(M)
    CD = np.zeros(M)
    CD0 = np.zeros(M)
    Mach = np.zeros(M)
    Drg = np.zeros(M)
    Thr_disp, Thr = np.zeros((2,M))
    gas_ratio = np.zeros(M)
    ct = np.zeros(M)
    
    W[0] = W0*profile['W0_factor']
    CL_i = profile['CL_i']
    V_i = profile['V_i']
    
    rho_init = 2*W[0]/(S*CL_i*np.power(V_i,2))
    h[0] = funcs.inv_isa_ATM(rho_init/funcs.SI_2_EN['den'], 'EN_tesis')
    
    prof_fijo_VaCL = {'h_i':h[0], 'V_i':V_i, 'W0':W[0], 'CL_i':CL_i}
    
    for j in range(M):
        if j == 0:
            rho[j], Temp[j], a[j] = funcs.isa_ATM(h[j]/funcs.SI_2_EN['lon'],'EN_tesis')[:3]
        else:
            a[j] = funcs.isa_ATM(h[j]/funcs.SI_2_EN['lon'],'EN_tesis')[2]
        Mach[j] = V_i/a[j]
        CD0[j] = mod_aeronave._CD0_WDrg(Mach[j])
        CD[j] = CD0[j] + k*np.power(CL_i,2)
        E_i[j] = CL_i/CD[j]
        Drg[j] = CD[j]*0.5*rho[j]*np.power(V_i,2)*S
        Thr_disp[j] = mod_aeronave._engine_T_(V_i/funcs.OPEN_2_EN['speed'], h[j], T_factor = funcs.OPEN_2_EN['force'])
        gas_ratio[j] = Drg[j]/Thr_disp[j]
        ct[j] = mod_aeronave._fflow_model_(Thr_disp[j]*gas_ratio[j]/funcs.OPEN_2_EN['force'], h[j], ct_factor = funcs.OPEN_2_EN['mass'])
        ct[j] = ct[j]/Drg[j] #OJO: CT LB / S PERO EQS CONSIDERAN LB / LBF S. Además aplico D = T
        W[j+1] = W[j]/np.exp(x_step*ct[j]/(V_i*E_i[j]))
        rho[j+1] = 2*W[j+1]/(CL_i*np.power(V_i,2)*S)
        h[j+1] = funcs.inv_isa_ATM(rho[j+1]/funcs.SI_2_EN['den'],'EN_tesis')
        
    extras = {'N':N,'h':h,'W':W,'rho':rho,'Mach':Mach,'gas':gas_ratio, 'x_prof':x, 'V':np.full(N,V_i), 'prof_fijo_VaCL':prof_fijo_VaCL}
    return(W[0]-W[-1], extras)

def multi_hCL(profile, N, otp, mod_aeronave, dist):
    '''
    inputs:
        profile, dict: {h_i, CL_i} para vuelo h-CL constante
        N, int
        mod_aeronave, funcs.plane obj
        dist, float - Distancia en [mi]
    '''
    #Set up del modelo de aeronave
    S = mod_aeronave.general_props['wing']['area']*funcs.OPEN_2_EN['area']
    W0 = mod_aeronave.general_props['limits']['MTOW']*funcs.OPEN_2_EN['mass']
    k = mod_aeronave.drag_props.polar['clean']['k']
    
    M = N-1
    dist = dist*funcs.OTH_2_EN['mi_ft']
    
    x_step = dist/M
    x = np.arange(0,dist+x_step,x_step)
    W = np.zeros(N)
    V = np.zeros(N)
    E_i = np.zeros(M)
    CD = np.zeros(M)
    CD0 = np.zeros(M)
    Mach = np.zeros(M)
    Drg = np.zeros(M)
    Thr_disp, Thr = np.zeros((2,M))
    gas_ratio = np.zeros(M)
    ct = np.zeros(M)
    
    CL_i = profile['CL_i']
    h_i = profile['h_i']
    rho, Temp, a = funcs.isa_ATM(h_i/funcs.SI_2_EN['lon'],'EN_tesis')[:3]
    W[0] = W0*profile['W0_factor']
    
    for j in range(M):
        V[j] = np.sqrt(2*W[j]/(rho*S*CL_i))
        Mach[j] = V[j]/a
        CD0[j] = mod_aeronave._CD0_WDrg(Mach[j])
        CD[j] = CD0[j] + k*np.power(CL_i,2)
        E_i[j] = CL_i/CD[j]
        Drg[j] = CD[j]*0.5*rho*np.power(V[j],2)*S
        Thr_disp[j] = mod_aeronave._engine_T_(V[j]/funcs.OPEN_2_EN['speed'], h_i, T_factor = funcs.OPEN_2_EN['force'])
        gas_ratio[j] = Drg[j]/Thr_disp[j]
        ct[j] = mod_aeronave._fflow_model_(Thr_disp[j]*gas_ratio[j]/funcs.OPEN_2_EN['force'], h_i, ct_factor = funcs.OPEN_2_EN['mass'])
        ct[j] = ct[j]/Drg[j] #OJO: CT LB / S PERO EQS CONSIDERAN LB / LBF S. Además aplico D = T
        W[j+1] = W[j]*np.power((1-x_step*ct[j]/(2*E_i[j]*V[j])),2)
        
    V[-1] = np.sqrt(2*W[-1]/(rho*S*CL_i))
    extras = {'N':N,'h':np.full(N,h_i),'W':W,'rho':rho,'Mach':Mach,'gas':gas_ratio, 'x_prof':x, 'V':V}
    return(W[0]-W[-1],extras)


def case_comp(N_arr,mod_aeronave,dist,**kwargs):
    '''
    Funcion para la comparacion facil vs los resultados optimizados del código
    inputs:
        N_arr, narray - Puntos segmento
        mod_aeronave, funcs.plane obj - Modelo de interés
        dist, float - Distancia a cubrir [mi]
    kwargs:
        
    returns:
        W_f, list 2d - Nested Wf
    '''
    if 'prof_test' in kwargs:
        prof_test = kwargs.get('prof_test')
    else:
        prof_test = {'h_i':32e3,'CL_i':0.6,'V_i':700, 'W0_factor': 0.90}
    Wf_hCL = []
    Wf_VaCL = []
    extras_VaCL = []
    extras_hCL = []
    for N in N_arr:
        loc_res = multi_VaCL(prof_test,N,1,mod_aeronave,dist)
        extras_VaCL.append(loc_res[1])
        Wf_VaCL.append(loc_res[0])
        loc_res = multi_hCL(prof_test,N,1,mod_aeronave, dist)
        extras_hCL.append(loc_res[1])
        Wf_hCL.append(loc_res[0])
    return(Wf_hCL,Wf_VaCL,extras_VaCL,extras_hCL)

if __name__ == '__main__':
    
    N_arr = [256]
    avion_A320 = funcs.plane('A320','V2500-A1')
    Wf_hCL,Wf_VaCL,extras_VaCL,extras_hCL = case_comp(N_arr, avion_A320,dist=3600)
    
    
    plt.rcParams.update({'font.size': 15, 'font.family':'monospace'})  
    fig, ax = plt.subplots()
    ax.plot(N_arr, Wf_VaCL, 'ro', linestyle = 'solid', label = '$V-C_L$ cte.')
    ax.plot(N_arr, Wf_hCL, 'gs',linestyle = 'solid', label = '$h-C_L$ cte.')
    ax.set_xlabel('N')
    ax.set_ylabel('Consumo $W_f \quad [lb]$')
    ax.set_title('Variación del consumo vs \n N entre perfiles de Breguet')
    ax.grid()
    ax.legend(title='Perfil')
    
    fig, ax = plt.subplots()
    for extra in extras_VaCL:
        ax.plot(extra['x_prof']*funcs.MI_2_FT['lon'],extra['h'],label=str(extra['N']))
    ax.legend(title='N puntos')
    ax.set_xlabel('Distancia $[mi]$')
    ax.set_ylabel(r'$h \quad [ft]$')
    ax.set_title('Variación de la altitud vs \n distancia para perfil V-CL cte. segmentado')
    ax.grid()
    
    fig, ax = plt.subplots()
    for extra in extras_hCL:
        ax.plot(extra['x_prof']*funcs.MI_2_FT['lon'],extra['V'],label=str(extra['N']))
    ax.legend(title='N puntos')
    ax.set_xlabel('Distancia $[mi]$')
    ax.set_ylabel(r'$V \quad [ft/s]$')
    ax.set_title('Variación de la velocidad vs \n distancia para perfil h-CL cte. segmentado')
    ax.grid()