from PyQt5.QtGui import QFont
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg


class PlotArea(PlotWidget):
    # for basics https://www.pythonguis.com/tutorials/plotting-pyqtgraph/
    # for styling https://groups.google.com/g/pyqtgraph/c/jS1Ju8R6PXk

    def __init__(self):
        super().__init__()
        self.showGrid(x=True, y=True, alpha=0.2)
        self.showAxis('top')
        self.showAxis('right')
        styles = {'color': '#FFF', 'font-size': '20px'}
        self.setLabel("left", "SPCM mean counts", **styles)
        self.setLabel("bottom", "Wavelength", 'nm', **styles)
        for axis_name in ['left', 'bottom', 'top', 'right']:
            self.getAxis(axis_name).setTickFont(QFont('Helvetica', 12))

        self.pen = pg.mkPen(color=(255, 140, 0))
        self.brush = pg.mkBrush(color=(0, 140, 255, 120))
        self.data_line = self.plot([1, 2], [1, 2], pen=self.pen,
                                   symbol='o', symbolSize=10, symbolBrush=self.brush, symbolPen=None)

    def clear_plot_data(self):
        self.plot_area.data_line.setData([], [])
