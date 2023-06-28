import queue
from contextlib import redirect_stdout

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSplitter

from gui.gui_plotting_area import PlotArea
from gui_logging_area import LoggingStream, LoggingArea


class CentralWidget(QSplitter):

    def __init__(self, *args, **kwargs):
        super().__init__(Qt.Vertical, *args, **kwargs)
        self._setup_plotting_area()
        self._setup_logging_area()

        self.setContentsMargins(7, 7, 7, 7)
        self.setStretchFactor(0, 0)
        self.setStretchFactor(1, 1)
        self.setSizes([1.5 * self.plot_area.sizeHint().height(), 1.5 * self.log_area.sizeHint().height()])
        print('Welcome to the Matisse PLE Scan GUI!')

    def _setup_plotting_area(self):
        self.plot_area = PlotArea()
        self.addWidget(self.plot_area)

    def _setup_logging_area(self):
        """Initialize logging queue and redirect stdout to the logging area."""
        self.log_queue = queue.Queue()
        self.log_area = LoggingArea(self.log_queue)
        self.log_area.setReadOnly(True)
        self.addWidget(self.log_area)

        # Set up a context manager to redirect stdout to the log window
        self.log_redirector = redirect_stdout(LoggingStream(self.log_queue))
        self.log_redirector.__enter__()
