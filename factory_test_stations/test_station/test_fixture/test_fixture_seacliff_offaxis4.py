import hardware_station_common.test_station.test_fixture
import os
import sys
import re
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
import threading


class SeacliffOffAxis4FixtureError(Exception):
    pass


class SeacliffOffAxis4Fixture(hardware_station_common.test_station.test_fixture.TestFixture):

    class Scanner710(object):
        def __init__(self, com_port='COM1'):
            self._error_msg = 'ERROR'
            self._cmd_on = b'LON\r'
            self._cmd_off = b'LOFF\r'
            self._max_retries = 3
            self._serial_port = serial.Serial(com_port,
                                              115200,
                                              parity='N',
                                              bytesize=8,
                                              stopbits=1,
                                              timeout=0.3,
                                              xonxoff=0,
                                              rtscts=0)
            self._com_port = com_port

        def scan(self, timeout=2):
            self._serial_port.write(self._cmd_off)
            retries = 1
            sn_code = None
            while retries <= self._max_retries and sn_code is None:
                self.on()
                msg = []
                tim = time.time()
                try:
                    while time.time() - tim < timeout and ord('\r') not in msg:
                        line_in = self._serial_port.readline()
                        if line_in != b'':
                            msg.extend(line_in)
                    if len(msg) > 0:
                        sn_code = bytearray(msg).decode('utf-8', 'ignore').splitlines(keepends=False)[-1]
                except Exception as ex:
                    print(f'unable to get data from SR700. {ex}')
                if sn_code == self._error_msg or sn_code is None:
                    self.off()
                    self._serial_port.readline()
                retries += 1
            return sn_code

        def off(self):
            self._serial_port.write(self._cmd_off)

        def on(self):
            self._serial_port.write(self._cmd_on)

        def __del__(self):
            if self._serial_port:
                self._serial_port.close()
    """
        class for Tokki offaxis Fixture
            this is for doing all the specific things necessary to interface with instruments
    """
    def __init__(self, station_config, operator_interface):
        hardware_station_common.test_station.test_fixture.TestFixture.__init__(self, station_config, operator_interface)
        self._serial_port = None
        self._verbose = station_config.IS_VERBOSE
        self._start_delimiter = ':'
        self._end_delimiter = '@_@'
        self._end_delimiter_auto_response = '^_^'
        self._error_msg = r'Please scanf "CMD_HELP" check help command'
        self._particle_counter_client = None  # type: ModbusSerialClient
        self._fixture_mutex = threading.Lock()

    def is_ready(self):
        if self._serial_port is not None and self._fixture_mutex.acquire(blocking=False):
            resp = self._read_response(0.1, end_delimiter=self._end_delimiter_auto_response)
            self._fixture_mutex.release()
            if resp:
                print(resp)
                btn_dic = {4: r'PowerOn_Button_R:(\d+)',
                           3: r'PowerOn_Button_L:(\d+)',
                           2: r'BUTTON_LEFT:(\d+)',
                           1: r'BUTTON_RIGHT:(\d+)',
                           0: r'BUTTON:(\d+)'}
                for key, item in btn_dic.items():
                    items = list(filter(lambda r: re.search(item, r, re.I | re.S), resp))
                    if items:
                        return key, int(re.search(item, items[0], re.I | re.S).group(1))

    def initialize(self, **kwargs):
        self._operator_interface.print_to_console("Initializing offaxis Fixture\n")
        self._serial_port = serial.Serial(kwargs.get('fixture_port'),
                                          115200,
                                          parity='N',
                                          stopbits=1,
                                          timeout=0.3,
                                          xonxoff=0,
                                          rtscts=0)
        if self._station_config.FIXTURE_PARTICLE_COUNTER:
            parity = 'N'
            Defaults.Retries = 5
            Defaults.RetryOnEmpty = True
            self._particle_counter_client = ModbusSerialClient(method='rtu', baudrate=9600, bytesize=8, parity=parity,
                                                               stopbits=1,
                                                               port=kwargs.get('particle_port'),
                                                               timeout=2000)
            self._particle_counter_client.inter_char_timeout = 0.2
            if not self._particle_counter_client.connect():
                raise SeacliffOffAxis4FixtureError(f'Unable to open particle counter port: {kwargs}')

        if not self._serial_port:
            raise SeacliffOffAxis4FixtureError(f'Unable to open fixture port: {kwargs}')
        else:  # disable the buttons automatically
            self.set_tri_color('y')
            for bk in ['A', 'B']:
                self.vacuum(False, bk_mode=bk)
                self.power_on_button_status(True, bk_mode=bk)
            self.button_enable()
            self.unload()
            for bk in ['A', 'B']:
                self.vacuum(False, bk_mode=bk)
                self.power_on_button_status(False, bk_mode=bk)
            self.button_disable()
            self.set_tri_color('g')
            if self._verbose:
                print(f"Fixture Initialized: {kwargs}")
            return True

    def _write_serial(self, input_bytes):
        if self._verbose:
            print('writing: ' + input_bytes)
        cmd = '{0}\r\n'.format(input_bytes)
        self._serial_port.reset_input_buffer()
        bytes_written = self._serial_port.write(cmd.encode())
        return bytes_written

    def flush_data(self):
        if self._serial_port is not None:
            self._serial_port.flush()

    def _read_response(self, timeout=10, end_delimiter='@_@'):
        msg = ''
        tim = time.time()
        while (not re.search(end_delimiter, msg, re.IGNORECASE)
               and (time.time() - tim < timeout)):
            line_in = self._serial_port.readline()
            if line_in != b'':
                msg = msg + line_in.decode()
        response = msg.strip().splitlines()
        if self._verbose:
            if len(response) > 1:
                pprint.pprint(response)
            elif end_delimiter not in [self._end_delimiter_auto_response]:
                print('Fail to read any data in {0} seconds. '.format(timeout))
        return response

    def read_response(self, timeout=5):
        response = self._read_response(timeout)
        if not response:
            raise SeacliffOffAxis4FixtureError('reading data time out ->.')
        return response

    def help(self):
        with self._fixture_mutex:
            self._write_serial(self._station_config.COMMAND_HELP)
            response = self.read_response()
        if self._verbose:
            pprint.pprint(response)
        return response

    def reset(self):
        with self._fixture_mutex:
            self._write_serial(self._station_config.COMMAND_RESET)
            response = self.read_response()
        val = int(self._prase_response(r'LOAD:(\d+)', response).group(1))
        if val == 0x00:
            time.sleep(self._station_config.FIXTURE_PTB_OFF_TIME)
        return val

    def id(self):
        with self._fixture_mutex:
            self._write_serial(self._station_config.COMMAND_ID)
            response = self.read_response()
        if self._verbose:
            print(response[1])
        return self._prase_response(r'ID:(.+)', response).group(1)

    def close(self):
        self._operator_interface.print_to_console("Closing tokki offaxis Fixture\n")
        if hasattr(self, '_serial_port') \
                and self._serial_port is not None:
            self.set_tri_color('y')
            for c in ['A', 'B']:
                self.power_on_button_status(False, c)
                self.vacuum(False, c)
            self.button_disable()
            self._serial_port.close()
            self._serial_port = None
        if hasattr(self, '_particle_counter_client') and \
                self._particle_counter_client is not None \
                and self._station_config.FIXTURE_PARTICLE_COUNTER:
            self._particle_counter_client.close()
            self._particle_counter_client = None
        if self._verbose:
            pprint.pprint("====== Fixture Close =========")
        return True

    ######################
    # Fixture control
    ######################
    def button_enable(self):
        with self._fixture_mutex:
            self._write_serial(self._station_config.COMMAND_BUTTON_ENABLE)
            response = self.read_response()
        return int(self._prase_response(r'BTN_ENABLE:(\d+)', response).group(1))

    def button_disable(self):
        with self._fixture_mutex:
            self._write_serial(self._station_config.COMMAND_BUTTON_DISABLE)
            response = self.read_response()
        return int(self._prase_response(r'BTN_DISABLE:(\d+)', response).group(1))

    def mov_abs_xy(self, x, y):
        CMD_MOVE_STRING = self._station_config.COMMAND_ABS_X_Y + ':' + str(x) + ',' + str(y)
        with self._fixture_mutex:
            self._write_serial(CMD_MOVE_STRING)
            response = self.read_response()
        if self._verbose:
            print(response)
        return int(self._prase_response(r'ABS_X_Y:(\d+)', response).group(1))

    def load(self):
        self._load()

    def unload(self):
        self._unload()

    def vacuum(self, on, bk_mode='A'):
        """
        get version number
        @return:
        """
        vacuum_dict = {
            True: ('ON', r'VACUUM_[L|]ON:(\d+)'),
            False: ('OFF', r'VACUUM_[L|R]OFF:(\d+)'),
        }
        bk_dic = {
            'A': f'L',
            'B': f'R'
        }
        cmd = vacuum_dict[on]
        with self._fixture_mutex:
            self._write_serial(f'{self._station_config.COMMAND_VACUUM_CTRL}:{bk_dic[bk_mode.upper()]}{cmd[0]}')
            response = self._read_response()
        return self._prase_response(cmd[1], response).group(1)

    def vacuum_status(self, bk_mode='A'):
        """
        enable the power on button
        @return:
        """
        bk_dic = {
            'A': 0x10,
            'B': 0x01
        }
        with self._fixture_mutex:
            self._write_serial(f'{self._station_config.COMMAND_VACUUM_STATUS}')
            response = self.read_response()
        return 0 != int(self._prase_response(r'Vacuum_Button_Status:(\d+)',
                        response).group(1), 16) & bk_dic[bk_mode.upper()]

    def power_on_status(self, bk_mode='A'):
        """
        @type bk_mode: 'A'/'B'
        enable the power on button
        @return:
        """
        bk_dic = {
            'A': f'L',
            'B': f'R'
        }
        with self._fixture_mutex:
            self._write_serial(f'{self._station_config.COMMAND_POWERON_STATUS}:{bk_dic[bk_mode.upper()]}')
            response = self.read_response()
        return int(self._prase_response(r'PowerOn_Button_[L|R]:(\d+)', response).group(1))

    def _load(self):
        with self._fixture_mutex:
            self._write_serial(self._station_config.COMMAND_LOAD)
            response = self.read_response(timeout=self._station_config.FIXTURE_UNLOAD_DLY)
        return int(self._prase_response(r'LOAD:(\d+)', response).group(1))

    def _unload(self):
        with self._fixture_mutex:
            self._write_serial(self._station_config.COMMAND_UNLOAD)
            response = self.read_response(timeout=self._station_config.FIXTURE_UNLOAD_DLY)
        return int(self._prase_response(r'UNLOAD:(\d+)', response).group(1))

    def _prase_response(self, regex, resp):
        if not resp:
            raise SeacliffOffAxis4FixtureError('unable to get data from fixture.')
        items = list(filter(lambda r: re.search(regex, r, re.I), resp))
        if not items:
            raise SeacliffOffAxis4FixtureError('unable to parse msg. {}'.format(items))
        return re.search(regex, items[0], re.I | re.S)

    def set_tri_color(self, color):
        """
        :type color: str
        """
        switch = {
            'r': self._station_config.COMMAND_TRI_LED_R,
            'y': self._station_config.COMMAND_TRI_LED_Y,
            'g': self._station_config.COMMAND_TRI_LED_G,
        }
        cmd = switch.get(color)
        if cmd:
            with self._fixture_mutex:
                self._write_serial(cmd)
                response = self.read_response()
            r = r'LED_[R|Y|G]:(\d+)'
            return int(self._prase_response(r, response).group(1))

    def power_on_button_status(self, on=True, bk_mode='A'):
        """
        @type on : bool
        @type bk_mode: 'A'/'B'
        enable the power on button
        @return:
        """
        status_dic = {
            True: (self._station_config.COMMAND_BUTTON_LITUP_ENABLE, r'PowerOnButton_ENABLE_[L|R]:(\d+)'),
            False: (self._station_config.COMMAND_BUTTON_LITUP_DISABLE, r'PowerOnButton_DISABLE_[L|R]:(\d+)'),
        }
        bk_dic = {
            'A': f'L',
            'B': f'R'
        }
        cmd = status_dic[on]
        with self._fixture_mutex:
            self._write_serial(f'{cmd[0]}:{bk_dic[bk_mode.upper()]}')
            response = self.read_response()
        if int(self._prase_response(cmd[1], response).group(1)) != 0:
            raise SeacliffOffAxis4FixtureError('fail to send command. %s' % response)

    ######################
    # Particle Counter Control
    ######################
    def particle_counter_on(self):
        if self._particle_counter_client is not None:
            wrs = self._particle_counter_client. \
                write_register(self._station_config.FIXTRUE_PARTICLE_ADDR_START,
                               1, unit=self._station_config.FIXTURE_PARTICLE_ADDR)
            if wrs is None or wrs.isError():
                raise SeacliffOffAxis4FixtureError('Failed to start particle counter .')

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
                    if hasattr(self._station_config,
                               'PARTICLE_COUNTER_APC') and self._station_config.PARTICLE_COUNTER_APC:
                        val = (ctypes.c_int32((rs.registers[0] << 16) + rs.registers[1])).value
                    break
            if val is None:
                raise SeacliffOffAxis4FixtureError('Failed to read data from particle counter.')
            return val

    def particle_counter_state(self):
        if self._particle_counter_client is not None:
            retries = 1
            val = None
            while retries <= 10 and val is None:
                rs = self._particle_counter_client.read_holding_registers(
                    self._station_config.FIXTRUE_PARTICLE_ADDR_STATUS,
                    2,
                    unit=self._station_config.FIXTURE_PARTICLE_ADDR)  # type: ReadHoldingRegistersResponse

                if rs is None or rs.isError():
                    if self._station_config.IS_VERBOSE:
                        pprint.pprint("Retries to read data from particle counter {0}/10. ".format(retries))
                    continue
                val = rs.registers[0]
            if val is None:
                raise SeacliffOffAxis4FixtureError('Failed to read data from particle counter.')
            return val

    def scan_code(self, com_port='COM1'):
        scanner = SeacliffOffAxis4Fixture.Scanner710(com_port=com_port)
        code = scanner.scan(timeout=2)
        del scanner
        return code


def print_to_console(self, msg):
    pass


if __name__ == '__main__':
    import sys
    import types

    sys.path.append(r'..\..')
    import station_config
    import serial.tools
    coms = serial.tools.list_ports.comports()

    station_config.load_station('seacliff_offaxis4')
    station_config.print_to_console = types.MethodType(print_to_console, station_config)
    the_unit = SeacliffOffAxis4Fixture(station_config, station_config)
    the_unit.initialize(fixture_port='com6', particle_port='com8')
    for __ in range(10):
        for bk in ['A', 'b']:
            the_unit.load()
            the_unit.button_enable(bk)
            the_unit.set_tri_color('y')
            the_unit.button_disable(bk)

            the_unit.power_on_button_status(True, bk_mode=bk)
            the_unit.power_on_button_status(False, bk_mode=bk)

            the_unit.unload()
            the_unit.set_tri_color('r')
    the_unit.close()
    pass