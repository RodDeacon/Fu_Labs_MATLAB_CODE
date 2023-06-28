classdef mciPLE_SiV < mcInput
% mciPLE takes one PLE scan when .measure() is called. Use mcData to take many PLE scans (e.g. mciPLE vs Time). Use mcePLE for
% automated PLE scans (taking spectrum first and aligning the laser with the ZPL in the spectrum).

    methods (Static)
        % Neccessary extra vars:
        %  - axes.red
        %  - axes.green
        %  - counter
        %  - xMin
        %  - xMax
        %  - upPixels
        %  - upTime
        %  - downTime
        
        function config = defaultConfig()
            config = mciPLE_SiV.PLEConfig(0, 3, 240, 10, 1);
        end
        function config = PLEConfig(xMin, xMax, upPixels, upTime, downTime)
            config.class = 'mciPLE_SiV';
            
            config.name = 'PLE with NFLaser';

            config.kind.kind =          'PLE';
            config.kind.name =          'PLE with Lion';
            config.kind.extUnits =      'photons / s';          % 'External' units.
            config.kind.shouldNormalize = true;             % If this variable is flagged, the measurement is subtracted from the previous and is divided by the time spent on a pixel. Not that this is done outside the measurement currently in mcData (individual calls to .measure() will not have this behavior currently)
            
            
            config.axes.red =       mcaDAQ.redConfig();
            %config.axes.green =     mcaDAQ.greenConfig(); % commenting out
                                        %since we do not have green shutter
            
            config.counter =        mciDAQ.counterConfig();
            %config.axes.NPpower =   mciDAQ.NPpower();
                    % No power meter for now
            
%             config.save_folder = NaN;
%             config.pow_fig = NaN; config.pow_ax = NaN;
%             config.norm_fig = NaN; config.norm_ax = NaN;
%             config.norm1_fig = NaN; config.norm1_ax = NaN;
                            
            % Error checks on xMin and xMax:
            if xMin > xMax
                temp = xMin;
                xMin = xMax;
                xMax = temp;
                warning('mciPLE_SiV.PLEConfig(): xMin > xMax! Switching them.');
            end
            
            if xMin == xMax
                error('mciPLE_SiV.PLEConfig(): xMin == xMax! Cannot scan over zero range.');
            end
            
            m = min(config.axes.red.kind.intRange);
            M = max(config.axes.red.kind.intRange);
            
            if m > xMin
                xMin = m;
                warning('mciPLE_SiV.PLEConfig(): xMin below range of red freq axis.')
            end
            if M < xMax
                xMax = M;
                warning('mciPLE_SiV.PLEConfig(): xMax above range of red freq axis.')
            end
            
            if m > xMax
                error('mciPLE_SiV.PLEConfig(): xMax out of range');
            end
            if M < xMin
                error('mciPLE_SiV.PLEConfig(): xMin out of range');
            end
            
            config.xMin =       xMin;
            config.xMax =       xMax;
            
            % Error checks on upTime and downTime
            if upTime == 0
                error('mciPLE_SiV.PLEConfig(): upTime is zero! We will never get there on time...');
            elseif upTime < 0
                upTime = -upTime;
            end
            if downTime == 0
                error('mciPLE_SiV.PLEConfig(): downTime is zero! We will never get there on time...');
            elseif downTime < 0
                downTime = -downTime;
            end
            
            config.upTime =    upTime;
            config.downTime =  downTime;
            
            config.upPixels =   upPixels;
            config.downPixels = round(upPixels*downTime/upTime);
            
%             s = upPixels + config.downPixels
            config.kind.sizeInput =    [upPixels + config.downPixels, 1];
%             config.kind
            

            %disp('Please note that 16 scans will be taken at each pixel (undocumented feature)');
            config.scansPerBin = 16;      % Bins per scan
            b = config.scansPerBin;
            config.output = [[linspace(xMin, xMax, b*upPixels) linspace(xMax, xMin, b*config.downPixels + 1)]' [zeros(1, b*upPixels) ones(1, b*config.downPixels) 0]'];    % One extra point for diff'ing.
            config.xaxis =  linspace(xMin, xMax + (xMax - xMin)*config.downPixels/upPixels, upPixels + config.downPixels);  % x Axis with fake units

        end
    end
    
    methods
        function I = mciPLE_SiV(varin)
            I.extra = {'xMin', 'xMax', 'upPixels', 'upTime'};
            if nargin == 0
                I.construct(I.defaultConfig());
            else
                I.construct(varin);
            end
            I = mcInstrumentHandler.register(I);
            
            %Other parameters to initialize
            %I.config.save_folder = uigetdir('D:\Lion_Scans\', 'Choose save directory') ;
            %I.config.pow_fig = figure('Position',[20 70 581 222]); I.config.pow_ax=axes('Parent', I.config.pow_fig); title('Lion Power vs piezo position');xlabel('Piezo (V)');ylabel('Power @735nm (mW)');hold(I.config.pow_ax, 'on');
            
            % Normalization attempt, removing because it doesn't work!
            % Nick 03 February 2023
            %I.config.norm_fig = figure('Position',[20 400 581 222]); I.config.norm_ax=axes('Parent', I.config.norm_fig); title('PL (Scaled and power normalized) vs piezo position'); xlabel('Piezo (V)'); ylabel('PL (arb.)'); hold(I.config.norm_ax, 'on');
            %I.config.norm1_fig = figure('Position',[20 732 581 222]); I.config.norm1_ax=axes('Parent', I.config.norm1_fig); title('Raw PL (bkg sub) vs piezo position'); xlabel('Piezo (V)'); ylabel('PL (cts/s)'); hold(I.config.norm1_ax, 'on');

        end
        
%         function axes_ = getInputAxes(I)
%             axes_ = {I.config.xaxis};
%         end
    end
    
    % These methods overwrite the empty methods defined in mcInput. mcInput will use these. The capitalized methods are used in
    %   more-complex methods defined in mcInput.
    methods
        function scans = getInputScans(I)
            scans = {I.config.xaxis};
        end
        
        function units = getInputScanUnits(~)
            units = {'V'};
        end
        
        % EQ
        function tf = Eq(I, b)  % Check if a foriegn object (b) is equal to this input object (a).
            tf = strcmpi(I.config.axes.red.name,    b.config.axes.red.name) && ... % ...then check if all of the other variables are the same.
                 I.config.xMin == b.config.xMin && ...
                 I.config.xMax == b.config.xMax && ...
                 I.config.upPixels ==   b.config.upPixels && ...
                 I.config.downPixels == b.config.downPixels && ...
                 I.config.upTime ==     b.config.upTime && ...
                 I.config.downTime ==   b.config.downTime;
        end
        
        % NAME
        function str = NameShort(I)
            str = [I.config.name ' (' num2str(I.config.upPixels) ' pix and '  num2str(I.config.upTime) ' sec up; '  num2str(I.config.downTime) ' sec down; from '  num2str(I.config.xMin) ' to '  num2str(I.config.xMax) ' V)'];
        end
        function str = NameVerb(I)
            str = I.NameShort();
            %[I.config.name ' (with red laser ' I.config.axes.red.name() ' and green laser ' I.config.axes.green.name() ')'];
        end
        
        % OPEN/CLOSE
        function Open(I)
%             I.config.axes.red.open();
            I.s = daq.createSession('ni');
            
            c = mciDAQ(I.config.counter);
            c.addToSession(I.s);
            
            r = mcaDAQ(I.config.axes.red);
            r.addToSession(I.s);
%             g = mcaDAQ(I.config.axes.green);
%             g.addToSession(I.s);
%             
%             NPp = mciDAQ(I.config.axes.NPpower);
%             NPp.addToSession(I.s);
            
            if ~isfield(I.config, 'scansPerBin')
                I.config.scansPerBin = 1;
            end
            
%             r = I.config.scansPerBin*I.config.upPixels/I.config.upTime;
            I.s.Rate = I.config.scansPerBin*I.config.upPixels/I.config.upTime;
        end
        function Close(I)
%             I.config.axes.red.close();
                
%                 %reset lasers
%                 upscan = [[0]' [0]']; 
%                 I.s.queueOutputData(upscan);
%                 [d, t] = startForeground(I.s);  % Fix timing?
                
            release(I.s);
        end
        
        % MEASURE
        function data = MeasureEmulation(I, ~)
%             I.config.upPixels
%             I.config.downPixels
            data = [3+rand(I.config.upPixels, 1); 10+2*rand(I.config.downPixels, 1)];
%             size(data)
%             t = I.config.upTime + I.config.downTime
            pause(I.config.upTime + I.config.downTime);
        end
        
        
        function data = Measure(I, ~)
            
         b = I.config.scansPerBin;
        
         
            %Run the forward scan
            
                % Configure the upscan voltage axis values
                % Lower bound is xMin, upper bound is xMax, the number of
                % pixels is given by the number of pixels defined by the
                % user multiplied by the parameter b=scansPerBin, which
                % is the amount of SPCM queries per pixel.
                upscan = [[linspace(I.config.xMin, I.config.xMax, b*I.config.upPixels+1) ]'];    % One extra point for diff'ing.
                I.s.queueOutputData(upscan);
                [d, t] = startForeground(I.s);  % Fix timing?
                
                % Power meter readout (NOT IMPLEMENTED)
                %%NPp_data = (d(2:end,2)*0.5647)'; %Newport power meter set to .5647 mW range
                
                % No clue what this does... Looks like it just gets the
                % right part of the data vector from `startForeground`?
                d=d(:,1);
               
                
                % Compute the counts per second
                % Need to `diff` since data comes in as raw counts and
                % times, cumulative to the device.
                % Diffing gets the counts between queries to the SPCM.
                data1 = (diff(d)./diff(t))'; %cts/s
                %data1 = diff(d)'; %raw photon numbers
                
                
                l = length(data1);

                % Configure the output data
                data = zeros(1, I.config.upPixels);
                %%LionPower = zeros(1, I.config.upPixels);
                
                
                % The next part accumulates the data
                
                % This loop cycles the measurement readout vector `d` in
                % blocks of `b=I.config.scansPerBin`.
                % Each real pixel which is saved into data had `b`
                % subpixels within it by design of the configuration 
                % (not sure why this was implemented...)
                % This loop cycles on each of the `b` subpixels, adding it
                % to the corresponding data pixel.
                
                % E.g. if there were 3 real pixels and b=4 then the first
                % loop gives the output data as 
                % data = [b[1], b[5], b[9] ]
                % The second loop adds the second subpixel
                % data = [b[1] + b[2], b[5] + b[6], b[9] + b[10] ]
                % and so on until all four subpixels are included
                
                % The problem with this is that if time is normalized prior
                % to the accumulation of the subpixels then the data output
                % is really given in units of `counts/b*s` which multiplies
                % the number artificially.
                for ii = 1:I.config.scansPerBin
                    data = data + data1(ii:I.config.scansPerBin:l);
                    
                    %LionPower = LionPower + NPp_data(ii:I.config.scansPerBin:l);
                end              
                
                
                % If operating with counts per second, need to divide the
                % data vector by the number of scans per pixel.
                % This is because it computes the counts/s for each
                % subpixel and then adds them directly.
                data = data / I.config.scansPerBin;
                
                
            %weird issue with daq fixed temporarily with reset     
                I.Close             
                I.Open

            
            %run the backscan
                downscan = [[linspace(I.config.xMax, I.config.xMin, b*I.config.downPixels + 1)]' ];    % One extra point for diff'ing.
                I.s.queueOutputData(downscan);
                
                
                [d, t] = startForeground(I.s);  % Fix timing?

                %NPp_data = d(:,2);
                %figure; plot(t,NPp_data);
                
                d=d(:,1); %Discard the power readout
                %data2 = diff(d)'; %raw photon numbers
                data2 = (diff(d)./diff(t))'; %cts/s
                
                l = length(data2);

                %data = zeros(1, I.config.upPixels + I.config.downPixels);
                data_down = [zeros(1, I.config.downPixels)];

                for ii = 1:I.config.scansPerBin
                    data_down = data_down + data2(ii:I.config.scansPerBin:l);
                end
            
                % Likewise need to renormalize here
                data_down = data_down / I.config.scansPerBin;
                
%                 raw_data = data;
%                 raw_power = LionPower;
                %norm_data = Ndat;
                
            %make output array
                data = [data data_down];
                data(I.config.upPixels + 1) = NaN; %output raw data to viewer
                
%             %save power data to the folder
%                 dateandtime = char(datetime);               % current date and time
%                 dateandtime(dateandtime==' ') = '_';        % set whitespace to underscore
%                 dateandtime(dateandtime=='-') = '';         % delete hyphens
%                 dateandtime(dateandtime==':') = '';         % delete colons
%                 
%                 v_axis = upscan;
%                 pix = I.config.upPixels;
%                 scan_time = I.config.upTime;
%                 save([I.config.save_folder '\' dateandtime 'LionScan.mat'],'v_axis', 'scan_time', 'pix','raw_data', 'raw_power', 'norm_data', 'norm_LionPower', 'Ndat', 'NNdat');
%                 
                %data = [data; [LionPower zeros(size(data_down))]; [Ndat zeros(size(data_down))]]';
            
                
                %switch the green OD
%                 God.goto(1);
%                 pause(0.1)
%                 God.goto(0);
                
            %clean up  
            I.close();  % Inefficient, but otherwise mciPLE never gives the counter up...
            
        end
    end
end




