"""
Release Note:
========================================================
Version 1.0.1
2022-7-22 elton<elton.tian@myzygroup.com>
-1. Optimize test sequence
-2. update sdk about conoscope to v88
-3. Optimize algorithm parameters to fix WhiteDot Issue.

========================================================
Version 1.0.0
2022-6-14 elton<elton.tian@myzygroup.com>
-1. Init version for E-MOT
"""


##################################
# directories
#
# Where is the root directory.
# 'factory-test' directory, logs directories, etc will get placed in there.
# (use windows-style paths.)
ROOT_DIR = r'C:\oculus\factory_test_omi\factory_test_stations'
SEQUENCE_RELATIVEPATH = r'C:\oculus\factory_test_omi\factory_test_stations\test_station\test_equipment\algorithm'
# CONOSCOPE_DLL_PATH = r'C:\ORel\dist\test_equipment_57'
CONOSCOPE_DLL_PATH = r'C:\oculus\run\test_equipment'
CSV_SUMMARY_DIR = r'C:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\eureka_mot_summary'
# RAW_IMAGE_LOG_DIR = r'C:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\raw'
RAW_IMAGE_LOG_DIR = r'c:\ShareData\Oculus_RawData'
##################################
# serial number codes
#
SERIAL_NUMBER_VALIDATION = False  # set to False for debugging
SERIAL_NUMBER_MODEL_NUMBER = 'PR0'  # Peak panel SN

DATA_CLEAN_SCHEDULE = []  # [(6, 8)]
DATA_CLEAN_SAVED_MINUTES = 60 * 10
DATA_CLEAN_SAVED_MINUTES_PNG = 3600 * 24

##################################
# Fixture parameters
# Fixture commands
PROXY_COMMUNICATION_PATH = r"C:\vision\Release\vision.exe"
IS_PROXY_COMMUNICATION = True
PROXY_ENDPOINT = 8099
FIXTURE_COMPORT = "COM10" #
FIXTURE_PARTICLE_COMPORT = "COM1" #
FIXTURE_PARTICLE_ADDR = 1
DUT_COMPORT = "COM1" #
DUT_ETH_PROXY = True
DUT_ETH_PROXY_ADDR = ('192.168.21.132', 6000)

AUTO_CFG_COMPORTS = False
FIXTURE_PARTICLE_COMPORT_FILTER = 'VID:PID=0403:6001'

SW_VERSION_SUFFIX = 'G'
SPEC_VERSION = '0000'

COMMAND_DISP_HELP = "$c.help"
COMMAND_DISP_VERSION_GRP=['mcu', 'hw', 'fpga']
COMMAND_DISP_VERSION = "Version"
COMMAND_DISP_GETBOARDID = "getBoardID"
COMMAND_DISP_POWERON = "DUT.powerOn,DSCMODE"
# COMMAND_DISP_POWERON = "DUT.powerOn,SSD2832_BistMode"
#COMMAND_DISP_POWERON = "DUT.powerOn"
COMMAND_DISP_POWEROFF = "DUT.powerOff"
COMMAND_DISP_RESET = "Reset"
COMMAND_DISP_SETCOLOR = "SetColor"
COMMAND_DISP_SHOWIMAGE = "ShowImage"
COMMAND_DISP_READ = "MIPI.Read"
COMMAND_DISP_WRITE = "MIPI.Write"
COMMAND_DISP_2832WRITE = "t.2832_MIPI_WRITE"
COMMAND_DISP_VSYNC = "REFRESHRATE"
COMMAND_DISP_GET_COLOR = "GetColor"
COMMAND_MEASURE_BLU = "Measure,BLU"

COMMAND_NVM_WRITE_CNT = 'NVMWCNT'
COMMAND_NVM_READ = 'NVMRead'
COMMAND_NVM_WRITE = 'NVMWrite'
COMMAND_SPEED_MODE = 'SET.B7MODE'
COMMAND_GETB5ECC = 'Get.B5ECC'
COMMAND_GET_MODULE_INPLACE = 'GET.MODULE.INPLACE'

COMMAND_DISP_REBOOT_DLY = 4

DISP_CHECKER_ENABLE = False

# blue
# https://blog.csdn.net/a2009374138/article/details/52174856
DISP_CHECKER_L_HsvH = 220
DISP_CHECKER_H_HsvH = 250
DISP_CHECKER_L_HsvS = 0.8
DISP_CHECKER_H_HsvS = 1
DISP_CHECKER_COLOR = (0, 0, 255)
DISP_CHECKER_LOCATION = (25, 5)
DISP_CHECKER_COUNT = 2

COMMAND_HELP = 'CMD_HELP'
COMMAND_ID = 'CMD_ID'
COMMAND_VERSION = 'CMD_VERSION'
COMMAND_BUTTON_ENABLE = 'CMD_START_BUTTON_ENABLE'
COMMAND_BUTTON_DISABLE = 'CMD_START_BUTTON_DISABLE'
COMMAND_RESET = 'CMD_RESET'
COMMAND_MODULE_MOVE = 'CMD_MODULE_MOVE'
COMMAND_MODULE_POSIT = 'CMD_MODULE_POSIT'
COMMAND_CAMERA_MOVE = 'CMD_CAMERA_MOVE'
COMMAND_CAMERA_POSIT = 'CMD_CAMERA_POSIT'
COMMAND_STATUS_LIGHT_ON = 'CMD_STATUS_LIGHT_ON'
COMMAND_STATUS_LIGHT_OFF = 'CMD_STATUS_LIGHT_OFF'
COMMAND_LOAD = "CMD_LOAD"
COMMAND_UNLOAD = "CMD_UNLOAD"
COMMAND_ALIGNMENT = "CMD_ALIGNMENT"
COMMAND_BUTTON_LITUP_ENABLE = 'CMD_POWERON_BUTTON_ENABLE'
COMMAND_BUTTON_LITUP_DISABLE = 'CMD_POWERON_BUTTON_DISABLE'
COMMAND_LITUP_STATUS = 'CMD_POWERON_BUTTON'
COMMAND_QUERY_TEMP = 'CMD_GET_TEMPERATURE'
COMMAND_QUERY_DUT_TEMP = 'CMD_GET_DUT_TEMPERATURE'
COMMAND_PROBE_BUTTON = 'CMD_PROBE_BUTTON'
COMMAND_ZERO_POSIT = 'CMD_ZERO_POSIT'
COMMAND_VACUUM_CTRL = 'CMD_VACUUM'
COMMAND_DUT_LOAD = 'CMD_DUT_LOAD'
COMMAND_DUT_UNLOAD = 'CMD_DUT_UNLOAD'
COMMAND_QUERY_TEMP_RANGE = (10, 60)

COMMAND_USB_POWER_ON = "CMD_USB_POWER_ON"
COMMAND_USB_POWER_OFF = "CMD_USB_POWER_OFF"
COMMAND_PTB_POWER_ON = "CMD_PTB_POWER_ON"
COMMAND_PTB_POWER_OFF = "CMD_PTB_POWER_OFF"
COMMAND_STATUS = "CMD_STATUS"

QUERY_DUT_TEMP_PER_PATTERN = True
DUT_LOAD_WITHOUT_OPERATOR = False
DUT_LITUP_OUTSIDE = True
TIMEOUT_FOR_BTN_IDLE = 20
FIXTURE_LOAD_DLY = 10
FIXTURE_UNLOAD_DLY = 20
FIXTURE_RESET_DLY = 45
FIXTURE_ALIGNMENT_DLY = 18
FIXTURE_MECH_STABLE_DLY = 0.05
FIXTURE_SOCK_DLY = 0.05
PARTICLE_COUNTER_TIMEOUT = 2
FIXTURE_PARTICLE_COUNTER = False

# FIXTRUE_PARTICLE_ADDR_READ = 40006
# FIXTRUE_PARTICLE_ADDR_START = 40003
# FIXTRUE_PARTICLE_ADDR_STATUS = 40003
# PARTICLE_COUNTER_CLJ = False

FIXTRUE_PARTICLE_ADDR_READ = 8
FIXTRUE_PARTICLE_ADDR_START = 30
FIXTRUE_PARTICLE_ADDR_STATUS = 30
PARTICLE_COUNTER_APC = True  # use apc-r210
FIXTRUE_PARTICLE_START_DLY = 0
FIXTURE_QUERY_TEMP_TIMEOUT = 20

# Fixture Status Enum Values
PTB_POSITION_STATUS = ["Testing Position", "Reset Position", "Outside Position", "Other Position"]
BUTTON_STATUS = ["Enable", "Disable"]
PTB_POSITION_STATUS = ["Enable", "Disable"]
CAMERA_POWER_STATUS = ["Enable", "Disable"]
FIXTURE_PTB_OFF_TIME = 1
FIXTURE_PTB_ON_TIME = 1
FIXTURE_USB_OFF_TIME = 1
FIXTURE_USB_ON_TIME = 1

########

#################################
# Fixture related parameters
# DISTANCE_BETWEEN_CAMERA_AND_DATUM = 26041
# genius: 17750+18000, sunny: 18530+18000, gtk: 21450+18000, genius-2: 21950+18000
DISTANCE_BETWEEN_CAMERA_AND_DATUM_dict = {
    'seacliff_mot-03': 18530+18000,
    'seacliff_mot-04': 17750+18000,
    'seacliff_mot-05': 21450+18000,
    'seacliff_mot-06': 21950+18000,
    'seacliff_mot-07': 23020+14000,
}

DISTANCE_BETWEEN_CAMERA_AND_DATUM = 0

##################################
# Test Equipment related parameters
SORTED_EXPORT_LOG = False
IS_PRINT_TO_LOG = False
IS_VERBOSE = True  # some path bug, temp set False and work on True later
CFG_PATH = r'..\Cfg'
TESTTYPE = 0 # for Capture and 1 for CaptureSequence. No other values should be set.

# PATTERNS =  ["W255", "W180", 'W127', 'W090', "R255", "G255", "B255"]
PATTERNS = ["W255", 'W127', "R255", "G255", "B255"]
SAVE_IMAGES = [False, False, False, False, False, False, False, False]
# SAVE_IMAGES = [True, True, True, True, True, True, True, True]
COLORS = [(255, 255, 255), (127, 127, 127), (255, 0, 0), (0, 255, 0), (0, 0, 255)]
DUT_DISPLAYSLEEPTIME = 0
DUT_NVRAM_WRITE_TIMEOUT = 10

VERSION_REVISION_EQUIPMENT = '88'
VERSION_REVISION_LIST = {
    'Conoscope': ['72'],
    'ConoscopeV2': ['87', '88'],
}
FILE_COUNT_INC = {0: 4, 1: 2, 2: 2, 3: 2, }

# set sensor_temperature
TEST_SENSOR_TEMPERATURE = 25.0
TEST_CPU_COUNT = 5

# config
CAM_INIT_CONFIG = {
    "exportFormat": 0,
    "AEMinExpoTimeUs": 10,
    "AEMaxExpoTimeUs": 9985000,
    "AEExpoTimeGranularityUs": 11111,
    "AELevelPercent": 80.0,

    "AEMeasAreaHeight": 200,
    "AEMeasAreaWidth": 192,
    "AEMeasAreaX": 3872,
    "AEMeasAreaY": 2900,

    "bUseRoi": False,
    "RoiXLeft": 0,
    "RoiXRight": 6001,
    "RoiYTop": 0,
    "RoiYBottom": 6001,
    'cxpLinkConfig': 1,
}

SEQ_CAP_INIT_CONFIG = {
    "sensorTemperature": 25,
    "bWaitForSensorTemperature": False,
    # "eNd": setup_cfg[1],  # Conoscope.Nd.Nd_1.value,
    # "eIris": setup_cfg[2],  # Conoscope.Iris.aperture_4mm.value,
    "nbAcquisition": 1,
    "bAutoExposure": False,
    "bUseExpoFile": True,
    'bSaveCapture': False,
    'eOuputImage': 3,
    "exposureTimeUs_FilterX": 10,
    "exposureTimeUs_FilterXz": 10,
    "exposureTimeUs_FilterYa": 10,
    "exposureTimeUs_FilterYb": 10,
    "exposureTimeUs_FilterZ": 10,

    "bSpectro": False,  # configuration for spectro
}

MEASURE_CAP_INIT_CONFIG = {
    "sensorTemperature": 25,
    # "eFilter": setup_cfg[0],  # self._device.Filter.Yb.value,
    # "eNd": setup_cfg[1],  # self._device.Nd.Nd_3.value,
    # "eIris": setup_cfg[2],  # self._device.Iris.aperture_2mm.value
}

MIN_SPACE_REQUIRED = [('C:\\', 500), ('D:\\', 3500)]

# parameters for test sequence.
TEST_SEQ_WAIT_FOR_TEMPERATURE = False
TEST_AUTO_EXPOSURE = False
TEST_SEQ_SAVE_CAPTURE = False

ANALYSIS_GRP_DISTORTION = ['GreenDistortion']
ANALYSIS_GRP_NORMAL_PATTERN = {'W255': 'w',
    'R255': 'r',
    'G255': 'g',
    'B255': 'b',
    'RGBBoresight': 'br',
    'PW255': 'w',
    }
ANALYSIS_GRP_COLOR_PATTERN_EX = {'WhiteDot': 'W255'}

# ANALYSIS_GRP_DISTORTION_PRIMARY = ['X', 'Y', 'Z']
ANALYSIS_GRP_DISTORTION_PRIMARY = ['Y']
# 'setup': (filter, nd, iris) is used for capture image,
# 'exposure': if not set , use seq-file.
# !!! image in Nand: comborgb, Green_Checkerboard_Contrast_Left, Green_Checkerboard_Contrast_Right,
#                          White_CAC_Checkerboard_Contrast_Left, White_CAC_Contrast_Contrast_Right,
#                Green_Sharpness_Pattern,
#                          Green_Distortion_Grid_Left, Green_Distortion_Grid_Right !!!
# Follow instruction from Evan(fb), pattern named with left, should be render to right-module.
#                                   pattern named with right, should be render to left-module.
# Sunny
TEST_ITEM_PATTERNS = [
    {'name': 'W255', 'pattern': 0, 'setup': (7, 0, 3), 'exposure': (111466, 144900, 211768, 167184, 144900)},
    {'name': 'W000', 'pattern': 1, 'setup': (7, 0, 3), 'exposure': (111466, 144900, 211768, 167184, 144900)},
    {'name': 'R255', 'pattern': 2, 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'G255', 'pattern': 3, 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'B255', 'pattern': 4, 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'RGBBoresight', 'pattern': (6, 5), 'setup': (7, 0, 3), 'exposure': (144900, 980852, 468134, 980852, 980852)},
    {'name': 'WhiteDot7', 'pattern': (8, 7), 'setup': (7, 0, 3), 'exposure': (111466, 144900, 211768, 167184, 144900)},
    {'name': 'WhiteDot8', 'pattern': (10, 9), 'setup': (7, 0, 3), 'exposure': (111466, 144900, 211768, 167184, 144900)},
    {'name': 'WhiteDot9', 'pattern': (12, 11), 'setup': (7, 0, 3), 'exposure': (111466, 144900, 211768, 167184, 144900)},
]

TEST_ITEM_PATTERNS_VERIFIED = {'PW255': ('WhitePointGLR', 'WhitePointGLG', 'WhitePointGLB')}

TEST_ITEM_POS = [
    {'name': 'normal', 'pos': (0, 0, 15000),
     'pattern': ['W255', 'R255', 'G255', 'B255', 'RGBBoresight'],
     'condition_A_patterns':[('WhiteDot', 'pattern', ['WhiteDot7', 'WhiteDot8', 'WhiteDot9']),
                             # ('PW255', None, []),
                             ]
     },
]

DATA_AT_POLE_AZI = [(-10.0, 0.0), (-20.0, 0.0), (-30.0, 0.0),
                     (0.0, -10.0), (0.0, -20.0), (0.0, -30.0),
                     (0.0, 0.0), (0.0, 10.0), (0.0, 20.0), (0.0, 30.0),
                     (10.0, 0.0), (20.0, 0.0), (30.0, 0.0)]
DATA_STATUS_DEGS = [10, 20, 30]

# sunny
# COLORMATRIX_COEFF = [[0.9941, -0.0076, -0.0066], [0.0009, 0.9614, -0.0025], [-0.0021, 0.0020, 0.9723]]
# genius
# COLORMATRIX_COEFF = [[0.9459, 0.0134, 0.0081], [-0.0205, 0.9731, 0.0031], [-0.0001, 0.0007, 1.0062]]
COLORMATRIX_COEFF = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

COMPENSATION_COEFF = {
    'L': {
        'DispCen_x_display': 0,
        'DispCen_y_display': 0,
    },
    'R': {
        'DispCen_x_display': 0,
        'DispCen_y_display': 0,
    },
}
##################################
# IT and work order
#
FACEBOOK_IT_ENABLED = False
# does the shopfloor use work orders?
USE_WORKORDER_ENTRY = False
# UI_MODE
OPTIMIZE_UI_MODE = True
SHOW_CONSOLE = False

IS_STATION_ACTIVE = True
STATION_TYPE = 'eureka_mot'
STATION_NUMBER = '0001'
AUTO_SCAN_CODE = False

SHOPFLOOR_SYSTEM = 'e_mot'

VERSION = 'SunnyP2-PreBuild-Alpha'
AUTO_CVT_BGR_IMAGE_FROM_XYZ = False
AUTO_SAVE_2_TXT = False
AUTO_SAVE_PROCESSED_PNG = True
EQUIPMENT_SIM_CAPTURE_FROM_DIR = False
DUT_SIM = False
EQUIPMENT_SIM = False
EQUIPMENT_WHEEL_SIM = False
EQUIPMENT_SPECTRO_SIM = False
FIXTURE_SIM = False
