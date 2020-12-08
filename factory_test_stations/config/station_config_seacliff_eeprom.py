##################################
# directories
#
# Where is the root directory.
# 'factory-test' directory, logs directories, etc will get placed in there.
# (use windows-style paths.)
ROOT_DIR = r'C:\oculus\factory_test_omi\factory_test_stations'
CSV_SUMMARY_DIR = r'C:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\eeprom_summary'
RAW_IMAGE_LOG_DIR = r'C:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\raw'
CALIB_REQ_DATA_JSON_FILENAME = r'c:\oculus\run\seacliff_eeprom\calib_data_biz.json'
##################################
# serial number codes
#
SERIAL_NUMBER_VALIDATION = False  # set to False for debugging
SERIAL_NUMBER_MODEL_NUMBER = '\dPR0[\w|\d]{10}'  # Peak panel SN

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

COMMAND_DISP_POWERON_DLY = 1.5
COMMAND_DISP_RESET_DLY = 1
COMMAND_DISP_SHOWIMG_DLY = 0.5
COMMAND_DISP_POWEROFF_DLY = 0.2

DUT_DISPLAYSLEEPTIME = 0.5
DUT_NVRAM_WRITE_TIMEOUT = 10
NVM_WRITE_PROTECT = True

CAMERA_CONFIG_FILE = r'C:\oculus\factory_test_omi\factory_test_stations\config\MER-132-43U3C(FQ0200080140).txt'
CAMERA_VERIFY_ENABLE = False
CAMERA_EXPOSURE = 80000
CAMERA_GAIN = 1.0

CAMERA_CHECK_ROI = (400, 260, 820, 650)  # resolution: 1292 * 964
CAMERA_CHECK_CFG = [
    {
        'pattern': (255, 0, 0),
        'chk_lsl': [0, 43, 46],
        'chk_usl': [30, 255, 255],
        'determine':[50, 100],
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

##################################
# serial number codes
#
SERIAL_NUMBER_VALIDATION = False  # set to False for debugging
SERIAL_NUMBER_MODEL_NUMBER = 'H'  # Fake model number requirement, need config

NVM_WRITE_COUNT_MAX = 6
# calibration required data.
USER_INPUT_CALIB_DATA = False

CALIB_REQ_DATA = {
    'display_boresight_x': 100.20,
    'display_boresight_y': -120.25,
    'rotation': -0.8,

    'lv_W255': 80,
    'x_W255': 0.3001,
    'y_W255': 0.3002,

    'lv_R255': 100,
    'x_R255': 0.654,
    'y_R255': 0.321,

    'lv_G255': 30,
    'x_G255': 0.3001,
    'y_G255': 0.6002,

    'lv_B255': 50,
    'x_B255': 0.1402,
    'y_B255': 0.0405,
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

#####
### Facebook_IT Enable boolean
FACEBOOK_IT_ENABLED = False

# does the shopfloor use work orders?
USE_WORKORDER_ENTRY = False
DUT_SIM = True
EQUIPMENT_SIM = True
FIXTURE_SIM = True
