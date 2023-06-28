from ctypes import c_int, c_float, create_string_buffer, pointer
from bidict import bidict

from matisse_controller.shamrock_ple.utils import load_lib


class Spectrograph:
    LIBRARY_NAME = 'atspectrograph.dll'
    DEVICE_ID = c_int(0)

    # Below constants are calculated using a pre-calibrated wavelength axis on SOLIS (end - start) / 1024
    GRATINGS_NM_PER_PIXEL = {
        300: 0.116523437,
        1200: 0.0273535156,
        1799: 0.01578125
    }

    # The offset to add, in nanometers, to data in a spectrum taken with a given grating.
    # These tend to change over time, so update accordingly. Offset is abs(pixel shift) * (nm per pixel)
    GRATINGS_OFFSET_NM = {
        300: 1.325,  # -11.4 px, last calibrated Aug 2019
        1200: 0.109,  # -4 px, last calibrated Apr 2015
        1799: 0.470  # -29.8 px, last calibrated Dec 2018
    }

    def __init__(self, initialize_on_definition=True):

        self.lib = load_lib(Spectrograph.LIBRARY_NAME)

        self.gratings = bidict()
        self.calibration_coefficients = [0., 1., 0., 0.]  # default for pixels

        if initialize_on_definition:
            self.initialize()

    def __del__(self):
        self.shutdown()

    def initialize(self):
        try:
            self.lib.ATSpectrographInitialize()

            num_devices = c_int()
            self.lib.ATSpectrographGetNumberDevices(pointer(num_devices))
            assert num_devices.value > 0, 'No spectrometer found.'

            self.setup_grating_info()

            self.calibration_coefficients = self.get_calibration_values()

        except OSError as err:
            raise RuntimeError('Unable to initialize Andor Shamrock API.') from err

    def setup_grating_info(self):
        """
        Fill out the bidirectional dictionary responsible for holding information about spectrometer gratings.
        """
        number = c_int()
        self.lib.ATSpectrographGetNumberGratings(Spectrograph.DEVICE_ID, pointer(number))
        blaze_str_len = 8
        blaze = create_string_buffer(blaze_str_len)
        for index in range(1, number.value + 1):
            lines, home, offset = c_float(), c_int(), c_int()
            self.lib.ATSpectrographGetGratingInfo(Spectrograph.DEVICE_ID, c_int(index), pointer(lines), blaze,
                                                  c_int(blaze_str_len), pointer(home), pointer(offset))
            self.gratings[round(lines.value)] = index

    def get_grating_grooves(self) -> int:
        """
        Returns
        -------
        int
            the number of grooves in the current spectrometer grating
        """
        index = c_int()
        self.lib.ATSpectrographGetGrating(Spectrograph.DEVICE_ID, pointer(index))
        return self.gratings.inverse[index.value]

    def set_grating_grooves(self, num_grooves: int):
        """
        Use the spectrometer grating with the specified number of grooves.

        Parameters
        ----------
        num_grooves
            the desired number of grooves
        """
        if num_grooves != self.get_grating_grooves():
            self.lib.ATSpectrographGetGrating(Spectrograph.DEVICE_ID, c_int(self.gratings[num_grooves]))

    def get_center_wavelength(self) -> float:
        """
        Returns
        -------
        float
            the current center wavelength of the spectrometer
        """
        wavelength = c_float()
        self.lib.ATSpectrographGetWavelength(Spectrograph.DEVICE_ID, pointer(wavelength))
        return wavelength.value

    def set_center_wavelength(self, wavelength: float):
        """
        Set the spectrometer wavelength at the specified value.

        Parameters
        ----------
        wavelength
            the desired center wavelength to set
        """
        if wavelength != self.get_center_wavelength():
            self.lib.ATSpectrographSetWavelength(Spectrograph.DEVICE_ID, c_float(wavelength))

    def get_calibration_values(self, detector_pixel_width: float = 26., detector_pixel_number: int = 1024):
        """
        Get the spectrometer pixel calibration coefficients λ = coeff0 + coeff1 * x + coeff1 * x ^ 2 + coeff1 * x ^ 3

        Parameters
        ---------
        detector_pixel_width: float
            the pixel width of the detector in μm
        detector_pixel_number: float
            the number of total pixels on the axis the pixels represent different wavelengths
        Returns
        -------
        list
            A list of 4 elements with the 4 coefficients of the calibration.
        """
        self.lib.ATSpectrographSetPixelWidth(Spectrograph.DEVICE_ID, c_float(detector_pixel_width))
        self.lib.ATSpectrographSetNumberPixels(Spectrograph.DEVICE_ID, c_int(detector_pixel_number))

        coeff0, coeff1, coeff2, coeff3 = c_float(), c_float(), c_float(), c_float()
        self.lib.ATSpectrographGetPixelCalibrationCoefficients(Spectrograph.DEVICE_ID, pointer(coeff0), pointer(coeff1),
                                                               pointer(coeff2), pointer(coeff3))

        return [coeff0.value, coeff1.value, coeff2.value, coeff3.value]

    def shutdown(self):
        """Run Shamrock-related cleanup and shutdown procedures."""
        self.lib.ATSpectrographClose()
