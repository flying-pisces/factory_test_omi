"""
Release Note:
========================================================
Version 3.0.0
2022-2-18 elton<elton.tian@myzygroup.com>
-1. Init version for OffAxisN
"""
##################################
# directories
#
# Where is the root directory.
# 'factory-test' directory, logs directories, etc will get placed in there.
# (use windows-style paths.)
ROOT_DIR = r'C:\oculus\factory_test_omi\factory_test_stations'
CSV_SUMMARY_DIR = r'C:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\tokki_offaxis_5Npt_5Patterns'


##################################
# serial number codes
#
SERIAL_NUMBER_VALIDATION = False  # set to False for debugging
SERIAL_NUMBER_MODEL_NUMBER = r'^\dPRP[\w|\d]{10}$'  # Peak panel SN

##################################
# Fixture parameters
# Fixture commands
FIXTURE_COMPORT = "COM9" #
FIXTURE_PARTICLE_COMPORT = "COM1" #
FIXTURE_SCANER_COMPORT = 'COM3'
FIXTURE_PARTICLE_ADDR = 1
DUT_COMPORT = "COM1" #
DUT_ETH_PROXY = True
DUT_ETH_PROXY_ADDR = ('192.168.21.132', 6000)

TIMEOUT_FOR_BTN_IDLE = 10

COMMAND_DISP_HELP = "$c.help"
COMMAND_DISP_VERSION_GRP=['mcu','hw','fpga']
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
COMMAND_DISP_VSYNC="REFRESHRATE"
COMMAND_DISP_GETCOLOR = "GetColor"

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

COMMAND_HELP = "CMD_HELP"
COMMAND_STATUS = "CMD_STATUS"
COMMAND_INITIALSTATUS = "CMD_INITIALSTATUS"
COMMAND_RESET = "CMD_RESET"
COMMAND_LOAD = "CMD_LOAD"
COMMAND_UNLOAD = "CMD_UNLOAD"
COMMAND_ID = "CMD_ID"
COMMAND_BUTTON_ENABLE = "CMD_BTN_ENABLE"
COMMAND_BUTTON_DISABLE = "CMD_BTN_DISABLE"
COMMAND_FLEX_POWER_ON = "CMD_FLEX_POWER_ON"
COMMAND_FLEX_POWER_OFF = "CMD_FLEX_POWER_OFF"
COMMAND_MICROUSB_POWER_ON = "CMD_MICROUSB_POWER_ON"
COMMAND_MICROUSB_POWER_OFF = "CMD_MICROUSB_POWER_OFF"
COMMAND_USB_POWER_ON = "CMD_USB_POWER_ON"
COMMAND_USB_POWER_OFF = "CMD_USB_POWER_OFF"
COMMAND_PTB_POWER_ON = "CMD_PTB_POWER_ON"
COMMAND_PTB_POWER_OFF = "CMD_PTB_POWER_OFF"
COMMAND_RADIANT_POWER_ON = "CMD_RADIANT_POWER_ON"
COMMAND_RADIANT_POWER_OFF = "CMD_RADIANT_POWER_OFF"
COMMAND_VERSION = "CMD_VERSION"
COMMAND_GET_PTB_CURRENT = "CMD_GET_PTB_CURRENT"
COMMAND_BARCODE = "CMD_BARCODE"
COMMAND_CLAW_CLOSE = "CMD_CLAW_CLOSE"
COMMAND_CLAW_OPEN = "CMD_CLAW_OPEN"
COMMAND_TRAY_DOWN = "CMD_TRAY_DOWN"
COMMAND_TRAY_UP = "CMD_TRAY_UP"
COMMAND_BUTTON_LIGHT_ON = "CMD_BUTTON_LIGHT_ON"
COMMAND_BUTTON_LIGHT_OFF = "CMD_BUTTON_LIGHT_OFF"
COMMAND_ELIMINATOR_ON = "CMD_ELIMINATOR_ON"
COMMAND_ELIMINATOR_OFF = "CMD_ELIMINATOR_OFF"
COMMAND_CARRIER_POSITION = "CMD_LOAD?"
COMMAND_POGO_UP = "CMD_POGO_UP"
COMMAND_POGO_DOWN = "CMD_POGO_DOWN"
COMMAND_ABS_X_Y = "CMD_ABS_X_Y"
COMMAND_RES_X_Y = "CMD_REG_X_Y"
COMMAND_MOTOR_HOME = "CMD_MOTOR_HOME"
COMMAND_PRESS_DOWN = 'CMD_PRESS_DOWN'
COMMAND_PRESS_UP = 'CMD_PRESS_UP'
COMMAND_TRI_LED_R = 'CMD_LED:R'
COMMAND_TRI_LED_Y = 'CMD_LED:Y'
COMMAND_TRI_LED_G = 'CMD_LED:G'
COMMAND_BUTTON_LITUP_ENABLE = 'CMD_POWERON_BUTTON_ENABLE'
COMMAND_BUTTON_LITUP_DISABLE = 'CMD_POWERON_BUTTON_DISABLE'
COMMAND_LITUP_STATUS = 'CMD_POWERON_BUTTON'
COMMAND_VACUUM_CTRL = 'CMD_VACUUM'

# Fixture Status Enum Values
PTB_POSITION_STATUS = ["Testing Position", "Reset Position", "Outside Position", "Other Position"]
BUTTON_STATUS = ["Enable", "Disable"]
PTB_POSITION_STATUS = ["Enable", "Disable"]
CAMERA_POWER_STATUS = ["Enable", "Disable"]

FIXTURE_UNLOAD_DLY = 20
FIXTURE_PTB_OFF_TIME = 1
FIXTURE_PTB_ON_TIME = 1
FIXTURE_USB_OFF_TIME = 1
FIXTURE_USB_ON_TIME = 1
FIXTURE_PTB_UNLOAD_DLY = 10
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
########

######## DUT Related Parameters which will be defined
# CUSTOM_ADB_RELATIVE_PATH = r'test_station\dut\adb.exe'
# DUT_ON_TIME = 4  ## assuming DUT need 5 seconds to be powered after USB powered on command
# DUT_DISPLAYSLEEPTIME = 1
# DISPLAY_CYCLE_TIME = 2
# DUT_RENDER_ONE_IMAGE_TIMEOUT = 10
# LAUNCH_TIME = 4
# DUT_MAX_WAIT_TIME =60
# DEFAULT_VSYNC_US = 13.8889  # 72  # 111.44646
DUT_ON_MAXRETRY = 5

DUT_DISPLAYSLEEPTIME = 0.025
##################################
# Test Equipment related parameters
IS_VERBOSE = False
IS_PRINT_TO_LOG = False
MPKAPI_RELATIVEPATH = r"C:\Program Files\Radiant Vision Systems\TrueTest 1.7\MPK_API.dll"
SEQUENCE_RELATIVEPATH = r'test_station\test_equipment\algorithm\tokki_offaxis2022.seqxc'
CALIBRATION_RELATIVEPATH = r'test_station\test_equipment\calibration'

ANALYSIS_RELATIVEPATH = r'factory-test_logs'

FOCUS_DISTANCE = 0.45
APERTURE = 8.0
ROTATION = 0
IS_AUTOEXPOSURE = False
LEFT = 1764
TOP = 928
WIDTH = 1337
HEIGHT = 1400
IS_SAVEDB = True
IS_EXPORT_CSV = False
IS_EXPORT_PNG = False
Resolution_Bin_X = 360
Resolution_Bin_Y = 360

TEST_POSITIONS = [('P1', (0, 0), ["W255", "W000", "R255", "G255", "B255"]),
                 ('P2', (1500, 0), ['W255', "W000", "R255", "G255", "B255"]),
                 ('P4', (0, -1500), ['W255', "W000", "R255", "G255", "B255"]),
                 ('P6', (-1500, 0), ['W255', "W000", "R255", "G255", "B255"]),
                 ('P8', (0, 1500), ['W255', "W000", "R255", "G255", "B255"]),
                 ]

TEST_PATTERNS = {
    'W255': {
        'P': (255, 255, 255),
        'A': "Points Of Interest W255",
    },
    'W000': {
        'P': (0, 0, 0),
        'A': "Points Of Interest W000",
    },
    'R255': {
        'P': (255, 0, 0),
        'A': "Points Of Interest R255",
    },
    'G255': {
        'P': (0, 255, 0),
        'A': "Points Of Interest G255",
    },
    'B255': {
        'P': (0, 0, 255),
        'A': "Points Of Interest B255",
    },
    'L127': {
        'P': (127, 127, 127),
        'A': "Points Of Interest L127",
    },
    'L063': {
        'P': (63, 63, 63),
        'A': "Points Of Interest L063",
    },
    'L031': {
        'P': (31, 31, 31),
        'A': "Points Of Interest L031",
    },
    'L015': {
        'P': (15, 15, 15),
        'A': "Points Of Interest L015",
    },
    'L007': {
        'P': (7, 7, 7),
        'A': "Points Of Interest L007",
    },
}

##################################

CR_TEST_PATTERNS = ['W255', 'W000']
CENTER_AT_POLE_AZI = 'P_0_0'

SAVE_PNL_IF_FAIL = {
    'LA': [],
    'RA': [],
}

BRIGHTNESS_AT_POLE_AZI = [(0, 0),
                         (30, 0), (30, 22), (30, 45), (30, 90), (30, 135), (30, 180), (30, 225), (30, 270), (30, 315), (30, 68), (30, 112), (30, 158), (30, 202), (30, 248), (30, 292), (30, 338),
                         (10, 0), (10, 22), (10, 45), (10, 90), (10, 135), (10, 180), (10, 225), (10, 270), (10, 315), (10, 68), (10, 112), (10, 158), (10, 202), (10, 248), (10, 292), (10, 338),
                         (20, 0), (20, 22), (20, 45), (20, 90), (20, 135), (20, 180), (20, 225), (20, 270), (20, 315), (20, 68), (20, 112), (20, 158), (20, 202), (20, 248), (20, 292), (20, 338),
                         (15, 0), (15, 22), (15, 45), (15, 90), (15, 135), (15, 180), (15, 225), (15, 270), (15, 315), (15, 68), (15, 112), (15, 158), (15, 202), (15, 248), (15, 292), (15, 338),
                          ]
BRIGHTNESS_AT_POLE_AZI_PER = [(15, 0), (15, 90), (15, 180), (15, 270), (30, 0), (30, 90), (30, 180), (30, 270)]
BRIGHTNESS_AT_POLE_ASSEM = [((30, 0), (30, 180))]
COLORSHIFT_AT_POLE_AZI = [(15, 0), (15, 22), (15, 45), (15, 90), (15, 135), (15, 180), (15, 225), (15, 270), (15, 315), (15, 68), (15, 112), (15, 158), (15, 202), (15, 248), (15, 292), (15, 338),
                         (30, 0), (30, 22), (30, 45), (30, 90), (30, 135), (30, 180), (30, 225), (30, 270), (30, 315), (30, 68), (30, 112), (30, 158), (30, 202), (30, 248), (30, 292), (30, 338)]
COLOR_PRIMARY_AT_POLE_AZI = [(0, 0), (15, 0), (15, 180), (30, 0), (30, 180)]

CR_AT_POLE_AZI = [(0, 0), (15, 0), (15, 90), (15, 180), (15, 270), (30, 0), (30, 90), (30, 180), (30, 270)]

EXPORT_RAW_DATA_PATTERN = {'P1': ['W255', 'W000']}
EXPORT_RAW_DATA_PATTERN_AZI = [('Vertical', 90), ('Diagonal', 45), ('Horizontal', 0), ('Diagonal', 135)]
EXPORT_RAW_DATA_PATTERN_POLE = list(range(-60, 61, 2))
IS_EXPORT_RAW_DATA = True

##################################
# IT and work order
#
FACEBOOK_IT_ENABLED = False
# does the shopfloor use work orders?
USE_WORKORDER_ENTRY = False

IS_STATION_ACTIVE = True
STATION_TYPE = 'tokki_offaxisn'
STATION_NUMBER = '0001'
SHOPFLOOR_SYSTEM = ''
AUTO_SCAN_CODE = False

DATA_COLLECT_ONLY = False
EQUIPMENT_DEMO_DATABASE = r'C:\ShareData\OffAxis'

DUT_SIM = False
CAMERA_SN = "1525410258"
# CAMERA_SN = 'Demo'
EQUIPMENT_SIM = False
FIXTURE_SIM = False
