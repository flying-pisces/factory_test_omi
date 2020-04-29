import hardware_station_common.test_station.test_fixture
import os
import sys
### Below two lines will be used for debug.
sys.path.append("../")
import glob
import serial
import serial.tools.list_ports
import time
import re
import pprint
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.register_write_message import WriteSingleRegisterResponse
from pymodbus.register_read_message import ReadHoldingRegistersResponse
from pymodbus.constants import Defaults
import time
import ctypes

class pancakepixelFixtureError(Exception):
    pass

class pancakepixelFixture(hardware_station_common.test_station.test_fixture.TestFixture):
    """
        class for auo unif Fixture
            this is for doing all the specific things necessary to interface with instruments
    """
    def __init__(self, station_config, operator_interface):
        hardware_station_common.test_station.test_fixture.TestFixture.__init__(self, station_config, operator_interface)
        self._serial_port = None
        self._verbose = station_config.IS_VERBOSE
        self._start_delimiter = ':'
        self._end_delimiter = '\r\n'
        self._error_msg = 'This command is illegal,please check it again'
        self._read_error = False
        self._particle_counter_client = None  # type: ModbusSerialClient

    def is_ready(self):
        if self._serial_port is not None:
            resp = self._read_response(2)
            btn_dic = {2 : r'BUTTON_LEFT:\d', 1 : r'BUTTON_RIGHT:\d', 0 : r'BUTTON:\d'}
            if resp:
                for key, item in btn_dic.items():
                    items = filter(lambda r: re.match(item, r, re.I), resp)
                    if items:
                        return key

    def initialize(self):
        self._operator_interface.print_to_console("Initializing Fixture\n")
        self._serial_port = serial.Serial(self._station_config.FIXTURE_COMPORT,
                                          115200,
                                          parity='N',
                                          stopbits=1,
                                          timeout=1,
                                          xonxoff=0,
                                          rtscts=0)
        if self._station_config.FIXTURE_PARTICLE_COUNTER:
                parity = 'N'
                Defaults.Retries = 5
                Defaults.RetryOnEmpty = True
                self._particle_counter_client = ModbusSerialClient(method='rtu', baudrate=9600, bytesize=8, parity=parity,
                                                                   stopbits=1,
                                                                   port=self._station_config.FIXTURE_PARTICLE_COMPORT,
                                                                   timeout=2000)
                if not self._particle_counter_client.connect():
                    raise pancakepixelFixtureError( 'Unable to open particle counter port: %s'
                                                    % self._station_config.FIXTURE_PARTICLE_COMPORT)

        if not self._serial_port:
            raise pancakepixelFixtureError('Unable to open fixture port: %s' % self._station_config.FIXTURE_COMPORT)
        else:
            self._operator_interface.print_to_console("Fixture %s Initialized.\n" % self._station_config.FIXTURE_COMPORT)
            return True

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

    def _read_response(self, timeout=5):
        response = []
        line_in = ""
        tim = time.time()
        while (not re.search("@_@", line_in, re.IGNORECASE)
               and (time.time() - tim < timeout)):
            line_in = self._serial_port.readline()
            if line_in != "":
                response.append(line_in)
        if self._verbose and len(response) > 1:
            pprint.pprint(response)
        return response

    ######################
    # Fixture info
    ######################

    def help(self):
        self._write_serial(self._station_config.COMMAND_HELP)
        response = self._read_response()
        if self._verbose:
            print response
        return response

    def reset(self):
        self._write_serial(self._station_config.COMMAND_RESET)
        response = self._read_response()
        if self._verbose:
            print(response[1])
        value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
        return value

    def id(self):
        self._write_serial(self._station_config.COMMAND_ID)
        response = self._read_response()
        if self._verbose:
            print(response[1])
        value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
        return value

    def version(self):
        self._write_serial(self._station_config.COMMAND_VERSION)
        response = self._read_response()
        if self._verbose:
            print(response[1])
        value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
        return value

    def close(self):
        self._operator_interface.print_to_console("Closing auo pixel Fixture\n")
        if hasattr(self, '_serial_port') \
                and self._serial_port is not None \
                and self._station_config.FIXTURE_COMPORT:
            self.elminator_off()
            self._serial_port.close()
            self._serial_port = None
        if hasattr(self, '_particle_counter_client') and \
                self._particle_counter_client is not None \
                and self._station_config.FIXTURE_PARTICLE_COUNTER:
            self._particle_counter_client.close()
            self._particle_counter_client = None
        if self._verbose:
            print "====== Fixture Close ========="
        return True

    ######################
    # Fixture control
    ######################

    def elminator_on(self):
        self._write_serial(self._station_config.COMMAND_ELIMINATOR_ON)
        #time.sleep(CARRIER_LOAD_TIME)
        response = self._read_response()
        if self._verbose:
            print(response[1])
        if "0" in response[1]:
            value = 0
        elif self._error_msg not in response[1]:
            value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
        else:
            value = None
            self._read_error = "True"
            raise pancakepixelFixtureError("Fail to Read %s" % response[0])
        return value

    def elminator_off(self):
        self._write_serial(self._station_config.COMMAND_ELIMINATOR_OFF)
        #time.sleep(CARRIER_LOAD_TIME)
        response = self._read_response()
        if self._verbose:
            print(response[1])
        if "0" in response[1]:
            value = 0
        elif self._error_msg not in response[1]:
            value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
        else:
            value = None
            self._read_error = "True"
            raise pancakepixelFixtureError("Fail to Read %s" % response[0])
        return value

    def load(self):
        self._write_serial(self._station_config.COMMAND_LOAD)
        #time.sleep(CARRIER_LOAD_TIME)
        response = self._read_response()
        if self._verbose:
            print(response[1])
        if "0" in response[1]:
            value = 0
        elif self._error_msg not in response[1]:
            value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
        else:
            value = None
            self._read_error = "True"
            raise pancakepixelFixtureError("Fail to Read %s" % response[0])
        return value

    def unload(self):
        self._write_serial(self._station_config.COMMAND_UNLOAD)
        #time.sleep(CARRIER_UNLOAD_TIME)
        response = self._read_response()
        if self._verbose:
            print(response[1])
        if "0" in response[1]:  ## temporary fix for FW1.0.20161114
            value = 0
        elif self._error_msg not in response[1]:
            value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
        else:
            value = None
            self._read_error = "True"
            raise pancakepixelFixtureError("Fail to Read %s" % response[0])
        return value

    def scan_serial(self):
        self._write_serial(self._station_config.COMMAND_BARCODE)
        #time.sleep(BARCODE_TIME)
        response = self._read_response()
        if self._verbose:
            print(response[1])
        if self._error_msg not in response[1]:
            value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
        else:
            value = None
            self._read_error = "True"
            raise pancakepixelFixtureError("Fail to Read %s" % response[0])
        return value

    ######################
    # Fixture button system control
    ######################
    def button_enable(self):
        self._write_serial(self._station_config.COMMAND_BUTTON_ENABLE)
        response = self._read_response()
        if self._verbose:
            print(response[1])
        if self._error_msg not in response[1]:
            value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
        else:
            value = None
            self._read_error = "True"
            raise pancakepixelFixtureError("Fail to Read %s" % response[0])
        return value

    def button_disable(self):
        self._write_serial(self._station_config.COMMAND_BUTTON_DISABLE)
        response = self._read_response()
        if self._verbose:
            print(response[1])
        if self._error_msg not in response[1]:
            value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
        else:
            value = None
            self._read_error = "True"
            raise pancakepixelFixtureError("Fail to Read %s" % response[0])
        return value

    ######################
    # Particle Counter Control
    ######################
    def particle_counter_on(self):
        if self._particle_counter_client is not None:
            wrs = self._particle_counter_client.\
                write_register(self._station_config.FIXTRUE_PARTICLE_ADDR_START,
                               1, unit=self._station_config.FIXTURE_PARTICLE_ADDR)
            if wrs is None or wrs.isError():
                raise pancakepixelFixtureError('Failed to start particle counter .')

    def particle_counter_off(self):
        if self._particle_counter_client is not None:
            self._particle_counter_client. write_register(self._station_config.FIXTRUE_PARTICLE_ADDR_START,
                                                          0, unit=self._station_config.FIXTURE_PARTICLE_ADDR)  # type: WriteSingleRegisterResponse

    def particle_counter_read_val(self):
        if self._particle_counter_client is not None:
            val = None
            retries = 1
            while retries <= 10:
                rs = self._particle_counter_client.read_holding_registers(self._station_config.FIXTRUE_PARTICLE_ADDR_READ,
                                                                          2, unit=self._station_config.FIXTURE_PARTICLE_ADDR)  # type: ReadHoldingRegistersResponse
                if rs is None or rs.isError():
                    if self._station_config.IS_VERBOSE:
                        print "Retries to read data from particle counter {}/10. ".format(retries)
                    retries += 1
                    time.sleep(0.5)
                else:
                    # val = rs.registers[0] * 65535 + rs.registers[1]
                    # modified by elton.  for apc-r210/310
                    val = ctypes.c_int32(rs.registers[0]  + (rs.registers[1] << 16)).value
                    if hasattr(station_config, 'PARTICLE_COUNTER_APC') and station_config.PARTICLE_COUNTER_APC:
                        val = (ctypes.c_int32((rs.registers[0] << 16) + rs.registers[1])).value
                    break
            if val is None:
                raise pancakepixelFixtureError('Failed to read data from particle counter.')
            return val

    def particle_counter_state(self):
        if self._particle_counter_client is not None:
            rs = self._particle_counter_client.read_holding_registers(self._station_config.FIXTRUE_PARTICLE_ADDR_STATUS,
                                                                      2,
                                                                      unit=self._station_config.FIXTURE_PARTICLE_ADDR)  # type: ReadHoldingRegistersResponse
            if rs is None or rs.isError():
                raise pancakepixelFixtureError('Fail to read data from particle counter. ')
            else:
                return rs.registers[0]

def print_to_console(self, msg):
    pass

if __name__ == "__main__":

    sys.path.append("../../")
    import types
    import station_config
    import hardware_station_common.operator_interface.operator_interface

    print 'Self check for test_fixture_pancanke_pixel'
    station_config.load_station('pancake_pixel')
    station_config.print_to_console = types.MethodType(print_to_console, station_config)
    the_fixture = pancakepixelFixture(station_config, station_config)

    the_fixture.initialize()
    the_fixture.reset()

    the_fixture.unload()
    time.sleep(1)
    the_fixture.load()

    the_fixture.close()