
##################################
# directories
#
# Where is the root directory.
# 'factory-test' directory, logs directories, etc will get placed in there.
# (use windows-style paths.)
ROOT_DIR = r'C:\oculus\factory_test_omi\factory_test_stations'
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
IS_PROXY_COMMUNICATION = True
PROXY_ENDPOINT = 8000
FIXTURE_COMPORT = "COM4" #
FIXTURE_PARTICLE_COMPORT = "COM8" #
FIXTURE_PARTICLE_ADDR = 1
DUT_COMPORT = "COM5" #

COMMAND_DISP_HELP = "$c.help"
COMMAND_DISP_VERSION_GRP=['mcu', 'hw', 'fpga']
COMMAND_DISP_VERSION = "Version"
COMMAND_DISP_GETBOARDID = "getBoardID"
COMMAND_DISP_POWERON = "DUT.powerOn,FPGA_compressMode"
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

COMMAND_USB_POWER_ON = "CMD_USB_POWER_ON"
COMMAND_USB_POWER_OFF = "CMD_USB_POWER_OFF"
COMMAND_PTB_POWER_ON = "CMD_PTB_POWER_ON"
COMMAND_PTB_POWER_OFF = "CMD_PTB_POWER_OFF"
COMMAND_STATUS = "CMD_STATUS"

DUT_LITUP_OUTSIDE = True
FIXTURE_UNLOAD_DLY = 20
FIXTURE_ALIGNMENT_DLY = 10

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
DISTANCE_BETWEEN_CAMERA_AND_DATUM = 26041

##################################
# Test Equipment related parameters
IS_VERBOSE = True # some path bug, temp set False and work on True later
CFG_PATH = r'test_station\test_equipment\Cfg'
TESTTYPE = 0 # for Capture and 1 for CaptureSequence. No other values should be set.

# PATTERNS =  ["W255", "W180", 'W127', 'W090', "R255", "G255", "B255"]
PATTERNS = ["W255", 'W127', "R255", "G255", "B255"]
SAVE_IMAGES = [False, False, False, False, False, False, False, False]
# SAVE_IMAGES = [True, True, True, True, True, True, True, True]
COLORS = [(255, 255, 255), (127, 127, 127), (255, 0, 0), (0, 255, 0), (0, 0, 255)]
DUT_DISPLAYSLEEPTIME = 1

TEST_ITEM_PATTERNS = [
    {'name': 'W255', 'pattern': (255, 255, 255), 'exposure': 3100},
    {'name': 'G127', 'pattern': (127, 127, 127), },
    {'name': 'W000', 'pattern': (0, 0, 0), },
    {'name': 'RGB', 'pattern': 0, },
    {'name': 'R255', 'pattern': (255, 0, 0), },
    {'name': 'G255', 'pattern': (0, 255, 0), },
    {'name': 'B255', 'pattern': (0, 0, 255), },
    {'name': 'GreenContrast', 'pattern': 1, },
    {'name': 'WhiteContrast', 'pattern': 2, },
    {'name': 'GreenSharpness', 'pattern': 3, },
    {'name': 'GreenDistortion', 'pattern': 4, }
]

TEST_ITEM_POS = [
    {'name': 'normal', 'pos': (0, 0, 15000),
     'pattern': ['W255', 'G127', 'W000', 'RGB', 'R255', 'G255', 'B255', 'GreenContrast', 'WhiteContrast',
                 'GreenSharpness', 'GreenDistortion']
     },
    {'name': 'extendedz', 'pos': (0, 0, 27000),
     'pattern': ['GreenDistortion']
     },
    {'name': 'blemish', 'pos': (0, 0, 5000),
     'pattern': ['W255']
     },
    {'name': 'extendedxpos', 'pos': (5071, 0, 16124),
     'pattern': ['W255']
     },
    {'name': 'extendedxneg', 'pos': (-5071, 0, 16124),
     'pattern': ['W255']
     },
    {'name': 'extendedypos', 'pos': (0, -5071, 16124),
     'pattern': ['W255']
     },
    {'name': 'extendedyneg', 'pos': (0, +5071, 16124),
     'pattern': ['W255']
     },
]

##################################
# IT and work order
#
FACEBOOK_IT_ENABLED = False
# does the shopfloor use work orders?
USE_WORKORDER_ENTRY = False

VERSION = 'SunnyP2-PreBuild-Alpha'
EQUIPMENT_DEMO_DATABASE = r'C:\360Downloads'
DUT_SIM = False
CAMERA_SN = "Demo"
EQUIPMENT_SIM = False
FIXTURE_SIM = False
