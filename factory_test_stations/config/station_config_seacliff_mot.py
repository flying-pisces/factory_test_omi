
##################################
# directories
#
# Where is the root directory.
# 'factory-test' directory, logs directories, etc will get placed in there.
# (use windows-style paths.)
ROOT_DIR = r'C:\oculus\factory_test_omi\factory_test_stations'
SEQUENCE_RELATIVEPATH = r'C:\oculus\run\seacliff_mot_run\test_station\test_equipment\algorithm'
CONOSCOPE_DLL_PATH = r'C:\ORel\dist\test_equipment'
CSV_SUMMARY_DIR = r'C:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\seacliff_summary'
RAW_IMAGE_LOG_DIR = r'C:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\raw'

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
DUT_ETH_PROXY = True
PROXY_ENDPOINT = 8000
FIXTURE_COMPORT = "COM4" #
FIXTURE_PARTICLE_COMPORT = "COM8" #
FIXTURE_PARTICLE_ADDR = 1
DUT_COMPORT = "COM5" #

AUTO_CFG_COMPORTS = False
FIXTURE_PARTICLE_COMPORT_FILTER = 'VID:PID=0403:6001'

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

COMMAND_DISP_POWERON_DLY = 1.5
COMMAND_DISP_RESET_DLY = 1
COMMAND_DISP_SHOWIMG_DLY = 0.5
COMMAND_DISP_POWEROFF_DLY = 0.2

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
COMMAND_PROBE_BUTTON = 'CMD_PROBE_BUTTON'

COMMAND_USB_POWER_ON = "CMD_USB_POWER_ON"
COMMAND_USB_POWER_OFF = "CMD_USB_POWER_OFF"
COMMAND_PTB_POWER_ON = "CMD_PTB_POWER_ON"
COMMAND_PTB_POWER_OFF = "CMD_PTB_POWER_OFF"
COMMAND_STATUS = "CMD_STATUS"

DUT_LOAD_WITHOUT_OPERATOR = False
DUT_LITUP_OUTSIDE = True
FIXTURE_UNLOAD_DLY = 20
FIXTURE_ALIGNMENT_DLY = 10
FIXTURE_MECH_STABLE_DLY = 0.05
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
DISTANCE_BETWEEN_CAMERA_AND_DATUM = 18530+18000

##################################
# Test Equipment related parameters
IS_PRINT_TO_LOG = False
IS_VERBOSE = True # some path bug, temp set False and work on True later
CFG_PATH = r'Cfg'
TESTTYPE = 0 # for Capture and 1 for CaptureSequence. No other values should be set.

# PATTERNS =  ["W255", "W180", 'W127', 'W090', "R255", "G255", "B255"]
PATTERNS = ["W255", 'W127', "R255", "G255", "B255"]
SAVE_IMAGES = [False, False, False, False, False, False, False, False]
# SAVE_IMAGES = [True, True, True, True, True, True, True, True]
COLORS = [(255, 255, 255), (127, 127, 127), (255, 0, 0), (0, 255, 0), (0, 0, 255)]
DUT_DISPLAYSLEEPTIME = 0.1

VERSION_REVISION_EQUIPMENT = 53
FILE_COUNT_INC = 14

# set sensor_temperature
TEST_SENSOR_TEMPERATURE = 25.0

# config
CAM_INIT_CONFIG = {
    "exportFormat": 0,
    "AEMinExpoTimeUs": 10,
    "AEMaxExpoTimeUs": 9985000,
    "AEExpoTimeGranularityUs": 11111,
    "AELevelPercent": 80.0,

    "AEMeasAreaHeight": 0,
    "AEMeasAreaWidth": 0,
    "AEMeasAreaX": 0,
    "AEMeasAreaY": 0,

    "bUseRoi": False,
    "RoiXLeft": 0,
    "RoiXRight": 6001,
    "RoiYTop": 0,
    "RoiYBottom": 6001
}

# parameters for test sequence.
TEST_SEQ_WAIT_FOR_TEMPERATURE = False
TEST_AUTO_EXPOSURE = True
TEST_SEQ_USE_EXPO_FILE = False
TEST_SEQ_SAVE_CAPTURE = True

ANALYSIS_GRP_DISTORTION = ['GreenDistortion']
ANALYSIS_GRP_MONO_PATTERN = ['W255']
ANALYSIS_GRP_COLOR_PATTERN = ['W255', 'R255', 'G255', 'B255']

ANALYSIS_GRP_DISTORTION_PRIMARY = ['X', 'Y', 'Z']

# 'setup': (filter, nd, iris) is used for capture image,
# 'exposure': if not set , use seq-file.
# !!! image in Nand: comborgb, Green_Checkerboard_Contrast_Left, Green_Checkerboard_Contrast_Right,
#                          White_CAC_Checkerboard_Contrast_Left, White_CAC_Contrast_Contrast_Right,
#                Green_Sharpness_Pattern,
#                          Green_Distortion_Grid_Left, Green_Distortion_Grid_Right !!!
# Follow instruction from Evan(fb), pattern named with left, should be render to right-module.
#                                   pattern named with right, should be render to left-module.

TEST_ITEM_PATTERNS = [
    {'name': 'W255', 'pattern': (255, 255, 255), 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'G127', 'pattern': (127, 127, 127), 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'W000', 'pattern': (0, 0, 0), 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'RGB', 'pattern': 0, 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'R255', 'pattern': (255, 0, 0), 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'G255', 'pattern': (0, 255, 0), 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'B255', 'pattern': (0, 0, 255), 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'GreenContrast', 'pattern': (2, 1), 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'WhiteContrast', 'pattern': (4, 3), 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'GreenSharpness', 'pattern': 5, 'setup': (7, 0, 3), 'exposure': '5000'},
    {'name': 'GreenDistortion', 'pattern': (7, 6), 'setup': (7, 0, 3), 'exposure': '5000'}
]

TEST_ITEM_POS = [
    {'name': 'normal', 'pos': (0, 0, 15000),
     'pattern': ['W255', 'R255', 'G255', 'B255', 'GreenDistortion']
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
##################################
# IT and work order
#
FACEBOOK_IT_ENABLED = False
# does the shopfloor use work orders?
USE_WORKORDER_ENTRY = False

VERSION = 'SunnyP2-PreBuild-Alpha'
AUTO_CVT_BGR_IMAGE_FROM_XYZ = False
AUTO_SAVE_2_TXT = False
EQUIPMENT_SIM_CAPTURE_FROM_DIR = False
DUT_SIM = False
EQUIPMENT_SIM = False
EQUIPMENT_WHEEL_SIM = False
FIXTURE_SIM = False
