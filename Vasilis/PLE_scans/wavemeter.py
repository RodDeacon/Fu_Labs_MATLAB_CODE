import threading
import warnings

import pyvisa
from serial import Serial, SerialException
from functions26.InstrumentHandler import GPIBInstrument


class WaveMeter:
    """An interface to serial port communication with the Coherent WaveMaster wavemeter."""

    wavemeter_lock = threading.Lock()

    def __init__(self, *args, **kwargs):
        self.initialize(*args, **kwargs)

    def initialize(self, *args, **kwargs):
        warnings.warn('Set your own "initialize" class method.')

    def __del__(self):
        warnings.warn('Set your own "delete" class method.')

    def query(self, command: str) -> str:
        """
        Wait to acquire an exclusive lock on the serial port, then send a command to the wavemeter.

        Parameters
        ----------
        command : str
            the command to send to the wavemeter

        Returns
        -------
        str
            the response from the wavemeter to the given command
        """
        warnings.warn('Set your own "query" class method.')
        return ''

    def get_raw_value(self) -> str:
        """
        Returns
        -------
        str
            the raw output from the wavemeter display
        """
        warnings.warn('Set your own "get_raw_value" class method.')
        return ''

    def get_wavelength(self) -> float:
        """
        Returns
        -------
        float
            a measurement from the wavemeter

        Notes
        -----
        Blocks the calling thread until a number is received.
        """
        warnings.warn('Set your own "get_wavelength" class method.')
        return -1.


class WaveMaster(WaveMeter):
    """An interface to serial port communication with the Coherent WaveMaster wavemeter."""

    wavemeter_lock = threading.Lock()

    def initialize(self, port: str):
        try:
            self.serial = Serial(port)
            self.serial.timeout = 10.0
            self.serial.write_timeout = 10.0
        except SerialException as err:
            raise IOError("Couldn't open connection to wavemeter.") from err

    def __del__(self):
        self.serial.close()

    def query(self, command: str) -> str:
        """
        Wait to acquire an exclusive lock on the serial port, then send a command to the wavemeter.

        Parameters
        ----------
        command : str
            the command to send to the wavemeter

        Returns
        -------
        str
            the response from the wavemeter to the given command
        """
        with WaveMaster.wavemeter_lock:
            try:
                if not self.serial.is_open:
                    self.serial.open()
                # Ensure a newline is at the end
                command = command.strip() + '\n\n'
                self.serial.write(command.encode())
                self.serial.flush()
                return self.serial.readline().strip().decode()
            except SerialException as err:
                raise IOError("Error communicating with wavemeter serial port.") from err

    def get_raw_value(self) -> str:
        """
        Returns
        -------
        str
            the raw output from the wavemeter display
        """
        return self.query('VAL?').split(',')[1].strip()

    def get_wavelength(self) -> float:
        """
        Returns
        -------
        float
            a measurement from the wavemeter

        Notes
        -----
        Blocks the calling thread until a number is received.
        """
        raw_value = self.get_raw_value()
        # Keep trying until we get a number
        while raw_value == 'NO SIGNAL' or raw_value == 'MULTI-LINE':
            raw_value = self.get_raw_value()
        return float(raw_value)


class WA1600(WaveMeter):

    def initialize(self, *args, **kwargs):
        self.device = GPIBInstrument('GPIB0::18::INSTR', '\n', ':READ:WAV?')

    def __del__(self):
        self.device.terminate_instrument()

    def query(self, command: str) -> str:
        """
        Wait to acquire an exclusive lock on the serial port, then send a command to the wavemeter.

        Parameters
        ----------
        command : str
            the command to send to the wavemeter

        Returns
        -------
        str
            the response from the wavemeter to the given command
        """
        with WA1600.wavemeter_lock:

            try:
                self.device.instrument.last_status
            except (pyvisa.errors.InvalidSession, AttributeError):
                self.device.initialize_instrument()

            return self.device.get_instrument_reading_string(command)

    def get_raw_value(self) -> str:
        return self.device.get_instrument_reading_string()

    def get_wavelength(self) -> float:
        raw_value = self.get_raw_value()
        # Keep trying until we get a number
        while raw_value.startswith('0'):
            raw_value = self.get_raw_value()
        return float(raw_value)

