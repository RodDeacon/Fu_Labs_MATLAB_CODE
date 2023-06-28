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
# filename = "Smp~TD300um_Lsr~Matisse-WV-30p0u_Col~Flt~TESx2-PnH~Out_Tmp~6p88_MgF~0_Msc~ExciteV"

# 11/29/2021 Measurements
# Start at 1.3-1.4 uW. Keep power between about 1uW and 2uW... just not like a factor
# of 2. Check power every once in a while.
# Power changes pretty slowly - oscillating between ~1.2, ~1.6. Gets lower near the edge of the BiFi.
# Can do small adjustments during measurements, just not while it says "acquiring".
# Have to copy over sif spectra to

# ple.start_stationary_ple_scan(filename,
#                               folder, 737.560, 737.590, 0.002, ['powermeter_B', 'spcm'],
#                               total_acq_time=10, counter_start=193)  # , wavemeter_type='WA1600')

# ple.start_stationary_ple_scan('Msc~trialWA1600_Lsr~Matisse-WV-15nW',
#                               'WA1600', 738.7512, 738.7762, 0.005, ['powermeter_AB'],
#                               total_acq_time=10, counter_start=1, wavemeter_type='WA1600')

# folder = "D:\\Dropbox Folder\\Dropbox\\35share\\data\\2022\\02_ZnO_Transmission_OD_CPT\\2022_03_10_Polarization\\044_0T_PLE_Ga\\"
#
# filename =  'Smp~TD300um_Lsr~Matisse-WV-100n_ExC~Plr~V_Col~Flt~PLBP-PnH~Out_Tmp~7p80_MgF~0_Msc~Transmission-SPCM'
#
"""
HERE!!!!!!!!!!!!!!!!!!!!!
"""
# folder = r"D:\Dropbox Folder\Dropbox\35share\data\2022\02_ZnO_Transmission_OD_CPT\2022_04_13_PLE_5T_1p82K\002_Smp~TD300um_Lsr~Matisse-WV-900u_Tmp~1p8_MgF~5_MsT~PLE_Msc~ExciteH"
# filename = 'Smp~TD300um_Lsr~Matisse-WV-900u_Exc~Flt~PL_Col~Flt~TESx2-PnH~In_Tmp~1p82_MgF~5'
#
# ple.start_stationary_ple_scan(filename,
#                               folder, 737.710, 737.740, 0.002, ['powermeter_B', 'spcm'],
#                               total_acq_time=10, counter_start=175)  # , wavemeter_type='WA1600')
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

""" HERE """
# folder = r'D:\Dropbox Folder\Dropbox\35share\data\2022\05_ZnO_InImplantation_Magnet\ContinuousAndorTrial'
# ple.start_continuous_ple_scan('034_Smp~TD300um_Lsr~Matisse-737p684-28u_Ls2~Toptica-368p79204-502u_Exc~WP2~259_Col~Flt~TESx2-PnH~In_Tmp~1p85_MgF~5-ScanSpeed0p001',
# # ple.start_continuous_ple_scan(filename,
#                               folder, 738.548, 738.555, ['powermeter_B', 'spcm'], matisse_scanning_speed=0.001,
#                               wavemeter_type='WA1600')


folder = r'D:\Dropbox Folder\Dropbox\35share\data\2022\10_TD300u_0T_SHB\2022_11_09'

start = 737.600
end = 737.680
# start = 737.850
# end = 737.790
scanning_speed = 0.001

start_str = str(start).replace('.', 'p') + 'n'
end_str = str(end).replace('.', 'p') + 'n'
scanning_speed_str = str(scanning_speed).replace('.', 'p')

filename = f'042_Smp~TD300u_Lsr~Matisse-sweep{start_str}to{end_str}step1n-160u_Col~Flt~TESx3-PnH~In_Exc~Flt~PL_Tmp~1p95_MgF~0_Msc~ScanSpeed~{scanning_speed_str}-Spot6'
# filename = f'014_Smp~TD300u_Lsr~Matisse-sweep{start_str}to{end_str}step1n-125n_Ls2~Toptica-368p82412n-0u_Col~Flt~TESx3-PnH~In_Exc~Flt~PL_Tmp~1p95_MgF~0_Msc~ScanSpeed~{scanning_speed_str}-Spot6'
ple.start_continuous_ple_scan(filename, folder,
                              start, end,
                              ['powermeter_B', 'spcm'],
                              matisse_scanning_speed=scanning_speed,
                              wavemeter_type='WA1600')

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

# filename = 'Smp~ZnOInImpl_Lsr~Matisse-WV-400n_Col~Flt~TESx2_Tmp~11p15_MgF~0'
# filename = 'Smp~ZnOInImpl_Lsr~Matisse-WV-1000n_Ls2~Toptica-369p217-3500n_Col~Flt~TESx2_EnC~WP2~154-WP4~290_Tmp~1p96_MgF~7'
# folder = r'D:\Dropbox Folder\Dropbox\35share\data\2022\05_ZnO_InImplantation_Magnet\ContinuousAndorTrial'
#

# ple.start_stationary_ple_scan(filename,
#                               folder, 738.540, 738.548, 0.002, ['powermeter_B', 'andor'],
#                               total_acq_time=2, counter_start=1)
# ple.start_stationary_ple_scan(filename,
#                               folder, 738.430, 738.500, 0.002, ['powermeter_B', 'andor'],
#                               total_acq_time=10, counter_start=32)
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
