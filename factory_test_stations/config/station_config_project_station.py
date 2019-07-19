##################################
# directories
#
# Where is the root directory.
# 'factory-test' directory, logs directories, etc will get placed in there.
# (use windows-style paths.)
ROOT_DIR = r'C:\projects\Pancake\factory_test_omi'

##################################
# serial number codes
#
SERIAL_NUMBER_VALIDATION = False  # set to False for debugging
SERIAL_NUMBER_MODEL_NUMBER = 'H'  # Fake model number requirement, need config


##################################
# shopfloor
#
SHOPFLOOR_SYSTEM = 'Sunny'
# Will we be enforcing shopfloor routing?
ENFORCE_SHOPFLOOR_ROUTING = False
# does the shopfloor use work orders?
# USE_WORKORDER_ENTRY = True

##################################
# station hardware
#
# visa instruments.  Hint: use Agilent VISA tools to make aliases!
# (e.g. "DMM" vs "USB0::2391::1543::MY47007422::0::INSTR")
######## To be config per station type 


#####
### Facebook_IT Enable boolean
FACEBOOK_IT_ENABLED = False

# does the shopfloor use work orders?
USE_WORKORDER_ENTRY = False
