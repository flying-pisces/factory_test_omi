"""
Release Note:
========================================================
Version 1.0.1
2022-2-22 elton<elton.tian@myzygroup.com>
-1. Change the schema for ROI to (cent_x, cent_y, half_w, half_h)
-2. Apply the hot-fix for X/Y,
-3. Change the distance for all the points except P1 to sqrt(x**2+y**2+z**2)

========================================================
Version 1.0.0
2022-2-22 elton<elton.tian@myzygroup.com>
-1. Init version for VID
"""
##################################
# directories
#
# Where is the root directory.
# 'factory-test' directory, logs directories, etc will get placed in there.
# (use windows-style paths.)
ROOT_DIR = r'C:\oculus\factory_test_omi\factory_test_stations'
RAW_IMAGE_LOG_DIR = r'C:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\raw'
# RAW_IMAGE_LOG_DIR = r'c:\ShareData\Oculus_RawData'
CSV_SUMMARY_DIR = r'C:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\VID_summary'

##################################
# serial number codes
#
SERIAL_NUMBER_VALIDATION = True  # set to False for debugging
SERIAL_NUMBER_MODEL_NUMBER = '^\w{14}$'  # Fake model number requirement, need config. re.regex

FIXTURE_COMPORT = 'COM2'
DUT_COMPORT = "COM1"
DUT_ETH_PROXY = True
DUT_ETH_PROXY_ADDR = ('192.168.21.132', 6000)

SW_VERSION_SUFFIX = ''
SPEC_VERSION = '0000'

CAMERA_DYNAMIC_LIB = r'C:\oculus\run\R25Config\SimplePython.dll'
# CAMERA_CONFIG = 'C:\oculus\CameraConfig.json'
CAMERA_CONFIG = r'C:\oculus\run\R25Config'
CAMERA_RX_SET = r'C:\oculus\run\R25Config\Facebook Oculus.rxset'
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
COMMAND_PRE_LOAD_TYPE = 'CMD_LOAD_DUT'
COMMAND_UNLOAD = "CMD_UNLOAD"
COMMAND_BUTTON_LITUP_ENABLE = 'CMD_POWERON_BUTTON_ENABLE'
COMMAND_BUTTON_LITUP_DISABLE = 'CMD_POWERON_BUTTON_DISABLE'
COMMAND_LITUP_STATUS = 'CMD_POWERON_BUTTON'
COMMAND_PROBE_BUTTON = 'CMD_PROBE_BUTTON'
FIXTURE_LOAD_DLY = 3
FIXTURE_UNLOAD_DLY = 3
TIMEOUT_FOR_BTN_IDLE = 30

CALIB_Z_BY_STATION_SW = True

TEST_ITEM_PATTERNS = [
    # {'name': 'G180', 'pattern': (1, 0)},
    # {'name': 'G255', 'pattern': (3, 2)},

    {'name': 'G180', 'pattern': (5, 4)},
    {'name': 'G255', 'pattern': (7, 6)},

    # {'name': 'B255', 'pattern': (0, 1)},
    # {'name': 'W127', 'pattern': 6},
    #
    # {'name': 'Audit', 'pattern': 1},
]

# use original HotFix
RAW_HOT_FIX = ['P1']

# sensable text
SENSIBLE_TEXT = {
    'L': {
        'P1': 'center',
        'P2': 'temporal',
        'P4': 'sky',
        'P6': 'nasal',
        'P8': 'ground',
    },
    'R': {
        'P1': 'center',
        'P2': 'nasal',
        'P4': 'sky',
        'P6': 'temporal',
        'P8': 'ground',
    }
}

# schema (cent_x, cent_y, half_w, half_h)
TEST_ITEM_POS = {
    'G180':
        {
            'ROI':
                {
                    'P1': (26.5, -65.5, 91.0, 80.0),
                    'P2': (24.0, 301.5, 91.5, 84),
                    'P4': (502.5, -60.0, 77.0, 86.5),
                    'P6': (31.0, -446.5, 93.0, 89.0),
                    'P8': (-435.0, -61.0, 103.5, 84.0),
                }
        },
    'G255':
        {
            'ROI':
                {
                    'P1': (26.5, -65.5, 91.0, 80.0),
                    'P2': (24.0, 301.5, 91.5, 84),
                    'P4': (502.5, -60.0, 77.0, 86.5),
                    'P6': (31.0, -446.5, 93.0, 89.0),
                    'P8': (-435.0, -61.0, 103.5, 84.0),
                }
        },
    # 'R255':
    #     {
    #         'ROI':
    #             {
    #                 'P1': (8, -92, 70, -58),
    #                 'P2': (12, 69, 77, 247),
    #                 'P4': (232, -96, 346, -53),
    #                 'P6': (9, -388, 77, -304),
    #                 'P8': (-184, -105, -143, -19),
    #             }
    #     },
    # 'W127':
    #     {
    #         'ROI':
    #             {
    #                 'P1': (7, -104, 50, -38),
    #                 'P2': (4, 339, 36, 360),
    #                 'P4': (481, -96, 510, -55),
    #                 'P6': (3, -509, 67, -474),
    #                 'P8': (-440, -96, -397, -36),
    #             }
    #     },
    #
    # 'Audit':
    #     {
    #         'ROI':
    #             {
    #                 'P1': (-9, -76, 110, --2),
    #                 'P2': (13, 301, 56, 348),
    #                 'P4': (409, -72, 458, -23),
    #                 'P6': (10, -455, 60, -420),
    #                 'P8': (-332, -45, -285, -3),
    #             }
    #     },
}

CALIB_DATA = {
    'L': {
        'P1': [(0, 0), (1, 1), (2, 2)],
        'P2': [(0, 0), (1, 1), (2, 2)],
        'P4': [(0, 0), (1, 1), (2, 2)],
        'P6': [(0, 0), (1, 1), (2, 2)],
        'P8': [(0, 0), (1, 1), (2, 2)],
    },
    'R': {
        'P1': [(0, 0), (1, 1), (2, 2)],
        'P2': [(0, 0), (1, 1), (2, 2)],
        'P4': [(0, 0), (1, 1), (2, 2)],
        'P6': [(0, 0), (1, 1), (2, 2)],
        'P8': [(0, 0), (1, 1), (2, 2)],
    }
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
SHOW_CONSOLE = False
# print all data to log-file
IS_PRINT_TO_LOG = False
IS_VERBOSE = True
TEST_CPU_COUNT = 5
#####
### Facebook_IT Enable boolean
FACEBOOK_IT_ENABLED = False
IS_STATION_ACTIVE = True

DUT_SIM = False
EQUIPMENT_SIM = False
FIXTURE_SIM = False

SW_TITLE = 'FactoryTestOMI - SVID'
STATION_TYPE = 'seacliff_vid'
STATION_NUMBER = '0001'

