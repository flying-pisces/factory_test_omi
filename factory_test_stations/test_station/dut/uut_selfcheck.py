import sys
sys.path.append("../")
sys.path.append("../../")
sys.path.append("../../../")
sys.path.append("../../../../")
import time

DUT_DISPLAYSLEEPTIME = 0.5

from displayCtrl import displayCtrlBoard

class DUTError(Exception):
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return repr(self.value)

class pancakeDut(hardware_station_common.test_station.dut.DUT):
    def __init__(self, serialNumber):
        hardware_station_common.test_station.dut.DUT.__init__(self, serialNumber, station_config, operatorInterface)
        self._display_server = None
        self.first_boot = True

    def initialize(self):
        self._display_server = displayCtrlBoard(self._station_config, self._operator_interface) # DisplayServer(custom_adb_path=self._adb_path)
        self._display_server.initialize()
        isinit = self.ptb_booted() and bool(self.ptb_detected()) and bool(self._display_server)#        self._display_server.kill_server()
        return isinit

    def connect_display(self, display_cycle_time=2, launch_time=4):
        if self.first_boot:
            self.first_boot = False
            # this should be set once, but run at least once on boot to ensure system settings are correct
            self._display_server.disable_animations()
            self._display_server.set_screen_timeout()
            self._display_server.set_displayserver_permissions()

        if self._display_server.is_connected() == False:
            self._display_server.connect()
        time.sleep(1)
        self._display_server.screen_off()
        time.sleep(display_cycle_time)
        self._display_server.screen_on()
        time.sleep(display_cycle_time)
        self._display_server.launch_displayserver()
        time.sleep(launch_time)
        return self._display_server.is_connected()

    def disconnect_display(self):
        retval = False
        self.screen_off()
        if self._display_server != None:
            retval = self._display_server.disconnect()
        return retval

    def screen_on(self):
        self._display_server.screen_on()

    def launch_displayserver(self):
        self._display_server.launch_displayserver()

    def close(self):
        self._operator_interface.print_to_console("Turn Off display................\n")
        self._display_server.screen_off()
        self._operator_interface.print_to_console("Closing DUT by killing the server\n")
        self._display_server.kill_server()

    def handle_first_boot_reboot(self):
        if self.first_boot:
            ret, stdout, stderr = self._display_server.reboot()
            self.first_boot = False
            return ret == 0
        return False

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
    '''
    def load_fragment_shader(self, shadername='frag.glsl'):
        self._display_server.load_fragment_shader(shadername)

    def vsync_microseconds(self):
        return self._display_server.get_median_vsync_microseconds()

    def send_data_as_file(self, data, remote_filename):
        self._display_server.send_data_as_file(data, remote_filename)

    def send_file(self, file, remote_filename):
        self._display_server.send_file(file, remote_filename)

    def screen_off(self):
        if self._display_server != None and self._display_server.is_connected():
            self._display_server.screen_off()
    '''
    def ptb_detected(self):
        return len(self._display_server.list_devices())

    def ptb_booted(self):
        return self._display_server.is_ready()

    def get_displayserver_version(self):
        return self._display_server.version()

    def get_os_version(self):
        return self._display_server.get_build_fingerprint()

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
    the_unit = pancakeDut("1HC30000000000")
    the_unit.initialize()
    print the_unit.ptb_detected()
    the_unit.connect_display()
    the_unit.screen_on()
    the_unit.launch_displayserver()
    the_unit.display_color()
    print the_unit.vsync_microseconds()

    FILENAME = "auo_register_33_180_0.png"
    the_unit.display_image(FILENAME)
    time.sleep(2)
    the_unit.displdisplay_color((255, 0, 0))
    the_unit.screen_off()
    time.sleep(5)
    print "Disconnecting display"
    the_unit.disconnect_display()ception):
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return repr(self.value)

class DUT():
    def __init__(self, serialNumber):
        self._display_server = None
        self._adb_path = custom_adb_path
        self.first_boot = True

    def initialize(self):
        self._display_server = DisplayServer(custom_adb_path=self._adb_path)
        isinit = self.ptb_booted() and bool(self.ptb_detected()) and bool(self._display_server)
        self._display_server.kill_server()
        return isinit
        #

    def connect_display(self, display_cycle_time=2, launch_time=4):
        if self.first_boot:
            self.first_boot = False
            # this should be set once, but run at least once on boot to ensure system settings are correct
            self._display_server.disable_animations()
            self._display_server.set_screen_timeout()
            self._display_server.set_displayserver_permissions()

        if self._display_server.is_connected() == False:
            self._display_server.connect()
        time.sleep(1)
        self._display_server.screen_off()
        time.sleep(display_cycle_time)
        self._display_server.screen_on()
        time.sleep(display_cycle_time)
        self._display_server.launch_displayserver()
        time.sleep(launch_time)
        return True

    def disconnect_display(self):
        retval = False
        self.screen_off()
        if self._display_server != None:
            retval = self._display_server.disconnect()
        return retval

    def screen_on(self):
        self._display_server.screen_on()

    def launch_displayserver(self):
        self._display_server.launch_displayserver()

    def close(self):
        print "Turn Off display................"
        self._display_server.screen_off()
        print "Closing DUT by killing the server"
        self._display_server.kill_server()

    def handle_first_boot_reboot(self):
        if self.first_boot:
            ret, stdout, stderr = self._display_server.reboot()
            self.first_boot = False
            return ret == 0
        return False

    def display_color(self, color=(255,255,255)):
        ## color here will be three integers tuple from 0 to 255 represent the RGB value
        ## example: my_ds.display_color((255,0,0))
        self._display_server.display_color(color)
        time.sleep(DUT_DISPLAYSLEEPTIME)

    def display_image(self, image):
        ## image here will be NAME.png under /sdcard/Pictures/
        ## example: my_ds.display_image("auo_red_33_44_0.png")
        self._display_server.display_image(image)
        time.sleep(DUT_DISPLAYSLEEPTIME)

    def load_fragment_shader(self, shadername='frag.glsl'):
        self._display_server.load_fragment_shader(shadername)

    def vsync_microseconds(self):
        return self._display_server.get_median_vsync_microseconds()

    def send_data_as_file(self, data, remote_filename):
        self._display_server.send_data_as_file(data, remote_filename)

    def send_file(self, file, remote_filename):
        self._display_server.send_file(file, remote_filename)

    def screen_off(self):
        if self._display_server != None and self._display_server.is_connected():
            self._display_server.screen_off()

    def ptb_detected(self):
        return len(self._display_server.list_devices())

    def ptb_booted(self):
        return self._display_server.is_ready()

    def get_displayserver_version(self):
        return self._display_server.version()

    def get_os_version(self):
        return self._display_server.get_build_fingerprint()

if __name__ == "__main__":
    SN = "1HC30000000000"
    the_unit = DUT("1HC30000000000")

    isinit = the_unit.initialize()
    print "the unit initialized is : {}".format(isinit)
    print  "the PTB detected totally is : {}".format(the_unit.ptb_detected())
    print  "the PTB booted totally is : {}".format(the_unit.ptb_booted())
    the_unit.connect_display()
    the_unit.screen_on()
    the_unit.launch_displayserver()
    the_unit.get_os_version()
    the_unit.get_displayserver_version()
    print the_unit.vsync_microseconds()
    the_unit.close()

    print  "2nd iter"

    the_unit.connect_display()
    print  "the PTB detected totally is : {}".format(the_unit.ptb_detected())
    print  "the PTB booted totally is : {}".format(the_unit.ptb_booted())
    the_unit.connect_display()
    the_unit.screen_on()
    the_unit.launch_displayserver()
    the_unit.get_os_version()
    the_unit.get_displayserver_version()
    print the_unit.vsync_microseconds()
    the_unit.close()
