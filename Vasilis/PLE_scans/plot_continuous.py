import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from functions26.filing.QDLFiling import MultiQDLF

file = MultiQDLF.load('measurement.mqdlf')

power_dict = {}
spcm_dict = {}
wavelength_dict = {}
for data_manager in file.data_managers:

    x_data = np.array(data_manager.data['x1'])
    y_data = np.array(data_manager.data['y1'])
    datatype = data_manager.datatype
    plt.figure()
    plt.plot(x_data, y_data)
    plt.title(datatype)
    if datatype == 'power':
        power_dict = pd.DataFrame(data={'time': x_data, 'power': y_data})
    elif datatype == 'spcm':
        spcm_dict = pd.DataFrame(data={'time': x_data, 'counts': y_data})
    elif datatype == 'wavelength':
        wavelength_dict = pd.DataFrame(data={'time': x_data, 'wavelength': y_data})

power_times = np.array(power_dict['time'])
spcm_normalized_counts = []
for spcm_index, counts in enumerate(spcm_dict['counts']):
    time = float(spcm_dict['time'][spcm_index])
    power_index = np.argmin(abs(power_times-time))
    power = power_dict['power'][power_index]
    spcm_normalized_counts.append(counts/power)


wavelength = wavelength_dict['wavelength']
wavelength_diff = np.diff(wavelength)
# print(abs(np.diff(wavelength)) > 0.001)
# high_wavelength_diff_args = wavelength_diff[]
high_wavelength_diff_args = list(np.argwhere(abs(np.diff(wavelength)) > 0.0010001)[0])
print(wavelength[high_wavelength_diff_args[0]+1])
wavelength_region_limits = [-1]+high_wavelength_diff_args+[len(wavelength)-1]
print(wavelength_region_limits)
fit_pars_dict = {}
fitted_wavelengths = []
for i in range(len(wavelength_region_limits[:-1])):
    wl_time = wavelength_dict['time'][wavelength_region_limits[i]+1:wavelength_region_limits[i+1]+1]
    wl = wavelength_dict['wavelength'][wavelength_region_limits[i]+1:wavelength_region_limits[i+1]+1]
    fit_pars = np.polyfit(wl_time, wl, 1)
    fit_pars_dict[wavelength_region_limits[i+1]] = fit_pars
    fitted_wavelengths += list(fit_pars[1] + fit_pars[0]*wl_time)
    # plt.plot(wl_time, fit_pars[1] + fit_pars[0]*wl_time)

wavelength_times = wavelength_dict['time']
plt.figure()
plt.plot(wavelength_times, wavelength)
plt.plot(wavelength_times, fitted_wavelengths)
plt.figure()
spcm_wavelength = []
for spcm_index, counts in enumerate(spcm_dict['counts']):
    time = float(spcm_dict['time'][spcm_index])
    wavelength_index = np.argmin(abs(wavelength_times-time))
    wl = fitted_wavelengths[wavelength_index]
    spcm_wavelength.append(wl-737)


plt.plot(spcm_wavelength, spcm_normalized_counts, '.')




plt.show()