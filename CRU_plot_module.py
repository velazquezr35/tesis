# -*- coding: utf-8 -*-
"""
Created on Tue May 11 16:46:35 2021

@author: Ramon Velazquez

Tesis de Grado 2021 - Ing. Aeronautica FCEFyN

Modulo de ploteo de perfiles de variables asociadas al vuelo crucero
"""

"""
------------------------------------------------------------------------------
Importar
------------------------------------------------------------------------------
"""
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
import os

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
###############################################################################################
#Funciones base
###############################################################################################
def gen_travel_profiles(modo, **kwargs):
    '''Funcion para la generacion de perfiles tipo travel para muestra de steps y trepadas
    inputs:
        modo, str - Definicion del funcionamiento (SIM, normal)
    kwargs puede contener:
            SIM_res dict - Paquete completo de infos resultado
        o definicion individual:
            y_prof, narray - variable y generica
            x_prof, narray - variable x generica
            dx_prof, narray - steps en x
            dy_prof, narray - steps en y
            tipo, str - define el tipo de ploteo, 'h_plot' para escalon
    returns:
        IN PROGRESS '''
        
    scale_factor = {'x_um':'mi','x_sf':0.000189394, 'W_f_um':'lb'} #Llevar esto a una def. global
    if 'scale_factor' in kwargs:
        scale_factor = kwargs.get('scale_factor')
        if scale_factor['x_um'] == 'mi':
            scale_factor['x_sf'] = scale_factor['x_sf']
        #elif:
            #etc...
            
    if modo == 'SIM':
        SIM_res = kwargs.get('SIM_res')
        if 'var' in kwargs:
            var = kwargs.get('var')
        else:
            var = 'h_prof'
        
        if var == 'h_prof':
            y_prof = SIM_res['h_prof']
            dy_prof = SIM_res['extras']['d_h']
            x_prof = SIM_res['x_prof']
            dx_prof = SIM_res['extras']['x_trep']
    
    else:
        y_prof = kwargs.get('y_prof')
        x_prof = kwargs.get('x_prof')
        dx_prof = kwargs.get('dx_prof')
        dy_prof = kwargs.get('dy_prof')
        
    x_comb = np.copy(x_prof)
    y_comb = np.copy(y_prof)
    
    dx_prof = dx_prof + x_prof[:-1]
    dy_prof = dy_prof + y_prof[:-1]
    count = 1
    for i in range(len(dx_prof)):
        x_comb = np.insert(x_comb,i+count,dx_prof[i])
        y_comb = np.insert(y_comb,i+count,dy_prof[i])
        count += 1
    return(x_comb, y_comb)

def plot_show_export(opt, res_data, **kwargs):
    '''Función principal para el ploteo global de varriables de vuelo
    inputs:
        opt, dict - Opciones generales generada por funcion en data_manag
        res_data, dict - Informacion general a plotear, salida de simulador
    kwargs puede contener:
        scale_factor, dict - Escalas para adecuacion de unidades en ejes de ploteo
    returns:
        print de finalizacion'''
        
    scale_factor = {'x_um':'mi','x_sf':0.000189394, 'W_f_um':'lb'}
    if 'scale_factor' in kwargs:
        scale_factor = kwargs.get('scale_factor')
        if scale_factor['x_um'] == 'mi':
            scale_factor['x_sf'] = 1/0.000189394
        #elif:
            #etc...

    # #Ploteo de h profile
    # fig,ax = plt.subplots()
    # ax.plot(res_data['x_prof']*scale_factor['x_sf'], res_data['h_prof'],marker='o', label = 'perfil optimizado')
    # ax.set_title("Perfil de vuelo crucero - x vs h, N: "+str(res_data['N']))
    # ax.set_xlabel("dist "+scale_factor['x_um'])
    # ax.set_ylabel("h [ft]")
    # ax.grid()
    # ax.legend(title='Wind status:' + str(res_data['wind_sim']))
    # fig.suptitle(r'$W_f$' + ': ' + str(np.round(res_data['W_f'],2)) + scale_factor['W_f_um'])
    # if opt['save']:
    #     s_name = opt['ruta'] + "/" + opt['filecode'] + "_hplot"
    #     plt.savefig(s_name,bbox_inches='tight')
    # if opt['close']:
    #     plt.close()

    # #Ploteo de Va profile
    # fig,ax = plt.subplots()
    # ax.plot(res_data['x_prof'][:-1]*scale_factor['x_sf'], res_data['Va_prof'],marker='o', label = 'perfil optimizado')
    # ax.set_title("Perfil de vuelo crucero - x vs Va, N: "+str(res_data['N']))
    # ax.set_xlabel("dist "+scale_factor['x_um'])
    # ax.set_ylabel("Va [ft/s]")
    # ax.grid()
    # ax.legend(title='Wind status:' + str(res_data['wind_sim']))
    # fig.suptitle(r'$W_f$' + ': ' + str(np.round(res_data['W_f'],2)) + scale_factor['W_f_um'])
    # if opt['save']:
    #     s_name = opt['ruta'] + "/" + opt['filecode'] + "_Vaplot"
    #     plt.savefig(s_name,bbox_inches='tight')
    # if opt['close']:
    #     plt.close()

    # #Ploteo de ts profile
    # fig,ax = plt.subplots()
    # ax.plot(res_data['x_prof'][:-1]*scale_factor['x_sf'], res_data['ts_prof'],marker='o', label = 'perfil optimizado')
    # ax.set_title("Perfil de vuelo crucero - x vs ts, N: "+str(res_data['N']))
    # ax.set_xlabel("dist "+scale_factor['x_um'])
    # ax.set_ylabel("ts [adim]")
    # ax.grid()
    # ax.legend(title='Wind status:' + str(res_data['wind_sim']))
    # fig.suptitle(r'$W_f$' + ': ' + str(np.round(res_data['W_f'],2)) + scale_factor['W_f_um'])
    # if opt['save']:
    #     s_name = opt['ruta'] + "/" + opt['filecode'] + "_tsplot"
    #     plt.savefig(s_name,bbox_inches='tight')
    # if opt['close']:
    #     plt.close()
        
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
    
    # if 'extra_s' in kwargs:
    #     extra_s = kwargs.get('extra_s')
    # if extra_s:
    #     extra_data = kwargs.get('extra_data')
        
    #     #Ploteo de CL profile
    # fig,ax = plt.subplots()
    # ax.plot(res_data['x_prof'][:-1]*scale_factor['x_sf'], extra_data['CL_prof'],marker='o', label = 'perfil optimizado')
    # ax.set_title("Perfil de vuelo crucero - x vs CL, N: "+str(res_data['N']))
    # ax.set_xlabel("dist "+scale_factor['x_um'])
    # ax.set_ylabel("CL")
    # ax.grid()
    # ax.legend(title='Wind status:' + str(res_data['wind_sim']))
    # fig.suptitle(r'$W_f$' + ': ' + str(np.round(res_data['W_f'],2)) + scale_factor['W_f_um'])
    # if opt['save']:
    #     s_name = opt['ruta'] + "/" + opt['filecode'] + "_CLeplot"
    #     plt.savefig(s_name,bbox_inches='tight')
    # if opt['close']:
    #     plt.close()
        
    #     #Ploteo de aceleración
    # fig,ax = plt.subplots()
    # ax.plot(res_data['x_prof'][:-1]*scale_factor['x_sf'], extra_data['acc_prof'],marker='o', label = 'perfil optimizado')
    # ax.set_title("Perfil de vuelo crucero - x vs a, N: "+str(res_data['N']))
    # ax.set_xlabel("dist "+scale_factor['x_um'])
    # ax.set_ylabel(r'a [$\frac{ft}{s^2}$]')
    # ax.grid()
    # ax.legend(title='Wind status:' + str(res_data['wind_sim']))
    # fig.suptitle(r'$W_f$' + ': ' + str(np.round(res_data['W_f'],2)) + scale_factor['W_f_um'])
    # if opt['save']:
    #     s_name = opt['ruta'] + "/" + opt['filecode'] + "_acceplot"
    #     plt.savefig(s_name,bbox_inches='tight')
    # if opt['close']:
    #     plt.close()
        
    #     #Ploteo de endurance
    # fig,ax = plt.subplots()
    # ax.plot(res_data['x_prof'][:-1]*scale_factor['x_sf'], extra_data['endurance'],marker='o', label = 'perfil optimizado')
    # ax.set_title("Perfil de vuelo crucero - x vs t = x/Va, N: "+str(res_data['N']))
    # ax.set_xlabel("dist "+scale_factor['x_um'])
    # ax.set_ylabel('t [s]')
    # ax2 = ax.twinx()
    # ax2.plot(res_data['x_prof'][:-1]*scale_factor['x_sf'], extra_data['endurance']/3600)
    # ax2.set_ylabel('t [horas]')
    # ax.grid()
    # ax.legend(title='Wind status:' + str(res_data['wind_sim']))
    # fig.suptitle(r'$W_f$' + ': ' + str(np.round(res_data['W_f'],2)) + scale_factor['W_f_um'])
    # if opt['save']:
    #     s_name = opt['ruta'] + "/" + opt['filecode'] + "_endureplot"
    #     plt.savefig(s_name, bbox_inches='tight')
    # if opt['close']:
    #     plt.close()
           
    return('fin de ploteo')

###############################################################################################
#Funciones custom para el informe de la tesis
###############################################################################################
def travel_plot(opt, res_data, **kwargs):
    '''
    Funcion para generar plots tipo travel que van al informe
    inputs:
        opt, dict - Opciones generales generada por funcion en data_manag
        res_data, dict - Informacion general a plotear, salida de simulador
    kwargs puede contener:
        scale_factor, dict - Escalas para adecuacion de unidades en ejes de ploteo
    returns:
        print de finalizacion
    '''
    plt.rcParams.update({'font.size': 15, 'font.family':'monospace'})        
    scale_factor = {'x_um':'mi','x_sf':0.000189394, 'W_f_um':'lb'}
    if 'scale_factor' in kwargs:
        scale_factor = kwargs.get('scale_factor')
        if scale_factor['x_um'] == 'mi':
            scale_factor['x_sf'] = scale_factor['x_sf']
        #elif:
            #etc...
    fig, ax = plt.subplots()
    loc_x, loc_y = gen_travel_profiles(modo='SIM',SIM_res=res_data)
    ax = add_vlines(res_data['x_prof']*scale_factor['x_sf'],ax)
    ax.plot(loc_x*scale_factor['x_sf'],loc_y,label='Trayectoria')
    
    ax.set_xlabel("dist. ["+scale_factor['x_um']+ ']', fontsize=17)
    ax.set_ylabel(r'$h$ [ft]' )
    ax = add_ticks(ax,x=res_data['x_prof']*scale_factor['x_sf'])
    ax.grid(which='minor', alpha=0.2)
    ax.grid(which='major', alpha=0.5)
    ax.set_title('Consumo final '+r'$W_f$' + ': ' + str(np.round(res_data['W_f'],2)) +' [' + scale_factor['W_f_um'] + ']')
    ax.legend(title = 'N:' + str(res_data['N']))
    fig.suptitle('Perfil de trayectoria - Viento: '+str(res_data['wind_sim']) )
    if opt['save']:
        s_name = opt['ruta'] + "/" + opt['filecode'] + "_h_trayplot"
        plt.savefig(s_name,bbox_inches='tight')
    if opt['close']:
        plt.close()
    return('Done!')

def ppal_comp_VCL(opt, res_data, **kwargs):
    '''Funcion para los plots que van al informe, comparando con VaCL. Pensado para alto M, por lo que tiene menos entidades.
    inputs:
        opt, dict - Opciones generales generada por funcion en data_manag
        res_data, dict - Informacion general a plotear, salida de simulador
    kwargs puede contener:
        scale_factor, dict - Escalas para adecuacion de unidades en ejes de ploteo
    returns:
        print de finalizacion'''
        
    plt.rcParams.update({'font.size': 15, 'font.family':'monospace'})        
    scale_factor = {'x_um':'mi','x_sf':0.000189394, 'W_f_um':'lb'}
    if 'scale_factor' in kwargs:
        scale_factor = kwargs.get('scale_factor')
        if scale_factor['x_um'] == 'mi':
            scale_factor['x_sf'] = scale_factor['x_sf']
        #elif:
            #etc...
    if 'savefig_dpi' in kwargs:
        savefig_dpi = kwargs.get('savefig_dpi')
    else:
        savefig_dpi = 600
    
    if 'BREG_prof' in kwargs:
        extra_BREG = True
        BREG_prof = kwargs.get('BREG_prof')
    else:
        extra_BREG = False
        
    #Definición fig y axs
    fig = plt.figure(figsize=(16,12))
    ax0 = fig.add_subplot(2,2,1)
    ax1 = fig.add_subplot(2,2,2)
    ax2 = fig.add_subplot(2,2,3)
    ax3 = fig.add_subplot(2,2,4)
    
    #Colores
    lines = {'color':'b'}
    plot = {'extra_marker_color':'r', 'y_label_fsize':18}
    plot['extra_marker_size'] = 0
    plot['major_grid_alph'] = 0.72
    plot['minor_grid_alph'] = 0.3
    
    #h profile
    #Ploteo de h profile
    # ax = add_vlines(res_data['x_prof']*scale_factor['x_sf'],ax)
    s_x, s_y, ex, ey = gen_splotdata(res_data['x_prof']*scale_factor['x_sf'], res_data['h_prof'], extra_markers = True)
    ex[-1] = s_x[-1]
    ax0.plot(s_x,s_y, color = lines['color'], label = 'óptimo',zorder=10, clip_on = False)
    ax0.plot(ex, ey,linewidth= 0, markersize=plot['extra_marker_size'], marker = 'v', color = plot['extra_marker_color'], zorder = 10, clip_on = False)
    # ax0, major_ticks = add_ticks(ax0,x=res_data['x_prof']*scale_factor['x_sf'])
    
    if extra_BREG:
        xtra_x = BREG_prof['x_prof']*scale_factor['x_sf']
        xtra_h = BREG_prof['h']
        ax0.plot(xtra_x, xtra_h, color = 'r', label='$V-C_L$', zorder=10, clip_on=False)
    ax0.set_ylabel(r'$h \quad [ft]$', fontsize = plot['y_label_fsize'])
    ax0.grid(which='minor', alpha=plot['minor_grid_alph'])
    ax0.grid(which='major', alpha=plot['major_grid_alph'])
    plt.setp(ax0.get_xticklabels(), visible=False)
    
    #Va profile
    # ax = add_vlines(res_data['x_prof']*scale_factor['x_sf'],ax)
    s_x, s_y, ex, ey = gen_splotdata(res_data['x_prof']*scale_factor['x_sf'], res_data['Va_prof'], extra_markers = True)
    ax1.plot(s_x, s_y, color = lines['color'], label = 'perfil optimizado',zorder=10, clip_on = False)
    ax1.plot(ex, ey,linewidth= 0, markersize=plot['extra_marker_size'], marker = 'v', color = plot['extra_marker_color'], zorder = 10, clip_on = False)
    ax1.set_ylabel(r'$V_a \quad [ft/s]$', fontsize = plot['y_label_fsize'])
    # ax1, major_ticks = add_ticks(ax1,x=res_data['x_prof']*scale_factor['x_sf'])
    if extra_BREG:
        xtra_Va = [BREG_prof['prof_fijo_VaCL']['V_i']]*len(xtra_x)
        ax1.plot(xtra_x, xtra_Va, color = 'r', label='$V-C_L$', zorder=10, clip_on=False)
    
    ax1.set_ylim([BREG_prof['prof_fijo_VaCL']['V_i']-10, BREG_prof['prof_fijo_VaCL']['V_i']+10])
    ax1.grid(which='minor', alpha=plot['minor_grid_alph'])
    ax1.grid(which='major', alpha=plot['major_grid_alph'])
    plt.setp(ax1.get_xticklabels(), visible=False)

    #ts profile
    # ax = add_vlines(res_data['x_prof']*scale_factor['x_sf'],ax)
    s_x, s_y, ex, ey = gen_splotdata(res_data['x_prof']*scale_factor['x_sf'], res_data['ts_prof'], extra_markers = True)
    ax2.plot(s_x, s_y, color = lines['color'], label = 'perfil optimizado',zorder=10, clip_on = False)
    ax2.plot(ex, ey,linewidth= 0, markersize=plot['extra_marker_size'], marker = 'v', color = plot['extra_marker_color'], zorder = 10, clip_on = False)
    ax2.set_xlabel("dist. ["+scale_factor['x_um']+ ']', fontsize=plot['y_label_fsize'])
    ax2.set_ylabel(r'$\% t_s \quad [adim]$', fontsize=plot['y_label_fsize'])
    # ax2, major_ticks = add_ticks(ax2,x=res_data['x_prof']*scale_factor['x_sf'])
    ax2.grid(which='minor', alpha=plot['minor_grid_alph'])
    ax2.grid(which='major', alpha= plot['major_grid_alph'])
        
    #C_L profile
    try:
        CL_prof = kwargs.get('extra_data')['CL_prof']
    except:
        raise NameError('XD')
    s_x, s_y, ex, ey = gen_splotdata(res_data['x_prof']*scale_factor['x_sf'], CL_prof, extra_markers = True)
    # ax3 = add_vlines(res_data['x_prof']*scale_factor['x_sf'],ax3)
    ax3.plot(s_x, s_y, color = lines['color'], label = 'perfil optimizado',zorder=10, clip_on = False)
    ax3.plot(ex, ey, linewidth= 0,  markersize=plot['extra_marker_size'],marker = 'v', color = plot['extra_marker_color'], zorder = 10, clip_on = False)
    ax3.set_xlabel("dist. ["+scale_factor['x_um']+ ']',fontsize = plot['y_label_fsize'])
    ax3.set_ylabel(r'$C_L \quad [adim]$', fontsize=plot['y_label_fsize'])
    # ax3, major_ticks = add_ticks(ax3,x=res_data['x_prof']*scale_factor['x_sf'])
    
    if extra_BREG:
        xtra_CL = [BREG_prof['prof_fijo_VaCL']['CL_i']]*len(xtra_x)
        ax3.plot(xtra_x, xtra_CL, color = 'r', label='$V-C_L$', zorder=10, clip_on=False)
    ax3.grid(which='minor', alpha=plot['minor_grid_alph'])
    ax3.grid(which='major', alpha=plot['major_grid_alph'])

    #limites y general
    for loc_ax in fig.get_axes():
        loc_ax.set_xlim(0,max(res_data['x_prof']*scale_factor['x_sf']))
        loc_ax.tick_params(axis='y', labelsize=16)
        
    custom_lines_legend = [Line2D([0],[0], linewidth = 2, marker='v', markersize = 0, color = lines['color']), Line2D([0],[0], linewidth = 2, marker='v', markersize = 0, color = 'r')]
    ax0.legend(custom_lines_legend, ['perfil óptimo', '$V-C_L$'], loc='best',fontsize = plot['y_label_fsize']-0.5, columnspacing=0.5, handletextpad=0.2)
    plt.subplots_adjust(left=0.08, right=0.97, top=0.96, bottom=0.11, hspace=0.1, wspace = 0.25)
    if opt['save']:
        s_name = opt['ruta'] + "/" + opt['filecode'] + '_4plot'
        plt.savefig(s_name,bbox_inches='tight', dpi = savefig_dpi)
    if opt['close']:
        plt.close()

def ppal_4_plots(opt, res_data, **kwargs):
    '''Funcion para los plots que van al informe
    inputs:
        opt, dict - Opciones generales generada por funcion en data_manag
        res_data, dict - Informacion general a plotear, salida de simulador
    kwargs puede contener:
        scale_factor, dict - Escalas para adecuacion de unidades en ejes de ploteo
    returns:
        print de finalizacion'''
        
    plt.rcParams.update({'font.size': 15, 'font.family':'monospace'})        
    scale_factor = {'x_um':'mi','x_sf':0.000189394, 'W_f_um':'lb'}
    if 'scale_factor' in kwargs:
        scale_factor = kwargs.get('scale_factor')
        if scale_factor['x_um'] == 'mi':
            scale_factor['x_sf'] = scale_factor['x_sf']
        #elif:
            #etc...
    if 'savefig_dpi' in kwargs:
        savefig_dpi = kwargs.get('savefig_dpi')
    else:
        savefig_dpi = 600
        
    #Definición fig y axs
    fig = plt.figure(figsize=(16,12))
    ax0 = fig.add_subplot(2,2,1)
    ax1 = fig.add_subplot(2,2,2)
    ax2 = fig.add_subplot(2,2,3)
    ax3 = fig.add_subplot(2,2,4)
    
    #Colores
    lines = {'color':'b'}
    plot = {'extra_marker_color':'r', 'y_label_fsize':18}
    plot['extra_marker_size'] = 8
    plot['major_grid_alph'] = 0.72
    plot['minor_grid_alph'] = 0.3
    
    #h profile
    #Ploteo de h profile
    # ax = add_vlines(res_data['x_prof']*scale_factor['x_sf'],ax)
    s_x, s_y, ex, ey = gen_splotdata(res_data['x_prof']*scale_factor['x_sf'], res_data['h_prof'], extra_markers = True)
    ex[-1] = s_x[-1]
    ax0.plot(s_x,s_y, color = lines['color'], label = 'óptimo',zorder=10, clip_on = False)
    ax0.plot(ex, ey,linewidth= 0, markersize=plot['extra_marker_size'], marker = 'v', color = plot['extra_marker_color'], zorder = 10, clip_on = False)
    ax0, major_ticks = add_ticks(ax0,x=res_data['x_prof']*scale_factor['x_sf'])
    ax0.set_ylabel(r'$h \quad [ft]$', fontsize = plot['y_label_fsize'])
    ax0.grid(which='minor', alpha=plot['minor_grid_alph'])
    ax0.grid(which='major', alpha=plot['major_grid_alph'])
    plt.setp(ax0.get_xticklabels(), visible=False)
    #Va profile
    # ax = add_vlines(res_data['x_prof']*scale_factor['x_sf'],ax)
    s_x, s_y, ex, ey = gen_splotdata(res_data['x_prof']*scale_factor['x_sf'], res_data['Va_prof'], extra_markers = True)
    ax1.plot(s_x, s_y, color = lines['color'], label = 'perfil optimizado',zorder=10, clip_on = False)
    ax1.plot(ex, ey,linewidth= 0, markersize=plot['extra_marker_size'], marker = 'v', color = plot['extra_marker_color'], zorder = 10, clip_on = False)
    ax1.set_ylabel(r'$V_a \quad [ft/s]$', fontsize = plot['y_label_fsize'])
    ax1, major_ticks = add_ticks(ax1,x=res_data['x_prof']*scale_factor['x_sf'])
    ax1.grid(which='minor', alpha=plot['minor_grid_alph'])
    ax1.grid(which='major', alpha=plot['major_grid_alph'])
    plt.setp(ax1.get_xticklabels(), visible=False)

    #ts profile
    # ax = add_vlines(res_data['x_prof']*scale_factor['x_sf'],ax)
    s_x, s_y, ex, ey = gen_splotdata(res_data['x_prof']*scale_factor['x_sf'], res_data['ts_prof'], extra_markers = True)
    ax2.plot(s_x, s_y, color = lines['color'], label = 'perfil optimizado',zorder=10, clip_on = False)
    ax2.plot(ex, ey,linewidth= 0, markersize=plot['extra_marker_size'], marker = 'v', color = plot['extra_marker_color'], zorder = 10, clip_on = False)
    ax2.set_xlabel("dist. ["+scale_factor['x_um']+ ']', fontsize=plot['y_label_fsize'])
    ax2.set_ylabel(r'$\% t_s \quad [adim]$', fontsize=plot['y_label_fsize'])
    ax2, major_ticks = add_ticks(ax2,x=res_data['x_prof']*scale_factor['x_sf'])
    ax2.grid(which='minor', alpha=plot['minor_grid_alph'])
    ax2.grid(which='major', alpha= plot['major_grid_alph'])
        
    #C_L profile
    try:
        CL_prof = kwargs.get('extra_data')['CL_prof']
    except:
        raise NameError('XD')
    s_x, s_y, ex, ey = gen_splotdata(res_data['x_prof']*scale_factor['x_sf'], CL_prof, extra_markers = True)
    # ax3 = add_vlines(res_data['x_prof']*scale_factor['x_sf'],ax3)
    ax3.plot(s_x, s_y, color = lines['color'], label = 'perfil optimizado',zorder=10, clip_on = False)
    ax3.plot(ex, ey, linewidth= 0,  markersize=plot['extra_marker_size'],marker = 'v', color = plot['extra_marker_color'], zorder = 10, clip_on = False)
    ax3.set_xlabel("dist. ["+scale_factor['x_um']+ ']',fontsize = plot['y_label_fsize'])
    ax3.set_ylabel(r'$C_L \quad [adim]$', fontsize=plot['y_label_fsize'])
    ax3, major_ticks = add_ticks(ax3,x=res_data['x_prof']*scale_factor['x_sf'])
    ax3.grid(which='minor', alpha=plot['minor_grid_alph'])
    ax3.grid(which='major', alpha=plot['major_grid_alph'])

    #limites y general
    for loc_ax in fig.get_axes():
        loc_ax.set_xlim(0,max(res_data['x_prof']*scale_factor['x_sf']))
        loc_ax.tick_params(axis='y', labelsize=16)
        
    custom_lines_legend = [Line2D([0],[0], linewidth = 0, marker='v', markersize = 9, color = plot['extra_marker_color'])]
    ax0.legend(custom_lines_legend, ['perfil óptimo'], loc='best',fontsize = plot['y_label_fsize']-0.5, columnspacing=0.5, handletextpad=0.2)
    plt.subplots_adjust(left=0.08, right=0.97, top=0.96, bottom=0.11, hspace=0.1, wspace = 0.25)
    if opt['save']:
        s_name = opt['ruta'] + "/" + opt['filecode'] + '_4plot'
        plt.savefig(s_name,bbox_inches='tight', dpi = savefig_dpi)
    if opt['close']:
        plt.close()

def ppal_gamma_plots(opt, res_data, **kwargs):
    '''Funcion para los plots que van al informe
    inputs:
        opt, dict - Opciones generales generada por funcion en data_manag
        res_data, dict - Informacion general a plotear, salida de simulador
    kwargs puede contener:
        scale_factor, dict - Escalas para adecuacion de unidades en ejes de ploteo
    returns:
        print de finalizacion'''
    #Ploteo de gamma profile
    try:
        tray_gamma_prof = np.rad2deg(kwargs.get('extra_data')['tray_gamma'])
    except:
        raise NameError('XD')
    
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot()
    plt.rcParams.update({'font.size': 15, 'font.family':'monospace'})        
    scale_factor = {'x_um':'mi','x_sf':0.000189394, 'W_f_um':'lb'}
    if 'scale_factor' in kwargs:
        scale_factor = kwargs.get('scale_factor')
        if scale_factor['x_um'] == 'mi':
            scale_factor['x_sf'] = scale_factor['x_sf']
        #elif:
            #etc...
    if 'savefig_dpi' in kwargs:
        savefig_dpi = kwargs.get('savefig_dpi')
    else:
        savefig_dpi = 600
    
    #Colores
    lines = {'color':'b'}
    plot = {'extra_marker_color':'r', 'y_label_fsize':16}
    plot['extra_marker_size'] = 8
    plot['major_grid_alph'] = 1
    plot['minor_grid_alph'] = 0.55
    
    s_x, s_y, ex, ey = gen_splotdata(res_data['x_prof']*scale_factor['x_sf'], tray_gamma_prof, extra_markers = True)
    ax.plot(s_x, s_y, color = lines['color'], label = 'perfil optimizado',zorder=10, clip_on = False)
    ax.plot(ex, ey, linewidth= 0,  markersize=plot['extra_marker_size'],marker = 'v', color = plot['extra_marker_color'], zorder = 10, clip_on = False)
    ax.set_xlabel("dist. ["+scale_factor['x_um']+ ']',fontsize = 15)
    ax.set_ylabel(r'$\gamma \quad [deg]$', fontsize=15)
    ax, major_ticks = add_ticks(ax,x=res_data['x_prof']*scale_factor['x_sf'])
    ax.grid(which='minor', alpha=plot['minor_grid_alph'])
    ax.grid(which='major', alpha=plot['major_grid_alph'])
    for loc_ax in fig.get_axes():
        loc_ax.set_xlim(0,max(res_data['x_prof']*scale_factor['x_sf']))
        loc_ax.tick_params(axis='y', labelsize=16)
        
    custom_lines_legend = [Line2D([0],[0], linewidth = 0, marker='v', markersize = 9, color = plot['extra_marker_color'])]
    fig.legend(custom_lines_legend, ['perfil óptimo'], loc=((0.665,0.91)),fontsize = plot['y_label_fsize']-0.5, columnspacing=0.5, handletextpad=0.2)
    plt.subplots_adjust(left=0.09, right=0.97)
    if opt['save']:
        s_name = opt['ruta'] + "/" + opt['filecode'] + '_gammaplot'
        plt.savefig(s_name,bbox_inches='tight', dpi = savefig_dpi)
    if opt['close']:
        plt.close()
        
def ppal_wind_plots(opt, res_data, **kwargs):
    '''
    Graficas de viento para informe
    '''
    plt.rcParams.update({'font.size': 15, 'font.family':'monospace'})        
    scale_factor = {'x_um':'mi','x_sf':0.000189394, 'W_f_um':'lb'}
    if 'scale_factor' in kwargs:
        scale_factor = kwargs.get('scale_factor')
        if scale_factor['x_um'] == 'mi':
            scale_factor['x_sf'] = scale_factor['x_sf']
        #elif:
            #etc...
    if 'savefig_dpi' in kwargs:
        savefig_dpi = kwargs.get('savefig_dpi')
    else:
        savefig_dpi = 600
    #Definición fig y axs
    fig = plt.figure(figsize=(15,5))
    ax0 = fig.add_subplot(1,2,1)
    ax1 = fig.add_subplot(1,2,2)
    
    #Colores
    lines = {'color':'b'}
    plot = {'extra_marker_color':'r', 'y_label_fsize':17.2}
    plot['extra_marker_size'] = 8
    plot['major_grid_alph'] = 0.72
    plot['minor_grid_alph'] = 0.3
    
    #Ploteo de WSpeed profile
    ax0.plot(res_data['x_prof'][:-1]*scale_factor['x_sf'], res_data['Vw_prof'],marker='o', label = 'Magnitud', color = 'b', zorder = 10, clip_on = False)
    ax0.set_xlabel("dist. ["+scale_factor['x_um']+ ']', fontsize=plot['y_label_fsize']-0.7)
    ax0.set_ylabel('$W_{speed} \ [ft/s]$', fontsize=plot['y_label_fsize'])
    ax0, major_ticks = add_ticks(ax0,x=res_data['x_prof']*scale_factor['x_sf'])
    ax0.grid(which='minor', alpha=plot['minor_grid_alph'])
    ax0.grid(which='major', alpha=plot['major_grid_alph'])
    ax0.set_ylim(min(res_data['Vw_prof']), max(res_data['Vw_prof']))
    ax0.legend(loc = 'upper right')
    des_inds = [0,2,4,6,8,10,12]
    ax0.set_yticks(res_data['Vw_prof'][des_inds])
    des_xinds = np.append(np.zeros(1,dtype=int), np.arange(1,17,2))
    ax0.set_xticks(res_data['x_prof'][des_xinds]*scale_factor['x_sf'])
    #Ploteo de WDir profile
    ax1.plot(res_data['x_prof'][:-1]*scale_factor['x_sf'], res_data['VD_prof'],marker='o', label = 'Dirección', color = 'r', zorder = 10, clip_on = False)
    ax1.set_xlabel("dist. ["+scale_factor['x_um']+ ']', fontsize=plot['y_label_fsize']-0.7)
    ax1.set_ylabel('$W_{dir} \ f/N \ [°]$', fontsize=plot['y_label_fsize'])
    ax1, major_ticks = add_ticks(ax1,x=res_data['x_prof']*scale_factor['x_sf'])
    ax1.grid(which='minor', alpha=plot['minor_grid_alph'])
    ax1.grid(which='major', alpha=plot['major_grid_alph'])
    ax1.legend(loc='upper right')
    d_0 = min(res_data['VD_prof'])
    d_f = max(res_data['VD_prof'])
    des_inds = [0,3,5,7,9,11,13,15]
    ax1.set_yticks(res_data['VD_prof'][des_inds])
    ax1.set_xticks(res_data['x_prof'][des_xinds]*scale_factor['x_sf'])
    ax1.set_ylim(d_0, d_f)
    #limites y general
    for loc_ax in fig.get_axes():
        loc_ax.set_xlim(0,max(res_data['x_prof'][:-1]*scale_factor['x_sf']))
        # loc_ax.tick_params(axis='y', labelsize=16)
    plt.subplots_adjust(left=0.086, right=0.98, top=0.96, bottom=0.13, hspace=0.1, wspace = 0.24)
    if opt['save']:
        s_name = opt['ruta'] + "/" + opt['filecode'] + "_WINDplot"
        plt.savefig(s_name,bbox_inches='tight')
    if opt['close']:
        plt.close()
        
def plot_propN(N_arr,prop,opt, **kwargs):
    '''
    Funcion que plotea una propiedad de los resultados de simulacion en funcion de N
    inputs:
        prop, ndarray - Variable dependiente
        N_arr, ndarray - Variable N independiente
    kwargs:
    returns:
        ax, matplotlib ax obj
    '''
    if 'wind_sim' in kwargs:
        wind_sim = kwargs.get('wind_sim')
    else:
        wind_sim = '¿?'
    if 'mode' in kwargs:
        mode = kwargs.get('mode')
    else:
        mode = 'norm'
    if 'grid' in opt:
        grid_status = opt['grid']
    else:
        grid_status = True
    if not 'y_scale' in opt:
        opt['y_scale'] = 'norm'
    if not 'x_scale' in opt:
        opt['x_scale'] = 'norm'
    if not 'filecode' in opt:
        opt['filecode'] = 'filecode_pls'
    if not 'dpi' in opt:
        opt['dpi'] = 150
    if not 'aspect_ratio' in opt:
        opt['aspect_ratio'] = 'auto'
    if not 'fig_size' in opt:
        opt['fig_size'] = (1,1)
    fig, ax = plt.subplots(figsize=opt['fig_size'],dpi = opt['dpi'])
    if mode == 'nested':
        for loc_prop in prop:
            ax.plot(N_arr,loc_prop, label = '')
    elif mode == 'norm':
        ax.plot(N_arr,prop,label='')
    ax = add_ticks(ax,x=N_arr,**kwargs)
    if grid_status:
        ax.grid(which='minor', alpha=0.2)
        ax.grid(which='major', alpha=0.5)
    ax.set_title('Viento: '+wind_sim)
    ax.legend(title = 'leyenda')
    ax.set_aspect(opt['aspect_ratio'])
    print(opt['aspect_ratio'])
    if not opt['y_scale'] == 'norm':
        ax.set_yscale(opt['y_scale'])
    if not opt['x_scale'] == 'norm':
        ax.set_xscale(opt['x_scale'])
    fig.suptitle('Análisis de convergencia')
    if opt['save']:
        s_name = opt['ruta'] + "/" + opt['filecode'] + "_WfvsNplot"
        check_e_file(s_name)
        plt.savefig(s_name, bbox_inches='tight')
    if opt['close']:
        plt.close()
    return(ax)
        
###############################################################################################
#General tools funcs
###############################################################################################
def check_e_file(s_name,**kwargs):
    '''
    Funcion para borrar archivo previo, dado que savefig puede dar problemas
    inputs:
        s_name: ruta+nombre de archivo a chequear
    kwargs:
    returns:
        none '''
    if 'fig_format' in kwargs:
        fig_format = kwargs.get('fig_format')
    else:
        fig_format = 'png'
    try:
        os.remove(s_name+'.'+fig_format)
        print('File removed')
    except:
        pass
    return()
def add_ticks(ax,**kwargs):
    '''
    Funcion para agregar grid custom a un obj ax
    inputs:
            ax, ax matplotlib obj
    kwargs:
        x
    returns: ax
    '''
    if 'x' in kwargs:
        x = kwargs.get('x')
        if 'xt_type' in kwargs:
            x_ticks = kwargs.get('xt_type')
        else:
            x_ticks = 'doble'
        if 'xt_major_step' in kwargs:
            xt_major_step = kwargs.get('xt_major_step')
        else:
            xt_major_step = 2
    
        if not x_ticks == 'none':
            dx = abs(x[xt_major_step]-x[0])
            major_ticks  = np.arange(x[0],x[-1]+dx,abs(x[xt_major_step]-x[0]))
            major_ticks[-1] = x[-1]
            ax.set_xticks(major_ticks)
            if x_ticks == 'doble':
                minor_ticks = np.arange(x[0],x[-1]+dx, dx/2)
                ax.set_xticks(minor_ticks, minor=True)
    return(ax, major_ticks)

def add_vlines(x,ax,**kwargs):
    '''
    Funcion para agregar lineas verticales igualmente espaciadas a un obj ax
    inputs:
        x, spacing array
        ax, ax matplotlib obj
    kwargs:
        
    returns: ax
    '''
    
    if 'vlines_linestyle' in kwargs:
        vlines_linestyle = kwargs.get('vlines_linestyle')
    else:
        vlines_linestyle = 'dashed'
    if 'vlines_linewidth' in kwargs:
        vlines_linewidth = kwargs.get('vlines_linewidth')
    else:
        vlines_linewidth = 0.75
    if 'vlines_color' in kwargs:
        vlines_color = kwargs.get('vlines_color')
    else:
        vlines_color = 'r'
    
    if 'vlines_label' in kwargs:
        vlines_label = kwargs.get('vlines_label')
    else:
        vlines_label = 'step'
    for loc_x in x[:-1]:
        ax.axvline(loc_x, color = vlines_color,linestyle=vlines_linestyle,linewidth=vlines_linewidth)
    ax.axvline(x[-1],label = vlines_label, color = vlines_color,linestyle=vlines_linestyle,linewidth=vlines_linewidth)
    return(ax)

###############################################################################################
#Funciones in progress
###############################################################################################
def gen_splotdata(x,y, **kwargs):
    '''
    DOC
    '''
    if 'extra_markers' in kwargs:
        extra_markers = kwargs.get('extra_markers')
    else:
        extra_markers = False
    
    s_x = []
    s_y = []
    
    s_x.append(x[0])
    s_y.append(y[0])
    for i in range(1, len(x)-1):
        s_x.append(x[i])
        s_x.append(x[i])
        s_y.append(y[i-1])
        s_y.append(y[i])
    if not len(x) == len(y):
        s_x.append(x[-1])
        s_y.append(y[-1])
    else:
        s_x.append(x[-1])
        s_y.append(y[-2])
        s_x.append(x[-1])
        s_y.append(y[-1])
        
    if extra_markers:
        dx = x[1]-x[0]
        if not len(x) == len(y):
            extra_x = x[:-1] + dx/2
        else:
            extra_x = x + dx/2
        extra_y = y
        return(s_x, s_y, extra_x, extra_y)
    else:
        return(s_x,s_y)
    
def comparativeN_plot(N,y, opt, **kwargs):
    '''
    Funcion de ploteo comparativo-incremental
    inputs:
        N_array, narray - Variable independiente 
        pop, narray - Variable dependiente
        opt, dict - Combo generico de info plots
    kwargs:
        tipo = Wf
        label pack
    returns:
        Done notific
    '''
    if 'wind_sim' in kwargs:
        wind_sim = kwargs.get('wind_sim')
    else:
        wind_sim = '¿?'
        
    if kwargs.get('tipo') == 'Wf':
        rel_incr = y[1:]/y[:-1] - 1
        rel_N = np.diff(N)
        fig, ax = plt.subplots()
        ax.plot(rel_N, rel_incr, marker = 'x', label = 'Wind: ' + wind_sim)
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
        ax.plot(N, y, marker = 'o', label = 'tiempo de cálculo - Wind: ' + wind_sim)
        ax.set_xlabel('N')
        ax.set_ylabel('t [s]')    
        ax2 = ax.twinx()
        ax2.plot(N, y/3600) #Escalar mejor
        ax2.set_ylabel('t [horas]')
        ax.grid()
        ax.legend()
        fig.suptitle(r'$W_f$')
        
        if opt['save']:
            s_name = opt['ruta'] + "/" + opt['filecode'] + "_CPUtplot"
            plt.savefig(s_name, bbox_inches='tight')
        if opt['close']:
            plt.close()