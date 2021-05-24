# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 16:26:04 2021

@author: Ramon Velazquez
"""

#Importar librerías
import scipy.optimize as sp
import matplotlib.pyplot as plt
import numpy as np
import CRU_extra_funcs as funcs
import CRU_penal as penal
import CRU_data_manag as data_manag
import META_mods_utiles as tesis_wind #Acomodar y poner otro
import CRU_plot_module as mplots
import CRU_wind_eval
import CRU_nav_module as nav


###############################################################################################

#Parámetros generales

###############################################################################################

#Opciones globales MatPlotlib
plt.rcParams.update({'font.size': 15})

#Definición modelos de viento
wind_model = tesis_wind.cargar('wind_models','full_BR_AR_WS')
wind_modelWD = tesis_wind.cargar('wind_models','full_BR_AR_WD')

#Datos atmosféricos y/o del avión globales en sistema EN_tesis
miavion = funcs.plane('A320','V2500-A1')

###############################################################################################

#Función principal

###############################################################################################

def simulador_crucero(profile, N, otp):
    '''Función principal que calcula el consumo y perfiles de variables para vuelo crucero propuesto \n
        inputs: \n
            - N: número de segmentos a dividir el tramo total \n
            - profile: array adim. Va,ts,h \n
            - otp: opciones para ejecución y muestra de resultados
            
            '''
    #Factores de escala y dim
    adim_prof = {'Va':700, 'h':32e3, 'ts':1, 'info':'Valores adim. del perfil input en sistema EN_tesis'}
    
    #Definición de perfiles
    M = N-1
    Va_prof = profile[:M]*adim_prof['Va']
    ts_prof = profile[M:2*M]*adim_prof['ts']
    h_prof = np.zeros(N)
    h_prof[1:] = profile[2*M:]*adim_prof['h']
    h_prof[0] = 32000

    #Datos locales del avión
    S = miavion.general_props['wing']['area']*funcs.OPEN_2_EN['area']
    W0 = miavion.general_props['limits']['MTOW']*funcs.OPEN_2_EN['mass']
    k = miavion.drag_props.polar['clean']['k']
    #Definición vuelo
    #USU > EZE
    prog_LATs = [-54, -24.78]
    prog_LONs = [-68, -65.411]
    
    rev = False
    if rev:
        prog_LATs = np.flip(prog_LATs)
        prog_LONs = np.flip(prog_LONs)
    
    prog_fw_azi, prog_bw_azi, prog_dists = nav.h_Di(prog_LATs, prog_LONs)

    tot_dist = sum(prog_dists)*funcs.OTH_2_EN['mi_ft']
    
    ###################################
    #Perfiles de variables de interés
    ###################################
    
    #Perfiles del viento
    Vw_prof = np.zeros(M)
    VwS_prof = np.zeros(M)
    VwD_prof = np.zeros(M)
    
    #Perfiles generales
    CL, CD, CD0 = np.zeros((3,M))
    rho, Temp = np.zeros((2,N))
    a, Mach = np.zeros((2,M))
    Thr_disp, ct, cth = np.zeros((3,M))
    Thr, Drg = np.zeros((2,M))
    P_disp, P_req, P_use = np.zeros((3,M))
    W = np.zeros(N)
    W[0] = W0
    q_1, B, r_1 = np.zeros((3,M))
    RC, d_t, d_fuel_dot, d_fuel = np.zeros((4,M))
    d_rec_trepada, d_restante = np.zeros((2,M))
    Thr_trepada, Drg_trepada = np.zeros((2,M))
    endurance_Va, endurance_tramo = np.zeros((2,M))
    wind_aporte = np.zeros(M)
    
    x_prof = np.linspace(0,tot_dist,N)
    
    d_h = np.diff(h_prof) #h steps
    d_x = np.diff(x_prof) #x steps
    LATs, LONGs = np.zeros((2,N))

    head = np.zeros(M) 
    acc = np.zeros(M)
    tray_gamma = np.zeros(M)
    
    for j in range(0,M): #Recorremos los M segmentos
    
        LATs[j], LONGs[j], head[j] = nav.nav_route(x_prof[j]/funcs.OTH_2_EN['mi_ft'],prog_dists,prog_fw_azi,prog_LATs, prog_LONs)

        if (d_h[j] == 0):
                      
            #Vuelo Va - h cte
            #Calculamos info atm
            
            rho[j], Temp[j], a[j] = funcs.isa_ATM(h_prof[j]/funcs.SI_2_EN['lon'],'EN_tesis')[:3]
            Mach[j] = Va_prof[j]/a[j]
            
            #Calculamos empuje motor con la info atm
            Thr_disp[j] = miavion._engine_T_(Va_prof[j]/funcs.OPEN_2_EN['speed'], h_prof[j], T_factor = funcs.OPEN_2_EN['force'])
            P_disp[j] = Thr_disp[j]*Va_prof[j]
            
            #Coeficientes y fuerzas aerodinámicas
            CL[j] = 2*W[j]/(rho[j]*S*np.power(Va_prof[j],2))
            CD0[j] = miavion._CD0_WDrg(Mach[j])
            CD[j] = CD0[j] + k*np.power(CL[j],2)
            Drg[j] = 0.5*rho[j]*np.power(Va_prof[j],2)*S*CD[j]
            
            #Por condicion T=D
            ts_prof[j] = Drg[j]/Thr_disp[j]
            
            ct[j] = miavion._fflow_model_(Thr_disp[j]*ts_prof[j]/funcs.OPEN_2_EN['force'], h_prof[j], ct_factor = funcs.OPEN_2_EN['mass'])
            ct[j] = ct[j]/Drg[j] #OJO: CT LB / S PERO EQS CONSIDERAN LB / LBF S. Además aplico D = T
            #Potencia requerida
            P_req[j] = Drg[j]*Va_prof[j]
            
            #Calculamos consumo en el tramo nivelado
            q_1[j] = 0.5*rho[j]*Va_prof[j]**2
            r_1[j] = k/(np.power(q_1[j]*S,2)*CD0[j])
            
            #Evaluar vel viento local

            
            
            if otp['wind_sim']:
                Vw_prof[j], VwS_prof[j], VwD_prof[j] = CRU_wind_eval.wind_eval(wind_model, wind_modelWD, h_prof[j]/funcs.SI_2_EN['lon'], LATs[j], LONGs[j], head[j], output_scale = funcs.SI_2_EN['lon']) #Ya salida en ft/s
                #Sacamos consumo para la dist. dx sin viento
                cons_no_wind = (np.tan(np.arctan(np.sqrt(r_1[j])*W[j])-d_x[j]*ct[j]*q_1[j]*S*CD0[j]*np.sqrt(r_1[j])/Va_prof[j]))/np.sqrt(r_1[j])
                # print(cons_no_wind)
                #Calculamos el tiempo (x_Vh / V) para la misma
                endurance_Va[j] = np.arctan(q_1[j]*S*np.sqrt(k*CD0[j])*(W[j]-cons_no_wind)/(np.power(q_1[j]*S,2)*CD0[j]+k*W[j]*cons_no_wind))/(ct[j]*np.sqrt(k*CD0[j])) #calculada por la dist. completa, a lo largo de la cual el viento afecta
                
                wind_aporte[j] = endurance_Va[j] * Vw_prof[j]
                #Si consideramos efecto de viento, hay menor o mayor distancia a recorrer
                dist_2r = d_x[j] - wind_aporte[j] #Convención: Proyección headwind = negativa, por lo que debo restar
                
            else: #si no, directamente la distancia del tramo
                dist_2r = d_x[j]
            
            #Tiempo para dist_2r:
            endurance_tramo[j] = dist_2r/Va_prof[j]
            acc[j] = Va_prof[j]/endurance_tramo[j]
            
            #Calculamos el combustible final en ese caso
            W[j+1] = (np.tan(np.arctan(np.sqrt(r_1[j])*W[j])-dist_2r*ct[j]*q_1[j]*S*CD0[j]*np.sqrt(r_1[j])/Va_prof[j]))/np.sqrt(r_1[j])
          
            Thr[j] = Drg[j] #Por condición de crucero
            P_use[j] = Thr[j]*Va_prof[j] #Potencia utilizada
            
        else:
            #Vuelo con RC inicial y luego Va - h cte
            #Sector inicial con trepada o descenso
            #Tomamos valores promedio
            loc_h = h_prof[j]+d_h[j]*0.5
            
            #Evaluamos viento
            if otp['wind_sim']:
                loc_Vw, loc_VwS, loc_VwD = CRU_wind_eval.wind_eval(wind_model, wind_modelWD, loc_h/funcs.SI_2_EN['lon'], LATs[j], LONGs[j], head[j], output_scale = funcs.SI_2_EN['lon']) #Ya salida en ft/s

            #Calculamos info atm
            loc_rho, loc_Temp, loc_a = funcs.isa_ATM(loc_h/funcs.SI_2_EN['lon'],'EN_tesis')[:3]
            loc_Mach = Va_prof[j]/loc_a
            
            #Calculamos empuje motor con la info media
            loc_Thr_disp = miavion._engine_T_(Va_prof[j]/funcs.OPEN_2_EN['speed'], loc_h, T_factor = funcs.OPEN_2_EN['force'])
            loc_P_disp = loc_Thr_disp*Va_prof[j]
            
            #Coeficientes y fuerzas aerodinámicas
            loc_CL = 2*W[j]/(loc_rho*S*np.power(Va_prof[j],2))
            loc_CD0 = miavion._CD0_WDrg(loc_Mach)
            loc_CD = loc_CD0 + k*np.power(loc_CL,2)
            loc_Drg = 0.5*loc_rho*np.power(Va_prof[j],2)*S*loc_CD
            
            loc_E = CD0[j]/loc_CL + k*loc_CL
            #Determinamos si trepa o desciende
            if d_h[j]>0:
                loc_Thr = ts_prof[j]*loc_Thr_disp #Empuje aplicado % del disp
            else:
                loc_Thr = ts_prof[j]*loc_Drg
            
            tray_gamma[j] = loc_Thr/W[j] - loc_E
            
            Thr_trepada[j] = loc_Thr
            Drg_trepada[j] = loc_Drg
            
            loc_Pot = Thr_trepada[j] * Va_prof[j]
            loc_Pot_req = loc_Drg*Va_prof[j]
            
            loc_ct = miavion._fflow_model_(loc_Thr/funcs.OPEN_2_EN['force'], loc_h, ct_factor = funcs.OPEN_2_EN['mass'])
            RC[j] = abs((loc_Pot-loc_Pot_req)/W[j]) #Rate of C / D
            d_t[j] = abs(d_h[j]/RC[j]) #Tiempo que tarda
            d_fuel_dot[j] = loc_ct #OJO, YA EN LB / S. No multiplicar por el THR.
            d_fuel[j] = d_fuel_dot[j]*d_t[j] #Consumo en trepada
            W[j+1] = W[j]-d_fuel[j] #Restamos para el próximo peso
            
            #Distancia cubierta en trepada
            d_rec_trepada[j] = Va_prof[j]*d_t[j]
            
            if otp['wind_sim']: #Si consideramos efecto de viento
                wind_aporte[j] = loc_Vw*d_t[j] #Velocidad viento x tiempo en trepar
                d_restante[j] = d_x[j]-d_rec_trepada[j] - wind_aporte[j] #Convención: Proyección headwind = negativa, por lo que debo restar
            else:
                d_restante[j] = d_x[j]-d_rec_trepada[j]                

        
            #Repetimos análisis que resta (recto y nivelado) para nueva alt
            #Evaluar vel viento local
            if otp['wind_sim']:
                Vw_prof[j], VwS_prof[j], VwD_prof[j] = CRU_wind_eval.wind_eval(wind_model, wind_modelWD, h_prof[j+1]/funcs.SI_2_EN['lon'], LATs[j], LONGs[j], head[j], output_scale = funcs.SI_2_EN['lon']) #Ya salida en ft/s
                        
            #Calculamos info atm
            rho[j], Temp[j], a[j] = funcs.isa_ATM(h_prof[j+1]/funcs.SI_2_EN['lon'],'EN_tesis')[:3] #Usar alt post trepada
            Mach[j] = Va_prof[j]/a[j]
            
            #Calculamos empuje motor con la info atm
            Thr_disp[j] = miavion._engine_T_(Va_prof[j]/funcs.OPEN_2_EN['speed'], h_prof[j], T_factor = funcs.OPEN_2_EN['force'])
            P_disp[j] = Thr_disp[j]*Va_prof[j]

            
            #Coeficientes y fuerzas aerodinámicas
            CL[j] = 2*W[j+1]/(rho[j]*S*np.power(Va_prof[j],2))
            CD0[j] = miavion._CD0_WDrg(Mach[j])
            CD[j] = CD0[j] + k*np.power(CL[j],2)
            
            Drg[j] = 0.5*rho[j]*np.power(Va_prof[j],2)*S*CD[j]
            
            Thr[j] = Drg[j] #post trepada
            P_use[j] = Thr[j]*Va_prof[j] #Potencia utilizada
            #Por condicion T=D
            ratio_ts = Drg[j]/Thr_disp[j]
            ct[j] = miavion._fflow_model_(Thr_disp[j]*ratio_ts/funcs.OPEN_2_EN['force'], h_prof[j+1], ct_factor = funcs.OPEN_2_EN['mass'])
            ct[j] = ct[j]/Drg[j] #OJO: CT LB / S PERO EQS CONSIDERAN LB / LBF S. Además aplico D = T
           
            #Potencia requerida
            P_req[j] = Drg[j]*Va_prof[j]
            #Calculamos consumo en el tramo nivelado
            q_1[j] = 0.5*rho[j]*Va_prof[j]**2
            r_1[j] = k/(np.power(q_1[j]*S,2)*CD0[j])
        
            
            if otp['wind_sim']:
                #Sacamos consumo para la dist. dx sin viento
                cons_no_wind = (np.tan(np.arctan(np.sqrt(r_1[j])*W[j+1])-d_restante[j]*ct[j]*q_1[j]*S*CD0[j]*np.sqrt(r_1[j])/Va_prof[j]))/np.sqrt(r_1[j])
                #Calculamos el tiempo (x_Vh / V) para la misma
                endurance_Va[j] = np.arctan(q_1[j]*S*np.sqrt(k*CD0[j])*(W[j+1]-cons_no_wind)/(np.power(q_1[j]*S,2)*CD0[j]+k*W[j+1]*cons_no_wind))/(ct[j]*np.sqrt(k*CD0[j])) #calculada por la dist. completa, a lo largo de la cual el viento afecta
                
                wind_aporte[j] = endurance_Va[j] * Vw_prof[j]
                #Si consideramos efecto de viento, hay menor o mayor distancia a recorrer
                dist_2r = d_restante[j] - wind_aporte[j] #Convención: Proyección headwind = negativa, por lo que debo restar
                
            else: #si no, directamente la distancia del tramo que falta
                dist_2r = d_restante[j]

            endurance_tramo[j] = d_t[j] + dist_2r/Va_prof[j]
            acc[j] = Va_prof[j]/endurance_tramo[j]
            
            #Calculamos el combustible final en ese caso
            W[j+1] = (np.tan(np.arctan(np.sqrt(r_1[j])*W[j+1])-dist_2r*ct[j]*q_1[j]*S*CD0[j]*np.sqrt(r_1[j])/Va_prof[j]))/np.sqrt(r_1[j])
    

    LATs[M], LONGs[M] = nav.nav_route(x_prof[M]/funcs.OTH_2_EN['mi_ft'],prog_dists,prog_fw_azi,prog_LATs, prog_LONs)[:2]
    consumo_fuel = abs((W[0]-W[N-1]))
    consumo_post_pen = penal.penalizacion(consumo_fuel, h_prof, CL, P_disp, P_req, ts_prof, Drg_trepada, Thr_trepada,d_h,d_x, d_rec_trepada, d_t, Va_prof, otp['pen_flag'], 'normal')

    if otp['output'] == "only":
        return(consumo_post_pen)
    elif otp['output'] == "normal":
        return(otp['output'], consumo_post_pen, h_prof, x_prof, Va_prof, ts_prof, Vw_prof, VwD_prof, N, 0)
    if otp['output'] =="full":
        print("In progress - Salida completa")
        print(Thr)
        print(Drg)
        print(Thr_disp*ts_prof)
        nav.plot_ruta(LATs, LONGs, save=True, ruta='res', filecode = str(N), close = True)
        extras = {'CL_prof':CL, 'CD_prof':CD, 'endurance':endurance_tramo, 'acc_prof':acc, 'tray_gamma':tray_gamma, 'Mach':Mach, 'a':a, 'W_prof':W}
        return(otp['output'], consumo_post_pen, h_prof, x_prof, Va_prof, ts_prof, Vw_prof, VwD_prof, N, extras)
        
        

if __name__ == "__main__":
    arr_N = [16, 32, 64, 100]
    fuels = []
    mod = True
    for a in arr_N:
        N = a
        V_test = 1
        ts_test = 0.95
        h_test = np.linspace(1.05,1.2, N-1)
        perfil_entrada = data_manag.gen_input_profile(N, V_test, ts_test, h_test)
        
        if mod:
            NM_opciones = data_manag.gen_sim_opciones('optimizar',0)
            NM_results = sp.minimize(simulador_crucero, perfil_entrada['prof_eval'], args=(perfil_entrada['N'],NM_opciones),method='Nelder-Mead', options={'maxiter': 1e7}, tol=1e-3)
            NM_results['N'] = N
            NM_results['wind_sim'] = NM_opciones['wind_sim']
            
            data_manag.BN_import_export(1,{'ruta':"res",'filename':"NM_output_"+str(N)+"_WTrue"},NM_results)
        # else:
            NM_results = data_manag.BN_import_export(0,{'ruta':"res",'filename':"NM_output_"+str(N)+"_WTrue"},0)
            ev_opciones = data_manag.gen_sim_opciones('evaluar',NM_results['wind_sim'],pen='full',output = 'full')
            SIM_results = data_manag.gen_res_SIM(*simulador_crucero(NM_results.x, NM_results.N, ev_opciones),ev_opciones['wind_sim'])
            
            data_manag.BN_import_export(1,{'ruta':"res",'filename':"RES_output_"+str(N)+"_WTrue"},SIM_results)
            plot_opciones = data_manag.gen_opt_plots('res','revN'+str(SIM_results['N'])+'Ws'+str(SIM_results['wind_sim']),1,1,1)
            mplots.plot_show_export(plot_opciones, SIM_results,extra_s = 1, extra_data = SIM_results['extras'])
        print(NM_results.success)
        fuels.append(SIM_results['W_f'])
    