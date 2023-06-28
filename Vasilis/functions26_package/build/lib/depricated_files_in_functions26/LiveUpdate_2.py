from spinmob import egg
import time
import numpy as np
import threading
import seaborn as sns
from pandas import DataFrame
from .units.UnitClass import UnitClass
from functools import partial


class AnimationManagerGUI:

    def __init__(self, initial_data_sets, collecting_data_function, shutdown_function=None, window_name='Live Update',
                 run_on_call=False, refresh_time_step=0.1, font_size=100, plot_labels=None, xaxis_points=0):

        # We accept a list with two rows like so: data_set = [[x1,x2,x3], [y1,y2,y3]]
        # or a list of multiple datasets of the aforementioned configuration
        if isinstance(initial_data_sets, DataFrame):
            raise TypeError('If you are only providing 1 set of x and y, you still need to put it in a list:'
                            ' [Dataframe(...)] and make sure the collecting_data_function returns a list')

        self.user_shutdown_function = shutdown_function
        self.initial_data_sets = initial_data_sets
        self.data_sets = self.initial_data_sets
        self.no_of_datasets = len(self.data_sets)
        self.window_name = window_name
        self.is_running = run_on_call
        self.refresh_time_step = refresh_time_step
        self.collecting_data_function = collecting_data_function
        self.font_size = font_size
        self.plot_labels = plot_labels
        if self.plot_labels is None:
            self.plot_labels = {'left': 'Y data', 'bottom': 'X data'}
        self.xaxis_points = xaxis_points
        self.font_size_axes = 20

        self.window = egg.gui.Window(self.window_name)

        self.start_button = egg.gui.Button("Start")
        self.window.place_object(self.start_button, 0, 0)
        self.start_button.signal_clicked.connect(self.on_start_click)
        self.current_start_click_count = 0

        self.stop_button = egg.gui.Button("Stop")
        self.window.place_object(self.stop_button, 1, 0)
        self.stop_button.signal_clicked.connect(self.on_stop_click)

        self.save_button = egg.gui.Button("Save")
        self.window.place_object(self.save_button, 2, 0)
        self.save_button.signal_clicked.connect(self.on_save_click)

        self.clear_button = egg.gui.Button("Clear")
        self.window.place_object(self.clear_button, 3, 0, alignment=2)
        self.clear_button.signal_clicked.connect(self.on_clear_click)

        self.shutdown_button = egg.gui.Button("Shutdown")
        self.window.place_object(self.shutdown_button, 4, 0, alignment=2)
        self.shutdown_button.signal_clicked.connect(self.on_shutdown_click)

        self.window.set_column_stretch(2, 20)  # creates big space between save and shutdown buttons

        self.plot_widget = egg.pyqtgraph.PlotWidget()
        self.window.place_object(self.plot_widget, 0, 1, column_span=5, alignment=0)
        self.set_plot_widget_axis_style()

        self.current_readings = []
        for i in range(self.no_of_datasets):
            self.current_readings.append(egg.gui.Label('NO DATA'))
            self.current_readings[i].set_style('font-size: ' + str(self.font_size) + 'px')
            self.window.place_object(self.current_readings[i], (i % 2) * 2, int(np.floor(2 + i / 2)), column_span=3,
                                     alignment=i % 2 + 1)

        self.plot_curve = []
        color_cycle = sns.color_palette("tab10")
        for i in range(self.no_of_datasets):
            # this is changing the plot line attributes (color, width etc).
            curve_pen = egg.pyqtgraph.mkPen(width=3, color=([crgb * 255 for crgb in color_cycle[i]]))
            self.plot_curve.append(egg.pyqtgraph.PlotCurveItem(pen=curve_pen))
            self.plot_widget.addItem(self.plot_curve[i])

        self.start_time = time.time()
        if self.is_running:
            self.start_button.click()
        else:
            self.stop_button.click()

    def on_start_click(self):
        self.current_start_click_count += 1
        start_click_count_on_entry = self.current_start_click_count
        self.is_running = True
        self.start_button.disable()
        self.stop_button.enable()

        data_thread = threading.Thread(target=partial(self.run_data_thread_loop, start_click_count_on_entry))
        data_thread.daemon = True
        plot_thread = threading.Thread(target=partial(self.run_plot_thread_loop, start_click_count_on_entry))
        plot_thread.daemon = True
        reading_thread = threading.Thread(target=partial(self.run_update_reading_loop, start_click_count_on_entry))
        reading_thread.daemon = True

        data_thread.start()
        plot_thread.start()
        reading_thread.start()

    def on_stop_click(self):
        self.is_running = False
        self.stop_button.disable()
        self.start_button.enable()

    def on_clear_click(self):
        was_running = self.is_running
        if was_running:
            self.stop_button.click()
        self.start_time = time.time()
        self.data_sets = self.initial_data_sets
        for i in range(self.no_of_datasets):
            x = np.array(self.data_sets[i]['x'])
            y = np.array(self.data_sets[i]['y'])
            self.plot_curve[i].setData(x, y)
        if was_running:
            self.start_button.click()

    def on_save_click(self):
        filename = egg.pyqtgraph.FileDialog.getSaveFileName(self.window._window, 'Save File')[0]
        if filename[-4:] != '.csv':
            filename = filename + '.csv'
        file = open(filename, 'w')
        current_data_sets = self.data_sets
        dataframe_for_save = DataFrame({})
        for i, dataset in enumerate(current_data_sets):
            for key in dataset:
                dataframe_for_save[key + str(i)] = dataset[key]
        dataframe_for_save.to_csv(filename, index=False)
        print('Saving data_points after you clicked save on the pop-up window.')
        file.close()

    def on_shutdown_click(self):
        self.stop_button.click()
        if self.user_shutdown_function is not None:
            self.user_shutdown_function
        else:
            print('Set your own shutdown function if you need to terminate instruments')

    def run_data_thread_loop(self, start_click_count_on_entry):
        while self.is_running and start_click_count_on_entry == self.current_start_click_count:
            self.data_sets = self.collecting_data_function(self.data_sets, self.start_time)

    def run_plot_thread_loop(self, start_click_count_on_entry):
        while self.is_running and start_click_count_on_entry == self.current_start_click_count:
            time.sleep(self.refresh_time_step)
            for i in range(self.no_of_datasets):
                x = np.array(self.data_sets[i]['x'])
                y = np.array(self.data_sets[i]['y'])
                # due to threading, and different timing, x and y are not of the same size
                if x.shape == y.shape:
                    self.plot_curve[i].setData(x[-self.xaxis_points:len(x)], y[-self.xaxis_points:len(y)])

    def run_update_reading_loop(self, start_click_count_on_entry, units='', form='{:.3f}'):
        while self.is_running and start_click_count_on_entry == self.current_start_click_count:
            time.sleep(self.refresh_time_step)
            for i in range(self.no_of_datasets):
                y = np.array(self.data_sets[i]['y'])
                if len(y) > 1:
                    self.current_readings[i].set_text(form.format(y[-1]) + units)

    def set_plot_widget_axis_style(self):
        self.plot_widget.getPlotItem()
        font = egg.pyqtgraph.QtGui.QFont()
        font.setPointSize(self.font_size_axes)
        label_style = {'color': '#FFF', 'font-size': str(self.font_size_axes) + 'pt'}
        for axis_name in ['left', 'bottom']:
            axis = self.plot_widget.getPlotItem().getAxis(axis_name)
            axis.setLabel(self.plot_labels[axis_name], **label_style)
            axis.setStyle(tickFont=font)


class AdvancedAnimationManagerGUI:

    def __init__(self, initial_data_sets, collecting_data_function, shutdown_function=None, window_name='Live Update',
                 run_on_call=False, refresh_time_step=0.1, font_size=100, plot_labels=None, xaxis_points=0):

        # We accept a list with two rows like so: data_set = [[x1,x2,x3], [y1,y2,y3]]
        # or a list of multiple datasets of the aforementioned configuration
        if isinstance(initial_data_sets, DataFrame):
            raise TypeError('If you are only providing 1 set of x and y, you still need to put it in a list:'
                            ' [Dataframe(...)] and make sure the collecting_data_function returns a list')

        self.user_shutdown_function = shutdown_function
        self.initial_data_sets = initial_data_sets
        self.data_sets = self.initial_data_sets
        self.no_of_datasets = len(self.data_sets)
        self.window_name = window_name
        self.is_running = run_on_call
        self.refresh_time_step = refresh_time_step
        self.collecting_data_function = collecting_data_function
        self.font_size = font_size
        self.plot_labels = plot_labels
        if self.plot_labels is None:
            self.plot_labels = {'left': 'Y data', 'bottom': 'X data'}
        self.xaxis_points = xaxis_points
        self.font_size_axes = 20

        self.window = egg.gui.Window(self.window_name)

        self.tab1 = egg.gui.TabArea(autosettings_path='tabs1')
        self.window.place_object(self.tab1)
        self.tab2 = egg.gui.TabArea(autosettings_path='tabs2')
        self.window.place_object(self.tab2)

        self.t_settings = self.tab1.add_tab('Settings')
        self.t_data_collection = self.tab2.add_tab('Data collection')

        self.settings = self.t_settings.place_object(egg.gui.TreeDictionary(autosettings_path='settings'))

        self.start_button = egg.gui.Button("Start")
        self.t_data_collection.place_object(self.start_button, 0, 0)
        self.start_button.signal_clicked.connect(self.on_start_click)
        self.current_start_click_count = 0

        self.stop_button = egg.gui.Button("Stop")
        self.t_data_collection.place_object(self.stop_button, 1, 0)
        self.stop_button.signal_clicked.connect(self.on_stop_click)

        self.save_button = egg.gui.Button("Save")
        self.t_data_collection.place_object(self.save_button, 2, 0)
        self.save_button.signal_clicked.connect(self.on_save_click)

        self.clear_button = egg.gui.Button("Clear")
        self.t_data_collection.place_object(self.clear_button, 3, 0, alignment=2)
        self.clear_button.signal_clicked.connect(self.on_clear_click)

        self.shutdown_button = egg.gui.Button("Shutdown")
        self.t_data_collection.place_object(self.shutdown_button, 4, 0, alignment=2)
        self.shutdown_button.signal_clicked.connect(self.on_shutdown_click)

        self.t_data_collection.set_column_stretch(2, 20)  # creates big space between save and shutdown buttons

        self.plot_widget = egg.pyqtgraph.PlotWidget()
        self.t_data_collection.place_object(self.plot_widget, 0, 1, column_span=5, alignment=0)
        self.set_plot_widget_axis_style()

        self.current_readings = []
        for i in range(self.no_of_datasets):
            self.current_readings.append(egg.gui.Label('NO DATA'))
            self.current_readings[i].set_style('font-size: ' + str(self.font_size) + 'px')
            self.t_data_collection.place_object(self.current_readings[i], (i % 2) * 2, int(np.floor(2 + i / 2)),
                                                column_span=3, alignment=i % 2 + 1)

        self.plot_curve = []
        color_cycle = sns.color_palette("tab10")
        for i in range(self.no_of_datasets):
            # this is changing the plot line attributes (color, width etc).
            curve_pen = egg.pyqtgraph.mkPen(width=3, color=([crgb * 255 for crgb in color_cycle[i]]))
            self.plot_curve.append(egg.pyqtgraph.PlotCurveItem(pen=curve_pen))
            self.plot_widget.addItem(self.plot_curve[i])

        self.start_time = time.time()
        if self.is_running:
            self.start_button.click()
        else:
            self.stop_button.click()

    def on_start_click(self):
        self.current_start_click_count += 1
        start_click_count_on_entry = self.current_start_click_count
        self.is_running = True
        self.start_button.disable()
        self.stop_button.enable()

        data_thread = threading.Thread(target=partial(self.run_data_thread_loop, start_click_count_on_entry))
        data_thread.daemon = True
        plot_thread = threading.Thread(target=partial(self.run_plot_thread_loop, start_click_count_on_entry))
        plot_thread.daemon = True
        reading_thread = threading.Thread(target=partial(self.run_update_reading_loop, start_click_count_on_entry))
        reading_thread.daemon = True

        data_thread.start()
        plot_thread.start()
        reading_thread.start()

    def on_stop_click(self):
        self.is_running = False
        self.stop_button.disable()
        self.start_button.enable()

    def on_clear_click(self):
        was_running = self.is_running
        if was_running:
            self.stop_button.click()
        self.start_time = time.time()
        self.data_sets = self.initial_data_sets
        for i in range(self.no_of_datasets):
            x = np.array(self.data_sets[i]['x'])
            y = np.array(self.data_sets[i]['y'])
            self.plot_curve[i].setData(x, y)
        if was_running:
            self.start_button.click()

    def on_save_click(self):
        filename = egg.pyqtgraph.FileDialog.getSaveFileName(self.window._window, 'Save File')[0]
        if filename[-4:] != '.csv':
            filename = filename + '.csv'
        file = open(filename, 'w')
        current_data_sets = self.data_sets
        dataframe_for_save = DataFrame({})
        for i, dataset in enumerate(current_data_sets):
            for key in dataset:
                dataframe_for_save[key + str(i)] = dataset[key]
        dataframe_for_save.to_csv(filename, index=False)
        print('Saving data_points after you clicked save on the pop-up window.')
        file.close()

    def on_shutdown_click(self):
        self.stop_button.click()
        if self.user_shutdown_function is not None:
            self.user_shutdown_function
        else:
            print('Set your own shutdown function if you need to terminate instruments')

    def run_data_thread_loop(self, start_click_count_on_entry):
        while self.is_running and start_click_count_on_entry == self.current_start_click_count:
            self.data_sets = self.collecting_data_function(self.data_sets, self.start_time)

    def run_plot_thread_loop(self, start_click_count_on_entry):
        while self.is_running and start_click_count_on_entry == self.current_start_click_count:
            time.sleep(self.refresh_time_step)
            for i in range(self.no_of_datasets):
                x = np.array(self.data_sets[i]['x'])
                y = np.array(self.data_sets[i]['y'])
                # due to threading, and different timing, x and y are not of the same size
                if x.shape == y.shape:
                    self.plot_curve[i].setData(x[-self.xaxis_points:len(x)], y[-self.xaxis_points:len(y)])

    def run_update_reading_loop(self, start_click_count_on_entry, units='', form='{:.3f}'):
        while self.is_running and start_click_count_on_entry == self.current_start_click_count:
            time.sleep(self.refresh_time_step)
            for i in range(self.no_of_datasets):
                y = np.array(self.data_sets[i]['y'])
                if len(y) > 1:
                    self.current_readings[i].set_text(form.format(y[-1]) + units)

    def set_plot_widget_axis_style(self):
        self.plot_widget.getPlotItem()
        font = egg.pyqtgraph.QtGui.QFont()
        font.setPointSize(self.font_size_axes)
        label_style = {'color': '#FFF', 'font-size': str(self.font_size_axes) + 'pt'}
        for axis_name in ['left', 'bottom']:
            axis = self.plot_widget.getPlotItem().getAxis(axis_name)
            axis.setLabel(self.plot_labels[axis_name], **label_style)
            axis.setStyle(tickFont=font)
