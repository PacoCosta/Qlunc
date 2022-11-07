# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 19:57:05 2020
@author: fcosta

Francisco Costa García
University of Stuttgart(c) 

###############################################################################
###################### __ Classes __ ##########################################
  
Creating components, modules and lidar classes. 
The command class is used to create digital "objects", representing the lidar 
components, and store necessary information to calculate uncertainties coming 
from hardware and data processing methods. 

`unc_func` contains the functions calculating the uncertainty for each
component, module and/or lidar system.
It is defined as a python module, so users can define their own uncertainty 
functions and implement them easily just pointing towards a different python 
module. 

Flags, general constants and atmospheric scenarios used along the calculations 
are also treated as classes. User should instantiate all, but the general 
constants.


How is the code working?

If user wants to implement another component/module s/he should create a class. 

For example, we might want build up a lidar and user wants to include a 'power'
module which, in turn contains an UPS (uninterruptible power supply) with 
certain parameter values, e.g. output power and output voltage. Let's call them
Pout and Vout. 

1) Create the `classes`:
    
So we create the class `UPS`:
    
def UPS():
    def __init__(self,PowerOutput,VoltageOutput,Uncertainty)
        
        self.Pout     = PowerOutput
        self.Vout     = VoltageOutput
        self.unc_func = Uncertainty

And also the class `power`, including the UPS component:

def power():
    def __init__UPS (self, U_PowerSupply,Uncertainty)
        self.UPS     = U_PowerSupply
        self.unc_fun = Uncertainty 

Then, the lidar is created (in this simple example) by including the module in 
a lidar class:

class lidar():
      def __init__ (self, Power_Module,Uncertainty)
          self.PowerMod = Power_Module
          self.unc_fun  = Uncertainty

Setting an atmospheric scenario is also needed:
class atmos_sc():
    def __init__ (self, Temperature, Humidity):
        self.T = Temperature
        self.H = Humidity
    
2) Instantiate the classes

Instantiating the component class:
UPS_1 = UPS(Pout     = 500, % in watts
            Vout     = 24,  % in volts
            unc_func = function calculating uncertainties)

Instantiating the module class to create the `Power` object:
Power_1 = power(Power_Module = UPS_1,
                unc_func      = function calculating uncertainties) 
        

Instantiating the lidar class:
Lidar_1 = lidar(Power_Module = Power_1,
                unc_func     = function calculating uncertainties)

So we have created a lidar digital twin with its first module, the `power` 
module, which in turn contains a component, the uninterruptible power supply.

(How to ask for uncertainties...)

Qlunc uses GUM (Guide to the expression of Uncertainties in Measurement) 
model to calculate uncertainty expansion.  
  
"""

#%% Constants:
class cts():
    k = 1.38064852e-23 # Boltzman constant:[m^2 kg s^-2 K^-1]
    h = 6.6207004e-34 # Plank constant [m^2 kg s^-1]
    e = 1.60217662e-19 # electron charge [C]
    c = 2.99792e8 #speed of light [m s^-1]


#%% LIDAR COMPONENTS
# Component Classes:
class photodetector():
    def __init__(self,name,Photo_BandWidth,Load_Resistor,Photo_efficiency,Dark_Current,Photo_SignalP,Active_Surf,Power_interval,Gain_TIA,V_Noise_TIA,unc_func):
                 self.PhotodetectorID  = name 
                 self.BandWidth        = Photo_BandWidth 
                 self.Load_Resistor    = Load_Resistor 
                 self.Efficiency       = Photo_efficiency
                 self.DarkCurrent      = Dark_Current
                 self.SignalPower      = Photo_SignalP
                 self.Active_Surf      = Active_Surf
                 self.Power_interval   = Power_interval
                 self.Gain_TIA         = Gain_TIA
                 self.V_Noise_TIA      = V_Noise_TIA
                 self.Uncertainty      = unc_func
                 print('Created new photodetector: {}'.format(self.PhotodetectorID))
        
class optical_amplifier():
    def __init__(self,name,NoiseFig,OA_Gain,OA_BW,Power_interval,unc_func):
                 self.Optical_AmplifierID = name
                 self.NoiseFig            = NoiseFig
                 self.OA_Gain             = OA_Gain
                 self.OA_BW               = OA_BW
                 self.Power_interval      = Power_interval
                 self.Uncertainty         = unc_func
                 print ('Created new optical amplifier: {}'.format(self.Optical_AmplifierID))
                 

class analog2digital_converter():
    def __init__(self,name,nbits,vref,vground,q_error,ADC_bandwidth,unc_func):
                 self.ADCID = name
                 self.nbits =nbits
                 self.vref = vref
                 self.vground = vground
                 self.q_error = q_error
                 self.BandWidth = ADC_bandwidth
                 self.Uncertainty = unc_func
                 print('Created new ADC: {}'.format(self.ADCID))
                 
class acousto_optic_modulator():
    def __init__(self,name,insertion_loss,unc_func):
                 self.AOMID          = name
                 self.insertion_loss = insertion_loss
                 self.Uncertainty   = unc_func
                 print ('Created new AOM: {}'.format(self.AOMID))
        
class power_source(): # Not included yet in Version Qlunc v-0.9 calculations
    def __init__(self,name,Inp_power,Out_power,unc_func):
                 self.Power_SourceID = name
                 self.Input_power    = Inp_power
                 self.Output_power   = Out_power
                 self.Uncertainty    = unc_func
                 print('Created new power source: {}'.format(self.Power_SourceID))

class laser(): # Not included yet in Version Qlunc v-0.9 calculations
    def __init__(self,name,Wavelength,stdv_wavelength,Laser_Bandwidth,Output_power,unc_func,RIN,conf_int):
                 self.LaserID         = name
                 self.Wavelength      = Wavelength
                 self.stdv_wavelength = stdv_wavelength
                 self.BandWidth       = Laser_Bandwidth
                 self.conf_int     = conf_int
                 self.Output_power    = Output_power
                 self.RIN             = RIN
                 self.Uncertainty     = unc_func
                 print('Created new laser: {}'.format(self.LaserID))        

class converter(): # Not included yet in Version Qlunc v-0.9 calculations
    def __init__(self,name,frequency,Conv_BW,Infinit,unc_func):
                 self.ConverterID = name
                 self.Frequency   = frequency
                 self.BandWidth   = Conv_BW
                 self.Infinit     = Infinit
                 self.Uncertainty = unc_func
                 print('Created new converter: {}'.format(self.ConverterID))

class scanner():
    def __init__(self,name,Href,time_pattern,N_Points,N_MC,time_point,scanner_type,pattern,lissajous_param,origin,sample_rate,focus_dist,cone_angle,azimuth,stdv_location,stdv_focus_dist,stdv_cone_angle,stdv_azimuth,correlations,unc_func):
                 self.ScannerID       = name
                 self.time_pattern    = time_pattern
                 self.N_Points        = N_Points
                 self.Href            = Href
                 self.N_MC            = N_MC
                 self.time_point      = time_point 
                 self.scanner_type    = scanner_type
                 self.origin          = origin
                 self.pattern         = pattern
                 self.lissajous_param = lissajous_param
                 self.sample_rate     = sample_rate
                 self.focus_dist      = focus_dist
                 self.cone_angle      = cone_angle
                 self.azimuth         = azimuth
                 self.stdv_location= stdv_location
                 self.stdv_focus_dist = stdv_focus_dist
                 self.stdv_cone_angle = stdv_cone_angle
                 self.stdv_azimuth    = stdv_azimuth                 
                 self.correlations    = correlations
                 self.Uncertainty     = unc_func      
                 print('Created new scanner: {}'.format(self.ScannerID))

class measurement_points():
    def __init__(self,coord_meas_point):
        self.coord_meas_point=coord_meas_point
        print('Measurement points created')
            

class optical_circulator():
    def __init__(self,name, insertion_loss,SNR,unc_func):#,isolation,return_loss): 
                 self.Optical_CirculatorID = name
                 self.insertion_loss       = insertion_loss # max value in dB
                 self.SNR                  = SNR #[dB]
        #        self.isolation            = isolation
        #        self.return_loss          = return_loss
                 self.Uncertainty          = unc_func
                 print ('Created new optical circulator: {}'.format(self.Optical_CirculatorID))

class telescope():
    def __init__(self,name,aperture,stdv_aperture,focal_length,fiber_lens_d,fiber_lens_offset,effective_radius_telescope,output_beam_radius,stdv_fiber_lens_d,stdv_fiber_lens_offset,stdv_focal_length,stdv_eff_radius_telescope,tau,tau_meas,stdv_tau, stdv_tau_meas,unc_func):
                self.TelescopeID                = name
                self.aperture                   = aperture
                self.stdv_aperture              = stdv_aperture
                self.focal_length               = focal_length
                self.fiber_lens_d               = fiber_lens_d
                self.fiber_lens_offset          = fiber_lens_offset
                self.effective_radius_telescope = effective_radius_telescope
                self.output_beam_radius         = output_beam_radius
                self.stdv_fiber_lens_d          = stdv_fiber_lens_d
                self.stdv_fiber_lens_offset     = stdv_fiber_lens_offset
                self.stdv_focal_length          = stdv_focal_length
                self.stdv_eff_radius_telescope  = stdv_eff_radius_telescope
                self.tau                        = tau
                self.tau_meas                   = tau_meas
                self.stdv_tau                   = stdv_tau
                self.stdv_tau_meas              = stdv_tau_meas                
                self.Uncertainty                = unc_func
                print('Created new telescope: {}'.format(self.TelescopeID))

class probe_volume():
    def __init__(self,name,extinction_coef,unc_func):
                 self.ProbeVolumeID              = name         
                 self.extinction_coef            = extinction_coef
                 self.Uncertainty                = unc_func
                 print('Class "Probe volume" created')

#%% LIDAR MODULES
                 
# Modules classes:
class photonics():
    def __init__(self,name,photodetector,optical_amplifier,laser,acousto_optic_modulator,unc_func):
                 self.PhotonicModuleID        = name
                 self.photodetector           = photodetector
                 self.optical_amplifier       = optical_amplifier
                 self.laser                   = laser
                 self.acousto_optic_modulator = acousto_optic_modulator
                 self.Uncertainty             = unc_func 
                 print('Created new photonic module: {}'.format(self.PhotonicModuleID))

class power(): # Not included yet in Version Qlunc v-0.9 calculations
    def __init__(self,name,power_source,converter,unc_func):
                 self.PowerModuleID  = name
                 self.power_source  = power_source
                 self.converter     = converter
                 self.Uncertainty   = unc_func  
                 print('Created new power module: {}'.format(self.PowerModuleID))

class optics():
    def __init__(self,name,scanner,optical_circulator,telescope,probe_volume,unc_func):
                 self.OpticsModuleID     = name
                 self.scanner            = scanner
                 self.optical_circulator = optical_circulator
                 self.telescope          = telescope
                 self.probe_volume       = probe_volume
                 self.Uncertainty        = unc_func 
                 print('Created new optic module: {}'.format(self.OpticsModuleID))

class signal_processor():
    def __init__(self,name,analog2digital_converter,unc_func): #f_analyser
                 self.SignalProcessorModuleID = name
                 self.analog2digital_converter = analog2digital_converter
                 # self.f_analyser =f_analyser
                 self.Uncertainty = unc_func
                 print('Created new signal processor module: {}'.format(self.SignalProcessorModuleID))


#%% Atmosphere object:
class atmosphere():
    def __init__(self,name,temperature,Hg,PL_exp,wind_direction, wind_tilt, Vref):
                 self.AtmosphereID   = name
                 self.temperature    = temperature
                 self.PL_exp         = PL_exp
                 self.Vref           = Vref
                 self.wind_direction = wind_direction
                 self.Hg             = Hg
                 self.wind_tilt     = wind_tilt                
                 print('Created new atmosphere: {}'.format(self.AtmosphereID))


#%% Creating lidar general data class:
class lidar_gral_inp():
    def __init__(self,name,wave,ltype,yaw_error,pitch_error,roll_error,dataframe):
                 self.Gral_InputsID   = name
                 self.LidarType       = ltype
                 self.Wavelength      = wave
                 self.yaw_error_dep   = yaw_error   # yaw error angle when deploying the lidar device in the grounf or in the nacelle
                 self.pitch_error_dep = pitch_error # pitch error angle when deploying the lidar device in the grounf or in the nacelle
                 self.roll_error_dep  = roll_error  # roll error angle when deploying the lidar device in the grounf or in the nacelle
                 self.dataframe       = dataframe   # Final dataframe
                 print('Created new lidar general inputs: {}'.format(self.Gral_InputsID))

#%% Lidar class:
class lidar():
    def __init__(self,name,photonics,optics,power,signal_processor,wfr_model,filt_method,probe_volume,lidar_inputs,unc_func,unc_Vh):
                 self.LidarID          = name
                 self.photonics        = photonics
                 self.optics           = optics
                 self.power            = power # Not included yet in Version Qlunc v-0.9 calculations
                 self.signal_processor = signal_processor
                 self.wfr_model        = wfr_model
                 self.filt_method      = filt_method
                 self.probe_volume     = probe_volume
                 self.lidar_inputs     = lidar_inputs
                 self.Uncertainty      = unc_func
                 self.Uncertainty_Vh   = unc_Vh
                 print('Created new lidar device: {}'.format(self.LidarID))

#%% Wind field recondtruction method
class wfr():
    def __init__ (self, name,reconstruction_model,unc_func):
        self.name = name
        self.reconstruction_model = reconstruction_model
        self.Uncertainty=unc_func
        print('Selected wfr model: {} terrain'.format(self.reconstruction_model))
#%% Data filtering method
class filtering_method():
    def __init__ (self, name,filt_method,unc_func):
        self.name = name
        self.filt_method = filt_method
        self.Uncertainty=unc_func
        print('Selected filtering model: {} '.format(self.filt_method))

        
#%% Create the lidar objects for pointing accuracy (called in 'UQ_Optics_Classes.py')
# class lidar_pointing():
#     def __init__(self, x,y,z,x_Lidar,y_Lidar,z_Lidar):
#         self.x_Lidar=x_Lidar
#         self.y_Lidar=y_Lidar
#         self.z_Lidar=z_Lidar
#         self.x=x
#         self.y=y
#         self.z=z
#     @classmethod
#     def vector_pos(cls,x,y,z,x_Lidar,y_Lidar,z_Lidar):
#         fx=(x-x_Lidar)
#         fy=(y-y_Lidar)
#         fz=(z-z_Lidar)
#         return(cls,fx,fy,fz)
#     @classmethod
#     def Cart2Sph (cls, x_vector_pos,y_vector_pos,z_vector_pos):
#         rho1,theta1,psi1 =SA.cart2sph(x_vector_pos,y_vector_pos,z_vector_pos)
#         return (cls,rho1,theta1,psi1)
        
    