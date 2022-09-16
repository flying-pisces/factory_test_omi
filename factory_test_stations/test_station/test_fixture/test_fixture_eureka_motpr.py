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
import threading
import hardware_station_common.test_station.test_fixture
import hardware_station_common.test_station.dut


class StationCommunicationProxy(object):
    _communication_proxy_name = r"D:\Version\Release\vision.exe"
    _progress_handle = None

    def __init__(self, port=9999):
        """
        :type port: int
        """
        self._addr = "127.0.0.1"
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # type: socket.socket
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self._max_len_per_package = 1024
        self._r_inputs = set()
        self._sock.connect((self._addr, self._port))
        pass

    def close(self):
        if self._sock is not None:
            self._sock.close()

    def readline(self, timeout=1):
        import io
        self._sock.settimeout(timeout)
        data = b''
        try:
            readable, writeable, exceptional = select.select([self._sock], [], [], timeout)
            if readable or writeable or exceptional:
                for s in readable:
                    try:
                        d2 = s.recv(self._max_len_per_package)
                        if isinstance(d2, bytes):
                            data += d2
                    except:
                        pass
        except io.BlockingIOError as e:
            data = None

        self._sock.settimeout(None)
        return data

    def __getattr__(self, item):
        def not_find(*args, **kwargs):
            pass

        if item in ['flush']:
            return not_find

    def write(self, cmd):
        """
        :type cmd: str
        """
        self._sock.sendall(cmd)

    def clear_buff(self):
        """
        Clear buffers
        """
        self._sock.setblocking(False)
        while True:
            try:
                __ = self._sock.recvfrom(self._max_len_per_package)
            except:
                break
        self._sock.setblocking(True)

    @staticmethod
    def run_daemon_application(cmd=None):
        import win32process
        import pywintypes
        cwd = os.getcwd()
        res = -1
        try:
            si = win32process.STARTUPINFO()
            pth, fn = os.path.split(StationCommunicationProxy._communication_proxy_name)
            os.chdir(pth)
            # si.dwFlags |= win32process.STARTF_USESHOWWINDOW
            StationCommunicationProxy._progress_handle \
                = win32process.CreateProcess(fn, cmd, None, None, 0, win32process.CREATE_NO_WINDOW, None, None, si)
            if not StationCommunicationProxy._progress_handle:
                res = -1
            res = 0
        except pywintypes.error as e:
            pass
        finally:
            os.chdir(cwd)
        if res != 0:
            raise Exception('fail to exec {0} res :{1}'.format(cmd, res))
        return res

    @staticmethod
    def close_application():
        import win32process
        import pywintypes
        try:
            if StationCommunicationProxy._progress_handle:
                win32process.TerminateProcess(StationCommunicationProxy._progress_handle[0], 0)
        except pywintypes.error as e:
            pass


@unique
class TriColorStatus(Enum):
    RED = 0
    YELLOW = 1
    GREEN = 2
    BUZZER = 3

@unique
class QueryTempParts(Enum):
    EquipmentAmbient = 0
    UUTNearBy = 1


class EurekaMotPRFixtureError(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        self.message = msg

    def __str__(self):
        return repr(self.message)


class EurekaMotPRFixture(hardware_station_common.test_station.test_fixture.TestFixture):
    """
        class for project station Fixture
            this is for doing all the specific things necessary to interface with instruments
    """

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
        # status of the platform
        self.PTB_Position = None
        self._Button_Status = None
        self._PTB_Power_Status = None
        self._USB_Power_Status = None
        self._alignment_pos = None
        self._fixture_mutex = threading.Lock()
        self._end_delimiter_auto_response = '^_^'

    def is_ready(self):
        if self._serial_port is not None and self._fixture_mutex.acquire(blocking=False):
            resp = self._read_response(0.1, end_delimiter=self._end_delimiter_auto_response)
            self._fixture_mutex.release()
            if resp:
                btn_dic = {3: r'PowerOn_Button:(\d+)',
                           2: r'BUTTON_Right:(\d+)',
                           1: r'BUTTON_Left:(\d+)',
                           0: r'BUTTON:(\d+)'}
                for key, item in btn_dic.items():
                    items = list(filter(lambda r: re.search(item, r, re.I | re.S), resp))
                    if items:
                        return key, int(re.search(item, items[0], re.I | re.S).group(1))

    def initialize(self, **kwargs):
        self._operator_interface.print_to_console("Initializing EurekaMotPR Fixture\n")
        if hasattr(self._station_config, 'IS_PROXY_COMMUNICATION') and \
                self._station_config.IS_PROXY_COMMUNICATION:
            StationCommunicationProxy._communication_proxy_name = self._station_config.PROXY_COMMUNICATION_PATH
            StationCommunicationProxy.run_daemon_application()
            time.sleep(6)
            self._serial_port = StationCommunicationProxy(kwargs.get('proxy_port'))
        else:
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
                                                               timeout=2)
            self._particle_counter_client.inter_char_timeout = 0.2
            if not self._particle_counter_client.connect():
                raise EurekaMotPRFixtureError(f'Unable to open particle counter port: {kwargs}')
        if not self._serial_port:
            raise EurekaMotPRFixtureError(f'Unable to open fixture port: {kwargs}')
        else:  # disable the buttons automatically
            # self.start_button_status(True)
            # self.power_on_button_status(True)
            # self.unload()
            # self.start_button_status(False)
            # self.power_on_button_status(False)
            self._operator_interface.print_to_console(f"Fixture Initialized {kwargs}.\n")
            return True

    def _write_serial(self, input_bytes):
        self._serial_port.flush()
        if self._verbose:
            print("flushed")
            print('writing: ' + input_bytes)
        cmd = '{0}\r\n'.format(input_bytes)
        # self._serial_port.reset_input_buffer()
        bytes_written = self._serial_port.write(cmd.encode())
        return bytes_written

    def flush_data(self):
        if isinstance(self._serial_port, StationCommunicationProxy):
            self._serial_port.clear_buff()
            if self._verbose:
                print(f'Clear buffer for StationCommunicationProxy\n')
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

    def help(self):
        with self._fixture_mutex:
            self._write_serial(self._station_config.COMMAND_HELP)
            response = self._read_response(5)
        return response

    def id(self):
        """
        get fixture id, it will raise an exception while Id is not saved to the E2PROM
        @return:
        """
        with self._fixture_mutex:
            self._write_serial(self._station_config.COMMAND_ID)
            response = self._read_response()
        return self._parse_response(r'ID:(.+)', response).group(1)

    def version(self):
        """
        get version number
        @return:
        """
        with self._fixture_mutex:
            self._write_serial(self._station_config.COMMAND_VERSION)
            response = self._read_response()
        return self._parse_response(r'VERSION:(.+)', response).group(1)

    def close(self):
        try:
            self._operator_interface.print_to_console("Closing EurekaMotPR Fixture\n")
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
        finally:
            if self._station_config.IS_PROXY_COMMUNICATION:
                StationCommunicationProxy.close_application()
        if self._verbose:
            pprint.pprint("====== Fixture Close =========")
        return True
    '''
    def status(self):
        self._write_serial(self._station_config.COMMAND_STATUS)
        response = self._read_response()
        deters = self._parse_response(r':(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)', response)
        self.PTB_Position = int(deters.group(1))
        self._Button_Status = int(deters.group(2))
        self._PTB_Power_Status = int(deters.group(3))
        self._USB_Power_Status = int(deters.group(7))
        return response

    def poweron_usb(self):
        self._write_serial(self._station_config.COMMAND_USB_POWER_ON)
        time.sleep(self._station_config.FIXTURE_USB_ON_TIME)
        response = self._read_response()
        value = int(self._parse_response(r'ON:(\d+)', response).group(1))
        self._USB_Power_Status = value
        return value

    def poweroff_usb(self):
        self._write_serial(self._station_config.COMMAND_USB_POWER_OFF)
        time.sleep(self._station_config.FIXTURE_USB_OFF_TIME)
        response = self._read_response()
        value = int(self._parse_response(r'ON:(\d+)', response).group(1))
        self._USB_Power_Status = value
        return value

    def poweron_ptb(self):
        self._write_serial(self._station_config.COMMAND_PTB_POWER_ON)
        time.sleep(self._station_config.FIXTURE_PTB_ON_TIME)
        response = self._read_response()
        value = int(self._parse_response(r'ON:(\d+)', response).group(1))
        self._PTB_Power_Status = value
        return value

    def poweroff_ptb(self):
        self._write_serial(self._station_config.COMMAND_PTB_POWER_OFF)
        time.sleep(self._station_config.FIXTURE_PTB_OFF_TIME)
        response = self._read_response()
        value = int(self._parse_response(r'ON:(\d+)', response).group(1))
        self._PTB_Power_Status = value
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
    '''
    ######################
    # Fixture control
    ######################
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
        with self._fixture_mutex:
            self._write_serial(cmd[0])
            response = self._read_response()
        if int(self._parse_response(cmd[1], response).group(1)) != 0:
            raise EurekaMotPRFixtureError('fail to send command. %s' % response)

    def query_button_power_on_status(self):
        """
        query the power on button
        @return:
        """
        cmd = (self._station_config.COMMAND_LITUP_STATUS, r'POWERON_BUTTON:(\d+)')
        with self._fixture_mutex:
            self._write_serial(cmd[0])
            response = self._read_response()
        if int(self._parse_response(cmd[1], response).group(1)) != 0:
            raise EurekaMotPRFixtureError('fail to send command. %s' % response)

    def query_probe_status(self):
        """
        query the power on button
        @return:
        """
        cmd = (self._station_config.COMMAND_PROBE_BUTTON, r'Probe_BUTTON:(\d+)')
        with self._fixture_mutex:
            self._write_serial(cmd[0])
            response = self._read_response()
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
        with self._fixture_mutex:
            self._write_serial(cmd[0])
            response = self._read_response()
        if int(self._parse_response(cmd[1], response).group(1)) != 0:
            raise EurekaMotPRFixtureError('fail to send command. %s' % response)

    def reset(self):
        self._write_serial(self._station_config.COMMAND_RESET)
        response = self._read_response(timeout=self._station_config.FIXTURE_RESET_DLY)
        val = int(self._parse_response(r'reset:(\d+)', response).group(1))
        if val == 0x00:
            time.sleep(self._station_config.FIXTURE_PTB_OFF_TIME)
        return val

    def mov_abs_xy_wrt_alignment(self, x, y):
        """
        move the module (x, y ref to DUT) to motor position
        (x: um, y: um, a: degree)
        @type x: int
        @type y: int
        @return:
        """
        if self._alignment_pos is None:
            raise EurekaMotPRFixtureError('alignment command should be executed firstly.')
        xx = self._alignment_pos[0] + x
        yy = self._alignment_pos[1] + y
        self.mov_abs_xya(xx, yy, self._alignment_pos[2])

    def mov_abs_xya(self, x, y, a):
        """
        move the module to position(x: um, y: um, a: degree)
        @type x: int
        @type y: int
        @param a: angle for module 0-360
        @type a: float
        @return:
        """
        if math.fabs(y) < self._y_limit_pos and not math.isclose(a, 0):
            msg = 'fail to move abs_xya.  y = {0} < {1} and a = {2}'.format(y, self._y_limit_pos, a)
            raise EurekaMotPRFixtureError(msg)
        if a > math.fabs(self._a_limit_pos):
            raise EurekaMotPRFixtureError('fail to move abs_xya.  | a | = {} < {} '.format(a, self._a_limit_pos))
        theta = int(math.sin(math.radians(a)) * self._rotate_scale)
        cmd_mov = '{0}:{1}, {2}, {3}'.format(self._station_config.COMMAND_MODULE_MOVE,
                                             int(x), int(y), int(theta))
        success = False
        retries = 1
        response = None
        rev_pattern = r'MODULE_MOVE:(\d+)'
        while retries <= 5 and not success:
            with self._fixture_mutex:
                self._write_serial(cmd_mov)
                response = self._read_response(timeout=20)
                rev_code = int(self._parse_response(rev_pattern, response).group(1))
            if rev_code == 0:
                success = True
            elif rev_code != 31:  # add retry for errcode 31
                break
            retries += 1
        if not success:
            raise EurekaMotPRFixtureError('fail to send command. %s' % response)

    def calib_zero_pos(self):
        """
        query the module position
        @return:
        """
        cmd = self._station_config.COMMAND_ZERO_POSIT
        with self._fixture_mutex:
            self._write_serial(cmd)
            delimiter = r'ZERO_POSIT:([+-]?[0-9]*(?:\.[0-9]*)?)'
            response = self._read_response()
        response = [self._re_space_sub.sub('', c) for c in response]
        deters = self._parse_response(delimiter, response)
        return int(deters[1])

    def module_pos(self):
        """
        query the module position
        @return:
        """
        cmd = self._station_config.COMMAND_MODULE_POSIT
        with self._fixture_mutex:
            self._write_serial(cmd)
            delimiter = r'MODULE_POSIT:([+-]?[0-9]*(?:\.[0-9]*)?),([+-]?[0-9]*(?:\.[0-9]*)?),([+-]?[0-9]*(?:\.[0-9]*)?)'
            response = self._read_response()
        response = [self._re_space_sub.sub('', c) for c in response]
        deters = self._parse_response(delimiter, response)
        return int(deters[1]), int(deters[2]), math.degrees(math.asin(float(deters[3]) / self._rotate_scale))

    def camera_pos(self):
        """
        query the camera position
        @return:
        """
        cmd = self._station_config.COMMAND_CAMERA_POSIT
        with self._fixture_mutex:
            self._write_serial(cmd)
            delimiter = r'CAMERA_POSIT:([+-]?[0-9]*(?:\.[0-9]*)?)'
            response = self._read_response()
        response = [self._re_space_sub.sub('', c) for c in response]
        return (self._station_config.DISTANCE_BETWEEN_CAMERA_AND_DATUM
                - int(self._parse_response(delimiter, response).group(1)))

    def mov_camera_z_wrt_alignment(self, z):
        """
        move the camera to z(um) position
        @type z: int
        @param z:
        @return:
        """
        self._operator_interface.print_to_console('mov z to wrt {0}\n'.format(z))
        zz = z + self._alignment_pos[3]
        self.mov_camera_z(zz)

    def mov_camera_z(self, z):
        """
        move the camera to z(um) position
        @type z: int
        @param z:
        @return:
        """
        z0 = self._station_config.DISTANCE_BETWEEN_CAMERA_AND_DATUM - z
        cmd_mov = '{0}:{1}'.format(self._station_config.COMMAND_CAMERA_MOVE, z0)
        with self._fixture_mutex:
            self._write_serial(cmd_mov)
            rev_pattern = r'CAMERA_MOVE:(\d+)'
        response = self._read_response(timeout=10 * 1000)
        if int(self._parse_response(rev_pattern, response).group(1)) != 0:
            raise EurekaMotPRFixtureError('fail to send command. %s' % response)

    def status(self):
        """
        query the button status
        @return:
        """
        cmd_status = '{0}'.format(self._station_config.COMMAND_STATUS)
        self._write_serial(cmd_status)
        response = self._read_response()
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
        with self._fixture_mutex:
            self._write_serial(cmd)
            rev_pattern = r'StatusLight_ON:(\d+)'
            response = self._read_response()
        if int(self._parse_response(rev_pattern, response).group(1)) != 0:
            raise EurekaMotPRFixtureError('fail to send command. %s' % response)

    def set_tri_color_off(self):
        """
        set the tricolor light off
        @return:
        """
        cmd = self._station_config.COMMAND_STATUS_LIGHT_OFF
        with self._fixture_mutex:
            self._write_serial(cmd)
            rev_pattern = r'StatusLight_OFF:(\d+)'
            response = self._read_response()
        if int(self._parse_response(rev_pattern, response).group(1)) != 0:
            raise EurekaMotPRFixtureError('fail to send command. %s' % response)

    def query_temp(self, parts=QueryTempParts.EquipmentAmbient):
        """
                set the tricolor light off
                @return:
                """
        cmd = {
            QueryTempParts.EquipmentAmbient: self._station_config.COMMAND_QUERY_TEMP,
            QueryTempParts.UUTNearBy: self._station_config.COMMAND_QUERY_DUT_TEMP,
        }
        with self._fixture_mutex:
            self._write_serial(cmd.get(parts))
            delimiter = r'Get(?:DUT)?Temperature:([+-]?[0-9]*(?:\.[0-9]*)?)'
            response = self._read_response(timeout=self._station_config.FIXTURE_QUERY_TEMP_TIMEOUT)
        response = [self._re_space_sub.sub('', c) for c in response]
        deters = self._parse_response(delimiter, response)
        temp_l, temp_h = self._station_config.COMMAND_QUERY_TEMP_RANGE
        if not (temp_l <= float(deters[1]) <= temp_h):
            raise EurekaMotPRFixtureError(f'temperature {deters[1]} is over range [{temp_l}, {temp_h}] does not make sense.')
        return float(deters[1])

    def load(self):
        """
        load carrier
        @return:
        """
        self._alignment_pos = None
        with self._fixture_mutex:
            self._write_serial(self._station_config.COMMAND_LOAD)
            rev_pattern = r'LOAD:(\d+)'
            response = self._read_response(timeout=self._station_config.FIXTURE_LOAD_DLY)
        return int(self._parse_response(rev_pattern, response).group(1))

    def unload(self):
        """
        unload carrier
        @return:
        """
        self._alignment_pos = None
        with self._fixture_mutex:
            self._write_serial(self._station_config.COMMAND_UNLOAD)
            rev_pattern = r'UNLOAD:(\d+)'
            response = self._read_response(timeout=self._station_config.FIXTURE_UNLOAD_DLY)
        return int(self._parse_response(rev_pattern, response).group(1))

    def load_dut(self):
        """
        get version number
        @return:
        """
        rev_pattern = r'DUTLOAD:(\d+)'
        with self._fixture_mutex:
            self._write_serial(f'{self._station_config.COMMAND_DUT_LOAD}')
            response = self._read_response()
        return int(self._parse_response(rev_pattern, response).group(1))

    def unload_dut(self):
        """
        get version number
        @return:
        """
        rev_pattern = r'DUTUNLOAD:(\d+)'
        with self._fixture_mutex:
            self._write_serial(f'{self._station_config.COMMAND_DUT_UNLOAD}')
            response = self._read_response()
        return int(self._parse_response(rev_pattern, response).group(1))

    def vacuum(self, on):
        """
        get version number
        @return:
        """
        vacuum_dict = {
            True: ('ON', r'VACUUM_ON:(\d+)'),
            False: ('OFF', r'VACUUM_OFF:(\d+)'),
        }
        cmd = vacuum_dict[on]
        with self._fixture_mutex:
            self._write_serial(f'{self._station_config.COMMAND_VACUUM_CTRL}:{cmd[0]}')
            response = self._read_response()
        return self._parse_response(cmd[1], response).group(1)

    def alignment(self, serial_number):
        self._alignment_pos = None
        self._write_serial('{0}:{1}'.format(self._station_config.COMMAND_ALIGNMENT, serial_number))
        rev_pattern = r'ALIGNMENT:([\+|\-|\,|\w]+)'
        response = self._read_response(timeout=self._station_config.FIXTURE_ALIGNMENT_DLY)
        if self._parse_response(rev_pattern, response).group(1).upper().find(r'ERROR') >= 0:
            return

        delimiter = r'ALIGNMENT:([+-]?[0-9]*(?:\.[0-9]*)?),([+-]?[0-9]*(?:\.[0-9]*)?),' \
                    r'([+-]?[0-9]*(?:\.[0-9]*)?),([+-]?[0-9]*(?:\.[0-9]*)?)(?:,([l|r]))'
        deters = self._parse_response(delimiter, response)
        res = int(deters[1]), int(deters[2]), \
            math.degrees(math.asin(float(deters[3]) / self._rotate_scale)), int(deters[4]), deters[5]
        module_pos = self.module_pos()
        self._alignment_pos = (*module_pos, res[3])
        self._operator_interface.print_to_console(f'alignment info for sn {serial_number} : {self._alignment_pos}\n')
        return res

    def _parse_response(self, regex, resp):
        """
        parse the response data with regex
        @type regex: Pattern[AnyStr]
        @type resp:  List<str>
        @return: Match
        """
        if len([c for c in resp if c.find(self._error_msg) >= 0]) > 0:
            raise EurekaMotPRFixtureError('error msg from fixture. %s' % resp)
        if not resp:
            raise EurekaMotPRFixtureError('unable to get data from fixture.')
        items = list(filter(lambda r: re.search(regex, r, re.I | re.S), resp))
        if not items:
            raise EurekaMotPRFixtureError('unable to parse msg. {}'.format(resp))
        return re.search(regex, items[0], re.I | re.S)

    ######################
    # Particle Counter Control
    ######################
    def particle_counter_on(self):
        if self._particle_counter_client is not None:
            val = None
            retries = 1
            while (retries <= 10) and (val is None):
                try:
                    wrs = self._particle_counter_client. \
                        write_register(self._station_config.FIXTRUE_PARTICLE_ADDR_START,
                                       1, unit=self._station_config.FIXTURE_PARTICLE_ADDR)
                    if wrs is None or wrs.isError():
                        time.sleep(0.05)
                    else:
                        val = 1
                except:
                    pass
                finally:
                    retries += 1
            if val is None:
                raise EurekaMotPRFixtureError('Failed to start particle counter .')

    def particle_counter_off(self):
        if self._particle_counter_client is not None:
            val = None
            retries = 1
            while (retries <= 10) and (val is None):
                try:
                    wrs = self._particle_counter_client.write_register(
                        self._station_config.FIXTRUE_PARTICLE_ADDR_START, 0,
                        unit=self._station_config.FIXTURE_PARTICLE_ADDR)  # type: WriteSingleRegisterResponse
                    if wrs is None or wrs.isError():
                        time.sleep(0.05)
                    else:
                        val = 1
                except:
                    pass
                finally:
                    retries += 1

    def particle_counter_read_val(self):
        if self._particle_counter_client is not None:
            val = None
            retries = 1
            while (retries <= 10) and (val is None):
                try:
                    rs = self._particle_counter_client.read_holding_registers(
                        self._station_config.FIXTRUE_PARTICLE_ADDR_READ,
                        2, unit=self._station_config.FIXTURE_PARTICLE_ADDR)  # type: ReadHoldingRegistersResponse
                    if rs is None or rs.isError():
                        if self._station_config.IS_VERBOSE:
                            print("Retries to read data from particle counter {}/10. ".format(retries))
                        time.sleep(0.05)
                    else:
                        # val = rs.registers[0] * 65535 + rs.registers[1]
                        # modified by elton.  for apc-r210/310
                        val = ctypes.c_int32(rs.registers[0] + (rs.registers[1] << 16)).value
                        if hasattr(self._station_config, 'PARTICLE_COUNTER_APC') and self._station_config.PARTICLE_COUNTER_APC:
                            val = (ctypes.c_int32((rs.registers[0] << 16) + rs.registers[1])).value
                except:
                    pass
                finally:
                    retries += 1
            if val is None:
                raise EurekaMotPRFixtureError('Failed to read data from particle counter.')
            return val

    def particle_counter_state(self):
        if self._particle_counter_client is not None:
            val = None
            retries = 1
            while (retries <= 10) and (val is None):
                try:
                    rs = self._particle_counter_client.read_holding_registers(
                        self._station_config.FIXTRUE_PARTICLE_ADDR_STATUS,
                        2,
                        unit=self._station_config.FIXTURE_PARTICLE_ADDR)  # type: ReadHoldingRegistersResponse
                    if rs is None or rs.isError():
                        time.sleep(0.05)
                    else:
                        val = rs.registers[0]
                except:
                    pass
                finally:
                    retries += 1
            if val is None:
                raise EurekaMotPRFixtureError('Fail to read data from particle counter. ')
            return val


def print_to_console(self, msg):
    pass


if __name__ == "__main__":
    import sys
    import types

    sys.path.append(r'../..')
    import logging
    import station_config
    station_config.load_station('eureka_motpr')
    station_config.print_to_console = types.MethodType(print_to_console, station_config)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logging.getLogger(__name__).addHandler(ch)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    try:
        the_unit = EurekaMotPRFixture(station_config, station_config)
        the_unit.initialize(fixture_port='com4', particle_port='com9', proxy_port=8099)

        for idx in range(0, 100):
            print('Loop ---> {}'.format(idx))
            try:
                the_unit.help()
                the_unit.id()
                the_unit.version()

                # the_unit.particle_counter_read_val()

                the_unit.load()
                the_unit.power_on_button_status(True)

                alignment_result = the_unit.alignment(None)
                if alignment_result is None:
                    print('unable to alignment.')
                else:
                    print('alignment: x: {0}, y: {1}, a: {2}, z: {3}'.format(*alignment_result))
                    for pos_item in station_config.TEST_ITEM_POS:
                        pos_name = pos_item['name']
                        x, y, z = pos_item.get('pos')
                        print(f'Mov to POS {pos_name}')
                        the_unit.mov_abs_xy_wrt_alignment(x, y)
                        the_unit.mov_camera_z_wrt_alignment(z)
                        time.sleep(1)

                the_unit.start_button_status(True)
                time.sleep(1)
                the_unit.start_button_status(False)

                the_unit.power_on_button_status(True)

                # the_unit.mov_abs_xya(5000, 130 * 1000, 00)
                #
                # the_unit.mov_abs_xya(10000, 130 * 1000, 5)

                the_unit.set_tri_color(TriColorStatus.RED)
                time.sleep(1)
                the_unit.set_tri_color(TriColorStatus.GREEN)
                time.sleep(1)
                # the_unit.set_tri_color(TriColorStatus.BUZZER)
                # time.sleep(1)
                the_unit.set_tri_color(TriColorStatus.YELLOW)
                time.sleep(1)
                the_unit.set_tri_color_off()

                the_unit.unload()

            except EurekaMotPRFixtureError as e:
                print(e.message)
            finally:
                pass
                # time.sleep(2)
                # the_unit.close()
    finally:
        the_unit.close()
