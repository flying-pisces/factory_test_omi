import hardware_station_common.test_station.test_station as test_station
import test_station.test_fixture.test_fixture_seacliff_eeprom as test_fixture
import test_station.test_equipment.test_equipment_seacliff_eeprom as test_equipment
import hardware_station_common.utils.gui_utils as gui_utils
import tkinter as tk
import test_station.dut.dut as dut
import pprint
import types
import ctypes
import math
import os
import sys
import time
import json
import Pmw
import shutil
import collections
import numpy as np
import suds.client
import tkinter.simpledialog
import tkinter as tk
import datetime


class EEPROMUserInputDialog(gui_utils.Dialog):
    def __init__(self, station_config, operator_interface, title=None):
        """

        @type operator_interface: operator_interface.
        """
        self._operator_interface = operator_interface
        self._station_config = station_config  # type: station_config
        self.is_looping = True
        self._value_dic = None
        super(EEPROMUserInputDialog, self).__init__(self._operator_interface._prompt.master, title)

    def body(self, master):
        self._boresight_x = Pmw.EntryField(master, labelpos=tk.W, label_text="boresight_x", value="0",
                                           validate={"validator": "real", "min": -128, "max": 128})
        self._boresight_y = Pmw.EntryField(master, labelpos=tk.W, label_text="boresight_y", value="0",
                                           validate={"validator": "real", "min": -128, "max": 128})
        self._boresight_r = Pmw.EntryField(master, labelpos=tk.W, label_text="rotation_r", value="0",
                                           validate={"validator": "real", "min": -2, "max": 2})

        self._w255_lv = Pmw.EntryField(master, labelpos=tk.W, label_text="W255_Lv", value="0",
                                           validate={"validator": "real", "min": 0, "max": 256})
        self._w255_x = Pmw.EntryField(master, labelpos=tk.W, label_text="W255_x", value="0",
                                           validate={"validator": "real", "min": 0, "max": 1})
        self._w255_y = Pmw.EntryField(master, labelpos=tk.W, label_text="W255_y", value="0",
                                           validate={"validator": "real", "min": 0, "max": 1})

        self._r255_lv = Pmw.EntryField(master, labelpos=tk.W, label_text="R255_Lv", value="0",
                                           validate={"validator": "real", "min": 0, "max": 256})
        self._r255_x = Pmw.EntryField(master, labelpos=tk.W, label_text="R255_x", value="0",
                                           validate={"validator": "real", "min": 0, "max": 1})
        self._r255_y = Pmw.EntryField(master, labelpos=tk.W, label_text="R255_y", value="0",
                                           validate={"validator": "real", "min": 0, "max": 1})

        self._g255_lv = Pmw.EntryField(master, labelpos=tk.W, label_text="G255_Lv", value="0",
                                           validate={"validator": "real", "min": 0, "max": 256})
        self._g255_x = Pmw.EntryField(master, labelpos=tk.W, label_text="G255_x", value="0",
                                           validate={"validator": "real", "min": 0, "max": 1})
        self._g255_y = Pmw.EntryField(master, labelpos=tk.W, label_text="G255_y", value="0",
                                           validate={"validator": "real", "min": 0, "max": 1})

        self._b255_lv = Pmw.EntryField(master, labelpos=tk.W, label_text="B255_Lv", value="0",
                                           validate={"validator": "real", "min": 0, "max": 256})
        self._b255_x = Pmw.EntryField(master, labelpos=tk.W, label_text="B255_x", value="0",
                                           validate={"validator": "real", "min": 0, "max": 1})
        self._b255_y = Pmw.EntryField(master, labelpos=tk.W, label_text="B255_y", value="0",
                                           validate={"validator": "real", "min": 0, "max": 1})

        items = [self._boresight_x, self._boresight_y, self._boresight_r, self._w255_lv, self._w255_x, self._w255_y,
                 self._r255_lv, self._r255_x, self._r255_y, self._g255_lv, self._g255_x, self._g255_y,
                 self._b255_lv, self._b255_x, self._b255_y]
        for idx, widget in enumerate(items):
            row = idx // 3
            col = idx % 3
            widget.grid(row=row, column=col)
        Pmw.alignlabels(items)
        return self._boresight_x  # initial focus

    def validate(self):
        try:
            self._value_dic = None
            boresight_x = float(self._boresight_x.getvalue())
            boresight_y = float(self._boresight_y.getvalue())
            boresight_r = float(self._boresight_r.getvalue())
            w255 = [float(c.getvalue()) for c in [self._w255_lv, self._w255_x, self._w255_y]]
            r255 = [float(c.getvalue()) for c in [self._r255_lv, self._r255_x, self._r255_y]]
            g255 = [float(c.getvalue()) for c in [self._g255_lv, self._g255_x, self._g255_y]]
            b255 = [float(c.getvalue()) for c in [self._b255_lv, self._b255_x, self._b255_y]]
            self._value_dic = {
                'display_boresight_x': boresight_x, 'display_boresight_y': boresight_y,  'rotation': boresight_r,
                'lv_W255': w255[0], 'x_W255': w255[1], 'y_W255': w255[2],
                'lv_R255': r255[0], 'x_R255': r255[1], 'y_R255': r255[2],
                'lv_G255': g255[0], 'x_G255': g255[1], 'y_G255': g255[2],
                'lv_B255': b255[0], 'x_B255': b255[1], 'y_B255': b255[2],
            }
            return True
        except Exception as e:
            self._operator_interface.print_to_console('Fail to validate data. {0}'.format(e.args))
            return False

    def current_cfg(self):
        return dict(self._value_dic) if self._value_dic is not None else None

    def apply(self):
        pass

    def cancel(self):
        self.is_looping = False
        super(EEPROMUserInputDialog, self).cancel()


def chk_and_set_measured_value_by_name(test_log, item, value):
    """

    :type test_log: test_station.TestRecord
    """
    if item in test_log.results_array():
        test_log.set_measured_value_by_name(item, value)
    else:
        pprint.pprint(item)


class seacliffeepromError(Exception):
    pass


class seacliffeepromStation(test_station.TestStation):
    """
        pancakeeeprom Station
    """
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
        self._operator_interface.print_to_console("auto config com ports...\n")
        self._station_config.DUT_COMPORT = None
        com_ports = list(serial.tools.list_ports.comports())

        for com in com_ports:
            hit_success = False
            if self._station_config.DUT_COMPORT is None:
                a_serial = None
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
                    if a_serial is not None:
                        a_serial.close()

            if hit_success:
                continue


    def __init__(self, station_config, operator_interface):
        test_station.TestStation.__init__(self, station_config, operator_interface)
        if (hasattr(self._station_config, 'IS_PRINT_TO_LOG')
                and self._station_config.IS_PRINT_TO_LOG):
            sys.stdout = self
            sys.stderr = self
            sys.stdin = None
        self._fixture = test_fixture.seacliffeepromFixture(station_config, operator_interface)
        self._equip = test_equipment.seacliffeepromEquipment(station_config, operator_interface)
        self._overall_errorcode = ''
        self._first_failed_test_result = None
        self._sw_version = '1.0.1'
        self._cvt_flag = {
            'S7.8': (2, True, 7, 8),
            'S1.6': (1, True, 1, 6),
            'U8.0': (1, False, 8, 0),
            'U0.16': (2, False, 0, 16),
            'U8.8': (2, False, 8, 8),
        }
        self._eeprom_map_group = collections.OrderedDict({
            'display_boresight_x': (6, 'S7.8', lambda tmp: -128 if tmp <= -128 else (128 if tmp >= 128 else None)),
            'display_boresight_y': (8, 'S7.8', lambda tmp: -128 if tmp <= -128 else (128 if tmp >= 128 else None)),
            'rotation': (10, 'S1.6', lambda tmp: -2 if tmp <= -2 else (2 if tmp >= 2 else None)),

            'lv_W255': (11, 'U8.8', lambda tmp: 0 if tmp < 0 else (256 if tmp >= 256 else None)),
            'x_W255': (13, 'U0.16', lambda tmp: 0 if tmp < 0 else (1 if tmp >= 1 else None)),
            'y_W255': (15, 'U0.16', lambda tmp: 0 if tmp < 0 else (1 if tmp >= 1 else None)),

            'lv_R255': (17, 'U8.8', lambda tmp: 0 if tmp < 0 else (256 if tmp >= 256 else None)),
            'lv_G255': (19, 'U8.8', lambda tmp: 0 if tmp < 0 else (256 if tmp >= 256 else None)),
            'lv_B255': (21, 'U8.8', lambda tmp: 0 if tmp < 0 else (256 if tmp >= 256 else None)),

            'x_R255': (23, 'U0.16', lambda tmp: 0 if tmp < 0 else (1 if tmp >= 1 else None)),
            'y_R255': (25, 'U0.16', lambda tmp: 0 if tmp < 0 else (1 if tmp >= 1 else None)),

            'x_G255': (27, 'U0.16', lambda tmp: 0 if tmp < 0 else (1 if tmp >= 1 else None)),
            'y_G255': (29, 'U0.16', lambda tmp: 0 if tmp < 0 else (1 if tmp >= 1 else None)),

            'x_B255': (31, 'U0.16', lambda tmp: 0 if tmp < 0 else (1 if tmp >= 1 else None)),
            'y_B255': (33, 'U0.16', lambda tmp: 0 if tmp < 0 else (1 if tmp >= 1 else None)),
        })

    def initialize(self):
        try:
            self._operator_interface.print_to_console(f'Initializing pancake EEPROM station...VER:{self._sw_version}\n')
            if self._station_config.AUTO_CFG_COMPORTS:
                self.auto_find_com_ports()

            msg = "find ports DUT = {0}. \n" \
                .format(self._station_config.DUT_COMPORT)
            self._operator_interface.print_to_console(msg)

            self._fixture.initialize()
            self._equip.initialize()
        except:
            self._operator_interface.operator_input(None, 'Fail to initialize test_station. ', 'error')
            raise

    def close(self):
        self._operator_interface.print_to_console("Close...\n")
        self._operator_interface.print_to_console("there, I'm shutting the station down..\n")
        self._fixture.close()

    # <editor-fold desc="Data Convert">
    def cvt_to_hex(self, value, flag):
        """
        @type value: float
        @type flag: str
        """
        data_len, sign_or_not, integ, deci = self._cvt_flag[flag]
        decimal, integral = math.modf(value)
        fraction = int(abs(decimal) * (1 << deci))
        integral = int(abs(integral))
        sign_bit = 1 if sign_or_not and (value < 0) else 0
        data = (sign_bit << (integ + deci)) | (integral << deci) | fraction
        return [f'0x{c:02X}' for c in data.to_bytes(data_len, 'big')]

    def cvt_from_hex(self, data_array, first_ind, flag):
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
        return -1.0 * value_without_sign if sign else value_without_sign

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

    def _do_test(self, serial_number, test_log):
        msg0 = 'info --> write protect: {0}, emulator_dut: {1}, emulator_equip: {2}, emulator_fixture: {3},' \
               ' camera verify: {4}, ver:{5}\n' \
            .format(
            self._station_config.NVM_WRITE_PROTECT, self._station_config.DUT_SIM,
            self._station_config.EQUIPMENT_SIM, self._station_config.FIXTURE_SIM,
            self._station_config.CAMERA_VERIFY_ENABLE, self._sw_version)
        self._operator_interface.print_to_console(msg0)
        self._overall_result = False
        self._overall_errorcode = ''
        self._operator_interface.print_to_console('waiting user to input the parameters...\n')
        test_log.set_measured_value_by_name_ex = types.MethodType(chk_and_set_measured_value_by_name, test_log)
        the_unit = dut.pancakeDut(serial_number, self._station_config, self._operator_interface)
        if self._station_config.DUT_SIM:
            the_unit = dut.projectDut(serial_number, self._station_config, self._operator_interface)

        calib_data = self._station_config.CALIB_REQ_DATA
        try:
            if self._station_config.USER_INPUT_CALIB_DATA in [0x01, True]:
                dlg = EEPROMUserInputDialog(self._station_config, self._operator_interface,
                                            'EEPROM Parameter for SN:{0}'.format(serial_number))
                while dlg.is_looping:
                    self._operator_interface.wait(0.5, None, False)
                calib_data = dlg.current_cfg()
            elif self._station_config.USER_INPUT_CALIB_DATA == 0x02:
                calib_data = None
                calib_data_json_fn = os.path.join(self._station_config.CALIB_REQ_DATA_FILENAME,
                                                  f'eeprom_session_miz_{serial_number}.json')
                if os.path.exists(calib_data_json_fn):
                    with open(f'{calib_data_json_fn}', 'r') as json_file:
                        calib_data = json.load(json_file)
                        eep_keys = set(self._eeprom_map_group.keys())
                        if not eep_keys.issubset(calib_data.keys()):
                            msg = f'unable to parse all the items from input items.\n'
                            self._operator_interface.print_to_console(f'{eep_keys}\n')
                            calib_data = None
                            self._operator_interface.operator_input(None, msg, msg_type='error')
        except:
            calib_data = None
            pass

        if calib_data is None:
            self._operator_interface.operator_input(None, f'unable to get enough information for {serial_number}.\n')
            raise test_station.TestStationProcessControlError(f'unable to get enough information for DUT {serial_number}.')

        self._operator_interface.print_to_console("Start write data to DUT. %s\n" % the_unit.serial_number)
        test_log.set_measured_value_by_name_ex('SW_VERSION', self._sw_version)
        try:
            the_unit.initialize()
            the_unit.screen_on()
            the_unit.display_image(0x01)

            self._operator_interface.print_to_console('read write count for nvram ...\n')
            write_status = the_unit.nvm_read_statistics()
            write_count = 0
            post_write_count = 0
            if self._station_config.DUT_SIM:
                write_status = [0, 1]
            if write_status is not None:
                write_count = int(write_status[1])
                test_log.set_measured_value_by_name_ex('PRE_WRITE_COUNTS', write_count)

            # TODO: capture the image to determine the status of DUT.
            self._operator_interface.print_to_console('image capture and verification ...\n')
            judge_by_camera = False
            if self._station_config.CAMERA_VERIFY_ENABLE:
                for idx, check_cfg in enumerate(self._station_config.CAMERA_CHECK_CFG):
                    pattern = check_cfg.get('pattern')
                    chk_lsl = check_cfg.get('chk_lsl')
                    chk_usl = check_cfg.get('chk_usl')
                    determine = check_cfg.get('determine')
                    self._operator_interface.print_to_console('check image with {0} ...\n'.format(pattern))
                    the_unit.display_color(pattern)
                    percent = int(self._fixture.CheckImage(pattern, chk_lsl, chk_usl) * 100)
                    self._operator_interface.print_to_console(
                        'check result with pattern: {0}:{1} ...{2}\n'.format(pattern, determine, percent))
                    if (determine is None) or (determine[0] <= percent <= determine[1]):
                        judge_by_camera = True
                    else:
                        judge_by_camera = False
                    if not judge_by_camera:
                        break
            if self._station_config.FIXTURE_SIM or (not self._station_config.CAMERA_VERIFY_ENABLE):
                judge_by_camera = True
            test_log.set_measured_value_by_name_ex('JUDGED_BY_CAM', judge_by_camera)

            if (0 <= write_count < self._station_config.NVM_WRITE_COUNT_MAX) and judge_by_camera:
                self._operator_interface.print_to_console('read all data from eeprom ...\n')

                var_data = dict(calib_data)  # type: dict

                raw_data = ['0x00'] * 45
                if not self._station_config.DUT_SIM:
                    raw_data = the_unit.nvm_read_data()[2:]
                # mark: convert raw data before flush to dict.
                for key, mapping in self._eeprom_map_group.items():
                    memory_idx = mapping[0] - 6
                    flag = mapping[1]
                    var_data[key] = self.cvt_from_hex(raw_data, memory_idx, flag)

                var_data['CS'] = raw_data[29]

                msg = '-'.join([f'{int(c1, 16):02X}' for c1 in raw_data[30:32]])
                var_data['VALIDATION'] = msg
                # mark: save them to database.
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_BORESIGHT_X', var_data.get('display_boresight_x'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_BORESIGHT_Y', var_data.get('display_boresight_y'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_ROTATION', var_data.get('rotation'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_LV_W255', var_data.get('lv_W255'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_X_W255', var_data.get('x_W255'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_Y_W255', var_data.get('y_W255'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_LV_R255', var_data.get('lv_R255'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_X_R255', var_data.get('x_R255'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_Y_R255', var_data.get('y_R255'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_LV_G255', var_data.get('lv_G255'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_X_G255', var_data.get('x_G255'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_Y_G255', var_data.get('y_G255'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_LV_B255', var_data.get('lv_B255'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_X_B255', var_data.get('x_B255'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_Y_B255', var_data.get('y_B255'))

                test_log.set_measured_value_by_name_ex('CURRENT_CS', var_data.get('CS'))
                test_log.set_measured_value_by_name_ex('CURRENT_VALIDATION_FIELD', var_data.get('VALIDATION'))

                raw_data_cpy = raw_data.copy()  # place holder for all the bytes.
                var_data = dict(calib_data)  # type: dict

                items_chk_result = []
                for key, mapping in self._eeprom_map_group.items():
                    memory_idx = mapping[0] - 6
                    flag = mapping[1]
                    memory_len = self._cvt_flag[flag][0]
                    tar_val = var_data[key]
                    val = mapping[2](tar_val)
                    if val is not None:  # indicate the value is out of range
                        tar_val = val
                    items_chk_result.append(val is None)
                    # encode the tar_val
                    raw_data_cpy[memory_idx: (memory_idx+memory_len)] = self.cvt_to_hex(tar_val, flag)

                raw_data_cpy[29:30] = self.uchar_checksum(raw_data_cpy[0:25])
                validate_field_result = 0
                for ind, val in enumerate(items_chk_result):
                    validate_field_result |= 0 if val else (0x01 << (15-ind))
                raw_data_cpy[30:32] = [f'0x{c:02X}' for c in
                                       validate_field_result.to_bytes(2, byteorder='big', signed=False)]
                # TODO: config all the data to array.

                print('Write configuration...........\n')
                self._operator_interface.print_to_console('write configuration to eeprom ...\n')
                if not self._station_config.NVM_WRITE_PROTECT:
                    the_unit.nvm_write_data(raw_data_cpy)
                else:
                    self._operator_interface.print_to_console('write configuration protected ...\n')
                    print('WR_DATA_SIM:  \n' + ','.join(raw_data_cpy))
                    time.sleep(self._station_config.DUT_NVRAM_WRITE_TIMEOUT)

                test_log.set_measured_value_by_name_ex('CFG_BORESIGHT_X', var_data.get('display_boresight_x'))
                test_log.set_measured_value_by_name_ex('CFG_BORESIGHT_Y', var_data.get('display_boresight_y'))
                test_log.set_measured_value_by_name_ex('CFG_ROTATION', var_data.get('rotation'))
                test_log.set_measured_value_by_name_ex('CFG_LV_W255', var_data.get('lv_W255'))
                test_log.set_measured_value_by_name_ex('CFG_X_W255', var_data.get('x_W255'))
                test_log.set_measured_value_by_name_ex('CFG_Y_W255', var_data.get('y_W255'))
                test_log.set_measured_value_by_name_ex('CFG_LV_R255', var_data.get('lv_R255'))
                test_log.set_measured_value_by_name_ex('CFG_X_R255', var_data.get('x_R255'))
                test_log.set_measured_value_by_name_ex('CFG_Y_R255', var_data.get('y_R255'))
                test_log.set_measured_value_by_name_ex('CFG_LV_G255', var_data.get('lv_G255'))
                test_log.set_measured_value_by_name_ex('CFG_X_G255', var_data.get('x_G255'))
                test_log.set_measured_value_by_name_ex('CFG_Y_G255', var_data.get('y_G255'))
                test_log.set_measured_value_by_name_ex('CFG_LV_B255', var_data.get('lv_B255'))
                test_log.set_measured_value_by_name_ex('CFG_X_B255', var_data.get('x_B255'))
                test_log.set_measured_value_by_name_ex('CFG_Y_B255', var_data.get('y_B255'))

                test_log.set_measured_value_by_name_ex('CFG_CS', raw_data_cpy[29])
                msg = '-'.join([f'{int(c1, 16):02X}' for c1 in raw_data_cpy[30:32]])
                test_log.set_measured_value_by_name_ex('CFG_VALIDATION_FIELD', msg)

                self._operator_interface.print_to_console('screen off ...\n')
                the_unit.screen_off()

                # TODO: it is able to do verification after flushing the NVRAM.
                self._operator_interface.print_to_console('screen on ...\n')
                the_unit.screen_on()
                self._operator_interface.print_to_console('read configuration from eeprom ...\n')
                data_from_nvram = raw_data_cpy.copy()
                if not self._station_config.DUT_SIM:
                    data_from_nvram = the_unit.nvm_read_data()[2:]
                data_from_nvram_cap = [c.upper() for c in data_from_nvram]
                raw_data_cpy_cap = [c.upper() for c in raw_data_cpy]
                test_log.set_measured_value_by_name_ex('POST_DATA_CHECK', data_from_nvram_cap == raw_data_cpy_cap)

                self._operator_interface.print_to_console('read write count for nvram ...\n')
                write_status = the_unit.nvm_read_statistics()
                if write_status is not None:
                    post_write_count = int(write_status[1])
                test_log.set_measured_value_by_name_ex('POST_WRITE_COUNTS', post_write_count)

                test_log.set_measured_value_by_name_ex(
                    'WRITE_COUNTS_CHECK', (post_write_count == (write_count + 1)))
            else:
                self._operator_interface.print_to_console(
                    f'Exp: write count = {self._station_config.NVM_WRITE_COUNT_MAX} or fail to {judge_by_camera}\n')
            the_unit.close()
        except (seacliffeepromError, dut.DUTError) as e:
            self._operator_interface.print_to_console("Non-parametric Test Failure\n")
            return self.close_test(test_log)

        else:
            return self.close_test(test_log)

    def close_test(self, test_log):
        ### Insert code to gracefully restore fixture to known state, e.g. clear_all_relays() ###
        self._overall_result = test_log.get_overall_result()
        self._first_failed_test_result = test_log.get_first_failed_test_result()
        return self._overall_result, self._first_failed_test_result

    def is_ready(self):
        if os.path.exists(self._station_config.CALIB_REQ_DATA_FILENAME):
            shutil.rmtree(self._station_config.CALIB_REQ_DATA_FILENAME)
        self._fixture.is_ready()

