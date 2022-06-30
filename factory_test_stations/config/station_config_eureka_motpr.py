##################################
# directories
#
# Where is the root directory.
# 'factory-test' directory, logs directories, etc will get placed in there.
# (use windows-style paths.)
ROOT_DIR = r'C:\Oculus'

##################################
# serial number codes
#
SERIAL_NUMBER_VALIDATION = False  # set to False for debugging
SERIAL_NUMBER_MODEL_NUMBER = 'H'  # Fake model number requirement, need config. re.regex

# station_type
# STATION_TYPE = 'project_station'
# STATION_NUMBER = 10001
# FULL_TREE_UI = False
#

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

#####
### Facebook_IT Enable boolean
FACEBOOK_IT_ENABLED = False
USE_WORKORDER_ENTRY = False

IS_STATION_ACTIVE = True
FULL_TREE_UI = True

STATION_TYPE = 'eureka_motpr'
STATION_NUMBER = '0001'

####
###
MIN_SPACE_REQUIRED = [('C:', 1024)]
SW_TITLE = r'OMI TEST STATION (MotPR)'

DUT_SIM = True
EQUIPMENT_SIM = True
FIXTURE_SIM = True

