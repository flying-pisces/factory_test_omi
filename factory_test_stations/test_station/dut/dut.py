import hardware_station_common.test_station.dut
import os
import time
# from test_station.dut.displayserver import DisplayServer
from displayCtrl import displayCtrlBoard

class DUTError(Exception):
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return repr(self.value)

class pancakeDut(hardware_station_common.test_station.dut.DUT):
    def __init__(self, serialNumber, station_config, operatorInterface):
        hardware_station_common.test_station.dut.DUT.__init__(self, serialNumber, station_config, operatorInterface)
        self._display_server = None
        self.first_boot = True

    def initialize(self):
        self._display_server = displayCtrlBoard(self._station_config, self._operator_interface) # DisplayServer(custom_adb_path=self._adb_path)
        return self._display_server.initialize()

    def connect_display(self, display_cycle_time=2, launch_time=4):
        if self.first_boot:
            self.first_boot = False
            self._display_server.screen_on()
            time.sleep(display_cycle_time)
        return True

    def screen_on(self):
        self._display_server.screen_on()

    def screen_off(self):
        self._display_server.screen_off()

    def close(self):
        self._operator_interface.print_to_console("Turn Off display................\n")
        self._display_server.screen_off()
        self._operator_interface.print_to_console("Closing DUT by the communication interface.\n")
        self._display_server.close()

    def display_color(self, color=(255,255,255)):
        ## color here will be three integers tuple from 0 to 255 represent the RGB value
        ## example: my_ds.display_color((255,0,0))
        self._display_server.display_color(color)
        time.sleep(self._station_config.DUT_DISPLAYSLEEPTIME)

    def display_image(self, image):
        ## image here will be NAME.png under /sdcard/Pictures/
        ## example: my_ds.display_image("auo_red_33_44_0.png")
        self._display_server.display_image(image)
        time.sleep(self._station_config.DUT_DISPLAYSLEEPTIME)

    def vsync_microseconds(self):
        # return self._station_config.DEFAULT_VSYNC_US
        return self._display_server.get_median_vsync_microseconds()

    def get_displayserver_version(self):
        return self._display_server.version()

############ projectDut is just an example
class projectDut(hardware_station_common.test_station.dut.DUT):
    """
        class for pancake uniformity DUT
            this is for doing all the specific things necessary to DUT
    """
    def __init__(self, serial_number, station_config, operator_interface):
        hardware_station_common.test_station.dut.DUT.__init__(self, serial_number, station_config, operator_interface)

    def is_ready(self):
        pass

    def initialize(self):
        self._operator_interface.print_to_console("Initializing pancake uniformity Fixture\n")

    def close(self):
        self._operator_interface.print_to_console("Closing pancake uniformity Fixture\n")

if __name__ == "__main__" :
    import sys
    sys.path.append(r'..\..')
    import dutTestUtil
    import station_config
    import logging
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logging.getLogger(__name__).addHandler(ch)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    station_config.load_station('pancake_pixel')
    # station_config.load_station('pancake_uniformity')
    operator = dutTestUtil.simOperator()
    the_unit = pancakeDut('COM1', station_config, operator)
    the_unit.initialize()
    the_unit.connect_display()
    the_unit.screen_on()
    time.sleep(1)
    the_unit.display_color()
    time.sleep(1)
    print the_unit.vsync_microseconds()
    for c in [(255,0,0), (0,255,0), (0,0,255)]:
        the_unit.display_color(c)
        time.sleep(0.5)

    time.sleep(2)
    the_unit.screen_off()
    the_unit.close()