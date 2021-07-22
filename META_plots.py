# -*- coding: utf-8 -*-
"""
Created on Wed May 26 14:42:50 2021

@author: Ramon Velazquez
"""

import os
import numpy as np
import matplotlib.pyplot as plt

def figure_gen(plot_opts,**kwargs):
    fig, ax = plt.subplots()
    ax.set_xlabel(plot_opts['xlabel'])
    ax.set_ylabel( plot_opts['ylabel'])
    if plot_opts['grid']:
        ax.grid()
    return(fig, ax)
    
def figure_finish(fig, ax, plot_opts):
    if 'legend' in plot_opts: 
        if plot_opts['legend']:
            ax.legend(title=plot_opts['legend_title'])
    if plot_opts['save']:
        try:
            s_name = plot_opts['ruta'] + "/" + plot_opts['filecode']
            plt.savefig(s_name, bbox_inches='tight')
        except:
            plot_opts['ruta'] = 'default_METAfigs'
            if not plot_opts['ruta'] in os.listdir():
                os.makedirs(plot_opts['ruta'])
            s_name = plot_opts['ruta'] + "/" + plot_opts['filecode']
            plt.savefig(s_name, bbox_inches='tight')
    if plot_opts['close']:
        plt.close()

def ov_plot(fig, ax, data_x,data_y, lab, mode, **kwargs):
    if mode == 'dots':
        ax.plot(data_x, data_y, 'ro', label = lab)
    elif mode == 'normal':
        ax.plot(data_x, data_y, label = lab)
    else:
        raise NameError('Definir correctamente modo de ploteo')

if __name__ == '__main__':
    import NMETA_handler as handler
    
    plot_opciones = handler.gen_plot_opts('presión','wspeed',1,ruta='h',filecode='gg', close=True)

    a = np.linspace(0,10,10)
    b = 2*a
    
    loc_fig, loc_ax = figure_gen(plot_opciones)
    ov_plot(loc_fig,loc_ax,a,b,'hola','dots')
    figure_finish(loc_fig,loc_ax,plot_opciones)
