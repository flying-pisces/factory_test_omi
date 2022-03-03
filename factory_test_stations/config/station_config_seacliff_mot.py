"""
Release Note:
========================================================
Version 1.2.5
2021-12-27 elton<elton.tian@myzygroup>
-1. add compensation for boresight center
-2. add compensation records into logs.

========================================================
Version 1.2.4
2021-11-16 elton<elton.tian@myzygroup>
-1. Conoscope V72
-2. Memory optimize
-3. Quit application while error.
-4. Fix errorcode issue when fail to do alignment 
-5. throw exception while temperature is over range.
-6. Algorithm updated to EVT1_1

========================================================
Version 1.2.3
2021-9-24 elton<elton.tian@myzygroup>
-1. add json-file reading for MOT while reading the data from DDIC.
-2. add SPEC_VERSION in limit.

========================================================
Version 1.2.2
2021-9-18 elton<elton.tian@myzygroup>
-1. add support for READ EEP DATA @GTK.
-2. algorithm V3.3 for MOT.
-3. optimize speed for MOT.

========================================================
Version 1.2.1
2021-8-16 elton<elton.tian@myzygroup>
-1. algorithm V3.2 for MOT.

========================================================
Version 1.2.0
2021-8-6 elton<elton.tian@myzygroup>
-1. algorithm V3 for MOT.

========================================================
Version 1.1.1b5
2021-6-4 author<xxx@xxx.com>
-1. remove default setting for white-dotV.
-2. update taprisoit to ver67

========================================================
Version 1.1.1b4
2021-5-20 author<xxx@xxx.com>
-1. add white-dotV2 pattern for MOT.

========================================================
Version 1.1.1b3
2021-4-24 author<xxx@xxx.com>
-1. add white-dot pattern for MOT.

========================================================
Version 1.1.1b2
2021-3-1 author<xxx@xxx.com>
-1. record temp. for each pattern.

========================================================
Version 1.1.2
2021-2-9 author<xxx@xxx.com>
-1. update reading for exposure_time from Eldim-Conoscope.

========================================================
Version 1.1.1
2021-2-25 author<xxx@xxx.com>
-1. disable all the button before testing.
-2. optimize connection for fixture.
-3. reset trapsiot automatically while some errors comes out from trapsiot.

========================================================
Version 1.1.1b
2021-2-9 author<xxx@xxx.com>
-1. change datetime format to local time.
-2. optimize setting for auto exposure time in sequence-mode.
-3. fix: unable to power on DUT in fixture emulator mode.
-4. optimize loop-testing mode.

========================================================
Version 1.1.0
2020-1-18 elton<elton.tian@myzygroup.com>
-1. Init version for MOT
"""


##################################
# directories
#
# Where is the root directory.
# 'factory-test' directory, logs directories, etc will get placed in there.
# (use windows-style paths.)
ROOT_DIR = r'C:\oculus\factory_test_omi\factory_test_stations'
SEQUENCE_RELATIVEPATH = r'C:\oculus\run\seacliff_mot_run\test_station\test_equipment\algorithm'
CONOSCOPE_DLL_PATH = r'C:\ORel\dist\test_equipment_57'
CSV_SUMMARY_DIR = r'C:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\seacliff_mot_summary'
RAW_IMAGE_LOG_DIR = r'C:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\raw'
RAW_IMAGE_LOG_DIR = r'c:\ShareData\Oculus_RawData'
##################################
# serial number codes
#
SERIAL_NUMBER_VALIDATION = False  # set to False for debugging
SERIAL_NUMBER_MODEL_NUMBER = 'PR0'  # Peak panel SN

##################################
# Fixture parameters
# Fixture commands
PROXY_COMMUNICATION_PATH = r"C:\vision\Release\vision.exe"
IS_PROXY_COMMUNICATION = False
PROXY_ENDPOINT = 8000
FIXTURE_COMPORT = "COM1" #
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

DISTANCE_BETWEEN_CAMERA_AND_DATUM = 21950+18000

##################################
# Test Equipment related parameters
SORTED_EXPORT_LOG = False
IS_PRINT_TO_LOG = False
IS_VERBOSE = False # some path bug, temp set False and work on True later
CFG_PATH = r'..\Cfg'
TESTTYPE = 0 # for Capture and 1 for CaptureSequence. No other values should be set.

# PATTERNS =  ["W255", "W180", 'W127', 'W090', "R255", "G255", "B255"]
PATTERNS = ["W255", 'W127', "R255", "G255", "B255"]
SAVE_IMAGES = [False, False, False, False, False, False, False, False]
# SAVE_IMAGES = [True, True, True, True, True, True, True, True]
COLORS = [(255, 255, 255), (127, 127, 127), (255, 0, 0), (0, 255, 0), (0, 0, 255)]
DUT_DISPLAYSLEEPTIME = 0
DUT_NVRAM_WRITE_TIMEOUT = 10

VERSION_REVISION_EQUIPMENT = '72'
FILE_COUNT_INC = {0: 4, 1: 2, 2: 2, 3: 2, }

# set sensor_temperature
TEST_SENSOR_TEMPERATURE = 25.0
TEST_CPU_COUNT = 5

# config
CAM_INIT_CONFIG = {
    "exportFormat": 0,
    "AEMinExpoTimeUs": 10,
    "AEMaxExpoTimeUs": 9985000,
    "AEExpoTimeGranularityUs": 11146,
    "AELevelPercent": 80.0,

    "AEMeasAreaHeight": 0,
    "AEMeasAreaWidth": 0,
    "AEMeasAreaX": 0,
    "AEMeasAreaY": 0,

    "bUseRoi": False,
    "RoiXLeft": 0,
    "RoiXRight": 6001,
    "RoiYTop": 0,
    "RoiYBottom": 6001,
    'cxpLinkConfig': 0,
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
    {'name': 'PW255', 'pattern': 22, 'setup': (7, 0, 3), 'exposure': (111466, 144900, 211768, 167184, 144900)},
    {'name': 'W255', 'pattern': 22, 'setup': (7, 0, 3), 'exposure': (111466, 144900, 211768, 167184, 144900)},
    {'name': 'G127', 'pattern': (127, 127, 127), 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'W000', 'pattern': 23, 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'RGB', 'pattern': 0, 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'R255', 'pattern': 24, 'setup': (7, 0, 3), 'exposure': (144900, 980852, 468134, 980852, 980852)},
    {'name': 'G255', 'pattern': 25, 'setup': (7, 0, 3), 'exposure': (300935, 980852, 345533, 178334, 980852)},
    {'name': 'B255', 'pattern': 26, 'setup': (7, 0, 3), 'exposure': (980852, 156050, 980852, 980852, 167184)},
    {'name': 'GreenContrast', 'pattern': (2, 1), 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'WhiteContrast', 'pattern': (4, 3), 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'GreenSharpness', 'pattern': 5, 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'GreenDistortion', 'pattern': (7, 6), 'setup': (7, 0, 3), 'exposure': (378967, 980852, 434700, 222917, 980852)},  #, 'oi_mode': 2},
    {'name': 'WhiteDot7', 'pattern': (8, 9), 'setup': (7, 0, 3), 'exposure': (111466, 144900, 211768, 167184, 144900)},
    {'name': 'WhiteDot8', 'pattern': (10, 11), 'setup': (7, 0, 3), 'exposure': (111466, 144900, 211768, 167184, 144900)},
    {'name': 'WhiteDot9', 'pattern': (12, 13), 'setup': (7, 0, 3), 'exposure': (111466, 144900, 211768, 167184, 144900)},
    {'name': 'WhiteDot10', 'pattern': (14, 15), 'setup': (7, 0, 3), 'exposure': (111466, 144900, 211768, 167184, 144900)},
    {'name': 'WhiteDot11', 'pattern': (16, 17), 'setup': (7, 0, 3), 'exposure': (111466, 144900, 211768, 167184, 144900)},
    {'name': 'WhiteDot12', 'pattern': (18, 19), 'setup': (7, 0, 3), 'exposure': (111466, 144900, 211768, 167184, 144900)},
    {'name': 'RGBBoresight', 'pattern': (20, 21), 'setup': (7, 0, 3), 'exposure': (111466, 144900, 211768, 167184, 144900)},
]
# Genius
TEST_ITEM_PATTERNS1 = [
    {'name': 'PW255', 'pattern': 22, 'setup': (7, 0, 3), 'exposure': (89167, 111466, 167184, 156050, 111466)},
    {'name': 'W255', 'pattern': 22, 'setup': (7, 0, 3), 'exposure': (89167, 111466, 167184, 156050, 111466)},
    {'name': 'G127', 'pattern': (127, 127, 127), 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'W000', 'pattern': 23, 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'RGB', 'pattern': 0, 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'R255', 'pattern': 24, 'setup': (7, 0, 3), 'exposure': (122601, 980852, 401251, 980852, 980852)},
    {'name': 'G255', 'pattern': 25, 'setup': (7, 0, 3), 'exposure': (278651, 980852, 278651, 167184, 980852)},
    {'name': 'B255', 'pattern': 26, 'setup': (7, 0, 3), 'exposure': (980852, 122601, 980852, 980852, 122601)},
    {'name': 'GreenContrast', 'pattern': (2, 1), 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'WhiteContrast', 'pattern': (4, 3), 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'GreenSharpness', 'pattern': 5, 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'GreenDistortion', 'pattern': (7, 6), 'setup': (7, 0, 3), 'exposure': (378967, 980852, 434700, 222917, 980852), 'oi_mode': 2},
    {'name': 'WhiteDot7', 'pattern': (8, 9), 'setup': (7, 0, 3), 'exposure': (89167, 111466, 167184, 156050, 111466)},
    {'name': 'WhiteDot8', 'pattern': (10, 11), 'setup': (7, 0, 3), 'exposure': (89167, 111466, 167184, 156050, 111466)},
    {'name': 'WhiteDot9', 'pattern': (12, 13), 'setup': (7, 0, 3), 'exposure': (89167, 111466, 167184, 156050, 111466)},
    {'name': 'WhiteDot10', 'pattern': (14, 15), 'setup': (7, 0, 3), 'exposure': (89167, 111466, 167184, 156050, 111466)},
    {'name': 'WhiteDot11', 'pattern': (16, 17), 'setup': (7, 0, 3), 'exposure': (89167, 111466, 167184, 156050, 111466)},
    {'name': 'WhiteDot12', 'pattern': (18, 19), 'setup': (7, 0, 3), 'exposure': (89167, 111466, 167184, 156050, 111466)},
    {'name': 'RGBBoresight', 'pattern': (20, 21), 'setup': (7, 0, 3), 'exposure': (89167, 111466, 167184, 156050, 111466)},
]

TEST_ITEM_PATTERNS_VERIFIED = {'PW255': ('WhitePointGLR', 'WhitePointGLG', 'WhitePointGLB')}

TEST_ITEM_POS = [
    {'name': 'normal', 'pos': (0, 0, 15000),
     'pattern': ['W255', 'RGBBoresight'],
     'condition_A_patterns':[('WhiteDot', 'pattern', ['WhiteDot10', 'WhiteDot11', 'WhiteDot12']),
                             # ('PW255', None, []),
                             ]
     },
    # {'name': 'normal', 'pos': (0, 0, 15000),
    #  'pattern': ['W255', 'G127', 'W000', 'RGB', 'R255', 'G255', 'B255', 'GreenContrast', 'WhiteContrast',
    #              'GreenSharpness', 'GreenDistortion']
    #  },
    # {'name': 'extendedz', 'pos': (0, 0, 27000),
    #  'pattern': ['W255', 'GreenDistortion']
    #  },
    # {'name': 'blemish', 'pos': (0, 0, 5000),
    #  'pattern': ['W255']
    #  },
    # {'name': 'extendedxpos', 'pos': (5071, 0, 16124),
    #  'pattern': ['W255']
    #  },
    # {'name': 'extendedxneg', 'pos': (-5071, 0, 16124),
    #  'pattern': ['W255']
    #  },
    # {'name': 'extendedypos', 'pos': (0, 5071, 16124),
    #  'pattern': ['W255']
    #  },
    # {'name': 'extendedyneg', 'pos': (0, -5071, 16124),
    #  'pattern': ['W255']
    #  },
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
STATION_TYPE = 'seacliff_mot'
STATION_NUMBER = '0001'
AUTO_SCAN_CODE = False

SHOPFLOOR_SYSTEM = 'genius_mot'

VERSION = 'SunnyP2-PreBuild-Alpha'
AUTO_CVT_BGR_IMAGE_FROM_XYZ = False
AUTO_SAVE_2_TXT = False
AUTO_SAVE_PROCESSED_PNG = True
EQUIPMENT_SIM_CAPTURE_FROM_DIR = False
DUT_SIM = True
EQUIPMENT_SIM = True
EQUIPMENT_WHEEL_SIM = True
FIXTURE_SIM = True
