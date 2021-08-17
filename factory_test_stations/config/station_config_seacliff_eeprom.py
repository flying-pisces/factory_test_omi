"""
Release Note:
========================================================
Version 1.2.0
2021-8-18 elton<elton.tian@mygyroup.com>
-1. update test items based MOT V1.2.x

========================================================
Version 1.1.4
2021-3-18 elton<elton.tian@mygyroup.com>
-1. keep the unit unable to power on in not testing mode.
-2. add inplace check for module.

========================================================
Version 1.1.3
2021-3-8 elton<elton.tian@mygyroup.com>
-1. read ecc before/after execute write command.
-2. retries automatically when the write count not changed after flushing.
-3. change default exposure time to 400k us

========================================================
Version 1.1.2
2021-2-27 elton<elton.tian@mygyroup.com>
-1. save images captured from CCD.
-2. try to fix bugs about opt_issue with retry strategy.
-3. skip to flash when the data to be write is equal to the data read from device.
-4. add optional to write/read in normal/slow mode for nvm.

========================================================
Version 1.1.1
2021-2-9 author<xxx@xxx.com>
-1. change datetime format to local time.

========================================================
Version 1.1.0
2020-1-18 elton<elton.tian@myzygroup.com>
-1. Init version for EEPROM
"""

##################################
# directories
#
# Where is the root directory.
# 'factory-test' directory, logs directories, etc will get placed in there.
# (use windows-style paths.)
ROOT_DIR = r'C:\oculus\factory_test_omi\factory_test_stations'
CSV_SUMMARY_DIR = r'C:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\seacliff_eeprom_summary'
RAW_IMAGE_LOG_DIR = r'C:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\raw'
CALIB_REQ_DATA_FILENAME = r'c:\oculus\run\seacliff_eeprom\session_data'
##################################
# serial number codes
#
SERIAL_NUMBER_VALIDATION = False  # set to False for debugging
SERIAL_NUMBER_MODEL_NUMBER = '\dPR0[\w]{10}'  # Peak panel SN

##################################
# Fixture parameters
AUTO_CFG_COMPORTS = True
DUT_COMPORT = "COM14"  #

COMMAND_DISP_HELP = "$c.help"
COMMAND_DISP_VERSION_GRP=['mcu', 'hw', 'fpga']
COMMAND_DISP_VERSION = "Version"
COMMAND_DISP_GETBOARDID = "getBoardID"
COMMAND_DISP_POWERON = "DUT.powerOn,DSCMODE"
COMMAND_DISP_POWEROFF = "DUT.powerOff"
COMMAND_DISP_RESET = "Reset"
COMMAND_DISP_SETCOLOR = "SetColor"
COMMAND_DISP_SHOWIMAGE = "ShowImage"
COMMAND_DISP_READ = "MIPI.Read"
COMMAND_DISP_WRITE = "MIPI.Write"
COMMAND_DISP_2832WRITE = "t.2832_MIPI_WRITE"
COMMAND_DISP_VSYNC = "REFRESHRATE"
COMMAND_DISP_GET_COLOR = "GetColor"

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

DUT_DISPLAYSLEEPTIME = 0
DUT_NVRAM_WRITE_TIMEOUT = 10
NVM_WRITE_PROTECT = True
NVM_EEC_READ = True
NVM_WRITE_SLOW_MOD = True
DUT_CHK_MODULE_INPLACE = False

MIN_SPACE_REQUIRED = [('C:', 500)]

CAMERA_CONFIG_FILE = r'C:\oculus\factory_test_omi\factory_test_stations\config\MER-132-43U3C(FQ0200080140).txt'
CAMERA_VERIFY_ENABLE = False
CAMERA_EXPOSURE = 400000
CAMERA_GAIN = 1.0

CAMERA_CHECK_ROI = (400, 260, 820, 650)  # resolution: 1292 * 964
CAMERA_CHECK_CFG = [
    {
        'pattern': (255, 0, 0),
        'chk_lsl': [0, 43, 46],
        'chk_usl': [30, 255, 255],
        'determine':[30, 100],
    },

    # {
    #     'pattern': (0, 255, 0),
    #     'chk_lsl': [80, 90, 46],
    #     'chk_usl': [120, 240, 255],
    #     'determine': None,
    # },
    #
    # {
    #     'pattern': (0, 0, 255),
    #     'chk_lsl': [150, 190, 46],
    #     'chk_usl': [160, 255, 255],
    #     'determine': None,
    # }
]

# blue
# https://blog.csdn.net/a2009374138/article/details/52174856
DISP_CHECKER_L_HsvH = 220
DISP_CHECKER_H_HsvH = 250
DISP_CHECKER_L_HsvS = 0.8
DISP_CHECKER_H_HsvS = 1
DISP_CHECKER_COLOR = (0, 0, 255)
DISP_CHECKER_LOCATION = (25, 5)
DISP_CHECKER_COUNT = 2

NVM_WRITE_COUNT_MAX = 6
# calibration required data.
USER_INPUT_CALIB_DATA = True

CALIB_REQ_DATA = {
    'display_boresight_x': 0.3180896059721896,
    'display_boresight_y': 2.1627223295544993,
    'rotation': -0.915799815681917,

    'lv_W255': 112.040344,
    'x_W255': 0.3228153833300315,
    'y_W255': 0.3285835704813771,

    'lv_R255': 26.819864,
    'x_R255': 0.6666388143079006,
    'y_R255': 0.3152183604502523,

    'lv_G255': 78.019005,
    'x_G255': 0.26605808295858685,
    'y_G255': 0.6448553761160989,

    'lv_B255': 6.2487288,
    'x_B255': 0.15439368793739008,
    'y_B255': 0.04709624165493779,

    'TemperatureW': 37,
    'TemperatureR': 38,
    'TemperatureG': 39,
    'TemperatureB': 40,
    'TemperatureWD': 41,
    'WhitePointGLR': 255,
    'WhitePointGLG': 244,
    'WhitePointGLB': 240,
}

##################################
# shopfloor
#
SHOPFLOOR_SYSTEM = 'Foxlink'
# Will we be enforcing shopfloor routing?
ENFORCE_SHOPFLOOR_ROUTING = False
# does the shopfloor use work orders?
USE_WORKORDER_ENTRY = True

##################################
# station hardware
#
# visa instruments.  Hint: use Agilent VISA tools to make aliases!
# (e.g. "DMM" vs "USB0::2391::1543::MY47007422::0::INSTR")
######## To be config per station type 
IS_VERBOSE = False
IS_PRINT_TO_LOG = False

# UI_MODE
OPTIMIZE_UI_MODE = True
SHOW_CONSOLE = True

#####
### Facebook_IT Enable boolean
FACEBOOK_IT_ENABLED = False

# does the shopfloor use work orders?
USE_WORKORDER_ENTRY = False
DUT_SIM = True
EQUIPMENT_SIM = True
FIXTURE_SIM = True
