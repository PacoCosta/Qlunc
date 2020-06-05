# -*- coding: utf-8 -*-
"""
Created on Thu May 21 00:11:03 2020

@author: fcosta
"""

from Qlunc_ImportModules import *
#import Qlunc_Help_standAlone as Salone
import Qlunc_inputs

#%%Naming data to make it easier:

#Atmosphere:
temp        = inputs.atm_inp.Atmospheric_inputs['temperature']
hum         = inputs.atm_inp.Atmospheric_inputs['humidity']
wave        = inputs.lidar_inp.Lidar_inputs['Wavelength']

#Power
conv_noise  = inputs.power_inp.Converter_uncertainty_inputs['Converter_noise']
conv_oc     = inputs.power_inp.Converter_uncertainty_inputs['Converter_OtherChanges']
conv_losses = inputs.power_inp.Converter_uncertainty_inputs['Converter_losses']
ps_noise    = inputs.power_inp.PowerSource_uncertainty_inputs['Power_source_noise']
ps_oc       = inputs.power_inp.PowerSource_uncertainty_inputs['Power_source_OtherChanges']

#photonics
amp_noise   = inputs.photonics_inp.Optical_amplifier_uncertainty_inputs['Optical_amplifier_noise']
amp_oc      = inputs.photonics_inp.Optical_amplifier_uncertainty_inputs['Optical_amplifier_OtherChanges']
#amp_noise_figure = Qlunc_UQ_Photonics_func.FigNoise(user_inputs,inputs,cts)
ls_noise    = inputs.photonics_inp.LaserSource_uncertainty_inputs['Laser_source_noise']
ls_oc       = inputs.photonics_inp.LaserSource_uncertainty_inputs['Laser_source_OtherChanges']
PHOTO_BW=inputs.photonics_inp.Photodetector_inputs['Photodetector_Bandwidth']
PHOTO_RL=inputs.photonics_inp.Photodetector_inputs['Photodetector_RL']
PHOTO_n=inputs.photonics_inp.Photodetector_inputs['Photodetector_Efficiency']
PHOTO_Id=inputs.photonics_inp.Photodetector_inputs['Photodetector_DarkCurrent']
PHOTO_SP=inputs.photonics_inp.Photodetector_inputs['Photodetector_Signal_power']
TIA_G=inputs.photonics_inp.TIA_inputs['Gain_TIA']
TIA_V_noise=inputs.photonics_inp.TIA_inputs['V_noise_TIA']

#telescope
tele_cl     = inputs.optics_inp.Telescope_uncertainty_inputs['Telescope_curvature_lens']
tele_oc     = inputs.optics_inp.Telescope_uncertainty_inputs['Telescope_OtherChanges']
tele_aberr  = inputs.optics_inp.Telescope_uncertainty_inputs['Telescope_aberration']
tele_losses = inputs.optics_inp.Telescope_uncertainty_inputs['Telescope_losses']


# %%Getting scenarios:
def Get_Scenarios():
    # Initialazing variables:
    global Scenarios
    Scenarios=dict()
    Temperature=[]       
    type_noise = [[wave]]
    Val        = ()
    Names_Val=['VAL_WAVE'] # initialize with wave because is a variable common to many component noises.
    VAL_T=None # initialize this values in None, as well as the values in 'add_typeN' to pass it as empty values to fill them in the loop when getting Scenarios!!!!!
    VAL_H=None
    # We need to create the cases we want to loop over. For that are the next steps to create 'type_noise' and 'Val'.
    # First create a dictionary (add_typeN) to identify type of noise with variables we want to use to loop over.
    
    add_typeN={'Power_source_noise'  :[[[ps_noise],'VAL_NOISE_POWER_SOURCE',[None]],   [[ps_oc],'VAL_OC_POWER_SOURCE',[None] ]]  ,
                                                                     
               'Converter_losses'    :[[[conv_losses],'VAL_CONVERTER_LOSSES',[None] ] ] ,           
               'Converter_noise'     :[[[conv_noise],'VAL_NOISE_CONVERTER',[None]],[[conv_oc],'VAL_OC_CONVERTER',[None]]],
                                                                   
               'Photodetector_noise' :[[[PHOTO_BW],'VAL_PHOTO_BW',[None]],[[PHOTO_RL], 'VAL_PHOTO_RL',[None]],
                                       [[PHOTO_n], 'VAL_PHOTO_n',[None]  ] ,[[PHOTO_Id], 'VAL_PHOTO_Id',[None]],
                                       [[PHOTO_SP], 'VAL_PHOTO_SP',[None]]],
                                       
               'TIA_noise'             :[[[TIA_G],'VAL_GAIN_TIA',[None]],[[TIA_V_noise],'VAL_V_NOISE_TIA',[None]]] ,                                     
#               'Optical_amplifier_fignoise'  :[[[amp_noise_figure], 'VAL_NOISE_FIG',[inputs.VAL.VAL_NOISE_FIG]  ]  ],
               'Optical_amplifier_noise'     :[[[amp_oc],  'VAL_OC_AMPLI',[None]],   [[amp_noise],'VAL_NOISE_AMPLI',[None]] ],  
                                                                   
               'Laser_source_noise'  :[[[ls_noise],'VAL_NOISE_LASER_SOURCE',[None]], [[ls_oc],'VAL_OC_LASER_SOURCE',[None] ]      ],
                                                                    
               'Telescope_noise'     :[[[tele_aberr],'VAL_ABERRATION_TELESCOPE',[None]],[[tele_oc],'VAL_OC_TELESCOPE',[None]],
                                       [[tele_cl], 'VAL_CURVE_LENS_TELESCOPE',[None]]],
                                                                     
                                                                    
               'Telescope_losses'    :[[[tele_losses],'VAL_LOSSES_TELESCOPE',[None]]]}              

    
 
#    type_noise = [wave,conv_noise,conv_oc,conv_losses,ps_noise,ps_oc,amp_noise,amp_oc,amp_noise_figure,ls_noise,ls_oc,photo_noise,photo_oc,
#                  tele_cl,tele_oc,tele_aberr,tele_losses]
    #%%Loop to create typeN and Val depending on the user modules/components inputs):

    for user_typeN in list(itertools.chain(*user_inputs.user_itype_noise)): # For user selection noises
        for i in range(len(add_typeN[user_typeN])):
            type_noise.append(((add_typeN[user_typeN][i][0]))) # obtaining the values we want to loop over
            Names_Val.append(((add_typeN[user_typeN][i][1])))  # obtaining the names to create the dictionary Scenarios, to pass as **Scenarios (in this way we can dinamically vary the variables of the functions)
            Val=Val+((tuple(add_typeN[user_typeN][i][2])))     # obtaining the number of none´s we need to run the loop
            

    # Main loop to go over all variables to create the cases:############### 
    # FIGURE NOISE IS NOT INCLUDED IN THE SCENARIOS BECAUSE IS NOT NEEDED FOR ANY CALCULATION. IT IS JUST A 'NOISE' MORE TO ADD AT THE END, 
    # WHEN BUILDING THE DATA FRAME  
#    pdb.set_trace()
    
    for i in list(SA.flatten('VAL_T','VAL_H',Names_Val)):
        Scenarios[i]=[]
    
    for VAL_T,VAL_H in zip (temp, hum):
            for Val in itertools.product(*list(itertools.chain(*type_noise))):
                for k,v in zip (Scenarios.keys(), (VAL_T,)+(VAL_H,)+Val): # for loop to build up the dictionary 'Scenarios'. If user includes some variability (dependency on wavelength e.g. of any variable)              
                    Scenarios[k].append(v)
#                Scenarios.append(list(flatten(inputs.VAL.VAL_T,inputs.VAL.VAL_H,inputs.VAL.VAL_WAVE,inputs.VAL.VAL_NOISE_FIG,Val))) #
                Temperature.append([VAL_T])

    return Scenarios,Temperature
#%% Running the different cases. If user has included it, the case is evaluated: Can I do this in a loop??????
def Get_Noise(module,Scenarios):    
    METHODS={}
    if module == 'Power':
        Func = {'Power_source_noise'  : Qlunc_UQ_Power_func.UQ_PowerSource,
                'Converter_noise'     : Qlunc_UQ_Power_func.UQ_Converter,
                'Converter_losses'    : Qlunc_UQ_Power_func.Losses_Converter,
                }
    
    elif module== 'Photonics':
        Func = {'Laser_source_noise'      : Qlunc_UQ_Photonics_func.UQ_LaserSource,
                'Photodetector_noise'     : Qlunc_UQ_Photonics_func.UQ_Photodetector,
                'Optical_amplifier_noise' : Qlunc_UQ_Photonics_func.UQ_Optical_amplifier, 
                }
        if 'Optical_amplifier' in list(SA.flatten(user_inputs.user_icomponents)): 
            # For methods that we want them to appear in estimations although they´re not in the 'user_inputs.user_itype_noise'(user options) list like the optical amplifier noise figure
            # wich is estimated automatically when introducing the optical amplifier as a component and is not involved in any calculations:
            METHODS.setdefault('Optical_amplifier_fignoise',Qlunc_UQ_Photonics_func.FigNoise(user_inputs,inputs,direct,**Scenarios)) 
    
    elif module=='Optics':
        Func = {'Telescope_noise'     : Qlunc_UQ_Optics_func.UQ_Telescope,
                'Telescope_losses'    : Qlunc_UQ_Optics_func.Losses_Telescope
                }
           
    for k,v in Func.items():
        if k in list(SA.flatten(user_inputs.user_itype_noise)):  
            METHODS.setdefault(k,list(SA.flatten(Func[k](user_inputs,inputs,cts,**Scenarios))))
#    pdb.set_trace()
    return METHODS



