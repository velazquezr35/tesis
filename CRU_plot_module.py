# -*- coding: utf-8 -*-
"""
Created on Tue May 11 16:46:35 2021

@author: Ramon Velazquez
"""
# -*- coding: utf-8 -*-

#Importar 
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({'font.size': 15})

##############################################

def comparativeN_plot(N,y, opt, **kwargs):
    ''' IN PROGRESS \n
    plot_opts: Usar dict genérico de info \n
    kwargs: tipo = Wf '''
    if kwargs.get('tipo') == 'Wf':
        rel_incr = y[1:]/y[:-1] - 1
        rel_N = np.diff(N)
        fig, ax = plt.subplots()
        ax.plot(rel_N, rel_incr, marker = 'x', label = 'Wind: ?')# + str(res_data['wind_sim']))
        ax.grid()
        ax.set_xlabel(r'$\Delta$ N')
        ax.set_ylabel(r'$\Delta W_f \%$')
        if opt['save']:
            s_name = opt['ruta'] + "/" + opt['filecode'] + "_incrWfvsNplot"
            plt.savefig(s_name, bbox_inches='tight')
        if opt['close']:
            plt.close()   
        fig, ax = plt.subplots()
        ax.plot(N,y, marker = 'o', label='Wind: ?')
        ax.grid()
        ax.set_xlabel('N')
        ax.set_ylabel('Wf [lb]')
        if opt['save']:
            s_name = opt['ruta'] + "/" + opt['filecode'] + "_WfvsNplot"
            plt.savefig(s_name, bbox_inches='tight')
        if opt['close']:
            plt.close()
    
    elif kwargs.get('tipo') == 'CPUt':
        ax.plot(N, y, marker = 'o', label = 'tiempo de cálculo')
        ax.set_xlabel('N')
        ax.set_ylabel('t [s]')    
        ax2 = ax.twinx()
        ax2.plot(N, y/3600)
        ax2.set_ylabel('t [horas]')
        ax.grid()
        ax.legend()
        fig.suptitle(r'$W_f$')
        
        if opt['save']:
            s_name = opt['ruta'] + "/" + opt['filecode'] + "_CPUtplot"
            plt.savefig(s_name, bbox_inches='tight')
        if opt['close']:
            plt.close()


################################################

def travel_plot(y_prof, y_trep_prof, x_prof, x_trep_prof, log_dH, **kwargs):
    '''y prof: y en steps normales \n
        y trep prof: y en trepadas
        kwargs: tipo: h_plot for plot escalón'''
    #Tratamiento y, no implica en orden creciente
    y_comb = np.copy(y_prof)
    count = 1
    for i in range(len(y_trep_prof)):
        y_comb = np.insert(y_comb, i+count, y_trep_prof[i])
        count = count +1
    
    #Tratamiento x, implica orden creciente
    x_comb = np.append(x_prof, x_trep_prof + x_prof[:-1])
    x_comb = np.sort(x_comb)
    
    #Adecuamos si corresponde
    for i in range(len(log_dH)):
        if log_dH[i]:
            print(i)
            y_comb[2*i+1] = y_comb[2*i]
    if kwargs.get('tipo') == 'h_plot':
        fig, ax = plt.subplots()
        ax.plot(x_comb, y_comb)
        ax.grid()
        for loc_x in x_prof:
            ax.axvline(loc_x, linestyle = 'dashed', color = 'r', linewidth = 0.8)
        return(x_comb, y_comb)
    else:
        fig, ax = plt.subplots()
        for i in range(len(y_comb)-1):
            ax.plot([x_comb[i],x_comb[i+1]], [y_comb[i],y_comb[i]], color = 'b')
            ax.plot([x_comb[i+1],x_comb[i+1]],[y_comb[i],y_comb[i+1]], color = 'b', linestyle = 'dashed', linewidth = 0.8)
        ax.grid()
              
        for loc_x in x_prof:
            ax.axvline(loc_x, linestyle = 'dashed', color = 'r', linewidth = 0.8)
        return(x_comb, y_comb)

#######################################################
def plot_show_export(opt, res_data, **kwargs):
    '''Función principal para ploteo global y completo \n
    opts, data, **kwargs'''
    scale_factor = {'x_um':'mi','x_sf':0.000189394, 'W_f_um':'lb'}
    
    if 'scale_factor' in kwargs:
        scale_factor = kwargs.get('scale_factor')
        if scale_factor['x_um'] == 'mi':
            scale_factor['x_sf'] = 1/0.000189394
        #elif:
            #etc...

#Ploteo de h profile
    fig,ax = plt.subplots()
    ax.plot(res_data['x_prof']*scale_factor['x_sf'], res_data['h_prof'],marker='o', label = 'perfil optimizado')
    ax.set_title("Perfil de vuelo crucero - x vs h, N: "+str(res_data['N']))
    ax.set_xlabel("dist "+scale_factor['x_um'])
    ax.set_ylabel("h [ft]")
    ax.grid()
    ax.legend(title='Wind status:' + str(res_data['wind_sim']))
    fig.suptitle(r'$W_f$' + ': ' + str(np.round(res_data['W_f'],2)) + scale_factor['W_f_um'])
    if opt['save']:
        s_name = opt['ruta'] + "/" + opt['filecode'] + "_hplot"
        plt.savefig(s_name,bbox_inches='tight')
    if opt['close']:
        plt.close()

#Ploteo de Va profile
    fig,ax = plt.subplots()
    ax.plot(res_data['x_prof'][:-1]*scale_factor['x_sf'], res_data['Va_prof'],marker='o', label = 'perfil optimizado')
    ax.set_title("Perfil de vuelo crucero - x vs Va, N: "+str(res_data['N']))
    ax.set_xlabel("dist "+scale_factor['x_um'])
    ax.set_ylabel("Va [ft/s]")
    ax.grid()
    ax.legend(title='Wind status:' + str(res_data['wind_sim']))
    fig.suptitle(r'$W_f$' + ': ' + str(np.round(res_data['W_f'],2)) + scale_factor['W_f_um'])
    if opt['save']:
        s_name = opt['ruta'] + "/" + opt['filecode'] + "_Vaplot"
        plt.savefig(s_name,bbox_inches='tight')
    if opt['close']:
        plt.close()

        
#Ploteo de ts profile
    fig,ax = plt.subplots()
    ax.plot(res_data['x_prof'][:-1]*scale_factor['x_sf'], res_data['ts_prof'],marker='o', label = 'perfil optimizado')
    ax.set_title("Perfil de vuelo crucero - x vs ts, N: "+str(res_data['N']))
    ax.set_xlabel("dist "+scale_factor['x_um'])
    ax.set_ylabel("ts [adim]")
    ax.grid()
    ax.legend(title='Wind status:' + str(res_data['wind_sim']))
    fig.suptitle(r'$W_f$' + ': ' + str(np.round(res_data['W_f'],2)) + scale_factor['W_f_um'])
    if opt['save']:
        s_name = opt['ruta'] + "/" + opt['filecode'] + "_tsplot"
        plt.savefig(s_name,bbox_inches='tight')
    if opt['close']:
        plt.close()
        
#Ploteo de WSpeed profile
    fig,ax = plt.subplots()
    ax.plot(res_data['x_prof'][:-1]*scale_factor['x_sf'], res_data['Vw_prof'],marker='o', label = 'perfil optimizado')
    ax.set_title("Perfil de vuelo crucero - x vs Vw, N: "+str(res_data['N']))
    ax.set_xlabel("dist "+scale_factor['x_um'])
    ax.set_ylabel("WSpeed [ft/s]")
    ax.grid()
    ax.legend(title='Wind status:' + str(res_data['wind_sim']))
    fig.suptitle(r'$W_f$' + ': ' + str(np.round(res_data['W_f'],2)) + scale_factor['W_f_um'])
    if opt['save']:
        s_name = opt['ruta'] + "/" + opt['filecode'] + "_Vwplot"
        plt.savefig(s_name,bbox_inches='tight')
    if opt['close']:
        plt.close()
        
        
#Ploteo de WDir profile
    fig,ax = plt.subplots()
    ax.plot(res_data['x_prof'][:-1]*scale_factor['x_sf'], res_data['VD_prof'],marker='o', label = 'perfil optimizado')
    ax.set_title("Perfil de vuelo crucero - x vs Va, N: "+str(res_data['N']))
    ax.set_xlabel("dist "+scale_factor['x_um'])
    ax.set_ylabel("Wind fir from N [deg]")
    ax.grid()
    ax.legend(title='Wind status:' + str(res_data['wind_sim']))
    fig.suptitle(r'$W_f$' + ': ' + str(np.round(res_data['W_f'],2)) + scale_factor['W_f_um'])
    if opt['save']:
        s_name = opt['ruta'] + "/" + opt['filecode'] + "_Vdplot"
        plt.savefig(s_name,bbox_inches='tight')
    if opt['close']:
        plt.close()
    
    if 'extra_s' in kwargs:
        extra_s = kwargs.get('extra_s')
    if extra_s:
        extra_data = kwargs.get('extra_data')
        
#Ploteo de CL profile

    fig,ax = plt.subplots()
    ax.plot(res_data['x_prof'][:-1]*scale_factor['x_sf'], extra_data['CL_prof'],marker='o', label = 'perfil optimizado')
    ax.set_title("Perfil de vuelo crucero - x vs CL, N: "+str(res_data['N']))
    ax.set_xlabel("dist "+scale_factor['x_um'])
    ax.set_ylabel("CL")
    ax.grid()
    ax.legend(title='Wind status:' + str(res_data['wind_sim']))
    fig.suptitle(r'$W_f$' + ': ' + str(np.round(res_data['W_f'],2)) + scale_factor['W_f_um'])
    if opt['save']:
        s_name = opt['ruta'] + "/" + opt['filecode'] + "_CLeplot"
        plt.savefig(s_name,bbox_inches='tight')
    if opt['close']:
        plt.close()
        
#Ploteo de aceleración

    fig,ax = plt.subplots()
    ax.plot(res_data['x_prof'][:-1]*scale_factor['x_sf'], extra_data['acc_prof'],marker='o', label = 'perfil optimizado')
    ax.set_title("Perfil de vuelo crucero - x vs a, N: "+str(res_data['N']))
    ax.set_xlabel("dist "+scale_factor['x_um'])
    ax.set_ylabel(r'a [$\frac{ft}{s^2}$]')
    ax.grid()
    ax.legend(title='Wind status:' + str(res_data['wind_sim']))
    fig.suptitle(r'$W_f$' + ': ' + str(np.round(res_data['W_f'],2)) + scale_factor['W_f_um'])
    if opt['save']:
        s_name = opt['ruta'] + "/" + opt['filecode'] + "_acceplot"
        plt.savefig(s_name,bbox_inches='tight')
    if opt['close']:
        plt.close()
        
#Ploteo de endurance

    fig,ax = plt.subplots()
    ax.plot(res_data['x_prof'][:-1]*scale_factor['x_sf'], extra_data['endurance'],marker='o', label = 'perfil optimizado')
    ax.set_title("Perfil de vuelo crucero - x vs t = x/Va, N: "+str(res_data['N']))
    ax.set_xlabel("dist "+scale_factor['x_um'])
    ax.set_ylabel('t [s]')
    ax2 = ax.twinx()
    ax2.plot(res_data['x_prof'][:-1]*scale_factor['x_sf'], extra_data['endurance']/3600)
    ax2.set_ylabel('t [horas]')
    ax.grid()
    ax.legend(title='Wind status:' + str(res_data['wind_sim']))
    fig.suptitle(r'$W_f$' + ': ' + str(np.round(res_data['W_f'],2)) + scale_factor['W_f_um'])
    if opt['save']:
        s_name = opt['ruta'] + "/" + opt['filecode'] + "_endureplot"
        plt.savefig(s_name, bbox_inches='tight')
    if opt['close']:
        plt.close()
        
        
    return('fin de ploteo')