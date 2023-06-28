import os.path
from typing import Dict, List, Any, Union

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget, QScrollArea, QSizePolicy, QGroupBox, QHBoxLayout, \
    QRadioButton, QFormLayout, QTabWidget, QTabBar, QStylePainter, QStyleOptionTab, QStyle, QLineEdit, QCheckBox, \
    QPushButton, QFileDialog, QComboBox

from gui.acquisition_settings import acquisition_settings_dictionary, get_acquisition_settings_dictionary_from_json


ACQ_MODE_SINGLE = 1
ACQ_MODE_ACCUMULATE = 2
ACQ_MODE_KINETICS = 3
ACQ_MODE_FAST_KINETICS = 4
ACQ_MODE_UNTIL_ABORT = 5
READ_MODE_FVB = 0
READ_MODE_MULTI_TRACK = 1
READ_MODE_RANDOM_TRACK = 2
READ_MODE_SINGLE_TRACK = 3
READ_MODE_IMAGE = 4
COSMIC_RAY_FILTER_OFF = 0
COSMIC_RAY_FILTER_ON = 2

acquisition_modes = {'Single': ACQ_MODE_SINGLE,
                     'Accumulate': ACQ_MODE_ACCUMULATE,
                     'Kinetics': ACQ_MODE_KINETICS,
                     'Fast Kinetics': ACQ_MODE_FAST_KINETICS,
                     'Until Abort': ACQ_MODE_UNTIL_ABORT,
                     }

readout_modes = {'FVB': READ_MODE_FVB,
                 'Multi-track': READ_MODE_MULTI_TRACK,
                 'Random-track': READ_MODE_RANDOM_TRACK,
                 'Single-track': READ_MODE_SINGLE_TRACK,
                 'Image': READ_MODE_IMAGE,
                 }

cosmic_ray_filter = {True: COSMIC_RAY_FILTER_ON,
                     False: COSMIC_RAY_FILTER_OFF}

wavemeter_names = {'WaveMaster': 'WaveMaster',
                   'WA1600': 'WA1600'}

stationary_save_file_extensions = {'qdlf': 'qdlf', 'csv': 'csv', 'json': 'json'}
continuous_save_file_extensions = {'mqdlf': 'mqdlf', 'csv': 'csv', 'json': 'json'}


class HorizontalTabBar(QTabBar):

    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionTab()
        for index in range(self.count()):
            self.initStyleOption(option, index)
            painter.drawControl(QStyle.CE_TabBarTabShape, option)
            painter.drawText(self.tabRect(index),
                             Qt.AlignCenter | Qt.TextDontClip,
                             self.tabText(index))

    def tabSizeHint(self, index):
        size = QTabBar.tabSizeHint(self, index)
        if size.width() < size.height():
            size.transpose()
        return size


class TabWidget(QTabWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabBar(HorizontalTabBar())
        self.setTabPosition(QTabWidget.West)

    def sizeHint(self) -> QtCore.QSize:
        size = super().sizeHint()
        size.setWidth(self.tabBar().sizeHint().width() + size.width())
        size.setHeight(self.tabBar().sizeHint().height() + size.height())
        return size


class GroupBox(QGroupBox):

    def __init__(self, *args, **kwargs):
        super(GroupBox, self).__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)


class LineEdit(QLineEdit):

    def __init__(self, text, parent, width=150):
        super().__init__(text, parent)
        self.setFixedSize(width, self.sizeHint().height())


class BrowseButton(QPushButton):

    def __init__(self, parent):
        super().__init__('Browse', parent)
        self.setFixedSize(100, self.sizeHint().height())


class FolderLineEdit(QWidget):

    def __init__(self, text, parent):
        super().__init__(parent)
        self.line_edit = LineEdit(text, self, 300)
        self.browse_button = BrowseButton(self)
        self.browse_button.clicked.connect(self.browse_button_process)

        layout = QHBoxLayout()
        layout.addWidget(self.line_edit)
        layout.addWidget(self.browse_button)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        self.setLayout(layout)
        self.adjustSize()

    def text(self):
        return self.line_edit.text()

    def browse_button_process(self):
        open_in_directory = os.path.join(self.line_edit.text(), '..')
        if not os.path.exists(open_in_directory):
            open_in_directory = ''
        directory = QFileDialog.getExistingDirectory(self.parent(), 'Select Folder', open_in_directory)
        if len(directory):
            self.line_edit.setText(directory)


class ComboBox(QComboBox):

    def __init__(self, parent, item_dict: Dict[Union[str, bool], Any], choice: str):
        super().__init__(parent)
        self.item_dict = item_dict
        self.addItems(self.item_dict.keys())
        self.setCurrentIndex(self.findText(choice))
        self.setFixedSize(150, self.sizeHint().height())

    def get_item_value(self, item: str) -> Any:
        return self.item_dict[item]

    def text(self):
        return self.currentText()


class CheckBox(QCheckBox):

    def __init__(self, value: bool, linked_widgets: List[LineEdit], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.linked_widgets = linked_widgets
        self.toggled.connect(self.on_toggle_action)

        self.set_initial_check_status(value)

    def set_initial_check_status(self, initial_value: bool):
        self.setChecked(initial_value)
        self.on_toggle_action()

    def on_toggle_action(self):
        if self.isChecked():
            for widget in self.linked_widgets:
                widget.setEnabled(False)
            self.setFocus()
        else:
            for widget in self.linked_widgets:
                widget.setEnabled(True)
            self.setFocus()


class WavemeterComboBox(ComboBox):
    def __init__(self, parent, item_dict: Dict[Union[str, bool], Any], choice: str):
        super().__init__(parent, item_dict, choice)
        self.dependences: Union[List[CheckBox], None] = None
        self.dependences_were_checked: Union[Dict[CheckBox, bool], None] = None
        self.currentTextChanged.connect(self.text_change_process)

    def update_dependences(self, wa1600_check_boxes: List[CheckBox]):
        self.dependences = wa1600_check_boxes
        self.dependences_were_checked = {dependence: dependence.isChecked() for dependence in self.dependences}
        self.text_change_process()

    def text_change_process(self):
        if self.dependences is not None:
            if self.currentText() == 'WA1600':
                self.dependences_were_checked = {dependence: dependence.isChecked() for dependence in self.dependences}
                for dependence in self.dependences:
                    dependence.setChecked(False)
                    dependence.setEnabled(False)
            else:
                for dependence in self.dependences:
                    dependence.setEnabled(True)
                    dependence.setChecked(self.dependences_were_checked[dependence])


class Tab(QScrollArea):
    def __init__(self, parent, tab_name, settings_dictionary):
        super().__init__(parent)

        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.horizontalScrollBar().setEnabled(False)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.tab_name = tab_name
        self.settings_dictionary = settings_dictionary

        widget = QWidget(parent)
        self.setWidget(widget)
        tab_layout = QVBoxLayout()
        widget.setLayout(tab_layout)

        self._load_dictionary_settings()
        self._set_boxes(tab_layout)
        self.widget().adjustSize()
        self.adjustSize()

    def sizeHint(self) -> QtCore.QSize:
        size = super(Tab, self).sizeHint()
        size.setWidth(self.verticalScrollBar().sizeHint().width() + size.width())
        return size

    def set_new_box(self, box_name: str, box_widgets: Dict):
        new_box = GroupBox(box_name)
        layout = QFormLayout()
        new_box.setLayout(layout)
        for key in box_widgets:
            layout.addRow(key, box_widgets[key])

        self.boxes[box_name] = new_box

    def _set_boxes(self, tab_layout: QVBoxLayout):
        self.boxes = {}
        for box_name in self.box_dictionary:
            self.set_new_box(box_name, self.box_dictionary[box_name])
        for box_name in self.boxes:
            tab_layout.addWidget(self.boxes[box_name])

        tab_layout.addStretch()

    def _load_dictionary_settings(self):
        settings_dictionary: Dict = self.settings_dictionary[self.tab_name]
        self.box_dictionary = {}
        for box_name, settings_sub_dictionary in settings_dictionary.items():
            self.box_dictionary[box_name] = {}
            for setting_name, setting_value in settings_sub_dictionary.items():
                if not isinstance(setting_value, bool):
                    if setting_name == 'Acquisition Mode':
                        self.box_dictionary[box_name][setting_name] = ComboBox(
                            self, acquisition_modes, str(setting_value))
                    elif setting_name == 'Readout Mode':
                        self.box_dictionary[box_name][setting_name] = ComboBox(
                            self, readout_modes, str(setting_value))
                    elif setting_name == 'Wavemeter Name':
                        self.box_dictionary[box_name][setting_name] = WavemeterComboBox(
                            self, wavemeter_names, str(setting_value))
                    else:
                        self.box_dictionary[box_name][setting_name] = LineEdit(str(setting_value), self)
            for setting_name, setting_value in settings_sub_dictionary.items():
                if isinstance(setting_value, bool):
                    if setting_name == "Use Pre-existing":
                        dependence_list = list(self.box_dictionary[box_name].values())
                    else:
                        dependence_list = []
                    self.box_dictionary[box_name][setting_name] = CheckBox(setting_value, dependence_list)

    def get_current_settings_dictionary(self):
        dictionary = {}
        for key, box_dict in self.box_dictionary.items():
            dictionary[key] = {}
            for second_key, widget in box_dict.items():
                dictionary[key][second_key] = get_acquisition_setup_menu_widget_value(widget)
        return dictionary


def get_acquisition_setup_menu_widget_value(widget):
    if isinstance(widget, (LineEdit, FolderLineEdit, ComboBox)):
        try:
            if '.' not in widget.text():
                value = int(widget.text())
            else:
                value = float(widget.text())
        except (ValueError, TypeError):
            value = widget.text()
            if value == 'True':
                value = True
            elif value == 'False':
                value = False
            elif value == 'None':
                value = None
    elif isinstance(widget, CheckBox):
        value = bool(widget.isChecked())
    else:
        value = '???'
    return value


class AcquisitionTypeWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QHBoxLayout()
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        stationary_button = QRadioButton("Stationary")
        layout.addWidget(stationary_button)
        continuous_button = QRadioButton("Continuous")
        layout.addWidget(continuous_button)
        layout.addStretch()
        self.radio_buttons = {'Stationary': stationary_button, 'Continuous': continuous_button}

        stationary_button.setChecked(True)


class AcquisitionTypeGroupBox(GroupBox):
    def __init__(self, *args, **kwargs):
        super().__init__('Acquisition Type', *args, **kwargs)
        layout = QHBoxLayout()
        self.radio_button_widget = AcquisitionTypeWidget(self.parent())
        layout.addWidget(self.radio_button_widget)
        self.setLayout(layout)


class GeneralTab(Tab):

    def __init__(self, parent, settings_dictionary):
        super().__init__(parent, "General", settings_dictionary)

    def set_new_box(self, box_name: str, box_widgets: Dict, acquisition_type: str = "Stationary"):
        new_box = GroupBox(box_name)
        layout = QFormLayout()
        new_box.setLayout(layout)
        for key in box_widgets:
            layout.addRow(key, box_widgets[key])

        self.boxes[acquisition_type][box_name] = new_box

    def _set_acquisition_type_box(self, tab_layout: QVBoxLayout):
        self.acquisition_type_box = AcquisitionTypeGroupBox(self)
        tab_layout.addWidget(self.acquisition_type_box)

        for key, radio_button in self.acquisition_type_box.radio_button_widget.radio_buttons.items():
            radio_button.setChecked(self.settings_dictionary["General"]["Acquisition Type"][key])

        self.acquisition_type_box.radio_button_widget.radio_buttons["Stationary"].toggled.connect(
            lambda: self.change_box_dictionary_by_acquisition_type_choice(
                self.acquisition_type_box.radio_button_widget.radio_buttons["Stationary"]))

        self.acquisition_type_box.radio_button_widget.radio_buttons["Continuous"].toggled.connect(
            lambda: self.change_box_dictionary_by_acquisition_type_choice(
                self.acquisition_type_box.radio_button_widget.radio_buttons["Continuous"]))

    def _set_boxes(self, tab_layout: QVBoxLayout):

        self._set_acquisition_type_box(tab_layout)

        self.boxes = {"Stationary": {},
                      "Continuous": {}}

        for box_name in self.stationary_box_dictionary:
            self.set_new_box(box_name, self.stationary_box_dictionary[box_name], "Stationary")
        for box_name in self.boxes["Stationary"]:
            tab_layout.addWidget(self.boxes["Stationary"][box_name])

        for box_name in self.continuous_box_dictionary:
            self.set_new_box(box_name, self.continuous_box_dictionary[box_name], "Continuous")
        for box_name in self.boxes["Continuous"]:
            tab_layout.addWidget(self.boxes["Continuous"][box_name])

        tab_layout.addStretch()

        self.change_box_dictionary_by_acquisition_type_choice(
            self.acquisition_type_box.radio_button_widget.radio_buttons["Stationary"])
        self.change_box_dictionary_by_acquisition_type_choice(
            self.acquisition_type_box.radio_button_widget.radio_buttons["Continuous"])

    def _load_dictionary_settings(self):
        stationary_settings_dictionary: Dict = self.settings_dictionary[self.tab_name]["Stationary"]
        continuous_settings_dictionary: Dict = self.settings_dictionary[self.tab_name]["Continuous"]
        self.stationary_box_dictionary = {}
        for box_name, settings_sub_dictionary in stationary_settings_dictionary.items():
            self.stationary_box_dictionary[box_name] = {}
            for setting_name, setting_value in settings_sub_dictionary.items():
                if box_name == "Active Measuring Devices":
                    self.stationary_box_dictionary[box_name][setting_name] = CheckBox(setting_value, [], self)
                elif setting_name == "Folder Name":
                    self.stationary_box_dictionary[box_name][setting_name] = FolderLineEdit(str(setting_value), self)
                elif setting_name == 'Saved File Extension':
                    self.stationary_box_dictionary[box_name][setting_name] = \
                        ComboBox(self, stationary_save_file_extensions, str(setting_value))
                else:
                    self.stationary_box_dictionary[box_name][setting_name] = LineEdit(str(setting_value), self)

        self.continuous_box_dictionary = {}
        for box_name, settings_sub_dictionary in continuous_settings_dictionary.items():
            self.continuous_box_dictionary[box_name] = {}
            for setting_name, setting_value in settings_sub_dictionary.items():
                if box_name == "Active Measuring Devices":
                    self.continuous_box_dictionary[box_name][setting_name] = CheckBox(setting_value, [], self)
                elif setting_name == "Folder Name":
                    self.continuous_box_dictionary[box_name][setting_name] = FolderLineEdit(str(setting_value), self)
                elif setting_name == 'Saved File Extension':
                    self.continuous_box_dictionary[box_name][setting_name] = \
                        ComboBox(self, continuous_save_file_extensions, str(setting_value))
                else:
                    self.continuous_box_dictionary[box_name][setting_name] = LineEdit(str(setting_value), self)

    def change_box_dictionary_by_acquisition_type_choice(self, button: QRadioButton):
        for box_name, box in self.boxes[button.text()].items():
            box: GroupBox
            box.setHidden(not button.isChecked())

    def get_current_settings_dictionary(self):
        dictionary = {'Acquisition Type': {
            'Stationary': self.acquisition_type_box.radio_button_widget.radio_buttons["Stationary"].isChecked(),
            'Continuous': self.acquisition_type_box.radio_button_widget.radio_buttons["Continuous"].isChecked()}}
        super_box_dictionaries = {'Stationary': self.stationary_box_dictionary,
                                  'Continuous': self.continuous_box_dictionary}
        for box_dictionaries_key, super_box_dict in super_box_dictionaries.items():
            dictionary[box_dictionaries_key] = {}
            for key, box_dict in super_box_dict.items():
                dictionary[box_dictionaries_key][key] = {}
                for second_key, widget in box_dict.items():
                    dictionary[box_dictionaries_key][key][second_key] = get_acquisition_setup_menu_widget_value(widget)
        return dictionary


class AcquisitionSetupDialog(QDialog):

    def __init__(self, parent, settings_dictionary=acquisition_settings_dictionary):
        super().__init__(parent=parent)
        self.setWindowTitle('Acquisition Setup')
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.__post_init__(settings_dictionary)
        self.load_default_settings()

    def __post_init__(self, settings_dictionary):
        self._set_tab_widget(settings_dictionary)
        self.layout().addWidget(self.tab_widget)
        # self.adjustSize()
        self.setFixedSize(self.sizeHint())

    def _set_tab_widget(self, settings_dictionary):
        self.tab_widget = TabWidget(self)
        # layout = QVBoxLayout()
        self._set_tabs(settings_dictionary)
        # self.tab_widget.setLayout(layout)

    def _set_tabs(self, settings_dictionary):
        self.tab_dictionary = {
            "General": GeneralTab(self.parent(), settings_dictionary),
            "Laser": Tab(self.parent(), "Laser", settings_dictionary),
            "SPCM": Tab(self.parent(), "SPCM", settings_dictionary),
            "Powermeter": Tab(self.parent(), "Powermeter", settings_dictionary),
            "WA1600": Tab(self.parent(), "WA1600", settings_dictionary),
            "Andor": Tab(self.parent(), "Andor", settings_dictionary)
        }
        for name, tab in self.tab_dictionary.items():
            self.tab_widget.addTab(tab, name)
        self.tab_widget.adjustSize()

        laser_coupled_wavemeter_dependences = [
            self.tab_dictionary['General'].stationary_box_dictionary['Active Measuring Devices']['wa1600'],
            self.tab_dictionary['General'].continuous_box_dictionary['Active Measuring Devices']['wa1600']
        ]
        self.tab_dictionary['Laser'].box_dictionary['Coupled Wavemeter']['Wavemeter Name'].update_dependences(
            laser_coupled_wavemeter_dependences)

    def get_current_acquisition_settings(self):
        current_acquisition_settings_dictionary = {}
        for key in self.tab_dictionary:
            current_acquisition_settings_dictionary[key] = self.tab_dictionary[key].get_current_settings_dictionary()
        return current_acquisition_settings_dictionary

    def _clear_all(self):
        for tab in self.tab_dictionary.values():
            tab.deleteLater()
        self.tab_dictionary = None
        self.layout().removeWidget(self.tab_widget)
        self.tab_widget.deleteLater()
        self.tab_widget = None

    def load_new_settings(self, settings_dictionary: Dict):
        self._clear_all()
        self.__post_init__(settings_dictionary)

    def load_default_settings(self):
        if os.path.exists('default_acquisition_settings.json'):
            self.load_new_settings(get_acquisition_settings_dictionary_from_json('default_acquisition_settings.json'))
        else:
            self.load_new_settings(acquisition_settings_dictionary)
