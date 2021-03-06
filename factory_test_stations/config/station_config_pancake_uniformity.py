##################################
# directories
#
# Where is the root directory.
# 'factory-test' directory, logs directories, etc will get placed in there.
# (use windows-style paths.)
ROOT_DIR = r'C:\oculus\factory_test_omi\factory_test_stations'
CSV_SUMMARY_DIR = r'C:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\unif_summary'


##################################
# serial number codes
#
SERIAL_NUMBER_VALIDATION = True  # set to False for debugging
SERIAL_NUMBER_MODEL_NUMBER = 'PR0'  # Peak panel SN

##################################
# Fixture parameters
# Fixture commands
FIXTURE_COMPORT = "COM2" #
FIXTURE_PARTICLE_COMPORT = "COM1" #
FIXTURE_PARTICLE_ADDR=1
DUT_COMPORT = "COM4" #

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
PTB_POSITION_STATUS = ["Enable", "Disable"]
CAMERA_POWER_STATUS = ["Enable", "Disable"]
FIXTURE_PTB_OFF_TIME = 1
FIXTURE_PTB_ON_TIME = 1
FIXTURE_USB_OFF_TIME = 1
FIXTURE_USB_ON_TIME = 1
FIXTURE_PARTICLE_COUNTER = False
# FIXTRUE_PARTICLE_ADDR_READ = 40006
# FIXTRUE_PARTICLE_ADDR_START = 40003
# FIXTRUE_PARTICLE_ADDR_STATUS = 40003
FIXTRUE_PARTICLE_ADDR_READ = 8
FIXTRUE_PARTICLE_ADDR_START = 30
FIXTRUE_PARTICLE_ADDR_STATUS = 30
FIXTRUE_PARTICLE_START_DLY = 0
########

######## DUT Related Parameters which will be defined
CUSTOM_ADB_RELATIVE_PATH = r'test_station\dut\adb.exe'
DUT_ON_TIME = 4  ## assuming DUT need 5 seconds to be powered after USB powered on command
DUT_DISPLAYSLEEPTIME = 1
DISPLAY_CYCLE_TIME = 2
DUT_RENDER_ONE_IMAGE_TIMEOUT = 10
LAUNCH_TIME = 4
DUT_MAX_WAIT_TIME =60
DEFAULT_VSYNC_US = 13.8889  # 72  # 111.44646
DUT_ON_MAXRETRY = 5

##################################
# Test Equipment related parameters
IS_VERBOSE = False
MPKAPI_RELATIVEPATH = r'test_station\test_equipment\MPK_API.dll'
SEQUENCE_RELATIVEPATH = r'test_station\test_equipment\algorithm\Myzy_Sequence_10-3-19.seqx'
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
Resolution_Bin_X = 100
Resolution_Bin_Y = 100


# TEST_POINTS = [(0, 0), (0, 18), (12.728, 12.728), (18, 0), (12.728, -12.728), (0, -18),
#                (-12.728, -12.728), (-18, 0), (-12.728, 12.728)]

CENTER_POINT_POS = 'P1'

TEST_POINTS_POS = [('P1', (22, 22)), ('P2', (22, 5)), ('P3', (34, 10)), ('P4', (40, 22)),
                   ('P5', (34, 34)), ('P6', (22, 40)),
                   ('P7', (10, 34)), ('P8', (5, 22)), ('P9', (10, 10))]

NEIGHBOR_POINTS = [('P1', ['P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9']),
                   ('P2', ['P3', 'P1', 'P9']),
                   ('P3', ['P2', 'P1', 'P4']),
                   ('P4', ['P3', 'P1', 'P5']),
                   ('P5', ['P4', 'P1', 'P6']),
                   ('P6', ['P5', 'P1', 'P7']),
                   ('P7', ['P6', 'P1', 'P8']),
                   ('P8', ['P7', 'P1', 'P9']),
                   ('P9', ['P8', 'P1', 'P2'])]

Resolution_Bin_REGISTER_SaveImg = True
Resolution_Bin_REGISTER_THRESH_L = 107
Resolution_Bin_REGISTER_THRESH_H = 255
Resolution_Bin_REGISTER_MIN_AREA = 1000
Resolution_Bin_REGISTER_PATTERN = 'White'
Resolution_Bin_Y_REGISTER = 45
Resolution_Bin_X_REGISTER = 45

Resolution_Bin_SCALE = 10
Resolution_REGISTER_SKIPTEXT = 6

SPECTRAL_RESPONSE = 'PhotoMetric'
CAMERA_SN = "159486608"

# PATTERNS =  ["W255", "W180", 'W127', 'W090', "R255", "G255", "B255"]
PATTERNS = ["W255", 'W127', "R255", "G255", "B255"]
SAVE_IMAGES = [False, False, False, False, False, False, False, False]
# SAVE_IMAGES = [True, True, True, True, True, True, True, True]
COLORS = [(255, 255, 255), (127, 127, 127), (255, 0, 0), (0, 255, 0), (0, 0, 255)]
# COLORS = ['0008', '0001', '0800', '8000', '0010', '0020', '0040']
# COLORS = ['1', '2', '3','4','5']
ANALYSIS = ["MLO_Uniformity W255", "MLO_Uniformity W127", "MLO_Uniformity R255", "MLO_Uniformity G255", "MLO_Uniformity B255"]
MEASUREMENTS = ["W255", 'W127', "R255", "G255", "B255"]
#gamma related
GAMMA_CHECK_GLS = []#["255", "180", "127", "090"]

##################################
# IT and work order
#
FACEBOOK_IT_ENABLED = False
# does the shopfloor use work orders?
USE_WORKORDER_ENTRY = False

EQUIPMENT_DEMO_DATABASE = r'G:\oculus_sunny_t3\unif'
DUT_SIM = True
CAMERA_SN = "Demo"
EQUIPMENT_SIM = True
FIXTURE_SIM = False
