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

# class plot_opts():
#     '''Clase genérica para opciones de ploteos. UPDATE al 060521 \n
# 	Methods: labs_opts: Títulos y demás \n
# 		    ie_opts: Opciones de guardado y muestra'''
# 	def labs_opts(self, title, suptitle, xlabel, ylabel, leg_title):
# 		self.title = title
# 		self.suptitle = suptitle
# 		self.xlabel = xlabel
# 		self.ylabel = ylabel
# 		self.leg_title = leg_title
# 	def ie_opts(self,save,close, filecode, folder)
# 		self.save = bool(save)
# 		self.close = bool(close)
# 		self.filecode = filecode
# 		self.folder = folder
# 		self.status = True
# 	def flags(self,wind):
# 		self.wind = bool(wind)
##############################################
def comparativeN_plot(N,consumo,tiempos, plot_opts):
    ''' IN PROGRESS '''   
    if wind_ind_plot_opts:

        pass
    
    rel_incr = consumo[1:]/consumo[:-1] - 1
    rel_N = np.diff(N)
    
    fig, ax = plt.subplots()
    ax.plot(rel_N, rel_incr, marker = 'x', label = ' OPT c/VIENTO')
    ax.set_xlabel(r'$\Delta$ N')
    ax.set_ylabel(r'$\Delta W_f \%$')
    ax.grid()
    ax.legend()
    fig.suptitle('Comparativa incremento de consumo vs incremento de N')
    if plot_opts.save:
        s_name = plot_opts.folder + "/" + plot_opts.filecode + "_incrplot"
        plt.savefig(s_name)
    if plot_opts.close:
        plt.close()
    
    fig, ax = plt.subplots()
    ax.plot(N,consumo, marker='o', label = 'OPT c/VIENTO')
    ax.set_xlabel('N steps')
    ax.set_ylabel('W_f [lb]')
    ax.set_xscale('log')
    ax.grid()
    ax.legend()
    fig.suptitle('Comparativa consumo vs N')
	
    if plot_opts.save:
        s_name = plot_opts.folder + "/" + plot_opts.filecode + "_WvNplot"
        plt.savefig(s_name)
    if plot_opts.close:
        plt.close()    

    fig, ax = plt.subplots()
    ax.plot(N, tiempos, marker = 'o', label = 'OPT c/VIENTO')
    ax.set_xlabel('N steps')
    ax.set_ylabel('t [s]')
    ax.grid()
    ax.legend()
    ax2 = ax.twinx()
    ax2.plot(N, tiempos/3600)
    ax2.set_ylabel('t [horas]')
    fig.suptitle('Comparativa tiempo vs N')
    if plot_opts.save:
        s_name = plot_opts.folder + "/" + plot_opts.filecode + "_tvNplot"
        plt.savefig(s_name)
    if plot_opts.close:
           plt.close()

################################################

# def travel_plot(y_prof, loc_y_prof, x_prof, xtrep_prof,plot_opts,**kwargs):
#     x_scale = 1
# # 	x_scala = 1
# #     if 'UMx' in kwargs:
# #         x_units = kwargs.get('UMx')
# #         x_units == 'ft':
# # 		x_scala = 0.000189394
#     # full_x = np.array([x_prof[0])
#     # full_y = np.array([y_prof[0])
#     for i in range(len(xtrep_prof)):
#         full_x = np.append(xtrep_prof[i]+x_prof[i])
#         full_x = np.append(x_prof[i+1])
#         full_y = np.append(loc_y_prof[i])
#         full_y = np.append(y_prof[i+1])
#     fig, ax = plt.subplots()
#     ax.plot(full_x*x_scala, full_y, marker = 'x', label = plot_opts.label)
#     ax.set_xlabel(plot_opts.xlabel)
#     ax.set_ylabel(plot_opts.ylabel)
#     ax.set_title(plot_opts.title)
#     fig.suptitle(plot_opts.suptitle)
#     ax.grid()
#     ax.legend()
#     if plot_opts.save:
#         s_name = plot_opts.folder + "/" + plot_opts.filecode + "_hplot"
#         plt.savefig(s_name)
#     if plot_opts.close:
#         plt.close()

#######################################################
def plot_show_export(opt, res_data, **kwargs):
    '''Función principal para ploteo global y completo \n
    opts, data, **kwargs'''
    scale_factor = {'x_um':'ft','x_sf':0.000189394, 'W_f_um':'lb'}
    
    if 'scale_factor' in kwargs:
        scale_factor = kwargs.get('scale_factor')
        if scale_factor['x_um'] == 'mi':
            scale_factor['x_sf'] = 1/0.000189394
        #elif:
            #etc...

#Ploteo de h profile
    fig,ax = plt.subplots()
    ax.plot(res_data['x_prof']*scale_factor['x_sf'], res_data['h_prof'],marker='o', label = 'perfil optimizado')
    ax.set_title("Perfil de vuelo crucero - x vs h: "+str(res_data['N']))
    ax.set_xlabel("dist "+scale_factor['x_um'])
    ax.set_ylabel("h [ft]")
    ax.grid()
    ax.legend(title='Wind status:' + str(res_data['wind_sim']))
    fig.suptitle(r'$W_f$' + ': ' + str(np.round(res_data['W_f'],2)) + scale_factor['W_f_um'])
    if opt['save']:
        s_name = opt['ruta'] + "/" + opt['filecode'] + "_hplot"
        plt.savefig(s_name)
    if opt['close']:
        plt.close()

#Ploteo de Va profile
    fig,ax = plt.subplots()
    ax.plot(res_data['x_prof']*scale_factor['x_sf'], res_data['Va_prof'],marker='o', label = 'perfil optimizado')
    ax.set_title("Perfil de vuelo crucero - x vs Va: "+str(res_data['N']))
    ax.set_xlabel("dist "+scale_factor['x_um'])
    ax.set_ylabel("Va [ft/s]")
    ax.grid()
    ax.legend(title='Wind status:' + str(res_data['wind_sim']))
    fig.suptitle(r'$W_f$' + ': ' + str(np.round(res_data['W_f'],2)) + scale_factor['W_f_um'])
    if opt['save']:
        s_name = opt['ruta'] + "/" + opt['filecode'] + "_Vaplot"
        plt.savefig(s_name)
    if opt['close']:
        plt.close()

        
#Ploteo de ts profile
    fig,ax = plt.subplots()
    ax.plot(res_data['x_prof']*scale_factor['x_sf'], res_data['ts_prof'],marker='o', label = 'perfil optimizado')
    ax.set_title("Perfil de vuelo crucero - x vs ts: "+str(res_data['N']))
    ax.set_xlabel("dist "+scale_factor['x_um'])
    ax.set_ylabel("ts [adim]")
    ax.grid()
    ax.legend(title='Wind status:' + str(res_data['wind_sim']))
    fig.suptitle(r'$W_f$' + ': ' + str(np.round(res_data['W_f'],2)) + scale_factor['W_f_um'])
    if opt['save']:
        s_name = opt['ruta'] + "/" + opt['filecode'] + "_tsplot"
        plt.savefig(s_name)
    if opt['close']:
        plt.close()
        
#Ploteo de WSpeed profile
    fig,ax = plt.subplots()
    ax.plot(res_data['x_prof'][:-1]*scale_factor['x_sf'], res_data['Vw_prof'],marker='o', label = 'perfil optimizado')
    ax.set_title("Perfil de vuelo crucero - x vs Vw: "+str(res_data['N']))
    ax.set_xlabel("dist "+scale_factor['x_um'])
    ax.set_ylabel("WSpeed [ft/s]")
    ax.grid()
    ax.legend(title='Wind status:' + str(res_data['wind_sim']))
    fig.suptitle(r'$W_f$' + ': ' + str(np.round(res_data['W_f'],2)) + scale_factor['W_f_um'])
    if opt['save']:
        s_name = opt['ruta'] + "/" + opt['filecode'] + "_Vwplot"
        plt.savefig(s_name)
    if opt['close']:
        plt.close()
        
        
#Ploteo de WDir profile
    fig,ax = plt.subplots()
    ax.plot(res_data['x_prof'][:-1]*scale_factor['x_sf'], res_data['VD_prof'],marker='o', label = 'perfil optimizado')
    ax.set_title("Perfil de vuelo crucero - x vs Va: "+str(res_data['N']))
    ax.set_xlabel("dist "+scale_factor['x_um'])
    ax.set_ylabel("Wind fir from N [deg]")
    ax.grid()
    ax.legend(title='Wind status:' + str(res_data['wind_sim']))
    fig.suptitle(r'$W_f$' + ': ' + str(np.round(res_data['W_f'],2)) + scale_factor['W_f_um'])
    if opt['save']:
        s_name = opt['ruta'] + "/" + opt['filecode'] + "_Vdplot"
        plt.savefig(s_name)
    if opt['close']:
        plt.close()
    
    #IN PROGRESS:
            #PLOTEO DE DEMÁS PERFILES
    return('fin de ploteo')

# def comp_plot(N,consumo, tiempo):
#     rel_incr = consumo[1:]/consumo[:-1] - 1
#     rel_N = np.diff(N)
    
#     fig, ax = plt.subplots()
#     ax.plot(rel_N, rel_incr, marker = 'x', label = ' OPT c/VIENTO')
#     ax.set_xlabel(r'$\Delta$ N')
#     ax.set_ylabel(r'$\Delta W_f \%$')
#     ax.grid()
#     ax.legend()
#     fig.suptitle('Comparativa incremento de consumo vs incremento de N')
    
#     fig, ax = plt.subplots()
#     ax.plot(N,consumo, marker='o', label = 'OPT c/VIENTO')
#     ax.set_xlabel('N steps')
#     ax.set_ylabel('W_f [lb]')
#     ax.set_xscale('log')
#     ax.grid()
#     ax.legend()
#     fig.suptitle('Comparativa consumo vs N')
    
#     fig, ax = plt.subplots()
#     ax.plot(N, tiempos, marker = 'o', label = 'OPT c/VIENTO')
#     ax.set_xlabel('N steps')
#     ax.set_ylabel('t [s]')
#     ax.grid()
#     ax.legend()
#     ax2 = ax.twinx()
#     ax2.plot(N, tiempos/3600)
#     ax2.set_ylabel('t [horas]')
#     fig.suptitle('Comparativa tiempo vs N')