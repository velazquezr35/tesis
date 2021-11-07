# -*- coding: utf-8 -*-
"""
Created on Wed May 26 14:42:50 2021

@author: Ramon Velazquez
"""

"""
------------------------------------------------------------------------------
Importar
------------------------------------------------------------------------------
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from skaero.atmosphere import coesa

"""
------------------------------------------------------------------------------
Opciones globales
------------------------------------------------------------------------------
"""
plt.rcParams.update({'font.size': 15, 'font.family':'monospace'})
 
"""
------------------------------------------------------------------------------
Funciones
------------------------------------------------------------------------------
"""
def figure_gen(plot_opts,**kwargs):
    '''
    Funcion que generra una figura para las opciones
    inputs:
        plot_opts, dict - Opciones de customizacion de ploteo
    kwargs puede contener:
    returns:
        fig ax, objs -
    '''
    fig, ax = plt.subplots()
    ax.set_xlabel(plot_opts['xlabel'])
    ax.set_ylabel( plot_opts['ylabel'])
    return(fig, ax)
    
def figure_finish(fig, ax, plot_opts):
    '''
    Funcion para la customizacion de ploteos
    inputs:
        fig, obj - Figura matplotlib
        ax, obj - Axe matplotlib
        plot_opts, dict - Opciones de customizacion
    returns:
        none    
    '''
    if 'savefig_dpi' in plot_opts:
        savefig_dpi = plot_opts['savefig_dpi']
    else:
        savefig_dpi = 200
    if 'legend' in plot_opts: 
        if plot_opts['legend']:
            ax.legend(title=plot_opts['legend_title'])
    if 'fig_title' in plot_opts:
        if plot_opts['fig_title']:
            ax.set_title(plot_opts['fig_title'])
    if plot_opts['save']:
        try:
            s_name = plot_opts['ruta'] + "/" + plot_opts['filecode']
            plt.savefig(s_name, bbox_inches='tight')
        except:
            plot_opts['ruta'] = 'default_METAfigs'
            if not plot_opts['ruta'] in os.listdir():
                os.makedirs(plot_opts['ruta'])
            s_name = plot_opts['ruta'] + "/" + plot_opts['filecode']
            plt.savefig(s_name+'.png', bbox_inches='tight', dpi = savefig_dpi)
    if plot_opts['close']:
        plt.close()
    return('Done')

def ov_plot(fig, ax, data_x,data_y, lab, mode, **kwargs):
    '''
    Funcion para el ploteo de informacion de estaciones, sea en modo por puntos scatter o con curvas
    inputs:
        fig, obj - Figure matplotlib
        ax, obj - Axe matplotlib
        data_x, ndarray - Datos eje x
        data_y, narray - Datos eje y
        lab, str - Label
        mode, str - Tipo de ploteo 'dots', 'normal' (curvas)
    returns:
        none
    '''
    if mode == 'dots':
        ax.plot(data_x, data_y, 'ro', label = lab)
    elif mode == 'normal':
        ax.plot(data_x, data_y, label = lab)
    else:
        raise NameError('Definir correctamente modo de ploteo')
    return('Done')

def part_fig_informe(p, wspd, wdir, **kwargs):
    '''
    DOC
    '''
    if 'folder' in kwargs:
        folder = kwargs.get('folder') + '/'
    else:
        folder = ''
    if 'savefig_dpi' in kwargs:
        savefig_dpi = kwargs.get('savefig_dpi')
    else:
        savefig_dpi = 200
        
    fig = plt.figure(figsize = (11,5))
    ax0 = fig.add_subplot(1,2,1)
    ax1 = fig.add_subplot(1,2,2)
    
    h= coesa.p_table(p)/1000
    ax0.plot(h, wspd, 'rs', markersize = 3, zorder=10, clip_on = True)
    ax0.set_xlabel('h [km]')
    ax0.set_ylabel('$V_w \quad [m/s]$')
    ax0.grid()
    
    ax1.plot(h, wdir, 'ro', markersize = 3,zorder=10, clip_on = True)
    ax1.set_xlabel('h [km]')
    ax1.set_ylabel('$W_D \quad [°]$')
    ax1.grid()
    upper_xlim = max(h)
    ax0.set_xlim(0,15)
    ax0.set_ylim(0, max(wspd))
    ax1.set_xlim(0,15)
    ax1.set_ylim(0,max(wdir))
    plt.subplots_adjust(left=0.1, right=0.97, top=0.97, bottom=0.13, wspace=0.25)
    
    if 'savefig' in kwargs:
        if kwargs.get('savefig'):
            plt.savefig(folder + 'sta_fig_'+str(len(h)), dpi = savefig_dpi)
    return(fig, [ax0,ax1])

def eval_fig_informe(h, wspd, wdir, **kwargs):
    '''
    DOC
    '''
    if 'folder' in kwargs:
        folder = kwargs.get('folder') + '/'
    else:
        folder = ''
    if 'savefig_dpi' in kwargs:
        savefig_dpi = kwargs.get('savefig_dpi')
    else:
        savefig_dpi = 200
    if 'labels' in kwargs:
        labels = kwargs.get('labels')
    else:
        labels = ['']*len(wspd)
    
    fig = plt.figure(figsize = (11,5))
    ax0 = fig.add_subplot(1,2,1)
    ax1 = fig.add_subplot(1,2,2)
    
    #colors
    colors = ['r', 'g', 'b']
    plot = {'extra_marker_color':'r', 'y_label_fsize':18}
    plot['extra_marker_size'] = 8
    plot['major_grid_alph'] = 0.72
    plot['minor_grid_alph'] = 0.3
    
    h /=1000
    for i in range(len(wspd)):
        ax0.plot(h, wspd[i], color = colors[i], linewidth = 1.5, label = labels[i])
        ax1.plot(h, wdir[i], color = colors[i], linewidth = 1.5, label = labels[i])
    
    ax0.set_xticks([1,5,10,15])
    ax1.set_xticks([1,5,10,15])
    ax1.set_yticks(np.round(np.arange(90,325,25),0))
    ax0.set_yticks(np.arange(5,50, 5))
    ax0.set_xticks([2.5, 7.5, 12.5], minor = True)
    ax1.set_xticks([2.5, 7.5, 12.5], minor = True)
    ax0.set_xlim(1,15)
    ax1.set_xlim(1,15)
    ax0.set_ylim(5,45)
    ax1.set_ylim(90,315)
    for loc_ax in fig.get_axes():
        loc_ax.grid(which='minor', alpha=plot['minor_grid_alph'])
        loc_ax.grid(which='major', alpha=plot['major_grid_alph'])
        loc_ax.set_xlabel('$h \ [km]$', fontsize=15)
    ax0.legend(loc='upper left')
    ax0.set_ylabel('$W_{speed} \ [m/s]$', fontsize=16)
    ax1.set_ylabel('$W_{dir} \ f/N \ [°]$', fontsize=16)
    plt.subplots_adjust(left=0.1, right=0.98, top=0.97, bottom=0.13, wspace=0.25)
    if 'savefig' in kwargs:
        if kwargs.get('savefig'):
            plt.savefig(folder + 'sta_fig_'+str(len(h)), dpi = savefig_dpi)
    return()

"""
------------------------------------------------------------------------------
Standalone
------------------------------------------------------------------------------
"""
if __name__ == '__main__':
    
    import META_handler as handler
    import matplotlib.pyplot as plt
    import CRU_nav_module as nav
    import META_krg_factory as krg

    
    folder = 'station_data/run'
    file_name = 'ARM00087596-data.txt.zip'
    loc_h, loc_spd, loc_dir, loc_alt, loc_lon = handler.read_station(file_name, folder, 'two', 1e3)
    part_fig_informe(loc_h, loc_spd, loc_dir, savefig=True, savefig_dpi = 800)
    

    # folder = 'WIND USA/USArun'
    # # for file_name in os.listdir(folder):
    # file_name = 'USM00074486-data.txt.zip'
    # # file_name = 'USM00072295-data.txt.zip'
    
    # loc_p, loc_spd, loc_dir, loc_alt, loc_lon = handler.read_station(file_name, folder, 'two', 1e3)

    # #Caso USA
    # # wind_modelSpeed = krg.exp_imp_modelo(0,'imp',{'folder':'WIND USA', 'name':'USA_SPD_3d_10e3'})
    # # wind_modelDir = krg.exp_imp_modelo(0, 'imp',{'folder':'WIND USA', 'name':'USA_DIR_3d'} )
    # # ruta_LATs =  [40.640752, 39.44, 33.948668]
    # # ruta_LONs = [-73.777911, -97.30, -118.410450]
    
    # #Caso ARBRA
    # ruta_LATs =  [-54.8396, -29,-3.041111]
    # ruta_LONs = [-68.3123, -63.05, -60.050556]
    
    # wind_modelSpeed = krg.exp_imp_modelo(0, 'imp', {'folder':'station_data', 'name':'full_BR_AR_WS_c02'})
    # wind_modelDir = krg.exp_imp_modelo(0, 'imp', {'folder':'station_data', 'name':'full_BR_AR_WD'})
    
    # # fwd_azi, back_azi,distance = nav.h_Di(ruta_LATs, ruta_LONs)
    
    # # x = np.linspace(0, distance, 17)
    # # LATs, LONs = [],[]
    # # for loc_x in x:
    # #     lLA, lLO = nav.nav_route(loc_x, distance, fwd_azi, ruta_LATs, ruta_LONs)[:2]
    # #     LATs.append(lLA)
    # #     LONs.append(lLO)
        
    # h = np.linspace(1e3,15e3,100)
    # w_spds, w_dirs = [],[]
    # for loc_lat, loc_lon in zip(ruta_LATs, ruta_LONs):
    #     spd = []
    #     wdir = []
    #     for loc_h in h:
    #         spd.append(wind_modelSpeed([loc_h, loc_lat, loc_lon])[0])
    #         wdir.append(wind_modelDir([loc_h, loc_lat, loc_lon])[0])
    #     w_spds.append(spd)
    #     w_dirs.append(wdir)
    # eval_fig_informe(h, w_spds, w_dirs, labels = ['USH','MID', 'MAO'], savefig=True, savefig_dpi=800)