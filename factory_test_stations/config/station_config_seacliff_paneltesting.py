"""
Release Note:
========================================================
Version 1.1.1b
2021-2-17 elton.tian<elton.tian@myzygroup.com>
-1. init version base on ERS P2.
-2. change datetime format to local time.
-3. fix: unable to power on DUT in fixture emulator mode.
-4. optimize loop-testing mode.
-5. optimize auto-finder for ParticleCounter.

========================================================
Version 0.1.4
2020-12-30 elton<elton.tian@myzygroup.com>
-1. Init version for bluni based on ERS P1.
"""
##################################
# directories
#
# Where is the root directory.
# 'factory-test' directory, logs directories, etc will get placed in there.
# (use windows-style paths.)
ROOT_DIR = r'C:\oculus\factory_test_omi\factory_test_stations'
CSV_SUMMARY_DIR = r'C:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\paneltesting_summary'

##################################
# serial number codes
#
SERIAL_NUMBER_VALIDATION = False  # set to False for debugging
SERIAL_NUMBER_MODEL_NUMBER = '\d30[\w|\d]{11}'  # Fake model number requirement, need config

##################################
# Fixture parameters
# Fixture commands
FIXTURE_PARTICLE_COUNTER = True
FIXTURE_PARTICLE_ADDR = 1
DUT_COMPORT = 'COM1'
CA_PORT = 'COM2'
FIXTURE_COMPORT = 'COM1'
FIXTURE_PARTICLE_COMPORT = 'COM2'

AUTO_CFG_COMPORTS = False
FIXTURE_PARTICLE_COMPORT_FILTER = 'VID:PID=0403:6001'

COMMAND_DISP_HELP = "$c.help"
COMMAND_DISP_VERSION_GRP = ['mcu', 'hw', 'fpga']
COMMAND_DISP_VERSION = "Version"
COMMAND_DISP_GETBOARDID = "getBoardID"
COMMAND_DISP_POWERON = "DUT.powerOn,FPGA_compressMode"
COMMAND_DISP_POWEROFF = "DUT.powerOff"
COMMAND_DISP_RESET = "Reset"
COMMAND_DISP_SETCOLOR = "SetColor"
COMMAND_DISP_SHOWIMAGE = "ShowImage"
COMMAND_DISP_READ = "MIPI.Read"
COMMAND_DISP_WRITE = "MIPI.Write"
COMMAND_DISP_2832WRITE = "t.2832_MIPI_WRITE"
COMMAND_DISP_VSYNC = "REFRESHRATE"

COMMAND_DISP_POWERON_DLY = 1.5
COMMAND_DISP_RESET_DLY = 1
COMMAND_DISP_SHOWIMG_DLY = 1
COMMAND_DISP_POWEROFF_DLY = 0.2

DISP_CHECKER_ENABLE = False
DISP_CHECKER_DLY = 2
DISP_CHECKER_IMG_INDEX = 0
DISP_CHECKER_CAMERA_INDEX = 0
DISP_CHECKER_THRESH_LOW = 200
DISP_CHECKER_THRESH_HIGH = 255
DISP_CHECKER_MIN = 50
DISP_CHECKER_L_SCORE = 100
DISP_CHECKER_H_SCORE = 1000
DISP_CHECKER_EXL_SCORE = 20000
DISP_CHECKER_COUNT = 2
DISP_CHECKER_IMG_SAVED = False

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
COMMAND_CA_UP = 'CMD_CARRIER_UP'
COMMAND_CA_DOWN = 'CMD_CARRIER_DW'

FIXTURE_RESET_DLY = 50
FIXTURE_UNLOAD_DLY = 15
DUT_LOAD_WITHOUT_OPERATOR = False

DUT_LITUP_OUTSIDE = True
TIMEOUT_FOR_BTN_IDLE = 20
# Fixture Status Enum Values
PTB_POSITION_STATUS = ["Testing Position", "Reset Position", "Outside Position", "Other Position"]
BUTTON_STATUS = ["Enable", "Disable"]
CAMERA_POWER_STATUS = ["Enable", "Disable"]

# pariticle counter
FIXTRUE_PARTICLE_ADDR_READ = 8
FIXTRUE_PARTICLE_ADDR_START = 30
FIXTRUE_PARTICLE_ADDR_STATUS = 30
PARTICLE_COUNTER_APC = True  # use apc-r210
FIXTRUE_PARTICLE_START_DLY = 0
PARTICLE_COUNTER_TIMEOUT = 2
##################################
# shopfloor
#
SHOPFLOOR_SYSTEM = 'Sunny'
# Will we be enforcing shopfloor routing?
ENFORCE_SHOPFLOOR_ROUTING = False
# does the shopfloor use work orders?
# USE_WORKORDER_ENTRY = True

######## DUT Related Parameters which will be defined
DUT_ON_TIME = 4  # assuming DUT need 5 seconds to be powered after USB powered on command
DUT_DISPLAYSLEEPTIME = 1
DISPLAY_CYCLE_TIME = 2
DUT_RENDER_ONE_IMAGE_TIMEOUT = 0
LAUNCH_TIME = 4
DUT_MAX_WAIT_TIME = 60
DUT_ON_MAXRETRY = 5

##################################
# Test Equipment related parameters
IS_PRINT_TO_LOG = False
IS_VERBOSE = True
MPKAPI_RELATIVEPATH = r'test_station\test_equipment\MPK_API.dll'
SEQUENCE_RELATIVEPATH = r'test_station\test_equipment\algorithm\y29 particle Defect.seqxc'
CALIBRATION_RELATIVEPATH = r'test_station\test_equipment\calibration'
ANALYSIS_RELATIVEPATH = r'factory-test_logs'
RAW_IMAGE_LOG_DIR = r'C:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\raw'

# LEFT = 462
# TOP = 1253
# WIDTH = 3781
# HEIGHT = 3954
LEFT = 200
TOP = 1300
WIDTH = 3781
HEIGHT = 3954
IS_SAVEDB = True
IS_EXPORT_CSV = False
IS_EXPORT_PNG = False
Resolution_Bin_X_REGISTER = 10
Resolution_Bin_Y_REGISTER = 10
Resolution_REGISTER_SKIPTEXT = 6
Resolution_Bin_X = 10
Resolution_Bin_Y = 10

PATTERNS_BRIGHT = ['W028', 'W048', 'W000']  # the first two are used to register data for bright test.
PATTERNS_DARK = ['W255', "R255", "G255", "B255"]
SAVE_IMAGES = [True, True, True, True, True, True, True]
PATTERN_COLORS = {'W028': (28, 28, 28),
                  'W048': (48, 48, 48),
                  'W000': (0, 0, 0),
                  'W255': (255, 255, 255),
                  'R255': (255, 0, 0),
                  'G255': (0, 255, 0),
                  'B255': (0, 0, 255)}

ANALYSIS = {'W028': "ParticleDefects W028",
            'W048': "ParticleDefects W048",
            'W000': "ParticleDefects W000",
            'W255': "ParticleDefects W255",
            'R255': "ParticleDefects R255",
            'G255': "ParticleDefects G255",
            'B255': "ParticleDefects B255"}

QUALITY_AREA_R = 18
SUPER_QUALITY_AREA_R = 7
SEPARATION_DISTANCE = 5
SEPARATION_DISTANCE_L = 1

SUPER_AREA_DEFECTS_COUNT_L = 0
SUPER_AREA_DEFECTS_COUNT_H = 1
QUALITY_AREA_DEFECTS_COUNT_B = 0
QUALITY_AREA_DEFECTS_COUNT_DU = 2
QUALITY_AREA_DEFECTS_COUNT_DL = 3

DARK_SUPER_AREA_DEFECTS_COUNT_L = 0
DARK_SUPER_AREA_DEFECTS_COUNT_H = 0

DARK_QUALITY_AREA_DEFECTS_COUNT_L = 0
DARK_QUALITY_AREA_DEFECTS_COUNT_H = 1

LOCATION_L = 10
LOCATION_U = 20

LOCATION_X0 = 0
LOCATION_Y0 = 0

SIZE_L = 0.03
SIZE_U = 0.1

# uniformity args
FIXTURE_CA_STABLE_DLY = 0.1
CA_ALG_COUNT = 5

# UNIF_PATTERNS = ['W255', 'W000']
UNIF_PATTERNS = ['W255']
GAMMA_CHECK_GLS = [('P1', 'W000'), ]

CENTER_POINT_POS = 'P1'

TEST_POINTS_POS = [('P1', (0, 0)), ('P2', (0, 18000)), ('P3', (12728, 12728)), ('P4', (18000, 0)),
                   ('P5', (12728, -12728)), ('P6', (0, -18000)),
                   ('P7', (-12728, -12728)), ('P8', (-18000, 0)), ('P9', (-12728, 12728))]

NEIGHBOR_POINTS = [('P1', ['P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9']),
                   ('P2', ['P3', 'P1', 'P9']),
                   ('P3', ['P2', 'P1', 'P4']),
                   ('P4', ['P3', 'P1', 'P5']),
                   ('P5', ['P4', 'P1', 'P6']),
                   ('P6', ['P5', 'P1', 'P7']),
                   ('P7', ['P6', 'P1', 'P8']),
                   ('P8', ['P7', 'P1', 'P9']),
                   ('P9', ['P8', 'P1', 'P2'])]

##################################
# IT and work order
#
FACEBOOK_IT_ENABLED = False
# does the shopfloor use work orders?
USE_WORKORDER_ENTRY = False

EQUIPMENT_DEMO_DATABASE = r'C:\360Downloads\offaxis_2'
CAMERA_SN = "Demo"
# CAMERA_SN = "91738177"
# CAMERA_SN = '94142510'
DUT_SIM = True
EQUIPMENT_SIM = True
FIXTURE_SIM = True
