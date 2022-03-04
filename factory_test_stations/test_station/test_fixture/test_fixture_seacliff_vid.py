import os
import re
import socket
import serial
import select
import pprint
import math
from enum import Enum, unique
import serial.tools.list_ports
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.register_write_message import WriteSingleRegisterResponse
from pymodbus.register_read_message import ReadHoldingRegistersResponse
from pymodbus.constants import Defaults
import time
import ctypes
import hardware_station_common.test_station.test_fixture
import hardware_station_common.test_station.dut


class seacliffVidFixtureError(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        self.message = msg

    def __str__(self):
        return repr(self.message)


class seacliffVidFixture(hardware_station_common.test_station.test_fixture.TestFixture):
    """
        class for seacliff vid Fixture
            this is for doing all the specific things necessary to interface with instruments
    """
    def __init__(self, station_config, operator_interface):
        hardware_station_common.test_station.test_fixture.TestFixture.__init__(self, station_config, operator_interface)
        self._serial_port = None
        self._verbose = station_config.IS_VERBOSE
        self._start_delimiter = ':'
        self._end_delimiter = '@_@'
        self._error_msg = r'imcomplete command'
        self._re_space_sub = re.compile(' ')
        self._version = None
        self._id = None

    def is_ready(self):
        if self._serial_port is not None:
            resp = self._read_response(0.5)
            if resp:
                btn_dic = {3: r'PowerOn_Button:\d', 2: r'BUTTON_LEFT:\d', 1: r'BUTTON_RIGHT:\d',
                           0x10: r'BUTTON_L:0', 0x11: r'BUTTON_R:0'}
                for key, item in btn_dic.items():
                    items = list(filter(lambda r: re.match(item, r, re.I | re.S), resp))
                    if items:
                        return key

    def initialize(self, **kwargs):
        self._operator_interface.print_to_console("Initializing seacliff vid Fixture\n")
        self._serial_port = serial.Serial(kwargs.get('fixture_com'),
                                          115200,
                                          parity='N',
                                          bytesize=8,
                                          stopbits=1,
                                          timeout=0.3,
                                          xonxoff=0,
                                          rtscts=0)
        if not self._serial_port:
            raise seacliffVidFixtureError(f'Unable to open fixture port: {kwargs}')
        else:  # disable the buttons automatically
            self.start_button_status(True)
            self.power_on_button_status(True)
            self.unload()
            self.start_button_status(False)
            self.power_on_button_status(False)
            self._version = self.version()
            self._id = self.id()

            self._operator_interface.print_to_console(f"Fixture %s Initialized. {kwargs}")
            return True

    @property
    def version(self):
        return self._version

    @property
    def fixture_id(self):
        return self._id

    def _write_serial(self, input_bytes):
        """
        @param input_bytes: fixture command without \r\n
        @type input_bytes: str
        """
        if self._verbose:
            print('writing: ' + input_bytes)
        cmd = '{0}\r\n'.format(input_bytes)
        self._serial_port.flush()
        bytes_written = self._serial_port.write(cmd.encode())
        return bytes_written

    def flush_data(self):
        if self._serial_port is not None:
            self._serial_port.flush()

    def _read_response(self, timeout=10, ignore_non_error=True, rev_pattern=None):
        msg = ''
        tim = time.time()
        while time.time() - tim < timeout:
            line_in = self._serial_port.readline()
            if line_in != b'':
                msg = msg + line_in.decode()
            if (re.search(self._end_delimiter, msg, re.IGNORECASE) and
                    ((rev_pattern is None) or re.search(rev_pattern, msg, re.IGNORECASE))):
                break

        response = msg.strip().splitlines()
        if self._verbose:
            if len(response) > 1:
                pprint.pprint(response)
            else:
                print('Fail to read any data in {0} seconds. '.format(timeout))
        if not ignore_non_error and response is None:
            raise seacliffVidFixtureError('reading data time out ->. ')
        return response

    def _parse_response(self, regex, resp):
        """
        parse the response data with regex
        @type regex: Pattern[AnyStr]
        @type resp:  List<str>
        @return: Match
        """
        if len([c for c in resp if c.find(self._error_msg) >= 0]) > 0:
            raise seacliffVidFixtureError('error msg from fixture. %s' % resp)
        if not resp:
            raise seacliffVidFixtureError('unable to get data from fixture.')
        items = list(filter(lambda r: re.search(regex, r, re.I | re.S), resp))
        if not items:
            raise seacliffVidFixtureError('unable to parse msg. {}'.format(resp))
        return re.search(regex, items[0], re.I | re.S)

    def help(self):
        self._write_serial(self._station_config.COMMAND_HELP)
        response = self._read_response(5, ignore_non_error=False)
        return response

    def id(self):
        """
        get fixture id, it will raise an exception while Id is not saved to the E2PROM
        @return:
        """
        self._write_serial(self._station_config.COMMAND_ID)
        response = self._read_response()
        return self._parse_response(r'GetBoardID:(.+)', response).group(1)

    def version(self):
        """
        get version number
        @return:
        """
        self._write_serial(self._station_config.COMMAND_VERSION)
        response = self._read_response()
        return self._parse_response(r'VERSION:(.+)', response).group(1)

    def close(self):
        try:
            self._operator_interface.print_to_console("Closing seacliff_VID Fixture\n")
            if hasattr(self, '_serial_port') \
                    and self._serial_port is not None \
                    and self._station_config.FIXTURE_COMPORT:
                self._serial_port.close()
                self._serial_port = None
        except Exception as e:
            print('Exception while closing. {0}'.format(str(e)))
        return True

    def power_on_button_status(self, on):
        """
        @type on : bool
        enable the power on button
        @return:
        """
        status_dic = {
            True: (self._station_config.COMMAND_BUTTON_LITUP_ENABLE, r'PowerOnButton_ENABLE:(\d+)'),
            False: (self._station_config.COMMAND_BUTTON_LITUP_DISABLE, r'PowerOnButton_DISABLE:(\d+)'),
        }
        cmd = status_dic[on]
        self._write_serial(cmd[0])
        response = self._read_response(rev_pattern=cmd[1])
        if int(self._parse_response(cmd[1], response).group(1)) != 0:
            raise seacliffVidFixtureError('fail to send command. %s' % response)

    def query_button_power_on_status(self):
        """
        query the power on button
        @return:
        """
        cmd = (self._station_config.COMMAND_LITUP_STATUS, r'POWERON_BUTTON:(\d+)')
        self._write_serial(cmd[0])
        response = self._read_response(rev_pattern=cmd[1])
        if int(self._parse_response(cmd[1], response).group(1)) != 0:
            raise seacliffVidFixtureError('fail to send command. %s' % response)

    def query_probe_status(self):
        """
        query the power on button
        @return:
        """
        cmd = (self._station_config.COMMAND_PROBE_BUTTON, r'Probe_BUTTON:(\d+)')
        self._write_serial(cmd[0])
        response = self._read_response(rev_pattern=cmd[1])
        return int(self._parse_response(cmd[1], response).group(1))

    def start_button_status(self, on):
        """
        @type on : bool
        enable the start button
        @return:
        """
        status_dic = {
            True: (self._station_config.COMMAND_BUTTON_ENABLE, r'START_BUTTON_ENABLE:(\d+)'),
            False: (self._station_config.COMMAND_BUTTON_DISABLE, r'START_BUTTON_DISABLE:(\d+)'),
        }
        cmd = status_dic[on]
        self._write_serial(cmd[0])
        response = self._read_response(rev_pattern=cmd[1])
        if int(self._parse_response(cmd[1], response).group(1)) != 0:
            raise seacliffVidFixtureError('fail to send command. %s' % response)

    def reset(self):
        """
        fixture reset
        @return:
        """
        self._write_serial(self._station_config.COMMAND_RESET)
        response = self._read_response(timeout=10)
        if int(self._parse_response(r'RESET:(\d+)', response).group(1)) != 0:
            raise seacliffVidFixtureError('fail to send command. %s' % response)

    def set_tri_color(self, status):
        """
        set the color for tricolor light
        @type status: TriColorStatus
        @return:
        """
        switch = {
            TriColorStatus.RED: 'red',
            TriColorStatus.YELLOW: 'yellow',
            TriColorStatus.GREEN: 'green',
            TriColorStatus.BUZZER: 'buzzer',
        }
        cmd = '{0}:{1}'.format(self._station_config.COMMAND_STATUS_LIGHT_ON, switch[status])
        self._write_serial(cmd)
        rev_pattern = r'StatusLight_ON:(\d+)'
        response = self._read_response(rev_pattern=rev_pattern)
        if int(self._parse_response(rev_pattern, response).group(1)) != 0:
            raise seacliffVidFixtureError('fail to send command. %s' % response)

    def set_tri_color_off(self):
        """
        set the tricolor light off
        @return:
        """
        cmd = self._station_config.COMMAND_STATUS_LIGHT_OFF
        self._write_serial(cmd)
        rev_pattern = r'StatusLight_OFF:(\d+)'
        response = self._read_response(rev_pattern=rev_pattern)
        if int(self._parse_response(rev_pattern, response).group(1)) != 0:
            raise seacliffVidFixtureError('fail to send command. %s' % response)

    def load(self, dut_type='L'):
        """
        load carrier
        @return:
        """
        module_typ_cmd = {
            'L': 'L',
            'R': 'R'
        }
        assert dut_type in module_typ_cmd
        self._write_serial(f'{self._station_config.COMMAND_LOAD}_{module_typ_cmd[dut_type]}')
        rev_pattern = r'LOAD_[L|R]:(\d+)'
        response = self._read_response(timeout=self._station_config.FIXTURE_LOAD_DLY, rev_pattern=rev_pattern)
        if int(self._parse_response(rev_pattern, response).group(1)) != 0:
            raise seacliffVidFixtureError('fail to send command. %s' % response)

    def load_position(self, dut_type='L'):
        """
        set the mode for  carrier loader
        @return:
        """
        module_typ_cmd = {
            'L': 'L',
            'R': 'R'
        }
        assert dut_type in module_typ_cmd
        self._write_serial(f'{self._station_config.COMMAND_PRE_LOAD_TYPE}:{module_typ_cmd[dut_type]}')
        rev_pattern = r'LOAD_DUT_[L|R]:(\d+)'
        response = self._read_response(timeout=self._station_config.FIXTURE_LOAD_DLY, rev_pattern=rev_pattern)
        if int(self._parse_response(rev_pattern, response).group(1)) != 0:
            raise seacliffVidFixtureError('fail to send command. %s' % response)

    def unload(self):
        """
        unload carrier
        @return:
        """
        self._alignment_pos = None
        self._write_serial(self._station_config.COMMAND_UNLOAD)
        rev_pattern = r'UNLOAD:(\d+)'
        response = self._read_response(rev_pattern=rev_pattern, timeout=self._station_config.FIXTURE_UNLOAD_DLY)
        if int(self._parse_response(rev_pattern, response).group(1)) != 0:
            raise seacliffVidFixtureError('fail to send command. %s' % response)

@unique
class TriColorStatus(Enum):
    RED = 0
    YELLOW = 1
    GREEN = 2
    BUZZER = 3


def print_to_console(self, msg):
    pass


if __name__ == '__main__':
    import sys
    import types

    sys.path.append(r'..\..')
    import station_config

    station_config.load_station('seacliff_vid')
    station_config.print_to_console = types.MethodType(print_to_console, station_config)
    the_unit = seacliffVidFixture(station_config, station_config)
    the_unit.initialize()
    the_unit.start_button_status(True)
    the_unit.close()

    pass