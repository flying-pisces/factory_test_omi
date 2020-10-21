import os
import time
import re
import numpy as np
import sys
import socket
import serial
import struct
import logging
import datetime
import string
import win32process
import win32event
import pywintypes
import cv as cv2
import pprint
import math
import hardware_station_common.test_station.dut


class DUTError(Exception):
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return repr(self.value)


class pancakeDut(hardware_station_common.test_station.dut.DUT):

    def __init__(self, serial_number, station_config, operator_interface):
        hardware_station_common.test_station.dut.DUT.__init__(self, serial_number, station_config, operator_interface)
        self._station_config = station_config
        self._operator_interface = operator_interface
        # hardware_station_common.test_station.dut.DUT.__init__(self, serialNumber, station_config, operatorInterface)
        self._verbose = station_config.IS_VERBOSE
        self.is_screen_poweron = False
        self._serial_port = None # type: serial.Serial
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self._start_delimiter = "$"
        self._end_delimiter = '\r\n'
        self._spliter = ','
        self._nvm_data_len = 45
        self._renderImgTool = os.path.join(os.getcwd(), r'CambriaTools\exe\CambriaTools.exe')

    def initialize(self):
        self.is_screen_poweron = False
        self._serial_port = serial.Serial(self._station_config.DUT_COMPORT,
                                          baudrate=115200,
                                          bytesize=serial.EIGHTBITS,
                                          parity=serial.PARITY_NONE,
                                          stopbits=serial.STOPBITS_ONE,
                                          rtscts=False,
                                          xonxoff=False,
                                          dsrdtr=False,
                                          timeout=1,
                                          writeTimeout=None,
                                          interCharTimeout=None)
        if not self._serial_port:
            raise DUTError('Unable to open DUT port : %s' % self._station_config.DUT_COMPORT)

        print('DUT %s Initialised. ' % self._station_config.DUT_COMPORT)
        return True

    def screen_on(self):
        if not self.is_screen_poweron:
            self._power_off()
            time.sleep(0.5)
            recvobj = self._power_on()
            if recvobj is None:
                raise DUTError("Exit power_on because can't receive any data from dut.")
            self.is_screen_poweron = True
            if recvobj[0] != '0000':
                raise DUTError("Exit power_off because rev err msg. Msg = {}".format(recvobj))
            return True

    def screen_off(self):
        if self.is_screen_poweron:
            self._power_off()
            self.is_screen_poweron = False

    def close(self):
        self._operator_interface.print_to_console("Turn Off display................\n")
        if self.is_screen_poweron:
            self._power_off()
        self._operator_interface.print_to_console("Closing DUT by the communication interface.\n")
        if self._serial_port is not None:
            self._serial_port.close()
            self._serial_port = None
        self.is_screen_poweron = False

    def get_color_ext(self, internal_or_external):
        """

        @type internal_or_external: bool
        """
        recvobj = self._get_color_ext(internal_or_external)
        if recvobj is None:
            raise DUTError("Exit get_color because can't receive any data from dut.")
        if int(recvobj[0]) != 0x00:
            raise DUTError("Exit get_color because rev err msg. Msg = {}".format(recvobj))
        return tuple([int(x, 16) for x in recvobj[1:]])

    def display_color_check(self, color):
        norm_color = tuple([c / 255.0 for c in color])
        color1 = np.float32([[norm_color]])
        hsv = cv2.cvtColor(color1, cv2.COLOR_RGB2HSV)
        h, s, v = tuple(hsv[0, 0, :])
        self._operator_interface.print_to_console('COLOR: = {},{},{}\n'.format(h, s, v))
        return (self._station_config.DISP_CHECKER_L_HsvH <= h <= self._station_config.DISP_CHECKER_H_HsvH and
                self._station_config.DISP_CHECKER_L_HsvS <= s <= self._station_config.DISP_CHECKER_H_HsvS)

    def display_color(self, color=(255, 255, 255)):  # (r,g,b)
        if self.is_screen_poweron:
            recvobj = self._setColor(color)
            if recvobj is None:
                raise DUTError("Exit display_color because can't receive any data from dut.")
            if int(recvobj[0]) != 0x00:
                raise DUTError("Exit display_color because rev err msg. Msg = {0}".format(recvobj))
        time.sleep(self._station_config.DUT_DISPLAYSLEEPTIME)

    def display_image(self, image, is_ddr_data=False):
        recvobj = self._showImage(image, is_ddr_data)
        if recvobj is None:
            raise DUTError("Exit disp_image because can't receive any data from dut.")
        if int(recvobj[0]) != 0x00:
            raise DUTError("Exit disp_image because rev err msg. Msg = {0}".format(recvobj))
        time.sleep(self._station_config.DUT_DISPLAYSLEEPTIME)

    def vsync_microseconds(self):
        recvobj = self._vsyn_time()
        if recvobj is None:
            raise DUTError("Exit display_color because can't receive any data from dut.")
        grpt = re.match(r'(\d*[\.]?\d*)', recvobj[1])
        grpf = re.match(r'(\d*[\.]?\d*)', recvobj[2])
        if grpf is None or grpt is None:
            raise DUTError("Exit display_color because rev err msg. Msg = {0}".format(recvobj))
        return float(grpt.group(0))

    def get_version(self, uname='mcu'):
        """
            get the version of FW. uname should be set one of ['mcu', 'hw', 'fpga']
        @type uname: str
        """
        return self._version(uname)

    def render_image(self, pics):
        """
            call utils to render images to ddr
        :type pics: []
        """
        if isinstance(pics, list):
            cmd = os.path.basename(self._renderImgTool) + ' -push ' + \
                  ' '.join([os.path.abspath(c) for c in pics])
            return self._timeout_execute(cmd, len(pics) * self._station_config.DUT_RENDER_ONE_IMAGE_TIMEOUT)

    def reboot(self):
        delay_seconds = 40
        if hasattr(self._station_config, 'COMMAND_DISP_REBOOT_DLY'):
            delay_seconds = self._station_config.COMMAND_DISP_REBOOT_DLY
        sw = datetime.datetime.now()

        recvobj = self._reboot()
        self.is_screen_poweron = False
        if recvobj is None:
            raise DUTError("Fail to reboot because can't receive any data from dut.")
        if int(recvobj[0]) != 0x00:
            raise DUTError("Fail to reboot because rev err msg. Msg = {}".format(recvobj))
        response = []
        while True:
            dt = datetime.datetime.now()
            if (dt - sw).total_seconds() > delay_seconds:
                raise DUTError('Fail to reboot because waiting msg timeout {0:4f}s. '.format((dt - sw).total_seconds()))
            line_in = self._serial_port.readline()
            if line_in == b'':
                time.sleep(1)
                if self._verbose:
                    print('.')
                continue
            response.append(line_in.decode())
            if self._verbose and len(response) > 1:
                pprint.pprint(response)
            recvobj = self._prase_respose('System OK', response)
            if int(recvobj[0]) != 0x00:
                raise DUTError("Fail to reboot because rev err msg. Msg = {}".format(recvobj))
            if self._verbose:
                print('Reboot system successfully . Elapse time {0:4f} s.'.format((dt - sw).total_seconds()))
            break

    def nvm_read_statistics(self):
        self._write_serial_cmd(self._station_config.COMMAND_NVM_WRITE_CNT)
        resp = self._read_response()
        recv_obj = self._prase_respose(self._station_config.COMMAND_NVM_WRITE_CNT, resp)
        if int(recv_obj[0]) != 0x00:
            raise DUTError('Fail to read write count. = {0}'.format(recv_obj))
        return recv_obj

    def nvm_write_data(self, data_array):
        """

        @type data_array: bytes
        @return: [errcode, data_len]
        """
        cmd = '{0}, {1}, {2}'.format(self._station_config.COMMAND_NVM_WRITE, len(data_array), ','.join(data_array))
        self._write_serial_cmd(cmd)
        resp = self._read_response(timeout=self._station_config.DUT_NVRAM_WRITE_TIMEOUT)
        recv_obj = self._prase_respose(self._station_config.COMMAND_NVM_WRITE, resp)
        if int(recv_obj[0]) != 0x00:
            raise DUTError('Fail to read write count. = {0}'.format(recv_obj))
        return recv_obj

    def nvm_read_data(self, data_len=45):
        """

        @type data_len: int
        @return: [errcode, len, data...]
        """
        cmd = '{0},{1}'.format(self._station_config.COMMAND_NVM_READ, data_len)
        self._write_serial_cmd(cmd)
        resp = self._read_response()
        recv_obj = self._prase_respose(self._station_config.COMMAND_NVM_READ, resp)
        if int(recv_obj[0]) != 0x00:
            raise DUTError('Fail to read write count. = {0}'.format(recv_obj))
        return recv_obj

    def _timeout_execute(self, cmd, timeout=0):
        if timeout == 0:
            timeout = win32event.INFINITE
        cwd = os.getcwd()
        res = -1
        try:
            si = win32process.STARTUPINFO()
            render_img_path = os.path.dirname(self._renderImgTool)
            os.chdir(render_img_path)
            # si.dwFlags |= win32process.STARTF_USESHOWWINDOW

            handle = win32process.CreateProcess(None, cmd, None, None, 0, win32process.CREATE_NO_WINDOW,
                                                None, None, si)
            rc = win32event.WaitForSingleObject(handle[0], timeout)
            if rc == win32event.WAIT_FAILED:
                res = -1
            elif rc == win32event.WAIT_TIMEOUT:
                try:
                    win32process.TerminateProcess(handle[0], 0)
                except pywintypes.error as e:
                    raise DUTError('exectue {0} timeout :{1}'.format(cmd, e))
                if rc == win32event.WAIT_OBJECT_0:
                    res = win32process.GetExitCodeProcess(handle[0])
            else:
                res = 0
        finally:
            os.chdir(cwd)
        if res != 0:
            raise DUTError('fail to exec {0} res :{1}'.format(cmd, res))
        return res

    def _write_serial_cmd(self, command):
        cmd = '$c.{}\r\n'.format(command)
        if self._verbose:
            print('send command ----------> {0}'.format(cmd))

        self._serial_port.flush()
        self._serial_port.write(cmd.encode('utf-8'))

    def _read_response(self, timeout=5):
        tim = time.time()
        msg = ''
        while (not re.search(self._end_delimiter, msg, re.IGNORECASE)
               and (time.time() - tim < timeout)):
            line_in = self._serial_port.readline()
            if line_in != b'':
                msg = msg + line_in.decode()
        response = msg.splitlines(keepends=False)
        if self._verbose and len(response) > 1:
            pprint.pprint(response)
        return response

    def _vsyn_time(self):
        self._write_serial_cmd(self._station_config.COMMAND_DISP_VSYNC)
        response = self._read_response()
        return self._prase_respose(self._station_config.COMMAND_DISP_VSYNC, response)

    def _help(self):
        self._write_serial_cmd(self._station_config.COMMAND_DISP_HELP)
        time.sleep(1)
        response = self._read_response()
        if self._verbose:
            print(response)
        value = []
        for item in response[0:len(response)-1]:
            value.append(item)
        return value

    def _version(self, model_name):
        self._write_serial_cmd("%s,%s" % (self._station_config.COMMAND_DISP_VERSION, model_name))
        response = self._read_response()
        return self._prase_respose(self._station_config.COMMAND_DISP_VERSION, response)

    def _get_boardId(self):
        self._write_serial_cmd(self._station_config.COMMAND_DISP_GETBOARDID)
        response = self._read_response()
        return self._prase_respose(self._station_config.COMMAND_DISP_GETBOARDID, response)

    def _prase_respose(self, command, response):
        print("command : {0},,,{1}".format(command, response))
        if response is None:
            return None
        cmd1 = command.split(self._spliter)[0]
        respstr = ''.join(response).upper()
        if cmd1.upper() not in respstr:
            return None
        values = respstr.split(self._spliter)
        if len(values) == 1:
            raise DUTError('display ctrl rev data format error. <- ' + respstr)
        return values[1:]

    def _power_on(self):
        self._write_serial_cmd(self._station_config.COMMAND_DISP_POWERON)
        time.sleep(self._station_config.COMMAND_DISP_POWERON_DLY)
        response = self._read_response()
        return self._prase_respose(self._station_config.COMMAND_DISP_POWERON, response)

    def _power_off(self):
        self._write_serial_cmd(self._station_config.COMMAND_DISP_POWEROFF)
        time.sleep(self._station_config.COMMAND_DISP_POWEROFF_DLY)
        response = self._read_response()
        # return self._prase_respose(self._station_config.COMMAND_DISP_POWEROFF, response)

    def _reset(self):
        self._write_serial_cmd(self._station_config.COMMAND_DISP_RESET)
        time.sleep(self._station_config.COMMAND_DISP_RESET_DLY)
        response = self._read_response()
        return self._prase_respose(self._station_config.COMMAND_DISP_RESET, response)

    def _showImage(self, image_index, is_ddr_img):
        # type: (int, bool) -> str
        command = ''
        if isinstance(image_index, str):
            command = '{},{}'.format(self._station_config.COMMAND_DISP_SHOWIMAGE, image_index)
        elif isinstance(image_index, int):
            if is_ddr_img:
                image_index = 0x20 + image_index
            command = '{},{}'.format(self._station_config.COMMAND_DISP_SHOWIMAGE, hex(image_index))
        self._write_serial_cmd(command)
        time.sleep(self._station_config.COMMAND_DISP_SHOWIMG_DLY)
        response = self._read_response()
        return self._prase_respose(self._station_config.COMMAND_DISP_SHOWIMAGE, response)

    def _setColor(self, color=(255, 255, 255)):
        command = '{0},0x{1[0]:02X},0x{1[1]:02X},0x{1[2]:02X}'.format(self._station_config.COMMAND_DISP_SETCOLOR, color)
        self._write_serial_cmd(command)
        time.sleep(0.02)
        response = self._read_response()
        return self._prase_respose(self._station_config.COMMAND_DISP_SETCOLOR, response)

    def _MIPI_read(self, reg, typ):
        command = '{0},{1},{2}'.format(self._station_config.COMMAND_DISP_READ, reg, typ)
        self._write_serial_cmd(command)
        # time.sleep(1)
        response = self._read_response()
        return self._prase_respose(self._station_config.COMMAND_DISP_READ, response)

    def _MIPI_write(self, reg, typ, val):
        command = '{0},{1},{2},{3}'.format(self._station_config.COMMAND_DISP_WRITE, reg, typ, val)
        self._write_serial_cmd(command)
        #time.sleep(1)
        response = self._read_response()
        return self._prase_respose(self._station_config.COMMAND_DISP_WRITE, response)

    def _reboot(self):
        cmd = 'Reboot'
        if hasattr(self._station_config, 'COMMAND_REBOOT'):
            cmd = self._station_config.COMMAND_REBOOT
        self._write_serial_cmd(cmd)
        response = self._read_response()
        return self._prase_respose(cmd, response)

    def _get_color_ext(self, internal_or_external):
        internal_external_dic = {
            True: 'INTERNAL',
            False: 'EXTERNAL'
        }
        cmd = '{0},{1}'.format(self._station_config.COMMAND_DISP_GET_COLOR, internal_external_dic[internal_or_external])
        self._write_serial_cmd(cmd)
        response = self._read_response()
        return self._prase_respose(cmd, response)
    # </editor-fold>

def print_to_console(self, msg):
    pass


############ projectDut is just an example
class projectDut(hardware_station_common.test_station.dut.DUT):
    """
        class for pancake uniformity DUT
            this is for doing all the specific things necessary to DUT
    """
    def __init__(self, serial_number, station_config, operator_interface):
        hardware_station_common.test_station.dut.DUT.__init__(self, serial_number, station_config, operator_interface)
        self._operator_interface = operator_interface
        self._station_config = station_config
        self._serial_number = serial_number

    def is_ready(self):
        pass

    def initialize(self):
        self._operator_interface.print_to_console("Initializing pancake uniformity Fixture\n")

    def close(self):
        self._operator_interface.print_to_console("Closing pancake uniformity Fixture\n")

    def __getattr__(self, item):
        def not_find(*args, **kwargs):
            pass
        if item in ['screen_on', 'screen_off', 'display_color', 'reboot', 'display_image', 'nvm_read_statistics',
                    'nvm_write_data', '_get_color_ext', 'render_image']:
            return not_find

if __name__ == "__main__" :

    class cfgstub(object):
        pass

    station_config = cfgstub()
    station_config.DUT_COMPORT = "COM14"
    station_config.DUT_DISPLAYSLEEPTIME = 0.1
    station_config.DUT_RENDER_ONE_IMAGE_TIMEOUT = 0
    station_config.COMMAND_DISP_HELP = "$c.help"
    station_config.COMMAND_DISP_VERSION_GRP = ['mcu', 'hw', 'fpga']
    station_config.COMMAND_DISP_VERSION = "Version"
    station_config.COMMAND_DISP_GETBOARDID = "getBoardID"
    station_config.COMMAND_DISP_POWERON = "DUT.powerOn,FPGA_compressMode"
    # COMMAND_DISP_POWERON = "DUT.powerOn,SSD2832_BistMode"
    station_config.COMMAND_DISP_POWEROFF = "DUT.powerOff"
    station_config.COMMAND_DISP_RESET = "Reset"
    station_config.COMMAND_DISP_SETCOLOR = "SetColor"
    station_config.COMMAND_DISP_SHOWIMAGE = "ShowImage"
    station_config.COMMAND_DISP_READ = "MIPI.Read"
    station_config.COMMAND_DISP_WRITE = "MIPI.Write"
    station_config.COMMAND_DISP_2832WRITE = "t.2832_MIPI_WRITE"
    station_config.COMMAND_DISP_VSYNC = "REFRESHRATE"

    station_config.COMMAND_NVM_WRITE_CNT = 'NVMWCNT'
    station_config.COMMAND_NVM_READ = 'NVMRead'
    station_config.COMMAND_NVM_WRITE = 'NVMWrite'

    station_config.COMMAND_DISP_POWERON_DLY = 1.5
    station_config.COMMAND_DISP_RESET_DLY = 1
    station_config.COMMAND_DISP_SHOWIMG_DLY = 0.5
    station_config.COMMAND_DISP_POWEROFF_DLY = 0.2

    import sys
    import types

    sys.path.append(r'..\..')

    station_config.print_to_console = types.MethodType(print_to_console, station_config)
    station_config.IS_VERBOSE = True

    # the_unit = projectDut(station_config, station_config, station_config)
    the_unit = pancakeDut(station_config, station_config, station_config)

    for idx in range(0, 2):

        print('Loop ---> {}'.format(idx))
        # !!! image format: 1800 * 1920, bit depth: 24, format: png/bmp
        pics = []
        if os.path.exists('img'):
            for c in os.listdir('img'):
                if c.endswith(".bmp") or c.endswith('.png'):
                    pics.append(r'img\{}'.format(c))

        print('pic - count {0}'.format(len(pics)))
        # the_unit.render_image(pics)

        the_unit.initialize()
        arr = the_unit.nvm_read_data()

        try:
            # the_unit.reboot()
            time.sleep(0.5)
            the_unit.screen_on()
            pprint.pprint(the_unit.nvm_read_statistics())
            raw_data = the_unit.nvm_read_data()
            r = raw_data[0]

            for c in [(0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255)]:
                the_unit.display_color(c)
                time.sleep(0.1)

            for c in range(0, len(pics)):  # show image in DDR
                the_unit.display_image(c, True)
                time.sleep(0.5)

            the_unit.screen_off()
        except Exception as e:
            print(e)
        finally:
            time.sleep(2)
            the_unit.close()
