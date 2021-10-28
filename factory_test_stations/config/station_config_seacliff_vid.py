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
IS_VERBOSE = False

#####
### Facebook_IT Enable boolean
FACEBOOK_IT_ENABLED = False

