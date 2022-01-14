##################################
# directories
#
# Where is the root directory.
# 'factory-test' directory, logs directories, etc will get placed in there.
# (use windows-style paths.)
ROOT_DIR = r'C:\oculus\factory_test_omi\factory_test_stations'
RAW_IMAGE_LOG_DIR = r'C:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\raw'
RAW_IMAGE_LOG_DIR = r'c:\ShareData\Oculus_RawData'

##################################
# serial number codes
#
SERIAL_NUMBER_VALIDATION = False  # set to False for debugging
SERIAL_NUMBER_MODEL_NUMBER = 'H'  # Fake model number requirement, need config. re.regex

FIXTURE_COMPORT = 'COM2'
DUT_COMPORT = "COM1"
DUT_ETH_PROXY = True
DUT_ETH_PROXY_ADDR = ('192.168.21.132', 6000)

SW_VERSION_SUFFIX = ''
SPEC_VERSION = '0000'

CAMERA_DYNAMIC_LIB = r'C:\oculus\SimplePython.dll'
CAMERA_CONFIG = 'C:\oculus\CameraConfig.json'
CAMERA_RX_SET = 'C:\oculus\Facebook Oculus.rxset'
# CAMERA_RX_SET = 'C:\oculus\OculusDensePointMap.rxset'

# DUT COMMAND
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

COMMAND_DISP_POWERON_DLY = 0.5
COMMAND_DISP_RESET_DLY = 1
COMMAND_DISP_SHOWIMG_DLY = 0.01
COMMAND_DISP_POWEROFF_DLY = 0
COMMAND_DISP_REBOOT_DLY = 4
DUT_DISPLAYSLEEPTIME = 0.025

# COMMAND for fixture
COMMAND_HELP = 'CMD_HELP'
COMMAND_ID = 'CMD_ID'
COMMAND_VERSION = 'CMD_VERSION'
COMMAND_BUTTON_ENABLE = 'CMD_START_BUTTON_ENABLE'
COMMAND_BUTTON_DISABLE = 'CMD_START_BUTTON_DISABLE'
COMMAND_RESET = 'CMD_RESET'
COMMAND_STATUS_LIGHT_ON = 'CMD_STATUS_LIGHT_ON'
COMMAND_STATUS_LIGHT_OFF = 'CMD_STATUS_LIGHT_OFF'
COMMAND_LOAD = "CMD_LOAD"
COMMAND_UNLOAD = "CMD_UNLOAD"
COMMAND_BUTTON_LITUP_ENABLE = 'CMD_POWERON_BUTTON_ENABLE'
COMMAND_BUTTON_LITUP_DISABLE = 'CMD_POWERON_BUTTON_DISABLE'
COMMAND_LITUP_STATUS = 'CMD_POWERON_BUTTON'
COMMAND_PROBE_BUTTON = 'CMD_PROBE_BUTTON'
FIXTURE_LOAD_DLY = 3
FIXTURE_UNLOAD_DLY = 3
TIMEOUT_FOR_BTN_IDLE = 20
FIXTURE_SOCK_DLY = 0.05

CALIB_Z_BY_STATION_SW = False

TEST_ITEM_PATTERNS = [
    {'name': 'W255', 'pattern': 0},
    {'name': 'W000', 'pattern': 1},
    {'name': 'R255', 'pattern': 2},
    {'name': 'G255', 'pattern': 3},
    {'name': 'B255', 'pattern': 4},
]

TEST_ITEM_POS = {
    'W255':
        {
            'ROI':
                {
                    'P1': (23, -79, 107, -8),
                    'P2': (23, 269, 105, 340),
                    'P4': (383, -92, 470, -16),
                    'P6': (42, -451, 125, -373),
                    'P8': (-313, -61, -232, 4),
                }
        },
}

##################################
# shopfloor
#
SHOPFLOOR_SYSTEM = 'Foxlink'
# Will we be enforcing shopfloor routing?
ENFORCE_SHOPFLOOR_ROUTING = False
# does the shopfloor use work orders?
USE_WORKORDER_ENTRY = False
# dose the shopfloor-script should be loaded every test loop.
SHOP_FLOOR_DBG = False

##################################
# station hardware
#
# visa instruments.  Hint: use Agilent VISA tools to make aliases!
# (e.g. "DMM" vs "USB0::2391::1543::MY47007422::0::INSTR")
######## To be config per station type 

################################
# optimize
# use multi-thread to save UI dead-lock.
OPTIMIZE_UI_MODE = True
# show console when running seperately.
SHOW_CONSOLE = True
# print all data to log-file
IS_PRINT_TO_LOG = False
IS_VERBOSE = True
TEST_CPU_COUNT = 5
#####
### Facebook_IT Enable boolean
FACEBOOK_IT_ENABLED = False

DUT_SIM = True
EQUIPMENT_SIM = True
FIXTURE_SIM = True

