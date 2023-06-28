import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
from dataclasses import dataclass, field
from functions26.FilenameManager import FileNumberManager, FilenameManager
from functions26.filing.QDLFiling import QDLFDataManager


@dataclass
class ScatterData:
    filenames: list
    means: list = field(init=False)
    stds: list = field(init=False)
    files: list = field(init=False)

    def __post_init__(self):
        means = []
        stds = []
        files = []

        for filename in self.filenames:
            file = QDLFDataManager.load(filename)
            mean = file.data['y1'].mean()
            std = file.data['y1'].std()
            means.append(mean)
            stds.append(std)

        self.files = files
        self.means = means
        self.stds = stds

    def append(self, filename: str):
        file = QDLFDataManager.load(filename)
        mean = file.data['y1'].mean()
        std = file.data['y1'].std()
        self.means.append(mean)
        self.stds.append(std)
        self.files.append(file)


class AutoPLE:

    def __init__(self, filenames, measurement_types_list):
        self.fnm = FilenameManager(filenames)
        measurement_filenames = {measurement_type: [] for measurement_type in measurement_types_list}
        wavelengths = []
        for filename in filenames:
            file_info = self.fnm._get_file_info(filename)
            for measurement_type in measurement_types_list:
                if file_info['Measurement Type'] == measurement_type:
                    measurement_filenames[measurement_type].append(filename)
            wavelength = file_info['Lsr: Wavelength (nm)']
            if wavelength not in wavelengths:
                wavelengths.append(wavelength)

        # data_columns = ['wavelength'] + [mt + ' mean' for mt in measurement_filenames.keys()] + \
        #                [mt + ' std' for mt in measurement_filenames.keys()]
        # self.data = pd.DataFrame(columns=data_columns)
        self.data = pd.DataFrame(data={})
        self.data['wavelength'] = wavelengths
        for measurement_type in measurement_filenames:
            mt_data = ScatterData(measurement_filenames[measurement_type])
            self.data[measurement_type + ' mean'] = mt_data.means
            self.data[measurement_type + ' std'] = mt_data.stds

        if 'power' in measurement_filenames:
            for measurement_type in measurement_filenames:
                mt_data = ScatterData(measurement_filenames[measurement_type])
                self.data['normalized ' + measurement_type + ' mean'] = np.array(mt_data.means)/self.data['power mean']
                self.data['normalized ' + measurement_type + ' std'] = \
                    np.sqrt((np.array(mt_data.stds) / np.array(mt_data.means)) ** 2 +
                            (self.data['power std'] / self.data['power mean']) ** 2) * \
                    self.data['normalized ' + measurement_type + ' mean']


start = 1
stop = 13
fnl = np.linspace(start, stop, stop - start + 1)
fnm = FileNumberManager(fnl, 'qdlf')

auto_ple = AutoPLE(fnm.filenames, ['power', 'spcm'])

plt.figure(1)
plt.plot(auto_ple.data['wavelength'], auto_ple.data['power mean'])
plt.figure(2)
plt.plot(auto_ple.data['wavelength'], auto_ple.data['normalized spcm mean'])

plt.show()
