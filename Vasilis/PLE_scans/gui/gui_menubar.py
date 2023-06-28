import os.path
import platform
import sys
from functools import partial
from typing import Dict

import pkg_resources
from PyQt5 import QtGui
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMenu, QAction, QFileDialog, QMenuBar, QMessageBox, QDialog, QVBoxLayout, QToolBar, \
    QPushButton, QApplication, QSizePolicy, QWidget, QScrollArea, QHBoxLayout, QRadioButton, QGroupBox, QFormLayout

from gui.acquisition_settings import get_acquisition_settings_dictionary_from_json, \
    export_acquisition_settings_dictionary_to_json
from gui.gui_acquisition_setup_dialog import AcquisitionSetupDialog
from gui.gui_acquisition_manager import AcquisitionManager
from gui_theme import get_icon_with_theme_colors, get_dark_theme_pallet, \
    get_light_theme_pallet


class MenuBar(QMenuBar):

    def __init__(self, parent):
        super().__init__(parent)
        self._create_file_menu()

    def _create_file_menu(self):
        FileMenu(self)
        AcquisitionMenu(self)


class FileMenu(QMenu):

    def __init__(self, menubar):
        super().__init__("&File", menubar)
        menubar.addMenu(self)

        self._create_menu_actions(menubar)
        self._connect_actions()
        self._create_menu()

    def _create_menu(self):
        # self.addMenu(self.new_project_submenu)

        # self.addAction(self.open_project_action)
        # self.addAction(self.save_project_action)
        # self.addAction(self.save_as_project_action)
        # self.addSeparator()
        self.addMenu(self.theme_submenu)
        self.theme_submenu.addAction(self.dark_theme_action)
        self.theme_submenu.addAction(self.light_theme_action)
        self.addSeparator()
        # self.addAction(self.settings_action)
        # if platform.system() == 'Windows':
        #     self.addAction(self.add_file_association_action)
        #     self.addSeparator()
        self.addAction(self.exit_action)

    def _connect_actions(self):
        # self.open_project_action.triggered.connect(partial(open_project, self))
        # self.save_project_action.triggered.connect(partial(save_project, self))
        # self.save_as_project_action.triggered.connect(partial(save_as_project, self))

        self.dark_theme_action.triggered.connect(partial(self.change_theme, get_dark_theme_pallet))
        self.light_theme_action.triggered.connect(partial(self.change_theme, get_light_theme_pallet))

        self.exit_action.triggered.connect(self.exit_application)

        self.reset_menu_icons()

    def _create_menu_actions(self, menubar: MenuBar):
        # self.open_project_action = QAction(QIcon.fromTheme("document-open"), "&Open Project...", menubar)
        # self.open_project_action.setShortcut('Ctrl+O')
        #
        # self.save_project_action = QAction(QIcon.fromTheme("document-save"), "&Save Project", menubar)
        # self.save_project_action.setShortcut('Ctrl+S')
        #
        # self.save_as_project_action = QAction(QIcon.fromTheme("document-save"), "&Save Project As...", menubar)
        # self.save_as_project_action.setShortcut('Ctrl+Alt+S')

        self.settings_action = QAction("&Settings...", menubar)

        self.theme_submenu = QMenu("&Theme", menubar)
        self.dark_theme_action = QAction("&Dark...", menubar)
        self.light_theme_action = QAction("&Light...", menubar)

        self.exit_action = QAction(QIcon.fromTheme("application-exit"), "&Exit", menubar)
        # self.exit_action.setShortcut('Alt+F4')

    def reset_menu_icons(self):
        current_palette = QApplication.instance().palette()

        # open_project_icon_dir = os.path.abspath('gui_icons/open-folder.svg')
        # self.open_project_action.setIcon(get_icon_with_theme_colors(open_project_icon_dir, current_palette))
        #
        # save_project_icon_dir = os.path.abspath('gui_icons/save.svg')
        # self.save_project_action.setIcon(get_icon_with_theme_colors(save_project_icon_dir, current_palette))
        #
        # export_project_icon_dir = os.path.abspath('gui_icons/export-to.svg')
        # self.export_as_project_action.setIcon(get_icon_with_theme_colors(export_project_icon_dir, current_palette))

        theme_icon_dir = os.path.abspath('gui_icons/color-palette.svg')
        self.theme_submenu.setIcon(get_icon_with_theme_colors(theme_icon_dir, current_palette))

        exit_icon_dir = os.path.abspath('gui_icons/shut-down.svg')
        self.exit_action.setIcon(get_icon_with_theme_colors(exit_icon_dir, current_palette))

    def change_theme(self, get_theme_pallet):
        app = QApplication.instance()
        if app is None:
            raise RuntimeError("No Qt Application found.")
        app.setStyle("Fusion")
        app.setPalette(get_theme_pallet())

        app = QApplication.instance()
        if app is None:
            raise RuntimeError("No Qt Application found.")
        app.setStyle("Fusion")

        menubar: MenuBar = self.parent().parent().menubar

        filemenu: FileMenu = menubar.findChild(FileMenu)
        filemenu.reset_menu_icons()

        acquisitionmenu: AcquisitionMenu = menubar.findChild(AcquisitionMenu)
        acquisitionmenu.reset_menu_icons()

    @staticmethod
    def exit_application():
        sys.exit()


class AcquisitionMenu(QMenu):

    def __init__(self, menubar):
        super().__init__("&Acquisition", menubar)
        menubar.addMenu(self)

        self._create_menu_actions(menubar)
        self._connect_actions()
        self._create_menu()

        self.acquisition_setup_dialog = AcquisitionSetupDialog(self.parent().parent())
        self.acquisition_manager = AcquisitionManager(self, self.parent().parent().central_widget.plot_area)

    def _create_menu(self):
        self.addAction(self.acquisition_setup_action)
        self.addSeparator()
        self.addAction(self.load_acquisition_setup_action)
        self.addAction(self.save_acquisition_setup_action)
        self.addSeparator()
        self.addAction(self.start_acquisition_action)
        self.addAction(self.stop_acquisition_action)

    def _connect_actions(self):

        self.acquisition_setup_action.triggered.connect(self.acquisition_setup_process)
        self.load_acquisition_setup_action.triggered.connect(self.load_acquisition_setup_process)
        self.save_acquisition_setup_action.triggered.connect(self.save_acquisition_setup_process)
        self.start_acquisition_action.triggered.connect(self.start_acquisition_process)
        self.stop_acquisition_action.triggered.connect(self.stop_acquisition_process)

        self.reset_menu_icons()

    def _create_menu_actions(self, menubar: MenuBar):

        self.acquisition_setup_action = QAction("&Acquisition Setup...", menubar)
        self.acquisition_setup_action.setShortcut('Shift+A')
        self.load_acquisition_setup_action = QAction("&Load Acquisition Setup...", menubar)
        self.load_acquisition_setup_action.setShortcut('Shift+L')
        self.save_acquisition_setup_action = QAction("&Save Acquisition Setup...", menubar)
        self.save_acquisition_setup_action.setShortcut('Shift+S')

        self.start_acquisition_action = QAction("&Start Acquisition", menubar)
        self.start_acquisition_action.setShortcut('F5')

        self.stop_acquisition_action = QAction("&Stop Acquisition", menubar)
        self.stop_acquisition_action.setShortcut('Ctrl+F5')
        self.stop_acquisition_action.setDisabled(True)

    def reset_menu_icons(self):
        current_palette = QApplication.instance().palette()

        acquisition_setup_icon_dir = os.path.abspath('gui_icons/acquisition-setup2.png')
        self.acquisition_setup_action.setIcon(get_icon_with_theme_colors(acquisition_setup_icon_dir, current_palette))

        start_icon_dir = os.path.abspath('gui_icons/start.svg')
        self.start_acquisition_action.setIcon(get_icon_with_theme_colors(start_icon_dir, current_palette))

        stop_icon_dir = os.path.abspath('gui_icons/stop.svg')
        self.stop_acquisition_action.setIcon(get_icon_with_theme_colors(stop_icon_dir, current_palette))

    def acquisition_setup_process(self):
        self.acquisition_setup_dialog.exec()

    def load_acquisition_setup_process(self):
        filename: str = QFileDialog.getOpenFileName(self.parent(), 'Load Acquisition Setup', '',
                                                    "JavaScript Open Notation (*.json);;"
                                                    "All Files (*)")[0]
        try:
            if filename != '':
                settings_dictionary = get_acquisition_settings_dictionary_from_json(filename)
                self.acquisition_setup_dialog.load_new_settings(settings_dictionary)
        except Exception as e:
            print(e)
            message_box = SimpleMessageBox("'Load Acquisition Setup' has failed...",
                                           f"File '{filename}' is not compatible or does not exist.",
                                           QMessageBox.Information)
            message_box.exec()

    def save_acquisition_setup_process(self):
        filename: str = QFileDialog.getSaveFileName(self.parent(), 'Save Acquisition Setup', '',
                                                    "JavaScript Open Notation (*.json);;"
                                                    "All Files (*)")[0]
        if len(filename):
            settings_dictionary = self.acquisition_setup_dialog.get_current_acquisition_settings()
            export_acquisition_settings_dictionary_to_json(settings_dictionary, filename)

            message_box = SimpleMessageBox("'Save Acquisition Setup' was successful...",
                                           f"File '{filename}' was saved.",
                                           QMessageBox.Information)
            message_box.exec()

    def start_acquisition_process(self):
        self.start_acquisition_action.setDisabled(True)
        self.stop_acquisition_action.setEnabled(True)
        self.acquisition_manager.start_ple_scan(True)
        self.acquisition_manager.start_plotting(True)

    def stop_acquisition_process(self):
        self.stop_acquisition_action.setDisabled(True)
        self.start_acquisition_action.setEnabled(True)
        self.acquisition_manager.stop_ple_scan()
        self.acquisition_manager.stop_plotting()


class SimpleMessageBox(QMessageBox):

    def __init__(self, title, message, icon: QMessageBox.Icon = QMessageBox.Information):
        super().__init__()
        self.setIcon(icon)
        self.setWindowTitle(title)
        self.setText(message)
