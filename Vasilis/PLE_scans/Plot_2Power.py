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
from functions26.InstrumentHandler import GPIBInstrument
import time
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from scipy import fftpack

def sin(x, A, c, p, T):

    return A * np.sin(p + np.divide(x, T)) + c

def sinTdef(x, A, c, p):

    T=0.00615929629766

    return A * np.sin(p + np.divide(x, T)) + c

def wavelength_to_energy(wavelength, mat=True):

    if mat:
        return 2 * 1239.8 / wavelength
    else:
        return 1239.8 / wavelength

def plot_fft(signal, step):
    """
    :param signal: Signal to transform
    :param step: 'Time' step
    :return: Plot of the fourier transform of 'signal'
    """

    sig_fft = fftpack.fft(signal, n=10000)
    sample_freq = fftpack.fftfreq(10000, 0.001)
    plt.plot(sample_freq, np.abs(sig_fft))
    plt.xlim(40, 60)
    plt.show()
    print(1/(48.5 * np.pi))

def plot_power_spc(min, max, min_wl, max_wl, energy=False):
    """
    :param min: Minimum file in directory to be read
    :param max: Maximum file in directory to be read
    :param energy: True = Energy plot, False = Wavelength plot
    :return: Plot of SPCM counts and power with standard deviation error bars
    """

    # Define data to be plotted

    xptics = []

    # Read data from folder (only qdlfs)

    dirs = ['./data5/', './data6/']

    corrs = []
    pow1vals = []
    pow1stds = []
    pow2vals = []
    pow2stds = []

    for dir in dirs:

        files = fnm([i for i in range(1, 1000)], ['qdlf'], dir)

        power1_vals = []
        power1_stdevs = []
        power2_vals = []
        power2_stdevs = []
        xtics = []

        for filename in files.filenames:


            file = QDLFDataManager.load(dir + filename)

            print(fnm._get_file_info(filename).keys())
            wavelength = fnm._get_file_info(filename)['Lsr: Wavelength (nm)']
            if(fnm._get_file_info(filename)['Measurement Type'] == 'power'):

                mean1 = np.array(file.data['y1']).mean()
                stdev1 = np.array(file.data['y1']).std()
                mean2 = np.array(file.data['y2']).mean()
                stdev2 = np.array(file.data['y2']).std()

                if ((stdev1 / mean1) < 0.1) and ((stdev2 / mean2) < 0.1):
                    power1_vals.append(mean1)
                    power1_stdevs.append(stdev1)
                    power2_vals.append(mean2)
                    power2_stdevs.append(stdev2)

                    if energy:
                        xtics.append(wavelength_to_energy(wavelength))
                    else:
                        xtics.append(wavelength)

        pow1vals.append(power1_vals)
        pow1stds.append(power1_stdevs)
        pow2vals.append(power2_vals)
        pow2stds.append(power2_stdevs)
        xptics.append(xtics)
        corrs.append(np.divide(power1_vals, power2_vals))

    fig, ax1 = plt.subplots()

    # Plot power
    if energy:
        ax1.set_xlabel('Energy (eV)')
    else:
        ax1.set_xlabel('Wavelength (nm)')
    ax1.set_ylabel('Power 1 (microW)', color='orange')
    ax1.errorbar(xptics[1], pow1vals[1], yerr=pow1stds[1], fmt = '-o', linestyle = 'none', color='orange')
    ax1.tick_params(axis='y', labelcolor='orange')

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    # Plot single photon counts
    ax2.set_ylabel('Power 2 (microW)', color='red')  # we already handled the x-label with ax1
    ax2.errorbar(xptics[1], pow2vals[1], yerr=pow2stds[1], fmt = '-o', linestyle = 'none', color='red')
    ax2.tick_params(axis='y', labelcolor='red')

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.title('2 Powers by Wavelength')
    plt.show()

    popt, pcov = curve_fit(sin, xptics[0], corrs[0], p0=[0.07, 0.58, 0, 0.0061])
    poptT, pcovT = curve_fit(sinTdef, xptics[0], corrs[0], p0=[0.07, 0.58, 0])
    poptT2, pcovT2 = curve_fit(sinTdef, xptics[1], corrs[1], p0=[0.07, 0.58, 0])

    print(popt)

    xx = np.linspace(min_wl, max_wl, 1000)

    plt.plot(xx, sin(xx, *popt), color='green')
    plt.plot(xx, sinTdef(xx, *poptT), color='red')
    plt.plot(xx, sinTdef(xx, *poptT2), color='blue')

    plt.plot(xptics[0], corrs[0], marker='o', linestyle = 'none', color='green')
    plt.plot(xptics[1], corrs[1], marker='o', linestyle='none', color='yellow')
    plt.title('Power1 / Power2 by Wavelength')
    plt.ylabel('Power1 / Power2')
    plt.ylim(0,1)
    if energy:
        plt.xlabel('Energy (eV)')
    else:
        plt.xlabel('Wavelength (nm)')
    plt.show()

    plot_fft(corrs[0], 0.001)

plot_power_spc(0,100,737.55,737.9, energy=False)
#plot_corrected(0,100, energy=True)