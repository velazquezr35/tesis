# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 08:45:46 2020

@author: Ramon Velazquez
"""

##Modelo avión empuje etc
import numpy as np

def isa_ATM(h): #ingreso input en FT, paso a metros
    if(h<0):
        h = 0.1
    h = h/3.281
    g = 9.81 #m/s2
    R_aire = 287 #m2/s2K
    gamma_aire = 1.4
    if (h<11000):
        T0 = 288.15 #K
        h0 = 0 #m
        a = -6.5/1000
        ro0 = 1.225
        T = T0 + a*(h-h0)
        rho = np.power(T/T0,(-1-g/(a*R_aire)))
        rho = rho*ro0
        a0 = np.sqrt(gamma_aire*R_aire*T)
        P = rho*R_aire*T
    else:
        T0 = 216.65
        h0 = 11e3
        ro0 = 0.3639
        T = T0
        rho = np.exp(-g*(h-h0)/(R_aire*T))
        rho = rho*ro0
        a0 = np.sqrt(gamma_aire*R_aire*T)
        P = rho*R_aire*T
    rho = rho*0.0019577143 #kg/m3 a slug/ft3
    T = T * 1.8 #kelvin to rankine
    a0 = a0/0.3048
    P = P*0.020885434273039  #pascal to PSI
    return([rho,T,a0,P])

def turbofan(V0,h):
    #h > FT, V0 > FT/s
    if (V0==0):
        V0 = 0.0000001
    
    rho,T0,a0,P0 = isa_ATM(h) #input ISA en ft
    M0 = V0/a0

    gamma_c = np.polyval([-1.20614668523318e-16,5.49680519900033e-13,-9.17212621649489e-10, 6.48730229306455e-07,-0.000205746784973442,1.42564262883996],T0)
    
    g0 = 32.174 # % Accel. due to gravity ft/s^2
    BPR = 8 #; % Bypass ratio
    Pi_c = 23 #; % Compressor pressure ratio
    Pi_c_fan = 1.625 #; % Fan pressure ratio
    Pi_d = 0.99 #; % Diffuser pressure ratio
    Pi_n = 0.98#; % Nozzle pressure ratio
    Pi_n_fan = 0.99#; % Fan exit pressure ratio
    Pi_b = 0.95#; % Combustion pressure loss ratio
    P9_P0 = 1#; % Overall core pressure ratio
    P9_fan_P0 = 1#; % Overall fan pressure ratio
    Hc = 18550 #; % Fuel heating value
    A9 = 10.8834 #; % Area of hot nozzle ft^2
    A9_fan = 38.68011208 #; % Area of cold nozzle ft^2
    Tt4 = 3559.67 #; % Max turbine inlet temperature deg R
    Tau_lambda = Tt4/T0 #; % "Temperature limit"
    ##% Air propertiess
    gamma_t = 1.34 #; % Heat capacity ratio at turbine
    cp_c = 0.24 #; % Specific heat capacity at compressor
    cp_t = 0.276 #; % Specific heat capacity at turbine
    #% Gas constants
    Rc = cp_c*778*(gamma_c-1)/gamma_c #; % Compressor
    Rt = cp_t*778*(gamma_t-1)/gamma_t#; % Turbine
    #% Efficiencies
    ec = 0.91 #; % Compressor polytropic efficiency
    ec_fan = 0.95 #; % Fan polytropic efficiency
    et = 0.95 #; % Turbine polytropic efficiency
    Nb = 0.99 #; % Burner efficiency
    Nm = 0.99 #; % Mechanical efficiency
    
    #Compressor stagnation temperature ratio, core and fan
    Tau_c = np.power(Pi_c,(gamma_c-1)/(gamma_c*ec))
    Tau_c_fan = np.power(Pi_c_fan,(gamma_c-1)/(gamma_c*ec_fan))
    
    Tau_r = 1 + ((gamma_c-1)/2)*np.power(M0,2)
    Pi_r = np.power(Tau_r, gamma_c/(gamma_c-1))
    
    f = (Tau_lambda-(Tau_r*Tau_c))/((Nb*Hc/(cp_c*T0))-Tau_lambda)
    
    Tau_t = 1-(1/(Nm*(1+f)))*(Tau_r/Tau_lambda)*((Tau_c-1)+ BPR*(Tau_c_fan-1))
    
    Pi_t = np.power(Tau_t,gamma_t/(et*(gamma_t-1)))
    
    Pt9_P9 = (1/P9_P0)*Pi_r*Pi_d*Pi_c*Pi_b*Pi_t*Pi_n
    
    Pt9_fan_P9_fan = (1/P9_fan_P0)*Pi_r*Pi_d*Pi_c_fan*Pi_n_fan
    
    T9_T0 = (cp_c/cp_t)*Tau_lambda*Tau_t/(np.power(Pt9_P9,(gamma_t - 1)/gamma_t))
    
    T9_fan_T0 = Tau_r*Tau_c_fan/(np.power(Pt9_fan_P9_fan,(gamma_c-1)/gamma_c))
    
    M0V9_V0 = np.sqrt((2/(gamma_c-1))*Tau_lambda*Tau_t*(1-(np.power(Pt9_P9,-(gamma_t-1)/gamma_t))))

    M0V9_fan_V0 = np.sqrt((2/(gamma_c-1))*Tau_r*Tau_c_fan*(1-(np.power(Pt9_fan_P9_fan,(-(gamma_c - 1) / gamma_c)))))
    
    V9 = M0V9_V0*V0/M0
    V9_fan = M0V9_fan_V0*V0/M0

    rho9 = P9_P0*P0/(Rt*T9_T0*T0)
    rho9_fan = P9_fan_P0*P0/(Rc*T9_fan_T0*T0)

    mFlow_core = (rho9*A9*V9)*(1+f)
    mFlow_fan = rho9_fan*A9_fan*V9_fan
    mFlow = (mFlow_core + mFlow_fan)/g0
    
    Tspec = (a0/(1 + BPR))*(((1 + f)*M0V9_V0)- M0 + (1 + f)*(1/(gamma_c*M0V9_V0))*T9_T0*(1-(1/P9_P0))+ BPR*(M0V9_fan_V0-M0+(1 /(gamma_c*M0V9_fan_V0))*T9_fan_T0*(1-(1/P9_fan_P0))))

    T = Tspec*mFlow*1.05;
    ct = f * 3600 * g0 / ((1 + BPR)*Tspec)*(np.power(h,2)*-0.000000000076486 - 0.000000551427739*h + 0.914412587412586)
    return([T,ct])

def planedata():
    W0 = 400000;
    S = 3050;
    AR = 8;
    e = 0.85;
    return([W0,S,AR,e])

def CD0_model(Ma):
    if (Ma<=0.8):
        CD0 = 0.02
    else:
        CD0 = 0.02 + 0.4*np.power(Ma-0.82,2)
    return(CD0)

# import matplotlib.pyplot as plt

# vel = np.linspace(0,1000, 100)

# fig, ax = plt.subplots()

# for j in range(0,5):
#     T = np.zeros([len(vel)])
#     h = j*1e4
#     for i in range(0, len(vel)):
#         T[i] = turbofan(vel[i],h)[0]
#     ax.plot(vel,T, label = 'h ' + str(h/1) + ' [ft]')
# ax.legend()
# ax.set_xlabel('V [ft/s]')
# ax.set_ylabel('T [lbf]')
# ax.grid()

# fig2, ax2 = plt.subplots()
# for j in range(0,5):
#     consume = np.zeros([len(vel)])
#     for r in range(0, len(vel)):
#         consume[r] = turbofan(vel[r],j*1e4)[1]
#     ax2.plot(vel, consume, label = str(j*1e4))
# ax2.grid()