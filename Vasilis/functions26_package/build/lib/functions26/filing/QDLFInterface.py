import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from .QDLFiling import QDLFDataManager
from ..DataXXX import DataSIF, DataOP, DataT1, DataRFSpectrum, DataSPCMCounter
from ..DataMultiXXX import DataMultiSIF, DataMultiOP, DataMultiT1, DataMultiRFSpectrum, DataMultiSPCMCounter


class QDLFMultiDataManager:
    qdlf_manager_datatypes = {'sif': DataSIF,
                              'op': DataOP,
                              'multisif': DataMultiSIF,
                              }

    def __init__(self, qdlf_manager_list, datatype):
        self.qdlf_manager_list = qdlf_manager_list
        self.datatype = datatype
        self.object = self.qdlf_manager_datatypes[self.datatype].load_with_qdlf_manager(qdlf_manager_list)

    @classmethod
    def load(cls, filename_list):
        if not isinstance(filename_list, list) or not isinstance(filename_list, np.ndarray):
            raise TypeError('filename_list must be a list or an numpy.ndarray.')

        qdlf_manager_list = []
        for filename in filename_list:
            qdlf_manager_list.append(QDLFDataManager.load(filename))

        return cls(qdlf_manager_list)


class Window(QMainWindow):
    """Main Window."""
    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle("Quantum Defects Lab Files")
        self.resize(400, 200)
        # self.centralWidget = QLabel("Hello, World")
        # self.centralWidget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        # self.setCentralWidget(self.centralWidget)

        self._creat_menubar()

    def _creat_menubar(self):
        menubar = self.menuBar()

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     win = Window()
#     win.show()
#     sys.exit(app.exec_())
