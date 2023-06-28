%------------------------------------------------------------------
% Define how the GUI controls behave
%------------------------------------------------------------------


function Callbacks(gui, ~, ~, cbName)
if ~isfield(gui.objects, 'isSetup')
    gui.setupObjects();
end
switch lower(cbName)
%     case 'galvo'
%         data = mcData(mcData.squareScanConfig(  gui.objects.galvos(1),...
%                                                 gui.objects.galvos(2),...
%                                                 gui.objects.counter,...
%                                                 gui.controls{1}.Value,...
%                                                 gui.controls{3}.Value,...
%                                                 gui.controls{2}.Value));
%         data.d
% 
%         mcDataViewer(data, false);  % Open mcDataViewer to view this data, but do not open the control figure
    case 'piezo'
        data = mcData(mcData.squareScanConfig(  gui.objects.piezos(1),...
                                                gui.objects.piezos(2),...
                                                gui.objects.counter,...
                                                gui.controls{1}.Value,...
                                                gui.controls{3}.Value,...
                                                gui.controls{2}.Value));
        mcDataViewer(data, false);  % Open mcDataViewer to view this data, but do not open the control figure
    case 'optx'
        data = mcData(mcData.optimizeConfig(    gui.objects.piezos(1),...
                                                gui.objects.counter,...
                                                gui.controls{4}.Value,...
                                                gui.controls{6}.Value,...
                                                gui.controls{7}.Value));
        mcDataViewer(data, false);  % Open mcDataViewer to view this data, but do not open the control figure
    case 'opty'
        data = mcData(mcData.optimizeConfig(    gui.objects.piezos(2),...
                                                gui.objects.counter,...
                                                gui.controls{4}.Value,...
                                                gui.controls{6}.Value,...
                                                gui.controls{7}.Value));
        mcDataViewer(data, false);  % Open mcDataViewer to view this data, but do not open the control figure
    case 'optz'
        data = mcData(mcData.optimizeConfig(    gui.objects.piezos(3),...
                                                gui.objects.counter,...
                                                gui.controls{5}.Value,...
                                                gui.controls{6}.Value,...
                                                gui.controls{7}.Value));
        mcDataViewer(data, false);  % Open mcDataViewer to view this data, but do not open the control figure

    case 'ple'
                                        
        % Setup the data config
        d.axes = {mcAxis};  % This is the time axis
        d.scans = {1:gui.controls{11}.Value};

        % mciPLE.PLEConfig(xMin, xMax, upPixels, upTime (s), downTime (s))
        d.inputs = {mciPLE_SiV.PLEConfig( gui.controls{12}.Value,...      % No error correction (e.g. check integer) because config should(?) catch it.
                                                gui.controls{13}.Value,...
                                                gui.controls{8}.Value,...
                                                gui.controls{9}.Value,...
                                                gui.controls{10}.Value)};
        d.intTimes = NaN; 	% Don't care about integration time because this input has a set integration time

        % Make the dataViewer and aquire
        mcDataViewer(mcData(d));
%                 case 'autople'
%                     mcDataViewer(mcData.autoPLEConfig());
        
    otherwise
        if ischar(cbName)
            disp([class(gui) '.Callbacks(s, e, cbName): No callback of name ' cbName '.']);
        else
            disp([class(gui) '.Callbacks(s, e, cbName): Did not understand cbName; not a string.']);
        end
 end
end