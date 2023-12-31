% https://github.com/optospinlab/simple_modularControl
% Check github repo for updates, bug reports and issues 
% Modified Feb-07-2021 by Srivatsa

classdef (Sealed) mcaDAQ < mcAxis
% mcaDAQ is the subclass of mcAxis that manages all NIDAQ devices. This includes:
%  - generic digital and analog outputs.
%  - piezos
%  - galvos

    methods (Static)
        % Neccessary extra vars:
        %  - dev
        %  - chn
        %  - type
        
        function config = defaultConfig()
            config = mcaDAQ.piezoConfig();
        end
        
        %----------------------------------
        % Template functions
        %----------------------------------
        config = analogConfig();
        config = digitalConfig();
        
        %--------------------------------------------
        % Your instruments
        % Add functions for your specific instruments
        %--------------------------------------------        
        config = piezoConfig();
        config = galvoConfig();
        
        
        % PLE laser configuration
        % Added Nick 31 Jan 2023
        function config = redDigitalConfig()
            config.class =              'mcaDAQ';
            
            config.name =               'Red-Flip';

            config.kind.kind =          'NIDAQdigital';
            config.kind.name =          'Red Modulation';
            config.kind.intRange =      {0 1};
            config.kind.int2extConv =   @(x)(x);                % Conversion from 'internal' units to 'external'.
            config.kind.ext2intConv =   @(x)(x);                % Conversion from 'external' units to 'internal'.
            config.kind.intUnits =      '1/0';                  % 'Internal' units.
            config.kind.extUnits =      '1/0';                  % 'External' units.
            config.kind.base =           0;                     % The (internal) value that the axis seeks at startup.

            config.dev =                'Dev1';
            config.chn =                'Port0/Line5';
            config.type =               'Output';
            
            config.keyStep =            1;
            config.joyStep =            1;
        end
        
        
        function config = redConfig()
            config.class =              'mcaDAQ';
            
            config.name =               'NFVel-Freq';

            config.kind.kind =          'NIDAQanalog';
            config.kind.name =          'New Focus Laser Freq Modulation';
            config.kind.intRange =      [-3 5];
            %config.kind.intRange = [0 5]; 
            config.kind.int2extConv =   @(x)(x);                % Conversion from 'internal' units to 'external'.
            config.kind.ext2intConv =   @(x)(x);                % Conversion from 'external' units to 'internal'.
            config.kind.intUnits =      'V';                    % 'Internal' units.
            config.kind.extUnits =      'V';                    % 'External' units.
            config.kind.base =           0;                     % The (internal) value that the axis seeks at startup.

%             config.dev =                'cDAQ1Mod1';
            config.dev =                'Dev1';
            config.chn =                'ao3';
            config.type =               'Voltage';
            
            config.keyStep =            .1;
            config.joyStep =            .5;
        end
        
        
        
        
        
    end
    
    methods
        function a = mcaDAQ(varin)
            a.extra = {'dev', 'chn', 'type'};
        
            if nargin == 0
                a.construct(mcaDAQ.defaultConfig());
            else
                a.construct(varin);
            end
            a = mcInstrumentHandler.register(a);

        end
    end
    
    % These methods overwrite the empty methods defined in mcAxis. mcAxis will use these. The capitalized methods are used in
    %   more-complex methods defined in mcAxis.
    methods
        % NAME
        function str = NameShort(a)
            str = [a.config.name ' (' a.config.dev ':' a.config.chn ':' a.config.type ')'];
        end
        function str = NameVerb(a)
            switch lower(a.config.kind.kind)
                case 'nidaqanalog'
                    str = [a.config.name ' (analog input on '  a.config.dev ', channel ' a.config.chn ' with type ' a.config.type ')'];
                case 'nidaqdigital'
                    str = [a.config.name ' (digital input on ' a.config.dev ', channel ' a.config.chn ' with type ' a.config.type ')'];
                otherwise
                    str = a.config.name;
            end
        end
        
        %EQ
        function tf = Eq(a, b)
            tf = strcmpi(a.config.dev,  b.config.dev) && ...
                 strcmpi(a.config.chn,  b.config.chn) && ...
                 strcmpi(a.config.type, b.config.type);
        end
        
        % OPEN/CLOSE
        function Open(a)
%             a.s = daq.createSession('ni');
%             a.addToSession(a.s);
            
            switch lower(a.config.kind.kind)
                case 'nidaqanalog'
                    a.s = daq.createSession('ni');
                    addAnalogOutputChannel(a.s, a.config.dev, a.config.chn, a.config.type);
                case 'nidaqdigital'
                    a.s = daq.createSession('ni');
                    addDigitalChannel(a.s, a.config.dev, a.config.chn, 'OutputOnly');
            end
            
            a.s.outputSingleScan(a.x);
        end
        function Close(a)
            a.s.release();
            delete(a.s)
        end
        
        % GOTO
        function GotoEmulation(a, x)
            a.xt = a.config.kind.ext2intConv(x);    % This will cause preformance reduction for identity conversions (@(x)(x)) e.g. digital. Change?
            a.x = a.xt;
        end
        function Goto(a, x)
            a.GotoEmulation(x);        % No need to rewrite code.
            a.s.outputSingleScan(a.x);
        end
    end
    
    methods
        % EXTRA
        function addToSession(a, s)
            if a.close()   % If the axis is not already closed, close it...
                switch lower(a.config.kind.kind)
                    case 'nidaqanalog'
                        addAnalogOutputChannel( s, a.config.dev, a.config.chn, a.config.type);
                    case 'nidaqdigital'
                        addDigitalChannel(      s, a.config.dev, a.config.chn, 'OutputOnly');
                    otherwise
                        error('This only works for NIDAQ outputs');
                end
            else
                error([a.name() ' could not be added to session.'])
            end
        end
    end
end




