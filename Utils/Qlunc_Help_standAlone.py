# -*- coding: utf-8 -*-
""".

Created on Mon May 18 00:03:43 2020
@author: fcosta

Francisco Costa García
University of Stuttgart(c) 
"""

from Utils.Qlunc_ImportModules import *
import pdb

#%%# used to flatt at some points along the code:
flatten = lambda *n: (e for a in n for e in (flatten(*a) if isinstance(a, (list,tuple)) else (a,))) 

#%% Rotation matrix for inclinometers in scanner    
def sum_mat(noisy_yaw,noisy_pitch, noisy_roll):
    """.
    
    Calculates the rotation matrix to apply uncertainty due to inclinometers deployment. Location: Qlunc_Help_standAlone.py
    
    Parameters
    ----------    
    * Noisy_yaw, noisy_pitch, noisy_roll
        Errors in yaw, pitch and roll
        
        
    Returns
    -------    
    Mean of the matrix after MonteCarlo simulation
    """
    R=[]
    for i in range(len(noisy_yaw)):    
        R.append([[np.cos(noisy_yaw[i])*np.cos(noisy_pitch[i])  ,  np.cos(noisy_yaw[i])*np.sin(noisy_pitch[i])*np.sin(noisy_roll[i])-np.sin(noisy_yaw[i])*np.cos(noisy_roll[i])  ,  np.cos(noisy_yaw[i])*np.sin(noisy_pitch[i])*np.cos(noisy_roll[i])+np.sin(noisy_yaw[i])*np.sin(noisy_roll[i])],
                  [np.sin(noisy_yaw[i])*np.cos(noisy_pitch[i])  ,  np.sin(noisy_yaw[i])*np.sin(noisy_pitch[i])*np.sin(noisy_roll[i])+np.cos(noisy_yaw[i])*np.cos(noisy_roll[i])  ,  np.sin(noisy_yaw[i])*np.sin(noisy_pitch[i])*np.cos(noisy_roll[i])-np.cos(noisy_yaw[i])*np.sin(noisy_roll[i])],
                  [       -np.sin(noisy_pitch[i])               ,  np.cos(noisy_pitch[i])*np.sin(noisy_roll[i])                                                                  ,  np.cos(noisy_pitch[i])*np.cos(noisy_roll[i])]])
    R_mean=np.sum(R,axis=0)/len(noisy_yaw)
    return R_mean

#%% sum dB:
def sum_dB(data,uncorrelated):
    """.
    
    Add up dB's. Location: Qlunc_Help_standAlone.py
    
    Parameters
    ----------    
    * SNR_data
        Signal to noise ratio
        
    * Bool
        Uncorrelated noise (default): True
        
    Returns
    -------    
    Sum of dBW
    
    """
    Sum_decibels=[] 
    # Sum_in_watts=[]
    to_watts=[]
    if uncorrelated:
        for ind in range(len(data)):
            to_watts.append(10**(data[ind]/10))
        Sum_in_watts=sum(to_watts)
        Sum_decibels=10*np.log10(Sum_in_watts)         
    else:
        print('correlated noise use case is not included yet')
        # Sumat= []
        # Sum_decibels=[]
        # for ii in data:
        #     watts=10**(ii/10)   
        #     Sumat.append (watts)
        # Sum_in_watts = sum(Sumat)
        # Sum_decibels.append(10*np.log10(Sum_in_watts) )        
    return Sum_decibels

#%% Combine uncertainties:
# The uncertainty combination is made following GUM
def unc_comb(data): 
    """.
    
    Uncertainty expansion - Location: Qlunc_Help_standAlone.py
    
    Parameters
    ----------   
    * data
        data is provided as a list of elements want to add on. Input data is expected to be in dB.
        
    Returns
    -------   
    list
    
    """
    data_watts  = []
    res_dB      = []
    res_watts   = []
    zipped_data = []
    if not isinstance (data,np.ndarray):
        data=np.array(data)    
    
    if len(data)==1:
        res_dB = list(data)
    else:
        for data_row in range(np.shape(data)[0]):# transform into watts        
            try:    
                data_db=data[data_row,:]
            except:
                data_db=data[data_row][0]             
            data_watts.append(10**(data_db/10))
        for i in range(len(data_watts[0])): # combining all uncertainties making sum of squares and the sqrt of the sum
            zipped_data.append(list(zip(*data_watts))[i])
            res_watts.append(np.sqrt(sum(map (lambda x: x**2,zipped_data[i])))) #  Combined stdv
            # res_watts.append(sum(map (lambda x: x**2,zipped_data[i]))) #   Combined Variance
            
            res_dB=10*np.log10(res_watts) #Convert into dB 
        del data_db
    return np.array(res_dB)

#%% System coordinates transformation

    
def sph2cart(rho,theta,phi): 
    x=[]
    y=[]
    z=[]    
    for i in range(len(rho)):
        x.append(rho[i]*np.cos(theta[i])*np.cos(phi[i]))
        y.append(rho[i]*np.cos(theta[i])*np.sin(phi[i]) )
        z.append(rho[i]*np.sin(theta[i]) )
    return(np.around(x,5),np.around(y,5),np.around(z,5))

def cart2sph(x,y,z): 
    rho=[]
    theta=[]
    phi=[]
    for ind in range(len(z)):
        rho.append(np.sqrt(x[ind]**2+y[ind]**2+z[ind]**2))
        if z[ind]<0:
            theta.append(-math.acos(np.sqrt(x[ind]**2+y[ind]**2)/np.sqrt(x[ind]**2+y[ind]**2+z[ind]**2)))
        elif z[ind]>=0:
            theta.append(math.acos(np.sqrt(x[ind]**2+y[ind]**2)/np.sqrt(x[ind]**2+y[ind]**2+z[ind]**2)))
        phi.append(math.atan2(y[ind],x[ind]))
        
        # if z[ind]>0:
        #         phi.append(np.arctan(np.sqrt(x[ind]**2+y[ind]**2)/z[ind]))
        # elif z[ind]==0:
        #         phi.append(np.array(np.pi/2))
        # elif z[ind]<0:
        #         phi.append((np.pi)+(np.arctan(np.sqrt(x[ind]**2+y[ind]**2)/z[ind])))
        # LOVE U Lucia!!
        # if x[ind]>0:
        #     if  y[ind]>=0:
        #         theta.append(np.arctan(y[ind]/x[ind]))            
        #     elif  y[ind]<0:
        #         theta.append((2.0*np.pi)+(np.arctan(y[ind]/x[ind])))           
        # elif x[ind]<0:
        #     theta.append((np.pi)+(np.arctan(y[ind]/x[ind])))            
        # elif x[ind]==0:
        #         theta.append(np.pi/2.0*(np.sign(y[ind])))
    # print(np.degrees(theta))
    return(np.array(rho),np.array(theta),np.array(phi)) # foc_dist, aperture angle, azimuth
#%% NDF function

def to_netcdf(DataXarray,Qlunc_yaml_inputs,Lidar,Atmospheric_Scenario):
    #DataXarray=Lidar.lidar_inputs.dataframe
    """.
    
    Save the project to an netcdf file - Location: Qlunc_Help_standAlone.py
    
    Parameters
    ----------    
    * DataXarray
        Data frame containing uncertainties of the lidar in xarray format. The name of the project is specify in the input yaml file.
        Change the name to create a different project. Otherwise the data is appended to the existing file. To read the 
        netndf file:
            xr.open_dataarray('C:/Users/fcosta/SWE_LOCAL/GIT_Qlunc/Projects/' + '<name_of_the_project>.nc')
        
    Returns
    -------    
    .netcdf file
    
    """
    if os.path.isfile('./Projects/' + Qlunc_yaml_inputs['Project']+ '.nc'):
        # Read the new lidar data
        Lidar.lidar_inputs.dataframe['Lidar']
        # time      = Atmospheric_Scenario.time 
        names     = [Lidar.LidarID]
        component = [i for i in DataXarray.keys()]
        data      = [ii for ii in DataXarray.values()]
        df_read   = xr.open_dataarray('./Projects/' + Qlunc_yaml_inputs['Project']+ '.nc')
        
        # Creating the new Xarray:
        dr = xr.DataArray(data,
                          coords = [component,names],
                          dims   = ('Components','Names'))
        
        # Concatenate data from different lidars
        df = xr.concat([df_read,dr],dim='Names')
        df_read.close()
        os.remove('./Projects/' +  Qlunc_yaml_inputs['Project']+ '.nc')
        df.to_netcdf('./Projects/'+ Qlunc_yaml_inputs['Project']+ '.nc','w')
    else:
                
        names     = [Lidar.LidarID]
        component = [i for i in DataXarray.keys()]
        # time      = [Atmospheric_Scenario.time ] 
        data      =[ii for ii in DataXarray.values()]
        df = xr.DataArray(data,
                          coords = [component,names],
                          dims   = ('Components','Names'))
        if not os.path.exists('./Projects'):
            os.makedirs('./Projects')       
        df.to_netcdf('./Projects/'+ Qlunc_yaml_inputs['Project']+ '.nc','w')
        return df
        
        # READ netcdf FILE.
        # da=xr.open_dataarray('C:/Users/fcosta/SWE_LOCAL/GIT_Qlunc/Projects/' + 'Gandia.nc')

#%% pulsed lidar probe volume calculations

def lin_interp(x, y, i, half):
    return x[i] + (x[i+1] - x[i]) * ((half - y[i]) / (y[i+1] - y[i]))

def half_max_x(x, y):
    half = max(y)/2.0
    signs = np.sign(np.add(y, -half))
    zero_crossings = (signs[0:-2] != signs[1:-1])
    zero_crossings_i = np.where(zero_crossings)[0]
    
    return [lin_interp(x, y, zero_crossings_i[0], half),
            lin_interp(x, y, zero_crossings_i[1], half)]


#%% Creates a sphere of radius equal to the estimates error distance around the lidar theoretical measured point

def sample_sphere(r,npoints, ndim=3):
    vec = np.random.randn(ndim, npoints)
    vec /= np.linalg.norm(vec, axis=0)
    xi,yi,zi=r*vec
    return xi,yi,zi



#%% RMSE

def rmse(f,ff):
    rm=[]
    rms=[]
    # ind_rm=0
    sum_rm=[]
    # for ffi,fi in zip(ff,f):
    rm=([(np.array(ff)-np.array(f))**2])
    rms=(np.sqrt(np.sum(rm)/len(ff)))
    # ind_rm=ind_rm+1
    return np.array(rms)

#%% Define meshgrid for the errors in pointing accuracy and focus range
def mesh (theta,psi,rho):
    box=np.meshgrid(theta,psi,rho)
    # Get coordinates of the points on the grid
    box_positions = np.vstack(map(np.ravel, box))
    theta=box_positions[0]
    psi=box_positions[1]
    rho=box_positions[2]
    # fig = plt.figure()

    # ax = fig.add_subplot(111, projection='3d')

    # ax.scatter(theta, psi, rho)

    # ax.set_xlabel('theta')
    # ax.set_ylabel('psi')
    # ax.set_zlabel('rho')
    # plt.show()
    return theta,psi,rho,box

#%% Wind velocity ucertainties
def U_Vh_MC(theta_c, psi_c,rho_c,loaded_dict,wind_direction,ind_wind_dir,Href,Vref,alpha,Hl):
    """.
    
    Calculates u and v wind speed components when two lidars are used to sample the wind. Location: Qlunc_Help_standAlone.py
    
    Parameters
    ----------    
    * correlated distributions theta, psi and rho
    
    * wind direction [degrees]
     
    * ind_wind_dir: index for looping
    
    * $H_{ref}$: Reference height  at which $V_{ref}$ is taken [m]
    
    * $V_{ref}$: reference velocity taken from an external sensor (e.g. cup anemometer) [m/s]
    
    * alpha: power law exponent [-] 
    
    * Hl: Lidar height [m]
  
    Returns
    -------    
    u and v wind speed components 
    """
    
    ### u
    # C_t1=(Hl+(rho_c[1]*np.sin(theta_c[1])))/Href
    # C_t2=(Hl+(rho_c[0]*np.sin(theta_c[0])))/Href
    
    # A0 = Vref*(np.sign(C_t1)*((abs(C_t1))**alpha))
    # B0 = np.cos(theta_c[1])*np.cos(psi_c[1]-wind_direction[ind_wind_dir])#np.cos(theta_c[1])*np.cos(psi_c[1])*np.cos(wind_direction[ind_wind_dir])+np.cos(theta_c[1])*np.sin(psi_c[1])*np.sin(wind_direction[ind_wind_dir])#+np.sin(theta_c[0])*np.tan(wind_tilt)
    # C0 = np.cos(theta_c[0])*np.sin(psi_c[0])
    # D0 = Vref*(np.sign(C_t2)*((abs(C_t2))**alpha))
    # E0 = np.cos(theta_c[0])*np.cos(psi_c[0]-wind_direction[ind_wind_dir])#np.cos(theta_c[0])*np.cos(psi_c[0])*np.cos(wind_direction[ind_wind_dir])+np.cos(theta_c[0])*np.sin(psi_c[0])*np.sin(wind_direction[ind_wind_dir])#+np.sin(theta_c[1])*np.tan(wind_tilt)
    # F0 = np.cos(theta_c[1])*np.sin(psi_c[1])
    # G  = np.cos(theta_c[0])*np.cos(theta_c[1])*(np.sin(psi_c[0]-psi_c[1])  )  
    # H0 = (A0*B0*C0)-(D0*E0*F0)
    # u_wind = (H0/G)
    
    # ### v
    # I0 = Vref*(np.sign(C_t2)*((abs(C_t2))**alpha))
    # J0 = np.cos(theta_c[0])*np.cos(psi_c[0]-wind_direction[ind_wind_dir])#np.cos(theta_c[0])*np.cos(psi_c[0])*np.cos(wind_direction[ind_wind_dir])+np.cos(theta_c[0])*np.sin(psi_c[0])*np.sin(wind_direction[ind_wind_dir])#+np.sin(Theta2_cr)*np.tan(wind_tilt)
    # K0 = np.cos(theta_c[1])*np.cos(psi_c[1])
    # L0 = Vref*(np.sign(C_t1)*((abs(C_t1))**alpha))
    # M0 = np.cos(theta_c[1])*np.cos(psi_c[1]-wind_direction[ind_wind_dir])#np.cos(theta_c[1])*np.cos(psi_c[1])*np.cos(wind_direction[ind_wind_dir])+np.cos(theta_c[1])*np.sin(psi_c[1])*np.sin(wind_direction[ind_wind_dir])#+np.sin(Theta1_cr)*np.tan(wind_tilt)
    # N0 = np.cos(theta_c[0])*np.cos(psi_c[0])   
    # O0 = (I0*J0*K0)-(L0*M0*N0)
    
    # v_wind = (O0/G)
    Vlos1 = loaded_dict[0]['Uncertainty'][0]['VLOS']
    Vlos2 = loaded_dict[1]['Uncertainty'][0]['VLOS']
    u_wind = (Vlos1*np.cos(theta_c[1])*np.sin(psi_c[1])-Vlos2*np.cos(theta_c[0])*np.sin(psi_c[0]))/(np.cos(theta_c[0])*np.cos(theta_c[1])*np.sin(psi_c[1]-psi_c[0]))
    v_wind = (Vlos2*np.cos(theta_c[0])*np.cos(psi_c[0])-Vlos1*np.cos(theta_c[1])*np.cos(psi_c[1]))/(np.cos(theta_c[0])*np.cos(theta_c[1])*np.sin(psi_c[1]-psi_c[0]))

    
    return (u_wind,v_wind)



def U_Vh_GUM(theta_c, psi_c,rho_c,wind_direction,ind_wind_dir,Href,Vref,alpha,Hl,U,Coef):
      
    """.
    
    Estimates the uncertainty in the horizontal wind speed $V_{h}$ by using the Guide to the expression of Uncertainty in Measurements (GUM). Location: Qlunc_Help_standAlone.py
    
    Parameters
    ----------    
    * correlated distributions theta, psi and rho
    
    * wind direction [degrees]
     
    * ind_wind_dir: index for looping
    
    * $H_{ref}$: Reference height  at which $V_{ref}$ is taken [m]
    
    * $V_{ref}$: reference velocity taken from an external sensor (e.g. cup anemometer) [m/s]
    
    * alpha: power law exponent [-] 
    
    * Hl: Lidar height [m]
  
    Returns
    -------    
    Estimated uncertainty in horizontal wind speed
    
    """
    #Avoid nans due to (-x)**alpha
    C_t1=(rho_c[0]*np.sin(theta_c[0])+Hl)/(Href)
    C_t2=(rho_c[1]*np.sin(theta_c[1])+Hl)/(Href)
    
    A = Vref*(np.sign(C_t1)*((abs(C_t1))**alpha))
    B = np.cos(theta_c[0])*np.cos(psi_c[0]-wind_direction[ind_wind_dir])#np.cos(theta_c[0])*np.cos(psi_c[0])*np.cos(wind_direction[ind_wind_dir])+np.cos(theta_c[0])*np.sin(psi_c[0])*(np.sin(wind_direction[ind_wind_dir]))
    C = Vref*(np.sign(C_t2)*((abs(C_t2))**alpha))
    D = np.cos(theta_c[1])*np.cos(psi_c[1]-wind_direction[ind_wind_dir])#np.cos(theta_c[1])*np.cos(psi_c[1])*np.cos(wind_direction[ind_wind_dir])+np.cos(theta_c[1])*np.sin(psi_c[1])*(np.sin(wind_direction[ind_wind_dir]))
    E = np.cos(theta_c[0])*np.cos(theta_c[1])*np.cos(psi_c[0]-psi_c[1])
    F = np.cos(theta_c[0])*np.cos(theta_c[1])*(np.sin(psi_c[0]-psi_c[1]))
    
    numerator = np.sqrt((A*B*np.cos(theta_c[1]))**2 + (C*D*np.cos(theta_c[0]))**2 - 2*(A*C*B*D*E))    
    dernumerator = 1/(2*numerator) 
    # pdb.set_trace()

    
    sh_term1 = Vref*alpha[0]*(np.sign(C_t1)*((abs(C_t1))**(alpha[0]-1)))
    sh_term2 = Vref*alpha[0]*(np.sign(C_t2)*((abs(C_t2))**(alpha[0]-1)))
    
    # Coefficients to calculate the partial derivatives
    
    ## Theta
    dert11 =  2*A*B*(np.cos(theta_c[1])**2)*((sh_term1*rho_c[0]*np.cos(theta_c[0])*B/Href)-np.sin(theta_c[0])*A*(np.cos(psi_c[0]-wind_direction[ind_wind_dir])))#2*A*B*(np.cos(theta_c[1])**2)*((sh_term1*rho_c[0]*np.cos(theta_c[0])*B/Href)+(A*(-np.sin(theta_c[0])*np.cos(psi_c[0])*np.cos(wind_direction[ind_wind_dir])-np.sin(theta_c[0])*np.sin(psi_c[0])*np.sin(wind_direction[ind_wind_dir]))))
    dert12 = -2*(C**2)*(D**2)*np.cos(theta_c[0])*(np.sin(theta_c[0]))
    dert13 = -2*C*D*((sh_term1*rho_c[0]*np.cos(theta_c[0])*B*E/Href)-np.sin(theta_c[0])*A*E*np.cos(psi_c[0]-wind_direction[ind_wind_dir])-A*B*(np.sin(theta_c[0])*np.cos(theta_c[1])*np.cos(psi_c[0]-psi_c[1])))#-2*((sh_term1*rho_c[0]*np.cos(theta_c[0])*C*B*D*E/Href)+A*C*(-np.sin(theta_c[0])*np.cos(psi_c[0])*np.cos(wind_direction[ind_wind_dir])-np.sin(theta_c[0])*np.sin(psi_c[0])*np.sin(wind_direction[ind_wind_dir]))*D*E+A*C*B*D*(-np.sin(theta_c[0])*np.cos(theta_c[1])*np.cos(psi_c[0]-psi_c[1])))
    
    dert21 = -2*(A**2)*(B**2)*np.cos(theta_c[1])*(np.sin(theta_c[1]))
    dert22 =  2*C*D*(np.cos(theta_c[0])**2)*(sh_term2*rho_c[1]*np.cos(theta_c[1])*D/Href-C*np.sin(theta_c[1])*np.cos(psi_c[1]-wind_direction[ind_wind_dir]))#2*C*D*(np.cos(theta_c[0])**2)*((sh_term2*rho_c[1]*np.cos(theta_c[1])*D/Href)+(C*(-np.sin(theta_c[1])*np.cos(psi_c[1])*np.cos(wind_direction[ind_wind_dir])-np.sin(theta_c[1])*np.sin(psi_c[1])*np.sin(wind_direction[ind_wind_dir]))))
    dert23 = -2*A*B*((sh_term2*rho_c[1]*np.cos(theta_c[1])*D*E/Href)-E*C*np.sin(theta_c[1])*np.cos(psi_c[1]-wind_direction[ind_wind_dir])-C*D*(np.sin(theta_c[1])*np.cos(theta_c[0])*np.cos(psi_c[0]-psi_c[1])))#-2*((sh_term2*rho_c[1]*np.cos(theta_c[1])*A*B*D*E/Href)+A*C*(-np.sin(theta_c[1])*np.cos(psi_c[1])*np.cos(wind_direction[ind_wind_dir])-np.sin(theta_c[1])*np.sin(psi_c[1])*np.sin(wind_direction[ind_wind_dir]))*B*E+A*C*B*D*(-np.sin(theta_c[1])*np.cos(theta_c[0])*np.cos(psi_c[0]-psi_c[1])))
    
    ## Psi
    derp11 =  2*(A**2)*B*(np.cos(theta_c[1])**2)*np.cos(theta_c[0])*(np.sin(wind_direction[ind_wind_dir]-psi_c[0]))#(2*A*B*np.cos(theta_c[1])*A*(-np.cos(theta_c[0])*np.sin(psi_c[0])*np.cos(wind_direction[ind_wind_dir])+np.cos(theta_c[0])*np.cos(psi_c[0])*np.sin(wind_direction[ind_wind_dir])))*np.cos(theta_c[1])
    derp12 = -2*A*C*D*np.cos(theta_c[0])*(E*(np.sin(wind_direction[ind_wind_dir]-psi_c[0]))-B*np.cos(theta_c[1])*(np.sin(psi_c[0]-psi_c[1])))#-2*(A*C*D*E*(-np.cos(theta_c[0])*np.sin(psi_c[0])*np.cos(wind_direction[ind_wind_dir])+np.cos(theta_c[0])*np.cos(psi_c[0])*np.sin(wind_direction[ind_wind_dir]))+A*B*C*D*np.cos(theta_c[0])*np.cos(theta_c[1])*(-np.sin(psi_c[0]-psi_c[1])))
    
    derp21 =  2*(C**2)*D*(np.cos(theta_c[0])**2)*np.cos(theta_c[1])*(np.sin(-psi_c[1]+wind_direction[ind_wind_dir]))#(2*C*D*np.cos(theta_c[0])*C*(-np.cos(theta_c[1])*np.sin(psi_c[1])*np.cos(wind_direction[ind_wind_dir])+np.cos(theta_c[1])*np.cos(psi_c[1])*np.sin(wind_direction[ind_wind_dir])))*np.cos(theta_c[0])
    derp22 = -2*A*C*B*np.cos(theta_c[1])*(E*(np.sin(wind_direction[ind_wind_dir]-psi_c[1]))+D*np.cos(theta_c[0])*(np.sin(psi_c[0]-psi_c[1])))#-2*(A*C*B*E*(-np.cos(theta_c[1])*np.sin(theta_c[1])*np.cos(wind_direction[ind_wind_dir])+np.cos(theta_c[1])*np.cos(psi_c[1])*np.sin(wind_direction[ind_wind_dir]))+A*B*C*D*np.cos(theta_c[0])*np.cos(theta_c[1])*(np.sin(psi_c[0]-psi_c[1])))
    
    ## Rho
    derr11 = (2*A*(B**2)*(np.cos(theta_c[1]))**2)*sh_term1*np.sin(theta_c[0])/Href
    derr12 = -2*C*B*D*E*sh_term1*np.sin(theta_c[0])/Href
              
    derr21 = (2*C*(D**2)*(np.cos(theta_c[0]))**2)*sh_term2*np.sin(theta_c[1])/Href
    derr22 = -2*A*B*D*E*sh_term2*np.sin(theta_c[1])/Href
    
    # With the coefficients we calculate the partial derivatives:
    dVh_dTheta1 = (dernumerator*(dert11+dert12+dert13)*F +numerator*np.cos(theta_c[1])*np.sin(theta_c[0])*(np.sin(psi_c[0]-psi_c[1])))/F**2
    dVh_dTheta2 = (dernumerator*(dert21+dert22+dert23)*F +numerator*np.cos(theta_c[0])*np.sin(theta_c[1])*(np.sin(psi_c[0]-psi_c[1])))/F**2
        
    dVh_dPsi1   = (dernumerator*(derp11+derp12)*F-numerator*np.cos(theta_c[1])*np.cos(theta_c[0])*np.cos(psi_c[0]-psi_c[1]))/F**2
    dVh_dPsi2   = (dernumerator*(derp21+derp22)*F+numerator*np.cos(theta_c[1])*np.cos(theta_c[0])*np.cos(psi_c[0]-psi_c[1]))/F**2
        
    dVh_dRho1   = (dernumerator*(derr11+derr12))/F
    dVh_dRho2   = (dernumerator*(derr21+derr22))/F
    
    ## Correlation terms:
    R = (dVh_dTheta1*dVh_dTheta2*U[0]*U[1]*Coef[0]+
         dVh_dPsi1*dVh_dPsi2*U[2]*U[3]*Coef[1]+
         dVh_dRho1*dVh_dRho2*U[4]*U[5]*Coef[2]+
     
        # dVh_dTheta1*dVh_dPsi1*U[0]*U[2]*psi1_theta1_corr_n+
        # dVh_dTheta2*dVh_dPsi1*U[1]*U[2]*psi1_theta2_corr_n+
        # dVh_dTheta1*dVh_dPsi2*U[0]*U[3]*psi2_theta1_corr_n+
        # dVh_dTheta2*dVh_dPsi2*U[1]*U[3]*psi2_theta2_corr_n+
     
        # dVh_dTheta1*dVh_dRho1*U[0]*U[4]*theta1_rho1_corr_n+
        # dVh_dTheta2*dVh_dRho1*U[1]*U[4]*theta2_rho1_corr_n+
        # dVh_dTheta1*dVh_dRho2*U[0]*U[5]*theta1_rho2_corr_n+
        # dVh_dTheta2*dVh_dRho2*U[1]*U[5]*theta2_rho2_corr_n+
     
        # dVh_dPsi1*dVh_dRho1*U[2]*U[4]*psi1_rho1_corr_n+
        # dVh_dPsi2*dVh_dRho1*U[3]*U[4]*psi2_rho1_corr_n+
        # dVh_dPsi1*dVh_dRho2*U[2]*U[5]*psi1_rho2_corr_n+
        # dVh_dPsi2*dVh_dRho2*U[3]*U[5]*psi2_rho2_corr_n
        # U[0]*U[1]*CORRCOEF_T[0][1]+U[2]*U[3]*CORRCOEF_P[0][1]+U[4]*U[5]*CORRCOEF_R[0][1]
      
        dVh_dTheta1*dVh_dPsi1*U[0]*U[2]*Coef[3]+
        dVh_dTheta2*dVh_dPsi1*U[1]*U[2]*Coef[4]+
        dVh_dTheta1*dVh_dPsi2*U[0]*U[3]*Coef[5]+
        dVh_dTheta2*dVh_dPsi2*U[1]*U[3]*Coef[6]+
     
        dVh_dTheta1*dVh_dRho1*U[0]*U[4]*Coef[7]+
        dVh_dTheta2*dVh_dRho1*U[1]*U[2]*Coef[8]+
        dVh_dTheta1*dVh_dRho2*U[0]*U[3]*Coef[9]+
        dVh_dTheta2*dVh_dRho2*U[1]*U[3]*Coef[10]+
     
        dVh_dPsi1*dVh_dRho1*U[2]*U[4]*Coef[11]+
        dVh_dPsi2*dVh_dRho1*U[3]*U[4]*Coef[12]+
        dVh_dPsi1*dVh_dRho2*U[2]*U[5]*Coef[13]+
        dVh_dPsi2*dVh_dRho2*U[3]*U[5]*Coef[14])  
    
    # With the partial derivatives and the correlation term R we calculate the uncertainty in Vh    
    U_Vh=np.sqrt((dVh_dTheta1*U[0])**2+(dVh_dTheta2*U[1])**2+(dVh_dPsi1*U[2])**2+(dVh_dPsi2*U[3])**2+(dVh_dRho1*U[4])**2+(dVh_dRho2*U[5])**2+2*R)[0]
    
    #%% u component uncertainty
    # pdb.set_trace()
    A_u_theta1 = Vref*np.cos(theta_c[1])*(C*np.cos(psi_c[1]-wind_direction[ind_wind_dir])*(-np.sin(theta_c[0]))*np.sin(psi_c[0]) - np.cos(psi_c[0]-wind_direction[ind_wind_dir])*np.sin(psi_c[1])*A*(alpha[0]*(rho_c[0]*np.cos(theta_c[0])*np.cos(theta_c[0])/(Hl+rho_c[0]*np.sin(theta_c[0])))-np.sin(theta_c[0])))
    A_u_theta2 = Vref*np.cos(theta_c[0])*(A*np.cos(psi_c[0]-wind_direction[ind_wind_dir])*(np.sin(theta_c[1]))*np.sin(psi_c[1]) + np.cos(psi_c[1]-wind_direction[ind_wind_dir])*np.sin(psi_c[0])*C*(alpha[0]*(rho_c[1]*np.cos(theta_c[1])*np.cos(theta_c[1])/(Hl+rho_c[1]*np.sin(theta_c[1])))-np.sin(theta_c[1])))
    
    u_theta1 = (A_u_theta1*F-(C*D*np.cos(theta_c[0])*np.sin(psi_c[0])-A*B*np.cos(theta_c[1])*np.sin(psi_c[1]))*(np.sin(psi_c[0]-psi_c[1]))*np.sin(theta_c[0])*np.cos(theta_c[1]))/F**2
    u_theta2 = (A_u_theta2*F-(C*D*np.cos(theta_c[0])*np.sin(psi_c[0])-A*B*np.cos(theta_c[1])*np.sin(psi_c[1]))*(np.sin(psi_c[0]-psi_c[1]))*np.sin(theta_c[1])*np.cos(theta_c[0]))/F**2

    U_u_theta =  np.sqrt((u_theta1*U[0])**2+(u_theta2*U[1])**2)
    
    # pdb.set_trace()
    return (U_Vh)
    
   # LoveU LU!

def U_VLOS_MC(theta,psi,rho,Hl,Href,alpha,wind_direction,Vref,ind_wind_dir,VLOS1_list):
     """.
    
     Performs a Montecarlo simulation to estimate the uncertainty in the line of sight velocity ( $V_{LOS}$ ). Location: Qlunc_Help_standAlone.py
    
     Parameters
     ----------    
     * correlated distributions theta, psi and rho
    
     * wind direction [degrees]
     
     * ind_wind_dir: index for looping
    
     * $H_{ref}$: Reference height  at which $V_{ref}$ is taken [m]
    
     * $V_{ref}$: reference velocity taken from an external sensor (e.g. cup anemometer) [m/s]
    
     * alpha: power law exponent [-] 
    
     * Hl: Lidar height [m]
        
        
     Returns
     -------    
     * Estimated line of sight wind speed [np.array]
     * Estimated average of the $V_{LOS}$
     * Estimated uncertainty in the $V_{LOS}$ [int]
     """
     # pdb.set_trace()
     VLOS01,U_VLOS1,=[],[]      
     A=((Hl+(np.sin(theta)*rho))/Href)      
     VLOS1 = Vref*(np.sign(A)*(abs(A)**alpha[0]))*(np.cos(theta)*np.cos(psi-wind_direction[ind_wind_dir])) #-np.sin(theta_corr[0][ind_npoints])*np.tan(wind_tilt[ind_npoints])
     VLOS1_list.append(np.mean(VLOS1))
     U_VLOS1   = np.nanstd(VLOS1)   
     return(VLOS1,U_VLOS1,VLOS1_list)

def U_VLOS_GUM (theta1,psi1,rho1,U_theta1,U_psi1,U_rho1,U_VLOS1,Hl,Vref,Href,alpha,wind_direction,ind_wind_dir,CROS_CORR):
    """.
    
    Analytical model based on the Guide to the expression of Uncertainty in Measurements (GUM) to estimate the uncertainty in the line of sight velocity ( $V_{LOS}$ ). Location: Qlunc_Help_standAlone.py
    
    Parameters
    ----------    
    * correlated distributions theta, psi and rho
    
    * wind direction [degrees]
     
    * ind_wind_dir: index for looping
    
    * $H_{ref}$: Reference height  at which $V_{ref}$ is taken [m]
    
    * $V_{ref}$: reference velocity taken from an external sensor (e.g. cup anemometer) [m/s]
    
    * alpha: power law exponent [-] 
    
    * Hl: Lidar height [m]
     
    * CROS_CORR: Correlation terms --> correlation betwee elevation and azimuth angles
        
        
    Returns
    -------    
    * Estimated uncertainty in the line of sight wind speed [np.array]
     
    """
    U_VLOS_sh_theta1,U_VLOS_sh_psi1,U_VLOS_sh_range1,U_VLOS1_GUM=[],[],[],[]
    # U_VLOS_sh_theta2,U_VLOS_sh_psi2,U_VLOS_sh_range2,U_VLOS2_GUM=[],[],[],[]
    B=((Hl+(np.sin(theta1)*rho1))/Href) 
    
    # VLOS1
    
    U_VLOS_sh_theta1 = Vref*(np.sign(B)*(abs(B)**alpha[0]))*np.cos(psi1-wind_direction[ind_wind_dir])*(alpha[0]*((rho1*(np.cos(theta1)**2)/(Hl+(np.sin(theta1)*rho1))))-np.sin(theta1))*U_theta1    
    U_VLOS_sh_psi1   = -Vref*np.cos((theta1))*(np.sign(B)*(abs(B)**alpha[0]))*(np.sin(psi1-wind_direction[ind_wind_dir]))*U_psi1
    U_VLOS_sh_range1 = Vref*alpha[0]*(np.sign(B)*(abs(B)**alpha[0]))*np.cos(theta1)*np.cos(psi1-wind_direction[ind_wind_dir])*(np.sin(theta1)/(Hl+(np.sin(theta1)*rho1)))*U_rho1
    # VLOS2
    # U_VLOS_sh_theta2 = Vref*(((Hl+(np.sin(theta2)*rho2))/Href)**alpha[0])*np.cos(psi2-wind_direction[ind_wind_dir])*(alpha[0]*((rho2*(np.cos(theta2)**2)/(Hl+(np.sin(theta2)*rho2))))-np.sin(theta2))*U_theta2    
    # U_VLOS_sh_psi2   = Vref*np.cos((theta2))*((((Hl)+(np.sin(theta2)*rho2))/Href)**alpha[0])*(np.sin(-psi2[0]+wind_direction[ind_wind_dir]))*(U_psi2) 
    # U_VLOS_sh_range2 = Vref*alpha[0]*(((Hl+(np.sin(theta2)*rho2))/Href)**alpha[0])*np.cos(theta2)*np.cos(psi2-wind_direction[ind_wind_dir])*(np.sin(theta2)/(Hl+(np.sin(theta2)*rho2)))*U_rho2
    
    # 2.4 Expanded uncertainty with contributions of theta, psi and rho

    # Correlation terms corresponding to the relation between same angles of different lidars ([theta1,theta2],[psi1,psi2],[rho1,rho2])
    # CC_P1_P2 = U_VLOS_sh_psi2*U_VLOS_sh_psi1*CROS_CORR[6]
    # CC_T1_T2 = U_VLOS_sh_theta2*U_VLOS_sh_theta1*CROS_CORR[7]
    # CC_R1_R2 = U_VLOS_sh_range2*U_VLOS_sh_range1*CROS_CORR[8]
    
    # Correlations terms LOS (theta1, rho1 and psi1)
    CC_T1_P1 = U_VLOS_sh_theta1*U_VLOS_sh_psi1*CROS_CORR[0]
    CC_T1_R1 = U_VLOS_sh_theta1*U_VLOS_sh_range1*CROS_CORR[1]
    CC_P1_R1 = U_VLOS_sh_range1*U_VLOS_sh_psi1*CROS_CORR[2]
    CC_VLOS  = 0#U_VLOS1*U_VLOS2*CORR_COEF
    
    # Estimated uncertainty in VLOS:
    U_VLOS1_GUM=np.sqrt(((U_VLOS_sh_theta1)**2+(U_VLOS_sh_psi1)**2+(U_VLOS_sh_range1)**2)+2*(CC_T1_P1+CC_T1_R1+CC_P1_R1+CC_VLOS)) 
    
    # Correlations variables LOS2 (theta2, rho2 and psi2)
    # CC_T2_P2 = U_VLOS_sh_theta2*U_VLOS_sh_psi2*CROS_CORR[3]
    # CC_T2_R2 =U_VLOS_sh_theta2*U_VLOS_sh_range2*CROS_CORR[4]
    # CC_P2_R2 = U_VLOS_sh_range2*U_VLOS_sh_psi2*CROS_CORR[5]
    # U_VLOS2_GUM=np.sqrt(((U_VLOS_sh_theta2)**2+(U_VLOS_sh_psi2)**2+(U_VLOS_sh_range2)**2)+2*(CC_T2_P2+CC_T2_R2+CC_P2_R2+CC_VLOS))
    return(U_VLOS1_GUM)

def VLOS_param (rho,theta,psi,U_theta1,U_psi1,U_rho1,N_MC,U_VLOS1,Hl,Vref,Href,alpha,wind_direction_TEST,ind_wind_dir,CROS_CORR):
    wind_direction_TEST = np.radians([45])
    # wind_tilt_TEST      = np.radians([0])
    #If want to vary range
    
    
    if len (rho) !=1:
        rho_TEST   = rho
        theta_TEST = theta*np.ones(len(rho_TEST))
        psi_TEST   = psi*np.ones(len(rho_TEST))
        U_theta1   = 0
        U_psi1   = 0
        # pdb.set_trace()
        ind_i = theta_TEST
    elif len(theta)!=1:
        theta_TEST = theta
        rho_TEST   = rho[0]*np.ones(len(theta_TEST))
        psi_TEST   = psi*np.ones(len(theta_TEST))
        U_rho1   = 0
        U_psi1   = 0
        ind_i = rho_TEST
    elif len(psi)!=1:
        psi_TEST   = psi
        rho_TEST   = rho[0]*np.ones(len(psi_TEST))
        theta_TEST = theta*np.ones(len(psi_TEST))
        U_rho1   = 0
        U_theta1  = 0
        ind_i = rho_TEST
    # pdb.set_trace()        
    # Calculate radial speed uncertainty for an heterogeneous flow
    U_Vrad_homo_MC,U_Vrad_homo_MC_LOS1,U_Vrad_homo_MC_LOS2 = [],[],[]
    VLOS_list_T,U_VLOS_T_MC,U_VLOS_T_GUM,U_VLOS_THomo_MC=[],[],[],[]
    for ind_0 in range(len(ind_i)):
        # MC method
        VLOS_T_MC1=[]
        theta1_T_noisy = np.random.normal(theta_TEST[ind_0],U_theta1,N_MC)
        psi1_T_noisy   = np.random.normal(psi_TEST[ind_0],U_psi1,N_MC)
        rho1_T_noisy   = np.random.normal(rho_TEST[ind_0],U_rho1,N_MC)

        VLOS_T_MC,U_VLOS_T,VLOS_LIST_T         = U_VLOS_MC(theta1_T_noisy,psi1_T_noisy,rho1_T_noisy,Hl,Href,alpha,wind_direction_TEST,Vref,0,VLOS_list_T)
        VLOS_THomo_MC,U_VLOS_THomo,VLOS_LIST_T = U_VLOS_MC(theta1_T_noisy,psi1_T_noisy,rho1_T_noisy,Hl,Href, [0], wind_direction_TEST,Vref,0,VLOS_list_T)
        
        U_VLOS_T_MC.append(U_VLOS_T)         # For an heterogeneous flow in the z direction (shear)
        U_VLOS_THomo_MC.append(U_VLOS_THomo) # For an homogeneous flow
    
    # GUM method
    U_VLOS_T_GUM     = U_VLOS_GUM (theta_TEST,psi_TEST,rho_TEST,U_theta1,U_psi1,U_rho1,U_VLOS1,Hl,Vref,Href,alpha,wind_direction_TEST,0,[0,0,0])  # For an heterogeneous flow in the z direction (shear)
    U_VLOS_THomo_GUM = U_VLOS_GUM (theta_TEST,psi_TEST,rho_TEST,U_theta1,U_psi1,U_rho1,U_VLOS1,Hl,Vref,Href,[0],wind_direction_TEST,0,[0,0,0])    # For an homogeneous flow
    # pdb.set_trace()
    return (U_VLOS_T_MC,U_VLOS_THomo_MC,U_VLOS_T_GUM,U_VLOS_THomo_GUM,rho_TEST,theta_TEST,psi_TEST)        

#%% Wind direction uncertainties
def U_WindDir_MC(theta_c, psi_c,rho_c,wind_direction,ind_wind_dir,Href,Vref,alpha,Hl):
    """.
    
    Calculates wind direction. Location: Qlunc_Help_standAlone.py
    
    Parameters
    ----------    
    * correlated distributions theta, psi and rho
    
    * wind direction [degrees]
     
    * ind_wind_dir: index for looping
    
    * $H_{ref}$: Reference height  at which $V_{ref}$ is taken [m]
    
    * $V_{ref}$: reference velocity taken from an external sensor (e.g. cup anemometer) [m/s]
    
    * alpha: power law exponent [-] 
    
    * Hl: Lidar height [m]
  
    Returns
    -------    
    u and v wind speed components 
    """
    #Wind direction
    # pdb.set_trace()
    
    C_t1 = ((Hl+(rho_c[0]*np.sin(theta_c[0])))/Href)
    C_t2 = ((Hl+(rho_c[1]*np.sin(theta_c[1])))/Href)
    A = (np.sign(C_t1)*(((C_t1))**alpha))*np.cos(psi_c[0]-wind_direction[ind_wind_dir])*np.cos(psi_c[1])
    B = (np.sign(C_t2)*(((C_t2))**alpha))*np.cos(psi_c[1]-wind_direction[ind_wind_dir])*np.cos(psi_c[0])
    C = (np.sign(C_t2)*(((C_t2))**alpha))*np.cos(psi_c[1]-wind_direction[ind_wind_dir])*np.sin(psi_c[0])
    D = (np.sign(C_t1)*(((C_t1))**alpha))*np.cos(psi_c[0]-wind_direction[ind_wind_dir])*np.sin(psi_c[1])    
    # P=(A-B)/(C-D)
    wind_dir = np.arctan((A-B)/(C-D))
    return (wind_dir)

def U_WindDir_GUM(theta_c, psi_c,rho_c,wind_direction,ind_wind_dir,Href,Vref,alpha,Hl,U,Coef):
    """.
    
    Calculates wind direction. Location: Qlunc_Help_standAlone.py
    
    Parameters
    ----------    
    * correlated distributions theta, psi and rho
    
    * wind direction [degrees]
     
    * ind_wind_dir: index for looping
    
    * $H_{ref}$: Reference height  at which $V_{ref}$ is taken [m]
    
    * $V_{ref}$: reference velocity taken from an external sensor (e.g. cup anemometer) [m/s]
    
    * alpha: power law exponent [-] 
    
    * Hl: Lidar height [m]
  
    Returns
    -------    
    u and v wind speed components 
    """
    # Wind direction uncertainty
    # pdb.set_trace()
    
    C_t1 = ((Hl+(rho_c[0]*np.sin(theta_c[0])))/Href)
    C_t2 = ((Hl+(rho_c[1]*np.sin(theta_c[1])))/Href)
    
    
    A = (np.sign(C_t1)*((abs(C_t1))**alpha))*np.cos(psi_c[0]-wind_direction[ind_wind_dir])*np.cos(psi_c[1])
    B = (np.sign(C_t2)*((abs(C_t2))**alpha))*np.cos(psi_c[1]-wind_direction[ind_wind_dir])*np.cos(psi_c[0])
    C = (np.sign(C_t2)*((abs(C_t2))**alpha))*np.cos(psi_c[1]-wind_direction[ind_wind_dir])*np.sin(psi_c[0])
    D = (np.sign(C_t1)*((abs(C_t1))**alpha))*np.cos(psi_c[0]-wind_direction[ind_wind_dir])*np.sin(psi_c[1])    
    X = ((A-B)/(C-D))
    P = 1/(1+X**2) 
    
    sh_term1 = alpha[0]*(np.sign(C_t1)*(abs(C_t1))**(alpha[0]-1))
    sh_term2 = alpha[0]*(np.sign(C_t2)*(abs(C_t2))**(alpha[0]-1))
    

    dWindDir_dtheta1 =  P*(1/(C-D)**2)*sh_term1*np.cos(theta_c[0])*(rho_c[0]/Href)*np.cos(psi_c[0]-wind_direction[ind_wind_dir])*((C-D)*np.cos(psi_c[1])+(A-B)*np.sin(psi_c[1]))
    dWindDir_dtheta2 = -P*(1/(C-D)**2)*sh_term2*np.cos(theta_c[1])*(rho_c[1]/Href)*np.cos(psi_c[1]-wind_direction[ind_wind_dir])*((C-D)*np.cos(psi_c[0])+(A-B)*np.sin(psi_c[0]))
    
    dWindDir_dpsi1 = P*(1/(C-D)**2)*(((C-D)*(-(np.sign(C_t1)*((abs(C_t1))**alpha))*np.sin(psi_c[0]-wind_direction[ind_wind_dir])*np.cos(psi_c[1])+\
                                              (np.sign(C_t2)*((abs(C_t2))**alpha))*np.cos(psi_c[1]-wind_direction[ind_wind_dir])*np.sin(psi_c[0])))-\
                                     ((A-B)*((np.sign(C_t2)*((abs(C_t2))**alpha))*np.cos(psi_c[1]-wind_direction[ind_wind_dir])*np.cos(psi_c[0])+\
                                              (np.sign(C_t1)*((abs(C_t1))**alpha))*np.sin(psi_c[0]-wind_direction[ind_wind_dir])*np.sin(psi_c[1]))))
    
    dWindDir_dpsi2 =  P*(1/(C-D)**2)*(((C-D)*(-(np.sign(C_t1)*((abs(C_t1))**alpha))*np.cos(psi_c[0]-wind_direction[ind_wind_dir])*np.sin(psi_c[1])+\
                                              (np.sign(C_t2)*((abs(C_t2))**alpha))*np.sin(psi_c[1]-wind_direction[ind_wind_dir])*np.cos(psi_c[0])))-\
                                     ((A-B)*(-(np.sign(C_t2)*((abs(C_t2))**alpha))*np.sin(psi_c[1]-wind_direction[ind_wind_dir])*np.sin(psi_c[0])-\
                                              (np.sign(C_t1)*((abs(C_t1))**alpha))*np.cos(psi_c[0]-wind_direction[ind_wind_dir])*np.cos(psi_c[1]))))
    
    dWindDir_drho1 =  P*(1/(C-D)**2)*sh_term1*(np.sin(theta_c[0])/Href)*np.cos(psi_c[0]-wind_direction[ind_wind_dir])*((C-D)*np.cos(psi_c[1])+(A-B)*np.sin(psi_c[1]))
    dWindDir_drho2 = -P*(1/(C-D)**2)*sh_term2*(np.sin(theta_c[1])/Href)*np.cos(psi_c[1]-wind_direction[ind_wind_dir])*((C-D)*np.cos(psi_c[0])+(A-B)*np.sin(psi_c[0]))
    
    ## Correlation terms:
    R = (dWindDir_dtheta1*dWindDir_dtheta2*U[0]*U[1]*Coef[0]+
          dWindDir_dpsi1*dWindDir_dpsi2*U[2]*U[3]*Coef[1]+
          dWindDir_drho1*dWindDir_drho2*U[4]*U[5]*Coef[2]+
     
        # dVh_dTheta1*dVh_dPsi1*U[0]*U[2]*psi1_theta1_corr_n+
        # dVh_dTheta2*dVh_dPsi1*U[1]*U[2]*psi1_theta2_corr_n+
        # dVh_dTheta1*dVh_dPsi2*U[0]*U[3]*psi2_theta1_corr_n+
        # dVh_dTheta2*dVh_dPsi2*U[1]*U[3]*psi2_theta2_corr_n+
     
        # dVh_dTheta1*dVh_dRho1*U[0]*U[4]*theta1_rho1_corr_n+
        # dVh_dTheta2*dVh_dRho1*U[1]*U[4]*theta2_rho1_corr_n+
        # dVh_dTheta1*dVh_dRho2*U[0]*U[5]*theta1_rho2_corr_n+
        # dVh_dTheta2*dVh_dRho2*U[1]*U[5]*theta2_rho2_corr_n+
     
        # dVh_dPsi1*dVh_dRho1*U[2]*U[4]*psi1_rho1_corr_n+
        # dVh_dPsi2*dVh_dRho1*U[3]*U[4]*psi2_rho1_corr_n+
        # dVh_dPsi1*dVh_dRho2*U[2]*U[5]*psi1_rho2_corr_n+
        # dVh_dPsi2*dVh_dRho2*U[3]*U[5]*psi2_rho2_corr_n
        # U[0]*U[1]*CORRCOEF_T[0][1]+U[2]*U[3]*CORRCOEF_P[0][1]+U[4]*U[5]*CORRCOEF_R[0][1]
      
        dWindDir_dtheta1*dWindDir_dpsi1*U[0]*U[2]*Coef[3]+
        dWindDir_dtheta2*dWindDir_dpsi1*U[1]*U[2]*Coef[4]+
        dWindDir_dtheta1*dWindDir_dpsi2*U[0]*U[3]*Coef[5]+
        dWindDir_dtheta2*dWindDir_dpsi2*U[1]*U[3]*Coef[6]+
     
        dWindDir_dtheta1*dWindDir_drho1*U[0]*U[4]*Coef[7]+
        dWindDir_dtheta2*dWindDir_drho1*U[1]*U[2]*Coef[8]+
        dWindDir_dtheta1*dWindDir_drho2*U[0]*U[3]*Coef[9]+
        dWindDir_dtheta2*dWindDir_drho2*U[1]*U[3]*Coef[10]+
     
        dWindDir_dpsi1*dWindDir_drho1*U[2]*U[4]*Coef[11]+
        dWindDir_dpsi2*dWindDir_drho1*U[3]*U[4]*Coef[12]+
        dWindDir_dpsi1*dWindDir_drho2*U[2]*U[5]*Coef[13]+
        dWindDir_dpsi2*dWindDir_drho2*U[3]*U[5]*Coef[14])  
    
    # With the partial derivatives and the correlation term R we calculate the uncertainty in Vh    
    U_wind_dir=np.sqrt((dWindDir_dtheta1*U[0])**2+(dWindDir_dtheta2*U[1])**2+(dWindDir_dpsi1*U[2])**2+(dWindDir_dpsi2*U[3])**2+(dWindDir_drho1*U[4])**2+(dWindDir_drho2*U[5])**2+2*R)[0]    
     
    return (U_wind_dir)
    