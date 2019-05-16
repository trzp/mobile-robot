function out_signal = bci_Process( in_signal )
% written by mrtang
global bci_Parameters;
global ExpMode;
global debug_index;
global debug;
global fA;
global fB;

if ExpMode>0
    global bci_States Flg;
    global  winL Twindow Tblwindow Tp3chs TMUD Tp3filter numchs outsig cubedim;
    global signal stimcode blocksize;
    phaseinseq = bci_States.PhaseInSequence;
    
    if debug
        debug_index = 1;
        save variables.mat
    end

    if 0<phaseinseq &&  phaseinseq <=2              %处于闪烁期
        signal = cat(1,signal,in_signal');
        stimcode = [stimcode;repmat(bci_States.StimulusCode,blocksize,1)];
        Flg = 0;
        outsig = double(-1*ones(1,6));
    end
    
    if debug
        debug_index = 2;
        save variables.mat
    end
    
    if phaseinseq>2 && Flg < 1   %计算一次结果
        signal_p300 = signal(:,Tp3chs);
%         sigp300_filter = filter(Tp3filter, 1, signal_p300);


        numflash = length(stimcode);
        ind = find(stimcode(1:numflash-1)==0 & stimcode(2:numflash)>=1)+1;
        xx = length(ind);
        Responses = zeros(xx,winL,numchs,'single');
        
        if debug
            debug_index = 3;
            save variables.mat
        end

        for kk = 1:xx
            %slice = sigp300_filter(ind(kk)+Twindow(1)-1:ind(kk)+Twindow(2)-2,:);
%             mean_bl = mean(sigp300_filter(ind(kk)+Tblwindow(1):ind(kk)+Tblwindow(2),:));
            
            slice = signal_p300(ind(kk)+Twindow(1)-1:ind(kk)+Twindow(2)-2,:);
            slice_filter = filtfilt(fB,fA,slice);
            
            basesig = signal_p300(ind(kk)+Tblwindow(1):ind(kk)+Tblwindow(2),:);
            basesig_filter = filtfilt(fB,fA,basesig);
            mean_bl = mean(basesig_filter);

            baseline = repmat(mean_bl,size(slice_filter,1),1);
            Responses(kk,:,:) = slice_filter - baseline;
        end
        
        if debug
            debug_index = 4;
            save variables.mat
        end
        
        scores = [];   %清空一下
        scores = reshape(Responses,size(Responses,1),numchs*winL)*TMUD;      
        codes = stimcode(ind);
        u_code = unique(codes);
        code_num = length(u_code);
        repeat_num = length(codes)/code_num;

        scc = [scores,codes];
        scc = sortrows(scc,2);
        ss = reshape(scc(:,1),repeat_num,code_num); 
        s_sum = mean(ss,1)';
        s_sum(:,2) = u_code;
        sort_s = sortrows(s_sum,1);
        
        %排序的编号，后面的可能性更大，且从0开始,注意传递到python的数据默认为解码为float64,对应matlab应该为double
        %matlab也是动态数据类型，所以一定要注意传递过去的数据要保证存储格式正确
        outsig = double(sort_s(:,2)');    
        
%         maxr = -inf;
%         maxri = -1;
%         for jj = 1:cubedim(1)                               %分析行
%             temx = sum(scores(scores(:,2)==jj,1));
%             if temx > maxr                                  %冒泡排序
%                 maxr = temx;
%                 maxri = jj;
%             end
%         end
%         maxc = -inf;
%         maxci = 0;
%         for ii = 1+cubedim(1):cubedim(1)+cubedim(2)
%             temy = sum(scores(scores(:,2)==ii,1));
%             if temy > maxc                                  %冒泡排序
%                 maxc = temy;
%                 maxci = ii;
%             end
%         end
%         outsig = [maxri-1,maxci-cubedim(1)-1]; 

        signal = [];
        stimcode = [];
        Flg = 1;
    end
    out_signal = outsig;
else
    out_signal = double(-1*ones(1,6));
end