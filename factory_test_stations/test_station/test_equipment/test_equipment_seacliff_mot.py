import hardware_station_common.test_station.test_equipment
import json
from Conoscope import Conoscope
import time

class seacliffmotEquipmentError(Exception):
    pass

class seacliffmotEquipment(hardware_station_common.test_station.test_equipment.TestEquipment):
    """
        class for project station Equipment
            this is for doing all the specific things necessary to interface with equipment
    """
    def __init__(self, station_config, operator_interface):
        hardware_station_common.test_station.test_equipment.TestEquipment.__init__(self, station_config, operator_interface)
        self.name = "eldim"
        self._verbose = station_config.IS_VERBOSE
        self._station_config = station_config
        self._device = Conoscope()
        self._error_message = self.name + "is out of work"
        self._version = None

## Eldim specific return.
    def _log(self, ret, functionName):
        print("  {0}".format(functionName))

        try:
            # case of return value is a string
            # print("  -> {0}".format(ret))
            returnData = json.loads(ret)
        except:
            # case of return is already a dict
            returnData = ret
        return returnData
        # try:
        #     # display return data
        #     for key, value in returnData.items():
        #         print("      {0:<20}: {1}".format(key, value))
        # except:
        #     print("  invalid return value")

    ########### IDENTIFY SELF ###########

    def version(self):
        if self._version is None:
            ret = self._device.CmdGetVersion()
            self._version = self._log(ret, "CmdGetVersion")
            if self._verbose:
                self._operator_interface.print_to_console("Equipment Version is \n" + str(self._version))
        return self._version

    def is_ready(self):
        pass

    def initialize(self):
        self._operator_interface.print_to_console("Initializing project station Fixture\n")

    def close(self):
        self._operator_interface.print_to_console("Closing project station Fixture\n")

def print_to_console(self, msg):
    pass

if __name__ == "__main__":
    import sys
    sys.path.append("../../")
    import types
    import station_config
    import hardware_station_common.operator_interface.operator_interface
    import station_config

    station_config.load_station('seacliff_mot')
    station_config.print_to_console = types.MethodType(print_to_console, station_config)
    the_equipment = seacliffmotEquipment(station_config, station_config)
    the_equipment.version()