import os
import pickle
import time
from ctypes import *
from multiprocessing import Pipe

import numpy as np
import threading
import queue

import matisse_controller.config as cfg
from matisse_controller.shamrock_ple.ccd import CCD
from matisse_controller.shamrock_ple.plotting import *
from matisse_controller.shamrock_ple.shamrock import Shamrock
from functions26.instruments.spcm import SPCM
from functions26.instruments.powermeter import PowerMeter
from matisse_controller.shamrock_ple.spectrograph import Spectrograph
from matisse_controller.matisse.matisse import Matisse
from functions26.instruments.wa1600 import WA1600

from functions26.filing.QDLFiling import QDLFDataManager, MultiQDLF
from typing import Union

ccd: Union[CCD, None] = None
shamrock: Union[Shamrock, None] = None
spectrograph: Union[Spectrograph, None] = None
spcm: Union[SPCM, None] = None
powermeter: Union[PowerMeter, None] = None
matisse: Union[Matisse, None] = None
wa1600: Union[WA1600, None] = None


class PLE:
    """PLE scanning functionality with the Andor Shamrock and Newton CCD, the SPCM and the Newport powermeter."""

    def __init__(self, powermeter_port=None, spcm_port=None, wa1600_port=None, matisse_wavemeter_port=None,
                 powermeter_sampling_time=0.05, spcm_sampling_time=0.05, wa1600_sampling_time=0.05):
        self.powermeter_port = powermeter_port
        self.powermeter_sampling_time = powermeter_sampling_time
        self.spcm_port = spcm_port
        self.spcm_sampling_time = spcm_sampling_time
        self.wa1600_port = wa1600_port
        self.wa1600_sampling_time = wa1600_sampling_time
        self.matisse_wavemeter_port = matisse_wavemeter_port

        self.ple_exit_flag = False
        self.analysis_plot_processes = []
        self.spectrum_plot_processes = []
        self.setup_device = {'andor': self.setup_andor,
                             'andor_old': self.setup_andor_old,
                             'powermeter_A': self.setup_powermeter,
                             'powermeter_B': self.setup_powermeter,
                             'powermeter_AB': self.setup_powermeter,
                             'spcm': self.setup_spcm,
                             'wa1600': self.setup_wa1600}

    @staticmethod
    def setup_andor_old():
        """
        Initialize the interfaces to the Andor Shamrock and Newton CCD. This only needs to be run once, since the two
        devices are global variables.
        """
        global ccd
        global shamrock
        if ccd is None:
            ccd = CCD()
            ccd.shutdown()
            print('CCD initialized.')
        if shamrock is None:
            shamrock = Shamrock()
            shamrock.shutdown()
            print('Shamrock initialized.')

    @staticmethod
    def setup_andor():
        """
        Initialize the interfaces to the Andor Shamrock and Newton CCD. This only needs to be run once, since the two
        devices are global variables.
        """
        global ccd
        global spectrograph
        while not ccd or not spectrograph:
            try:
                if ccd is None:
                    ccd = CCD()
                    print('CCD initialized.')
                if spectrograph is None:
                    spectrograph = Spectrograph()
                    print('Spectrograph initialized.')
            except Exception:
                print('Connection to CCD or Spectrograph was not possible. Make sure that all the cables are connected '
                      'and the stupid Andor Solis Software is off. '
                      'Will attempt another initialization sequence in 10 seconds.')
                time.sleep(10)

    def setup_spcm(self):
        """
        Initialize the interfaces to the SPCM. This only needs to be run once, since the two devices are global
        variables.
        """
        global spcm
        if spcm is None:
            spcm = SPCM(self.spcm_port)
            print('SPCM initialized.')

    def setup_powermeter(self, channel: str):
        """
        Initialize the interfaces to the Newport powermeter. This only needs to be run once, since the two devices are
        global variables.
        """
        global powermeter
        if powermeter is None:
            powermeter = PowerMeter(channel, self.powermeter_port)
            print('Newport powermeter initialized.')

    def setup_matisse(self, wavemeter_type, scanning_speed=None):
        global matisse
        if matisse is None:
            # try:
            if wavemeter_type == 'WA1600':
                cfg.configuration.CONFIGURATION['wavemeter']['precision'] = 4
                cfg.configuration.CONFIGURATION['matisse']['stabilization']['tolerance'] = 0.0002
            matisse = Matisse(wavemeter_type, self.matisse_wavemeter_port)
            if scanning_speed is not None:
                matisse.query(f"SCAN:RISINGSPEED {scanning_speed:.20f}")
                matisse.query(f"SCAN:FALLINGSPEED {scanning_speed:.20f}")
            if matisse.all_control_loops_on() and not matisse.is_lock_correction_on():
                matisse.start_laser_lock_correction()
            # except Exception as err:
            #     matisse = None
            #     raise err

    def setup_wa1600(self):
        """
        Initialize the interfaces to the WA1600. This only needs to be run once, since the device is a global
        variable.
        """
        global wa1600
        if wa1600 is None:
            wa1600 = WA1600(self.wa1600_port)
            print('WA1600 initialized.')

    @staticmethod
    def clean_up_globals():
        """
        Remove references to the Shamrock and Newton, allowing us to re-initialize them again later.
        """
        global ccd
        global shamrock
        global spectrograph
        global spcm
        global powermeter
        global matisse
        global wa1600

        if isinstance(ccd, CCD):
            ccd.shutdown()
        if isinstance(shamrock, Shamrock):
            shamrock.shutdown()
        if isinstance(spectrograph, Spectrograph):
            spectrograph.shutdown()
        if isinstance(spcm, SPCM):
            spcm.stop_acquisition()
        if isinstance(powermeter, PowerMeter):
            powermeter.stop_acquisition()
        if isinstance(matisse, Matisse):
            matisse.__del__()
        if isinstance(wa1600, WA1600):
            wa1600.stop_acquisition()

        ccd = None
        shamrock = None
        spectrograph = None
        spcm = None
        powermeter = None
        matisse = None
        wa1600 = None

    def _setup_wavelength_tolerance(self, wavemeter_type):
        if wavemeter_type == 'WA1600':
            self.tolerance = 3E-4
        else:
            self.tolerance = 10**-cfg.get(cfg.WAVEMETER_PRECISION)

    def lock_at_wavelength(self, wavelength: float):
        """Try to lock the Matisse at a given wavelength, waiting to return until we're within a small tolerance."""
        tolerance = self.tolerance
        matisse.set_wavelength(wavelength)
        while matisse.is_setting_wavelength:
            time.sleep(5)
        lock_persisted = False
        while not lock_persisted:
            while abs(wavelength - matisse.wavemeter_wavelength()) > tolerance or \
                    (  # matisse.is_setting_wavelength or
                     matisse.is_scanning_bifi or
                     matisse.is_scanning_thin_etalon) and matisse.laser_locked():
                if self.ple_exit_flag:
                    break
                if not matisse.is_lock_correction_on() and not matisse.is_scanning_bifi \
                        and not matisse.is_scanning_thin_etalon:
                    matisse.start_laser_lock_correction()
                time.sleep(5)
            time.sleep(5)
            if abs(wavelength - matisse.wavemeter_wavelength()) <= tolerance and \
                    (  # not matisse.is_setting_wavelength and
                     not matisse.is_scanning_bifi and not
                    matisse.is_scanning_thin_etalon) and matisse.laser_locked():
                lock_persisted = True

    def stop_ple_tasks(self):
        """Trigger the exit flags to stop running scans and PLE measurements."""
        self.ple_exit_flag = True
        if ccd:
            ccd.exit_flag = True

    # def start_stationary_ple_scan(self, *args, **kwargs):
    #     print('Starting Stationary Scan!')
    #     while not self.ple_exit_flag:
    #         time.sleep(1)
    #     print('Exiting Stationary Scan!')

    def start_stationary_ple_scan(self, scan_name: str, scan_location: str, initial_wavelength: float,
                                  final_wavelength: float, step: float, device_list: list,
                                  center_wavelength: float = None, grating_grooves: int = None, total_acq_time=1,
                                  file_extension='qdlf', counter_start=1,
                                  matisse_scanning_speed=cfg.get(cfg.REFCELL_SCAN_RISING_SPEED),
                                  wavemeter_type='WaveMaster',
                                  *ccd_args, **ccd_kwargs):
        """
        Perform a PLE scan using the Andor Shamrock spectrometer and Newton CCD.

        Generates text files with data from each spectrum taken during the scan, and pickles the Python dictionary of
        all data into {scan_name}.pickle.

        Parameters
        ----------
        scan_name
            a unique name to give the PLE measurement, which will be included in the name of all the data files
        scan_location
            the name of a folder to contain all relevant scan data
        initial_wavelength
            starting wavelength for the PLE scan
        final_wavelength
            ending wavelength for the PLE scan
        step
            the desired change in wavelength between each individual scan
        center_wavelength
            the wavelength at which to set the spectrometer
        grating_grooves
            the number of grooves to use for the spectrometer grating
        plot_analysis
            whether to plot the PLE analysis in real time
        integration_start : float
            the wavelength at which to start integration for real-time analysis plotting
        integration_end : float
            the wavelength at which to stop integration for real-time analysis plotting
        *ccd_args
            args to pass to `matisse_controller.shamrock_ple.ccd.CCD.setup`
        **ccd_kwargs
            kwargs to pass to `matisse_controller.shamrock_ple.ccd.CCD.setup`
        """
        self.ple_exit_flag = False

        if not scan_name:
            print('WARNING: Name of PLE scan is required.')
            return
        if not scan_location:
            print('WARNING: Location of PLE scan is required.')
            return

        # data_file_name = os.path.join(scan_location, f"{scan_name}.qdlf")
        #
        # if os.path.exists(data_file_name):
        #     print(f"WARNING: A PLE scan has already been run for '{scan_name}'. Choose a new name and try again.")
        #     return

        if not os.path.exists(scan_location):
            print(f'WARNING: The specified scan location "{scan_location}" was not found, but was created.')
            os.mkdir(scan_location)

        self.setup_matisse(wavemeter_type, matisse_scanning_speed)
        self._setup_wavelength_tolerance(wavemeter_type)
        for device in device_list:
            if device.startswith('powermeter'):
                self.setup_device[device](device.split('_')[1])
            else:
                self.setup_device[device]()
            if device == 'andor':
                if grating_grooves is not None:
                    print(f"Setting spectrometer grating to {grating_grooves} grvs...")
                    shamrock.set_grating_grooves(grating_grooves)
                if center_wavelength is not None:
                    print(f"Setting spectrometer center wavelength to {center_wavelength}...")
                    shamrock.set_center_wavelength(center_wavelength)
                ccd.setup(total_acq_time, *ccd_args, **ccd_kwargs)

        if self.ple_exit_flag:
            self.clean_up_globals()
            return

        wavelengths = np.append(np.arange(initial_wavelength, final_wavelength, step), final_wavelength)
        print(wavelengths)
        # wavelength_range = abs(round(final_wavelength - initial_wavelength, cfg.get(cfg.WAVEMETER_PRECISION)))

        for i, wavelength in enumerate(wavelengths):
            if self.ple_exit_flag:
                print('Received PLE exit signal.')
                break
            counter = i + counter_start
            print(f"Starting acquisition {counter-counter_start + 1}/{len(wavelengths)}.")
            wavelength = round(float(wavelength), cfg.get(cfg.WAVEMETER_PRECISION))
            self.lock_at_wavelength(wavelength)
            if self.ple_exit_flag:
                print('Received PLE exit signal.')
                break
            # file_name = os.path.join(scan_location, f"{str(counter).zfill(3)}_{scan_name}_{wavelength}nm"
            #                                         f"_StepSize_{step}nm_Range_{wavelength_range}nm.sif")

            file_name = scan_name.replace('WV', str(wavelength).replace('.', 'p') + 'n')  # 737.765 -> 737p765n <- WV
            file_name = f"{str(counter).zfill(3)}_" + file_name

            start_time = time.time()
            start_event = threading.Event()
            stop_event = threading.Event()
            if 'powermeter_A' in device_list or 'powermeter_B' in device_list or 'powermeter_AB' in device_list:
                powermeter.start_acquisition(start_time, start_event, stop_event, self.powermeter_sampling_time)
            if 'spcm' in device_list:
                spcm.start_acquisition(start_time, start_event, stop_event, self.spcm_sampling_time)
            if 'wa1600' in device_list:
                wa1600.start_acquisition(start_time, start_event, stop_event, self.wa1600_sampling_time)

            print('Acquiring...')
            start_event.set()
            latest_start_time = time.time()
            if 'andor' in device_list:
                # acquisition_data = ccd.take_acquisition()  # FVB mode bins into each column, so this only grabs points along width
                ccd.start_acquisition()
                ccd.wait_for_acquisition()
            else:
                while total_acq_time > time.time() - latest_start_time:
                    time.sleep(0.01)

            stop_event.set()
            if 'powermeter_A' in device_list or 'powermeter_B' in device_list or 'powermeter_AB' in device_list:
                file_name_pm = os.path.join(scan_location, file_name + '_MsT~power.' + file_extension)
                powermeter.stop_and_save_acquisition(file_name_pm)
            if 'spcm' in device_list:
                file_name_spcm = os.path.join(scan_location, file_name + '_MsT~spcm.' + file_extension)
                spcm.stop_and_save_acquisition(file_name_spcm)
            if 'wa1600' in device_list:
                file_name_wa1600 = os.path.join(scan_location, file_name + '_MsT~wavelength.' + file_extension)
                wa1600.stop_and_save_acquisition(file_name_wa1600)
            if 'andor' in device_list:
                # scan_location = scan_location.replace('\\', '/')
                # file_name_andor = os.path.join(scan_location, file_name + '.sif')
                # file_name_andor = file_name_andor.encode('unicode-escape')
                # file_name_andor = file_name_andor.decode('latin-1')#.encode('utf-8')
                # file_name_andor = scan_location + '/' + file_name + '.sif'
                # print(file_name_andor)
                file_name_andor = file_name + '.sif'

                # print(file_name_andor)
                ccd.save_as_sif(file_name_andor, spectrograph.calibration_coefficients)
                os.rename(file_name_andor, os.path.join(scan_location, file_name_andor))  # moves file to target folder

            print('Acquisition ended')

        print('Finished PLE scan.')
        self.clean_up_globals()

    # def start_continuous_ple_scan(self, *args, **kwargs):
    #     print('Starting Continuous Scan!')
    #     while not self.ple_exit_flag:
    #         time.sleep(1)
    #     print('Exiting Continuous Scan!')

    def start_continuous_ple_scan(self, scan_name: str, scan_location: str, initial_wavelength: float,
                                  final_wavelength: float, device_list: list, total_acquisitions = 1,
                                  file_extension='mqdlf', counter_start=1, end_of_acquisition_processes=None,
                                  matisse_scanning_speed=cfg.get(cfg.REFCELL_SCAN_RISING_SPEED),
                                  wavemeter_type='WaveMaster'):
        """
        Perform a PLE scan using the Andor Shamrock spectrometer and Newton CCD.

        Generates text files with data from each spectrum taken during the scan, and pickles the Python dictionary of
        all data into {scan_name}.pickle.

        Parameters
        ----------
        scan_name
            a unique name to give the PLE measurement, which will be included in the name of all the data files
        scan_location
            the name of a folder to contain all relevant scan data
        initial_wavelength
            starting wavelength for the PLE scan
        final_wavelength
            ending wavelength for the PLE scan
        """
        self.ple_exit_flag = False

        if not scan_name:
            print('WARNING: Name of PLE scan is required.')
            return
        if not scan_location:
            print('WARNING: Location of PLE scan is required.')
            return

        if not os.path.exists(scan_location):
            print(f'WARNING: The specified scan location "{scan_location}" was not found, but was created.')
            os.mkdir(scan_location)

        self.setup_matisse(wavemeter_type, cfg.get(cfg.REFCELL_SCAN_RISING_SPEED))
        self._setup_wavelength_tolerance(wavemeter_type)

        for device in device_list:
            if device.startswith('powermeter'):
                self.setup_device[device](device.split('_')[1])
            else:
                self.setup_device[device]()

        if self.ple_exit_flag:
            print('Received PLE exit signal.')
            return

        file_name = os.path.join(scan_location, scan_name + '.' + file_extension)

        print(f"Going to initial wavelength {initial_wavelength}")
        wavelength = initial_wavelength
        wavelength = round(float(wavelength), cfg.get(cfg.WAVEMETER_PRECISION))
        self.lock_at_wavelength(wavelength)

        if self.ple_exit_flag:
            print('Received PLE exit signal.')
            return

        # matisse.query(f"SCAN:RISINGSPEED {matisse_scanning_speed:.20f}")
        # matisse.query(f"SCAN:FALLINGSPEED {matisse_scanning_speed:.20f}")
        data_manager_list = []
        identifiers = []
        for i in range(total_acquisitions):
            if self.ple_exit_flag:
                print('Received PLE exit signal.')
                return
            counter = i + counter_start
            start_event = threading.Event()
            stop_event = threading.Event()

            print(f"Starting acquisition {counter - counter_start + 1}/{total_acquisitions}.")
            start_time = time.time()

            if 'powermeter_A' in device_list or 'powermeter_B' in device_list or 'powermeter_AB' in device_list:
                powermeter.start_acquisition(start_time, start_event, stop_event, self.powermeter_sampling_time)
            if 'spcm' in device_list:
                spcm.start_acquisition(start_time, start_event, stop_event, self.spcm_sampling_time)

            print('Acquiring...')
            # start_event.set()
            latest_start_time = time.time()

            wv_sleep_time = 0.05
            wavelengths, wavelength_time_array = self.scan_matisse(initial_wavelength, final_wavelength, wv_sleep_time,
                                                                   start_event, stop_event, matisse_scanning_speed)

            stop_event.set()
            counter_string = str(counter).zfill(len(str(total_acquisitions)))

            data_manager_list.append(self.get_wavelength_data_manager(wavelengths, wavelength_time_array, start_time,
                                                                      wv_sleep_time))
            identifiers.append(counter_string + '_wavelength')
            if 'powermeter_A' in device_list or 'powermeter_B' in device_list or 'powermeter_AB' in device_list:
                data_manager_list.append(powermeter.stop_acquisition())
                identifiers.append(counter_string + '_powermeter')
            if 'spcm' in device_list:
                data_manager_list.append(spcm.stop_acquisition())
                identifiers.append(counter_string + '_spcm')

            temp_wv = initial_wavelength
            initial_wavelength = final_wavelength
            final_wavelength = temp_wv

            if end_of_acquisition_processes is not None:
                end_of_acquisition_processes(MultiQDLF(data_manager_list, identifiers, counter_string))

        print('Acquisition ended')
        multi_qdlf = MultiQDLF(data_manager_list, identifiers, 'ContinuousWavelengthScanPLE')
        multi_qdlf.save(file_name)

        print('Data saved as: ' + file_name)
        matisse.stop_scan()
        matisse.stop_laser_lock_correction()
        matisse.laser_locked()
        print('Finished PLE scan.')
        self.clean_up_globals()

    def scan_matisse(self, initial_wavelength, final_wavelength, wv_sleep_time, start_event, stop_event,
                     scanning_speed):

        wavelength_pipeline = queue.Queue()
        print_wavelength_thread = threading.Thread(target=self.wavelength_printing, args=(wavelength_pipeline,
                                                                                          stop_event), daemon=False)
        print_wavelength_thread.start()

        matisse.stabilize_off()

        original_stabilization_rising_speed = matisse.query(f"SCAN:RISINGSPEED?", True)
        original_stabilization_falling_speed = matisse.query(f"SCAN:FALLINGSPEED?", True)
        matisse.query(f"SCAN:RISINGSPEED {scanning_speed:.20f}")
        matisse.query(f"SCAN:FALLINGSPEED {scanning_speed:.20f}")

        matisse.target_wavelength = round(float(final_wavelength), cfg.get(cfg.WAVEMETER_PRECISION))
        scan_direction = int((final_wavelength - initial_wavelength) < 0)
        matisse.start_scan(scan_direction)
        start_event.set()

        wavelengths = []
        wavelength_time_array = np.array([], dtype=float)

        wavelengths.append(matisse.wavemeter_wavelength())
        wavelength_time_array = np.append(wavelength_time_array, time.time())

        if scan_direction == 0:  # goes up
            while np.mean(wavelengths[-10:]) < matisse.target_wavelength:
                if self.ple_exit_flag:
                    print('Received PLE exit signal.')
                    break
                time.sleep(wv_sleep_time)
                try:
                    wavelengths.append(matisse.wavemeter_wavelength())
                except ValueError:
                    pass
                wavelength_time_array = np.append(wavelength_time_array, time.time())
                wavelength_pipeline.put(wavelengths[-1])
        else:  # goes down
            while np.mean(wavelengths[-10:]) > matisse.target_wavelength:
                if self.ple_exit_flag:
                    print('Received PLE exit signal.')
                    break
                time.sleep(wv_sleep_time)
                try:
                    wavelengths.append(matisse.wavemeter_wavelength())
                except ValueError:
                    pass
                wavelength_time_array = np.append(wavelength_time_array, time.time())
                wavelength_pipeline.put(wavelengths[-1])

        matisse.query(f"SCAN:RISINGSPEED {original_stabilization_rising_speed:.20f}")
        matisse.query(f"SCAN:FALLINGSPEED {original_stabilization_falling_speed:.20f}")
        matisse.stabilize_on()

        wavelength_pipeline.put(None)

        return wavelengths, wavelength_time_array

    @staticmethod
    def wavelength_printing(wavelength_pipeline: queue.Queue, stop_event: threading.Event):
        wavelength = 0
        t0 = time.time()
        print_time_step = 10
        time_sleep = 0.05
        steps_per_print = int(print_time_step/time_sleep)
        counter = 0
        while not stop_event.is_set() and wavelength is not None:
            counter += 1
            wavelength = wavelength_pipeline.get()
            if counter % steps_per_print == 0:
                print(f"The wavelength is at {wavelength} nm")
            time.sleep(time_sleep)

    @staticmethod
    def get_wavelength_data_manager(wavelengths, time_array, start_time, time_step):
        data = {'x1': time_array - start_time, 'y1': wavelengths}
        data_manager = QDLFDataManager(data, parameters={'start_time': start_time, 'time_step': time_step},
                                       datatype='wavelength')

        return data_manager
