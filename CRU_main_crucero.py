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
import CRU_extra_text as text
import META_mods_utiles as tesis_wind #Acomodar y poner otro
import CRU_wind_eval
import pickle
import time

#Parámetros generales
plt.rcParams.update({'font.size': 15})

#Definición viento
wind_model = tesis_wind.cargar('wind_models','full_BR_AR_WS')
wind_modelWD = tesis_wind.cargar('wind_models','full_BR_AR_WD')

###############################################################################################

#Función principal

###############################################################################################

def simulador_crucero(N, profile, otp):
    '''Función principal que calcula el consumo y perfiles de variables para vuelo crucero propuesto \n
        inputs: \n
            - N: número de segmentos a dividir el tramo total \n
            - profile: array adim. Va,ts,h \n
            - otp: opciones para ejecución y muestra de resultados
            
            '''
    
    print(len(profile), N)
    Va_prof = profile[:N]*800 #adim a 800 [ft/s]
    ts_prof = profile[N:2*N]
    h_prof = np.zeros(N)
    h_prof[1:] = profile[2*N:]*32e3
    h_prof[0] = 32000 #adim a 32 [kft]

    #Data aire y avión
    air = 1.4 #gamma aire
    R = 1716 #Cte aire para el sist. de un.
    [W0, S, AR, e] = funcs.planedata()
    k = 1/(AR*e*np.pi) #Factor os. para polar simplificada
    
    #Definición vuelo
    # dist = 1.32e7 #2.0592e7 #pies (Distancia original del caso de tesis)
    dist = 2.0592e7 #3900 millas
    
    #Variables que nos interesan    
    #Perfiles del viento
    Vw_prof = np.zeros(N-1)
    VwS_prof = np.zeros(N-1)
    VwD_prof = np.zeros(N-1)

    
    CL, CD, CD0 = np.zeros((3,N))
    rho, Temp = np.zeros((2,N))
    a, Mach = np.zeros((2,N))
    Thr_disp, ct, cth = np.zeros((3,N))
    Thr, Drg = np.zeros((2,N-1))
    P_disp, P_req, P_use = np.zeros((3,N))
    W = np.zeros(N)
    W[0] = W0
    q_1, B, r_1 = np.zeros((3,N))
    RC, d_t, d_fuel_dot, d_fuel = np.zeros((4,N))
    d_rec_trepada, d_restante = np.zeros((2,N-1))
    Thr_trepada, Drg_trepada = np.zeros((2,N-1))
    endurance_Va, endurance_Vt = np.zeros((2,N-1))
    wind_aporte = np.zeros(N-1)
    
    x_prof = np.linspace(0,dist,N)
    
    d_h = np.diff(h_prof) #h steps
    d_x = np.diff(x_prof) #x steps
    
    LATs, LONGs = np.zeros((2,N))
    
    # print(x_prof, d_x)
    print(d_h)
    
    for j in range(0,N-1): #Recorremos los M segmentos

        LONGs[j] = -54.81 + 54.81/3900 *x_prof[j]*0.000189394 #TEST EVALUAR INICIO; LUEGO LLEVAR A PUNTO MEDIO!
        LATs[j] = -68.31 + 17.31/3900*x_prof[j]*0.000189394 #TEST EVALUAR INICIO; LUEGO LLEVAR A PUNTO MEDIO!
        #Determinar si trepa o mantiene:
        
        if (d_h[j] == 0):
                      
            #Vuelo Va - h cte
            #Calculamos info atm
            rho[j], Temp[j] = funcs.isa_ATM(h_prof[j])[:2]
            a[j] = np.sqrt(air*R*Temp[j])
            Mach[j] = Va_prof[j]/a[j]
            
            #Calculamos empuje motor con la info atm
            Thr_disp[j], cth[j] = funcs.turbofan(Va_prof[j],h_prof[j])
            ct[j] = cth[j]/3600
            
            #Potencia disponible
            P_disp[j] = Thr_disp[j]*Va_prof[j]
            
            #Coeficientes y fuerzas aerodinámicas
            CL[j] = 2*W[j]/(rho[j]*S*np.power(Va_prof[j],2))
            CD0[j] = funcs.CD0_model(Mach[j]) #Con polar
            CD[j] = CD0[j] + k*np.power(CL[j],2)
            
            Drg[j] = 0.5*rho[j]*np.power(Va_prof[j],2)*S*CD[j]
    
            #Potencia requerida
            P_req[j] = Drg[j]*Va_prof[j]
        
            
            #Calculamos consumo en el tramo nivelado
            q_1[j] = 0.5*rho[j]*Va_prof[j]**2
            r_1[j] = k/(np.power(q_1[j]*S,2)*CD0[j])
            
            #Evaluar vel viento local

            Vw_prof[j], VwS_prof[j], VwD_prof[j] = CRU_wind_eval.wind_eval(wind_model, wind_modelWD, h_prof[j]/3.28, LATs[j], LONGs[j]) #Ya salida en ft/s
            
            
            if otp['wind_sim']:
                #Sacamos consumo para la dist. dx sin viento
                cons_no_wind = (np.tan(np.arctan(np.sqrt(r_1[j])*W[j])-d_x[j]*ct[j]*q_1[j]*S*CD0[j]*np.sqrt(r_1[j])/Va_prof[j]))/np.sqrt(r_1[j])
                # print(cons_no_wind)
                #Calculamos el tiempo (x_Vh / V) para la misma
                endurance_Va = np.arctan(q_1[j]*S*np.sqrt(k*CD0[j])*(W[j]-cons_no_wind)/(np.power(q_1[j]*S,2)*CD0[j]+k*W[j]*cons_no_wind))/(ct[j]*np.sqrt(k*CD0[j])) #calculada por la dist. completa, a lo largo de la cual el viento afecta
                
                wind_aporte[j] = endurance_Va * Vw_prof[j]
                #Si consideramos efecto de viento, hay menor o mayor distancia a recorrer
                dist_2r = d_x[j] + wind_aporte[j]
                
            else: #si no, directamente la distancia del tramo
                dist_2r = d_x[j]
            
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
            loc_Vw, loc_VwS, loc_VwD = CRU_wind_eval.wind_eval(wind_model, wind_modelWD, loc_h/3.28, LATs[j], LONGs[j]) #Ya salida en ft/s

            #Calculamos info atm
            loc_rho, loc_Temp = funcs.isa_ATM(loc_h)[:2]
            loc_a = np.sqrt(air*R*loc_Temp)
            loc_Mach = Va_prof[j]/loc_a
            
            #Calculamos empuje motor con la info media
            loc_Thr_disp, loc_cth = funcs.turbofan(Va_prof[j],loc_h)
            loc_ct = loc_cth/3600
            #Potencia disponible para la trepada
            loc_P_disp = loc_Thr_disp*Va_prof[j]
            
            #Coeficientes y fuerzas aerodinámicas
            loc_CL = 2*W[j]/(loc_rho*S*np.power(Va_prof[j],2))
            loc_CD0 = funcs.CD0_model(loc_Mach) #Con polar
            loc_CD = loc_CD0 + k*np.power(loc_CL,2)
            
            loc_Drg = 0.5*loc_rho*np.power(Va_prof[j],2)*S*loc_CD
            
            loc_E = loc_CD0/loc_CL + k*loc_CL
            #Determinamos si trepa o desciende
            if d_h[j]>0:
                loc_Thr = ts_prof[j]*loc_Thr_disp #Empuje aplicado % del disp
            else:
                loc_Thr = ts_prof[j]*loc_Drg
            
            loc_gamma = loc_Thr/W[j] - loc_E
            
            Thr_trepada[j] = loc_Thr
            Drg_trepada[j] = loc_Drg
            # print(Thr_trepada-Drg_trepada)
            
            loc_Pot = Thr_trepada[j] * Va_prof[j]
            loc_Pot_req = loc_Drg*Va_prof[j]
            
            RC[j] = abs((loc_Pot-loc_Pot_req)/W[j]) #Rate of C / D
            
            d_t[j] = abs(d_h[j]/RC[j]) #Tiempo que tarda
            d_fuel_dot[j] = loc_ct*loc_Thr
            d_fuel[j] = d_fuel_dot[j]*d_t[j] #Consumo en trepada
            W[j+1] = W[j]-d_fuel[j] #Restamos para el próximo peso
            
            #Distancia cubierta en trepada
            d_rec_trepada[j] = Va_prof[j]*d_t[j]
            
            if otp['wind_sim']: #Si consideramos efecto de viento
                wind_aporte[j] = loc_Vw*d_t[j] #Velocidad viento x tiempo en trepar
                d_restante[j] = d_x[j]-d_rec_trepada[j] + wind_aporte[j]
            else:
                d_restante[j] = d_x[j]-d_rec_trepada[j]                

        
            #Repetimos análisis que resta (recto y nivelado) para nueva alt
            
            #Evaluar vel viento local

            Vw_prof[j], VwS_prof[j], VwD_prof[j] = CRU_wind_eval.wind_eval(wind_model, wind_modelWD, h_prof[j+1]/3.28, LATs[j], LONGs[j]) #Ya salida en ft/s
                        
            #Calculamos info atm
            rho[j], Temp[j] = funcs.isa_ATM(h_prof[j+1])[:2] #Usar alt post trepada
            a[j] = np.sqrt(air*R*Temp[j])
            Mach[j] = Va_prof[j]/a[j]
            
            #Calculamos empuje motor con la info atm
            Thr_disp[j], cth[j] = funcs.turbofan(Va_prof[j],h_prof[j+1])
            ct[j] = cth[j]/3600
            
            #Potencia disponible
            P_disp[j] = Thr_disp[j]*Va_prof[j]
            Thr[j] = Drg[j] #post trepada
            P_use[j] = Thr[j]*Va_prof[j] #Potencia utilizada
            
            #Coeficientes y fuerzas aerodinámicas
            CL[j] = 2*W[j+1]/(rho[j]*S*np.power(Va_prof[j],2))
            CD0[j] = funcs.CD0_model(Mach[j]) #Con polar
            CD[j] = CD0[j] + k*np.power(CL[j],2)
            
            Drg[j] = 0.5*rho[j]*np.power(Va_prof[j],2)*S*CD[j]
    
            #Potencia requerida
            P_req[j] = Drg[j]*Va_prof[j]
            
            #Calculamos consumo en el tramo nivelado
            q_1[j] = 0.5*rho[j]*Va_prof[j]**2
            r_1[j] = k/(np.power(q_1[j]*S,2)*CD0[j])
        
            
            if otp['wind_sim']:
                #Sacamos consumo para la dist. dx sin viento
                cons_no_wind = (np.tan(np.arctan(np.sqrt(r_1[j])*W[j+1])-d_restante[j]*ct[j]*q_1[j]*S*CD0[j]*np.sqrt(r_1[j])/Va_prof[j]))/np.sqrt(r_1[j])
                #Calculamos el tiempo (x_Vh / V) para la misma
                endurance_Va = np.arctan(q_1[j]*S*np.sqrt(k*CD0[j])*(W[j+1]-cons_no_wind)/(np.power(q_1[j]*S,2)*CD0[j]+k*W[j+1]*cons_no_wind))/(ct[j]*np.sqrt(k*CD0[j])) #calculada por la dist. completa, a lo largo de la cual el viento afecta
                
                wind_aporte[j] = endurance_Va * Vw_prof[j]
                #Si consideramos efecto de viento, hay menor o mayor distancia a recorrer
                dist_2r = d_restante[j] + wind_aporte[j]
                
            else: #si no, directamente la distancia del tramo que falta
                dist_2r = d_restante[j]
            
            #Calculamos el combustible final en ese caso
            W[j+1] = (np.tan(np.arctan(np.sqrt(r_1[j])*W[j+1])-dist_2r*ct[j]*q_1[j]*S*CD0[j]*np.sqrt(r_1[j])/Va_prof[j]))/np.sqrt(r_1[j])
    

    consumo_fuel = abs((W[0]-W[N-1]))

    consumo_new_pen = penal.penalizacion(consumo_fuel, CL, P_disp, P_req, ts_prof, Drg_trepada, Thr_trepada,d_h,d_x-wind_aporte, d_rec_trepada-wind_aporte, d_t, Va_prof, otp['pen_flag'], 'normal')

    #Built-in plot routine (sencilla)
    if otp['plot']:
        fig, ax = plt.subplots()
        ax.plot(x_prof[:-1],Vw_prof,label='Vel viento ft/s')
        ax.set_title("Vel viento - N" + str(N))
        ax.set_xlabel("Dist ft")
        ax.set_ylabel("Vel ft/s")
        ax.grid()
        ax.legend()
        
        fig,ax = plt.subplots()
        ax.plot(x_prof/2.0592e7*3900, h_prof)
        ax.set_title("x vs h: "+str(N))
        ax.set_xlabel("dist [mi]")
        ax.set_ylabel("h [ft]- N: "+str(N))
        ax.grid()
        
        fig,ax = plt.subplots()
        ax.plot(x_prof/2.0592e7*3900,W)
        ax.set_xlabel("dist [mi]")
        ax.set_ylabel("peso [lb]")
        ax.set_title("x vs W - N: "+str(N))
        ax.grid()
        
        fig,ax = plt.subplots()
        ax.plot(x_prof/2.0592e7*3900, Va_prof)
        ax.set_xlabel("dist [mi]")
        ax.set_ylabel("Va [ft/s]")
        ax.set_title("x vs Va - N: "+str(N))
        ax.grid()
        
        fig,ax = plt.subplots()
        ax.plot(x_prof/2.0592e7*3900, ts_prof)
        ax.set_xlabel("dist [mi]")
        ax.set_ylabel("ts [adim]")
        ax.set_title("x vs %ts - N: "+str(N))
        ax.grid()

        fig,ax = plt.subplots()
        ax.plot(x_prof[:-1]/2.0592e7*3900, VwD_prof)
        ax.set_xlabel("dist [mi]")
        ax.set_ylabel("WD [deg from N]")
        ax.set_title("x vs WD - N: "+str(N))
        ax.grid()
        
        fig,ax = plt.subplots()
        ax.plot(x_prof[:-1]/2.0592e7*3900, Vw_prof)
        ax.set_xlabel("dist [mi]")
        ax.set_ylabel("vel proyectada")
        ax.set_title("x vs proy. WS - N: "+str(N))
        ax.grid()
        
        fig,ax = plt.subplots()
        ax.plot(x_prof[:-1]/2.0592e7*3900, CL[:-1])
        ax.set_xlabel("dist [mi]")
        ax.set_ylabel("CL global")
        ax.set_title("x vs CL: "+str(N))
        fig.suptitle('Consumo: ' + str(np.round(consumo_fuel,2)) + ' [lb]')
        ax.grid()
        
    if otp['output'] == "only":
        return(consumo_fuel)
    elif otp['output'] == "normal":
        return(consumo_new_pen, h_prof, x_prof, Va_prof, ts_prof, N, Vw_prof, VwD_prof)
    if otp['output'] =="full":
        print("In progress - Salida completa")
        
    
###############################################################################################

#Definición de clases/diccionarios para la simulación

###############################################################################################

def gen_iexport_XMLs(ruta,fname):
    '''Opciones de exportar/importar archivos con Pickle'''   
    return({'ruta':ruta,'fname':fname})

def gen_opt_plots(folder,name,status,save,close):
    '''Opciones para ploteo y savefigs con Matplotlib'''
    return({'folder':folder,'name':name, 'status':status, 'save':save, 'close':close})

def gen_res_SIM(W_f, h_prof, x_prof, Va_prof, ts_prof, Vw_prof, VD_prof, N):
    return({'W_f':W_f, 'h_prof':h_prof, 'x_prof':x_prof, 'Va_prof':Va_prof, 'ts_prof':ts_prof,'Vw_prof':Vw_prof, 'VD_prof':VD_prof, 'N':N})

def gen_sim_opciones(tipo, wind, **kwargs):
    ''' Clase para opciones de ejecución del simulador \n
    optimizar = Corrida sin salidas
    evaluar = Corrida con salidas
    kwargs: pen, plot, output
    Opciones por default 1,1,normal
    '''
    if tipo == 'optimizar':
        return({'pen_flag':'none', 'wind_sim':bool(wind),'output':'normal','plot':False})
    
    elif tipo == 'evaluar':
            pen_flag = True
            plot = False
            output = "normal"
            if 'pen' in kwargs:
                pen_flag = kwargs.get('pen')
            if 'plot' in kwargs:
                plot = kwargs.get('plot')
            if 'output' in kwargs:
                output = kwargs.get('output')   
            return({'pen_flag':pen_flag, 'wind_sim':bool(wind), 'output':output, 'plot':bool(plot)})

def gen_input_profile(N, Va_adim, ts, h_adim):
    '''Clase para definir inputs'''
    loc_prof_eval = np.zeros(3*N-1)
    loc_prof_eval[:N] = Va_adim
    loc_prof_eval[N:2*N] = ts
    loc_prof_eval[2*N:] = h_adim
    return({'N':N, 'prof_eval':loc_prof_eval})

def BN_import_export(modo,opt,inp):
    ''' modo 0: cargar resultados \n
        modo 1: exportar resultados'''
    if modo:
        loc_file = open(opt.ruta+"/"+opt.filename,'wb')
        pickle.dump(inp,loc_file)
        loc_file.close()
        return('data saved')
    else:
        loc_file = open(opt.ruta+"/"+opt.filename,'rb')
        inp = pickle.load(loc_file)
        loc_file.close()
        return(inp)

def test_vsN():
    N = [10]
    consumos = []
    dts = []
    main_ruta = 'res'
    #Perfil que nos interesa
    
    for i in N:
        
        t1 = time.time()
        V_test = 0.9
        ts_test = 0.9
        h_test = np.linspace(32.5e3/35e3,1.1,i-1)
    
        prof_input = input_profile()
        prof_input._dots_(i, V_test, ts_test, h_test)

        NM_opciones = sim_opciones('optimizar',1)
        ev_opciones = sim_opciones('evaluar',1)

        sim_results = res_SIM()
        
        XML_opciones = iexport_XMLs(main_ruta, '0605WpN_'+str(i))
        plots_opciones = opts_plots(main_ruta, '0605WpN_'+str(i),1,1)

        
        sim_results.NM_params = sp.minimize(optimizame, prof_input.prof_eval, args=(prof_input.N,NM_opciones), method='Nelder-Mead', options={'maxiter': 1e7}, tol=1e-1)
        t2 = time.time()
        print(sim_results.NM_params.success)
        # if sim_results.NM_params.success:
        sim_results._basicRES_(*simulador_crucero(sim_results.NM_params.x, prof_input.N, ev_opciones))
        consumos.append(sim_results.consumo)
        XML_opciones.filetipo = 'RES'
        BN_import_export(1,XML_opciones, sim_results)
        XML_opciones.filetipo = 'INP'
        BN_import_export(1,XML_opciones, sim_results.NM_params.x)
        plot_show_export(plots_opciones, sim_results)
        dts.append(t2-t1)
        # else:
        #     print("Non success sim")
        #     dts.append(0)
        #     consumos.append(0)
    return(consumos, dts)








if __name__ == "__main__":
    pass
    # BN_opciones = iexport_XMLs('res', 'WpN_8')
    # perfil_entrada = BN_import_export(0,BN_opciones,0)
    # ev_opciones = sim_opciones('evaluar',1, plot=True)
    
    # print(simulador_crucero(perfil_entrada,int((len(perfil_entrada)+1)/3), ev_opciones))
