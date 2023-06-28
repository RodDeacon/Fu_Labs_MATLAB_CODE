# 2021-04-02
# This code was made for use in the Fu lab
# Find the original code under Dropbox/35share/python/vasilis
# by Vasilis Niaouris
import os
import matplotlib.pyplot as plt
from functions26.LiveUpdate import LiveUpdateGUI
from functions26.units.UnitClass import UnitClass
from multiprocessing import shared_memory
from functions26.filing.QDLFiling import QDLFDataManager
from functions26.FilenameManager import FileNumberManager as fnm
from functions26.FittingManager import FittingManager, voigt_linear_fit
import re
from functions26.InstrumentHandler import GPIBInstrument
import time
import pandas as pd
import numpy as np

def sin(x, A, c, p, T):

    return A * np.sin(p + np.divide(x, T)) + c

def get_corrected_power(wavelengths, powers, vals):

    return np.multiply(powers, sin(wavelengths, *vals))

def wavelength_to_energy(wavelength, mat=True):

    if mat:
        return 2 * 1239.8 / wavelength
    else:
        return 1239.8 / wavelength

def energy_to_GHz(energy):

    return energy * 241799

def plot_fit_PLE(xtics, ytics, min, max, name, fit='Voigt'):

    ### FitManager

    fitmng, fwhms, centers = voigt_linear_fit(xtics, ytics)

    xx = np.linspace(min, max, 1000)

    fmfwhm = re.findall('\d*\.?\d+', str(fwhms))[0]
    start_wl=737.632
    fwE = wavelength_to_energy(start_wl, True) - wavelength_to_energy(float(fmfwhm)+start_wl, True)
    fwhmGHz = energy_to_GHz(fwE)

    plt.plot(xtics, ytics, label='data', marker='o', color='green', linestyle='none')
    plt.plot(xx, fitmng.y_fit, label='FWHM: ' + str(fwhmGHz)[:7] + 'GHz')
    plt.title("Voigt fit to " + name)
    plt.legend()
    plt.show()
    return fitmng.fit_pars

def plot_power_spc(min, max, energy=False):
    """
    :param min: Minimum file in directory to be read
    :param max: Maximum file in directory to be read
    :param energy: True = Energy plot, False = Wavelength plot
    :return: Plot of SPCM counts and power with standard deviation error bars
    """

    # Define data to be plotted
    spc_vals = []
    spc_stdevs = []
    power_vals = []
    power_stdevs = []

    xstics = []
    xptics = []

    # Read data from folder (only qdlfs)

    print(os.listdir())

    dir = './data4/'

    files = fnm([i for i in range(1, 1000)], ['qdlf'], dir)

    for filename in files.filenames:


        file = QDLFDataManager.load(dir + filename)

        wavelength = fnm._get_file_info(filename)['Lsr: Wavelength (nm)']
        if(fnm._get_file_info(filename)['Measurement Type'] == 'spcm'):

            mean = np.array(file.data['y1']).mean()
            stdev = np.array(file.data['y1']).std()

            if (stdev / mean):
                spc_vals.append(mean)
                spc_stdevs.append(stdev)

                if energy:
                    xstics.append(wavelength_to_energy(wavelength))
                else:
                    xstics.append(wavelength)
        elif(fnm._get_file_info(filename)['Measurement Type'] == 'power'):

            mean = np.array(file.data['y1']).mean()
            stdev = np.array(file.data['y1']).std()

            if (stdev / mean):
                power_vals.append(mean)
                power_stdevs.append(stdev)

                if energy:
                    xptics.append(wavelength_to_energy(wavelength))
                else:
                    xptics.append(wavelength)

    fig, ax1 = plt.subplots()

    phaseshift = 0

    #Correction model... [Amplitude, average, phase, period/2pi]
    corr_pow_vals = get_corrected_power(xptics, power_vals, [0.06164462, 0.58686473, 1.29227259+phaseshift, 0.00615929629766])

    # Plot power
    if energy:
        ax1.set_xlabel('Energy (eV)')
    else:
        ax1.set_xlabel('Wavelength (nm)')
    ax1.set_ylabel('Power (microW)', color='red')
    ax1.errorbar(xptics, power_vals, yerr=power_stdevs, fmt = '-o', linestyle = 'none', color='red')
    ax1.errorbar(xptics, corr_pow_vals, yerr=power_stdevs, fmt = '-o', linestyle = 'none', color='purple')
    ax1.tick_params(axis='y', labelcolor='red')

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    # Plot single photon counts
    ax2.set_ylabel('SPCM counts', color='blue')  # we already handled the x-label with ax1
    ax2.errorbar(xstics, spc_vals, yerr=spc_stdevs, fmt = '-o', linestyle = 'none', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.title('SPCM and Power by Wavelength')
    xx = np.linspace(min, max, 1000)

    ax1.plot(xx, np.multiply(0.5, sin(xx, *[0.06164462, 0.58686473, 1.29227259, 0.00615929629766])), color='green')
    ax1.plot(xx, np.multiply(0.5, sin(xx, *[0.06164462, 0.58686473, 1.29227259+phaseshift, 0.00615929629766])), color='blue')
    plt.show()

    plt.plot(xstics, np.divide(spc_vals, corr_pow_vals), marker='o', linestyle = 'none', color='green', label='with sin')
    #plt.plot(xstics, np.divide(np.divide(spc_vals, power_vals), 0.58686473), marker='o', linestyle='none', color='yellow', label='no osc')
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Counts/(sec * power) (rel. units)')
    plt.title('Power Corrected PLE')
    plt.legend()
    plt.show()

    plot_fit_PLE(xstics, np.divide(spc_vals, corr_pow_vals), min, max, 'Power Corrected PLE', fit='Voigt')

def plot_corrected(min, max, energy=False):
    """
    :param min: Minimum file in directory to be read
    :param max: Maximum file in directory to be read
    :param energy: True = Energy plot, False = Wavelength plot
    :return: Plot of power corrected SPCM counts
    """

    c_vals = []
    xtics = []

    filerange = os.listdir()[min:max]

    for filename in filerange:
        if (filename.find("qdlf") != -1):
            file = QDLFDataManager.load(filename)

            if energy:
                xtics.append(wavelength_to_energy(file.parameters['wavelength']))
            else:
                xtics.append(file.parameters['wavelength'])

            c_vals.append(np.array(file.data['spc']).mean()/np.array(file.data['power']).mean())

    # Plot stdev of power
    color = 'tab:red'
    if energy:
        plt.xlabel('Energy (eV)')
    else:
        plt.xlabel('Wavelength (nm)')
    plt.ylabel('Power corrected counts/sec', color=color)
    plt.plot(xtics, c_vals, color=color, marker='o', linestyle='None')
    plt.tick_params(axis='y', labelcolor=color)
    plt.title('Corrected PLE')
    plt.show()

def plot_raw(dfs):
    """
    :param dfs: dataframe with data
    :return: Time dependant plot of data
    """

    sp_p_df = dfs[0]

    #Plots powers together

    fig, ax1 = plt.subplots()

    #Plot power
    color = 'tab:red'
    ax1.set_xlabel('time (s)')
    ax1.set_ylabel('Power (microW)', color=color)
    ax1.plot(sp_p_df['time'], sp_p_df['power'], color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    #Plot single photon counts
    color = 'tab:blue'
    ax2.set_ylabel('SPCM counts', color=color)  # we already handled the x-label with ax1
    ax2.plot(sp_p_df['time'], sp_p_df['spc'], color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.show()

plot_power_spc(737.550,737.750, energy=False)
#plot_corrected(0,100, energy=True)