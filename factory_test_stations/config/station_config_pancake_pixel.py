##################################
# directories
#
# Where is the root directory.
# 'factory-test' directory, logs directories, etc will get placed in there.
# (use windows-style paths.)
ROOT_DIR = r'C:\oculus\factory_test_omi\factory_test_stations'
CSV_SUMMARY_DIR = r'C:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\pixel_summary'

##################################
# serial number codes
#
SERIAL_NUMBER_VALIDATION = True  # set to False for debugging
SERIAL_NUMBER_MODEL_NUMBER = r'\dPR0[\d|\w]{10}'  # Fake model number requirement, need config

##################################
# Fixture parameters
# Fixture commands
FIXTURE_COMPORT = "COM2" #
FIXTURE_PARTICLE_COMPORT="COM1" #
FIXTURE_PARTICLE_ADDR=1
DUT_COMPORT = "COM9" #

COMMAND_DISP_HELP = "$c.help"
COMMAND_DISP_VERSION_GRP=['mcu','hw','fpga']
COMMAND_DISP_VERSION = "Version"
COMMAND_DISP_GETBOARDID = "getBoardID"
COMMAND_DISP_POWERON = "DUT.powerOn,FPGA_compressMode"
# COMMAND_DISP_POWERON = "DUT.powerOn,SSD2832_BistMode"
COMMAND_DISP_POWEROFF = "DUT.powerOff"
COMMAND_DISP_RESET = "Reset"
COMMAND_DISP_SETCOLOR = "SetColor"
COMMAND_DISP_SHOWIMAGE = "ShowImage"
COMMAND_DISP_READ = "MIPI.Read"
COMMAND_DISP_WRITE = "MIPI.Write"
COMMAND_DISP_2832WRITE = "t.2832_MIPI_WRITE"
COMMAND_DISP_VSYNC="REFRESHRATE"

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

COMMAND_FIXTURE_INFO = "CMD_FIXTURE_INFORMATION\r\n"
COMMAND_HELP = "CMD_HELP\r\n"
COMMAND_STATUS = "CMD_STATUS\r\n"
COMMAND_INITIALSTATUS = "CMD_INITIALSTATUS\r\n"
COMMAND_RESET = "CMD_RESET\r\n"
COMMAND_LOAD = "CMD_LOAD\r\n"
COMMAND_UNLOAD = "CMD_UNLOAD\r\n"
COMMAND_ID = "CMD_ID\r\n"
COMMAND_BUTTON_ENABLE = "CMD_BUTTON_ENABLE\r\n"
COMMAND_BUTTON_DISABLE = "CMD_BUTTON_DISABLE\r\n"
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

# Fixture Status Enum Values
PTB_POSITION_STATUS = ["Testing Position", "Reset Position", "Outside Position", "Other Position"]
BUTTON_STATUS = ["Enable", "Disable"]
CAMERA_POWER_STATUS = ["Enable", "Disable"]
FIXTURE_PTB_OFF_TIME = 1
FIXTURE_PTB_ON_TIME = 1
FIXTURE_USB_OFF_TIME = 1
FIXTURE_USB_ON_TIME = 1
FIXTURE_PARTICLE_COUNTER = False
FIXTRUE_PARTICLE_ADDR_READ = 40006
FIXTRUE_PARTICLE_ADDR_START = 40003
FIXTRUE_PARTICLE_ADDR_STATUS = 40003
FIXTRUE_PARTICLE_START_DLY = 3
##################################
# shopfloor
#
SHOPFLOOR_SYSTEM = 'Sunny'
# Will we be enforcing shopfloor routing?
ENFORCE_SHOPFLOOR_ROUTING = False
# does the shopfloor use work orders?
#USE_WORKORDER_ENTRY = True

######## DUT Related Parameters which will be defined
DUT_ON_TIME = 4  ## assuming DUT need 5 seconds to be powered after USB powered on command
DUT_DISPLAYSLEEPTIME = 1
DISPLAY_CYCLE_TIME = 2
DUT_RENDER_ONE_IMAGE_TIMEOUT = 0
LAUNCH_TIME = 4
DUT_MAX_WAIT_TIME =60
DEFAULT_VSYNC_US = 13.889 #111.44646  #
DUT_ON_MAXRETRY = 5

##################################
# Test Equipment related parameters
IS_VERBOSE = True
MPKAPI_RELATIVEPATH = r'test_station\test_equipment\MPK_API.dll'
SEQUENCE_RELATIVEPATH = r'test_station\test_equipment\algorithm\y29 particle Defect.seqx'
CALIBRATION_RELATIVEPATH = r'test_station\test_equipment\calibration'
ANALYSIS_RELATIVEPATH = r'factory-test_logs'

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
IS_EXPORT_PNG = True
Resolution_Bin_X_REGISTER = 10
Resolution_Bin_Y_REGISTER = 10
Resolution_REGISTER_SKIPTEXT = 6
Resolution_Bin_X = 10
Resolution_Bin_Y = 10

CAMERA_SN = "91738177"

PATTERNS_BRIGHT = ['W028', 'W048', 'W000']  # the first two are used to register data for bright test.
PATTERNS_DARK = ['W255'] #, "R255", "G255", "B255"]
PATTERNS = ["W028", "W048", "W000", "W255", "R255", "G255", "B255"]
# PATTERNS = ["White","Black","Red","Green","Blue"]
SAVE_IMAGES = [True, True, True, True, True, True, True]
COLORS = [(28, 28, 28), (48, 48, 48), (0, 0, 0), (255, 255, 255),  (255, 0, 0), (0, 255, 0), (0, 0, 255)]
# COLORS = ['0008','0000']
# COLORS = ['1', '2', '3','4','5']
ANALYSIS = ["ParticleDefects W028", "ParticleDefects W048", "ParticleDefects W000", "ParticleDefects W255",
            "ParticleDefects R255", "ParticleDefects G255", "ParticleDefects B255"]
MEASUREMENTS = ["W028", "W048", "W000", "W255", "R255", "G255", "B255"]
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

##################################
# IT and work order
#
FACEBOOK_IT_ENABLED = False
# does the shopfloor use work orders?
USE_WORKORDER_ENTRY = False

EQUIPMENT_DEMO_DATABASE = r'G:\oculus_sunny_t3\pixel'
CAMERA_SN = "Demo"
DUT_SIM = True
EQUIPMENT_SIM = True
FIXTURE_SIM = True
