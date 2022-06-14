from typing import Callable
import hardware_station_common.test_station.test_station as test_station
import psutil
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
import collections
import math
from hardware_station_common.utils.io_utils import round_ex
import threading
import shutil
from pathlib import Path
import datetime


class seacliffmotStationError(Exception):
    pass


class EEPStationAssistant(object):
    def __init__(self):
        self._cvt_flag = {
            'S7.8': (2, True, 7, 8),
            'S1.6': (1, True, 1, 6),
            'U8.0': (1, False, 8, 0),
            'U0.16': (2, False, 0, 16),
            'U8.8': (2, False, 8, 8),
            'S4.3': (1, True, 4, 3),
        }
        self._ddic_version = '0x12'
        self._nvm_data_len = 70
        self._dr_offset = 6
        self._eeprom_map_group = collections.OrderedDict({
            'display_boresight_x': (6, 'S7.8',
                                    lambda tmp: -128 if tmp <= -128 else (128 if tmp >= 128 else tmp),
                                    lambda tmp: -128 <= tmp <= 128),
            'display_boresight_y': (8, 'S7.8',
                                    lambda tmp: -128 if tmp <= -128 else (128 if tmp >= 128 else tmp),
                                    lambda tmp: -128 <= tmp <= 128),
            'rotation': (10, 'S1.6',
                         lambda tmp: -2 if tmp <= -2 else (2 if tmp >= 2 else tmp),
                         lambda tmp: -2 <= tmp <= 2),

            'lv_W255': (11, 'U8.8',
                        lambda tmp: 0 if tmp < 0 else (256 if tmp >= 256 else tmp),
                        lambda tmp: 0 <= tmp <= 256),
            'x_W255': (13, 'U0.16',
                       lambda tmp: 0 if tmp < 0 else (1 if tmp >= 1 else tmp),
                       lambda tmp: 0 <= tmp <= 1),
            'y_W255': (15, 'U0.16',
                       lambda tmp: 0 if tmp < 0 else (1 if tmp >= 1 else tmp),
                       lambda tmp: 0 <= tmp <= 1),

            'lv_R255': (17, 'U8.8',
                        lambda tmp: 0 if tmp < 0 else (256 if tmp >= 256 else tmp),
                        lambda tmp: 0 <= tmp <= 256),
            'lv_G255': (19, 'U8.8',
                        lambda tmp: 0 if tmp < 0 else (256 if tmp >= 256 else tmp),
                        lambda tmp: 0 <= tmp <= 256),
            'lv_B255': (21, 'U8.8',
                        lambda tmp: 0 if tmp < 0 else (256 if tmp >= 256 else tmp),
                        lambda tmp: 0 <= tmp <= 256),

            'x_R255': (23, 'U0.16',
                       lambda tmp: 0 if tmp < 0 else (1 if tmp >= 1 else tmp),
                       lambda tmp: 0 <= tmp <= 1),
            'y_R255': (25, 'U0.16',
                       lambda tmp: 0 if tmp < 0 else (1 if tmp >= 1 else tmp),
                       lambda tmp: 0 <= tmp <= 1),

            'x_G255': (27, 'U0.16',
                       lambda tmp: 0 if tmp < 0 else (1 if tmp >= 1 else tmp),
                       lambda tmp: 0 <= tmp <= 1),
            'y_G255': (29, 'U0.16',
                       lambda tmp: 0 if tmp < 0 else (1 if tmp >= 1 else tmp),
                       lambda tmp: 0 <= tmp <= 1),

            'x_B255': (31, 'U0.16',
                       lambda tmp: 0 if tmp < 0 else (1 if tmp >= 1 else tmp),
                       lambda tmp: 0 <= tmp <= 1),
            'y_B255': (33, 'U0.16',
                       lambda tmp: 0 if tmp < 0 else (1 if tmp >= 1 else tmp),
                       lambda tmp: 0 <= tmp <= 1),

            'TemperatureW': (35, 'S4.3',
                             lambda tmp: 14 if tmp <= 14 else (56 if tmp >= 56 else tmp),
                             lambda tmp: 14 <= tmp <= 56, 30),
            'TemperatureR': (36, 'S4.3',
                             lambda tmp: 14 if tmp <= 14 else (56 if tmp >= 56 else tmp),
                             lambda tmp: 14 <= tmp <= 56, 30),
            'TemperatureG': (37, 'S4.3',
                             lambda tmp: 14 if tmp <= 14 else (56 if tmp >= 56 else tmp),
                             lambda tmp: 14 <= tmp <= 56, 30),
            'TemperatureB': (38, 'S4.3',
                             lambda tmp: 14 if tmp <= 14 else (56 if tmp >= 56 else tmp),
                             lambda tmp: 14 <= tmp <= 56, 30),
            'TemperatureWD': (39, 'S4.3',
                              lambda tmp: 14 if tmp <= 14 else (56 if tmp >= 56 else tmp),
                              lambda tmp: 14 <= tmp <= 56, 30),

            'WhitePointGLR': (40, 'U8.0',
                              lambda tmp: 0 if tmp < 0 else (255 if tmp >= 255 else tmp),
                              lambda tmp: 0 <= tmp <= 255),
            'WhitePointGLG': (41, 'U8.0',
                              lambda tmp: 0 if tmp < 0 else (255 if tmp >= 255 else tmp),
                              lambda tmp: 0 <= tmp <= 255),
            'WhitePointGLB': (42, 'U8.0',
                              lambda tmp: 0 if tmp < 0 else (255 if tmp >= 255 else tmp),
                              lambda tmp: 0 <= tmp <= 255),
        })

    @property
    def nvm_data_len(self):
        return self._nvm_data_len

    # <editor-fold desc="Data Convert">
    def cvt_to_hex(self, value, flag, base_val=None):
        """
        @type value: float
        @type flag: str
        """
        data_len, sign_or_not, integ, deci = self._cvt_flag[flag]
        if base_val != None:
            value = value - base_val
        decimal, integral = math.modf(value)
        fraction = int(abs(decimal) * (1 << deci))
        integral = int(abs(integral))
        sign_bit = 1 if sign_or_not and (value < 0) else 0
        data = (sign_bit << (integ + deci)) | (integral << deci) | fraction
        return [f'0x{c:02X}' for c in data.to_bytes(data_len, 'big')]

    def cvt_from_hex(self, data_array, first_ind, flag, base_val=None):
        """
        @type data_array: []
        @type first_ind: int
        @type flag: str
        """
        data_len, sign_or_not, integ, deci = self._cvt_flag[flag]
        darray = [int(c, 16) for c in data_array[first_ind:(first_ind + data_len)]]
        a_value = int.from_bytes(darray, 'big', signed=False)

        def bit_mask(bit_len):
            mask = 0x01 if bit_len != 0 else 0
            for c in range(0, bit_len - 1):
                mask |= (mask << 1)
            return mask

        sign_bit_mask = bit_mask(integ + deci + 1)
        fraction_mask = bit_mask(deci)
        integral_mask = bit_mask(integ)

        fraction = a_value & fraction_mask
        integral = (a_value >> deci) & integral_mask
        sign = (a_value >> (deci + integ) & sign_bit_mask) if sign_or_not else 0

        value_without_sign = (integral + fraction / (1 << deci))
        value_with_sign = -1.0 * value_without_sign if sign else value_without_sign
        if base_val is not None:
            value_with_sign = value_with_sign + base_val
        return value_with_sign

    def uchar_checksum(self, data_array):
        """
        char_checksum The checksum is calculated in bytes. Each byte is translated as an unsigned integer
        @param data_array: data_array
        :return:
        """
        length = len(data_array)
        checksum = 0
        for i in range(0, length):
            checksum += int(data_array[i], 16)
            checksum &= 0xFF  # truncate to 1 byte

        return [f'0x{checksum:02X}', ]

        # </editor-fold>

    def uchar_checksum_chk(self, data_array):
        if (not data_array) or len(data_array) < self._nvm_data_len:
            return False
        cs = self.uchar_checksum(data_array[0:43 - self._dr_offset])
        return int(cs[0], 16) == int(data_array[43 - self._dr_offset], 16)

    def decode_raw_data(self, raw_data):
        """

        @type raw_data: list
        """
        var_data = {}
        for key, mapping in self._eeprom_map_group.items():
            memory_idx = mapping[0] - self._dr_offset
            flag = mapping[1]
            b_val = None
            if len(mapping) >= 5:
                b_val = mapping[4]
            var_data[key] = self.cvt_from_hex(raw_data, memory_idx, flag, base_val=b_val)
        var_data['CS'] = raw_data[43 - self._dr_offset]
        msg = '-'.join([f'{int(c1, 16):02X}' for c1 in raw_data[(44 - self._dr_offset):(47 - self._dr_offset)]])
        var_data['VALIDATION'] = msg
        var_data['DDIC_VERSION'] = raw_data[75 - self._dr_offset]
        return var_data

    def encode_parameter_items(self, raw_data, var_data):
        raw_data_cpy = raw_data.copy()
        items_chk_result = []
        for key, mapping in self._eeprom_map_group.items():
            memory_idx = mapping[0] - self._dr_offset
            flag = mapping[1]
            memory_len = self._cvt_flag[flag][0]
            tar_val = var_data[key]
            set_val = mapping[2](tar_val)

            items_chk_result.append(mapping[3](tar_val))
            b_val = None
            if len(mapping) >= 5:
                b_val = mapping[4]
            # encode the tar_val
            raw_data_cpy[memory_idx: (memory_idx + memory_len)] = self.cvt_to_hex(set_val, flag, base_val=b_val)

        raw_data_cpy[(43 - self._dr_offset):(44 - self._dr_offset)] = self.uchar_checksum(raw_data_cpy[0:(43 - self._dr_offset)])
        validate_field_result = 0
        for ind, val in enumerate(items_chk_result):
            validate_field_result |= 0 if val else (0x01 << (23 - ind))
        raw_data_cpy[(44 - self._dr_offset):(47 - self._dr_offset)] = [f'0x{c:02X}' for c in
                      validate_field_result.to_bytes(3, byteorder='big', signed=False)]
        raw_data_cpy[75 - self._dr_offset] = self._ddic_version
        return raw_data_cpy


def limit_cpu():
    p = psutil.Process(os.getpid())
    p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)


class seacliffmotStation(test_station.TestStation):

    _fixture: test_fixture_seacliff_mot.seacliffmotFixture
    _pool: mp.Pool

    def auto_find_com_ports(self):
        import serial.tools.list_ports
        import serial
        from pymodbus.client.sync import ModbusSerialClient
        from pymodbus.register_read_message import ReadHoldingRegistersResponse

        # <editor-fold desc="port configuration automatically">
        cfg = 'station_config_seacliff_mot.json'
        station_config = {
            'FixtureCom': 'Fixture',
            'ParticleCounter': 'ParticleCounter',
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
        if not self._station_config.FIXTURE_SIM and not self._station_config.IS_PROXY_COMMUNICATION:
            # config the port for fixture
            regex_port = station_config['FixtureCom']
            com_ports = [c[0] for c in port_list if re.search(regex_port, c[2], re.I | re.S)]
            if len(com_ports) != 1:
                port_err_message.append(f'Fixture')
            else:
                self.fixture_port = com_ports[-1]

        # config the port for scanner
        if self._station_config.FIXTURE_PARTICLE_COUNTER:
            regex_port = station_config['ParticleCounter']
            com_ports = [c[0] for c in port_list if re.search(regex_port, c[2], re.I | re.S)]
            if len(com_ports) == 1:
                self.fixture_particle_port = com_ports[-1]
            else:
                port_err_message.append(f'Particle counter')
        # </editor-fold>

        if not self._station_config.FIXTURE_SIM and len(port_err_message) > 0:
            raise seacliffmotStationError(f'Fail to find ports for fixture {";".join(port_err_message)}')

    def __init__(self, station_config, operator_interface):
        test_station.TestStation.__init__(self, station_config, operator_interface)
        self._fixture = None
        self._fixture = test_fixture_seacliff_mot.seacliffmotFixture(station_config, operator_interface)
        if hasattr(station_config, 'FIXTURE_SIM') and station_config.FIXTURE_SIM:
            self._fixture = projectstationFixture(station_config, operator_interface)
        self._equipment = test_equipment_seacliff_mot.seacliffmotEquipment(station_config, operator_interface)
        self._overall_errorcode = ''
        self._first_failed_test_result = None
        self._sw_version = f"1.2.9{self._station_config.SW_VERSION_SUFFIX if hasattr(self._station_config, 'SW_VERSION_SUFFIX') else ''}"
        self._latest_serial_number = None  # type: str
        self._the_unit = None  # type: pancakeDut
        self._retries_screen_on = 0
        self._is_screen_on_by_op = False
        self._is_cancel_test_by_op = False
        self._is_alignment_success = False
        self._module_left_or_right = None
        self._probe_con_status = False
        self._eepStationAssistant = EEPStationAssistant()
        self._eep_data_from_npy = {}
        self._multi_lock = mp.Lock()
        self.fixture_port = None
        self.fixture_particle_port = None
        self._is_exit = False
        self._is_running = False

    def initialize(self):
        try:
            self._operator_interface.print_to_console("Initializing Seacliff MOT station...{0}\n"
                                                      .format(self._sw_version))
            if self._station_config.AUTO_CFG_COMPORTS:
                self.auto_find_com_ports()
            else:
                self.fixture_port = self._station_config.FIXTURE_COMPORT
                self.fixture_particle_port = self._station_config.FIXTURE_PARTICLE_COMPORT

            msg = "find ports FIXTURE = {0}, PARTICLE COUNTER = {1}. \n" \
                .format(self.fixture_port,
                        self.fixture_particle_port)
            self._operator_interface.print_to_console(msg)
            eep_data_json_file = os.path.join(self._station_config.SEQUENCE_RELATIVEPATH, 'eep_p1_all.json')
            if os.path.exists(eep_data_json_file):
                with open(eep_data_json_file, 'r') as jf:
                    yyds = np.array(json.load(jf))
                    self._eep_data_from_npy = dict(zip(yyds[:, 0], yyds[:, 1:]))

            self._fixture.initialize(fixture_port=self.fixture_port,
                                     particle_port=self.fixture_particle_port,
                                     proxy_port=self._station_config.PROXY_ENDPOINT)

            self._station_config.DISTANCE_BETWEEN_CAMERA_AND_DATUM = self._fixture.calib_zero_pos()
            fixture_id = self._fixture.id()
            if not self._station_config.FIXTURE_SIM and fixture_id != self._station_config.STATION_NUMBER:
                raise seacliffmotStationError(
                    f'Fixture Id is not set correctly {self._station_config.STATION_NUMBER} != FW: {fixture_id}')
            self._operator_interface.print_to_console(
                f'update distance between camera and datum: {self._station_config.DISTANCE_BETWEEN_CAMERA_AND_DATUM}\n')
            self._equipment.initialize()
            self._equipment.open()
            threading.Thread(target=self._auto_backup_thr, daemon=True).start()
        except Exception as e:
            self._operator_interface.operator_input(None, str(e), 'error')
            raise

    def data_backup(self, source_path, target_path):
        if not os.path.exists(target_path):
            os.makedirs(target_path)
        if os.path.exists(source_path):
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    src_file = os.path.join(root, file)
                    shutil.move(src_file, target_path)

    # backup the raw data automatically
    def _auto_backup_thr(self):
        raw_dir = os.path.join(self._station_config.ROOT_DIR, self._station_config.RAW_IMAGE_LOG_DIR)
        bak_dir = raw_dir
        if hasattr(self._station_config, 'RAW_IMAGE_LOG_DIR_BAK'):
            bak_dir = os.path.join(self._station_config.ROOT_DIR, self._station_config.RAW_IMAGE_LOG_DIR_BAK)
        ex_file_list = []

        def date_time_check(fn):
            tm = None
            try:
                xx = fn[fn.rindex('_') + 1:]
                tm = datetime.datetime.strptime(xx, '%Y%m%d-%H%M%S').timestamp()
            except:
                pass
            return tm

        while not self._is_exit:
            if self._is_running:
                time.sleep(0.5)
                continue
            # delete all the bin files automatically.
            cur_time = datetime.datetime.now().hour + datetime.datetime.now().minute / 60
            if any([c1 <= cur_time <= c2 for c1, c2 in self._station_config.DATA_CLEAN_SCHEDULE]) and \
                    os.path.exists(raw_dir):
                mask = ['.bin', '.json']
                uut_raw_dir = [(c, date_time_check(c)) for c in os.listdir(raw_dir)
                               if os.path.isdir(os.path.join(raw_dir, c))
                               and os.path.exists(os.path.join(self._station_config.ROOT_DIR, 'factory-test_logs', f'{c}_P.log'))
                               and len(list(Path(os.path.join(raw_dir, c)).rglob('*.bin'))) > 0
                               and date_time_check(c)]
                uut_raw_dir = [os.path.join(raw_dir, c) for c, d in uut_raw_dir if time.time() - d
                               > self._station_config.DATA_CLEAN_SAVED_MINUTES]
                try:
                    def clean_camera_file(dirn):
                        if not os.path.isdir(dirn):
                            return
                        for fn in os.listdir(dirn):
                            tmp = os.path.join(dirn, fn)
                            if os.path.isdir(tmp):
                                clean_camera_file(tmp)
                            elif os.path.splitext(tmp)[1] in mask:
                                os.remove(tmp)
                    if len(uut_raw_dir) > 0:
                        clean_camera_file(uut_raw_dir[0])
                except Exception as e:
                    self._operator_interface.print_to_console(f'Fail to delete the bin exp={str(e)}', 'red')
                time.sleep(0.02)
                continue

            # backup all the data automatically
            if not(os.path.exists(bak_dir) and os.path.exists(raw_dir) and not os.path.samefile(bak_dir, raw_dir)):
                time.sleep(0.5)
                continue

            time.sleep(0.2)

            # uut_raw_dir = [(c, date_time_check(c)) for c in os.listdir(raw_dir)
            #                if os.path.isdir(os.path.join(raw_dir, c)) and c not in ex_file_list and date_time_check(c)]
            # # backup all the raw data which is created about 8 hours ago.
            # uut_raw_dir_old = [c for c, d in uut_raw_dir if time.time() - d > self._station_config.DATA_CLEAN_SAVED_MINUTES_PNG]
            # if len(uut_raw_dir_old) <= 0:
            #     time.sleep(1)
            #     continue
            # n1 = uut_raw_dir_old[-1]
            # try:
            #     self.data_backup(os.path.join(raw_dir, n1), os.path.join(os.path.join(bak_dir, n1)))
            #
            #     shutil.rmtree(os.path.join(raw_dir, n1))
            # except Exception as e:
            #     ex_file_list.append(n1)
            #     self._operator_interface.print_to_console(f'Fail to backup file to {bak_dir}. Exp = {str(e)}')

    def _close_fixture(self):
        if self._fixture is not None:
            self._operator_interface.print_to_console("Close...\n")
            self._fixture.close()
            self._fixture = None

    def close(self):
        self._is_exit = True
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
        pattern_info = None
        for c in self._station_config.TEST_ITEM_PATTERNS:
            if c.get('name') and c['name'] == name:
                pattern_info = c
        if not self._station_config.DUT_SIM and name in self._station_config.TEST_ITEM_PATTERNS_VERIFIED.keys():
            if len(self._eep_data) <= 0:
                pattern_info = None
            else:
                pattern_info['pattern'] = tuple([int(self._eep_data[c])
                                                 for c in self._station_config.TEST_ITEM_PATTERNS_VERIFIED[name]])
        return pattern_info

    @staticmethod
    def get_filenames_in_folder(parent_dir, pattern):
        file_names = []
        for home, dirs, files in os.walk(parent_dir):
            for file_name in files:
                if re.search(pattern, file_name, re.I):
                    file_names.append(os.path.join(home, file_name))
        file_names.sort(reverse=True)
        return file_names

    def chk_and_set_measured_value_by_name(self, test_log, item, value, value_msg=None):
        """
        :type test_log: test_station.TestRecord
        """
        exp_format_dic = {
            'OnAxis Lum': 1, 'OnAxis x': 4, 'OnAxis y': 4,
            'Lum_Ratio>0.7MaxLum_30deg': 2, "u'v'_delta_to_OnAxis_30deg": 4,
            "DispCen_x_display": 1, "DispCen_y_display": 1, "Disp_Rotate_x": 2,
            'R_x_corrected': 4, 'R_y_corrected': 4,
            'G_x_corrected': 3, 'G_y_corrected': 4,
            'B_x_corrected': 3, 'B_y_corrected': 4,
            'Instantaneous % of On-axis': 3,
        }
        if item in test_log.results_array():
            test_log.set_measured_value_by_name(item, value)
            did_pass = test_log.get_test_by_name(item).did_pass()
            if value_msg is None:
                value_msg = value
                disp_format = [(k, v) for k, v in exp_format_dic.items() if k in item]
                if any(disp_format) and isinstance(value, float):
                    value_msg = round_ex(value, disp_format[0][1])
            if hasattr(self._operator_interface, 'update_test_value'):
                self._operator_interface.update_test_value(item, value_msg, 1 if did_pass else -1)

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
        # if self._the_unit is None:
        #     raise test_station.TestStationProcessControlError(f'Fail to query dual_start for DUT {serial_number}.')
        self._probe_con_status = True
        if not self._station_config.FIXTURE_SIM:
            self._probe_con_status = self._fixture.query_probe_status() == 0

        self._overall_result = False
        self._overall_errorcode = ''
        latest_pattern_value_bak = None
        cpu_count = mp.cpu_count()
        cpu_count_used = self._station_config.TEST_CPU_COUNT
        self._pool = mp.Pool(cpu_count_used, limit_cpu)
        self._pool_alg_dic = {}
        self._exported_parametric = {}
        self._gl_W255 = {}
        self._temperature_dic = {}
        self._eep_data = {}
        try:
            self._is_running = True
            self._operator_interface.print_to_console(f"Initialize Test condition.={cpu_count_used}/{cpu_count}.. \n")
            self._operator_interface.print_to_console(
                "\n*********** Fixture at %s to load DUT ***************\n" % self.fixture_port)

            self._operator_interface.print_to_console("Testing Unit %s\n" % self._the_unit.serial_number)
            self._operator_interface.print_to_console("Initialize DUT... \n")

            test_log.set_measured_value_by_name_ex = types.MethodType(self.chk_and_set_measured_value_by_name, test_log)

            self._operator_interface.print_to_console("Testing Unit %s\n" % self._the_unit.serial_number)
            test_log.set_measured_value_by_name_ex('SW_VERSION', self._sw_version)
            equip_version = self._equipment.version()
            if isinstance(equip_version, dict):
                test_log.set_measured_value_by_name_ex('EQUIP_VERSION', equip_version.get('Lib_Version'))
            test_log.set_measured_value_by_name_ex('SPEC_VERSION', self._station_config.SPEC_VERSION)

            test_log.set_measured_value_by_name_ex("DUT_ModuleType", self._module_left_or_right)
            test_log.set_measured_value_by_name_ex('Carrier_ProbeConnectStatus', self._probe_con_status)
            test_log.set_measured_value_by_name_ex("DUT_ScreenOnRetries", self._retries_screen_on)
            test_log.set_measured_value_by_name_ex("DUT_ScreenOnStatus", self._is_screen_on_by_op)
            test_log.set_measured_value_by_name_ex("DUT_CancelByOperator", self._is_cancel_test_by_op)
            test_log.set_measured_value_by_name_ex("DUT_AlignmentSuccess", self._is_alignment_success)

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

            if len(self._station_config.TEST_ITEM_PATTERNS_VERIFIED) > 0:
                self._operator_interface.print_to_console(f'Try to read data from MODULE.\n')
                self._the_unit.nvm_speed_mode(mode='low')
                eep_success = False
                try:
                    write_status = self._the_unit.nvm_read_statistics()
                    self._operator_interface.print_to_console(f"Write status --- {str(write_status)}\n")
                    raw_data = self._the_unit.nvm_read_data()[2:]
                    if serial_number in self._eep_data_from_npy.keys():
                        self._operator_interface.print_to_console(f"Get EEP data for {serial_number} from npy.")
                        self._eep_data['WhitePointGLR'] = self._eep_data_from_npy[serial_number][0]
                        self._eep_data['WhitePointGLG'] = self._eep_data_from_npy[serial_number][1]
                        self._eep_data['WhitePointGLB'] = self._eep_data_from_npy[serial_number][2]
                    elif self._eepStationAssistant.uchar_checksum_chk(raw_data) and int(raw_data[-1], 16) >= 0x11:
                        self._operator_interface.print_to_console(f"RAW <-- {','.join(raw_data)}\n")
                        self._eep_data = self._eepStationAssistant.decode_raw_data(raw_data=raw_data)
                    if len(self._eep_data) > 0:
                        for k, v in self._station_config.TEST_ITEM_PATTERNS_VERIFIED.items():
                            verified_tuple = [(c, int(self._eep_data[c])) for c in v]
                            [test_log.set_measured_value_by_name_ex(f'UUT_{k}_{c}', v) for c, v in verified_tuple]
                        eep_success = True
                except Exception as e:
                    self._operator_interface.print_to_console(f'Fail to read initialized data, exp: {str(e)}')
                self._the_unit.nvm_speed_mode(mode='normal')
                self._the_unit.screen_off()
                self._the_unit.screen_on()

                test_log.set_measured_value_by_name_ex('UUT_READ_EEP_DATA', eep_success)
                self._operator_interface.print_to_console(f'set module to normal mode.\n')

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
                if os.path.exists(os.path.join(capture_path, 'measure_env.json')):
                    with open(os.path.join(capture_path, 'measure_env.json'), 'r') as json_f:
                        data = json.load(json_f)
                        self._temperature_dic = data['Temperature']
                else:
                    self._operator_interface.print_to_console(f'set default temperature for all patterns.\n')
            if not os.path.exists(capture_path):
                test_station.utils.os_utils.mkdir_p(capture_path)
                os.chmod(capture_path, 0o777)
            config = self._equipment.get_config()
            user_config = dict(self._station_config.CAM_INIT_CONFIG)
            config.update(dict([(k, v) for k, v in user_config.items() if k in config.keys()]))

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

                    dut_temp = self._temperature_dic.get(f'{pos_name}_{pattern_name}')
                    if dut_temp is None:
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

                patterns_in_testing = []
                for pattern_name, pre_condition, pattern_group in item_condition_a_patterns:
                    dut_temp = self._temperature_dic.get(f'{pos_name}_{pattern_name}')
                    if dut_temp is None:
                        dut_temp = 30
                    if is_query_temp:
                        self._operator_interface.print_to_console(f'query temperature for {pos_name}_{pattern_name}\n')
                        dut_temp = self._fixture.query_temp(test_fixture_seacliff_mot.QueryTempParts.UUTNearBy)
                    self._temperature_dic[f'{pos_name}_{pattern_name}'] = dut_temp
                    test_log.set_measured_value_by_name_ex(f'UUT_TEMPERATURE_{pos_name}_{pattern_name}', dut_temp)
                    if pre_condition:
                        self._operator_interface.print_to_console(f'Wait condition: [{pre_condition}] to complete.\n')
                        self._operator_interface.print_to_console('Please wait...')
                        pre_condition_pool_keys = [f'{pos_name}_{c}' for c in pos_item.get(pre_condition)]
                        while len([pn for pn, pv in self._pool_alg_dic.items()
                                   if (pn in pre_condition_pool_keys) and not pv]) > 0:
                            self._operator_interface.wait(1, '.')
                        self._operator_interface.wait(0, '\n')
                        self._operator_interface.print_to_console(f'pattern group [{pre_condition}] finished.\n')

                    rel_pattern_name = pattern_name
                    if pattern_name in self._station_config.ANALYSIS_GRP_COLOR_PATTERN_EX.keys():
                        ref_patterns = ['W255', 'RGBBoresight']
                        ref_pattern = self._station_config.ANALYSIS_GRP_COLOR_PATTERN_EX[pattern_name]
                        exp_data = tuple([self._exported_parametric[f'{pos_name}_{c}'] for c in ref_patterns])
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
            try:
                self._operator_interface.print_to_console(str(e))
                self._operator_interface.print_to_console('Reset taprisiot automatically by command.\n')
                self._equipment.reset()
                self._equipment.close()
                self._operator_interface.print_to_console('open taprisiot automatically.\n')
                self._equipment.open()
            except BaseException as e2:
                self._operator_interface.print_to_console(f'Taprisiot Error E2: {str(e2)}\n')
            finally:
                self._operator_interface.print_to_console(f'Taprisiot Error: {str(e)}\n')
                self._operator_interface.operator_input('Taprisiot Error, Restart Software !!!', str(e), msg_type='error')
            os._exit(1)
        except test_fixture_seacliff_mot.seacliffmotFixtureError as e:
            self._operator_interface.print_to_console(f'Fixture Error: {str(e)}\n')
            self._operator_interface.operator_input('Fixture Error, Restart Software !!!', str(e), msg_type='error')
            os._exit(1)
        except seacliffmotStationError as e:
            self._operator_interface.operator_input(None, str(e), msg_type='error')
            self._operator_interface.print_to_console(str(e))
        except (Exception, BaseException) as e:
            self._operator_interface.operator_input(None, f'Error: {str(e)} \n', msg_type='error')
            raise
        except:
            self._operator_interface.operator_input(None, f'Please connect with myzy firstly.', msg_type='error')
        finally:
            try:
                self._pool.close()
                self._operator_interface.print_to_console('Wait ProcessingPool to complete.\n')
                self._operator_interface.print_to_console('Please wait...')
                self._the_unit.close()
                self._fixture.unload()
            except:
                pass
            while len([pn for pn, pv in self._pool_alg_dic.items() if not pv]) > 0:
                self._operator_interface.wait(1, '.')
            self._operator_interface.wait(0, '\n')
            self._operator_interface.print_to_console('\nfinish to process\n')
            self._pool.join()
            self._pool = None
            self._the_unit = None
            self._is_running = False
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
        config = self._equipment.get_config()
        config.update({'fileNamePrepend': pre_file_name})
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
            self._the_unit.initialize(com_port=self._station_config.DUT_COMPORT,
                                      eth_addr=self._station_config.DUT_ETH_PROXY_ADDR)
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
                            # self._the_unit.reboot()  # Reboot
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
                    # self._the_unit = None
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
        if not os.path.exists(os.path.join(capture_path, 'measure_env.json')):
            with open(os.path.join(capture_path, 'measure_env.json'), 'w') as json_f:
                json.dump({'Temperature': self._temperature_dic}, json_f, ensure_ascii=True, indent=4)
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
            coeff = opt['coeff']
            mot_alg = test_equipment_seacliff_mot.MotAlgorithmHelper(coeff, save_plots=save_plots)
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
                            self._multi_lock.acquire()
                            try:
                                pos_name_i, pattern_name_i, pri_k_i, distortion_exports = res
                                if isinstance(distortion_exports, dict):
                                    self._exported_parametric[f'{pos_name_i}_{pattern_name_i}'] = distortion_exports
                                    for export_key, export_value in distortion_exports.items():
                                        measure_item_name = '{0}_{1}_{2}_{3}'.format(
                                            pos_name_i, pattern_name_i, pri_k_i, export_key)
                                        test_log.set_measured_value_by_name_ex(measure_item_name, export_value)
                                self._operator_interface.print_to_console(f'finish export {pos_name_i}, {pattern_name_i}')
                                self._pool_alg_dic[f'{pos_name_i}_{pattern_name_i}'] = True
                            except Exception as e2:
                                self._operator_interface.print_to_console(f'err: distortion_callback {str(e2)}.\n')
                            self._multi_lock.release()

                        opt = {
                            'pri_key': pri_k,
                            'fil': pri_v,
                            'save_plots': self._station_config.AUTO_SAVE_PROCESSED_PNG,
                            'ModuleTemp': self._temperature_dic[f'{pos_name}_{pattern_name}'],
                            'coeff': self._station_config.COLORMATRIX_COEFF,
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
        err_msg = None
        try:
            alg_optional = opt['alg']
            fil = opt['filename']
            save_plots = opt['save_plots']
            coeff = opt['coeff']
            mot_alg = test_equipment_seacliff_mot.MotAlgorithmHelper(coeff, save_plots=save_plots)
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
            err_msg = f'normal_pattern_parametric_export_ex_parallel E: {str(e)} Arg: {pattern_name} OPT: {opt}'
        return pos_name, pattern_name, parametric_exports, err_msg

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
                        self._multi_lock.acquire()
                        try:
                            pos_name_i, pattern_name_i, color_exports, err_msg = res
                            if isinstance(color_exports, dict):
                                self._exported_parametric[f'{pos_name_i}_{pattern_name_i}'] = color_exports
                                for export_key, export_value in color_exports.items():
                                    measure_item_name = '{0}_{1}_{2}'.format(
                                        pos_name_i, pattern_name_i, export_key)

                                    if export_key in self._station_config.COMPENSATION_COEFF[self._module_left_or_right]:
                                        cp = self._station_config.COMPENSATION_COEFF[self._module_left_or_right][export_key]
                                        if isinstance(export_value, float):
                                            export_value += cp
                                        test_log.set_measured_value_by_name_ex(f'COMPENSATION_{export_key}', cp)
                                    test_log.set_measured_value_by_name_ex(measure_item_name, export_value)
                            self._operator_interface.print_to_console(f'finish export {pos_name_i}, {pattern_name_i}, err_msg: {err_msg}')
                            self._pool_alg_dic[f'{pos_name_i}_{pattern_name_i}'] = True
                        except Exception as e2:
                            self._operator_interface.print_to_console(f'err: color_pattern_callback {str(e2)}.\n')
                        self._multi_lock.release()
                    dut_temp = self._temperature_dic[f'{pos_name}_{ana_pattern}']
                    opt = {
                        'alg': alg_optional,
                        'filename': file_x[0],
                        'temperature': dut_temp,
                        'moduleLR': self._module_left_or_right,
                        'save_plots': self._station_config.AUTO_SAVE_PROCESSED_PNG,
                        'coeff': self._station_config.COLORMATRIX_COEFF,
                    }
                    self._pool.apply_async(
                        seacliffmotStation.normal_pattern_parametric_export_ex_parallel,
                        (pos_name, ana_pattern, opt),
                        callback=color_pattern_parametric_export_ex_parallel_callback)
                    self._pool_alg_dic[f'{pos_name}_{ana_pattern}'] = False

                except Exception as e:
                    self._operator_interface.print_to_console(
                        f'Fail to export data for pattern: {pos_name}_{ana_pattern}, {str(e)}\n')

    @staticmethod
    def grade_a_pattern_parametric_export_ex_parallel(pos_name, pattern_name, opt):
        # print(f'Try to do parametric_export_ex_parallel _ {pos_name}: {pattern_name}')
        white_dot_exports = None
        err_msg = None
        XYZ_W = []
        try:
            fil = opt['filename']
            fil_ref = opt['refname']
            save_plots = opt['save_plots']
            coeff = opt['coeff']

            mot_alg = test_equipment_seacliff_mot.MotAlgorithmHelper(coeff, save_plots=save_plots)
            XYZ_W = mot_alg.white_dot_pattern_w255_read(fil_ref, multi_process=False)
            white_dot_exports = mot_alg.white_dot_pattern_parametric_export(XYZ_W,
                        opt['GL'], opt['x_w'], opt['y_w'], temp_w=opt['Temp_W'],
                        module_temp=opt['ModuleTemp'], xfilename=fil)
        except Exception as e:
            err_msg = f'grade_a_pattern_parametric_export_ex_parallel E: {str(e)} Arg: {pattern_name} OPT: {opt}'
        finally:
            del XYZ_W
        return pos_name, pattern_name, white_dot_exports, err_msg

    def grade_a_patterns_parametric_export_ex(self, ana_pos_item, ana_pattern, capture_path, test_log):
        self._operator_interface.print_to_console(f'Try to analysis data for {ana_pos_item} --> {ana_pattern}\n')
        for pos_item in self._station_config.TEST_ITEM_POS:
            pos_name = pos_item['name']
            item_patterns = pos_item.get('condition_A_patterns')
            if (ana_pos_item != pos_name) or (item_patterns is None):
                continue

            for pattern_name, __, __ in item_patterns:
                if pattern_name not in self._station_config.ANALYSIS_GRP_COLOR_PATTERN_EX.keys()\
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
                            self._multi_lock.acquire()
                            try:
                                pos_name_i, pattern_name_i, white_dot_exports, err_msg = res
                                if isinstance(white_dot_exports, dict):
                                    self._exported_parametric[f'{pos_name_i}_{pattern_name_i}'] = white_dot_exports
                                    for export_key, export_value in white_dot_exports.items():
                                        measure_item_name = '{0}_{1}_{2}'.format(
                                            pos_name_i, pattern_name_i, export_key)
                                        test_log.set_measured_value_by_name_ex(measure_item_name, export_value)
                                self._operator_interface.print_to_console(f'finish export {pos_name_i}, {pattern_name_i}, err_msg: {err_msg}')
                                self._pool_alg_dic[f'{pos_name_i}_{pattern_name_i}'] = True
                            except Exception as e2:
                                self._operator_interface.print_to_console(f'err: grade_a_callback {str(e2)}.\n')
                            self._multi_lock.release()
                        opt = {'ModuleTemp': self._temperature_dic[f'{pos_name}_{pattern_name}'],
                               'Temp_W': self._temperature_dic[f'{pos_name}_{ref_pattern}'],
                               'filename': file_x[0],
                               'refname': file_ref[0],
                               'save_plots': self._station_config.AUTO_SAVE_PROCESSED_PNG,
                               'coeff': self._station_config.COLORMATRIX_COEFF}
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


