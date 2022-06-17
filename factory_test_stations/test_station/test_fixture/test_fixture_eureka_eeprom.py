import hardware_station_common.test_station.test_fixture
import serial

import test_station.test_fixture.gxipy as gx
from PIL import Image
import cv2
import os
import numpy as np
import time
import re


class EurekaEEPROMFixtureErr(Exception):
    def __init__(self, msg):
        self._msg = msg


class EurekaEEPROMFixture(hardware_station_common.test_station.test_fixture.TestFixture):
    """
        class for Eureka EEPROM Fixture
            this is for doing all the specific things necessary to interface with equipment
    """
    def __init__(self, station_config, operator_interface):
        hardware_station_common.test_station.test_fixture.TestFixture.__init__(self, station_config, operator_interface)
        self._device_manager = None
        self._camera_sn = None
        self._camera = None  # type: gx.Device
        self._verbose = station_config.IS_VERBOSE
        self._serial_port: serial.Serial = None

    def is_ready(self):
        pass

    def initialize(self, **kwargs):
        self._operator_interface.print_to_console("Initializing Eureka EEPROM Fixture\n")
        self._serial_port = kwargs.get('sp')
        if self._station_config.CAMERA_VERIFY_ENABLE:
            self._device_manager = gx.DeviceManager()
            dev_num, dev_info_list = self._device_manager.update_device_list()
            dev_list = [c for c in dev_info_list if c.get('model_name') == 'MER-132-43U3C']
            if len(dev_list) != 0x01:
                raise EurekaEEPROMFixtureErr('Fail to init instrument. cam = {0}'.format(len(dev_list)))
            self._camera_sn = dev_list[0].get('sn')
            self._operator_interface.print_to_console('Camera for verification. sn = {0}\n'.format(self._camera_sn))
            self._camera = self._device_manager.open_device_by_sn(dev_list[0].get('sn'))
            cfg_file = os.path.basename(os.path.join(self._station_config.CAMERA_CONFIG_FILE))
            self._operator_interface.print_to_console('Init camera from configuration file = {0}\n'.format(cfg_file))
            self._camera.import_config_file(self._station_config.CAMERA_CONFIG_FILE, True)
            self._camera.TriggerMode.set(gx.GxSwitchEntry.OFF)
            self._camera.ExposureTime.set(self._station_config.CAMERA_EXPOSURE)
            self._camera.Gain.set(self._station_config.CAMERA_GAIN)

    def close(self):
        self._operator_interface.print_to_console("Closing Eureka EEPROM Fixture\n")

    def display_color_check(self, color):
        norm_color = tuple([c / 255.0 for c in color])
        color1 = np.float32([[norm_color]])
        hsv = cv2.cvtColor(color1, cv2.COLOR_RGB2HSV)
        h, s, v = tuple(hsv[0, 0, :])
        self._operator_interface.print_to_console('COLOR: = {},{},{}\n'.format(h, s, v))
        return (self._station_config.DISP_CHECKER_L_HsvH <= h <= self._station_config.DISP_CHECKER_H_HsvH and
                self._station_config.DISP_CHECKER_L_HsvS <= s <= self._station_config.DISP_CHECKER_H_HsvS)

    def CheckImage(self, exp_fn, lower, upper):
        img = self._captureImg()  # type: np.ndarray
        if img is None:
            raise EurekaEEPROMFixtureErr('Fail to capture image from camera.')

        roi_img = img[self._station_config.CAMERA_CHECK_ROI[1]:self._station_config.CAMERA_CHECK_ROI[3],
              self._station_config.CAMERA_CHECK_ROI[0]:self._station_config.CAMERA_CHECK_ROI[2]]
        cv2.imwrite(exp_fn, roi_img)

        hsv = cv2.cvtColor(roi_img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lowerb=np.array(lower), upperb=np.array(upper))
        nonzero_count = np.count_nonzero(mask)
        roi_w, roi_h, __ = np.shape(hsv)
        self._operator_interface.print_to_console('color statistics: {0} /{1}\n'.format(nonzero_count, roi_h * roi_w))
        return nonzero_count/(roi_h * roi_w)

    def _captureImg(self):
        if self._camera is None:
            return
        cv_image = None
        try:
            self._camera.stream_on()
            raw_image = self._camera.data_stream[0].get_image()  # type: Image
            rgb_image = raw_image.convert('RGB')
            numpy_image = rgb_image.get_numpy_array()
            cv_image = cv2.cvtColor(np.asarray(numpy_image), cv2.COLOR_RGB2BGR)
        finally:
            self._camera.stream_off()
            return cv_image

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
            print('rev command <---------- {0}'.format(response))
        return response

    def unload(self):
        # $C.Module.Out   $P.Module.Out,0000
        self._write_serial_cmd(f'{self._station_config.COMMAND_MODULE_OUT}')
        response = self._read_response()
        recvobj = self._prase_respose(self._station_config.COMMAND_MODULE_OUT, response)
        if recvobj is None:
            raise EurekaEEPROMFixtureErr("Fail module_out because can't receive any data from dut.")
        if int(recvobj[0]) != 0x00:
            raise EurekaEEPROMFixtureErr("Exit module_out because rev err msg. Msg = {}".format(recvobj))
        return recvobj[0]

    def disable_dual_btn(self):
        # $C.DISABLE.STARTBTN   $P.DISABLE.STARTBTN,0000
        self._write_serial_cmd(f'{self._station_config.COMMAND_DUAL_DISABLE}')
        response = self._read_response()
        recvobj = self._prase_respose(self._station_config.COMMAND_DUAL_DISABLE, response)
        if recvobj is None:
            raise EurekaEEPROMFixtureErr("Fail disable_dual_btn because can't receive any data from dut.")
        if int(recvobj[0]) != 0x00:
            raise EurekaEEPROMFixtureErr("Exit disable_dual_btn because rev err msg. Msg = {}".format(recvobj))
        return recvobj[0]
