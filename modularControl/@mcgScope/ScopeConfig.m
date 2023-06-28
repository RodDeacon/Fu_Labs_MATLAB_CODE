%--------------------------------------------
% Define the GUI Controls visible to the user
%--------------------------------------------
% If you make changes to the GUI controls below, please delete the
% old config file from pwd/modularControl/configs/ to re-initialize
% GUI (else the changes will not update)!!
%--------------------------------------------

function config = ScopeConfig()

    % Use the instrument definitions to check input axis limits
    galvoConfig = mcaDAQ.galvoConfig();
    piezoConfig = mcaDAQ.piezoConfig();

    % This defines how the GUI works 
    %                     Style     String              Variable    TooltipString                                                                       Optional: Limit [min max round] (only for edit)
    config.controls = { %{ 'title',  'Galvos:  ',        NaN,        'Confocal scanning for the galvo mirrors.' },...
                        %{ 'edit',   'Range (mV): ',     200,        'The range of the scan (in X and Y), centered on the current position. If this scan goes out of bounds, it is shifted to be in bounds.',                                        [0 abs(diff(galvoConfig.kind.int2extConv(galvoConfig.kind.intRange)))]},...
                        %{ 'edit',   'Pixels (#): ',     50,         'The number of points (in each dimension) which should be sampled over the scan range.',                                                                                        [1 Inf 1]},...
                        %{ 'edit',   'Speed (mV/s): ',   200,        'The time taken for an optimization. The speed in this case will be [range/time].',     [0 Inf]},...
                        %{ 'push',   'Galvo Scan',       'galvo',    'Push to active a scan with the above parameters.' },...
                        { 'title',  'Piezos: ',         NaN,        'Confocal scanning and optimization for the piezos.' },...
                        { 'edit',   'Range (um): ',     50,         'The range of the scan (in X and Y), centered on the current position. If this scan goes out of bounds, it is shifted to be in bounds.',                                        [0 abs(diff(piezoConfig.kind.int2extConv(piezoConfig.kind.intRange)))]},...
                        { 'edit',   'Pixels (#): ',     50,         'The number of points (in each dimension) which should be sampled over the scan range.',                                                                                        [1 Inf 1]},...
                        { 'edit',   'Speed (um/s): ',   50,         'The speed at which the range should be scanned over. Each scan will take [range/speed] seconds and [range/(speed*pixels)] seconds will be spent at each point of the scan.',   [0 Inf]},...
                        { 'push',   'Piezo Scan',       'piezo',    'Push to active a scan with the above parameters.' },...
                        { 'edit',   'Range XY (um): ',  1,          'The range of the scan (in X or Y), centered on the current position. If this scan goes out of bounds, it is shifted to be in bounds.',                                         [0 abs(diff(piezoConfig.kind.int2extConv(piezoConfig.kind.intRange)))]},...
                        { 'edit',   'Range Z (um): ',   5,          'The range of the scan (in Z), centered on the current position. If this scan goes out of bounds, it is shifted to be in bounds.',                                              [0 abs(diff(piezoConfig.kind.int2extConv(piezoConfig.kind.intRange)))]},...
                        { 'edit',   'Pixels (#): ',     50,         'The number of points which should be sampled over the scan range.',                                                                                                            [1 Inf 1]},...
                        { 'edit',   'Time (s): ',       2,          'The time taken for an optimization. The speed in this case will be [range/time].',     [0 Inf]},...
                        { 'push',   'Optimize X',      'optX',      'Push to active an optimization in the X direction with the above parameters.' },...
                        { 'push',   'Optimize Y',      'optY',      'Push to active an optimization in the Y direction with the above parameters.' },...
                        { 'push',   'Optimize Z',      'optZ',      'Push to active an optimization in the Z direction with the above parameters.' },...
                        { 'title',  'PLE:  ',           NaN,        'Use the below to activate PLE scans.' },...
                        { 'edit',   'PLE Pixels (#): ', 240,        'The number of bins that are displayed. Note that (currently) 16 points are taken under every bin. The pump pixels are caclulated from the PLE and pump times.',                [0 Inf 1]},...
                        { 'edit',   'PLE Time (s): ',   10,         'The amount of time that the PLE scan should take.',                                    [0 Inf]},...
                        { 'edit',   'Pump Time (s): ',  1,          'The repump time to restore the NV charge state.',                                      [0 Inf]},...
                        { 'edit',   'PLE Scans (#): ',  20,         'The number of scans that should be taken before stopping.',                            [1 Inf 1]},...
                        { 'edit',   'Freq Min (V): ',   0,          'The voltage controlling the laser frequency at the beginning of each PLE scan.',       [-5 5]},...
                        { 'edit',   'Freq Max (V): ',   5,          'The voltage controlling the laser frequency at the end of each PLE scan.',             [-5 5]},...
                        { 'push',   'PLE',              'ple',      'Push to active a scan with the above parameters.' },...      
                        };
end