import json
from typing import Dict, List, Union

acquisition_settings_dictionary = {
    "General": {
        "Acquisition Type": {
            "Stationary": True,
            "Continuous": False
        },
        "Stationary": {
            "File Options": {
                "Folder Name": ".",
                "Filename Template": "Lsr~Matisse-WV-1n_Msc~StationaryScan",
                "Saved File Extension": "qdlf",
                "Filename No. Start": 1
            },
            "Scan Options": {
                "Initial Wavelength (nm)": 737.770,
                "Final Wavelength (nm)": 737.840,
                "Scan Step (nm)": 0.002,
                "Acquisition Time (s)": 10.0,
                "Scanning speed": 0.005
            },
            "Active Measuring Devices": {
                "andor": False,
                # "andor_old": False,
                "powermeter_A": False,
                "powermeter_B": True,
                "spcm": True,
                "wa1600": False
            }
        },
        "Continuous": {
            "File Options": {
                "Folder Name": ".",
                "Filename": "continuous_scan",
                "Saved File Extension": "mqdlf"
            },
            "Scan Options": {
                "Initial Wavelength (nm)": 737.770,
                "Final Wavelength (nm)": 737.840,
                "Scanning speed": 0.0002,
                "Total Acquisitions": 1
            },
            "Active Measuring Devices": {
                "powermeter_A": False,
                "powermeter_B": True,
                "spcm": True,
                "wa1600": False
            }
        }
    },
    "Laser": {
        "Device": {
            "Device Port": "TBD",
        },
        "Coupled Wavemeter": {
            "Wavemeter Name": "WaveMaster",
            "Wavemeter Port": "COM5"
        },
    },
    "SPCM": {
        "Device": {
            "Device Port": "dev1/ctr1",
            "Sampling Time (s)": 0.05,
        },
    },
    "Powermeter": {
        "Device": {
            "Device Port": "GPIB0::5::INSTR",
            "Sampling Time (s)": 0.05,
        },
    },
    "WA1600": {
        "Device": {
            "Device Port": "GPIB0::18::INSTR",
            "Sampling Time (s)": 0.05,
        },
    },
    "Andor": {
        "Spectrograph": {
            "Center Wavelength (nm)": 740.0,
            "Grating Grooves": 3,
            "Use Pre-existing": True,
        },
        "CCD": {
            "Acquisition Mode": "Single",
            "Readout Mode": "FVB",
            "Temperature (C)": -67.0,
            "Wait for Temperature": True,
            "Accumulation Number": 1,
            "Cosmic Ray Filter": True,
            "Use Pre-existing": True,
        }
    }
}

acquisition_settings_laser_wavemeter_name_options = ['WaveMaster', 'WA1600']


def add_extension_if_necessary(filename, extension):
    if extension[0] != '.':
        extension = '.' + extension
    # finding if filename has ending same as extension and if not, it adds the extension ending to the file
    filename_ending = filename.split('.')[-1]
    if filename_ending != extension[1:]:
        filename = filename + extension

    return filename


def get_acquisition_settings_dictionary_from_json(filename: str) -> Dict:
    with open(filename, 'r') as file:
        dictionary: dict = json.load(file)

    return dictionary


def export_acquisition_settings_dictionary_to_json(dictionary: Dict, filename: str):
    filename = add_extension_if_necessary(filename, 'json')
    with open(filename, "w") as outfile:
        outfile.write(json.dumps(dictionary, indent=4))


def get_acquisition_setting(setting_string: str,
                            target_dictionary=None) -> Union[Dict, List, int, float, bool, str, None]:
    """Takes a setting string separated with '/' and returns the acquisition setting value in the given target
    dictionary. If the target dictionary is not provided, then the default settings are used."""
    if target_dictionary is None:
        target_dictionary = acquisition_settings_dictionary

    try:
        keys = setting_string.split('/')
        value = target_dictionary
        for key in keys:
            value = value[key]
        return value
    except KeyError:
        return None


def get_acquisition_setting_from_json(setting_string: str,
                                      filename: str) -> Union[Dict, List, int, float, bool, str, None]:
    """Takes a setting string separated with '/' and returns the default acquisition setting value"""
    try:
        keys = setting_string.split('/')
        value = get_acquisition_settings_dictionary_from_json(filename)
        for key in keys:
            value = value[key]
        return value
    except KeyError:
        return None
