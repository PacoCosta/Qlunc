# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 17:26:23 2020

@author: fcosta
"""
#%% Flags
flag_plot=1



#%% ################################################################
###################### __ Instances __ #################################

'''
Here the lidar device is made up with respective modules and components.
Instances of each component are created to build up the corresponding module. Once we have the components
we create the modules, adding up the components. In the same way, once we have the different modules that we
want to include in our lidar, we can create it adding up the modules we have been created.
Different lidars, atmospheric scenarios, components and modules can be created on paralel and can be combined
easily.
Example: ....
'''
#############  Optics ###################

# Components:

#Scanner1          = scanner(name           = 'Scan1',
#                           origin          = [0,0,0], #Origin
#                           focus_dist      = np.array([500,600,750,950,1250,1550,2100, 2950,3700]),
#                           sample_rate     = 10,
#                           theta           = np.array([0]*9),
#                           phi             = np.array([0]*9) ,
#                           stdv_focus_dist = .1,
#                           stdv_theta      = .1,
#                           stdv_phi        = .1,
#                           unc_func        = uopc.UQ_Scanner)       
Scanner1          = scanner(name           = 'Scan1',
                           origin          = [0,0,0], #Origin
                           focus_dist      = np.array([40]*24),
                           sample_rate     = 10,
                           theta           = np.array([7]*24), #np.linspace(0,125,24),#
                           phi             = np.arange(0,360,15),
                           stdv_focus_dist = 0.8,
                           stdv_theta      = 0.8,
                           stdv_phi        = 0.8,
                           unc_func        = uopc.UQ_Scanner)  
Scanner2          = scanner(name           = 'Scan2',
                           origin          = [0,0,0], #Origin
                           focus_dist      = np.array([80]*24),
                           sample_rate     = 10,
                           theta           = np.array([7]*24),
                           phi             = np.arange(0,360,15),
                           stdv_focus_dist = 0.3,
                           stdv_theta      = 0.3,
                           stdv_phi        = 0.1,
                           unc_func        = uopc.UQ_Scanner)       

Scanner3          = scanner(name           = 'Scan3',
                           origin          = [0,0,0], #Origin
                           focus_dist      = np.array([120]*24),
                           sample_rate     = 10,
                           theta           = np.array([7]*24),# np.linspace(0,180,24),#
                           phi             = np.arange(0,360,15) ,#np.array([0]*24),#
                           stdv_focus_dist = 6,
                           stdv_theta      = 1,
                           stdv_phi        = 4,
                           unc_func        = uopc.UQ_Scanner)       

Optical_circulator1 = optical_circulator (name = 'OptCirc1',
                                          insertion_loss = -100,
                                          unc_func = uopc.UQ_OpticalCirculator) 
# Module:

Optics_Module1 =  optics (name     = 'OptMod1',
                         scanner  = Scanner1,#None,#
                         optical_circulator = Optical_circulator1,
                         unc_func = uopc.sum_unc_optics) # here you put the function describing your uncertainty
Optics_Module2 =  optics (name     = 'OptMod2',
                         scanner  = Scanner2,
                         optical_circulator = Optical_circulator1,
                         unc_func = uopc.sum_unc_optics)
Optics_Module3 =  optics (name     = 'OptMod3',
                         scanner  = Scanner3,
                         optical_circulator = Optical_circulator1,
                         unc_func = uopc.sum_unc_optics)

#############  Photonics ###################

# Components:

OpticalAmplifier = optical_amplifier(name     = 'OA1',
                                     OA_NF    = 50 ,#'NoiseFigure.csv',#
                                     OA_Gain  = 30,
                                     unc_func = uphc.UQ_Optical_amplifier)

Photodetector    = photodetector(name             = 'Photo1',
                                 Photo_BandWidth  = 380e6,
                                 Load_Resistor    = 50,
                                 Photo_efficiency = .85,
                                 Dark_Current     = 5e-9,
                                 Photo_SignalP    = 1e-3,
                                 Power_interval   = np.arange(0,1000,.001), # power interval for the photodetector interval
                                 Gain_TIA         = 5e3,
                                 V_Noise_TIA      = 160e-6,
                                 unc_func         = uphc.UQ_Photodetector)

# Module:

Photonics_Module = photonics(name              = 'PhotoMod1',
                             photodetector     = Photodetector, # or None
                             optical_amplifier =  OpticalAmplifier,# None,#
                             unc_func          = uphc.sum_unc_photonics)

#############  Power #########################################

# Components:

PowerSource      = power_source(name      = 'P_Source1',
                                Inp_power = 1,
                                Out_power = 2e-3,
                                unc_func  = upwc.UQ_PowerSource)

Converter        = converter(name      = 'Conv1',
                             frequency = 100,
                             Conv_BW   = 1e5,
                             Infinit   = .8,
                             unc_func  = upwc.UQ_Converter)

# Module:

Power_Module     = power(name         = 'PowerMod1',
                         power_source = PowerSource,
                         converter    = Converter,
                         unc_func     = upwc.sum_unc_power)



########## Lidar general inputs #########################:
Lidar_inputs     = lidar_gral_inp(name        = 'Gral_inp1', 
                                  wave        = 1550e-9, 
                                  sample_rate = 2,       # Hz
                                  yaw_error   = 0,       # Degreesof rotation around z axis because of inclinometer errors
                                  pitch_error = 0,       # Degrees of rotation around y axis
                                  roll_error  = 0)       # Degrees of rotation around z axis


##########  LIDAR  #####################################

Lidar1 = lidar(name         = 'Caixa1',
               photonics    = Photonics_Module,
               optics       = Optics_Module1,
               power        = None,
               lidar_inputs = Lidar_inputs,
               unc_func     = ulc.sum_unc_lidar)
Lidar2 = lidar(name         = 'Caixa2',
               photonics    = Photonics_Module,
               optics       = Optics_Module2,
               power        = Power_Module,
               lidar_inputs = Lidar_inputs,
               unc_func     = ulc.sum_unc_lidar)

Lidar3 = lidar(name         = 'Caixa3',
               photonics    = Photonics_Module,
               optics       = Optics_Module3,
               power        = Power_Module,
               lidar_inputs = Lidar_inputs,
               unc_func     = ulc.sum_unc_lidar)

#%% Creating atmospheric scenarios:
Atmospheric_TimeSeries = True # This defines whether we are using a time series (True) or single values (False) to describe the atmosphere (T, H, rain and fog) 
                               # If so we obtain a time series describing the noise implemented in the measurement.
if Atmospheric_TimeSeries:
    Atmos_TS_FILE           = 'AtmosphericScenarios.csv'
    AtmosphericScenarios_TS = pd.read_csv(Atmos_TS_FILE,delimiter=';',decimal=',')
    Atmospheric_inputs={
                        'temperature' : list(AtmosphericScenarios_TS.loc[:,'T']),# [K]
                        'humidity'    : list(AtmosphericScenarios_TS.loc[:,'H']),# [%]
                        'rain'        : list(AtmosphericScenarios_TS.loc[:,'rain']),
                        'fog'         : list(AtmosphericScenarios_TS.loc[:,'fog']),
                        'time'        : list(AtmosphericScenarios_TS.loc[:,'t'])#for rain and fog intensity intervals might be introduced [none,low, medium high]
                        } 
    Atmospheric_Scenario=atmosphere(name        = 'Atmosphere1',
                                    temperature = Atmospheric_inputs['temperature'])
else:    

    Atmospheric_Scenario=atmosphere(name        = 'Atmosphere1',
                                    temperature = [1])

#%% Plotting:

# Plot parameters:
if flag_plot==1:
    
    plot_param={'axes_label_fontsize' : 16,
                'textbox_fontsize'    : 14,
                'title_fontsize'      : 24,
                'suptitle_fontsize'   : 23,
                'legend_fontsize'     : 12,
                'xlim'                : [-50,50],
                'ylim'                : [-50,50],
                'zlim'                : [0,130],
                'markersize'          : 5,
                'markersize_lidar'    : 9,
                'marker'              : '.',
                'markerTheo'          : '.b',
                'tick_labelrotation'  : 45}
    
#########    # Scanner pointing accuracy uncertainty:#################
    
#    Calculating inputs for plotting:
    Scanner_Data1 = Lidar1.optics.scanner.Uncertainty(Lidar1,Atmospheric_Scenario,cts)
    Scanner_Data2 = Lidar2.optics.scanner.Uncertainty(Lidar2,Atmospheric_Scenario,cts)
    Scanner_Data3 = Lidar3.optics.scanner.Uncertainty(Lidar3,Atmospheric_Scenario,cts)
    
    # Creating the figure and the axes
    fig,(axs1,axs2,axs3) = plt.subplots(1,3,sharey=False) 
#    ax.plot.errorbar(Lidar1.optics.scanner.focus_dist,,plot_param['marker'],markersize=6.5,label='stdv Distance')
    
    # fitting the results to a straight line
    z1 = np.polyfit(Lidar1.optics.scanner.focus_dist, Scanner_Data1['Simu_Mean_Distance'], 1) # With '1' is a straight line y=ax+b
    f1 = np.poly1d(z1)
    # calculate new x's and y's
    x_new1 = np.linspace(Lidar1.optics.scanner.focus_dist[0], Lidar1.optics.scanner.focus_dist[-1], 50)
    y_new1 = f1(x_new1)

    
    z2 = np.polyfit(Scanner2.theta, Scanner_Data2['Simu_Mean_Distance'], 1) # With '1' is a straight line y=ax+b
    f2 = np.poly1d(z2)
    # calculate new x's and y's
    x_new2 = np.linspace(Scanner2.theta[0], Scanner2.theta[-1], 50)
    y_new2 = f2(x_new2)

   
    z3 = np.polyfit(Scanner3.phi, Scanner_Data3['Simu_Mean_Distance'], 1) # With '1' is a straight line y=ax+b
    f3 = np.poly1d(z3)
    # calculate new x's and y's
    x_new3 = np.linspace(Scanner3.phi[0], Scanner3.phi[-1], 50)
    y_new3 = f3(x_new3)
    
     # Plotting:
    axs1.plot(x_new1,y_new1,'r-',label='Fitted curve1')
    axs1.errorbar(Lidar1.optics.scanner.focus_dist,Scanner_Data1['Simu_Mean_Distance'],yerr=Scanner_Data1['STDV_Distance'],label='Data1')
    axs2.plot(x_new2,y_new2,'r-',label='Fitted curve2')
    axs2.errorbar(Scanner2.theta,Scanner_Data2['Simu_Mean_Distance'],yerr=Scanner_Data2['STDV_Distance'],label='Data2')
    axs3.plot(x_new3,y_new3,'r-',label='Fitted curve3')
    axs3.errorbar(Scanner3.phi,Scanner_Data3['Simu_Mean_Distance'],yerr=Scanner_Data3['STDV_Distance'],label='Data3')
    
    #Title and axis labels for the different plots
    fig.suptitle('Mean Distance error and stdv of the Distance error [m]',fontsize=plot_param['suptitle_fontsize'])
    axs1.set_title('Variation with f.distance',fontsize=plot_param['title_fontsize'])
    axs1.set(xlabel='Focus Distance [m]',ylabel='Distance error [m]')
    axs1.yaxis.get_label().set_fontsize(plot_param['axes_label_fontsize'])
    axs1.xaxis.get_label().set_fontsize(plot_param['axes_label_fontsize'])
    axs2.set_title(r'Variation with $\theta$',fontsize=plot_param['title_fontsize'])
    axs2.set(xlabel=r'$\theta$'+' [°]')
    axs2.xaxis.get_label().set_fontsize(plot_param['axes_label_fontsize'])
    axs3.set_title(r'Variation with $\phi$',fontsize=plot_param['title_fontsize'])
    axs3.set(xlabel=r'$\phi$'+' [°]')
    axs3.xaxis.get_label().set_fontsize(plot_param['axes_label_fontsize'])
    axs1.set_ylim(0,10)
    axs2.set_ylim(0,10)
    axs3.set_ylim(0,10)
    # text box with the fitted polynomial on the plot
    axs1.text(np.min(x_new1),np.max(y_new1),'$y$={0:.3g}$x$+{1:.3g}'.format(z1[0],z1[1]),fontsize=plot_param['textbox_fontsize'])
    axs2.text(np.min(x_new2),np.max(y_new2),'$y$={0:.3g}$x$+{1:.3g}'.format(z2[0],z2[1]),fontsize=plot_param['textbox_fontsize'])
    axs3.text(np.min(x_new3),np.max(y_new3),'$y$={0:.3g}$x$+{1:.3g}'.format(z3[0],z3[1]),fontsize=plot_param['textbox_fontsize'])
#    

##############    Ploting scanner measuring points pattern #######################
    # Creating the figure and the axes
    fig,axs4 = plt.subplots()  
    axs4=plt.axes(projection='3d')
    
    axs4.plot([Lidar1.optics.scanner.origin[0]],[Lidar1.optics.scanner.origin[1]],[Lidar1.optics.scanner.origin[2]],'ob',label='{} coordinates [{},{},{}]'.format(Lidar1.LidarID,Lidar1.optics.scanner.origin[0],Lidar1.optics.scanner.origin[1],Lidar1.optics.scanner.origin[2]),markersize=plot_param['markersize_lidar'])
    axs4.plot(Scanner_Data1['MeasPoint_Coordinates'][0],Scanner_Data1['MeasPoint_Coordinates'][1],Scanner_Data1['MeasPoint_Coordinates'][2],plot_param['markerTheo'],markersize=plot_param['markersize'],label='Theoretical measuring point')
    axs4.plot(Scanner_Data1['NoisyMeasPoint_Coordinates'][0],Scanner_Data1['NoisyMeasPoint_Coordinates'][1],Scanner_Data1['NoisyMeasPoint_Coordinates'][2],plot_param['marker'],markersize=plot_param['markersize'],label='Distance error [m] = {0:.3g}$\pm${1:.3g}'.format(np.mean(Scanner_Data1['Simu_Mean_Distance']),np.mean(Scanner_Data1['STDV_Distance'])))

    axs4.plot(Scanner_Data2['MeasPoint_Coordinates'][0],Scanner_Data2['MeasPoint_Coordinates'][1],Scanner_Data2['MeasPoint_Coordinates'][2],plot_param['markerTheo'],markersize=plot_param['markersize'])
    axs4.plot(Scanner_Data2['NoisyMeasPoint_Coordinates'][0],Scanner_Data2['NoisyMeasPoint_Coordinates'][1],Scanner_Data2['NoisyMeasPoint_Coordinates'][2],plot_param['marker'],markersize=plot_param['markersize'],label='Distance error [m] = {0:.3g}$\pm${1:.3g}'.format(np.mean(Scanner_Data2['Simu_Mean_Distance']),np.mean(Scanner_Data2['STDV_Distance'])))
    
    axs4.plot(Scanner_Data3['MeasPoint_Coordinates'][0],Scanner_Data3['MeasPoint_Coordinates'][1],Scanner_Data3['MeasPoint_Coordinates'][2],plot_param['markerTheo'],markersize=plot_param['markersize'])
    axs4.plot(Scanner_Data3['NoisyMeasPoint_Coordinates'][0],Scanner_Data3['NoisyMeasPoint_Coordinates'][1],Scanner_Data3['NoisyMeasPoint_Coordinates'][2],plot_param['marker'],markersize=plot_param['markersize'],label='Distance error [m] = {0:.3g}$\pm${1:.3g}'.format(np.mean(Scanner_Data3['Simu_Mean_Distance']),np.mean(Scanner_Data3['STDV_Distance'])))
    
    axs4.set_xlabel('x [m]',fontsize=plot_param['axes_label_fontsize'])#,orientation=plot_param['tick_labelrotation'])
    axs4.set_ylabel('y [m]',fontsize=plot_param['axes_label_fontsize'])#,orientation=plot_param['tick_labelrotation'])
    axs4.set_zlabel('z [m]',fontsize=plot_param['axes_label_fontsize'])
#    
    axs4.set_title('Scanner pointing accuracy',fontsize=plot_param['title_fontsize'])
#    axs4.text(np.min(x_new3),np.max(y_new3),'$y$={0:.3g}$x$+{1:.3g}'.format(z3[0],z3[1]),fontsize=plot_param['textbox_fontsize'])
    axs4.legend()
#    axs4.text(np.min(x_new1),np.max(y_new1),'$y$={0:.3g}$x$+{1:.3g}'.format(z1[0],z1[1]))
    axs4.set_xlim3d(plot_param['xlim'][0],plot_param['xlim'][1])
    axs4.set_ylim3d(plot_param['ylim'][0],plot_param['ylim'][1])
    axs4.set_zlim3d(plot_param['zlim'][0],plot_param['zlim'][1])
#    plt.rcParams['legend.fontsize'] = plot_param['legend_fontsize']
    
   
###########   Plot photodetector noise   #############################       

    UQ_photo=Lidar1.photonics.photodetector.Uncertainty(Lidar1,Atmospheric_Scenario,cts) # Obtain the UQ photodetector dictionary wit SNR and UQ information
    
    Psax=10*np.log10(Lidar1.photonics.photodetector.Power_interval) 
    plt.figure()
    #plt.xscale('log',basex=10)
    #plt.yscale('log',basey=10)
    
    plt.plot(Psax,UQ_photo['SNR_data_photo']['SNR_Shot_Noise'][0],Psax,UQ_photo['SNR_data_photo']['SNR_Thermal'][0],Psax,UQ_photo['SNR_data_photo']['SNR_Dark_Current'][0],Psax,UQ_photo['SNR_data_photo']['SNR_TIA'][0])
    plt.xlabel('Input Signal optical power (dBm)',fontsize=plot_param['axes_label_fontsize'])
    plt.ylabel('SNR (dB)',fontsize=plot_param['axes_label_fontsize'])
    plt.legend(['Shot Noise','Thermal Noise','Dark current Noise','TIA Noise'],fontsize=plot_param['legend_fontsize'])#,'Total error [w]'])
    plt.title('SNR Photodetector',fontsize=plot_param['title_fontsize'])
    plt.grid(axis='both')
       





















    #
    #params = {'legend.fontsize': 'x-large',
    #          'figure.figsize': (15, 5),
    #         'axes.labelsize': 'x-large',
    #         'axes.titlesize':'x-large',
    #         'xtick.labelsize':'x-large',
    #         'ytick.labelsize':'x-large'}
    #pylab.rcParams.update(params)
    #ax.set_legend('stdv_rho  {}'.format(stdv_rho))
    #ax.quiver(*origin,xcart,ycart,zcart)
    #    