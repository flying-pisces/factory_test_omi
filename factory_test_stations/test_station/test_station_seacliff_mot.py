from typing import Callable
import hardware_station_common.test_station.test_station as test_station
import test_station.test_fixture.test_fixture_seacliff_mot as test_fixture_seacliff_mot
from test_station.test_fixture.test_fixture_project_station import projectstationFixture
import test_station.test_equipment.test_equipment_seacliff_mot as test_equipment_seacliff_mot
from test_station.dut.dut import pancakeDut, projectDut, DUTError
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


def chk_and_set_measured_value_by_name(test_log, item, value):
    """

    :type test_log: test_station.TestRecord
    """
    if item in test_log.results_array():
        test_log.set_measured_value_by_name(item, value)
    # else:
    #     pprint.pprint(item)


class seacliffmotStationError(Exception):
    pass


class seacliffmotStation(test_station.TestStation):

    _fixture: test_fixture_seacliff_mot.seacliffmotFixture
    _pool: mp.Pool

    def write(self, msg):
        """
        @type msg: str
        @return:
        """
        if msg.endswith('\n'):
            msg += os.linesep
        self._operator_interface.print_to_console(msg)

    def auto_find_com_ports(self):
        import serial.tools.list_ports
        import serial
        from pymodbus.client.sync import ModbusSerialClient
        from pymodbus.register_read_message import ReadHoldingRegistersResponse

        self._operator_interface.print_to_console("auto config com ports...\n")
        self._station_config.DUT_COMPORT = None
        self._station_config.FIXTURE_COMPORT = None
        self._station_config.FIXTURE_PARTICLE_COMPORT = None

        com_ports = list(serial.tools.list_ports.comports())
        pprint.pprint(f'Ports = {[(com.device, com.hwid, com.description) for com in com_ports]} \n')

        for com in com_ports:
            hit_success = False
            if self._station_config.FIXTURE_PARTICLE_COUNTER \
                    and self._station_config.FIXTURE_PARTICLE_COMPORT is None \
                    and (self._station_config.FIXTURE_PARTICLE_COMPORT_FILTER in com.hwid):
                try:
                    timeout_modbus = 5 if not hasattr(self._station_config, 'PARTICLE_COUNTER_TIMEOUT') \
                        else self._station_config.PARTICLE_COUNTER_TIMEOUT
                    modbus_client = ModbusSerialClient(method='rtu', baudrate=9600, bytesize=8,
                                                       parity='N', stopbits=1,
                                                       port=com.device, timeout=timeout_modbus)
                    if modbus_client is not None:
                        retries = 1
                        while (retries < 5) and (not hit_success):
                            print(f'try to search modbus for particle counter. {retries}\n')
                            if modbus_client.connect():
                                rs = modbus_client.read_holding_registers(
                                    self._station_config.FIXTRUE_PARTICLE_ADDR_STATUS,
                                    2, unit=self._station_config.FIXTURE_PARTICLE_ADDR)
                                modbus_client.close()
                                # type: ReadHoldingRegistersResponse
                                if rs is None or rs.isError():
                                    # retries = retries + 1
                                    time.sleep(0.05)
                                else:
                                    self._station_config.FIXTURE_PARTICLE_COMPORT = com.device
                                    hit_success = True
                            retries += 1
                except Exception as e:
                    print(f'Fail to confirm [{com.device}] for particle counter. {str(e)}\n')

            if hit_success:
                continue
            if (self._station_config.FIXTURE_COMPORT is None) and (not self._station_config.IS_PROXY_COMMUNICATION):
                a_serial = None
                try:
                    a_serial = serial.Serial(com.device, 115200, parity='N', stopbits=1, bytesize=8,
                                             timeout=1, xonxoff=0, rtscts=0)
                    if a_serial is not None:
                        a_serial.flush()
                        a_serial.write('CMD_ID\r\n'.encode())
                        msg = a_serial.readline()
                        if 'ID' in msg.decode(encoding='utf-8').upper():
                            self._station_config.FIXTURE_COMPORT = com.device
                            hit_success = True
                except Exception as e:
                    pass
                finally:
                    if a_serial is not None:
                        a_serial.close()

            if (self._station_config.DUT_COMPORT is None) and not self._station_config.DUT_ETH_PROXY:
                try:
                    a_serial = serial.Serial(com.device, 115200, parity='N', stopbits=1, bytesize=8,
                                             timeout=1, xonxoff=0, rtscts=0)
                    if a_serial is not None:
                        a_serial.flush()
                        a_serial.write('$c.VERSION,mcu\r\n'.encode())
                        ver_mcu = a_serial.readline()
                        if '$P.VERSION' in ver_mcu.decode(encoding='utf-8').upper():
                            a_serial.flush()
                            a_serial.write('$c.DUT.POWEROFF\r\n'.encode())
                            pw_msg = a_serial.readline()
                            if pw_msg != b'':
                                print('Ver_MCU: {0}, POWER_OFF: {1}'.format(ver_mcu, pw_msg.decode()))
                            self._station_config.DUT_COMPORT = com.device
                            hit_success = True
                except Exception as e:
                    pass
                finally:
                    a_serial.close()

            if hit_success:
                continue

    def __init__(self, station_config, operator_interface):
        test_station.TestStation.__init__(self, station_config, operator_interface)
        if hasattr(self._station_config, 'IS_PRINT_TO_LOG') and self._station_config.IS_PRINT_TO_LOG:
            sys.stdout = self
            sys.stderr = self
            sys.stdin = None
        self._fixture = None
        self._fixture = test_fixture_seacliff_mot.seacliffmotFixture(station_config, operator_interface)
        if hasattr(station_config, 'FIXTURE_SIM') and station_config.FIXTURE_SIM:
            self._fixture = projectstationFixture(station_config, operator_interface)
        self._equipment = test_equipment_seacliff_mot.seacliffmotEquipment(station_config, operator_interface)
        self._overall_errorcode = ''
        self._first_failed_test_result = None
        self._sw_version = '1.2.0'
        self._latest_serial_number = None  # type: str
        self._the_unit = None  # type: pancakeDut
        self._retries_screen_on = 0
        self._is_screen_on_by_op = False
        self._is_cancel_test_by_op = False
        self._is_alignment_success = False
        self._module_left_or_right = None
        self._probe_con_status = False

    def initialize(self):
        try:
            self._operator_interface.print_to_console("Initializing Seacliff MOT station...{0}\n"
                                                      .format(self._sw_version))
            if self._station_config.AUTO_CFG_COMPORTS:
                self.auto_find_com_ports()

            msg = "find ports FIXTURE = {0}, DUT = {1}, PARTICLE COUNTER = {2}. \n" \
                .format(self._station_config.FIXTURE_COMPORT,
                        self._station_config.DUT_COMPORT, self._station_config.FIXTURE_PARTICLE_COMPORT)
            self._operator_interface.print_to_console(msg)

            self._fixture.initialize()
            self._equipment.initialize()
            self._equipment.open()
        except Exception as e:
            self._operator_interface.operator_input(None, str(e), 'error')
            raise

    def _close_fixture(self):
        if self._fixture is not None:
            self._operator_interface.print_to_console("Close...\n")
            self._fixture.close()
            self._fixture = None

    def close(self):
        self._operator_interface.print_to_console("Close...\n")
        self._operator_interface.print_to_console("\there, I'm shutting the station down..\n")
        try:
            self._close_fixture()
        except Exception as e:
            pass
        try:
            self._equipment.close()
            self._equipment.kill()
        except Exception as e:
            pass

    def get_test_item_pattern(self, name):
        for c in self._station_config.TEST_ITEM_PATTERNS:
            if c.get('name') and c['name'] == name:
                return c

    @staticmethod
    def get_filenames_in_folder(parent_dir, pattern):
        file_names = []
        for home, dirs, files in os.walk(parent_dir):
            for file_name in files:
                if re.search(pattern, file_name, re.I):
                    file_names.append(os.path.join(home, file_name))
        file_names.sort(reverse=True)
        return file_names

    def _do_test(self, serial_number, test_log):
        """

        @type test_log: test_station.test_log.test_log
        """
        msg0 = 'info --> lit up: {0}, emulator_dut: {1}, emulator_equip: {2}, emulator_fixture: {3},' \
               ' particle:{4}, dut_checker:{5} ver: {6}\n' .format(
                self._station_config.DUT_LITUP_OUTSIDE, self._station_config.DUT_SIM,
                self._station_config.EQUIPMENT_SIM, self._station_config.FIXTURE_SIM,
                self._station_config.FIXTURE_PARTICLE_COUNTER, self._station_config.DISP_CHECKER_ENABLE,
                self._sw_version)
        self._operator_interface.print_to_console(msg0)
        is_query_temp = (hasattr(self._station_config, 'QUERY_DUT_TEMP_PER_PATTERN')
                         and self._station_config.QUERY_DUT_TEMP_PER_PATTERN
                         and not self._station_config.FIXTURE_SIM)

        self._query_dual_start()
        if self._the_unit is None:
            raise test_station.TestStationProcessControlError(f'Fail to query dual_start for DUT {serial_number}.')
        self._probe_con_status = True
        if not self._station_config.FIXTURE_SIM:
            self._probe_con_status = self._fixture.query_probe_status() == 0

        self._overall_result = False
        self._overall_errorcode = ''
        latest_pattern_value_bak = None
        cpu_count = mp.cpu_count()
        self._pool = mp.Pool(2)
        self._pool_alg_dic = {}
        self._exported_parametric = {}
        self._gl_W255 = {}
        self._temperature_dic = {}
        try:
            self._operator_interface.print_to_console(
                "\n*********** Fixture at %s to load DUT %s ***************\n"
                % (self._station_config.FIXTURE_COMPORT, self._station_config.DUT_COMPORT))

            self._operator_interface.print_to_console("Testing Unit %s\n" % self._the_unit.serial_number)
            self._operator_interface.print_to_console("Initialize DUT... \n")

            test_log.set_measured_value_by_name_ex = types.MethodType(chk_and_set_measured_value_by_name, test_log)

            self._operator_interface.print_to_console("Testing Unit %s\n" % self._the_unit.serial_number)
            test_log.set_measured_value_by_name_ex('SW_VERSION', self._sw_version)

            test_log.set_measured_value_by_name_ex('Carrier_ProbeConnectStatus', self._probe_con_status)
            test_log.set_measured_value_by_name_ex("DUT_ScreenOnRetries", self._retries_screen_on)
            test_log.set_measured_value_by_name_ex("DUT_ScreenOnStatus", self._is_screen_on_by_op)
            test_log.set_measured_value_by_name_ex("DUT_CancelByOperator", self._is_cancel_test_by_op)
            test_log.set_measured_value_by_name_ex("DUT_AlignmentSuccess", self._is_alignment_success)
            test_log.set_measured_value_by_name_ex("DUT_ModuleType", self._module_left_or_right)

            particle_count = 0
            if self._station_config.FIXTURE_PARTICLE_COUNTER:
                particle_count = self._fixture.particle_counter_read_val()
            test_log.set_measured_value_by_name_ex("ENV_ParticleCounter", particle_count)
            ambient_temp = self._fixture.query_temp()
            test_log.set_measured_value_by_name_ex("ENV_AmbientTemp", ambient_temp)

            if not self._is_screen_on_by_op:
                raise seacliffmotStationError('fail to power screen on normally.')
            if not self._is_alignment_success:
                raise seacliffmotStationError('Fail to alignment.\n')
            equip_version = self._equipment.version()
            if isinstance(equip_version, dict):
                test_log.set_measured_value_by_name_ex('EQUIP_VERSION', equip_version.get('Lib_Version'))
            # capture path accorded with test_log.
            uni_file_name = re.sub('_x.log', '', test_log.get_filename())
            capture_path = os.path.join(self._station_config.RAW_IMAGE_LOG_DIR, uni_file_name)
            if self._station_config.EQUIPMENT_SIM:
                uut_dirs = [c for c in glob.glob(os.path.join(self._station_config.RAW_IMAGE_LOG_DIR, r'*'))
                            if os.path.isdir(c)
                            and os.path.relpath(c, self._station_config.RAW_IMAGE_LOG_DIR)
                            .upper().startswith(serial_number.upper())]
                if len(uut_dirs) > 0:
                    capture_path = uut_dirs[-1]
            if not os.path.exists(capture_path):
                test_station.utils.os_utils.mkdir_p(capture_path)
                os.chmod(capture_path, 0o777)
            config = dict(self._station_config.CAM_INIT_CONFIG)

            config["capturePath"] = capture_path
            config['cfgPath'] = os.path.join(self._station_config.CONOSCOPE_DLL_PATH, self._station_config.CFG_PATH)

            self._operator_interface.print_to_console("set current config = {0}\n".format(config))
            self._equipment.set_config(config)
            current_test_position = None
            patterns_in_testing = []

            for pos_item in self._station_config.TEST_ITEM_POS:
                pos_name = pos_item['name']
                pos_val = pos_item['pos']
                item_patterns = pos_item.get('pattern')
                item_condition_a_patterns = pos_item.get('condition_A_patterns')
                if item_patterns is None and item_condition_a_patterns is None:
                    continue
                if current_test_position != pos_name:
                    self._operator_interface.print_to_console('mov dut to pos = {0}\n'.format(pos_name))
                    self._fixture.mov_abs_xy_wrt_alignment(pos_val[0], pos_val[1])
                    time.sleep(self._station_config.FIXTURE_SOCK_DLY)
                    self._fixture.mov_camera_z_wrt_alignment(pos_val[2])
                    time.sleep(self._station_config.FIXTURE_MECH_STABLE_DLY)
                    current_test_position = pos_name

                for pattern_name in item_patterns:
                    pattern_info = self.get_test_item_pattern(pattern_name)
                    if not pattern_info:
                        self._operator_interface.print_to_console(
                            'Unable to find information for pattern: %s \n' % pattern_name)
                        continue
                    patterns_in_testing.append((pos_name, pattern_name))
                    self._operator_interface.print_to_console('test pattern name = {0}\n'.format(pattern_name))

                    if latest_pattern_value_bak != pattern_info['pattern']:
                        latest_pattern_value_bak = pattern_info['pattern']
                        pattern_value_valid = self.render_pattern_on_dut(pattern_name, latest_pattern_value_bak)
                        if not pattern_value_valid:
                            self._operator_interface.print_to_console('Unable to change pattern: {0} = {1} \n'
                                                                      .format(pattern_name, latest_pattern_value_bak))
                            continue

                    dut_temp = 30
                    if is_query_temp:
                        self._operator_interface.print_to_console(f'query temperature for {pos_name}_{pattern_name}\n')
                        dut_temp = self._fixture.query_temp(test_fixture_seacliff_mot.QueryTempParts.UUTNearBy)
                    self._temperature_dic[f'{pos_name}_{pattern_name}'] = dut_temp
                    test_log.set_measured_value_by_name_ex(f'UUT_TEMPERATURE_{pos_name}_{pattern_name}', dut_temp)

                    raw_success_save = self.capture_images_for_pattern(pos_name, capture_path, pattern_name,
                                                                       pattern_name)

                    measure_item_name = 'Test_RAW_IMAGE_SAVE_SUCCESS_{0}_{1}'.format(pos_name, pattern_name)
                    test_log.set_measured_value_by_name_ex(measure_item_name, raw_success_save)

                    # current_obj = self._station_config.copy()
                    self.do_pattern_parametric_export(pos_name, pattern_name, capture_path, test_log)

                self._operator_interface.print_to_console('Wait init pattern to complete.\n')
                self._operator_interface.print_to_console('Please wait...')
                while len([pn for pn, pv in self._pool_alg_dic.items() if not pv]) > 0:
                    self._operator_interface.wait(1, '.')
                self._operator_interface.wait(0, '\n')
                ref_patterns = ['W255', 'R255', 'G255', 'B255']
                exp_data = tuple([self._exported_parametric[f'{pos_name}_{c}'] for c in ref_patterns])

                patterns_in_testing = []
                for pattern_name, n_dots, pattern_group in item_condition_a_patterns:
                    dut_temp = 30
                    if is_query_temp:
                        self._operator_interface.print_to_console(f'query temperature for {pos_name}_{pattern_name}\n')
                        dut_temp = self._fixture.query_temp(test_fixture_seacliff_mot.QueryTempParts.UUTNearBy)
                    self._temperature_dic[f'{pos_name}_{pattern_name}'] = dut_temp
                    test_log.set_measured_value_by_name_ex(f'UUT_TEMPERATURE_{pos_name}_{pattern_name}', dut_temp)
                    ref_pattern_name = self._station_config.ANALYSIS_GRP_COLOR_PATTERN_EX[pattern_name]
                    self._gl_W255[f'{pos_name}_{pattern_name}'] = \
                        test_equipment_seacliff_mot.MotAlgorithmHelper.calc_gl_for_brightdot(*exp_data,
                             module_temp=self._temperature_dic[f'{pos_name}_{pattern_name}'])
                    self._operator_interface.print_to_console(
                        f"\ncalc gray level from W/R/G/B --> {self._gl_W255[f'{pos_name}_{pattern_name}']['GL']}\n")

                    rel_pattern_name = None
                    if self._gl_W255[f'{pos_name}_{pattern_name}']['GL'][2] == 255:
                        rel_pattern_name = pattern_group[0]
                    elif self._gl_W255[f'{pos_name}_{pattern_name}']['GL'][1] == 255:
                        rel_pattern_name = pattern_group[1]
                    elif self._gl_W255[f'{pos_name}_{pattern_name}']['GL'][0] == 255:
                        rel_pattern_name = pattern_group[2]

                    pattern_info = self.get_test_item_pattern(rel_pattern_name)
                    if not pattern_info:
                        self._operator_interface.print_to_console(
                            'Unable to find information for pattern: %s \n' % rel_pattern_name)
                        continue
                    patterns_in_testing.append((pos_name, rel_pattern_name))
                    self._operator_interface.print_to_console('test pattern name = {0}\n'.format(pattern_name))
                    if latest_pattern_value_bak != pattern_info['pattern']:
                        latest_pattern_value_bak = pattern_info['pattern']
                        pattern_value_valid = self.render_pattern_on_dut(rel_pattern_name, latest_pattern_value_bak)
                        if not pattern_value_valid:
                            self._operator_interface.print_to_console('Unable to change pattern: {0} = {1} \n'
                                                                      .format(pattern_name, latest_pattern_value_bak))
                            continue

                    measure_item_name = 'Test_Pattern_{0}_{1}'.format(pos_name, pattern_name)
                    test_log.set_measured_value_by_name_ex(measure_item_name, rel_pattern_name)

                    raw_success_save = self.capture_images_for_pattern(
                        pos_name, capture_path, rel_pattern_name, pattern_name)

                    measure_item_name = 'Test_RAW_IMAGE_SAVE_SUCCESS_{0}_{1}'.format(pos_name, pattern_name)
                    test_log.set_measured_value_by_name_ex(measure_item_name, raw_success_save)

                    self.do_pattern_parametric_export(pos_name, pattern_name, capture_path, test_log)

            self._operator_interface.print_to_console("all images captured, now start to export data. \n")
            self.data_export(serial_number, capture_path, test_log)
            del config, patterns_in_testing
        except test_equipment_seacliff_mot.seacliffmotEquipmentError as e:
            self._operator_interface.print_to_console(str(e))
            self._operator_interface.print_to_console('Reset taprisiot automatically by command.\n')
            self._equipment.reset()
            self._equipment.close()
            self._operator_interface.print_to_console('open taprisiot automatically.\n')
            self._equipment.open()
        except seacliffmotStationError as e:
            self._operator_interface.operator_input(None, str(e), msg_type='error')
            self._operator_interface.print_to_console(str(e))
        finally:
            self._pool.close()
            self._operator_interface.print_to_console('Wait ProcessingPool to complete.\n')
            self._operator_interface.print_to_console('Please wait...')
            while len([pn for pn, pv in self._pool_alg_dic.items() if not pv]) > 0:
                self._operator_interface.wait(1, '.')
            self._operator_interface.wait(0, '\n')
            self._operator_interface.print_to_console('\nfinish to process\n')
            self._pool.join()
            self._pool = None
            try:
                self._the_unit.close()
                self._fixture.unload()
            except:
                self._the_unit = None
        del self._pool_alg_dic
        self._operator_interface.print_to_console(f'Finish------------{serial_number}-------\n')
        return self.close_test(test_log)

    def do_pattern_parametric_export(self, pos_name, pattern_name, capture_path, test_log):
        if pattern_name in self._station_config.ANALYSIS_GRP_DISTORTION:
            self.distortion_centroid_parametric_export_ex(pos_name, pattern_name, capture_path, test_log)
        elif pattern_name in self._station_config.ANALYSIS_GRP_NORMAL_PATTERN.keys():
            self.normal_pattern_parametric_export_ex(pos_name, pattern_name, capture_path, test_log)
        elif pattern_name in self._station_config.ANALYSIS_GRP_COLOR_PATTERN_EX.keys():
            self.grade_a_patterns_parametric_export_ex(pos_name, pattern_name, capture_path, test_log)

    def capture_images_for_pattern(self, pos_name, capture_path, pattern_name, exp_pattern_name):
        pre_file_name = '{0}_{1}_'.format(pos_name, exp_pattern_name)
        config = {'fileNamePrepend': pre_file_name}
        self._operator_interface.print_to_console("set current config = {0}\n".format(config))
        self._equipment.set_config(config)
        pattern: dict
        pattern = self.get_test_item_pattern(pattern_name)
        pattern_value = pattern.get('pattern')
        out_image_mode = 0
        if pattern.get('oi_mode'):
            out_image_mode = pattern.get('oi_mode')
        file_count_per_capture = self._station_config.FILE_COUNT_INC.get(out_image_mode)
        lambda_sum_files: Callable[[], int] = lambda: sum([len(list(filter(
            lambda x: re.search('(_float.bin|.json)$', x, re.I | re.S), files))) for r, d, files in os.walk(capture_path)])
        test_item_raw_files_pre = lambda_sum_files()
        if self._station_config.EQUIPMENT_SIM and not self._station_config.EQUIPMENT_SIM_CAPTURE_FROM_DIR:
            self._operator_interface.print_to_console(
                "Skip to Capture Bin File for color {0} in emulator mode\n".format(pattern_value))
            test_item_raw_files_post = test_item_raw_files_pre + file_count_per_capture
        else:
            msg = '********* Eldim Capturing Bin File for color {0} ***************\n'.format(pattern_value)
            self._operator_interface.print_to_console(msg)
            self._equipment.do_measure_and_export(pos_name, pattern_name)
            test_item_raw_files_post = lambda_sum_files()
        self._operator_interface.print_to_console(
            'file count detect {0} --> {1}. \n'.format(test_item_raw_files_pre, test_item_raw_files_post))
        raw_success_save = (test_item_raw_files_pre + file_count_per_capture) == test_item_raw_files_post
        return raw_success_save

    def render_pattern_on_dut(self, pattern_name, pattern_value):
        msg = 'try to render image  {0} -> {1} to {2} module.\n' \
            .format(pattern_name, pattern_value, self._module_left_or_right)
        self._operator_interface.print_to_console(msg)
        pattern_value_valid = True
        if isinstance(pattern_value, (int, str)):
            self._the_unit.display_image(pattern_value, False)
        elif isinstance(pattern_value, tuple):
            if len(pattern_value) == 0x03:
                self._the_unit.display_color(pattern_value)
            elif len(pattern_value) == 0x02 and self._module_left_or_right == 'L':
                self._the_unit.display_image(pattern_value[0])
            elif len(pattern_value) == 0x02 and self._module_left_or_right == 'R':
                self._the_unit.display_image(pattern_value[1])
            else:
                pattern_value_valid = False
        else:
            pattern_value_valid = False
        return pattern_value_valid

    def close_test(self, test_log):
        self._overall_result = test_log.get_overall_result()
        self._first_failed_test_result = test_log.get_first_failed_test_result()
        return self._overall_result, self._first_failed_test_result

    def validate_sn(self, serial_num):
        self._latest_serial_number = serial_num
        return test_station.TestStation.validate_sn(self, serial_num)

    def is_ready(self):
        return True

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
        self._is_alignment_success = False
        self._module_left_or_right = None
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
                    self._is_alignment_success = True
                    self._module_left_or_right = 'R'
                    self._fixture._alignment_pos = (0, 0, 0, 0)
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
                        time.sleep(self._station_config.FIXTURE_SOCK_DLY)
                        alignment_result = self._fixture.alignment(self._latest_serial_number)
                        if isinstance(alignment_result, tuple):
                            self._module_left_or_right = str(alignment_result[4]).upper()
                            self._is_alignment_success = True

                    elif ready_status == 0x03 or ready_status == 0x02:
                        self._operator_interface.print_to_console('Try to lit up DUT.\n')
                        self._retries_screen_on += 1
                        # power the dut on normally.
                        if power_on_trigger:
                            self._the_unit.screen_off()
                            self._the_unit.reboot()  # Reboot
                        self._the_unit.screen_on()
                        power_on_trigger = True
                        # check the color sensor
                        timeout_for_dual = timeout_for_btn_idle
                        color_check_result = True
                        if self._station_config.DISP_CHECKER_ENABLE:
                            color_check_result = False
                            color = self._the_unit.get_color_ext(False)
                            if self._the_unit.display_color_check(color):
                                color_check_result = True
                            if color_check_result:
                                self._fixture.power_on_button_status(False)
                                time.sleep(self._station_config.FIXTURE_SOCK_DLY)
                                self._fixture.start_button_status(True)
                        else:
                            self._fixture.power_on_button_status(False)
                            time.sleep(self._station_config.FIXTURE_SOCK_DLY)
                            self._fixture.start_button_status(True)
                    elif ready_status == 0x01:
                        self._is_cancel_test_by_op = True  # Cancel test.
                time.sleep(0.1)
                timeout_for_dual -= 1
        except (seacliffmotStationError, DUTError, RuntimeError) as e:
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

    def data_export(self, serial_number, capture_path, test_log):
        """
        @param serial_number: str
        @param capture_path: str
        @param test_log: test_station.test_log.test_log
        @return:
        """
        if not (self._station_config.AUTO_CVT_BGR_IMAGE_FROM_XYZ or self._station_config.AUTO_SAVE_2_TXT):
            return
        data_items_XYZ = {}
        for pos_item in self._station_config.TEST_ITEM_POS:
            pos_name = pos_item['name']
            item_patterns = pos_item.get('pattern')
            if item_patterns is None:
                continue
            for pattern_name in item_patterns:
                pattern_info = self.get_test_item_pattern(pattern_name)
                if not pattern_info:
                    continue
                pre_file_name = '{0}_{1}'.format(pos_name, pattern_name)
                file_x = seacliffmotStation.get_filenames_in_folder(capture_path, r'{0}_.*_X_float\.bin'.format(pre_file_name))
                file_y = seacliffmotStation.get_filenames_in_folder(capture_path, r'{0}_.*_Y_float\.bin'.format(pre_file_name))
                file_z = seacliffmotStation.get_filenames_in_folder(capture_path, r'{0}_.*_Z_float\.bin'.format(pre_file_name))
                if len(file_x) != 0 and len(file_y) == len(file_x) and len(file_z) == len(file_x):
                    self._operator_interface.print_to_console('Read X/Y/Z float from {0} bins.\n'.format(pre_file_name))
                    group_data = [test_equipment_seacliff_mot.MotAlgorithmHelper.get_export_data(fn,
                                  station_config=self._station_config)
                                  for fn in (file_x[0], file_y[0], file_z[0])]

                    # group_data[0] = np.linspace(-10, 10, 5)
                    # group_data[1] = np.linspace(-20, 20, 5)
                    # group_data[2] = np.linspace(0, 0, 5)

                    X, Y, Z = group_data
                    data_items_XYZ[pre_file_name] = np.dstack(group_data)

                    self._operator_interface.print_to_console('convert XYZ --> xyY\n')
                    os_err = np.seterr(divide='ignore', invalid='ignore')
                    x = X/(X + Y + Z)
                    y = Y/(X + Y + Z)
                    np.seterr(**os_err)
                    mask = (X + Y + Z) == 0
                    xyY_mask = np.dstack([mask, mask, mask])
                    xyY = np.where(xyY_mask, np.zeros_like(xyY_mask), np.dstack([x, y, Y]))

                    self._operator_interface.print_to_console('start to export data for %s\n' % pre_file_name)
                    img_base_name = os.path.basename(file_x[0]).split('_X_float.bin')[0]
                    if self._station_config.AUTO_CVT_BGR_IMAGE_FROM_XYZ:
                        self._operator_interface.print_to_console('save {0} bgr image.\n'.format(pre_file_name))
                        img_file_name = os.path.join(os.path.dirname(file_x[0]), img_base_name + '.bmp')
                        xyz = cv2.merge(group_data)
                        bgr = cv2.cvtColor(xyz, cv2.COLOR_XYZ2BGR)
                        cv2.imwrite(img_file_name, bgr)
                    if self._station_config.AUTO_SAVE_2_TXT:
                        self._operator_interface.print_to_console('save {0} txt.\n'.format(pre_file_name))
                        txt_x_file_name = os.path.join(os.path.dirname(file_x[0]), img_base_name + '_X.txt')
                        txt_y_file_name = os.path.join(os.path.dirname(file_x[0]), img_base_name + '_Y.txt')
                        txt_z_file_name = os.path.join(os.path.dirname(file_x[0]), img_base_name + '_Z.txt')
                        np.savetxt(txt_x_file_name, group_data[0])
                        np.savetxt(txt_y_file_name, group_data[1])
                        np.savetxt(txt_z_file_name, group_data[2])
                    del group_data, X, Y, Z, x, y, xyY, xyY_mask
                self._operator_interface.print_to_console('parse data {0} finished.\n'.format(pre_file_name))
        del data_items_XYZ
        pass

    @staticmethod
    def distortion_centroid_parametric_export_ex_parallel(pos_name, pattern_name, opt):
        distortion_exports = None
        try:
            pri_key = opt['pri_key']
            fil = opt['fil']
            save_plots = opt['save_plots']
            module_temp = opt['ModuleTemp']
            mot_alg = test_equipment_seacliff_mot.MotAlgorithmHelper(save_plots=save_plots)
            distortion_exports = mot_alg.distortion_centroid_parametric_export(fil, module_temp=module_temp)
        except:
            pass
        return pos_name, pattern_name, pri_key, distortion_exports

    def distortion_centroid_parametric_export_ex(self, ana_pos_item, ana_pattern, capture_path, test_log):
        self._operator_interface.print_to_console(f'Try to analysis data for {ana_pos_item} --> {ana_pattern}\n')
        for pos_item in self._station_config.TEST_ITEM_POS:
            pos_name = pos_item['name']
            item_patterns = pos_item.get('pattern')
            if (item_patterns is None) or (pos_name != ana_pos_item):
                continue
            analysis_patterns = [c for c in item_patterns if c in self._station_config.ANALYSIS_GRP_DISTORTION]
            for pattern_name in analysis_patterns:
                pattern_info = self.get_test_item_pattern(pattern_name)
                if (ana_pattern != pattern_name) or (not pattern_info):
                    continue

                file_x, file_y, file_z = self.extract_basic_info_for_pattern(capture_path, pattern_name, pos_name,
                                                                             test_log)
                primary = ['X', 'Y', 'Z']
                primary_dict = dict(zip(primary, [file_x, file_y, file_z]))
                if hasattr(self._station_config, 'ANALYSIS_GRP_DISTORTION_PRIMARY'):
                    primary = self._station_config.ANALYSIS_GRP_DISTORTION_PRIMARY

                for pri_k in primary:
                    file_k = primary_dict.get(pri_k)
                    if len(file_k) <= 0:
                        continue
                    pri_v = file_k[0]
                    try:
                        self._operator_interface.print_to_console(
                            'start to export {0}, {1}-{2}\n'.format(pos_name, pattern_name, pri_k))

                        def distortion_centroid_parametric_export_ex_parallel_callback(res):
                            pos_name_i, pattern_name_i, pri_k_i, distortion_exports = res
                            if distortion_exports is not None:
                                self._exported_parametric[f'{pos_name_i}_{pattern_name_i}'] = distortion_exports
                                for export_key, export_value in distortion_exports.items():
                                    measure_item_name = '{0}_{1}_{2}_{3}'.format(
                                        pos_name_i, pattern_name_i, pri_k_i, export_key)
                                    test_log.set_measured_value_by_name_ex(measure_item_name, export_value)
                            self._operator_interface.print_to_console(f'finish export {pos_name_i}, {pattern_name_i}')
                            self._pool_alg_dic[f'{pos_name_i}_{pattern_name_i}'] = True

                        opt = {
                            'pri_key': pri_k,
                            'fil': pri_v,
                            'save_plots': self._station_config.AUTO_SAVE_PROCESSED_PNG,
                            'ModuleTemp': self._temperature_dic[f'{pos_name}_{pattern_name}'],
                        }
                        self._pool.apply_async(
                            seacliffmotStation.distortion_centroid_parametric_export_ex_parallel, (
                                pos_name, pattern_name, opt),
                            callback=distortion_centroid_parametric_export_ex_parallel_callback)
                        self._pool_alg_dic[f'{pos_name}_{pattern_name}'] = False
                    except Exception as e:
                        self._operator_interface.print_to_console(
                            f'Fail to export data for pattern: {pos_name}_{pattern_name} Distortion {pri_k}\n')

    @staticmethod
    def normal_pattern_parametric_export_ex_parallel(pos_name, pattern_name, opt):
        parametric_exports = None
        try:
            alg_optional = opt['alg']
            fil = opt['filename']
            save_plots = opt['save_plots']
            mot_alg = test_equipment_seacliff_mot.MotAlgorithmHelper(save_plots=save_plots)
            if alg_optional == 'w':
                dut_temp = opt['temperature']
                module_LR = opt['moduleLR']
                parametric_exports = mot_alg.color_pattern_parametric_export_W255(module_LR, dut_temp, fil)
            elif alg_optional in ['r', 'g', 'b']:
                dut_temp = opt['temperature']
                parametric_exports = mot_alg.color_pattern_parametric_export_RGB(alg_optional, dut_temp, fil)
            elif alg_optional in ['br']:
                dut_temp = opt['temperature']
                parametric_exports = mot_alg.rgbboresight_parametric_export(dut_temp, fil)
            elif alg_optional in ['gd']:
                parametric_exports = mot_alg.distortion_centroid_parametric_export(fil)
        except Exception as e:
            pass
        return pos_name, pattern_name, parametric_exports

    def normal_pattern_parametric_export_ex(self, ana_pos_item, ana_pattern, capture_path, test_log):
        self._operator_interface.print_to_console(f'Try to analysis data for {ana_pos_item} --> {ana_pattern}\n')
        for pos_item in self._station_config.TEST_ITEM_POS:
            pos_name = pos_item['name']
            item_patterns = pos_item.get('pattern')
            if (ana_pos_item != pos_name) or (item_patterns is None):
                continue

            pattern_info = self.get_test_item_pattern(ana_pattern)
            if not pattern_info:
                continue
            alg_optional = self._station_config.ANALYSIS_GRP_NORMAL_PATTERN.get(ana_pattern)
            if not alg_optional:
                continue

            file_x, file_y, file_z = self.extract_basic_info_for_pattern(capture_path, ana_pattern, pos_name,
                                                                         test_log)
            if len(file_x) != 0 and len(file_y) == len(file_x) and len(file_z) == len(file_x):
                try:
                    self._operator_interface.print_to_console(
                        'start to export {0}, {1}\n'.format(pos_name, ana_pattern))

                    def color_pattern_parametric_export_ex_parallel_callback(res):
                        pos_name_i, pattern_name_i, color_exports = res
                        if color_exports is not None:
                            self._exported_parametric[f'{pos_name_i}_{pattern_name_i}'] = color_exports
                            for export_key, export_value in color_exports.items():
                                measure_item_name = '{0}_{1}_{2}'.format(
                                    pos_name_i, pattern_name_i, export_key)
                                test_log.set_measured_value_by_name_ex(measure_item_name, export_value)
                        self._operator_interface.print_to_console(f'finish export {pos_name_i}, {pattern_name_i}')
                        self._pool_alg_dic[f'{pos_name_i}_{pattern_name_i}'] = True
                    dut_temp = self._temperature_dic[f'{pos_name}_{ana_pattern}']
                    opt = {
                        'alg': alg_optional,
                        'filename': file_x[0],
                        'temperature': dut_temp,
                        'moduleLR': self._module_left_or_right,
                        'save_plots': self._station_config.AUTO_SAVE_PROCESSED_PNG,
                    }
                    self._pool.apply_async(
                        seacliffmotStation.normal_pattern_parametric_export_ex_parallel,
                        (pos_name, ana_pattern, opt),
                        callback=color_pattern_parametric_export_ex_parallel_callback)
                    self._pool_alg_dic[f'{pos_name}_{ana_pattern}'] = False

                except Exception as e:
                    self._operator_interface.print_to_console(
                        'Fail to export data for pattern: {0}_{1}, {2}\n'.format(pos_name, ana_pattern, e.args))

    @staticmethod
    def grade_a_pattern_parametric_export_ex_parallel(pos_name, pattern_name, opt):
        # print(f'Try to do parametric_export_ex_parallel _ {pos_name}: {pattern_name}')
        white_dot_exports = None
        XYZ = []
        XYZ_W = []
        try:
            n_dots = opt['nDots']
            fil = opt['filename']
            fil_ref = opt['refname']
            save_plots = opt['save_plots']
            mot_alg = test_equipment_seacliff_mot.MotAlgorithmHelper(save_plots=save_plots)
            XYZ = mot_alg.white_dot_pattern_w255_read(fil_ref, multi_process=False)
            XYZ_W = np.stack(XYZ, axis=2)
            white_dot_exports = mot_alg.white_dot_pattern_parametric_export(XYZ_W,
                        opt['GL'], opt['x_w'], opt['y_w'],
                        opt['ModuleTemp'], fil)
        except Exception as e:
            pass
        finally:
            del XYZ, XYZ_W
        return pos_name, pattern_name, white_dot_exports

    def grade_a_patterns_parametric_export_ex(self, ana_pos_item, ana_pattern, capture_path, test_log):
        self._operator_interface.print_to_console(f'Try to analysis data for {ana_pos_item} --> {ana_pattern}\n')
        for pos_item in self._station_config.TEST_ITEM_POS:
            pos_name = pos_item['name']
            item_patterns = pos_item.get('condition_A_patterns')
            if (ana_pos_item != pos_name) or (item_patterns is None):
                continue

            for pattern_name, n_dots, __ in item_patterns:
                if pattern_name not in self._station_config.ANALYSIS_GRP_COLOR_PATTERN_EX\
                        or pattern_name != ana_pattern:
                    continue
                ref_pattern = self._station_config.ANALYSIS_GRP_COLOR_PATTERN_EX[pattern_name]
                file_ref = seacliffmotStation.get_filenames_in_folder(
                    capture_path, rf'{pos_name}_{ref_pattern}_.*_X_float\.bin')
                file_x, file_y, file_z = self.extract_basic_info_for_pattern(capture_path, pattern_name, pos_name,
                                                                             test_log)
                if len(file_x) != 0 and len(file_y) == len(file_x) and len(file_z) == len(file_x) and len(file_ref) > 0:
                    try:
                        self._operator_interface.print_to_console(
                            'start to export {0}, {1}\n'.format(pos_name, pattern_name))

                        def grade_a_parametric_export_ex_parallel_callback(res):
                            pos_name_i, pattern_name_i, white_dot_exports = res
                            if white_dot_exports is not None:
                                self._exported_parametric[f'{pos_name_i}_{pattern_name_i}'] = white_dot_exports
                                for export_key, export_value in white_dot_exports.items():
                                    measure_item_name = '{0}_{1}_{2}'.format(
                                        pos_name_i, pattern_name_i, export_key)
                                    test_log.set_measured_value_by_name_ex(measure_item_name, export_value)
                            self._operator_interface.print_to_console(f'finish export {pos_name_i}, {pattern_name_i}')
                            self._pool_alg_dic[f'{pos_name_i}_{pattern_name_i}'] = True
                        opt = {'ModuleTemp': self._temperature_dic[f'{pos_name}_{pattern_name}'],
                               'nDots': n_dots,
                               'filename': file_x[0],
                               'refname': file_ref[0],
                               'save_plots': self._station_config.AUTO_SAVE_PROCESSED_PNG}
                        opt.update(self._gl_W255[f'{pos_name}_{pattern_name}'].copy())

                        self._pool.apply_async(
                            seacliffmotStation.grade_a_pattern_parametric_export_ex_parallel,
                            (pos_name, pattern_name, opt),
                            callback=grade_a_parametric_export_ex_parallel_callback)
                        self._pool_alg_dic[f'{pos_name}_{pattern_name}'] = False

                    except Exception as e:
                        self._operator_interface.print_to_console(
                            'Fail to export data for pattern: {0}_{1}, {2}\n'.format(pos_name, pattern_name, e.args))

    def extract_basic_info_for_pattern(self, capture_path, pattern_name, pos_name, test_log):
        pre_file_name = '{0}_{1}'.format(pos_name, pattern_name)
        json_k = seacliffmotStation.get_filenames_in_folder(
            capture_path, f'{pre_file_name}_.*' + r'_iris_\d.json')
        if len(json_k) > 0:
            pri_v = json_k[0]
            try:
                exposure_items = {}
                with open(pri_v, 'r') as json_file:
                    json_data = json.load(json_file)
                    exposure_items = json_data.get('Captures')
                filters = ['X', 'Xz', 'Ya', 'Yb', 'Z']
                exp_filters = [c for c in filters if c in exposure_items.keys()]
                if isinstance(exposure_items, dict):
                    [test_log.set_measured_value_by_name_ex(
                        f'{pre_file_name}_ExposureTime_{k}',
                        exposure_items[k]['exposureTimeUs'])
                        for k in exp_filters]
                    [test_log.set_measured_value_by_name_ex(
                        f'{pre_file_name}_SaturationLevel_{k}',
                        exposure_items[k]['saturationLevel'])
                        for k in exp_filters]
            except Exception as e:
                self._operator_interface.print_to_console(
                    f'Fail to load Json file {pre_file_name}. exp = {str(e)}.\n')
        file_x = seacliffmotStation.get_filenames_in_folder(capture_path,
                                                            r'{0}_.*_X_float\.bin'.format(pre_file_name))
        file_y = seacliffmotStation.get_filenames_in_folder(capture_path,
                                                            r'{0}_.*_Y_float\.bin'.format(pre_file_name))
        file_z = seacliffmotStation.get_filenames_in_folder(capture_path,
                                                            r'{0}_.*_Z_float\.bin'.format(pre_file_name))
        return file_x, file_y, file_z
