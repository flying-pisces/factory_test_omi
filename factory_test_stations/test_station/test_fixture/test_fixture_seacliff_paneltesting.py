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


class seacliffpaneltestingFixtureError(Exception):
    def __init__(self, msg):
        self._message = msg


@unique
class TriColorStatus(Enum):
    RED = 0
    YELLOW = 1
    GREEN = 2
    BUZZER = 3


class seacliffpaneltestingFixture(hardware_station_common.test_station.test_fixture.TestFixture):
    def __init__(self, station_config, operator_interface):
        hardware_station_common.test_station.test_fixture.TestFixture.__init__(self, station_config, operator_interface)
        self._serial_port = None
        self._verbose = station_config.IS_VERBOSE
        self._start_delimiter = ':'
        self._end_delimiter = '@_@'
        self._error_msg = r'imcomplete command'
        self._rotate_scale = 65 * 1000
        self._y_limit_pos = 12 * 1000
        self._a_limit_pos = 10
        self._re_space_sub = re.compile(' ')
        self._particle_counter_client = None  # type: ModbusSerialClient
        self._safe_position = None

    def is_ready(self):
        if self._serial_port is not None:
            resp = self._read_response(2)
            if resp:
                if not hasattr(self._station_config, 'DUT_LITUP_OUTSIDE') or not self._station_config.DUT_LITUP_OUTSIDE:
                    items = list(filter(lambda r: re.match(r'LOAD:\d+', r, re.I | re.S), resp))
                    if items:
                        return int((items[0].split(self._start_delimiter))[1].split(self._end_delimiter)[0]) == 0x00
                else:
                    btn_dic = {3: r'PowerOn_Button:\d', 2: r'BUTTON_LEFT:\d', 1: r'BUTTON_RIGHT:\d', 0: r'BUTTON:\d'}
                    for key, item in btn_dic.items():
                        items = list(filter(lambda r: re.match(item, r, re.I | re.S), resp))
                        if items:
                            return key

    def initialize(self):
        self._operator_interface.print_to_console("Initializing seacliff_paneltesting Fixture\n")
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
            if (not self._particle_counter_client) or (not self._particle_counter_client.connect()):
                raise seacliffpaneltestingFixtureError('Unable to open particle counter port: %s'
                                                 % self._station_config.FIXTURE_PARTICLE_COMPORT)
        if (not self._serial_port) or (not self._serial_port.isOpen()):
            raise seacliffpaneltestingFixtureError('Unable to open fixture port: %s' % self._station_config.FIXTURE_COMPORT)
        else:  # disable the buttons automatically
            self.start_button_status(True)
            self.power_on_button_status(True)
            self.unload()
            self.start_button_status(False)
            self.power_on_button_status(False)

            self._operator_interface.print_to_console(
                "Fixture %s Initialized.\n" % self._station_config.FIXTURE_COMPORT)
            return True

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

    def _read_response(self, timeout=10):
        msg = ''
        tim = time.time()
        while (not re.search(self._end_delimiter, msg, re.IGNORECASE)
               and (time.time() - tim < timeout)):
            line_in = self._serial_port.readline()
            if line_in != b'':
                msg = msg + line_in.decode()
        response = msg.strip().splitlines()
        if self._verbose:
            if len(response) > 1:
                pprint.pprint(response)
            else:
                print('Fail to read any data in {0} seconds. '.format(timeout))
        return response

    def read_response(self, timeout=5):
        response = self._read_response(timeout)
        if not response:
            raise seacliffpaneltestingFixtureError('reading data time out ->.')
        return response

    def help(self):
        self._write_serial(self._station_config.COMMAND_HELP)
        response = self.read_response(5)
        return response

    def id(self):
        """
        get fixture id, it will raise an exception while Id is not saved to the E2PROM
        @return:
        """
        self._write_serial(self._station_config.COMMAND_ID)
        response = self._read_response()
        return self._parse_response(r'ID:(.+)', response).group(1)

    def version(self):
        """
        get version number
        @return:
        """
        self._write_serial(self._station_config.COMMAND_VERSION)
        response = self._read_response()
        return self._parse_response(r'VERSION:(.+)', response).group(1).replace(',', '_')

    def close(self):
        try:
            self._operator_interface.print_to_console("Closing seacliff_mot Fixture\n")
            if hasattr(self, '_serial_port') \
                    and self._serial_port is not None \
                    and self._station_config.FIXTURE_COMPORT:
                # self.button_disable()
                self._serial_port.close()
                self._serial_port = None
            if hasattr(self, '_particle_counter_client') and \
                    self._particle_counter_client is not None \
                    and self._station_config.FIXTURE_PARTICLE_COUNTER:
                self._particle_counter_client.close()
                self._particle_counter_client = None
        except Exception as e:
            print('Exception while closing. {0}'.format(str(e)))
            pass
        if self._verbose:
            pprint.pprint("====== Fixture Close =========")
        return True

    def status(self):
        self._write_serial(self._station_config.COMMAND_STATUS)
        response = self._read_response()
        deters = self._parse_response(r':(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)', response)
        return response

    ######################
    # Fixture control
    ######################
    def unlock_servo_axis(self, axis):
        """
        @type axis : str
        @return:
        """
        cmd = ('{0}:{1}'.format('CMD_SERVO_POWEROFF', axis), r'ServoPowerOFF_\w:\d*')
        self._write_serial(cmd[0])
        response = self.read_response()
        if int(self._parse_response(cmd[1], response).group(1)) != 0:
            raise seacliffpaneltestingFixtureError('fail to send command. %s' % response)

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
        response = self.read_response()
        if int(self._parse_response(cmd[1], response).group(1)) != 0:
            raise seacliffpaneltestingFixtureError('fail to send command. %s' % response)

    def query_button_power_on_status(self):
        """
        query the power on button
        @return:
        """
        cmd = (self._station_config.COMMAND_LITUP_STATUS, r'POWERON_BUTTON:(\d+)')
        self._write_serial(cmd[0])
        response = self.read_response()
        if int(self._parse_response(cmd[1], response).group(1)) != 0:
            raise seacliffpaneltestingFixtureError('fail to send command. %s' % response)

    def query_probe_status(self):
        """
        query the power on button
        @return:
        """
        cmd = (self._station_config.COMMAND_PROBE_BUTTON, r'Probe_BUTTON:(\d+)')
        self._write_serial(cmd[0])
        response = self.read_response()
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
        response = self.read_response()
        if int(self._parse_response(cmd[1], response).group(1)) != 0:
            raise seacliffpaneltestingFixtureError('fail to send command. %s' % response)

    def reset(self):
        """
        fixture reset
        @return:
        """
        self._write_serial(self._station_config.COMMAND_RESET)
        response = self.read_response(timeout=10)
        if int(self._parse_response(r'RESET:(\d+)', response).group(1)) != 0:
            raise seacliffpaneltestingFixtureError('fail to send command. %s' % response)

    def mov_abs_xy_wrt_dut(self, x, y):
        """
        move the module to position(x: um, y: um, a: degree)
        @type x: int
        @type y: int
        @return:
        """
        cmd_mov = '{0}:{1}, {2}'.format(self._station_config.COMMAND_MODULE_MOVE,
                                             int(-1*y), int(x))
        self._write_serial(cmd_mov)
        response = self.read_response(timeout=20)
        if int(self._parse_response(r'MODULE_MOVE:(\d+)', response).group(1)) != 0:
            raise seacliffpaneltestingFixtureError('fail to send command. %s' % response)

    def module_pos_wrt_dut(self):
        """
        query the module position
        @return:
        """
        cmd = self._station_config.COMMAND_MODULE_POSIT
        self._write_serial(cmd)
        response = self.read_response()
        response = [self._re_space_sub.sub('', c) for c in response]
        delimiter = r'MODULE_POSIT:([+-]?[0-9]*(?:\.[0-9]*)?),([+-]?[0-9]*(?:\.[0-9]*)?)'
        deters = self._parse_response(delimiter, response)
        return int(deters[2]), -1*int(deters[1])

    def status(self):
        """
        query the button status
        @return:
        """
        cmd_status = '{0}'.format(self._station_config.COMMAND_STATUS)
        self._write_serial(cmd_status)
        response = self.read_response()
        return self._parse_response(r'START_BUTTON:(\d+)', response).group(1)

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
        response = self.read_response()
        if int(self._parse_response(r'StatusLight_ON:(\d+)', response).group(1)) != 0:
            raise seacliffpaneltestingFixtureError('fail to send command. %s' % response)

    def set_tri_color_off(self):
        """
        set the tricolor light off
        @return:
        """
        cmd = self._station_config.COMMAND_STATUS_LIGHT_OFF
        self._write_serial(cmd)
        response = self.read_response()
        if int(self._parse_response(r'StatusLight_OFF:(\d+)', response).group(1)) != 0:
            raise seacliffpaneltestingFixtureError('fail to send command. %s' % response)

    def ca_postion_z(self, wip):
        cmds = {
            False: self._station_config.COMMAND_CA_UP,
            True: self._station_config.COMMAND_CA_DOWN,
        }
        cmd = cmds.get(wip)
        if cmd is not None:
            self._write_serial(cmd)
            response = self.read_response()
            if int(self._parse_response(r'CARRIER(?:DW|UP):(\d+)', response).group(1)) != 0:
                raise seacliffpaneltestingFixtureError('fail to send command. %s' % response)

    def load(self):
        """
        load carrier
        @return:
        """
        self._safe_position = None
        self._write_serial(self._station_config.COMMAND_LOAD)
        response = self.read_response()
        if int(self._parse_response(r'LOAD:(\d+)', response).group(1)) != 0:
            raise seacliffpaneltestingFixtureError('fail to send command. %s' % response)

    def unload(self):
        """
        unload carrier
        @return:
        """
        self._write_serial(self._station_config.COMMAND_UNLOAD)
        response = self.read_response(timeout=self._station_config.FIXTURE_UNLOAD_DLY)
        if int(self._parse_response(r'UNLOAD:(\d+)', response).group(1)) != 0:
            raise seacliffpaneltestingFixtureError('fail to send command. %s' % response)

    def _parse_response(self, regex, resp):
        """
        parse the response data with regex
        @type regex: Pattern[AnyStr]
        @type resp:  List<str>
        @return: Match
        """
        if len([c for c in resp if c.find(self._error_msg) >= 0]) > 0:
            raise seacliffpaneltestingFixtureError('error msg from fixture. %s' % resp)
        if not resp:
            raise seacliffpaneltestingFixtureError('unable to get data from fixture.')
        items = list(filter(lambda r: re.search(regex, r, re.I | re.S), resp))
        if not items:
            raise seacliffpaneltestingFixtureError('unable to parse msg. {}'.format(resp))
        return re.search(regex, items[0], re.I | re.S)

    ######################
    # Particle Counter Control
    ######################
    def particle_counter_on(self):
        if self._particle_counter_client is not None:
            wrs = self._particle_counter_client. \
                write_register(self._station_config.FIXTRUE_PARTICLE_ADDR_START,
                               1, unit=self._station_config.FIXTURE_PARTICLE_ADDR)
            if wrs is None or wrs.isError():
                raise seacliffpaneltestingFixtureError('Failed to start particle counter .')

    def particle_counter_off(self):
        if self._particle_counter_client is not None:
            self._particle_counter_client.write_register(self._station_config.FIXTRUE_PARTICLE_ADDR_START,
                                                         0,
                                                         unit=self._station_config.FIXTURE_PARTICLE_ADDR)  # type: WriteSingleRegisterResponse

    def particle_counter_read_val(self):
        if self._particle_counter_client is not None:
            val = None
            retries = 1
            while retries <= 10:
                rs = self._particle_counter_client.read_holding_registers(
                    self._station_config.FIXTRUE_PARTICLE_ADDR_READ,
                    2, unit=self._station_config.FIXTURE_PARTICLE_ADDR)  # type: ReadHoldingRegistersResponse
                if rs is None or rs.isError():
                    if self._station_config.IS_VERBOSE:
                        print("Retries to read data from particle counter {}/10. ".format(retries))
                    retries += 1
                    time.sleep(0.5)
                else:
                    # val = rs.registers[0] * 65535 + rs.registers[1]
                    # modified by elton.  for apc-r210/310
                    val = ctypes.c_int32(rs.registers[0] + (rs.registers[1] << 16)).value
                    if hasattr(self._station_config, 'PARTICLE_COUNTER_APC') and self._station_config.PARTICLE_COUNTER_APC:
                        val = (ctypes.c_int32((rs.registers[0] << 16) + rs.registers[1])).value
                    break
            if val is None:
                raise seacliffpaneltestingFixtureError('Failed to read data from particle counter.')
            return val

    def particle_counter_state(self):
        if self._particle_counter_client is not None:
            retries = 1
            val = None
            while retries <= 10:
                rs = self._particle_counter_client.read_holding_registers(
                    self._station_config.FIXTRUE_PARTICLE_ADDR_STATUS,
                    2,
                    unit=self._station_config.FIXTURE_PARTICLE_ADDR)  # type: ReadHoldingRegistersResponse
                if rs is None or rs.isError():
                    print('Fail to read data from particle counter. ')
                    retries = retries + 1
                    time.sleep(0.5)
                    continue
                else:
                    val = rs.registers[0]
                    break
            if val is None:
                raise seacliffpaneltestingFixtureError('Failed to read status from particle counter.')
            return val


def print_to_console(self, msg):
    pass


if __name__ == "__main__":
    import sys
    import types

    sys.path.append(r'../..')
    import logging
    import station_config
    station_config.load_station('seacliff_paneltesting')
    station_config.print_to_console = types.MethodType(print_to_console, station_config)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logging.getLogger(__name__).addHandler(ch)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    try:
        the_unit = seacliffpaneltestingFixture(station_config, station_config)
        the_unit.initialize()
        the_unit.load()
        for idx in range(0, 100):
            print('Loop ---> {}'.format(idx))
            try:
                the_unit.help()
                the_unit.id()
                the_unit.version()
                aa = the_unit.module_pos_wrt_dut()

                # the_unit.particle_counter_read_val()

                the_unit.load()
                the_unit.power_on_button_status(True)

                the_unit.start_button_status(True)
                time.sleep(1)
                the_unit.start_button_status(False)

                the_unit.power_on_button_status(True)

                for c, d in station_config.TEST_POINTS_POS:
                    print('Mov position {0}'.format(c))
                    the_unit.mov_abs_xy_wrt_dut(*d)
                    time.sleep(1)

                the_unit.set_tri_color(TriColorStatus.RED)
                time.sleep(1)
                the_unit.set_tri_color(TriColorStatus.GREEN)
                time.sleep(1)
                # the_unit.set_tri_color(TriColorStatus.BUZZER)
                # time.sleep(1)
                the_unit.set_tri_color(TriColorStatus.YELLOW)
                time.sleep(1)
                the_unit.set_tri_color_off()

            except seacliffpaneltestingFixtureError as e:
                print(e.message)
            finally:
                pass
                # time.sleep(2)
                # the_unit.close()
    finally:
        the_unit.close()
