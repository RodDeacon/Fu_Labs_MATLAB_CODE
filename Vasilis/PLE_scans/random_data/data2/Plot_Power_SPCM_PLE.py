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


def wavelength_to_energy(wavelength, mat=True):

    if mat:
        return 2 * 1239.8 / wavelength
    else:
        return 1239.8 / wavelength
'''
def spcm_avg(filenum):



def power_avg(filenum):

def spcm_stdev(filenum):

def power_stdev(filenum):

'''

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

    files = fnm([i for i in range(1, 100)], ['qdlf'])

    for filename in files.filenames:

        file = QDLFDataManager.load(filename)

        wavelength = fnm._get_file_info(filename)['Lsr: Wavelength (nm)']
        if filename.find("spcm") != -1:

            if energy:
                xstics.append(wavelength_to_energy(wavelength))
            else:
                xstics.append(wavelength)

            spc_vals.append(np.array(file.data['y1']).mean())
            spc_stdevs.append(np.array(file.data['y1']).std())
        elif filename.find("power") != -1:

            if energy:
                xptics.append(wavelength_to_energy(wavelength))
            else:
                xptics.append(wavelength)

            power_vals.append(np.array(file.data['y1']).mean())
            power_stdevs.append(np.array(file.data['y1']).std())

    fig, ax1 = plt.subplots()

    # Plot power
    if energy:
        ax1.set_xlabel('Energy (eV)')
    else:
        ax1.set_xlabel('Wavelength (nm)')
    ax1.set_ylabel('Power (microW)', color='red')
    ax1.errorbar(xptics, power_vals, yerr=power_stdevs, fmt = '-o', linestyle = 'none', color='red')
    ax1.tick_params(axis='y', labelcolor='red')

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    # Plot single photon counts
    ax2.set_ylabel('SPCM counts', color='blue')  # we already handled the x-label with ax1
    ax2.errorbar(xstics, spc_vals, yerr=spc_stdevs, fmt = '-o', linestyle = 'none', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.title('SPCM and Power by Wavelength')
    plt.show()

    c_vals = np.divide(spc_vals, power_vals)

    plt.plot(xstics, c_vals)
    plt.show()

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

plot_power_spc(0,100, energy=False)
#plot_corrected(0,100, energy=True)