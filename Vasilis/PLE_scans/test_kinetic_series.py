from matisse_controller.shamrock_ple import ACQ_MODE_FAST_KINETICS, READ_MODE_FVB, COSMIC_RAY_FILTER_ON
from matisse_controller.shamrock_ple.ccd import CCD
from matisse_controller.shamrock_ple.spectrograph import Spectrograph

ccd = CCD()
spectrograph = Spectrograph()

ccd.setup(1, acquisition_mode=ACQ_MODE_FAST_KINETICS, readout_mode=READ_MODE_FVB, temperature=-60, cool_down=True, number_accumulations=2, cosmic_ray_filter=COSMIC_RAY_FILTER_ON)




if isinstance(ccd, CCD):
    ccd.shutdown()

if isinstance(spectrograph, Spectrograph):
    spectrograph.shutdown()

