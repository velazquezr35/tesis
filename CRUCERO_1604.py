# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 16:26:04 2021

@author: Ramon Velazquez
"""

#Importar librerías
import scipy.optimize as sp
import matplotlib.pyplot as plt
import numpy as np
import funcs_1604 as funcs
import penal_1604 as penal
import text_1604 as text
import test_evaluador_1604 as tesis_wind #Acomodar y poner otro
import pickle

plt.rcParams.update({'font.size': 13})

#Definición viento
wind_model = tesis_wind.cargar()


#Cálculo de consumo

def simulador_crucero(profile,N, otp):
        
    Va_prof = profile[:N]*800 #El perfil viene adim. [ft/s]
    ts_prof = profile[N:2*N]
    
    h_prof = np.zeros(N)
    h_prof[1:] = profile[2*N:]*35e3
    h_prof[0] = 32000

    #Data aire y avión
    air = 1.4 #gamma aire
    R = 1716 #Cte aire para el sist. de un.
    [W0, S, AR, e] = funcs.planedata()
    k = 1/(AR*e*np.pi) #Factor os. para polar simplificada
    
    test_list = []
    
    #Definición vuelo
    # dist = 1.32e7 #2.0592e7 #pies
    dist = 2.0592e7
    
    #Variables que nos interesan
    Vg_prof = np.copy(Va_prof)
    Vw_prof = np.zeros(N-1)
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
    # print(d_h)
    for j in range(0,N-1): #Recorremos los M segmentos

        LONGs[j] = -54.81 + 54.81/3900 *x_prof[j]*0.000189394 #TEST EVALUAR INICIO; LUEGO LLEVAR A PUNTO MEDIO!
        LATs[j] = -68.31 + 17.31/3900*x_prof[j]*0.000189394 #TEST EVALUAR INICIO; LUEGO LLEVAR A PUNTO MEDIO!
        #Determinar si trepa o mantiene:
        
        if (d_h[j] == 0):
                      
            # print("Step cte")
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
            Vw_prof[j] = wind_model([h_prof[j]/3.28,LATs[j],LONGs[j]])[0] #h from ft to m
            Vw_prof[j] = -Vw_prof[j]*3.28 #ft/s to m/s
            
            print("data wind")
            print(Vw_prof[j],h_prof[j]/3.28, LATs[j],LONGs[j],x_prof[j])
            
            if otp.wind_sim:
                #Sacamos consumo para la dist. dx sin viento
                cons_no_wind = (np.tan(np.arctan(np.sqrt(r_1[j])*W[j])-d_x[j]*ct[j]*q_1[j]*S*CD0[j]*np.sqrt(r_1[j])/Vg_prof[j]))/np.sqrt(r_1[j])
                # print(cons_no_wind)
                #Calculamos el tiempo (x_Vh / V) para la misma
                endurance_Va = np.arctan(q_1[j]*S*np.sqrt(k*CD0[j])*(W[j]-cons_no_wind)/(np.power(q_1[j]*S,2)*CD0[j]+k*W[j]*cons_no_wind))/(ct[j]*np.sqrt(k*CD0[j])) #calculada por la dist. completa, a lo largo de la cual el viento afecta
                
                wind_aporte[j] = endurance_Va * Vw_prof[j]
                #Si consideramos efecto de viento, hay menor o mayor distancia a recorrer
                dist_2r = d_x[j] + wind_aporte[j]
                
            else: #si no, directamente la distancia del tramo
                dist_2r = d_x[j]
            
            #Calculamos el combustible final en ese caso
            W[j+1] = (np.tan(np.arctan(np.sqrt(r_1[j])*W[j])-dist_2r*ct[j]*q_1[j]*S*CD0[j]*np.sqrt(r_1[j])/Vg_prof[j]))/np.sqrt(r_1[j])
          
            Thr[j] = Drg[j] #Por condición de crucero
            P_use[j] = Thr[j]*Va_prof[j] #Potencia utilizada
            
        else:
            #Vuelo con RC inicial y luego Va - h cte
            #Sector inicial con trepada o descenso
            #Tomamos valores promedio
            loc_h = h_prof[j]+d_h[j]*0.5
            
            #Evaluamos viento
            loc_Vw = wind_model([loc_h/3.28, LATs[j], LONGs[j]])[0] #Idem inicial
            loc_Vw = loc_Vw*3.28

            # loc_h = h_prof[j]
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
            d_rec_trepada[j] = Vg_prof[j]*d_t[j]
            
            if otp.wind_sim: #Si consideramos efecto de viento
                wind_aporte[j] = loc_Vw*d_t[j] #Velocidad viento x tiempo en trepar
                d_restante[j] = d_x[j]-d_rec_trepada[j] + wind_aporte[j]
            else:
                d_restante[j] = d_x[j]-d_rec_trepada[j]                

        
            #Repetimos análisis que resta (recto y nivelado) para nueva alt
            
            #Evaluar vel viento local
            Vw_prof[j] = wind_model([h_prof[j+1]/3.28,LATs[j],LONGs[j]])[0] #h from ft to m #MEJORAR APROXIMACI+ON DE LAT Y LON ACÁ CON VALOR MEDIO
            Vw_prof[j] = -Vw_prof[j]*3.28 #ft/s to m/s
            
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
            
            if otp.wind_sim: #Si consideramos efecto de viento
                Vg_prof[j] = Va_prof[j]
            else:
                Vg_prof[j] = Va_prof[j] #Vel. aero = Vel tierra
            
            #Calculamos consumo en el tramo nivelado
            q_1[j] = 0.5*rho[j]*Va_prof[j]**2
            r_1[j] = k/(np.power(q_1[j]*S,2)*CD0[j])
        
            
            if otp.wind_sim:
                #Sacamos consumo para la dist. dx sin viento
                cons_no_wind = (np.tan(np.arctan(np.sqrt(r_1[j])*W[j+1])-d_restante[j]*ct[j]*q_1[j]*S*CD0[j]*np.sqrt(r_1[j])/Vg_prof[j]))/np.sqrt(r_1[j])
                #Calculamos el tiempo (x_Vh / V) para la misma
                endurance_Va = np.arctan(q_1[j]*S*np.sqrt(k*CD0[j])*(W[j+1]-cons_no_wind)/(np.power(q_1[j]*S,2)*CD0[j]+k*W[j+1]*cons_no_wind))/(ct[j]*np.sqrt(k*CD0[j])) #calculada por la dist. completa, a lo largo de la cual el viento afecta
                
                wind_aporte[j] = endurance_Va * Vw_prof[j]
                #Si consideramos efecto de viento, hay menor o mayor distancia a recorrer
                dist_2r = d_restante[j] + wind_aporte[j]
                
            else: #si no, directamente la distancia del tramo que falta
                dist_2r = d_restante[j]
            
            #Calculamos el combustible final en ese caso
            W[j+1] = (np.tan(np.arctan(np.sqrt(r_1[j])*W[j+1])-dist_2r*ct[j]*q_1[j]*S*CD0[j]*np.sqrt(r_1[j])/Vg_prof[j]))/np.sqrt(r_1[j])
        # print(Vg_prof-Va_prof)
    

    consumo_fuel = abs((W[0]-W[N-1]))

    consumo_new_pen = penal.nueva_penalizacion(consumo_fuel, CL, P_disp, P_req, ts_prof, Drg_trepada, Thr_trepada,d_h,d_x-wind_aporte, d_rec_trepada-wind_aporte, d_t, otp.pen_flag, Va_prof)
    # (W_f, CL, P_av, P_req, ts, Drg, Thr, d_h, x_step, x_climb, d_t,pen):
    # consumo_fuel = penal.penalizar(consumo_fuel, CL, P_disp, P_req, ts_prof, d_h, Drg, Thr, d_t, d_x, d_rec_trepada, otp.pen_flag)
    # W_f = penal.penalizar(W_f, CL, Pot_disp, Pot_req, ts_prof, h_step, Drg, Thr, d_t, x_step, d_R, pen_status)
    
    #Built-in plot routine (sencilla)
    if otp.plot:
        fig, ax = plt.subplots()
        ax.plot(x_prof[:-1],Vw_prof,label='Vel viento ft/s')
        ax.set_title("Vel viento - N" + str(N))
        ax.set_xlabel("Dist ft")
        ax.set_ylabel("Vel ft/s")
        ax.grid()
        ax.legend()
        
        fig,ax = plt.subplots()
        ax.plot(x_prof/2.0592e7*3900, h_prof,marker='o')
        ax.set_title("x vs h: "+str(N))
        ax.set_xlabel("dist [mi]")
        ax.set_ylabel("h [ft]- N: "+str(N))
        ax.grid()
        
        fig,ax = plt.subplots()
        ax.plot(x_prof/2.0592e7*3900,W,marker='s')
        ax.set_xlabel("dist [mi]")
        ax.set_ylabel("peso [lb]")
        ax.set_title("x vs W - N: "+str(N))
        ax.grid()
        
        fig,ax = plt.subplots()
        ax.plot(x_prof/2.0592e7*3900, Va_prof,marker='s')
        ax.set_xlabel("dist [mi]")
        ax.set_ylabel("Va [ft/s]")
        ax.set_title("x vs Va - N: "+str(N))
        ax.grid()
        
        fig,ax = plt.subplots()
        ax.plot(x_prof/2.0592e7*3900, ts_prof,marker='s')
        ax.set_xlabel("dist [mi]")
        ax.set_ylabel("ts [adim]")
        ax.set_title("x vs %ts - N: "+str(N))
        ax.grid()

        
    if otp.output == "only":
        return(consumo_fuel)
    if otp.output == "normal":
        return(consumo_new_pen, h_prof, x_prof, Va_prof, ts_prof, N)
    if otp.output =="full":
        print("u crazy")
        
    
##########################################



def optimizame(profile,N,opciones):
    w_f = simulador_crucero(profile, N, opciones)[0]
    return(w_f)


def res_import_export(modo, res, inp, opt):
    if modo:
        #Ploteamos
        if opt.plot.status:
            
            fig,ax = plt.subplots()
            ax.plot(res.x_profile/2.0592e7*3900, res.h_profile,marker='o')
            ax.set_title("x vs h: "+str(res.N))
            ax.set_xlabel("dist [mi]")
            ax.set_ylabel("h [ft]- N: "+str(res.N))
            ax.grid()
            fig.suptitle("Consumo calculado: " + str(np.round(res.consumo,2)) + " [lb]")
            if opt.plot.save:
                s_name = opt.plot.folder + "/" + opt.plot.filecode + "_hplot"
                plt.savefig(s_name, dpi=200)
            if opt.plot.close:
                plt.close()
            
                    
            fig,ax = plt.subplots()
            ax.plot(res.x_profile/2.0592e7*3900, res.Va_profile,marker='s')
            ax.set_xlabel("dist [mi]")
            ax.set_ylabel("Va [ft/s]")
            ax.set_title("x vs Va - N: "+str(res.N))
            ax.grid()
            fig.suptitle("Consumo calculado: " + str(np.round(res.consumo,2)) + " [lb]")
            if opt.plot.save:
                s_name = opt.plot.folder + "/" + opt.plot.filecode + "_Vaplot"
                plt.savefig(s_name, dpi=200)
            if opt.plot.close:
                plt.close()
            
            fig,ax = plt.subplots()
            ax.plot(res.x_profile/2.0592e7*3900 , res.ts_profile,marker='s')
            ax.set_xlabel("dist [mi]")
            ax.set_ylabel("ts [adim]")
            ax.set_title("x vs %ts - N: "+str(res.N))
            ax.grid()
            fig.suptitle("Consumo calculado: " + str(np.round(res.consumo,2)) + " [lb]")
            if opt.plot.save:
                s_name = opt.plot.folder + "/" + opt.plot.filecode + "_tsplot"
                plt.savefig(s_name, dpi=200)
                
            if opt.plot.close:
                plt.close()

        if opt.sav.status:
            loc_file = open(opt.sav.folder+"/"+opt.sav.filename+"_INPUT",'wb')
            pickle.dump(inp,loc_file)
            loc_file.close()
            loc_file = open(opt.sav.folder+"/"+opt.sav.filename+"_RESULT",'wb')
            pickle.dump(res, loc_file)
            loc_file.close()
        return()
            
    else:
        
        loc_file = open(opt.sav.folder+"/"+opt.sav.filename+"_INPUT",'rb')
        inp = pickle.load(loc_file)
        loc_file.close()
        loc_file = open(opt.sav.folder+"/"+opt.sav.filename+"_RESULT",'rb')
        res = pickle.load(loc_file)
        loc_file.close() 
        return(res, inp)
##########################################
#Definición de clases para la simulación

class export_opts():
    class sav:
        status = True
        def _filenam_(dat, folder, name):
            dat.folder = folder
            dat.filename = name
        
    class plot:
        save = True
        status = True
        close = True
        def _fignam_(dat, folder, name):
            dat.folder = folder
            dat.filecode = name

        
class res_SIM():
    def _basicRES_(res, consumo, h_profile, x_profile, Va_profile, ts_profile, N):
        res.consumo = consumo
        res.h_profile = h_profile
        res.x_profile = x_profile
        res.Va_profile = Va_profile
        res.ts_profile = ts_profile
        res.N = N
    class NM_params():
        pass

class otp_optimizar():
    def __init__(self):
        self.pen_flag = False
        self.wind_sim = False
        self.output = "normal"
        self.plot = False
        
class otp_test():
    def __init__(self):
        self.pen_flag = True
        self.wind_sim = False
        self.output = "normal"
        self.plot = True
        
class otp_test_wind():
    def __init__(self):
        self.pen_flag = True
        self.wind_sim = True
        self.output = "normal"
        self.plot = True

class opt_test():
    def cond(pen,wind,output,plot):
        opt_test.pen_flag = pen
        opt_test.output = output
        opt_test.wind_sim = wind
        opt_test.plot = plot

class input_profile():
    '''Clase para definir inputs y luego exportar fácilmente'''
    def _dots_(perfil, N, Va_adim, ts, h):
        '''Formación del perfil de puntos típicos'''
        perfil.N = N
        perfil.prof_eval = np.zeros(3*N-1)
        perfil.prof_eval[:N] = Va_adim
        perfil.prof_eval[N:2*N] = ts
        perfil.prof_eval[2*N:] = h
        
if __name__ == "__main__":
    
    N = [128]
    #Perfil que nos interesa
    
    for i in N:
        
        V_test = 0.9
        ts_test = 0.9
        h_test = np.linspace(32.5e3/35e3,1.1,i-1)
    
        prof_input = input_profile()
        prof_input._dots_(i, V_test, ts_test, h_test)

        opciones = otp_optimizar()

        sim_results = res_SIM()
        
        opciones_exportar = export_opts()
        opciones_exportar.plot._fignam_(opciones_exportar.plot,'res','N_'+str(i))
        opciones_exportar.sav._filenam_(opciones_exportar.sav, 'res','N_'+str(i))
        
        sim_results.NM_params = sp.minimize(optimizame, prof_input.prof_eval, args=(prof_input.N,opciones), method='Nelder-Mead', options={'maxiter': 1e7}, tol=1e-2)
    
        if sim_results.NM_params.success:
            sim_results._basicRES_(*simulador_crucero(sim_results.NM_params.x, prof_input.N, opciones))
            res_import_export(1,sim_results,sim_results.NM_params.x,export_opts)
        else:
            print("Non success sim")
# 

# rta_no_wind = text.readata("NO_log_wind_dist_example")
# rta_wind = text.readata("SI_log_wind_dist_example")
# consumo_nW = optimizame(rta_no_wind, N, test_opciones)
# consumo_W = optimizame(rta_wind,N, test_opciones_W)
# # test_profile = np.zeros(3*N)
# # test_profile[:N]=0.95
# # test_profile[N:2*N]=1
# # test_profile[2*N:]=30e3




# consumo_hV_nW = optimizame(test_profile, N, test_opciones)
# consumoo_hV_W = optimizame(test_profile,N,test_opciones_W)


