##################################
# directories
#
# Where is the root directory.
# 'factory-test' directory, logs directories, etc will get placed in there.
# (use windows-style paths.)
ROOT_DIR = r'C:\oculus\factory_test_omi\factory_test_stations'
CSV_SUMMARY_DIR = r'C:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\eeprom_summary'
RAW_IMAGE_LOG_DIR = r'C:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\raw'

##################################
# serial number codes
#
SERIAL_NUMBER_VALIDATION = False  # set to False for debugging
SERIAL_NUMBER_MODEL_NUMBER = '\dPR0[\w|\d]{10}'  # Peak panel SN

##################################
# Fixture parameters
# Fixture commands
PROXY_COMMUNICATION_PATH = r"C:\Version\Release\vision.exe"
IS_PROXY_COMMUNICATION = True
PROXY_ENDPOINT = 8000
FIXTURE_COMPORT = "COM4" #
FIXTURE_PARTICLE_COMPORT = "COM8" #
FIXTURE_PARTICLE_ADDR = 1
DUT_COMPORT = "COM5" #

COMMAND_DISP_HELP = "$c.help"
COMMAND_DISP_VERSION_GRP=['mcu', 'hw', 'fpga']
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
COMMAND_DISP_VSYNC = "REFRESHRATE"
COMMAND_DISP_GET_COLOR = "GetColor"

COMMAND_NVM_WRITE_CNT = 'NVMWCNT'
COMMAND_NVM_READ = 'NVMRead'
COMMAND_NVM_WRITE = 'NVMWrite'

COMMAND_DISP_POWERON_DLY = 1.5
COMMAND_DISP_RESET_DLY = 1
COMMAND_DISP_SHOWIMG_DLY = 0.5
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

##################################
# serial number codes
#
SERIAL_NUMBER_VALIDATION = False  # set to False for debugging
SERIAL_NUMBER_MODEL_NUMBER = 'H'  # Fake model number requirement, need config


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

#####
### Facebook_IT Enable boolean
FACEBOOK_IT_ENABLED = False

# does the shopfloor use work orders?
USE_WORKORDER_ENTRY = False
