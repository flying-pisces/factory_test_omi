##################################
# directories
#
# Where is the root directory.
# 'factory-test' directory, logs directories, etc will get placed in there.
# (use windows-style paths.)
ROOT_DIR = r'C:\oculus\factory_test_omi\factory_test_stations'
CSV_SUMMARY_DIR = r'c:\offaxis_summray'


##################################
# serial number codes
#
SERIAL_NUMBER_VALIDATION = False  # set to False for debugging
SERIAL_NUMBER_MODEL_NUMBER = 'PR0'  # Peak panel SN

##################################
# Fixture parameters
# Fixture commands
FIXTURE_COMPORT = "COM9" #
FIXTURE_PARTICLE_COMPORT = "COM3" #
FIXTURE_PARTICLE_ADDR=1
DUT_COMPORT = "COM5" #

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

COMMAND_DISP_POWERON_DLY = 1.5
COMMAND_DISP_RESET_DLY = 1
COMMAND_DISP_SHOWIMG_DLY = 1
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

COMMAND_HELP = "CMD_HELP\r\n"
COMMAND_STATUS = "CMD_STATUS\r\n"
COMMAND_INITIALSTATUS = "CMD_INITIALSTATUS\r\n"
COMMAND_RESET = "CMD_RESET\r\n"
COMMAND_LOAD = "CMD_LOAD\r\n"
COMMAND_UNLOAD = "CMD_UNLOAD\r\n"
COMMAND_ID = "CMD_ID\r\n"
COMMAND_BUTTON_ENABLE = "CMD_BTN_ENABLE\r\n"
COMMAND_BUTTON_DISABLE = "CMD_BTN_DISABLE\r\n"
COMMAND_FLEX_POWER_ON = "CMD_FLEX_POWER_ON\r\n"
COMMAND_FLEX_POWER_OFF = "CMD_FLEX_POWER_OFF\r\n"
COMMAND_MICROUSB_POWER_ON = "CMD_MICROUSB_POWER_ON\r\n"
COMMAND_MICROUSB_POWER_OFF = "CMD_MICROUSB_POWER_OFF\r\n"
COMMAND_USB_POWER_ON = "CMD_USB_POWER_ON\r\n"
COMMAND_USB_POWER_OFF = "CMD_USB_POWER_OFF\r\n"
COMMAND_PTB_POWER_ON = "CMD_PTB_POWER_ON\r\n"
COMMAND_PTB_POWER_OFF = "CMD_PTB_POWER_OFF\r\n"
COMMAND_RADIANT_POWER_ON = "CMD_RADIANT_POWER_ON\r\n"
COMMAND_RADIANT_POWER_OFF = "CMD_RADIANT_POWER_OFF\r\n"
COMMAND_VERSION = "CMD_VERSION\r\n"
COMMAND_GET_PTB_CURRENT = "CMD_GET_PTB_CURRENT\r\n"
COMMAND_BARCODE = "CMD_BARCODE\r\n"
COMMAND_CLAW_CLOSE = "CMD_CLAW_CLOSE\r\n"
COMMAND_CLAW_OPEN = "CMD_CLAW_OPEN\r\n"
COMMAND_TRAY_DOWN = "CMD_TRAY_DOWN\r\n"
COMMAND_TRAY_UP = "CMD_TRAY_UP\r\n"
COMMAND_BUTTON_LIGHT_ON = "CMD_BUTTON_LIGHT_ON\r\n"
COMMAND_BUTTON_LIGHT_OFF = "CMD_BUTTON_LIGHT_OFF\r\n"
COMMAND_ELIMINATOR_ON = "CMD_ELIMINATOR_ON\r\n"
COMMAND_ELIMINATOR_OFF = "CMD_ELIMINATOR_OFF\r\n"
COMMAND_CARRIER_POSITION = "CMD_LOAD?\r\n"
COMMAND_POGO_UP = "CMD_POGO_UP\r\n"
COMMAND_POGO_DOWN = "CMD_POGO_DOWN\r\n"
COMMAND_ABS_X_Y = "CMD_ABS_X_Y"
COMMAND_RES_X_Y = "CMD_REG_X_Y"
COMMAND_MOTOR_HOME = "CMD_MOTOR_HOME\r\n"

# Fixture Status Enum Values
PTB_POSITION_STATUS = ["Testing Position", "Reset Position", "Outside Position", "Other Position"]
BUTTON_STATUS = ["Enable", "Disable"]
PTB_POSITION_STATUS = ["Enable", "Disable"]
CAMERA_POWER_STATUS = ["Enable", "Disable"]
FIXTURE_PTB_OFF_TIME = 1
FIXTURE_PTB_ON_TIME = 1
FIXTURE_USB_OFF_TIME = 1
FIXTURE_USB_ON_TIME = 1
FIXTURE_PTB_UNLOAD_DLY = 6
FIXTURE_PARTICLE_COUNTER = False
FIXTRUE_PARTICLE_ADDR_READ = 40005
FIXTRUE_PARTICLE_ADDR_START = 40003
FIXTRUE_PARTICLE_ADDR_STATUS = 40003
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
DUT_ON_MAXRETRY = 10

DUT_DISPLAYSLEEPTIME = 1
##################################
# Test Equipment related parameters
IS_VERBOSE = True
MPKAPI_RELATIVEPATH = r'test_station\test_equipment\MPK_API.dll'
SEQUENCE_RELATIVEPATH = r'test_station\test_equipment\algorithm\I16+Conoscope - POI2.seqx'
CALIBRATION_RELATIVEPATH = r'test_station\test_equipment\calibration'

DATABASE_RELATIVEPATH_ACT = r'factory-test_logs'
DATABASE_RELATIVEPATH_BAK = r'factory-test_logs'
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
Resolution_Bin_X = 0
Resolution_Bin_Y = 0
RESTART_TEST_COUNT = 10
DB_MAX_SIZE = 2048

CAMERA_SN = "159496752"

# PATTERNS =  ["W255", "W180", 'W127', 'W090', "R255", "G255", "B255"]
POSITIONS = {'P1':(0, 0),  'P2': (0, 18), 'P4': (18, 0), 'P6': (0, -18), 'P8': (-18, 0)}
PATTERNS = ["W255", "W000", "R255", "G255", "B255"]
SAVE_IMAGES = [False, False, False, False, False]
# SAVE_IMAGES = [True, True, True, True, True, True]
COLORS = [(255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)]
# COLORS = ['0008', '0001', '0800', '8000', '0010']
ANALYSIS = ["Points Of Interest White", "Points Of Interest Black", "Points Of Interest Red", "Points Of Interest Green", "Points Of Interest Blue"]
MEASUREMENTS = ["White", "Black", "Red", "Green", "Blue"]
##################################

BRIGHTNESS_AT_DEG_30 = ['P1', 'P2', 'P3', 'P4']
BRIGHTNESS_AT_DEG_PERCENT_IDS =  ['P1', 'P2', 'P3', 'P4']
BRIGHTNESS_AT_DEG_PERCENT = 16

BRIGHTNESS_AT_DEG_10 = ['P1', 'P2', 'P3', 'P4']
COLORSHIFT_AT_DEG_10 = ['P1', 'P2', 'P3', 'P4']
BRIGHTNESS_AT_DEG_20 = ['P1', 'P2', 'P3', 'P4']
COLORSHIFT_AT_DEG_20 = ['P1', 'P2', 'P3', 'P4']

COLORSHIFT_RATIO_AT_DEG_30 = ['P1', 'P2', 'P3', 'P4']
CR_AT_DEG_30 = ['P1', 'P2', 'P3', 'P4']
CR_AT_DEG_0 = ['P1', 'P2', 'P3', 'P4']

BRIGHTNESS_AT_DEG_PERCENT_IDS = ['P1', 'P2', 'P3', 'P4']




##################################
# IT and work order
#
FACEBOOK_IT_ENABLED = False
# does the shopfloor use work orders?
USE_WORKORDER_ENTRY = False

EQUIPMENT_DEMO_DATABASE = r'C:\360Downloads\1PR01234567890_pancake_offaxis-0_20191203-213526.ttxm'
DUT_SIM = True
EQUIPMENT_SIM = True
FIXTURE_SIM = True
