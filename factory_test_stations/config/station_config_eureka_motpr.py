"""
Release Note:
========================================================
Version 1.0.4
2022-11-09 eason<eason.qian@myzygroup.com>
-1. Update new test flow chat:
             <-------------------------------------------------------------------|cancel test
                                                                                 |
    scan barcode-->put on dut-->vacuum on-->cover board-->off vacuum-->screen on-->start btn on-->press btn and start to test
                                                                             |                                    |
                                                            if screen not on |----------------->finish test <-----|
-2. update shop_floor file, cancel start caller service in station file,use common shop_floor_uni_mes.py file to start caller
    service and connet to service to send/recieve data
-3. update shop_floor_uni_mes file, add mes_helper.exe path to config in station_config file
========================================================
Version 1.0.3
2022-11-01 eason<eason.qian@myzygroup.com>
-1. Update new limits at station_limit_eureka_motpr.py
-2. Off Vacuum when dut go into the fixture
-3. Add MES Func to Sunny Factory and By FACEBOOK_IT_ENABLED attribute to Control if Enable
-4. Save Log File to D:/Oculus/..
========================================================
Version 1.0.2
2022-10-20 eason<eason.qian@myzygroup.com>
-1. Add Bool_Test to Control if test on Station_Config
========================================================
Version 1.0.1
2022-10-14 eason<eason.qian@myzygroup.com>
-1. Init version for MOTPR
"""


##################################
# directories
#
# Where is the root directory.
# 'factory-test' directory, logs directories, etc will get placed in there.
# (use windows-style paths.)
ROOT_DIR = r'D:\Oculus'
RAW_IMAGE_LOG_DIR = r'D:/oculus/factory_test_omi/factory_test_stations/factory-test_logs/Raw'
CSV_SUMMARY_DIR = r'D:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\eureka_mot_summary'
##################################
# serial number codes
#
SERIAL_NUMBER_VALIDATION = False  # set to False for debugging
SERIAL_NUMBER_MODEL_NUMBER = 'H'  # Fake model number requirement, need config. re.regex

SW_VERSION = '1.0.4'

DUT_COMPORT = "COM1" #
DUT_ETH_PROXY = True
DUT_ETH_PROXY_ADDR = ('192.168.21.132', 6000)

# station_type
# STATION_TYPE = 'project_station'
# STATION_NUMBER = 10001
# FULL_TREE_UI = False
#
##################################
#Fixture para
IS_PROXY_COMMUNICATION = True
PROXY_COMMUNICATION_PATH = r"C:\Release\Vision\vision.exe"
PROXY_ENDPOINT = 8099
FIXTURE_COMPORT = "COM18" #
FIXTURE_PARTICLE_COMPORT = "COM16" #
FIXTURE_PARTICLE_COUNTER = False
AUTO_CFG_COMPORTS = True
FIXTURE_PARTICLE_ADDR = 1

DUT_LOAD_WITHOUT_OPERATOR = False

#Command
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
COMMAND_BUTTON_POWEROFF_ENABLE = 'CMD_POWEROFF_BUTTON_ENABLE'
COMMAND_BUTTON_POWEROFF_DISABLE = 'CMD_POWEROFF_BUTTON_DISABLE'
COMMAND_LITUP_STATUS = 'CMD_POWERON_BUTTON'
COMMAND_GET_COVERBOARD_STATUS = 'CMD_GET_COVER_BOARD_STATUS'
COMMAND_QUERY_TEMP = 'CMD_GET_TEMPERATURE'
COMMAND_QUERY_DUT_TEMP = 'CMD_GET_DUT_TEMPERATURE'
COMMAND_PROBE_BUTTON = 'CMD_PROBE_BUTTON'
COMMAND_ZERO_POSIT = 'CMD_ZERO_POSIT'
COMMAND_VACUUM_CTRL = 'CMD_SET_VACUUM'
COMMAND_GET_VACUUM_STATUS = 'CMD_GET_VACUUM_STATUS'
COMMAND_DUT_LOAD = 'CMD_DUT_LOAD'
COMMAND_DUT_UNLOAD = 'CMD_DUT_UNLOAD'
COMMAND_QUERY_TEMP_RANGE = (10, 60)

COMMAND_USB_POWER_ON = "CMD_USB_POWER_ON"
COMMAND_USB_POWER_OFF = "CMD_USB_POWER_OFF"
COMMAND_PTB_POWER_ON = "CMD_PTB_POWER_ON"
COMMAND_PTB_POWER_OFF = "CMD_PTB_POWER_OFF"
COMMAND_STATUS = "CMD_STATUS"

QUERY_DUT_TEMP_PER_PATTERN = True
DUT_LITUP_OUTSIDE = True
TIMEOUT_FOR_BTN_IDLE = 20
FIXTURE_LOAD_DLY = 10
FIXTURE_UNLOAD_DLY = 20
FIXTURE_RESET_DLY = 45
FIXTURE_ALIGNMENT_DLY = 18
FIXTURE_MECH_STABLE_DLY = 0.05
FIXTURE_SOCK_DLY = 0.05
PARTICLE_COUNTER_TIMEOUT = 2

# FIXTRUE_PARTICLE_ADDR_READ = 40006
# FIXTRUE_PARTICLE_ADDR_START = 40003
# FIXTRUE_PARTICLE_ADDR_STATUS = 40003
# PARTICLE_COUNTER_CLJ = False

FIXTRUE_PARTICLE_ADDR_READ = 8
FIXTRUE_PARTICLE_ADDR_START = 30
FIXTRUE_PARTICLE_ADDR_STATUS = 30
PARTICLE_COUNTER_APC = True  # use apc-r210
FIXTRUE_PARTICLE_START_DLY = 0
FIXTURE_QUERY_TEMP_TIMEOUT = 20

# Fixture Status Enum Values
#PTB_POSITION_STATUS = ["Testing Position", "Reset Position", "Outside Position", "Other Position"]
BUTTON_STATUS = ["Enable", "Disable"]
PTB_POSITION_STATUS = ["Enable", "Disable"]
CAMERA_POWER_STATUS = ["Enable", "Disable"]
FIXTURE_PTB_OFF_TIME = 1
FIXTURE_PTB_ON_TIME = 1
FIXTURE_USB_OFF_TIME = 1
FIXTURE_USB_ON_TIME = 1
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
    "SynchMode": 3,     ## Non = 0, Auto = 1, Learn = 2, User = 3
    'Frequency': 90,
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
    'CW255': {
        'P': {'L': 1, 'R': 3},
        'exposure': 1,
        #'Bool_TEST': False
    },
    'CW000': {
        'P': {'L': 0, 'R': 2},
        'exposure': 1,
        #'Bool_TEST': False
    }


}

TEST_POSITIONS = [('Nominal', (0, 0, 15000), ["W255", "R255", "G255", "B255", "CW255", "CW000"])]

SMOOTH_COUNT = 1
NG_CONTINUALLY_ENABLE = True
DUT_SCREEN_ON_RETRYS = 3
##################################
# shopfloor
#
#SHOPFLOOR_SYSTEM = 'uni_mes'
SHOPFLOOR_SYSTEM = 'foxlink'
SHOPFLOOR_DIR = '.'
# Will we be enforcing shopfloor routing?
ENFORCE_SHOPFLOOR_ROUTING = False
# does the shopfloor use work orders?
USE_WORKORDER_ENTRY = False
# dose the shopfloor-script should be loaded every test loop.
SHOP_FLOOR_DBG = False

MES_HELPER_EXE = "mes_helper"
MES_HELPER_EXE_PATH = r"C:\Oculus\run\mes_helper\service\mes_helper.exe"
#MES_HELPER_EXE_PATH = r"D:\桌面\MESHelper\dist\mes_helper_mot\mes_helper_mot.exe"
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

