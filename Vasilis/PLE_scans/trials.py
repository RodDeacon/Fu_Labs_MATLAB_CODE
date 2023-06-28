import time
import threading

from ple import PLE
from functions26.useful_functions import send_email


def notify_user(message, email_details_file_path, recipients='', subject='PLE Scan'):
    # get mailing info
    file = open(email_details_file_path, 'r')
    email_details = file.read().splitlines()
    file.close()

    if isinstance(recipients, str):
        recipients = [recipients]

    return send_email(sender_id=email_details[0], sender_password=email_details[1], recipients=recipients,
                      message=message, subject=subject)


ple = PLE()
# ple.start_stationary_ple_scan('scan_example', '.', 737.674, 737.678, 0.002, ['powermeter', 'spcm'],
#                               total_acq_time=1)
# folder = "D:\\Dropbox Folder\\Dropbox\\35share\\data\\2021\\2021_08_TempDep\\2021_09_07\\002_PLE_0T_1p9K_350n\\"
# folder = "D:\\Dropbox Folder\\Dropbox\\35share\\data\\2021\\2021_08_CPT\\2021_09_21_PLE_0T_In\\PLE_1p72K_200nW\\"
# folder = "D:\\Dropbox Folder\\Dropbox\\35share\\data\\2021\\2021_08_TempDep\\2021_10_07_Indium\\016_16p37 K\\"
# Ls2~Top-368p8630-0p067u
# filename = 'Smp~TD300um_Lsr~Matisse-WV-0p5u_Col~Flt~TESx2-PnH~In_Tmp~16p37_MgF~0_Msc~Spot4'

# folder = "D:\\Dropbox Folder\\Dropbox\\35share\\data\\2021\\2021_11_TempFollowUp\\12_12_2021\\002_20p1K_In\\"
# filename = 'Smp~TD300um_Lsr~Matisse-WV-2uW_Col~Flt~TESx2-PnH~In_Tmp~17p4_MgF~0_Msc~None'

# folder = "D:\\Dropbox Folder\\Dropbox\\35share\\data\\2022\\2022_Beamsplitter\\001_Trials\\"
# filename = 'Smp~TD300um_Lsr~Matisse-WV-2uW_ExC~WP2~055-WP4~020_Col~Flt~TESx2-PnH~Out_Tmp~4p3_MgF~5_Msc~TwoPower'

# folder = "D:\\Dropbox Folder\\Dropbox\\35share\\data\\2022\\01_ZnO_SnLiIsotope" \
#          "\\2_25_PLE\\005_In_PLE_Sn008Diffuse"

         # "001_Smp~TD300um_Col~Flt~ND0p3nNDXnPLFilter-PnH~Out_Tmp~6p76_MgF~6_MsT~Transmission_Msc~SPCM"
         # "002_Smp~TD300um_Col~Flt~PLFilter-PnH~Out_Tmp~6p76_MgF~6_MsT~Transmission_Msc~SPCM"
# filename = 'Smp~TD300um_Lsr~Matisse-WV-8uW_Col~Flt~ND0p3nNDXnPLFilter-PnH~Out_Tmp~6p76_MgF~6_Msc~PowerMeter'
# filename = 'Smp~TD300um_Lsr~Matisse-WV-15nW_Col~Flt~PLFilter-PnH~Out_Tmp~6p76_MgF~6_Msc~SPCM'
# filename = 'Smp~TD300um_Lsr~Matisse-WV-8uW_Col~Flt~PLTES-PnH~Out_Tmp~7p4_MgF~0_Msc~Spectrometer'

# folder = "D:\\Dropbox Folder\\Dropbox\\35share\\data\\2022\\02_ZnO_Transmission_OD_CPT\\" \
#          "2022_03_14_PLE_test_6p88K_0T\\" \
#          "001_Smp~TD300um_Col~Flt~TESx2-PnH~Out_Tmp~6p88_MgF~0_MsT~PLE"
#

# folder = "D:\\Dropbox Folder\\Dropbox\\ZnO_temp\\Samples\\TDmiscBox\\TD300uTransmission\\Spectra\\009_PLE_FixedPowerMeter"
# folder = "D:\\Dropbox Folder\\Dropbox\\ZnO_temp\\Samples\\Oslo_Samples\\HT_TD_Oslo_HiLi_03\\Spectra\\003_PLE"

# 11/29/2021 Measurements
# Start at 1.3-1.4 uW. Keep power between about 1uW and 2uW... just not like a factor
# of 2. Check power every once in a while.
# Power changes pretty slowly - oscillating between ~1.2, ~1.6. Gets lower near the edge of the BiFi.
# Can do small adjustments during measurements, just not while it says "acquiring".
# Have to copy over sif spectra to

# ple.start_stationary_ple_scan(filename,
#                               folder, 737.683, 737.753, 0.003, ['powermeter_B', 'andor'],
#                               total_acq_time=4, counter_start=51)  # , wavemeter_type='WA1600')

# ple.start_stationary_ple_scan('Msc~trialWA1600_Lsr~Matisse-WV-15nW',
#                               'WA1600', 738.7512, 738.7762, 0.005, ['powermeter_AB'],
#                               total_acq_time=10, counter_start=1, wavemeter_type='WA1600')

# folder = r'D:\Dropbox Folder\Dropbox\35share\data\2022\10_TD300u_0T_SHB\2022_11_07\027_Lsr~Matisse-scan737p795nto748p850nstep0p5p-2p07m_Ls2~Toptica-368p91107n-0u_Col~Flt~TESx2-PnH~In_Exc~Flt~PL_Tmp~1p7_MgF~0_MsT~PLE'
# ple.start_stationary_ple_scan('Lsr~Matisse-WV-2p07m_Ls2~Toptica-368p91107n-0u_Col~Flt~TESx2-PnH~In_Exc~Flt~PL_Tmp~1p7_MgF~0',
#                               folder, 737.795, 737.850, 0.001, ['powermeter_B', 'andor'],
#                               total_acq_time=0.05, counter_start=1, wavemeter_type='WA1600')

# folder = "D:\\Dropbox Folder\\Dropbox\\35share\\data\\2022\\02_ZnO_Transmission_OD_CPT\\2022_03_10_Polarization\\044_0T_PLE_Ga\\"
#
# filename =  'Smp~TD300um_Lsr~Matisse-WV-100n_ExC~Plr~V_Col~Flt~PLBP-PnH~Out_Tmp~7p80_MgF~0_Msc~Transmission-SPCM'
#
"""
HERE!!!!!!!!!!!!!!!!!!!!!
"""
# folder = r"D:\Dropbox Folder\Dropbox\35share\data\2022\05_ZnO_InImplantation_Magnet\07_08_CPT_Prep\001_1Laser_PLE_HE_7K"
# filename = 'Smp~ZnOInImpl_Lsr~Matisse-WV-5u_Col~Flt~TESx2_Tmp~7p0_MgF~7_Msc~Spot4'
#
# ple.start_stationary_ple_scan(filename,
#                               folder, 738.400, 738.470, 0.002, ['powermeter_B', 'andor'],
#                               total_acq_time=4, counter_start=1  , wavemeter_type='WA1600')
"""
HERE!!!!!!!!!!!!!!!!!!!!!
"""
# folder = "D:\\Dropbox Folder\\Dropbox\\35share\\data\\2021\\2021_11_EpiLayer_Backside\\2021_11_TempFollowUp\\11_21_2021\\004_12p2K_In\\"
# folder = "D:\\Dropbox Folder\\Dropbox\\35share\\data\\2021\\2021_08_CPT\\2021_09_24_6T_1p92K_CPT_2nd_peak_power_dependence_the good_one\\"
# ple.start_continuous_ple_scan('Smp~TD300um_Lsr~Matisse-WV-450n_Col~Flt~TESx2-PnH~In_Tmp~2p
# 086_MgF~0_Msc~Spot4-PMB-Continuous-NoFilter-2', folder,  737.625, 737.665,  ['powermeter_B', 'spcm'], matisse_scanning_speed=0.0015)

# ple.start_continuous_ple_scan('Smp~TD300um_Lsr~Matisse-WV-2u_Ls2~Top-368p8638-6u_Col~Flt~TESx2-PnH~In_EnC~WP2~015_Tmp~1p88_MgF~6_Msc~Spot4-FilterInCollection5p6To1p1-LE-fine', folder,  737.712, 737.720
# ,  ['powermeter_B', 'spcm'], matisse_scanning_speed=0.00005)

# folder = "D:\\Dropbox Folder\\Dropbox\\35share\\data\\2022\\02_ZnO_Transmission_OD_CPT\\" \
#          "2022_02_27_Transmission_test_6p76K_6T_two_lasers"
# folder = "D:\\Dropbox Folder\\Dropbox\\35share\\data\\2022\\02_ZnO_Transmission_OD_CPT\\" \
#          "2022_03_06_Transmission_1p7K_6T_Ga_two_lasers\\"
#
# filename = "Smp~TD300um_Lsr~Matisse-WV-1p75u_Ls2~toptica-368p88134-1p66u_Exc~WP2~057_Col~Flt~PLFilter-PnH~Out-Plr~132_Tmp~1p84_MgF~6"
#
# """ CPT HERE """
# folder = r'D:\Dropbox Folder\Dropbox\35share\data\2022\05_ZnO_InImplantation_Magnet\07_09_CPT'
# # # # ple.start_continuous_ple_scan('034_Smp~TD300um_Lsr~Matisse-737p684-28u_Ls2~Toptica-368p79204-502u_Exc~WP2~259_Col~Flt~TESx2-PnH~In_Tmp~1p85_MgF~5-ScanSpeed0p001',
# ple.start_continuous_ple_scan('022_Smp~ZnOInImpl_Lsr~Matisse-WV-1p0u_Ls2~Toptica-369p21775-0p76u_Col~Flt~TESx2_EnC~WP2~233-WP4~310_Tmp~1p95_MgF~7_Msc~Spot4-ScanSpeed0p000001',
#                               folder, 738.6171, 738.6175, ['powermeter_B', 'spcm'], matisse_scanning_speed=0.000001,
#                               wavemeter_type='WA1600')
# """ HERE """
#
# """ Two-power Calibration"""
#
# filename = 'Smp~Sn008Diffused_Lsr~Matisse-WV-2u_Exc~Flt~Na~Flt~TES-PnH~Out_Tmp~5p7_MgF~0_Msc~PLE'
# folder = 'D:\\Dropbox Folder\\Dropbox\\35share\\data\\2022\\01_ZnO_SnLiIsotope\\4_23_PLE\\001_Sn008Diffused\\InPLE'

# """ Microwave Polarization Testing """
# filename = 'Smp~TD50umFMR3_Lsr~Matisse-WV-3n_Exc~Flt~Plr~H_Col~Flt~TES-PnH~Out_EnC~WP2~160-WP4~252_Tmp~8p6_MgF~3_Msc~Spot7_MsT~power_MsT~spcm'
# folder = r'D:\Dropbox Folder\Dropbox\35share\data\2022\04_pODMR_MW\5_09_Optical_Pumping_Polarization\Spot_7_3T_01'
#
# ple.start_stationary_ple_scan(filename,
#                               folder, 737.605, 737.675, 0.003, ['powermeter_B', 'andor'],
#                               total_acq_time=10, counter_start=1)  # , wavemeter_type='WA1600')

# notify_user('The scan is complete!', 'C:\\Users\\NV PC\\Desktop\\email_info.txt', '5039278970@tmomail.net')
#
# filename = 'Smp~SnImplantationN2Anneal_Lsr~Matisse-WV-20u_Col~Flt~TES_Tmp~5p7_MgF~0_Msc~e11Spot1TES'
# folder = r'D:\Dropbox Folder\Dropbox\35share\data\2022\08_Sn_Implantation\secondAnnealinN2\Spot1SnPLEfinescan'

# folder="D:\\Dropbox Folder\\Dropbox\\35share\\data\\2023\\05_twoInimplant\\SnPLEe82400gPLfocus"
# filename = "Smp~2ndInImplant-e8_Lsr~Matisse-WV-6u_Col~Flt~TESTES-PnH~Out_Tmp~5p15_MgF~0_Msc~SnTESon2400gcenter379nm"

#Sn ????
# ple.start_stationary_ple_scan(filename,
#                               folder, 739.395, 739.425, 0.002, ['powermeter_A', 'andor'],
#                               total_acq_time=10, counter_start=12)
# ple.start_stationary_ple_scan(filename,
#                               folder, 739.425, 739.475, 0.001, ['powermeter_A', 'andor'],
#                               total_acq_time=10, counter_start=29)
# ple.start_stationary_ple_scan(filename,
#                               folder, 739.475, 739.510, 0.002, ['powermeter_A', 'andor'],
#                               total_acq_time=160, counter_start=1)

# ple.start_stationary_ple_scan(filename,
#                               folder, 739.077, 739.158, 0.003, ['powermeter_B', 'andor'],
#                               total_acq_time=10, counter_start=42)

#
# filename = 'Smp~ZnOInImplpostSIMS_Lsr~Matisse-WV-1u_Col~Flt~TESTES_Tmp~7p35_MgF~0_Msc~e9center'
# folder = r'D:\Dropbox Folder\Dropbox\35share\data\2022\01_ZnO_InImplantation\12_aftersims\e9PLE'

folder="D:\\Dropbox Folder\\Dropbox\\35share\\data\\2023\\05_InsurfaceTES\\1stInPLEcontrolPinhole-again"
filename = "Smp~1stInImplant-control_Lsr~Matisse-WV-44u_Col~Flt~TESTES-PnH~In_Tmp~6p65_MgF~0_Msc~2400gcenter378nm"


#Indium main line

# ple.start_stationary_ple_scan(filename,
#                               folder, 738.478, 738.530, 0.002, ['powermeter_A', 'andor'],
#                               total_acq_time=10, counter_start=1)

# ple.start_stationary_ple_scan(filename,
#                               folder, 738.480, 738.530, 0.002, ['powermeter_A', 'andor'],
#                               total_acq_time=10, counter_start=1)

ple.start_stationary_ple_scan(filename,
                              folder, 738.530, 738.570, 0.002, ['powermeter_A', 'andor'],
                              total_acq_time=10, counter_start=29)

# ple.start_stationary_ple_scan(filename,
#                               folder, 738.508, 738.530, 0.002, ['powermeter_A', 'andor'],
#                               total_acq_time=10, counter_start=17)

# ple.start_stationary_ple_scan(filename,
#                               folder, 738.545, 738.560, 0.001, ['powermeter_A', 'andor'],
#                               total_acq_time=10, counter_start=48)

#### Al main line
# ple.start_stationary_ple_scan(filename,
#                               folder, 737.580, 737.655, 0.002, ['powermeter_B', 'andor'],
#                               total_acq_time=5, counter_start=1)

# ple.start_stationary_ple_scan(filename,
#                               folder, 737.655, 737.730, 0.001, ['powermeter_B', 'andor'],
#                               total_acq_time=5, counter_start=77)

# ple.start_stationary_ple_scan(filename,
#                               folder, 737.730, 737.820, 0.002, ['powermeter_B', 'andor'],
#                               total_acq_time=5, counter_start=154)

# ple.start_stationary_ple_scan(filename,
#                               folder, 737.580, 737.630, 0.002, ['powermeter_B', 'andor'],
#                               total_acq_time=5, counter_start=1)

# ple.start_stationary_ple_scan(filename,
#                               folder, 737.805, 737.880, 0.005, ['powermeter_B', 'andor'],
#                               total_acq_time=5, counter_start=1)

# ple.start_stationary_ple_scan(filename,
#                               folder, 737.795, 737.820, 0.005, ['powermeter_B', 'andor'],
#                               total_acq_time=5, counter_start=59)


# ple.start_stationary_ple_scan(filename,
#                               folder, 737.695, 737.760, 0.005, ['powermeter_B', 'spcm'],
#                               total_acq_time=5, counter_start=100)

# ple.start_stationary_ple_scan(filename,
#                               folder, 737.755, 737.800, 0.005, ['powermeter_B', 'spcm'],
#                               total_acq_time=5, counter_start=58)

notify_user('The scan is complete!', 'C:\\Users\\NV PC\\Desktop\\email_info.txt', '5039278970@tmomail.net')
#### AL excited state
# ple.start_stationary_ple_scan(filename,
#                               folder, 737.300, 737.350, 0.005, ['powermeter_B', 'spcm'],
#                               total_acq_time=5, counter_start=1)

# ple.start_stationary_ple_scan(filename,
#                               folder, 737.353, 737.393, 0.001, ['powermeter_B', 'spcm'],
#                               total_acq_time=5, counter_start=13)

# ple.start_stationary_ple_scan(filename,
#                               folder, 737.398, 737.470, 0.005, ['powermeter_B', 'spcm'],
#                               total_acq_time=5, counter_start=55)

# ple.start_stationary_ple_scan(filename,
#                               folder, 737.435, 737.480, 0.005, ['powermeter_B', 'spcm'],
#                               total_acq_time=5, counter_start=41)

# ple.start_stationary_ple_scan(filename,
#                               folder, 737.400, 737.401, 0.005, ['powermeter_B', 'spcm'],
#                               total_acq_time=5, counter_start=30)


# ple.start_stationary_ple_scan(filename,
#                               folder, 738.500, 738.570, 0.002, ['powermeter_B', 'andor'],
#                               total_acq_time=10, counter_start=72)
# ple.start_stationary_ple_scan(filename,
#                               folder, 738.582, 738.640, 0.002, ['powermeter_B', 'andor'],
#                               total_acq_time=10, counter_start=116)
# ple.start_stationary_ple_scan(filename,
#                               folder, 738.640, 738.670, 0.002, ['powermeter_B', 'andor'],
#                               total_acq_time=10, counter_start=146)
# ple.start_stationary_ple_scan(filename,
#                               folder, 737.826, 737.860, 0.002, ['powermeter_B', 'spcm'],
#                               total_acq_time=10, counter_start=63, wavemeter_type='WA1600')
# ple.start_stationary_ple_scan(filename,
#                               folder, 737.862, 737.901, 0.003, ['powermeter_B', 'spcm'],
#                               total_acq_time=10, counter_start=81, wavemeter_type='WA1600')
# ple.start_stationary_ple_scan(filename,
#                               folder, 737.898, 737.920, 0.003, ['powermeter_B', 'spcm'],
#                               total_acq_time=10, counter_start=93, wavemeter_type='WA1600')


# ple.start_stationary_ple_scan(filename,
#                               folder, 737.800, 737.835, 0.001, ['powermeter_B', 'andor'],
#                               total_acq_time=0.1, counter_start=1, wavemeter_type='WA1600')


### Excited State
# ple.start_stationary_ple_scan(filename,
#                               folder, 738.023, 738.060, 0.003, ['powermeter_B', 'spcm'],
#                               total_acq_time=10, counter_start=1, wavemeter_type='WA1600')
# ple.start_stationary_ple_scan(filename,
#                               folder, 738.062, 738.100, 0.002, ['powermeter_B', 'spcm'],
#                               total_acq_time=10, counter_start=15, wavemeter_type='WA1600')
# ple.start_stationary_ple_scan(filename,
#                               folder, 738.102, 738.130, 0.003, ['powermeter_B', 'spcm'],
#                               total_acq_time=10, counter_start=36, wavemeter_type='WA1600')

#notify_user('The scan is complete!', 'C:\\Users\\NV PC\\Desktop\\email_info.txt', '2066371859@tmomail.net')
notify_user('The scan is complete!', 'C:\\Users\\NV PC\\Desktop\\email_info.txt', '2066367426@tmomail.net')
#
#
#

# print("This message will remain")
# print("\r")
# time.sleep(3)
# print('hello', end='\r')

from functions26.FilenameManager import FileNumberManager

# testing powermeter
# from powermeter import PowerMeter

# powermeter = PowerMeter('A')
# t0 = time.time()
# stop_event = threading.Event()
# start_event = threading.Event()
# powermeter.start_acquisition(t0, start_event, stop_event, 0.1)
# start_event.set()
# time.sleep(5)
# stop_event.set()
# powermeter.stop_and_save_acquisition('222.qdlf')
# print('done')


# testing spcm
# from spcm import SPCM
#
# spcm = SPCM()
# t0 = time.time()
# stop_event = threading.Event()
# start_event = threading.Event()
# spcm.start_acquisition(t0, start_event, stop_event, 0.1)
# start_event.set()
# time.sleep(5)
# stop_event.set()
# spcm.stop_and_save_acquisition('222.qdlf')
# print('done')


# testing spectrometer
# from matisse_controller.shamrock_ple.ccd import CCD
# from matisse_controller.shamrock_ple.shamrock import Shamrock
#
# shamrock = Shamrock()
# ccd = CCD()
