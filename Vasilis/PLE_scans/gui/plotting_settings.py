import json
from typing import Dict, List, Union


plotting_settings_dictionary = {
    "Data Options": {
        "Stationary Datasets": {
            "X-axis": "TBD",
            "Y-axis": "TBD"
        },
        "Continuous Datasets": {
            "X-axis": "TBD",
            "Y-axis": "TBD"
        },
        "Line Options": {
            "Show": True,
            "Type": "TBD",
            "Size": 12,
            "Color (RGBA)": [255, 140, 0, 255],
        },
        "Symbol Options": {
            "Show": True,
            "Type": "TBD",
            "Size": 12,
            "Color (RGBA)": [0, 140, 255, 120],
        },
    },
    "Axes": {
        "Active Axes": {
            "Left": True,
            "Bottom": True,
            "Right": True,
            "Top": True,
        },
        "Style": {
            "Type": "TBD",
            "Size": 12,
            "Color (RGBA)": [255, 140, 0, 255],
        },
    },
    "Labels": {
        "Active Labels": {
            "Left": True,
            "Right": True,
        },
        "Style": {
            "Show": True,
            "Type": "TBD",
            "Size": 12,
            "Color (RGBA)": [255, 140, 0, 255],
        },
    },
    "Grids": {
        "Active Grids": {
            "Horizontal": True,
            "Vertical": True,
        },
        "Style": {
            "Type": "TBD",
            "Size": 12,
            "Color (RGBA)": [255, 140, 0, 255],
        },
    },
}


def add_extension_if_necessary(filename, extension):
    if extension[0] != '.':
        extension = '.' + extension
    # finding if filename has ending same as extension and if not, it adds the extension ending to the file
    filename_ending = filename.split('.')[-1]
    if filename_ending != extension[1:]:
        filename = filename + extension

    return filename


def get_plotting_settings_dictionary_from_json(filename: str) -> Dict:
    with open(filename, 'r') as file:
        dictionary: dict = json.load(file)

    return dictionary


def export_plotting_settings_dictionary_to_json(dictionary: Dict, filename: str):
    filename = add_extension_if_necessary(filename, 'json')
    with open(filename, "w") as outfile:
        outfile.write(json.dumps(dictionary, indent=4))


def get_plotting_setting(setting_string: str,
                         target_dictionary=None) -> Union[Dict, List, int, float, bool, str, None]:
    """Takes a setting string separated with '/' and returns the plotting setting value in the given target
    dictionary. If the target dictionary is not provided, then the default settings are used."""
    if target_dictionary is None:
        target_dictionary = plotting_settings_dictionary

    try:
        keys = setting_string.split('/')
        value = target_dictionary
        for key in keys:
            value = value[key]
        return value
    except KeyError:
        return None


def get_plotting_setting_from_json(setting_string: str,
                                   filename: str) -> Union[Dict, List, int, float, bool, str, None]:
    """Takes a setting string separated with '/' and returns the default plotting setting value"""
    try:
        keys = setting_string.split('/')
        value = get_plotting_settings_dictionary_from_json(filename)
        for key in keys:
            value = value[key]
        return value
    except KeyError:
        return None
