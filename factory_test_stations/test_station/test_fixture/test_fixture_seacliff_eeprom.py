import hardware_station_common.test_station.test_fixture
import test_station.test_fixture.gxipy as gx
from PIL import Image
import cv2
import os
import numpy as np


class seacliffeepromFixtureErr(Exception):
    def __init__(self, msg):
        self._msg = msg


class seacliffeepromFixture(hardware_station_common.test_station.test_fixture.TestFixture):
    """
        class for pancake eeprom Equipment
            this is for doing all the specific things necessary to interface with equipment
    """
    def __init__(self, station_config, operator_interface):
        hardware_station_common.test_station.test_fixture.TestFixture.__init__(self, station_config, operator_interface)
        self._device_manager = None
        self._camera_sn = None
        self._camera = None  # type: gx.Device

    def is_ready(self):
        pass

    def initialize(self):
        self._operator_interface.print_to_console("Initializing pancake eeprom Equipment\n")
        if self._station_config.CAMERA_VERIFY_ENABLE:
            self._device_manager = gx.DeviceManager()
            dev_num, dev_info_list = self._device_manager.update_device_list()
            dev_list = [c for c in dev_info_list if c.get('model_name') == 'MER-132-43U3C']
            if len(dev_list) != 0x01:
                raise seacliffeepromFixtureErr('Fail to init instrument. cam = {0}'.format(len(dev_list)))
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
        self._operator_interface.print_to_console("Closing pancake eeprom Equipment\n")

    def display_color_check(self, color):
        norm_color = tuple([c / 255.0 for c in color])
        color1 = np.float32([[norm_color]])
        hsv = cv2.cvtColor(color1, cv2.COLOR_RGB2HSV)
        h, s, v = tuple(hsv[0, 0, :])
        self._operator_interface.print_to_console('COLOR: = {},{},{}\n'.format(h, s, v))
        return (self._station_config.DISP_CHECKER_L_HsvH <= h <= self._station_config.DISP_CHECKER_H_HsvH and
                self._station_config.DISP_CHECKER_L_HsvS <= s <= self._station_config.DISP_CHECKER_H_HsvS)

    def CheckImage(self, pattern, lower, upper):
        img = self._captureImg()  # type: np.ndarray
        if img is None:
            raise seacliffeepromFixtureErr('Fail to capture image from camera.')

        roi_img = img[self._station_config.CAMERA_CHECK_ROI[1]:self._station_config.CAMERA_CHECK_ROI[3],
              self._station_config.CAMERA_CHECK_ROI[0]:self._station_config.CAMERA_CHECK_ROI[2]]
        cv2.imwrite('{0}.bmp'.format(pattern), roi_img)

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


if __name__ == '__main__':
    print('-------------------------')
    # sys.path.append(r'C:\Program Files\Daheng Imaging\GalaxySDK\APIDll\Win64')
    img = cv2.imread('test_000.bmp')
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    hsv = hsv[0:100, 80: 100]
    low_hsv = np.array([0, 43, 46])
    high_hsv = np.array([10, 255, 255])
    mask = cv2.inRange(hsv, low_hsv, high_hsv)
    nonzero = np.count_nonzero(mask)
    dd = np.size(mask)

    CAMERA_CHECK_CFG = [
        {
            'pattern': (255, 0, 0),
            'chk_lsl': [0, 43, 46],
            'chk_usl': [10, 255, 255],
            'determine': [50, 100],
        }
    ]

    device_manager = gx.DeviceManager()
    dev_num, dev_info_list = device_manager.update_device_list()
    try:
        dev_list = [c for c in dev_info_list if c.get('model_name') == 'MER-132-43U3C']
        if len(dev_list) == 0x01:
            cam = device_manager.open_device_by_sn(dev_list[0].get('sn'))
            cfg = r'C:\oculus\factory_test_omi\factory_test_stations\config\MER-132-43U3C(FQ0200080140).txt'
            cam.import_config_file(cfg, True)

            cam.TriggerMode.set(gx.GxSwitchEntry.OFF)
            cam.ExposureTime.set(80000.0)
            cam.Gain.set(1.0)
            cam.stream_on()

            raw_image = cam.data_stream[0].get_image()  # type: Image
            if raw_image is None:
                print('Fail to capture image.')
            else:
                rgb_image = raw_image.convert('RGB')
                numpy_image = rgb_image.get_numpy_array()
                bgr_img = cv2.cvtColor(np.asarray(numpy_image), cv2.COLOR_RGB2BGR)
                saved_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)
                cv2.imwrite('test_000.bmp', saved_img)
            cam.stream_off()
            cam.close_device()
    except Exception as e:
        print('exception {0}.\n'.format(e.args))

    print('-----------------------end')