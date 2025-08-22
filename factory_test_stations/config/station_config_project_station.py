##################################
# directories
#
# Where is the root directory.
# 'factory-test' directory, logs directories, etc will get placed in there.
# (cross-platform paths using os.path)
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_SUMMARY_DIR = os.path.join(ROOT_DIR, 'factory-test_logs', 'project_summary')
RAW_DIR = os.path.join(os.path.dirname(ROOT_DIR), 'raw_logs')
##################################
# serial number codes
#
SERIAL_NUMBER_VALIDATION = False  # set to False for debugging
SERIAL_NUMBER_MODEL_NUMBER = r'\dNBS[\d|\w]{10}$'  # Fake model number requirement, need config

ANALYSIS_RELATIVEPATH = r'factory-test_logs'

##################################
# shopfloor
#
SHOPFLOOR_SYSTEM = 'Genius'
# Will we be enforcing shopfloor routing?
ENFORCE_SHOPFLOOR_ROUTING = False
# does the shopfloor use work orders?
# USE_WORKORDER_ENTRY = True
COLORS = [1,2,3,4,5]
##################################
# station hardware
#
# visa instruments.  Hint: use Agilent VISA tools to make aliases!
# (e.g. "DMM" vs "USB0::2391::1543::MY47007422::0::INSTR")
######## To be config per station type 


#####
### Facebook_IT Enable boolean - Disabled for barebone testing
FACEBOOK_IT_ENABLED = False

# does the shopfloor use work orders?
USE_WORKORDER_ENTRY = False

VERSION = 'SunnyP2-PreBuild-Alpha'