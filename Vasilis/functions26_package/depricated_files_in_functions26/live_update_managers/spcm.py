from .LiveUpdate import AnimationManagerGUI
from .InstrumentHandler import NIdaqInstrument
import numpy as np
from nidaqmx.constants import Edge, AcquisitionType
import nidaqmx.stream_readers as ndsr
from pandas import DataFrame
import threading
from functools import partial
import time


class SPCMAnimationManagerGUI(AnimationManagerGUI):

    def __init__(self, device_name, external_rate_in_hz=50, fontsize=100):
        self.spcm = NIdaqInstrument(device_name)
        self.internal_rate = 20000000  # in Hz
        self.external_rate = external_rate_in_hz  # in Hz
        self.sample_no_per_iteration = int(self.internal_rate/self.external_rate)

        self.spcm.task.timing.cfg_samp_clk_timing(self.internal_rate, source="/dev1/20MHzTimebase",
                                                  active_edge=Edge.RISING, sample_mode=AcquisitionType.CONTINUOUS)

        self.reader = ndsr.CounterReader(self.spcm.task.in_stream)
        self.spcm.\
            task.register_every_n_samples_acquired_into_buffer_event(self.sample_no_per_iteration,
                                                                     self.reading_spcm_task_callback)

        initial_data_set = [DataFrame({'x': [], 'y': []})]

        self.previous_point = 0
        super().__init__(initial_data_set, None,
                         shutdown_function=self.spcm.terminate_instrument, window_name='SPCM Live Update',
                         run_on_call=False, refresh_time_step=0.02, font_size=fontsize,
                         plot_labels={'left': 'Counts/second', 'bottom': 'Time (s)'},
                         xaxis_points=int(10*self.external_rate))


    def on_start_click(self):
        self.current_start_click_count += 1
        start_click_count_on_entry = self.current_start_click_count
        self.is_running = True
        self.start_button.disable()
        self.stop_button.enable()

        plot_thread = threading.Thread(target=partial(self.run_plot_thread_loop, start_click_count_on_entry))
        plot_thread.daemon = True
        reading_thread = threading.Thread(target=partial(self.run_update_reading_loop, start_click_count_on_entry,
                                                         form='{:.0f}'))
        reading_thread.daemon = True

        self.spcm.task.start()
        plot_thread.start()
        # reading_thread.start()

    def on_stop_click(self):
        self.is_running = False
        self.stop_button.disable()
        self.start_button.enable()
        self.spcm.task.stop()

    def on_clear_click(self):
        was_running = self.is_running
        if was_running:
            self.stop_button.click()

        self.previous_point = 0
        self.start_time = time.time()

        self.data_sets = self.initial_data_sets
        for i in range(self.no_of_datasets):
            x = np.array(self.data_sets[i]['x'])
            y = np.array(self.data_sets[i]['y'])
            self.plot_curve[i].setData(x, y)
        if was_running:
            self.start_button.click()

    def reading_spcm_task_callback(self, task_idx, every_n_samples_event_type, num_samples, callback_data):
        buffer = np.zeros(num_samples)
        self.reader.read_many_sample_double(buffer, number_of_samples_per_channel=num_samples)
        data_set = self.data_sets[0]
        new_point = buffer[-1]*self.external_rate
        newline = DataFrame({'x': [time.time() - self.start_time], 'y': [new_point - self.previous_point]})
        self.data_sets = [data_set.append(newline)]
        self.previous_point = new_point
        return 0


class SPCMAnimationManagerGUI2(AnimationManagerGUI):

    def __init__(self, device_name, external_rate_in_hz=50, fontsize=100):
        self.spcm = NIdaqInstrument(device_name)
        self.internal_rate = 20000000  # in Hz
        self.external_rate = external_rate_in_hz  # in Hz
        self.sample_no_per_iteration = int(self.internal_rate/self.external_rate)

        self.spcm.task.timing.cfg_samp_clk_timing(self.internal_rate, source="/dev1/20MHzTimebase",
                                                  active_edge=Edge.RISING, sample_mode=AcquisitionType.CONTINUOUS)

        self.reader = ndsr.CounterReader(self.spcm.task.in_stream)
        self.spcm.\
            task.register_every_n_samples_acquired_into_buffer_event(self.sample_no_per_iteration,
                                                                     self.reading_spcm_task_callback)

        initial_data_set = [DataFrame({'x': [], 'y': []})]

        self.previous_point = 0
        super().__init__(initial_data_set, None,
                         shutdown_function=self.spcm.terminate_instrument, window_name='SPCM Live Update',
                         run_on_call=False, refresh_time_step=0.02, font_size=fontsize,
                         plot_labels={'left': 'Counts/second', 'bottom': 'Time (s)'},
                         xaxis_points=int(10*self.external_rate))

    def on_start_click(self):
        self.current_start_click_count += 1
        start_click_count_on_entry = self.current_start_click_count
        self.is_running = True
        self.start_button.disable()
        self.stop_button.enable()

        plot_thread = threading.Thread(target=partial(self.run_plot_thread_loop, start_click_count_on_entry))
        plot_thread.daemon = True
        reading_thread = threading.Thread(target=partial(self.run_update_reading_loop, start_click_count_on_entry,
                                                         form='{:.0f}'))
        reading_thread.daemon = True

        self.spcm.task.start()
        plot_thread.start()
        # reading_thread.start()

    def on_stop_click(self):
        self.is_running = False
        self.stop_button.disable()
        self.start_button.enable()
        self.spcm.task.stop()

    def on_clear_click(self):
        was_running = self.is_running
        if was_running:
            self.stop_button.click()

        self.previous_point = 0
        self.start_time = time.time()

        self.data_sets = self.initial_data_sets
        for i in range(self.no_of_datasets):
            x = np.array(self.data_sets[i]['x'])
            y = np.array(self.data_sets[i]['y'])
            self.plot_curve[i].setData(x, y)
        if was_running:
            self.start_button.click()

    def reading_spcm_task_callback(self, task_idx, every_n_samples_event_type, num_samples, callback_data):
        buffer = np.zeros(num_samples)
        self.reader.read_many_sample_double(buffer, number_of_samples_per_channel=num_samples)
        data_set = self.data_sets[0]
        new_point = buffer[-1]*self.external_rate
        newline = DataFrame({'x': [time.time() - self.start_time], 'y': [new_point - self.previous_point]})
        self.data_sets = [data_set.append(newline)]
        self.previous_point = new_point
        return 0


