#!/usr/bin/python
# -*- Coding: UTF-8 -*- #
__author__ = 'elton'

import re
import numpy as np
import sys
import socket
import serial
import struct
import logging
import time
import string
import dutchecker as dutchecker

class displayCtrlMyzyError(Exception):
    pass

class displayCtrlBoard:
    HOST = "127.0.0.1"
    PORT = 1234

    SUCCESS_CODE = 0000
    DISPLAY_IMAGE_FILE = 1
    DISPLAY_IMAGE_RAW = 2
    DISPLAY_SOLID_COLOR = 3
    FRAG_SHADER = 4
    VERT_SHADER = 5
    LOAD_MURA_DATA = 6
    UNLOAD_MURA_DATA = 7

    def __init__(self, station_config, operator_interface):
        self.is_screen_poweron = False
        self._serial_port = None
        self._station_config = station_config
        self._operator_interface = operator_interface
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self._start_delimiter = "$"
        self._end_delimiter = '\r\n'
        self._spliter = ','

    def close(self):
        if self._serial_port is not None:
            self._serial_port.close()
            self._serial_port = None

    def initialize(self):
        self.is_screen_poweron = False
        self._serial_port = serial.Serial(self._station_config.DUT_COMPORT,
                      baudrate = 115200,
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
            raise displayCtrlMyzyError('Unable to open DUT port : %s'%self._station_config.DUT_COMPORT)
            return False
        else:
            print 'DUT %s Initialised. '%self._station_config.DUT_COMPORT
            return True

    def _write_serial(self, input_bytes):
        bytes_written = self._serial_port.write(input_bytes)
        self._serial_port.flush()
        return bytes_written

    def _write_serial_cmd(self, command):
        cmd = '$c.{}\r\n'.format(command)
        self._serial_port.write(cmd)
        self._serial_port.flush()

    def _read_response(self):
        response = []
        while True:
            line_in = self._serial_port.readline()
            if line_in != '':
                response.append(line_in)
            else:
                break
        print "<--- {}".format(response)
        return response

    def get_median_vsync_microseconds(self):
        # return self._station_config.DEFAULT_VSYNC_US

        recvobj = self._vsyn_time()
        if recvobj is None:
            raise RuntimeError("Exit display_color because can't receive any data from dut.")
        else:
            grpt = re.match(r'(\d*[\.]?\d*)', recvobj[1])
            grpf = re.match(r'(\d*[\.]?\d*)', recvobj[2])
            if grpf is None or grpt is None:
                raise RuntimeError("Exit display_color because rev err msg. Msg = {}".format(recvobj))
            return string.atof(grpt.group(0))

    def display_color(self, c=(255,255,255)):
        if self.is_screen_poweron:
            recvobj = self._setColor(c)
            if recvobj is None:
                raise RuntimeError("Exit display_color because can't receive any data from dut.")
            elif int(recvobj[0]) != 0x00:
                raise RuntimeError("Exit display_color because rev err msg. Msg = {}".format(recvobj))

    def screen_on(self):
        if not self.is_screen_poweron:
            dutchecker = dutchecker.dut_checker()
            #  camera
            if self._station_config.DISP_CHECKER_ENABLE:
                dutchecker.open()
                time.sleep(self._station_config.DISP_CHECKER_DLY)

            retryCount = 1
            self._power_off()
            time.sleep(0.5)
            while retryCount <= self._station_config.DUT_ON_MAXRETRY and not self.is_screen_poweron:
                recvobj = self._power_on()
                if recvobj is None:
                    raise RuntimeError("Exit power_on because can't receive any data from dut.")
                else:
                    if self._station_config.DISP_CHECKER_ENABLE:
                        score = dutchecker.do_checker()
                        if score is not None and max(score) >= self._station_config.DISP_CHECKER_L_SCORE:
                            self.is_screen_poweron = True
                            if self._station_config.DISP_CHECKER_IMG_SAVED:
                                fn0 = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
                                fn = 'DUT_CHECKER_{0}_{1}.jpg'.format(fn0, retryCount + 1)
                                dutchecker.save_log_img(fn)
                    else:
                        self.is_screen_poweron = True

                if not self.is_screen_poweron:
                    msg = 'Retry power_on {}/{} times.\n'.format(retryCount + 1, self._station_config.DUT_ON_MAXRETRY)
                    self._power_off()
                    time.sleep(0.5)
                    self._operator_interface.print_to_console(msg)
                if retryCount >= self._station_config.DUT_ON_MAXRETRY:
                    raise RuntimeError("Exit power_on because rev err msg. Msg = {0}".format(recvobj))
                else:
                    retryCount = retryCount + 1

    def screen_off(self):
        if self.is_screen_poweron:
            recvobj = self._power_off()
            if recvobj is None:
                raise RuntimeError("Exit power_off because can't receive any data from dut.")
            elif int(recvobj[0]) != 0x00:
                raise RuntimeError("Exit power_off because rev err msg. Msg = {}".format(recvobj))
            else:
                self.is_screen_poweron = False

    def display_image(self, imagefile):
        recvobj = self._showImage(imagefile)
        if recvobj is None:
            raise RuntimeError("Exit disp_image because can't receive any data from dut.")
        elif int(recvobj[0]) != 0x00:
            raise RuntimeError("Exit disp_image because rev err msg. Msg = {}".format(recvobj))

    def version(self):
        return self._version("mcu")

    ###
    # COMMUNICAION INTERFACE
    ###

    def _vsyn_time(self):
        self._write_serial_cmd(self._station_config.COMMAND_DISP_VSYNC)
        response = self._read_response()
        return self._prase_respose(self._station_config.COMMAND_DISP_VSYNC, response)

    def _help(self):
        self._write_serial_cmd(self._station_config.COMMAND_DISP_HELP)
        time.sleep(1)
        response = self._read_response()
        print response
        value = []
        for item in response[0:len(response)-1]:
            value.append(item)
        return value

    def _version(self, model_name):
        self._write_serial_cmd("%s,%s"%(self._station_config.COMMAND_DISP_VERSION,model_name))
        response = self._read_response()
        return self._prase_respose(self._station_config.COMMAND_DISP_VERSION, response)

    def _get_boardId(self):
        self._write_serial_cmd(self._station_config.COMMAND_DISP_GETBOARDID)
        time.sleep(1)
        response = self._read_response()
        return self._prase_respose(self._station_config.COMMAND_DISP_GETBOARDID, response)

    def _prase_respose(self, command, response):

        print "command : {},,,{}".format(command, response)

        if response is None:
            return None
        cmd1 = command.split(self._spliter)[0]
        respstr = ''.join(response).upper()
        cmd = ''.format(cmd1).upper()
        if cmd not in respstr:
            return None
        values = respstr.split(self._spliter)
        if len(values) == 1:
            raise RuntimeError('display ctrl rev data format error. <- ' + respstr)


        return  values[1:]

    def _power_on(self):
        self._write_serial_cmd(self._station_config.COMMAND_DISP_POWERON)
        time.sleep(self._station_config.COMMAND_DISP_POWERON_DLY)
        response = self._read_response()
        return self._prase_respose(self._station_config.COMMAND_DISP_POWERON, response)

    def _power_off(self):
        self._write_serial_cmd(self._station_config.COMMAND_DISP_POWEROFF)
        time.sleep(self._station_config.COMMAND_DISP_POWEROFF_DLY)
        response = self._read_response()
        return self._prase_respose(self._station_config.COMMAND_DISP_POWEROFF, response)

    def _reset(self):
        self._write_serial_cmd(self._station_config.COMMAND_DISP_RESET)
        time.sleep(self._station_config.COMMAND_DISP_RESET_DLY)
        response = self._read_response()
        return self._prase_respose(self._station_config.COMMAND_DISP_RESET, response)

    def _showImage(self, imageindex):
        command ='{},{}'.format(self._station_config.COMMAND_DISP_SHOWIMAGE, imageindex)
        self._write_serial_cmd(command)
        time.sleep(self._station_config.COMMAND_DISP_SHOWIMG_DLY)
        response = self._read_response()
        return self._prase_respose(self._station_config.COMMAND_DISP_SHOWIMAGE, response)

    def _setColor(self, c = (255,255,255)):
        command = '{0},0x{1[0]:X},0x{1[1]:X},0x{1[2]:X}'.format(self._station_config.COMMAND_DISP_SETCOLOR, c)
        self._write_serial_cmd(command)
        time.sleep(1)
        response = self._read_response()
        return self._prase_respose(self._station_config.COMMAND_DISP_SETCOLOR, response)

    def _MIPI_read(self, reg, typ):
        command = '{0},{1},{2}'.format(self._station_config.COMMAND_DISP_READ, reg, typ)
        self._write_serial_cmd(command)
        time.sleep(1)
        response = self._read_response()
        return self._prase_respose(self._station_config.COMMAND_DISP_READ, response)

    def _MIPI_write(self, reg, typ, val):
        command = '{0},{1},{2},{3}'.format(self._station_config.COMMAND_DISP_WRITE, reg, typ, val)
        self._write_serial_cmd(command)
        #time.sleep(1)
        response = self._read_response()
        return self._prase_respose(self._station_config.COMMAND_DISP_WRITE, response)

    def _2832_MIPI_write(self, val):
        # command = "0X0302,25,0x01DE,0xff00,0x10ff,0x2020,0xB410,0x03B4,0xFFE4,0xFFFF,0x207F,0x0810,0x0001,0x0000,0x0000"
        command ="0X0302,25,0x01DE,0x{}00,0x10{},0x2020,0xB410,0x03B4,0xFFE4,0xFFFF,0x207F,0x0810,0x0001,0x0000,0x0000"\
            .format(val[0:2], val[2:4])
        command = '{},{}'.format(self._station_config.COMMAND_DISP_2832WRITE, command)
        self._write_serial_cmd(command)
        return ['0000']

    def _send_displayserver_command(self, commandID, extra=None, data=None):
        extra_bytesize = 0
        data_bytesize = 0
        extra_byteArr = bytearray()
        data_byteArr = bytearray()

        if extra is not None:
            extra_byteArr = bytearray(extra, 'utf8')
        if data is not None:
            if isinstance(data, tuple): #color
                data_byteArr = bytearray(str(data).strip('()'), 'utf8')
            elif isinstance(data, np.ndarray):
                if data.dtype == np.float32:
                    data = (data * 255).round().astype(np.uint8) #convert to uint8
                data_byteArr = bytearray(data, 'utf8')
            else:
                data_byteArr = bytearray(data)
        command = bytearray()
        command.append(commandID)
        command += struct.pack('>I', len(extra_byteArr))
        command += struct.pack('>I', len(data_byteArr))
        command += extra_byteArr
        command += data_byteArr

        s = socket.socket()
        try:
            num_bytes = len(command)
            s.connect((self.HOST, self.PORT))
            sent = s.send(command)
            if sent == 0:
                raise RuntimeError("socket failed to send")
            if sent != num_bytes:
                raise RuntimeError("only " + sent + " of " + num_bytes + " bytes are sent.")
            reply = s.recv(10)
            if not reply:
                raise RuntimeError("socket failed to receive.")
            if str(commandID) not in reply:
                raise RuntimeError("displayCtrlBoard failed to complete commond")
            else:
                msg = "displayCtrlBoard done"
                extras = extra.split(';')
                if commandID == self.DISPLAY_IMAGE_RAW:
                    msg = msg + "displaying raw image of dimension {}x{}".format(extra[2], extra[3])
                elif commandID == self.DISPLAY_IMAGE_FILE:
                    msg = msg + "displaying imgfile: {}".format(data)
                elif commandID == self.DISPLAY_SOLID_COLOR:
                    msg = msg + "displaying color {}".format(str(data))
                elif commandID == self.VERT_SHADER:
                    msg = msg + "updating vertex shader to {}".format(extra)
                elif commandID == self.FRAG_SHADER:
                    msg = msg + "updating fragmen shader to {}".format(extra)
                self._logger.info(msg)
            s.close()
            return sent
        except Exception as err:
            self._logger.error(str(err[0]))

    def disp_imgfile_tcp(self, filename, num_frame = -1, retry = 10):
        num_try = 0
        extra = None
        while not self._send_displayserver_command(self.DISPLAY_IMAGE_FILE, extra, filename):
            time.sleep(1)
            num_try += 1
            self._logger.warning("display server failed {} times, Try again".format(num_try))
            if num_try >= retry:
                raise RuntimeError("Exit because display server failed {} times, check whether it successfully launched.".format(num_try))

if __name__ == '__main__':
    sys.path.append("../..")
    import station_config
    import dutTestUtil

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logging.getLogger(__name__).addHandler(ch)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    station_config.load_station('pancake_pixel')
    # station_config.load_station('pancake_uniformity')
    operator = dutTestUtil.simOperator()
    the_disp = displayCtrlBoard(station_config, operator)
    the_disp.initialize()
    the_disp.version()
    # for idx in ['0008', '0000','0008', '0000']:
    # the_disp._power_on()
        # the_disp.display_image(idx)
        #  time.sleep(1)
        # the_disp._power_off()
        # time.sleep(1)



    # for c in [(255,255,255)]:
    for c in range(0, 5):
        the_disp._power_on()
        time.sleep(1)
        vsync = the_disp.get_median_vsync_microseconds()
        time.sleep(1)
        # the_disp._setColor(c)
        the_disp.display_image(c)
        time.sleep(1)
        the_disp._power_off()

    the_disp.close()

    #
    # the_disp._setColor((1,2,3))
    #
    # the_disp._version("mcu")
    # the_disp.screen_on()
    # time.sleep(2)
    # the_disp.screen_off()
    # time.sleep(2)
    #
    # # the_disp._send_displayserver_command(1, None, None)
    #
    # the_disp.screen_on()



