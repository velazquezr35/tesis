# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 16:26:04 2021

@author: Ramon Velazquez

Tesis de Grado 2021 - Ing. Aeronautica FCEFyN

Modulo principal para el calculo y optimizacion del vuelo crucero de aeronaves comerciales
"""

"""
------------------------------------------------------------------------------
Importar
------------------------------------------------------------------------------
"""
import scipy.optimize as sp
import matplotlib.pyplot as plt
import numpy as np
import CRU_extra_funcs as funcs
import CRU_penal as penal
import CRU_data_manag as data_manag
import META_krg_factory as krg
import CRU_plot_module as mplots
import CRU_wind_eval
import CRU_nav_module as nav

"""
------------------------------------------------------------------------------
Opciones globales
------------------------------------------------------------------------------
"""
plt.rcParams.update({'font.size': 15})

"""
------------------------------------------------------------------------------
Funciones
------------------------------------------------------------------------------
"""

def cruise_sim(profile,N, otp, mod_aeronave, **kwargs):
    '''
    Función principal de simulacion y costo que calcula el consumo y variables asociadas para un vuelo propuesto \n
    inputs: \n
            profile, array - [Va,ts,h] size 3N-1
            N, int - numero de segmentos a dividir el tramo total
            otp, dict - opciones para ejecucion y muestra de resultados, debe contener:
                'ruta': dict, informacion de ruta [LATs, LONGs, rev] (cords formato START > END)
                'wind': dict, contiene sendos modelos de viento (necesario solamente si otp['wind_sim'] = True)
            mod_aeronave, plane obj - modelo de aeronave a simular
    kwargs (puede contener):
            glob_print, bool - para imprimir resultados y pasos informativos intermedios, default False
            adim_profile, dict {Va: float,h: float,ts: float} - para utilizar un perfil input adimensionalizado particular, default 700 fts, 32e3 ft, 1 adim (sistema EN_tesis)
            h_0, float - altitud inicial fija de crucero, default 32e3 ft
    '''
    
    if 'glob_print' in kwargs:
        glob_print = kwargs.get('glob_print')
    else:
        glob_print = False
    
    if 'adim_profile' in kwargs:
        adim_profile = kwargs.get('adim_profile')
    else:
        adim_prof = {'Va':700, 'h':32e3, 'ts':1, 'info':'Valores adimensionales del perfil input en sistema EN_tesis'}
    
    if 'h_0' in kwargs:
        h_0 = kwargs.get('h_0')
    else:
        h_0 = 32e3
        
    if otp['wind_sim'] == True:
        wmodel_WSpeed = otp['wind']['wmodel_WSpeed']
        wmodel_WDir = otp['wind']['wmodel_WDir']
    
    #Set up del perfil
    M = N-1
    Va_prof = profile[:M]*adim_prof['Va']
    ts_prof = profile[M:2*M]*adim_prof['ts']
    h_prof = np.zeros(N)
    h_prof[1:] = profile[2*M:]*adim_prof['h']
    h_prof[0] = 32000
    
    #Set up del modelo de aeronave
    S = mod_aeronave.general_props['wing']['area']*funcs.OPEN_2_EN['area']
    W0 = mod_aeronave.general_props['limits']['MTOW']*funcs.OPEN_2_EN['mass']
    k = mod_aeronave.drag_props.polar['clean']['k']
    
    #Set up de la navegacion
    prog_LATs = otp['ruta']['LATs']
    prog_LONs = otp['ruta']['LONs']
    rev = otp['ruta']['rev']
    if rev:
        prog_LATs = np.flip(prog_LATs)
        prog_LONs = np.flip(prog_LONs)
    prog_fw_azi, prog_bw_azi, prog_dists = nav.h_Di(prog_LATs, prog_LONs)
    tot_dist = sum(prog_dists)*funcs.OTH_2_EN['mi_ft']
    
    #Set up de perfiles de variables de interes
    #Viento
    Vw_prof = np.zeros(M)
    VwS_prof = np.zeros(M)
    VwD_prof = np.zeros(M)
    
    #Generales
    CL, CD, CD0 = np.zeros((3,M))
    rho, Temp = np.zeros((2,N))
    a, Mach = np.zeros((2,M))
    Thr_disp, ct, cth = np.zeros((3,M))
    Thr, Drg = np.zeros((2,M))
    P_disp, P_req, P_use = np.zeros((3,M))
    W = np.zeros(N)
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
    headng = np.zeros(M) 
    acc = np.zeros(M)
    tray_gamma = np.zeros(M)
    gas_ratio = np.zeros(M)
    #Set up del peso inicial
    W[0] = W0
    
    #Recorrida y calculo de los M segmentos
    for j in range(0,M):
        #NOTA: Llevar la siguiente a la longitud media del segmento
        LATs[j], LONGs[j], headng[j] = nav.nav_route(x_prof[j]/funcs.OTH_2_EN['mi_ft'],prog_dists,prog_fw_azi,prog_LATs, prog_LONs)
        
        #Caso sin cambio de altitud, analisis directo bajo perfil h-Va constante
        if d_h[j] == 0:            
            rho[j], Temp[j], a[j] = funcs.isa_ATM(h_prof[j]/funcs.SI_2_EN['lon'],'EN_tesis')[:3]
            Mach[j] = Va_prof[j]/a[j]
            Thr_disp[j] = mod_aeronave._engine_T_(Va_prof[j]/funcs.OPEN_2_EN['speed'], h_prof[j], T_factor = funcs.OPEN_2_EN['force'])
            P_disp[j] = Thr_disp[j]*Va_prof[j]
            CL[j] = 2*W[j]/(rho[j]*S*np.power(Va_prof[j],2))
            CD0[j] = mod_aeronave._CD0_WDrg(Mach[j])
            CD[j] = CD0[j] + k*np.power(CL[j],2)
            Drg[j] = 0.5*rho[j]*np.power(Va_prof[j],2)*S*CD[j]
            gas_ratio[j] = Drg[j]/Thr_disp[j]
            ct[j] = mod_aeronave._fflow_model_(Thr_disp[j]*gas_ratio[j]/funcs.OPEN_2_EN['force'], h_prof[j], ct_factor = funcs.OPEN_2_EN['mass'])
            ct[j] = ct[j]/Drg[j] #OJO: CT LB / S PERO EQS CONSIDERAN LB / LBF S. Además aplico D = T
            P_req[j] = Drg[j]*Va_prof[j]
            q_1[j] = 0.5*rho[j]*Va_prof[j]**2
            r_1[j] = k/(np.power(q_1[j]*S,2)*CD0[j])
            
            if otp['wind_sim']:
                Vw_prof[j], VwS_prof[j], VwD_prof[j] = CRU_wind_eval.wind_eval(wmodel_WSpeed, wmodel_WDir, h_prof[j]/funcs.SI_2_EN['lon'], LATs[j], LONGs[j], headng[j], output_scale = funcs.SI_2_EN['lon']) #Ya salida en ft/s
                cons_no_wind = (np.tan(np.arctan(np.sqrt(r_1[j])*W[j])-d_x[j]*ct[j]*q_1[j]*S*CD0[j]*np.sqrt(r_1[j])/Va_prof[j]))/np.sqrt(r_1[j])
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
          
        #Caso con cambio de altitud
        else:
            #Analisis inicial para trepada segun teoria dV/dh = cte
            #Valores en la h y Va promedio
            h_prom = h_prof[j]+d_h[j]*0.5
            if j == 0: #Si permitimos trepar al inicio, asumimos misma Va para ambos
                Va_prom = Va_prof[j]
            else:
                Va_prom = (Va_prof[j]+Va_prof[j-1])/2
            rho_prom, Temp_prom, a_prom = funcs.isa_ATM(h_prom/funcs.SI_2_EN['lon'],'EN_tesis')[:3]
            Mach_prom = Va_prom/a_prom
            Thr_disp_prom = mod_aeronave._engine_T_(Va_prom/funcs.OPEN_2_EN['speed'], h_prom, T_factor = funcs.OPEN_2_EN['force'])
            P_disp_prom = Thr_disp_prom * Va_prom
            if otp['wind_sim']:
                Vw_prom, VwS_prom, VwD_prom = CRU_wind_eval.wind_eval(wmodel_WSpeed, wmodel_WDir, h_prom/funcs.SI_2_EN['lon'], LATs[j], LONGs[j], headng[j], output_scale = funcs.SI_2_EN['lon']) #Ya salida en ft/s
            
            #Calculo iterativo
            W_prom = W[j]
            d_W_prom = 1
            counter = 0
            while abs(d_W_prom) > 0.01:
                pre_W_prom = W_prom
                CL_prom = 2*W_prom/(rho_prom*S*np.power(Va_prom,2))
                CD0_prom = mod_aeronave._CD0_WDrg(Mach_prom)
                CD_prom = CD0_prom + k*np.power(CL_prom,2)
                Drg_prom = 0.5*rho_prom*np.power(Va_prom,2)*S*CD_prom
                dV_dh = (Va_prof[j]-Va_prof[j-1])/(d_h[j])
                if d_h[j]>0:
                    Thr_prom = ts_prof[j]*Thr_disp_prom
                else:
                    Thr_prom = ts_prof[j]*Drg_prom
                
                h_dot = (Thr_prom-Drg_prom)*Va_prom/W_prom / (1+Va_prom*dV_dh)
                t_climb = d_h[j]/h_dot
                ct_prom = mod_aeronave._fflow_model_(Thr_prom/funcs.OPEN_2_EN['force'], h_prom, ct_factor = funcs.OPEN_2_EN['mass']) #Ya en lb/s
                d_fuel = t_climb*ct_prom
                W_f_climb = W[j] - d_fuel
                W_prom = W[j] - W_f_climb/2
                d_W_prom = (W_prom-pre_W_prom)/pre_W_prom
                counter += 1
            
            #Updates correspondientes
            W[j+1] = W_f_climb
            Drg_trepada[j] = Drg_prom
            Thr_trepada[j] = Thr_prom
            d_t[j] = t_climb
            #Distancia cubierta en trepada
            d_rec_trepada[j] = Va_prom*t_climb
            if otp['wind_sim']: #Si consideramos efecto de viento
                wind_aporte[j] = Vw_prom*t_climb #Velocidad viento x tiempo en trepar
                d_restante[j] = d_x[j]-d_rec_trepada[j] - wind_aporte[j] #Convención: Proyección headwind = negativa, por lo que debo restar
            else:
                d_restante[j] = d_x[j]-d_rec_trepada[j]                

            #Analisis para tramo restante bajo perfil h-Va constante
            if otp['wind_sim']:
                Vw_prof[j], VwS_prof[j], VwD_prof[j] = CRU_wind_eval.wind_eval(wmodel_WSpeed, wmodel_WDir, h_prof[j+1]/funcs.SI_2_EN['lon'], LATs[j], LONGs[j], headng[j], output_scale = funcs.SI_2_EN['lon']) #Ya salida en ft/s
            rho[j], Temp[j], a[j] = funcs.isa_ATM(h_prof[j+1]/funcs.SI_2_EN['lon'],'EN_tesis')[:3] #Usando altitud post trepada
            Mach[j] = Va_prof[j]/a[j]
            Thr_disp[j] = mod_aeronave._engine_T_(Va_prof[j]/funcs.OPEN_2_EN['speed'], h_prof[j], T_factor = funcs.OPEN_2_EN['force'])
            P_disp[j] = Thr_disp[j]*Va_prof[j]
            CL[j] = 2*W[j+1]/(rho[j]*S*np.power(Va_prof[j],2))
            CD0[j] = mod_aeronave._CD0_WDrg(Mach[j])
            CD[j] = CD0[j] + k*np.power(CL[j],2)
            Drg[j] = 0.5*rho[j]*np.power(Va_prof[j],2)*S*CD[j]
            Thr[j] = Drg[j] #post trepada
            P_use[j] = Thr[j]*Va_prof[j] #Potencia utilizada
            gas_ratio[j] = Drg[j]/Thr_disp[j]
            ct[j] = mod_aeronave._fflow_model_(Thr_disp[j]*gas_ratio[j]/funcs.OPEN_2_EN['force'], h_prof[j+1], ct_factor = funcs.OPEN_2_EN['mass'])
            ct[j] = ct[j]/Drg[j] #OJO: CT LB / S PERO EQS CONSIDERAN LB / LBF S. Además aplico D = T
            P_req[j] = Drg[j]*Va_prof[j]
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
    consumo_post_pen = penal.penalizacion(consumo_fuel, h_prof, CL, P_disp, P_req, ts_prof, Drg_trepada, Thr_trepada,d_h,d_x, d_rec_trepada, otp['pen_flag'], 'normal')

    if otp['output'] == "only":
        return(consumo_post_pen)
    elif otp['output'] == "normal":
        return(otp['output'], consumo_post_pen, h_prof, x_prof, Va_prof, ts_prof, Vw_prof, VwD_prof, N, 0)
    if otp['output'] =="full":
        print("In progress - Salida completa")
        nav.plot_ruta(LATs, LONGs, save=True, ruta='res', filecode = str(N), close = True)
        extras = {'CL_prof':CL, 'CD_prof':CD, 'endurance':endurance_tramo, 'acc_prof':acc, 'tray_gamma':tray_gamma, 'Mach':Mach, 'a':a, 'W_prof':W}
        return(otp['output'], consumo_post_pen, h_prof, x_prof, Va_prof, ts_prof, Vw_prof, VwD_prof, N, extras)
    

if __name__ == "__main__":
    #Ejemplo de user end func
    #(Luego se puede llevar a un archivo aparte, mas limpio)
    
    #Definición modelos de viento y aeronave
    wind_modelSpeed = krg.exp_imp_modelo(0,'imp',{'folder':'wind_models', 'name':'full_BR_AR_WS'})
    wind_modelWDirection = krg.exp_imp_modelo(0,'imp',{'folder':'wind_models', 'name':'full_BR_AR_WD'})
    avion_A320 = funcs.plane('A320','V2500-A1')
    #Esto ver de acomodar en otro lado
    wind_mods = {'wmodel_WSpeed':wind_modelSpeed, 'wmodel_WDir':wind_modelWDirection}
    
    #Ruta a recorrer
    #USU > EZE
    ruta_LATs = [-54, -24.78]
    ruta_LONs = [-68, -65.411]
    ruta_rev = False
    ruta_info = {'LATs':ruta_LATs, 'LONs':ruta_LONs, 'rev':ruta_rev}
    
    #Seteo de la corrida
    # N = [4,8,16,32,64,128,256]
    N = 16
    modo = True #True para optimizar, False para evaluar
    
    V_test = 1
    ts_test = 0.95
    h_test = np.linspace(1.05,1.2, N-1)
    perfil_entrada = data_manag.gen_input_profile(N, V_test, ts_test, h_test)
    
    if modo:
        NM_opciones = data_manag.gen_sim_opciones('optimizar',wind=False)
        #Ver de agregar esto directo en generar opciones
        NM_opciones['wind'] = wind_mods
        NM_opciones['ruta'] = ruta_info
        NM_results = sp.minimize(cruise_sim, perfil_entrada['prof_eval'], args = (perfil_entrada['N'], NM_opciones, avion_A320), method = 'Nelder-Mead', options={'maxiter': 1e7}, tol=1e-3)
        NM_results['N'] = N
        NM_results['wind_sim'] = NM_opciones['wind_sim']
        data_manag.BN_import_export(1,{'ruta':"res",'filename':"NM_output_"+str(N)+"_indicadorW"},NM_results)
    else:
        NM_results = data_manag.BN_import_export(0,{'ruta':"res",'filename':"NM_output_"+str(N)+"_indicadorW"},0)
        ev_opciones = data_manag.gen_sim_opciones('evaluar',NM_results['wind_sim'],pen='full',output = 'full')
        ev_opciones['wind'] = wind_mods
        ev_opciones['ruta'] = ruta_info
        SIM_results = data_manag.gen_res_SIM(*cruise_sim(NM_results.x, NM_results.N, ev_opciones,avion_A320),ev_opciones['wind_sim'])
        data_manag.BN_import_export(1,{'ruta':"res",'filename':"RES_output_"+str(N)+"_indicadorW"},SIM_results)
        plot_opciones = data_manag.gen_opt_plots('res','revN'+str(SIM_results['N'])+'Ws'+str(SIM_results['wind_sim']),1,1,1)
        mplots.plot_show_export(plot_opciones, SIM_results,extra_s = 1, extra_data = SIM_results['extras'])
        print(NM_results.success)
        print(SIM_results['W_f'])
    