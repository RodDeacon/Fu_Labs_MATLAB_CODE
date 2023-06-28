import ctypes
import datetime
import logging
import os
import platform
import sys
from functools import partial

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

from gui_central_widget import CentralWidget
from gui_menubar import MenuBar
from gui_theme import get_dark_theme_pallet

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)  # enable highdpi scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)  # use highdpi icons

if platform.system() == 'Windows':
    my_app_id = u'QDL.MatissePLEScan.0.0.1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)

from functions26.FittingManager import FittingManager
# TODO: Add Frequency option.
# TODO: Add measurement time-step for spcm and powermeter and wa1600 in acquisition dialog
#  and connect it to the PLE class: test result!.
# TODO: Modify the continuous scan plotting function to not stop until the acquisition stops: test result!.
# TODO: Add easy way to run a sequence after each continuous scan.
# TODO: Allow continuous scan analysis code (func26 and this gui) to work not only with (m)qdlf,
#  but also with csv and json.
# TODO: Fix issue with file extension not being added automatically in the file name when running a scan.
# TODO: Add plotting settings in new menubar item (such as labels, datasets, fonts, colors etc).
# TODO: Make other GUI for reading qdlf files. Use above plotting settings as a baseline.


class Window(QMainWindow):
    """Main Window."""

    def __init__(self):
        """Initializer."""
        super().__init__()
        self.setWindowTitle("QDL Matisse PLE Scan")
        self.resize(1000, 600)
        self.setWindowIcon(QtGui.QIcon('logo.png'))
        self._setup()

    def _setup(self):
        self._create_central_widget()
        self._create_menubar()

    def _create_central_widget(self):
        self.central_widget = CentralWidget(self)
        self.setCentralWidget(self.central_widget)

    def _create_menubar(self):
        self.menubar = MenuBar(self)
        self.setMenuBar(self.menubar)


class Application(QApplication):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setStyle("Fusion")
        self.setPalette(get_dark_theme_pallet())


def run():
    app = Application(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())


def main(divert_errors_to_log=False):
    if divert_errors_to_log:
        try:
            run()
        except Exception:
            time = str(datetime.datetime.now())
            time = time.replace(' ', '_')
            time = time.replace('-', '_')
            time = time.replace(':', '_')
            time = time.replace('.', 'p')
            logging.basicConfig(filename=f'../Error_Report_{time}.log', level=logging.DEBUG,
                                format='%(asctime)s %(message)s')
            logging.error('A critical error occurred.', exc_info=True)
    else:
        run()


if __name__ == "__main__":
    main()
