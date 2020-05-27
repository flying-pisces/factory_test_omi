import hardware_station_common.test_station.test_fixture
import os
import sys
import re
### Below two lines will be used for debug.
sys.path.append("../")
import glob
import serial
import serial.tools.list_ports
import time
import pprint
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.register_write_message import WriteSingleRegisterResponse
from pymodbus.register_read_message import ReadHoldingRegistersResponse
from pymodbus.constants import Defaults
import time
import ctypes

class pancakeoffaxisFixtureError(Exception):
    pass

class pancakeoffaxisFixture(hardware_station_common.test_station.test_fixture.TestFixture):
    """
        class for auo unif Fixture
            this is for doing all the specific things necessary to interface with instruments
    """
    def __init__(self, station_config, operator_interface):
        hardware_station_common.test_station.test_fixture.TestFixture.__init__(self, station_config, operator_interface)
        self._serial_port = None
        self._verbose = station_config.IS_VERBOSE
        self._start_delimiter = ':'
        self._end_delimiter = '@_@'
        self._error_msg = r'Please scanf "CMD_HELP" check help command'
        self._particle_counter_client = None  # type: ModbusSerialClient

    def is_ready(self):
        if self._serial_port is not None:
            resp = self._read_response(2)
            if resp:
                if not hasattr(self._station_config, 'DUT_LITUP_OUTSIDE') or not self._station_config.DUT_LITUP_OUTSIDE:
                    items = filter(lambda r: re.match(r'LOAD:\d+', r, re.I), resp)
                    if items:
                        return int((items[0].split(self._start_delimiter))[1].split(self._end_delimiter)[0]) == 0x00
                else:
                    btn_dic = {2 : r'BUTTON_LEFT:\d', 1 : r'BUTTON_RIGHT:\d', 0 : r'BUTTON:\d'}
                    for key, item in btn_dic.items():
                        items = filter(lambda r: re.match(item, r, re.I), resp)
                        if items:
                            return key

    def initialize(self):
        self._operator_interface.print_to_console("Initializing offaxis Fixture\n")
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
                    raise pancakeoffaxisFixtureError( 'Unable to open particle counter port: %s'
                                                      % self._station_config.FIXTURE_PARTICLE_COMPORT)

        if not self._serial_port:
            raise pancakeoffaxisFixtureError('Unable to open fixture port: %s' % self._station_config.FIXTURE_COMPORT)
        else:  # disable the buttons automatically
            self.set_tri_color('y')
            self.button_enable()
            self.unload()
            self.button_disable()
            self.set_tri_color('g')
            if self._verbose:
                print "Fixture %s Initialized" % self._station_config.FIXTURE_COMPORT
            return True

    def _write_serial(self, input_bytes):
        self._serial_port.flush()
        if self._verbose:
            print("flushed")
            print('writing: ' + input_bytes)
        bytes_written = self._serial_port.write(input_bytes)
        return bytes_written

    def flush_data(self):
        if self._serial_port is not None:
            self._serial_port.flush

    def _read_response(self, timeout=5):
        response = []
        line_in = ""
        tim = time.time()
        while (not re.search(self._end_delimiter, line_in, re.IGNORECASE)
               and (time.time() - tim < timeout)):
            line_in = self._serial_port.readline()
            if line_in != "":
                response.append(line_in)
        if self._verbose and len(response) > 1:
            pprint.pprint(response)
        return response

    def read_response(self, timeout=5):
        response = self._read_response(timeout)
        if not response:
            raise pancakeoffaxisFixtureError('reading data time out ->.')
        return response

    def help(self):
        self._write_serial(self._station_config.COMMAND_HELP)
        response = self.read_response()
        if self._verbose:
            pprint.pprint(response)
        return response

    def reset(self):
        self._write_serial(self._station_config.COMMAND_RESET)
        response = self.read_response()
        val = self._prase_response('LOAD:\d+', response)
        if val == 0x00:
            time.sleep(self._station_config.FIXTURE_PTB_OFF_TIME)
        return val

    def id(self):
        self._write_serial(self._station_config.COMMAND_ID)
        response = self.read_response()
        if self._verbose:
            print(response[1])
        value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
        return value

    def close(self):
        self._operator_interface.print_to_console("Closing auo offaxis Fixture\n")
        if hasattr(self, '_serial_port') \
                and self._serial_port is not None \
                and self._station_config.FIXTURE_COMPORT:
            self.set_tri_color('y')
            self.button_disable()
            self._serial_port.close()
            self._serial_port = None
        if hasattr(self, '_particle_counter_client') and \
                self._particle_counter_client is not None \
                and self._station_config.FIXTURE_PARTICLE_COUNTER:
            self._particle_counter_client.close()
            self._particle_counter_client = None
        if self._verbose:
            pprint.pprint( "====== Fixture Close =========")
        return True

    ######################
    # Fixture control
    ######################
    def button_enable(self):
        self._write_serial(self._station_config.COMMAND_BUTTON_ENABLE)
        response = self.read_response()
        return self._prase_response(r'BTN_ENABLE:\d+', response)

    def button_disable(self):
        self._write_serial(self._station_config.COMMAND_BUTTON_DISABLE)
        response = self.read_response()
        return self._prase_response(r'BTN_DISABLE:\d+', response)

    def mov_abs_xy(self, x, y):
        CMD_MOVE_STRING = self._station_config.COMMAND_ABS_X_Y + ' ' + str(x) + " " + str(y) + "\r\n"
        self._write_serial(CMD_MOVE_STRING)
        response = self.read_response()
        if self._verbose:
            print(response)
        return self._prase_response(r'ABS_X_Y:\d+', response)

    def pogo_state_up(self, up):
        cmd = self._station_config.COMMAND_POGO_DOWN # OFF
        r = r'POGO_DOWN:\d+'
        if up:
            cmd = self._station_config.COMMAND_POGO_UP # ON
            r = r'POGO_UP:\d+'
        self._write_serial(cmd)
        response = self.read_response()
        return self._prase_response(r, response)

    def load(self):
        self._load()

    def unload(self):
        self._unload()

    def _load(self):
        self._write_serial(self._station_config.COMMAND_LOAD)
        response = self.read_response()
        return self._prase_response(r'LOAD:\d+', response)

    def _unload(self):
        self._write_serial(self._station_config.COMMAND_UNLOAD)
        response = self.read_response(timeout=self._station_config.FIXTURE_PTB_UNLOAD_DLY)
        return self._prase_response(r'UNLOAD:\d+', response)

    def _prase_response(self, regex, resp):
        if not resp:
            raise pancakeoffaxisFixtureError('unable to get data from fixture.')
        items = filter(lambda r : re.search(regex, r, re.I), resp)
        if not items:
            raise pancakeoffaxisFixtureError('unable to parse msg. {}'.format(items))
        return (items[0].split(self._start_delimiter))[1].split(self._end_delimiter)[0]

    def press_ctrl_up(self, up=True):
        cmd = self._station_config.COMMAND_PRESS_DOWN # ON
        r = r'PRESS_DOWN:\d+'
        if up:
            cmd = self._station_config.COMMAND_PRESS_UP # OFF
            r = r'PRESS_UP:\d+'
        self._write_serial(cmd)
        response = self.read_response()
        return self._prase_response(r, response)

    def set_tri_color(self, color):
        """
        :type color: str
        """
        switch = {
            'r':self._station_config.COMMAND_TRI_LED_R,
            'y':self._station_config.COMMAND_TRI_LED_Y,
            'g':self._station_config.COMMAND_TRI_LED_G,
        }
        cmd = switch.get(color)
        if cmd:
            self._write_serial(cmd)
            response = self.read_response()
            r = r'LED_[R|Y|G]:\d+'
            return self._prase_response(r, response)

    ######################
    # Particle Counter Control
    ######################
    def particle_counter_on(self):
        if self._particle_counter_client is not None:
            wrs = self._particle_counter_client.\
                write_register(self._station_config.FIXTRUE_PARTICLE_ADDR_START,
                               1, unit=self._station_config.FIXTURE_PARTICLE_ADDR)
            if wrs is None or wrs.isError():
                raise pancakeoffaxisFixtureError('Failed to start particle counter .')

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
                    if hasattr(self._station_config, 'PARTICLE_COUNTER_APC') and self._station_config.PARTICLE_COUNTER_APC:
                        val = (ctypes.c_int32((rs.registers[0] << 16) + rs.registers[1])).value
                    break
            if val is None:
                raise pancakeoffaxisFixtureError('Failed to read data from particle counter.')
            return val

    def particle_counter_state(self):
        if self._particle_counter_client is not None:
            rs = self._particle_counter_client.read_holding_registers(self._station_config.FIXTRUE_PARTICLE_ADDR_STATUS,
                                                                      2,
                                                                      unit=self._station_config.FIXTURE_PARTICLE_ADDR)  # type: ReadHoldingRegistersResponse
            if rs is None or rs.isError():
                raise pancakeoffaxisFixtureError('Fail to read data from particle counter. ')
            else:
                return rs.registers[0]

def print_to_console(self, msg):
    pass

if __name__ == "__main__":
        sys.path.append("../../")
        import types
        import station_config
        import hardware_station_common.operator_interface.operator_interface

        print 'Self check for pancake_offaxis'
        station_config.load_station('pancake_offaxis')
        station_config.FIXTURE_COMPORT = 'COM15'
        station_config.print_to_console = types.MethodType(print_to_console, station_config)
        the_fixture = pancakeoffaxisFixture(station_config, station_config)
        the_fixture._verbose = True

        try:
            the_fixture.initialize()

            # the_fixture.mov_abs_xy(5, 1)
            print 'Id = %s'%the_fixture.id()

            the_fixture.press_ctrl_up(False)
            the_fixture.pogo_state_up(True)
            the_fixture.load()

            the_fixture.button_enable()
            pprint.pprint(the_fixture.help())
            the_fixture.mov_abs_xy(0, 18)
            the_fixture.mov_abs_xy(0, -18)
            the_fixture.mov_abs_xy(18, 0)
            the_fixture.mov_abs_xy(-18, 0)
            the_fixture.mov_abs_xy(0, 0)

            the_fixture.unload()

        except pancakeoffaxisFixtureError as e:
            print 'exception {}'.format(e.message)
        finally:
            the_fixture.close()