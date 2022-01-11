from typing import Callable
import hardware_station_common.test_station.test_station as test_station
import psutil
import test_station.test_fixture.test_fixture_seacliff_vid as test_fixture_seacliff_vid
from test_station.test_fixture.test_fixture_project_station import projectstationFixture
import test_station.test_equipment.test_equipment_seacliff_vid as test_equipment_seacliff_vid
from test_station.dut.dut import pancakeDut, projectDut, DUTError
import hardware_station_common.utils.os_utils as os_utils
import time
import os
import types
import re
import pprint
import glob
import numpy as np
import sys
import cv2
import multiprocessing as mp
import json
import collections
import math
import csv


class seacliffVidStationError(Exception):
    pass


def chk_and_set_measured_value_by_name(test_log, item, value):
    """

    :type test_log: test_station.TestRecord
    """
    if item in test_log.results_array():
        test_log.set_measured_value_by_name(item, value)
    # else:
    #     pprint.pprint(item)


def limit_cpu():
    p = psutil.Process(os.getpid())
    p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)


class seacliffVidStation(test_station.TestStation):
    """
        seacliffvid Station
    """

    def __init__(self, station_config, operator_interface):
        test_station.TestStation.__init__(self, station_config, operator_interface)
        self._fixture = test_fixture_seacliff_vid.seacliffVidFixture(station_config, operator_interface)
        self._equip = test_equipment_seacliff_vid.seacliffVidEquipment(station_config, operator_interface)
        if self._station_config.FIXTURE_SIM:
            self._fixture = projectstationFixture(station_config, operator_interface)
        self._overall_errorcode = ''
        self._first_failed_test_result = None
        self._the_unit: projectDut = None
        self._is_screen_on_by_op = False
        self._is_cancel_test_by_op = False
        self._retries_screen_on = 0
        self._sw_version = '0.0.1'

    def initialize(self):
        try:
            self._operator_interface.print_to_console("Initializing seacliff vid station...\n")
            self._fixture.initialize()
            self._equip.initialize()
        except:
            raise

    def close(self):
        self._operator_interface.print_to_console("Close...\n")
        self._operator_interface.print_to_console("\there, I'm shutting the station down..\n")
        self._equip.close()
        self._equip = None
        self._fixture.close()
        self._fixture = None

    def _query_dual_start(self):
        serial_number = self._latest_serial_number
        self._operator_interface.print_to_console("Testing Unit %s\n" % serial_number)
        self._the_unit = pancakeDut(serial_number, self._station_config, self._operator_interface)
        if hasattr(self._station_config, 'DUT_SIM') and self._station_config.DUT_SIM:
            self._the_unit = projectDut(serial_number, self._station_config, self._operator_interface)

        # TODO:  Initialized the DUT Simply
        ready = False
        power_on_trigger = False
        self._retries_screen_on = 0
        self._is_screen_on_by_op = False
        self._is_cancel_test_by_op = False
        self._probe_con_status = False
        timeout_for_btn_idle = (20 if not hasattr(self._station_config, 'TIMEOUT_FOR_BTN_IDLE')
                                    else self._station_config.TIMEOUT_FOR_BTN_IDLE)
        timeout_for_dual = timeout_for_btn_idle
        try:
            self._fixture.flush_data()
            self._fixture.power_on_button_status(False)
            time.sleep(self._station_config.FIXTURE_SOCK_DLY)
            self._fixture.start_button_status(False)
            time.sleep(self._station_config.FIXTURE_SOCK_DLY)
            self._fixture.power_on_button_status(True)
            time.sleep(self._station_config.FIXTURE_SOCK_DLY)
            self._the_unit.initialize()
            self._the_unit.nvm_speed_mode(mode='normal')
            self._operator_interface.print_to_console("Initialize DUT... \n")
            while timeout_for_dual > 0:
                if ready or self._is_cancel_test_by_op:
                    break
                msg_prompt = 'Load DUT, and then Press PowerOn-Btn (Lit up) in %s S...'
                if power_on_trigger:
                    msg_prompt = 'Press Dual-Btn(Load)/PowerOn-Btn(Re Lit up)  in %s S...'
                self._operator_interface.prompt(msg_prompt % timeout_for_dual, 'yellow')
                if self._station_config.FIXTURE_SIM:
                    self._is_screen_on_by_op = True
                    self._the_unit.screen_on()
                    ready = True
                    continue

                if (hasattr(self._station_config, 'DUT_LOAD_WITHOUT_OPERATOR')
                        and self._station_config.DUT_LOAD_WITHOUT_OPERATOR is True):
                    self._fixture.load()
                    ready_status = 0
                else:
                    ready_status = self._fixture.is_ready()
                if ready_status is not None:
                    if ready_status == 0x00:  # load DUT automatically and then screen on
                        ready = True  # Start to test.
                        self._is_screen_on_by_op = True
                        if self._retries_screen_on == 0:
                            self._the_unit.screen_on()
                        self._the_unit.display_color((255, 0, 0))
                        self._fixture.power_on_button_status(False)
                    elif ready_status == 0x03 or ready_status == 0x02:
                        self._operator_interface.print_to_console('Try to lit up DUT.\n')
                        self._retries_screen_on += 1
                        # power the dut on normally.
                        if power_on_trigger:
                            self._the_unit.screen_off()
                            # self._the_unit.reboot()  # Reboot
                        self._the_unit.screen_on()
                        power_on_trigger = True
                        # check the color sensor
                        timeout_for_dual = timeout_for_btn_idle
                        self._fixture.power_on_button_status(False)
                        time.sleep(self._station_config.FIXTURE_SOCK_DLY)
                        self._fixture.start_button_status(True)
                    elif ready_status == 0x01:
                        self._is_cancel_test_by_op = True  # Cancel test.
                time.sleep(0.1)
                timeout_for_dual -= 1
        except (seacliffVidStationError, DUTError, RuntimeError) as e:
            self._operator_interface.operator_input(None, str(e), msg_type='error')
            self._operator_interface.print_to_console('exception msg %s.\n' % str(e))
        finally:
            # noinspection PyBroadException
            try:
                if not ready:
                    if not self._is_cancel_test_by_op:
                        self._operator_interface.print_to_console(
                            'Unable to get start signal in %s from fixture.\n' % timeout_for_dual)
                    else:
                        self._operator_interface.print_to_console(
                            'Cancel start signal from dual %s.\n' % timeout_for_dual)
                    self._the_unit.close()
                    self._the_unit = None
                self._fixture.start_button_status(False)
                time.sleep(self._station_config.FIXTURE_SOCK_DLY)
                self._fixture.power_on_button_status(False)
            except Exception as e:
                self._operator_interface.operator_input(None, str(e), msg_type='error')
                self._operator_interface.print_to_console('exception msg %s.\n' % str(e))
            self._operator_interface.prompt('', 'SystemButtonFace')

    def get_test_item_pattern(self, name):
        pattern_info = None
        for c in self._station_config.TEST_ITEM_PATTERNS:
            if c.get('name') and c['name'] == name:
                pattern_info = c
        return pattern_info

    def render_pattern_on_dut(self, pattern_name, pattern_value):
        msg = f'try to render image  {pattern_name} -> {pattern_value}.\n'
        self._operator_interface.print_to_console(msg)
        pattern_value_valid = True
        if isinstance(pattern_value, (int, str)):
            self._the_unit.display_image(pattern_value, False)
        elif isinstance(pattern_value, tuple):
            if len(pattern_value) == 0x03:
                self._the_unit.display_color(pattern_value)
            else:
                pattern_value_valid = False
        else:
            pattern_value_valid = False
        return pattern_value_valid

    def _do_test(self, serial_number, test_log):
        self._overall_result = False
        self._overall_errorcode = ''

        self._operator_interface.print_to_console(f"Testing Unit {self._latest_serial_number}\n")
        """

               @type test_log: test_station.test_log.test_log
               """
        msg0 = f'info --> emulator_dut: {self._station_config.DUT_SIM},' \
               f' emulator_equip: {self._station_config.EQUIPMENT_SIM}, ' \
               f'emulator_fixture: {self._station_config.FIXTURE_SIM},' \
               f'ver: {self._sw_version}\n'
        self._operator_interface.print_to_console(msg0)

        self._query_dual_start()
        if self._the_unit is None:
            raise test_station.TestStationProcessControlError(f'Fail to query dual_start for DUT {serial_number}.')
        self._probe_con_status = True
        # if not self._station_config.FIXTURE_SIM:
        #     self._probe_con_status = self._fixture.query_probe_status() == 0

        self._overall_result = False
        self._overall_errorcode = ''
        latest_pattern_value_bak = None
        cpu_count = mp.cpu_count()
        cpu_count_used = self._station_config.TEST_CPU_COUNT
        self._pool = mp.Pool(cpu_count_used, limit_cpu)
        try:
            self._operator_interface.print_to_console(f"Initialize Test condition.={cpu_count_used}/{cpu_count}.. \n")
            self._operator_interface.print_to_console(
                "\n*********** Fixture at %s to load DUT %s ***************\n"
                % (self._station_config.FIXTURE_COMPORT, self._station_config.DUT_COMPORT))

            self._operator_interface.print_to_console("Testing Unit %s\n" % self._the_unit.serial_number)
            self._operator_interface.print_to_console("Initialize DUT... \n")
            self._the_unit.screen_on()

            test_log.set_measured_value_by_name_ex = types.MethodType(chk_and_set_measured_value_by_name, test_log)

            self._operator_interface.print_to_console("Testing Unit %s\n" % self._the_unit.serial_number)
            test_log.set_measured_value_by_name_ex('SW_VERSION', self._sw_version)
            test_log.set_measured_value_by_name_ex('EQUIP_SN', self._equip.camera_sn)
            test_log.set_measured_value_by_name_ex('SPEC_VERSION', self._station_config.SPEC_VERSION)

            test_log.set_measured_value_by_name_ex('Carrier_ProbeConnectStatus', self._probe_con_status)
            test_log.set_measured_value_by_name_ex("DUT_ScreenOnRetries", self._retries_screen_on)
            test_log.set_measured_value_by_name_ex("DUT_ScreenOnStatus", self._is_screen_on_by_op)
            test_log.set_measured_value_by_name_ex("DUT_CancelByOperator", self._is_cancel_test_by_op)

            uni_file_name = re.sub('_x.log', '', test_log.get_filename())
            capture_path = os.path.join(self._station_config.RAW_IMAGE_LOG_DIR, uni_file_name)
            if self._station_config.EQUIPMENT_SIM:
                uut_dirs = [c for c in glob.glob(os.path.join(self._station_config.RAW_IMAGE_LOG_DIR, r'*'))
                            if os.path.isdir(c)
                            and os.path.relpath(c, self._station_config.RAW_IMAGE_LOG_DIR)
                                .upper().startswith(serial_number.upper())]
                if len(uut_dirs) > 0:
                    capture_path = uut_dirs[-1]

            for pattern_name, __ in self._station_config.TEST_ITEM_POS.items():
                pattern_info = self.get_test_item_pattern(pattern_name)
                if not pattern_info:
                    self._operator_interface.print_to_console(
                        'Unable to find information for pattern: %s \n' % pattern_name)
                    continue

                if latest_pattern_value_bak != pattern_info['pattern']:
                    pattern_value_valid = self.render_pattern_on_dut(pattern_name, pattern_info['pattern'])
                    if not pattern_value_valid:
                        self._operator_interface.print_to_console(
                            'Unable to change pattern: {0} = {1} \n'.format(pattern_name, pattern_info['pattern']))
                        continue
                    latest_pattern_value_bak = pattern_info['pattern']
                self._operator_interface.print_to_console(f'capture image for pattern: {pattern_name}\n')
                if not os.path.exists(os.path.join(capture_path, 'exp')):
                    os_utils.mkdir_p(os.path.join(capture_path, 'exp'))
                self._equip.do_measure_and_export(pattern_name, capture_path)

            self._operator_interface.print_to_console(f'post image processed.\n')
            for pattern_name, pattern_config in self._station_config.TEST_ITEM_POS.items():
                fns = glob.glob(
                    os.path.join(capture_path, 'exp',
                                rf'{pattern_name}_Depth3D_ViewObjectOrthographic_To_Reference_AfterSettings.tiff'))
                fn = fns[0] if len(fns) == 0x01 else None
                if not fn:
                    self._operator_interface.print_to_console(f'Unable to find tiff file for {pattern_name}\n')
                    continue
                from skimage.io import imread
                img = imread(os.path.join(fn, fn))
                roi_items = pattern_config['ROI']
                with np.errstate(divide='ignore', invalid='ignore'):
                    for p_name, roi in roi_items.items():
                        x_tl, y_tl, x_br, y_br = roi
                        image_x = np.array(img[:, :, 0])
                        image_y = np.array(img[:, :, 1])
                        image_z = np.array(img[:, :, 2])
                        image_a = np.array(img[:, :, 3])
                        maskx = np.where([image_x >= x_tl, image_x <= x_br], 1, 0)
                        masky = np.where([image_y >= y_tl, image_y <= y_br], 1, 0)
                        maskx = np.multiply(maskx[0], maskx[1])
                        masky = np.multiply(masky[0], masky[1])

                        maskxy = np.multiply(maskx, masky)
                        maskxy_position = np.nonzero(maskxy)
                        raw_x = image_x[maskxy_position]
                        raw_y = image_y[maskxy_position]
                        raw_z = image_z[maskxy_position]
                        raw_a = image_a[maskxy_position]
                        exp_csv_fn = os.path.join(capture_path, 'exp', f'{pattern_name}_{p_name}.csv')
                        if not os.path.exists(os.path.dirname(exp_csv_fn)):
                            os_utils.mkdir_p(os.path.dirname(exp_csv_fn))
                        with open(exp_csv_fn, 'w', newline='') as csv_file:
                            field_names = ['x', 'y', 'z', 'a']
                            writer = csv.writer(csv_file, dialect='excel')
                            writer.writerow(field_names)
                            writer.writerows(tuple(zip(raw_x, raw_y, raw_z, raw_a)))
                        if len(raw_z) > 0:
                            test_log.set_measured_value_by_name_ex(f'{pattern_name}_{p_name}', np.mean(raw_z))
                        del image_x, image_y, image_z, image_a, raw_x, raw_y, raw_z, raw_a
                        del maskx, masky, maskxy, maskxy_position
                del img

            self._operator_interface.print_to_console(f'test sequence for VID station finished.\n')

        except seacliffVidStationError:
            self._operator_interface.print_to_console(f"VID for {serial_number} Test Failure\n")
            return self.close_test(test_log)
        else:
            return self.close_test(test_log)

        finally:
            try:
                self._fixture.unload()
                self._the_unit.close()
            except:
                pass

    def close_test(self, test_log):
        ### Insert code to gracefully restore fixture to known state, e.g. clear_all_relays() ###
        self._overall_result = test_log.get_overall_result()
        self._first_failed_test_result = test_log.get_first_failed_test_result()
        return self._overall_result, self._first_failed_test_result

    def is_ready(self):
        return True

    def validate_sn(self, serial_num):
        self._latest_serial_number = serial_num
        return test_station.TestStation.validate_sn(self, serial_num)
