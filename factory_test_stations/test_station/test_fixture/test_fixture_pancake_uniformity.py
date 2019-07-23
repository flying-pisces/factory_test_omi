import hardware_station_common.test_station.test_fixture
import os
import sys
### Below two lines will be used for debug.
sys.path.append("../")
import glob
import serial
import serial.tools.list_ports
import time
import math

class pancakeuniformityFixtureError(Exception):
    pass

class pancakeuniformityFixture(hardware_station_common.test_station.test_fixture.TestFixture):
    """
        class for auo unif Fixture
            this is for doing all the specific things necessary to interface with instruments
    """
    def __init__(self, station_config, operator_interface):
        hardware_station_common.test_station.test_fixture.TestFixture.__init__(self, station_config, operator_interface)
        self._serial_port = None
        self._verbose = None
        self._start_delimiter = ':'
        self._end_delimiter = '\r\n'
        self._error_msg = 'This command is illegal,please check it again'
        self._read_error = False
        # status of the platform
        self.PTB_Position = None
        self._Button_Status = None
        self._PTB_Power_Status = None
        self._USB_Power_Status = None
        self.equipment = None

    def is_ready(self):
        pass

    def initialize(self):
        self._operator_interface.print_to_console("Initializing auo uniformity Fixture\n")
        self._serial_port = serial.Serial(self._station_config.FIXTURE_COMPORT,
                                          115200,
                                          parity='N',
                                          stopbits=1,
                                          timeout=1,
                                          xonxoff=0,
                                          rtscts=0)
        if not self._serial_port:
            raise pancakeuniformityFixtureError('Unable to open fixture port: %s' % self._station_config.FIXTURE_COMPORT)
            return False
        else:
            print "Fixture %s Initialized" % self._station_config.FIXTURE_COMPORT
            if self._PTB_Power_Status != '0':
                self.poweron_ptb()
                self._operator_interface.print_to_console("Power on PTB {}\n".format(self._PTB_Power_Status))
            if self._USB_Power_Status != '0':
                self.poweron_usb()
                self._operator_interface.print_to_console("Power on USB {}\n".format(self._USB_Power_Status))
        isinit = bool(self._serial_port) and not bool(int(self._PTB_Power_Status)) and not bool(int(self._USB_Power_Status))
        return isinit

    def _parsing_response(self, response):
        value = []
        for item in response[1:len(response) - 1]:
            value.append((item.split(self._start_delimiter))[1].split(self._end_delimiter)[0])
        return value

    def _write_serial(self, input_bytes):
        if self._verbose:
            print('writing: ' + input_bytes)
        bytes_written = self._serial_port.write(input_bytes)
        if self._verbose:
            print("wrote, flushing")
        self._serial_port.flush()
        if self._verbose:
            print("flushed")
        return bytes_written

    def _read_response(self):
        response = []
        line_in = ""
        while (line_in != "@_@"):
            line_in = self._serial_port.readline()
            if (line_in != ""):
                response.append(line_in)
        return response

    ######################
    # Fixture info
    ######################
    def status(self):
        self._write_serial(self._station_config.COMMAND_STATUS)
        response = self._read_response()
        print response
        value = self._parsing_response(response)
        self.PTB_Position = int(value[0])
        self._Button_Status = int(value[1])
        self._PTB_Power_Status = int(value[2])
        self._USB_Power_Status = int(value[6])
        return response

    def help(self):
        self._write_serial(self._station_config.COMMAND_HELP)
        response = self._read_response()
        print response
        return response

    def reset(self):
        self._write_serial(self._station_config.COMMAND_RESET)
        response = self._read_response()
        print(response[1])
        value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
        return value

    def id(self):
        self._write_serial(self._station_config.COMMAND_ID)
        response = self._read_response()
        print(response[1])
        value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
        return value

    def version(self):
        self._write_serial(self._station_config.COMMAND_VERSION)
        response = self._read_response()
        print(response[1])
        value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
        return value

    def close(self):
        self._operator_interface.print_to_console("Closing auo unif Fixture\n")
        if hasattr(self, '_serial_port') and self._station_config.FIXTURE_COMPORT:
            self._serial_port.close()
            self._serial_port = None
            print "====== Fixture Close ========="
        return True

    ######################
    # Fixture control
    ######################

    def elminator_on(self):
        self._write_serial(self._station_config.COMMAND_ELIMINATOR_ON)
        #time.sleep(CARRIER_LOAD_TIME)
        response = self._read_response()
        print(response[1])
        if "0" in response[1]:
            value = 0
        elif self._error_msg not in response[1]:
            value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
        else:
            value = None
            self._read_error = "True"
            raise pancakeuniformityFixtureError("Fail to Read %s" % response[0])
        return value

    def elminator_off(self):
        self._write_serial(self._station_config.COMMAND_ELIMINATOR_OFF)
        #time.sleep(CARRIER_LOAD_TIME)
        response = self._read_response()
        print(response[1])
        if "0" in response[1]:
            value = 0
        elif self._error_msg not in response[1]:
            value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
        else:
            value = None
            self._read_error = "True"
            raise pancakeuniformityFixtureError("Fail to Read %s" % response[0])
        return value

    def load(self):
        self._write_serial(self._station_config.COMMAND_LOAD)
        #time.sleep(CARRIER_LOAD_TIME)
        response = self._read_response()
        print(response[1])
        if "0" in response[1]:
            value = 0
        elif self._error_msg not in response[1]:
            value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
        else:
            value = None
            self._read_error = "True"
            raise pancakeuniformityFixtureError("Fail to Read %s" % response[0])
        return value

    def unload(self):
        self._write_serial(self._station_config.COMMAND_UNLOAD)
        #time.sleep(CARRIER_UNLOAD_TIME)
        response = self._read_response()
        print(response[1])
        if "0" in response[1]:  ## temporary fix for FW1.0.20161114
            value = 0
        elif self._error_msg not in response[1]:
            value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
        else:
            value = None
            self._read_error = "True"
            raise pancakeuniformityFixtureError("Fail to Read %s" % response[0])
        return value

    def scan_serial(self):
        self._write_serial(self._station_config.COMMAND_BARCODE)
        #time.sleep(BARCODE_TIME)
        response = self._read_response()
        print(response[1])
        if self._error_msg not in response[1]:
            value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
        else:
            value = None
            self._read_error = "True"
            raise pancakeuniformityFixtureError("Fail to Read %s" % response[0])
        return value

    def poweron_usb(self):
        self._write_serial(self._station_config.COMMAND_USB_POWER_ON)
        time.sleep(self._station_config.FIXTURE_USB_ON_TIME)
        response = self._read_response()
        print(response[1])
        if self._error_msg not in response[1]:
            value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
            self._USB_Power_Status = value
        else:
            value = None
            self._read_error = "True"
            raise pancakeuniformityFixtureError("Fail to Read %s" % response[0])
        return value

    def poweroff_usb(self):
        self._write_serial(self._station_config.COMMAND_USB_POWER_OFF)
        time.sleep(self._station_config.FIXTURE_USB_OFF_TIME)
        response = self._read_response()
        print(response[1])
        if self._error_msg not in response[1]:
            value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
            self._USB_Power_Status = value
        else:
            value = None
            self._read_error = "True"
            raise pancakeuniformityFixtureError("Fail to Read %s" % response[0])
        return value


    def poweron_ptb(self):
        self._write_serial(self._station_config.COMMAND_PTB_POWER_ON)
        time.sleep(self._station_config.FIXTURE_PTB_ON_TIME)
        response = self._read_response()
        print(response[1])
        if self._error_msg not in response[1]:
            value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
            self._PTB_Power_Status = value
        else:
            value = None
            self._read_error = "True"
            raise pancakeuniformityFixtureError("Fail to Read %s" % response[0])
        return value

    def poweroff_ptb(self):
        self._write_serial(self._station_config.COMMAND_PTB_POWER_OFF)
        time.sleep(self._station_config.FIXTURE_PTB_OFF_TIME)
        response = self._read_response()
        print(response[1])
        if self._error_msg not in response[1]:
            value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
            self._PTB_Power_Status = value
        else:
            value = None
            self._read_error = "True"
            raise pancakeuniformityFixtureError("Fail to Read %s" % response[0])
        return value

    def powercycle_dut(self):
        self._write_serial(self._station_config.COMMAND_USB_POWER_OFF)
        time.sleep(self._station_config.FIXTURE_USB_OFF_TIME)
        self._write_serial(self._station_config.COMMAND_PTB_POWER_OFF)
        time.sleep(self._station_config.FIXTURE_PTB_OFF_TIME)
        self._write_serial(self._station_config.COMMAND_PTB_POWER_ON)
        time.sleep(self._station_config.FIXTURE_PTB_ON_TIME)
        self._write_serial(self._station_config.COMMAND_USB_POWER_ON)
        time.sleep(self._station_config.FIXTURE_USB_ON_TIME + self._station_config.DUT_ON_TIME)
        response = self._read_response()
        print(response[1])
        if self._error_msg not in response[1]:
            value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
        else:
            value = None
            self._read_error = "True"
            raise pancakeuniformityFixtureError("Fail to Read %s" % response[0])
        return value
    ######################
    # Fixture button system control
    ######################
    def button_enable(self):
        self._write_serial(self._station_config.COMMAND_BUTTON_ENABLE)
        response = self._read_response()
        print(response[1])
        if self._error_msg not in response[1]:
            value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
        else:
            value = None
            self._read_error = "True"
            raise pancakeuniformityFixtureError("Fail to Read %s" % response[0])
        return value

    def button_disable(self):
        self._write_serial(self._station_config.COMMAND_BUTTON_DISABLE)
        response = self._read_response()
        print(response[1])
        if self._error_msg not in response[1]:
            value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
        else:
            value = None
            self._read_error = "True"
            raise pancakeuniformityFixtureError("Fail to Read %s" % response[0])
        return value

if __name__ == "__main__":
        sys.path.append("../../")
        import dutTestUtil
        import station_config
        import hardware_station_common.operator_interface.operator_interface

        print 'Self check for pancake_uniformity'
        station_config.load_station('pancake_uniformity')
        operator = dutTestUtil.simOperator()
        the_fixture = pancakeuniformityFixture(station_config, operator)

        the_fixture.initialize()
        the_fixture.reset()

        the_fixture.unload()
        time.sleep(1)
        the_fixture.load()

        the_fixture.close()