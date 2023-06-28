import os
import time
from concurrent.futures import Future
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Union, Dict, Tuple

import numpy as np
from functions26.DataAutoPLE import DataAutoStationaryPLE, DataAutoContinuousPLE
from functions26.constants import n_air

from gui.gui_utils import handled_slot, raise_error_from_future
from gui.acquisition_settings import get_acquisition_setting
from ple import PLE


class AcquisitionManager:

    def __init__(self, acquisition_menu, plot_area):
        from gui.gui_menubar import AcquisitionMenu
        self.acquisition_menu: AcquisitionMenu = acquisition_menu
        from gui.gui_plotting_area import PlotArea
        self.plot_area: PlotArea = plot_area

        self.work_executor = ThreadPoolExecutor()

        self.ple: Union[PLE, None] = None
        self.ple_scan_worker: Union[Future, None] = None

        self.ple_file: Union[DataAutoStationaryPLE, None] = None
        self.ple_plot_worker: Union[Future, None] = None
        # self.ple_plot_timer: Union[QTimer, None] = None
        self.stop_plotting_flag: bool = False

        self.x_data_key = 'x_nm'
        self.y_data_key = 'spcm_mean_counts'

    @handled_slot(bool)
    def start_ple_scan(self, checked):
        if self.ple_scan_worker and self.ple_scan_worker.running():
            print('WARNING: A PLE scan is currently in progress.')
            return

        self.set_ple_instance()
        kwargs, acquisition_type = get_acquisition_parameters_and_type(self.get_acquisition_settings_dictionary())
        if acquisition_type == 'Stationary':
            self.ple_scan_worker = self.work_executor.submit(self.ple.start_stationary_ple_scan, **kwargs)
        elif acquisition_type == 'Continuous':
            self.ple_scan_worker = self.work_executor.submit(self.ple.start_continuous_ple_scan, **kwargs)
        self.ple_scan_worker.add_done_callback(raise_error_from_future)

    def get_acquisition_settings_dictionary(self) -> Dict:
        acquisition_dialog = self.acquisition_menu.acquisition_setup_dialog
        return acquisition_dialog.get_current_acquisition_settings()

    def set_ple_instance(self):
        settings_dictionary = self.get_acquisition_settings_dictionary()
        self.ple: PLE = initialize_ple_instance(settings_dictionary)

    def clear_ple_instance(self):
        if self.ple:
            self.ple.clean_up_globals()
            self.ple = None

    def stop_ple_scan(self):
        self.clear_workers(clear_ple_scan=True)

    @handled_slot(bool)
    def start_plotting(self, checked):
        if self.ple_plot_worker and self.ple_plot_worker.running():
            print('WARNING: A PLE scan is currently in progress.')
            return

        kwargs, acquisition_type = get_acquisition_parameters_and_type(self.get_acquisition_settings_dictionary())
        if acquisition_type == 'Stationary':
            self.ple_plot_worker = self.work_executor.submit(self.start_plot_stationary, kwargs['scan_location'],
                                                             'Lsr: Wavelength (nm)', False, n_air)
        elif acquisition_type == 'Continuous':
            print(kwargs)
            self.ple_plot_worker = self.work_executor.submit(self.start_plot_continuous, kwargs['scan_name'],
                                                             kwargs['scan_location'], False, n_air)
        self.ple_plot_worker.add_done_callback(raise_error_from_future)

    def start_plot_stationary(self, folder: str, varying_variable: str, second_order: bool, refractive_index: float):
        self.stop_plotting_flag = False

        while not os.path.exists(folder):
            time.sleep(1)
            if self.stop_plotting_flag:
                return

        while len(os.listdir(folder)) < 1:
            time.sleep(1)
            if self.stop_plotting_flag:
                return

        filenames = [os.path.join(folder, f) for f in os.listdir(folder)
                     if os.path.isfile(os.path.join(folder, f)) and f.endswith('.qdlf')]
        while len(filenames) < 1:
            time.sleep(1)
            filenames = [os.path.join(folder, f) for f in os.listdir(folder)
                         if os.path.isfile(os.path.join(folder, f)) and f.endswith('.qdlf')]
            if self.stop_plotting_flag:
                return

        self.ple_file = DataAutoStationaryPLE(
            folder, varying_variable=varying_variable, second_order=second_order,
            want_oscillation=False, refractive_index=refractive_index)

        while not self.stop_plotting_flag:
            self.update_stationary_plot_data(folder)
            time.sleep(1)

    def start_plot_continuous(self, filename: str, folder: str, second_order: bool, refractive_index: float):
        self.stop_plotting_flag = False

        filename = os.path.join(folder, filename)
        while not os.path.exists(filename):
            time.sleep(1)
            if self.stop_plotting_flag:
                return

        while not self.stop_plotting_flag:
            self.update_stationary_plot_data(folder)
            self.ple_file = DataAutoContinuousPLE(
                filename, second_order=second_order, refractive_index=refractive_index, want_oscillation=False)
            self.plot_area.data_line.setData(np.array(self.ple_file.data['x_nm']),
                                             np.array(self.ple_file.data['y_counts']))
            time.sleep(1)

    def update_stationary_plot_data(self, folder: str):
        self.ple_file.append_measurement(folder, None)
        self.plot_area.data_line.setData(np.array(self.ple_file.data[self.x_data_key]),
                                         np.array(self.ple_file.data[self.y_data_key]))

    def stop_plotting(self):
        self.clear_workers(clean_ple_plot=True)

    def clear_plot_data(self):
        self.ple_file = None
        self.plot_area.clear_plot_data()

    def clear_workers(self, clear_ple_scan=False, clean_ple_plot=False):
        if clear_ple_scan:
            if self.ple_scan_worker:
                self.ple.stop_ple_tasks()
                print('Waiting for PLE scan to wrap up.')
                self.ple_scan_worker.result()
            self.ple_scan_worker = None
            self.clear_ple_instance()
            print('PLE scan ended successfully.')

        if clean_ple_plot:
            if self.ple_plot_worker:
                self.stop_plotting_flag = True
                print('Waiting for PLE plotting to wrap up.')
                self.ple_plot_worker.result()
            self.ple_plot_worker = None
            print('PLE plotting ended successfully.')

    def __del__(self):
        self.clear_workers(True, True)


def initialize_ple_instance(settings_dictionary) -> PLE:
    def get_setting(key):
        return get_acquisition_setting(key, settings_dictionary)

    powermeter_port = get_setting('Powermeter/Device/Device Port')
    powermeter_sampling_time = get_setting('Powermeter/Device/Sampling Time (s)')
    spcm_port = get_setting('SPCM/Device/Device Port')
    spcm_sampling_time = get_setting('SPCM/Device/Sampling Time (s)')
    wa1600_port = get_setting('WA1600/Device/Device Port')
    wa1600_sampling_time = get_setting('WA1600/Device/Sampling Time (s)')
    matisse_wavemeter_port = get_setting('Laser/Coupled Wavemeter/Wavemeter Port')

    return PLE(powermeter_port, spcm_port, wa1600_port, matisse_wavemeter_port,
               powermeter_sampling_time, spcm_sampling_time, wa1600_sampling_time)


def get_acquisition_parameters_and_type(settings_dictionary) -> Tuple[Dict, str]:
    def get_setting(key):
        return get_acquisition_setting(key, settings_dictionary)

    stationary_scan_type = get_setting('General/Acquisition Type/Stationary')
    if stationary_scan_type:
        acquisition_type = 'Stationary'
    else:
        acquisition_type = 'Continuous'

    devices = get_setting(f'General/{acquisition_type}/Active Measuring Devices')
    device_list = []
    for device_name, value in devices.items():
        if value:
            device_list.append(device_name)
    if 'andor' and 'andor_old' in device_list:
        device_list.remove('andor_old')

    kwargs = {
        'scan_location': get_setting(f'General/{acquisition_type}/File Options/Folder Name'),
        'initial_wavelength': get_setting(f'General/{acquisition_type}/Scan Options/Initial Wavelength (nm)'),
        'final_wavelength': get_setting(f'General/{acquisition_type}/Scan Options/Final Wavelength (nm)'),
        'file_extension': get_setting(f'General/{acquisition_type}/File Options/Saved File Extension'),
        'matisse_scanning_speed': get_setting(f'General/{acquisition_type}/Scan Options/Scanning speed'),
        'device_list': device_list, 'wavemeter_type': get_setting('Laser/Coupled Wavemeter/Wavemeter Name')
    }

    if stationary_scan_type:
        kwargs['scan_name']: str = get_setting(
            'General/Stationary/File Options/Filename Template')
        kwargs['step']: float = get_setting(
            'General/Stationary/Scan Options/Scan Step (nm)')
        kwargs['total_acq_time']: float = get_setting(
            'General/Stationary/Scan Options/Acquisition Time (s)')
        kwargs['counter_start']: int = get_setting(
            'General/Stationary/File Options/Filename No. Start')

        if 'andor' or 'andor_old' in device_list:
            if not get_setting('Andor/Spectrograph/Use Pre-existing'):
                kwargs['center_wavelength']: float = get_setting('Andor/Spectrograph/Center Wavelength (nm)')
                kwargs['grating_grooves']: int = get_setting('Andor/Spectrograph/Grating Grooves')
            if not get_setting('Andor/CCD/Use Pre-existing'):
                from gui.gui_acquisition_setup_dialog import acquisition_modes, readout_modes, cosmic_ray_filter
                kwargs['acquisition_mode']: int = acquisition_modes[get_setting('Andor/CCD/Acquisition Mode')]
                kwargs['readout_mode']: int = readout_modes[get_setting('Andor/CCD/Readout Mode')]
                kwargs['temperature']: float = get_setting('Andor/CCD/Temperature (C)')
                kwargs['cool_down']: bool = get_setting('Andor/CCD/Wait for Temperature')
                kwargs['number_accumulations']: int = get_setting('Andor/CCD/Accumulation Number')
                kwargs['cosmic_ray_filter']: int = cosmic_ray_filter[get_setting('Andor/CCD/Cosmic Ray Filter')]
    else:
        kwargs['scan_name']: str = get_setting('General/Continuous/File Options/Filename')
        kwargs['total_acquisitions'] = get_setting('General/Continuous/Scan Options/Total Acquisitions')

    return kwargs, acquisition_type
