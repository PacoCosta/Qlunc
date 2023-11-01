%%%
% Header
% fft_test
% Simulating data processing
% ADC and frequency analyser

% Through Montecarlo simulations calculates:
%   - Uncertainty in vlos due to sampling frequency bias
%   - Uncertainty in vlos due to laser wavelength drift
%   - Uncertainty in vlos due to spectra average when more than 1 pulse is
%     selected
% Takes a signal discretised at fs and digitises it. A Fourier
% transform is applied to the digitised signal to obtain the frequency
% spectra.

% Issues:
%   - Resolution.
%   - Noise in the signal ('noise')
%   -
%   -


% Francisco Costa
% SWE-2022
%%%

%%
clear all %#ok<CLALL>
% close all
clc
format shortEng
%% Inputs

% distance         = 2000;
% PRF              = physconst('LightSpeed')/(2*distance);
n_bits           = 8;      % N_MC� bits ADC
V_ref            = 10;      % Reference voltaje ADC
lidar_wavelength = 1550e-9; % wavelength of the laser source.
fs_av            = 100e6;    % sampling frequency
L                = 2^n_bits;    %length of the signal.
n_fftpoints      = L;       % n� of points for each block (fft points).
fd               = 2*V_ref/lidar_wavelength;  % Doppler frequency corresponding to Vref
level_noise      = 0.008; % Hardware noise added before signal downmixing
n_pulses         = 1;   % n pulses for averaging the spectra
N_MC             = 1e3; % n� MC samples to calculate the uncertainty due to bias in sampling frequency and wavelength
Dp               = L*2.9e8*.5/fs_av;
%% Uncertainty in the signal processing.

%%% Uncertainty in the sampling frequency %%%
per         = 2e-4;
% bias_fs_av  = (per/100)*fs_av; % +/-
std_fs_av   = (per/100)*fs_av;%/sqrt(3); % 2e-6*fs_av; % 
fs          = [fs_av;std_fs_av.*randn(N_MC,1) + fs_av];
Ts          = 1./fs;
% Accepted values
Tv = 1/fs_av;
tv = (0:n_fftpoints-1)*Tv;
fv = linspace(0,fs_av/2,floor(length(tv)/2+1));
vv=0.5*lidar_wavelength*fv;


%%% Stdv due drift in the wavelength of the laser %%%
stdv_wavelength  = 1e-9/sqrt(3); % m
wavelength_noise = lidar_wavelength+stdv_wavelength*randn(N_MC+1,1); % Noisy wavelength vector
e_perc_wavelength = 100*wavelength_noise/lidar_wavelength;



%% Loop to calculate the frequency spectra for each fs

tic
for ind_npulses = 1:n_pulses
    for ind_fs = 1:N_MC+1

        % Time and frequency vectors
        t{ind_fs} = (0:n_fftpoints-1)*Ts(ind_fs); %#ok<SAGROW> %time vector
        f{ind_fs}  = linspace(0,fs(ind_fs)/2,floor(length(t{ind_fs}))/2+1); %#ok<SAGROW> % floor()"/2+1" is added to match the length of the double-sided spectrum (P1)
        
        % Signal + Hardware noise:
        noise      = level_noise*randn(size(t{ind_fs}));
        
        S{ind_fs}         = noise+(14*sin(2*pi*fd.*t{ind_fs}) - 2.1*sin(2*pi*1.9*abs(randn(1,1))*fd*t{ind_fs}) + 2*sin(2*pi*3*abs(randn(1,1))*fd*t{ind_fs})+...
                      3.24*sin(2*pi*6*abs(randn(1,1))*fd.*t{ind_fs}) + 4.7*sin(2*pi*2*abs(randn(1,1))*fd*t{ind_fs}) - 1.4*sin(2*pi*abs(randn(1,1))*fd*t{ind_fs})); % Adding up Signal contributors
        
%         S{ind_fs}  = awgn(S0, 5); %#ok<SAGROW>
        
        
        % Spectrum function from matlab:
        [pxx{ind_fs},fr{ind_fs}] = pspectrum(S{ind_fs}./max(abs(S{ind_fs}))); %#ok<SAGROW>
        
        % Normalise signal:
        X{ind_fs} =  S{ind_fs}./max(abs(S{ind_fs}))  ; %#ok<SAGROW>
        
        %%%%%%%%%%%%%%%%%%
        % ADC:
        % Quantisation of the signal
        ENOB = n_bits; %(SINAD-1.76)/6.02;
        vres= (2/(2^ENOB));
        % find upper and lower limits
        low_lim= sort(-vres:-vres: -1, 'ascend');
        upp_lim=(vres:vres:1);
        v=[low_lim,0,upp_lim]; % vector of ADC quantized values
        
        [~,mm,ttt]=histcounts(X{ind_fs},v); % calculates the indexes of the bins X values belong to
        F_mid = conv(v, [0.5,0.5], 'valid'); % calculates the intermediate value of the elements in v (the gaps' values)--> V values of quantization
        quant=F_mid(ttt);
        S_quant = quant;
        % Mean the quantize original signal (mean and get the closest to the
        % original value
        for ind_quant=1:size(S_quant,2)
            [s,b]=min(abs(S_quant(:,ind_quant)-mean(S_quant(:,ind_quant))));
            mean_S_quant{ind_fs}(:,ind_quant)= S_quant(b,ind_quant);
        end
        
        % RMSE due to digitisation process. If the signal is unbiased, RMSE
        % is the standard deviation.
        RMSE_digit(ind_fs,ind_npulses)= (sqrt(abs(sum(X{ind_fs}-S_quant)).^2/length(t{ind_fs}))); %#ok<SAGROW>
        
        
        % tic
        %%%%%%%%%%%%%%%%%%
        % Frequency analyser:
        % FFT of the Quantised signal
        P3            = fft(mean_S_quant{ind_fs}'); % Fourier transform
        P2            = abs(P3')/n_fftpoints;
        P1            = P2(:,1:n_fftpoints/2+1);
        P1(2:end-1)   = 2*P1(2:end-1);
        S_fft_quant   = P1.^2;
        S_fft_quant_mean(ind_fs,:) = P1.^2; %#ok<SAGROW>
        
        % T(1,ind_fs)=toc;
        % Time_fft(1,ind_fs)=sum(T); % Time taken for each fft
        
        % Peak detection from the spectra
        [ii_mean,ii1_mean]          = max(S_fft_quant); % Assume maximum as a peak detection method
        fd_peak(ind_fs,ind_npulses)  = f{ind_fs} (ii1_mean); %#ok<SAGROW>
        
        % Vlos
        vlos_MC(ind_fs,ind_npulses) = 0.5*wavelength_noise(ind_fs)*fd_peak(ind_fs,ind_npulses); %#ok<SAGROW>
        
        
        % Assessing Statistics:
        %         mode_S_quant{ind_fs}   = mode(S_quant);
        
        % Velocity and frequency resolution. Frequency resolution: ratio(fs,nfft_points)
        f_resolution(ind_fs,ind_npulses) = f{ind_fs}(2); %#ok<SAGROW>
        V_resolution(ind_fs,ind_npulses) = 0.5*lidar_wavelength*(f_resolution(ind_fs,ind_npulses)); %#ok<SAGROW>
        
        
        % Relative error in the peak detection
%         Relative_error(ind_fs,:,ind_npulses) =  100*abs((fd - f_peak(ind_fs,ind_npulses)))/fd; %#ok<SAGROW>
%         stdv_signal (ind_fs,:,ind_npulses) = level_noise/sqrt(size(P3,1)); %#ok<SAGROW>
        % STDV_signal (ind_fs,:) = level_noise/sqrt(size(P3,1));
        RMSE(ind_fs,:,ind_npulses) =sqrt(mean((X{ind_fs}-mean_S_quant{ind_fs}).^2)); %#ok<SAGROW>
        SNQR(ind_fs,:,ind_npulses) =((6.02*n_bits-1.25)); %#ok<SAGROW>
        
        % Clear variables
        clear P3
        clear S_quant
        clear S_quant_chop
        clear S_fft_quant
    end
    
    % Spectra of each pulse. Is the averaged spectra after the montecarlo simulation
    Spec_mean_pulse(ind_npulses,:)  = mean(S_fft_quant_mean(2:end,:),1); %#ok<SAGROW>
    
    % Original spectra of each pulse
    S_original(ind_npulses,:)=S_fft_quant_mean(1,:); %#ok<SAGROW>
    
    % V LOS from montecarlo
    v_MC_pulse(ind_npulses,:)      = mean(vlos_MC(2:end,ind_npulses),1); %#ok<SAGROW>
    stdv_v_MC_pulse(ind_npulses,:) = std(vlos_MC(2:end,ind_npulses)); %#ok<SAGROW>
    RE_pulse(ind_npulses,:)        = stdv_v_MC_pulse(ind_npulses,:)/v_MC_pulse(ind_npulses,:); %#ok<SAGROW>

end

%% Statistics

mean_S_original = mean(S_original,1);
Spec_mean       = mean(Spec_mean_pulse);

% Frequency
% Original Doppler frequency
mean_fd_pulse_OR = mean(fd_peak(1,:),1);
stdv_fd_pulse_OR  = std(fd_peak(1,:));

% Peaks' statistics
mean_fd_pulse      = mean(fd_peak(2:end,:),1);
stdv_fd_pulse      = std(fd_peak(2:end,:));
stdv_fd_pulse_mean = mean(stdv_fd_pulse);
RE_pulse2          = (stdv_fd_pulse ./mean_fd_pulse)*100;

mean_fd    = mean(mean_fd_pulse,2);
stdv_fd_av = std(mean_fd_pulse); % stdv between the peaks of the different pulses

stdv_fd = sqrt((stdv_fd_pulse_mean)^2+(stdv_fd_av)^2); % Sum of variances from errors in fs and peak averaging:

%% Uncertainty in LOS 

% Mc method
v_s_MC          = mean(v_MC_pulse);
stdv_bias_v_MC  = mean(stdv_v_MC_pulse); % Mean of the stdvs of each pulse
stdv_av_v_MC    = std(v_MC_pulse);
stdv_T_v_MC     = sqrt(stdv_bias_v_MC^2+stdv_av_v_MC^2);
RE_MC           = 100*stdv_T_v_MC/v_s_MC;

% Analytical method
corr_coeff      = 1;
v_An            = 0.5*lidar_wavelength*mean_fd_pulse;
stdv_v_An       = sqrt(0.25*fd^2*stdv_wavelength^2+0.25*lidar_wavelength^2.*stdv_fd.^2+2*corr_coeff*(0.5*fd*stdv_wavelength*0.5*lidar_wavelength.*stdv_fd));
stdv_v_An2       = sqrt(0.25*fd^2*stdv_wavelength^2+0.25*lidar_wavelength^2.*stdv_fd.^2);

RE_v            = (stdv_v_An./v_An)*100;



%% PLOTS

%%%%%%%% Plotting signals + digitised signal + error: %%%%%%%%%%%%%%%%%%%%
% markersize=[{'k-*'},{'b-*'},{'r-*'},{'g-*'},{'c-*'},{'m-*'},{'y-*'}];
% markersize_2=[{'k--x'},{'b--x'},{'r--x'},{'g--x'},{'c--x'},{'m--x'},{'y--x'}];
% markersize_3=[{'m-.'},{'b-.'},{'r-.'},{'g-.'},{'c-.'},{'m-.'},{'y-.'}];
% figure,hold on
% for in_sig=1:length(fs)
%    
%     plot(t{in_sig}(1,:)  ,X{in_sig}(1,:),markersize{in_sig},'Linewidth',1.2,'displayname','Original signal')
%     plot(t{in_sig},mean_S_quant{in_sig},markersize_2{in_sig},'Linewidth',1.9,'displayname','Quantised signal' );
%     plot(t{in_sig},X{in_sig}(1,:)-mean_S_quant{in_sig},markersize_3{in_sig},'Linewidth',1.9,'displayname',['Error(RMSE [-] = ',num2str(RMSE(in_sig)),')']);
%     %     plot(t{i} ,X{i}(1,:)  ,markersize{i})
%     %     plot(t{i},S_quant0{i},markersize_2{i},'Linewidth',1.4);
% end
% xlabel('time [s]')
% ylabel('[-]')
% title(['Signal quantisation -',' n�bits = ', num2str(n_bits), ' - fs [Hz] = ',num2str(fs(in_sig),'%.2s') ])
% hold off
% legend show
% grid on
% set(gca,'FontSize',35);
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%% fft signals %%%%%%%%%%%%%%
fig=figure;
hold on

% Against velocity
% plot(vv,pow2db(mean_S_original),'-k','linewidth',2.7,'displayname','Doppler Spectrum (f_s)');
% plot(vv,pow2db(mean(Spec_mean_pulse,1)),'-m','linewidth',2.1,'displayname',['% Biased Doppler Spectrum']);
% xlabel('Wind velocity [ms^{-1}]');
% ylabel('PSD [dB]');

% Against frequency
plot(fv,pow2db(mean_S_original),'-k','linewidth',2.7,'displayname','Doppler Spectra');
plot(fv,pow2db(Spec_mean_pulse),'-m','linewidth',3.1,'displayname','Biased Doppler Spectra');

xlabel('Frequency [Hz]');
ylabel('PSD [dB]');


Y_text_in_plot=pow2db(max(mean_S_original)); % Takes the height of the last peak. Just a convention, to plot properly
str={['# fft                  =  ', num2str(n_fftpoints)],...
    ['# pulses           =  ', num2str(n_pulses)],...
    ['# MC samples =  ', num2str(N_MC)],...
    ['u_{est} [ms^{-1}]     =  ', num2str(stdv_T_v_MC,'%.1s') ],...
    ['u_{est} [%]         =  ', num2str(RE_MC,'%.1s') ]};
% text(5e6,Y_text_in_plot-2.9,str, 'fontsize',17);
anot=annotation(fig, 'textbox');
anot.FontSize=19;
anot.String=str;
anot.Position =  [0.135 0.415 0.6 0.5];
anot.FitBoxToText='on';
% title('Frequency spectra', 'fontsize',25)

% legend show
leg=legend;
leg.FontSize=19 ;
legend show
grid on
% l1.MarkerFaceColor = l1.Color;
set(gca,'FontSize',35);
hold off

toc


%% Plot input quantities probability distributions
figure,
histogram(fs,15,'displayname','Probability distribution f_s')
leg=legend;
leg.FontSize=19 ;
legend show
grid on
set(gca,'FontSize',35);
hold off

figure,
histogram(noise,'displayname','Probability distribution noise')
leg=legend;
leg.FontSize=19 ;
legend show
grid on
set(gca,'FontSize',35);
hold off

figure,
histfit(fd_peak(:,1))
pd = fitdist(fd_peak(:,1),'Normal')
% figure,
% histogram(noise,'displayname','Probability distribution noise')
% leg=legend;
% leg.FontSize=19 ;
% legend show
% grid on
% set(gca,'FontSize',35);
% hold off


%%%%% Plot matlab spectrum %%%%%%%%%%%%%%%%%%%%%%%%%%%%
% figure, hold on
% for in_fft=1:length(fs)
%
%     plot(fr{in_fft},pow2db(pxx{in_fft}))
%
% end
% legend show
% grid on
% xlabel('Frequency (Hz)')
% ylabel('Power Spectrum (dB)')
% title('Default Frequency Resolution')
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% ####### LOG SCALE ########

% set(gca, 'YScale', 'log')
% set(gca, 'XScale', 'log')


% % Plotting sensitivity annalysis
% figure,plot(n_fftpoints,Relative_error,'bo')
% title('Relative error vs. N_MC�of samples', 'fontsize',20)
% ylabel('Relative error [%]', 'fontsize',20)
% xlabel('Number of fft points', 'fontsize',20)
% grid on
% figure,plot(n_fftpoints,T,'bo')
% title('Computational time vs. N_MC�of samples', 'fontsize',20)
% ylabel('time[s]', 'fontsize',20)
% xlabel('Number of fft points', 'fontsize',20)
% legend
% grid on
% set(gca,'FontSize',20);% %
% figure,plot(fs,Relative_error,'bo')
% title('Relative error vs. Sampling frequency', 'fontsize',20)
% ylabel('Relative error [%]', 'fontsize',20)
% xlabel('Sampling frequency [Hz]', 'fontsize',20)
