from typing import Callable
import hardware_station_common.test_station.test_station as test_station
import psutil
import test_station.test_fixture.test_fixture_seacliff_vid as test_fixture_seacliff_vid
from test_station.test_fixture.test_fixture_project_station import projectstationFixture
import test_station.test_equipment.test_equipment_seacliff_vid as test_equipment_seacliff_vid
from test_station.dut.dut import pancakeDut, projectDut, DUTError
import hardware_station_common.utils.os_utils as os_utils
import hardware_station_common.utils.io_utils as io_utils
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
import serial


class seacliffVidStationError(Exception):
    pass


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
        self._panel_left_or_right = None
        self._latest_serial_number = None
        self._fixture_port = None
        self._sw_version = '0.0.1'

    def initialize(self):
        try:
            self._operator_interface.print_to_console("Initializing seacliff vid station...\n")
            # <editor-fold desc="port configuration automatically">
            cfg = 'station_config_seacliff_vid.json'
            station_config = {
                'FixtureCom': 'Fixture',
            }
            com_ports = list(serial.tools.list_ports.comports())
            port_list = [(com.device, com.hwid, com.serial_number, com.description)
                         for com in com_ports if com.serial_number]
            if not os.path.exists(cfg):
                station_config['PORT_LIST'] = port_list
                with open(cfg, 'w') as f:
                    json.dump(station_config, fp=f, indent=4)
            else:
                with open(cfg, 'r') as f:
                    station_config = json.load(f)

            port_err_message = []
            # config the port for fixture
            regex_port = station_config['FixtureCom']
            com_ports = [c[0] for c in port_list if re.search(regex_port, c[2], re.I | re.S)]
            if len(com_ports) != 1:
                port_err_message.append(f'Fixture')
            else:
                self._fixture_port = com_ports[-1]
            # </editor-fold>
            if not self._station_config.FIXTURE_SIM and len(port_err_message) > 0:
                raise seacliffVidStationError(f'Fail to find ports for fixture {";".join(port_err_message)}')

            self._fixture.initialize(fixture_com=self._fixture_port)
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

    def chk_and_set_measured_value_by_name(self, test_log, item, value):
        """

        :type test_log: test_station.TestRecord
        """
        if item in test_log.results_array():
            test_log.set_measured_value_by_name(item, value)
            did_pass = test_log.get_test_by_name(item).did_pass()
            self._operator_interface.update_test_value(item, value, 1 if did_pass else -1)
        # else:
        #     pprint.pprint(item)

    def z_corr(self, zr):
        return 10180 * np.power(zr, -0.2526) - 1823

    def _query_dual_start(self):
        serial_number = self._latest_serial_number
        self._operator_interface.print_to_console("Testing Unit %s\n" % serial_number)
        self._the_unit = pancakeDut(serial_number, self._station_config, self._operator_interface)
        if hasattr(self._station_config, 'DUT_SIM') and self._station_config.DUT_SIM:
            self._the_unit = projectDut(serial_number, self._station_config, self._operator_interface)

        ready = False
        power_on_trigger = False
        self._retries_screen_on = 0
        self._is_screen_on_by_op = False
        self._is_cancel_test_by_op = False
        self._probe_con_status = False
        timeout_for_btn_idle = (20 if not hasattr(self._station_config, 'TIMEOUT_FOR_BTN_IDLE')
                                    else self._station_config.TIMEOUT_FOR_BTN_IDLE)
        timeout_for_dual = time.time()
        try:
            self._fixture.flush_data()
            self._fixture.power_on_button_status(False)
            self._fixture.start_button_status(False)
            self._fixture.power_on_button_status(True)
            self._the_unit.initialize(com_port=self._station_config.DUT_COMPORT,
                                      eth_addr=self._station_config.DUT_ETH_PROXY_ADDR)
            self._the_unit.nvm_speed_mode(mode='normal')
            self._operator_interface.print_to_console("Initialize DUT... \n")
            tm_current = timeout_for_dual
            while tm_current - timeout_for_dual <= timeout_for_btn_idle:
                if ready or self._is_cancel_test_by_op:
                    break
                msg_prompt = 'Load DUT, and then Press PowerOn-Btn (On screen) in %s S...'
                if power_on_trigger:
                    msg_prompt = 'Press Dual-Btn(Load)/PowerOn-Btn(Toggle)  in %s S...'
                tm_data = timeout_for_btn_idle - (tm_current - timeout_for_dual)
                self._operator_interface.prompt(msg_prompt % int(tm_data), 'yellow')
                if self._station_config.FIXTURE_SIM:
                    self._is_screen_on_by_op = True
                    self._the_unit.screen_on()
                    ready = True
                    continue

                if (hasattr(self._station_config, 'DUT_LOAD_WITHOUT_OPERATOR')
                        and self._station_config.DUT_LOAD_WITHOUT_OPERATOR is True):
                    self._fixture.load(self._panel_left_or_right)
                    ready_status = 0
                else:
                    ready_status = self._fixture.is_ready()
                if ready_status is not None:
                    if ready_status in [0x10, 0x11]:  # load DUT automatically and then screen on
                        if ((ready_status == 0x10 and self._panel_left_or_right == 'L') or
                                (ready_status == 0x11 and self._panel_left_or_right == 'R')):
                            ready = True  # Start to test.
                            self._is_screen_on_by_op = True
                            if self._retries_screen_on == 0:
                                self._the_unit.screen_on()
                            self._the_unit.display_color((255, 0, 0))
                            self._fixture.power_on_button_status(False)
                        else:
                            msg = f'Fail to start [{serial_number}]: {ready_status}, {self._panel_left_or_right}'
                            self._operator_interface.print_to_console(msg, 'red')
                    elif ready_status == 0x03 or ready_status == 0x02:
                        self._operator_interface.print_to_console('Try to lit up DUT.\n')
                        self._retries_screen_on += 1
                        # power the dut on normally.
                        if power_on_trigger:
                            self._the_unit.screen_off()
                            power_on_trigger = False
                            self._fixture.button_disable()
                            self._fixture.power_on_button_status(True)
                        else:
                            self._the_unit.screen_on()
                            power_on_trigger = True
                            self._fixture.power_on_button_status(False)
                            self._fixture.button_enable()
                            self._fixture.load_position(self._panel_left_or_right)
                        timeout_for_dual = time.time()
                    elif ready_status == 0x01:
                        self._is_cancel_test_by_op = True  # Cancel test.
                time.sleep(0.1)
        except (seacliffVidStationError, DUTError, RuntimeError) as e:
            self._operator_interface.operator_input(None, str(e), msg_type='error')
            self._operator_interface.print_to_console('exception msg %s.\n' % str(e))
        finally:
            # noinspection PyBroadException
            try:
                if not ready:
                    if not self._is_cancel_test_by_op:
                        self._operator_interface.print_to_console(
                            'Unable to get start signal in %s from fixture.\n' % int(time.time() - timeout_for_dual))
                    else:
                        self._operator_interface.print_to_console(
                            'Cancel start signal from dual %s.\n' % int(time.time() - timeout_for_dual))
                    self._the_unit.close()
                    self._the_unit = None
                self._fixture.start_button_status(False)
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
        pattern_value_valid = False
        if isinstance(pattern_value, (int, str)):
            self._the_unit.display_image(pattern_value, False)
            pattern_value_valid = True
        elif isinstance(pattern_value, tuple) and len(pattern_value) == 0x03:
            self._the_unit.display_color(pattern_value)
            pattern_value_valid = True
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

            test_log.set_measured_value_by_name_ex = types.MethodType(self.chk_and_set_measured_value_by_name, test_log)

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

                sel_pattern_value = None
                if isinstance(pattern_info['pattern'], int) or isinstance(pattern_info['pattern'], str):
                    sel_pattern_value = pattern_info['pattern']
                elif isinstance(pattern_info['pattern'], tuple):
                    if self._panel_left_or_right == 'L':
                        sel_pattern_value = pattern_info['pattern'][0]
                    elif self._panel_left_or_right == 'R':
                        sel_pattern_value = pattern_info['pattern'][1]
                if sel_pattern_value is None:
                    raise seacliffVidStationError(f'unable to parse the pattern: {pattern_name}')

                if latest_pattern_value_bak != sel_pattern_value:
                    pattern_value_valid = self.render_pattern_on_dut(pattern_name, sel_pattern_value)
                    if not pattern_value_valid:
                        self._operator_interface.print_to_console(
                            'Unable to change pattern: {0} = {1} \n'.format(pattern_name, sel_pattern_value))
                        continue
                    latest_pattern_value_bak = sel_pattern_value

                self._operator_interface.print_to_console(f'capture image for pattern: {pattern_name}\n')
                if not os.path.exists(os.path.join(capture_path, 'exp')):
                    os_utils.mkdir_p(os.path.join(capture_path, 'exp'))
                self._equip.do_measure_and_export(pattern_name, capture_path)

            self._operator_interface.print_to_console(f'post image processed.\n')
            for pattern_name, pattern_config in self._station_config.TEST_ITEM_POS.items():
                fns = glob.glob(
                    os.path.join(capture_path, 'exp',
                                rf'{pattern_name}_Depth3D_ViewVirtualUndistorted_To_Reference_AfterSettings.tiff'))
                fn = fns[0] if len(fns) == 0x01 else None
                if not fn:
                    self._operator_interface.print_to_console(f'Unable to find tiff file for {pattern_name}\n')
                    continue
                from skimage.io import imread
                img = imread(os.path.join(capture_path, fn))
                roi_items = pattern_config['ROI']
                with np.errstate(divide='ignore', invalid='ignore'):
                    for p_name, roi in roi_items.items():
                        self._operator_interface.print_to_console(f'parse data {p_name}: {roi} \n')
                        x_tl, y_tl, x_br, y_br = roi
                        image_x = np.array(img[:, :, 0])
                        image_y = np.array(img[:, :, 1])
                        image_z = np.array(img[:, :, 2])
                        image_a = np.array(img[:, :, 3])
                        maskx = np.where([image_x >= x_tl, image_x <= x_br], 1, 0)
                        masky = np.where([image_y >= y_tl, image_y <= y_br], 1, 0)
                        maskx = np.multiply(maskx[0], maskx[1])
                        masky = np.multiply(masky[0], masky[1])

                        # maskx = np.zeros(image_x.shape)
                        # masky = np.zeros(image_y.shape)
                        # maskx[x_tl:x_br, :] = 1
                        # masky[:, y_tl:y_br] = 1
                        # maskx = np.multiply(maskx, np.where(image_x != np.nan, 1, 0))
                        # masky = np.multiply(masky, np.where(image_y != np.nan, 1, 0))

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
                            if len(raw_z) > 0 and self._station_config.CALIB_Z_BY_STATION_SW:
                                raw_z = self.z_corr(raw_z)
                            writer.writerows(tuple(zip(raw_x, raw_y, raw_z, raw_a)))
                            if len(raw_z) > 0:
                                mean_z = io_utils.round_ex(np.mean(raw_z), 2)
                                test_log.set_measured_value_by_name_ex(f'{pattern_name}_{p_name}', mean_z)
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
        self._panel_left_or_right = None
        self._latest_serial_number = serial_num
        if test_station.TestStation.validate_sn(self, serial_num):
            if not self._station_config.SERIAL_NUMBER_VALIDATION:
                return True
            else:
                self._panel_left_or_right = dict({
                    'Q': 'L',
                    'R': 'R',
                }).get([self._parse(serial_num)['QRM']])
            if self._panel_left_or_right in ['L', 'R']:
                return True
            else:
                self._operator_interface.print_to_console(
                    f'Unable to determine this PANEL is left-one or right-one. from SN: {serial_num}\n', 'red')
                return False
        return False

    def _parse(self, serial_num):
        assert len(serial_num) == 14, f'{serial_num} is not matched the rules defined by meta.'
        return {
            'project_code': serial_num[0:2],
            'vendor_code': serial_num[2:4],
            'QRM': serial_num[4],
            'configuration_code': serial_num[5:7],
            'uid': serial_num[10:14]
        }