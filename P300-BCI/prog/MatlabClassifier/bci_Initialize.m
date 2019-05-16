function bci_Initialize( in_signal_dims, out_signal_dims )
global bci_Parameters bci_States;
global ExpMode;
global fA fB;
ExpMode = str2double(bci_Parameters.ExpMode);
if ExpMode>0
    %% 导入训练参数
    curpath = cd;
    ind = find(curpath=='\');
    mudpath = fullfile(curpath(1:ind(end-1)-1),'parms\mud');
    cd(mudpath);
    load MUD.mat;
    global TFs Twindow Tblwindow Tp3chs TMUD Tp3filter winL numchs ontim offtim;
    cd(curpath);

    %% 导入设置参数、状态
    global signal stimcode blocksize Flg outsig cubedim;
    outsig = -1*ones(1,6);
    signal = [];
    stimcode = [];
    PhaseInSequence = 0;
    Flg = 0;
    samplingrate = str2double(bci_Parameters.SamplingRate);
    % if samplingrate ~= TFs
    %     error('the sampling rate is not equal to trainning Fs');
    % end
    tem1 = str2double(bci_Parameters.StimulusDuration);
    tem2 = str2double(bci_Parameters.ISIDuration);
    % if tem1+tem2 ~= ontim+offtim
    %     str = ['the stimulust duration and ISI duration must set with the same with offline setting.',' duration: ',num2str(ontim),' ISI: ',num2str(offtim)];
    %     warning(str)
    % end
    blocksize = str2double(bci_Parameters.SampleBlockSize);
    winL = Twindow(2)-Twindow(1);
    numchs = size(Tp3chs,2);
    c = bci_Parameters.cube_dim;
    cubedim = [str2double(c{1}),str2double(c{2})];
    
    srate = samplingrate;
    srate = 200;
    fs=srate/2;
    Wp=[3/fs 20/fs];
    Ws=[2/fs 25/fs];
    [N,Wn]=cheb1ord(Wp,Ws,3,40);
    [fB,fA] = cheby1(N,0.5,Wn);   
end



