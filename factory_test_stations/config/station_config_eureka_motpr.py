##################################
# directories
#
# Where is the root directory.
# 'factory-test' directory, logs directories, etc will get placed in there.
# (use windows-style paths.)
ROOT_DIR = r'C:\Oculus'
RAW_IMAGE_LOG_DIR = r'C:/oculus/factory_test_omi/factory_test_stations/factory-test_logs/Raw'
##################################
# serial number codes
#
SERIAL_NUMBER_VALIDATION = False  # set to False for debugging
SERIAL_NUMBER_MODEL_NUMBER = 'H'  # Fake model number requirement, need config. re.regex

DUT_COMPORT = "COM6" #
DUT_ETH_PROXY = True
DUT_ETH_PROXY_ADDR = ('192.168.21.132', 6000)

# station_type
# STATION_TYPE = 'project_station'
# STATION_NUMBER = 10001
# FULL_TREE_UI = False
#

#Command
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

PR788_Config = {
    "Log_Path": r'C:/oculus/factory_test_omi/factory_test_stations/factory-test_logs/PR788',
    "Auto_Exposure": True,
    #"Granularity": 1/9 * 10**6,
    "Oberserve": 2,     ## 2 ~ 10
    "SynchMode": 0,     ## Non = 0, Auto = 1, Learn = 2, User = 3
    "SpeedMode": 0,     ## Normal = 0, Fast = 1, 2xFast = 2, 4xFast = 3
}

TEST_PATTERNS = {
    'W255': {
        'P': (255, 255, 255),
        'spectral': True,
        'exposure': 1
    },
    'R255': {
        'P': (255, 0, 0),
        'exposure': 1
    },
    'G255': {
        'P': (0, 255, 0),
        'exposure': 1
    },
    'B255': {
        'P': (0, 0, 255),
        'exposure': 1
    },
}

TEST_POSITIONS = [('Nominal', (0, 0), ["W255", "R255", "G255", "B255"])]

SMOOTH_COUNT = 3

##################################
# shopfloor
#
SHOPFLOOR_SYSTEM = 'Foxlink'
SHOPFLOOR_DIR = '.'
# Will we be enforcing shopfloor routing?
ENFORCE_SHOPFLOOR_ROUTING = False
# does the shopfloor use work orders?
USE_WORKORDER_ENTRY = True
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

SPECTRAL_MEASURE = True

#####
### Facebook_IT Enable boolean
FACEBOOK_IT_ENABLED = False
USE_WORKORDER_ENTRY = False

IS_STATION_ACTIVE = True
FULL_TREE_UI = True

STATION_TYPE = 'eureka_motpr'
STATION_NUMBER = '0001'

###
###
MIN_SPACE_REQUIRED = [('C:', 1024)]
SW_TITLE = r'OMI TEST STATION (MotPR)'

DUT_SIM = False
EQUIPMENT_SIM = False
FIXTURE_SIM = False

