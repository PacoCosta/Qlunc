%%%
% Header
% fft_test
% Simulating data processing
% ADC and frequency analyser
%
%Francisco Costa
% SWE-2022
%%%

%%
clear all
% close all
clc
%% Inputs

n_bits = 12; % N� bits ADC
V_ref  = 15; % Reference voltaje ADC
% SINAD  = 69.9;

lidar_wavelength = 1550e-9;
fs_av            = 100e6;      % sampling frequency
L                = 2^9;      %length of the signal. Cannot be lower than n_fftpoints!!!
n_fftpoints      = L;       % n� of points for each block (fft points). Cannot be higher than L!!!

fd               = 2*V_ref/lidar_wavelength;  % Doppler frequency corresponding to Vref
level_noise      = .5;

%% Uncertainty in the sampling frequency.
% Gaussian distributed sampling frequency uncertainty with mean = fs_av and stdv = sigma_feq
N=1000;
bias_fs_av =2.5e6; % +/-
% Lower and upper boundaries of the range where to find the
% frequency fs
lb = fs_av-bias_fs_av;
ub = fs_av+bias_fs_av;
% Rectangular random distribution of frequencies and periods. The
% probability is 1 for values within the range [lb,ub] and 0 outside.
% fs = (ub-lb).*rand(N,1) + lb;
% Ts = 1./fs;


Tv=1/fs_av;
tv=(0:n_fftpoints-1)*Tv;
fv = linspace(0,fs_av/2,floor(length(tv)/2+1));
% Same but with GUM
% std_fs_av = bias_fs_av/sqrt(3);
% fs = std_fs_av.*randn(N,1) + fs_av;
% Ts = 1./fs;


%% Loop to calculate the frequency spectra for each fs
n_pulses=10;% n pulses
for ind_npulses=1:n_pulses % n pulses
    % Rectangular random distribution of frequencies and periods. The
    % probability is 1 for values within the range [lb,ub] and 0 outside.
    fs = (ub-lb).*rand(N,1) + lb;
    Ts = 1./fs;
    for ind_fs=1:length(fs)
        % Time and frequency vectors
        tf{ind_fs} = (0:n_fftpoints-1)*Ts(ind_fs); %tf vector
        f{ind_fs} = linspace(0,fs(ind_fs)/2,floor(length(tf{ind_fs})/2+1));
        
        % Signal:
        t{ind_fs}  = (0:L-1)*Ts(ind_fs); %t vector
        noise      = level_noise*randn(size(t{ind_fs}));
        S{ind_fs}  = noise+(10*sin(2*pi*fd.*t{ind_fs})-2.1*sin(2*pi*10*abs(randn(1,1))*fd*t{ind_fs})+2*sin(2*pi*3*abs(randn(1,1))*fd*t{ind_fs})+...
                            1.24*sin(2*pi*6*abs(randn(1,1))*fd.*t{ind_fs})+ 1.7*sin(2*pi*2*abs(randn(1,1))*fd*t{ind_fs})-1.4*sin(2*pi*abs(randn(1,1))*fd*t{ind_fs}));% Adding up Signal contributors
        
        % Spectrum function from matlab:
        [pxx{ind_fs},fr{ind_fs}] = pspectrum(S{ind_fs}./max(abs(S{ind_fs})));
        
        
        % introduce  normally distributed random noise in the signal
        %     stdv_n=std(noise);
        X{ind_fs} =  S{ind_fs}./max(abs(S{ind_fs}))  ;
        
        %%%%%%%%%%%%%%%%%%
        % ADC:
        % Quantization of the signal
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
        
        
        %%%%%%%%%%%%%%%%%%
        % Frequency analyser:
        % FFT of the Quantised signal
        % FFT:
        P3 = fft(mean_S_quant{ind_fs}'); % Fourier transform
        P2= abs(P3')/n_fftpoints;
        P1 = P2(:,1:n_fftpoints/2+1);
        % P1(2:end-1) = 2*P1(2:end-1);
        S_fft_quant=P1.^2;
        sss(ind_fs,:)=P1.^2;
        
        %         T(1,ind_fs)=toc;
        
        %         % Time taken for each fft
        %         Time_fft(1,ind_fs)=sum(T);
        
        % Peak detection from the spectra
        [ii_mean,ii1_mean]    = max(S_fft_quant);
        f_peak(ind_fs,ind_npulses)         = f{ind_fs} (ii1_mean);
        
        % Vlos
        v_MC(ind_fs,ind_npulses) =0.5*lidar_wavelength*f_peak(ind_fs,ind_npulses);
        
        
        % Assessing Statistics:
%         mode_S_quant{ind_fs}   = mode(S_quant);

        % Velocity resolution
        V_resolution(ind_fs,:,ind_npulses)=0.5*lidar_wavelength*(2*f{ind_fs}(2));
        
        
%         mean_S{ind_fs}         = mean(X{ind_fs},1);
%         %     stdv_det{ind_fs}       = mean(stdv_n)/length(stdv_n); % experimental stdv
%         
%         
%         % Relative error in the peak detection
%         Relative_error(ind_fs,:,ind_npulses) =  100*abs((fd - f_peak(ind_fs,ind_npulses)))/fd;
%         stdv_signal (ind_fs,:,ind_npulses) = level_noise/sqrt(size(P3,1));
%         % STDV_signal (ind_fs,:) = level_noise/sqrt(size(P3,1));
%         RMSE(ind_fs,:,ind_npulses) =sqrt(mean((mean_S{ind_fs}-mean_S_quant{ind_fs}).^2));
%         SNQR(ind_fs,:,ind_npulses) =((6.02*n_bits-1.25));
%         
        % Clear variables
        clear P3
        clear S_quant
        clear S_quant_chop
        clear S_fft_quant
    end
    format shortEng
%     stdv_v_pulse(ind_npulses) = std(v_MC);
%     mean_fpeak_pulse(:,ind_npulses) = mean(f_peak(:,ind_npulses));

    % Signal mean
    Spec_mean_pulse(ind_npulses,:)  = mean(sss,1);

end

%% Statistics

% Frequency
mean_fpeak_pulse = mean(f_peak,1);
stdv_freq_pulse = std(f_peak);
format short
RE_pulse      = (stdv_freq_pulse ./mean_fpeak_pulse)*100;


% Error in LOS

% Mc method
mean_v_pulse = mean(v_MC,1);
std_v_pulse = std(v_MC);

mean_v=mean(mean_v_pulse);
stdv_v=std(mean_v_pulse);
RE_v=(stdv_v/mean_v)*100;


stdv_lambda=1e-9;
stdv_freq    = std(mean_fpeak_pulse);

% Analytical method
% u_v2=0.5*sqrt((fd^2*stdv_lambda^2+lidar_wavelength^2.*stdv_freq.^2));
% v2=0.5*lidar_wavelength*fd;
% RE_v = (u_v/m_v)*100;



Spec_mean    = mean(Spec_mean_pulse,1);
mean_f_Peak  = mean(mean_fpeak_pulse,1);


% RE=(stdv_freq/mean_f_Peak)*100;
% disp(['Peak frequency mean: ',num2str(mean_f_Peak)])
% disp(['Peak frequency variance: ',num2str((stdv_freq)^2)])
% format short

% %% Error in LOS
% stdv_lambda=1e-9;
%
% u_v=std(v_MC);
% m_v=mean(v_MC);
%
% u_v2=0.5*sqrt((fd^2*stdv_lambda^2+lidar_wavelength^2*stdv_freq^2));
% v2=0.5*lidar_wavelength*fd;
% RE_v = (u_v/m_v)*100;


%% PLOTS

% Plotting signals:
% markersize=[{'k-*'},{'b-*'},{'r-*'},{'g-*'},{'c-*'},{'m-*'},{'y-*'}];
% markersize_2=[{'r--x'},{'b--x'},{'r--x'},{'g--x'},{'c--x'},{'m--x'},{'y--x'}];
% markersize_3=[{'k-.'},{'b-.'},{'r-.'},{'g-.'},{'c-.'},{'m-.'},{'y-.'}];
% figure,hold on
% for in_sig=1:length(fs)
%     Legend1{in_sig}=['fs = ',num2str(fs(in_sig),'%.2s') , '; SNQR = ', num2str(SNQR{in_sig},'%.2s'),' dB'];
%     plot(t{in_sig}(1,:)  ,mean_S{in_sig}(1,:),'Linewidth',1.2,'displayname',Legend1{in_sig})
%     plot(t{in_sig},mean_S_quant{in_sig},'Linewidth',1.9,'displayname','Q');
%     plot(t{in_sig},mean_S{in_sig}(1,:)-mean_S_quant{in_sig},'Linewidth',1.9,'displayname',['Quantization error; N� bits =',num2str(n_bits) ]);
%     %     plot(t{i} ,X{i}(1,:)  ,markersize{i})
%     %     plot(t{i},S_quant0{i},markersize_2{i},'Linewidth',1.4);
% end
% xlabel('time [s]', 'fontsize',20)
% ylabel('[-]', 'fontsize',20)
% title(['Signal -',' sigma = ',num2str(level_noise),'; n�bits = ', num2str(n_bits)],'fontsize',25)
% hold off
% legend show
% grid on
% set(gca,'FontSize',20);


% % fft signals

figure, hold on
for in_fft=1:ind_npulses
    Legend2{in_fft}=['\sigma_{f}[Hz] =  ', num2str(stdv_freq_pulse,'%.1s') ];
    plot(fv,pow2db(Spec_mean_pulse(in_fft,:)),'displayname',Legend2{in_fft});

end
plot(fv,pow2db(Spec_mean),'-k','linewidth',3,'displayname','Averaged Doppler Spectra');
Y_text_in_plot=pow2db(max(Spec_mean)); % Takes the height of the last peak. Just a convention, to plot properly
str={['#MC samples= ', num2str(N)],['\sigma_{V}[ms^{-1}] =  ', num2str(stdv_v,'%.1s') ],['RE_{V} [%] = ', num2str(RE_v,'%.1s') ]};
text(5e6,Y_text_in_plot-.9,str, 'fontsize',25);
% set(gca, 'YScale', 'log')
% set(gca, 'XScale', 'log')
% title('Frequency spectra', 'fontsize',25)
xlabel('f [Hz]');%, 'fontsize',35)
ylabel('PSD [dB]');% 'fontsize',35)
grid on
% l1.MarkerFaceColor = l1.Color;
set(gca,'FontSize',29);

% Y_text_in_plot=pow2db(max(Spec_mean)); % Takes the height of the last peak. Just a convention, to plot properly
% str={['#MC samples= ', num2str(N)],['\sigma_{V}[ms^{-1}] =  ', num2str(stdv_v,'%.1s') ],['RE_{V} [%] = ', num2str(RE,'%.1s') ]};
% text(5e6,Y_text_in_plot-.9,str, 'fontsize',25);
% hold off
% % legend
% title('Frequency spectra', 'fontsize',25)
% xlabel('f [Hz]', 'fontsize',25)
% ylabel('PSD [dB]', 'fontsize',25)
% grid on
% % l1.MarkerFaceColor = l1.Color;
% set(gca,'FontSize',20);


figure, hold on
for in_fft=1:length(fs)
    
    plot(fr{in_fft},pow2db(pxx{in_fft}))
    
end
legend show
grid on
xlabel('Frequency (Hz)')
ylabel('Power Spectrum (dB)')
title('Default Frequency Resolution')
% ###############

%
%
% % Plotting sensitivity annalysis
% figure,plot(n_fftpoints,Relative_error,'bo')
% title('Relative error vs. N�of samples', 'fontsize',20)
% ylabel('Relative error [%]', 'fontsize',20)
% xlabel('Number of fft points', 'fontsize',20)
% grid on
% figure,plot(n_fftpoints,T,'bo')
% title('Computational time vs. N�of samples', 'fontsize',20)
% ylabel('time[s]', 'fontsize',20)
% xlabel('Number of fft points', 'fontsize',20)
% legend
% grid on
% set(gca,'FontSize',20);% %
% figure,plot(fs,Relative_error,'bo')
% title('Relative error vs. Sampling frequency', 'fontsize',20)
% ylabel('Relative error [%]', 'fontsize',20)
% xlabel('Sampling frequency [Hz]', 'fontsize',20)



% t_inf = 0:.001:2000;
% t_inf2 = 0:.01:2000;
% Signal = 5*sin(2*pi*signal_f.*t_inf)+ .9*sin(2*pi*abs(randn(1,1))*signal_f*t_inf)+sin(2*pi*abs(randn(1,1))*signal_f*t_inf)+ sin(2*pi*abs(randn(1,1))*signal_f*t_inf)+...
%     1.1*sin(2*pi*signal_f.*t_inf)+ .5*sin(2*pi*abs(randn(1,1))*signal_f*t_inf)+sin(2*pi*abs(randn(1,1))*signal_f*t_inf)+ sin(2*pi*abs(randn(1,1))*signal_f*t_inf);
% Signal2 = 5*sin(2*pi*signal_f.*t_inf2)+ .9*sin(2*pi*abs(randn(1,1))*signal_f*t_inf2)+sin(2*pi*abs(randn(1,1))*signal_f*t_inf2)+ sin(2*pi*abs(randn(1,1))*signal_f*t_inf2)+...
%     1.1*sin(2*pi*signal_f.*t_inf2)+ .5*sin(2*pi*abs(randn(1,1))*signal_f*t_inf2)+sin(2*pi*abs(randn(1,1))*signal_f*t_inf2)+ sin(2*pi*abs(randn(1,1))*signal_f*t_inf2);
