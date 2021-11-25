import hardware_station_common.test_station.test_station as test_station
import test_station.test_fixture.test_fixture_seacliff_eeprom as test_fixture_eeprom
import test_station.test_equipment.test_equipment_seacliff_eeprom as test_equipment_seacliff_eeprom
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
import datetime
import hardware_station_common


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

        self._tempW = Pmw.EntryField(master, labelpos=tk.W, label_text="Temp. W", value="30",
                                      validate={"validator": "real", "min": 30, "max": 60})
        self._tempR = Pmw.EntryField(master, labelpos=tk.W, label_text="Temp. R", value="30",
                                     validate={"validator": "real", "min": 30, "max": 60})
        self._tempG = Pmw.EntryField(master, labelpos=tk.W, label_text="Temp. G", value="30",
                                     validate={"validator": "real", "min": 30, "max": 60})
        self._tempB = Pmw.EntryField(master, labelpos=tk.W, label_text="Temp. B", value="30",
                                     validate={"validator": "real", "min": 30, "max": 60})
        self._tempWD = Pmw.EntryField(master, labelpos=tk.W, label_text="Temp. New W", value="30",
                                     validate={"validator": "real", "min": 30, "max": 60})

        self._gl_R = Pmw.EntryField(master, labelpos=tk.W, label_text="GL R", value="0",
                                       validate={"validator": "real", "min": 0, "max": 256})
        self._gl_G = Pmw.EntryField(master, labelpos=tk.W, label_text="GL G", value="0",
                                    validate={"validator": "real", "min": 0, "max": 256})
        self._gl_B = Pmw.EntryField(master, labelpos=tk.W, label_text="GL B", value="0",
                                    validate={"validator": "real", "min": 0, "max": 256})

        items = [self._boresight_x, self._boresight_y, self._boresight_r, self._w255_lv, self._w255_x, self._w255_y,
                 self._r255_lv, self._r255_x, self._r255_y, self._g255_lv, self._g255_x, self._g255_y,
                 self._b255_lv, self._b255_x, self._b255_y,
                 self._tempW, self._tempR, self._tempG, self._tempB, self._tempWD, self._gl_R, self._gl_G, self._gl_B]
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

            temps = [float(c.getvalue()) for c in [self._tempW, self._tempR, self._tempG, self._tempB, self._tempWD]]
            wd_gl = [float(c.getvalue()) for c in [self._gl_R, self._gl_G, self._gl_B]]

            self._value_dic = {
                'display_boresight_x': boresight_x, 'display_boresight_y': boresight_y,  'rotation': boresight_r,
                'lv_W255': w255[0], 'x_W255': w255[1], 'y_W255': w255[2],
                'lv_R255': r255[0], 'x_R255': r255[1], 'y_R255': r255[2],
                'lv_G255': g255[0], 'x_G255': g255[1], 'y_G255': g255[2],
                'lv_B255': b255[0], 'x_B255': b255[1], 'y_B255': b255[2],
                'TemperatureW': temps[0],
                'TemperatureR': temps[1],
                'TemperatureG': temps[2],
                'TemperatureB': temps[3],
                'TemperatureWD': temps[4],
                'WhitePointGLR':  wd_gl[0],
                'WhitePointGLG':  wd_gl[1],
                'WhitePointGLB':  wd_gl[2],
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
    # else:
    #     pprint.pprint(item)


class seacliffeepromError(Exception):
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
        self._fixture = test_fixture_eeprom.seacliffeepromFixture(station_config, operator_interface)
        self._equip = test_equipment_seacliff_eeprom.seacliffeepromEquipment(station_config, operator_interface)
        self._overall_errorcode = ''
        self._first_failed_test_result = None
        self._sw_version = '1.2.3'
        self._eep_assistant = EEPStationAssistant()
        self._max_retries = 5

    def initialize(self):
        if (self._station_config.DUT_SIM
                or self._station_config.EQUIPMENT_SIM
                or self._station_config.FIXTURE_SIM
                or self._station_config.NVM_WRITE_PROTECT
                or self._station_config.USER_INPUT_CALIB_DATA not in [0x02]
                or not self._station_config.CAMERA_VERIFY_ENABLE):
            self._operator_interface.operator_input('warn', 'Parameters should be configured correctly', 'warning')
            raise
        try:
            self._operator_interface.print_to_console(f'Initializing pancake EEPROM station...VER:{self._sw_version}\n')
            if self._station_config.AUTO_CFG_COMPORTS:
                self.auto_find_com_ports()

            msg = "find ports DUT = {0}. \n" \
                .format(self._station_config.DUT_COMPORT)
            self._operator_interface.print_to_console(msg)
            self._fixture.initialize()
            self._equip.initialize()

            if os.path.exists(self._station_config.CALIB_REQ_DATA_FILENAME):
                shutil.rmtree(self._station_config.CALIB_REQ_DATA_FILENAME)
        except:
            self._operator_interface.operator_input(None, 'Fail to initialize test_station. ', 'error')
            raise

    def close(self):
        self._operator_interface.print_to_console("Close...\n")
        self._operator_interface.print_to_console("there, I'm shutting the station down..\n")
        self._fixture.close()

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

        write_in_slow_mod = False
        if hasattr(self._station_config, 'NVM_WRITE_SLOW_MOD') and self._station_config.NVM_WRITE_SLOW_MOD:
            write_in_slow_mod = True
        calib_data = None  # self._station_config.CALIB_REQ_DATA
        var_check_data = None
        try:
            if self._station_config.USER_INPUT_CALIB_DATA == 0x01:
                dlg = EEPROMUserInputDialog(self._station_config, self._operator_interface,
                                            'EEPROM Parameter for SN:{0}'.format(serial_number))
                while dlg.is_looping:
                    self._operator_interface.wait(0.5, '')
                calib_data = dlg.current_cfg()
            elif self._station_config.USER_INPUT_CALIB_DATA == 0x02:
                calib_data = None
                calib_data_json_fn = os.path.join(self._station_config.CALIB_REQ_DATA_FILENAME,
                                                  f'eeprom_session_miz_{serial_number}.json')
                if os.path.exists(calib_data_json_fn):
                    with open(f'{calib_data_json_fn}', 'r') as json_file:
                        calib_data = json.load(json_file)
                        eep_keys = set(self._eep_assistant._eeprom_map_group.keys())
                        if not eep_keys.issubset(calib_data.keys()):
                            msg = f'unable to parse all the items from input items.\n'
                            self._operator_interface.print_to_console(f'{eep_keys}\n')
                            calib_data = None
                            self._operator_interface.operator_input(None, msg, msg_type='error')
        except Exception as e:
            calib_data = None
            pass

        if calib_data is None:
            self._operator_interface.operator_input(None, f'unable to get enough information for {serial_number}.\n')
            raise test_station.TestStationProcessControlError(f'unable to get enough information for DUT {serial_number}.')

        self._operator_interface.print_to_console("Start write data to DUT. %s\n" % the_unit.serial_number)
        test_log.set_measured_value_by_name_ex('SW_VERSION', self._sw_version)

        try:
            the_unit.initialize()
            recv_obj = the_unit.screen_on(ignore_err=True)
            if recv_obj is True or self._station_config.DUT_SIM:
                test_log.set_measured_value_by_name_ex('DUT_POWER_ON_INFO', 0)
                test_log.set_measured_value_by_name_ex('DUT_POWER_ON_RES', True)
            elif isinstance(recv_obj, list):
                test_log.set_measured_value_by_name_ex('DUT_POWER_ON_INFO', recv_obj[1])
                test_log.set_measured_value_by_name_ex('DUT_POWER_ON_RES', False)
                raise seacliffeepromError(f'Unable to power on DUT. {str(recv_obj)}')

            post_data_check = False
            self._operator_interface.print_to_console('Start to query holder position. ')
            retries_query = 1
            module_inplace = False
            if not hasattr(self._station_config, 'DUT_CHK_MODULE_INPLACE'):
                module_inplace = True
            else:
                module_inplace = not self._station_config.DUT_CHK_MODULE_INPLACE
            while not module_inplace and retries_query <= 10:
                self._operator_interface.print_to_console(f'Please push the holder into the carbinet. {retries_query}\n')
                rev_obj = the_unit.get_module_inplace()
                if rev_obj is not None:
                    module_inplace = int(rev_obj[1]) == 1
                if module_inplace:
                    continue
                time.sleep(1)
                retries_query += 1
            if not module_inplace:
                raise test_station.TestStationProcessControlError(f'Fail to check position for DUT {serial_number}.')

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

                    img_dir = os.path.join(self._station_config.ROOT_DIR, 'factory-test_debug', 'Imgs')
                    if not os.path.exists(img_dir):
                        hardware_station_common.utils.os_utils.mkdir_p(img_dir)
                        os.chmod(img_dir, 0o777)
                    img_fn = os.path.join(
                        img_dir, f"{serial_number}_{pattern}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.bmp")
                    percent = int(self._fixture.CheckImage(img_fn, chk_lsl, chk_usl) * 100)
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
            if not judge_by_camera:
                raise seacliffeepromError(f'Unable to determine the status. {judge_by_camera}')
            if write_in_slow_mod:
                the_unit.nvm_speed_mode(mode='low')
            self._operator_interface.print_to_console('read write count for nvram ...\n')
            write_status = the_unit.nvm_read_statistics()
            write_count = 0
            post_write_count = 0
            if self._station_config.DUT_SIM:
                write_status = [0, 1]
                post_write_count = 1
            if write_status is not None:
                write_count = int(write_status[1])
                post_write_count = write_count
                test_log.set_measured_value_by_name_ex('PRE_WRITE_COUNTS', write_count)

            if (0 <= write_count < self._station_config.NVM_WRITE_COUNT_MAX) and judge_by_camera:
                self._operator_interface.print_to_console('read all data from eeprom ...\n')

                var_data = dict(calib_data)  # type: dict

                raw_data = ['0x00'] * self._eep_assistant.nvm_data_len
                if not self._station_config.DUT_SIM:
                    try:
                        raw_data = the_unit.nvm_read_data(data_len=self._eep_assistant.nvm_data_len)[2:]
                    except Exception as e:
                        self._operator_interface.print_to_console(f'Fail to read initialized data, exp: {str(e)}')
                        raw_data = ['0x00'] * self._eep_assistant.nvm_data_len
                self._operator_interface.print_to_console('RD_DATA:\n')
                self._operator_interface.print_to_console(f"<-- {','.join(raw_data)}\n")

                raw_data_cpy = raw_data.copy()  # place holder for all the bytes.
                var_data = dict(calib_data)  # type: dict
                raw_data_cpy = self._eep_assistant.encode_parameter_items(raw_data_cpy, var_data=var_data)

                # TODO: config all the data to array.
                print('Write configuration...........\n')
                self._operator_interface.print_to_console(f"WR_DATA:  \n --> {','.join(raw_data_cpy)} \n")
                same_mem = [d1.upper() for d1 in raw_data] == [d2.upper() for d2 in raw_data_cpy]
                if not same_mem and not self._station_config.NVM_WRITE_PROTECT:
                    configuration_success_by_count = 1
                    while configuration_success_by_count <= 3 and post_write_count <= write_count:
                        self._operator_interface.print_to_console(
                            f'write configuration to eeprom ...{configuration_success_by_count} / 3\n')
                        max_tries = 2
                        write_tries = 1
                        nvm_write_data_success = False
                        while write_tries <= max_tries and not nvm_write_data_success:
                            self._operator_interface.print_to_console(f'try to nvm_write {write_tries} / {max_tries}\n')
                            try:
                                if self._station_config.NVM_EEC_READ:
                                    the_unit.nvm_get_ecc()
                                the_unit.nvm_write_data(raw_data_cpy)
                                if self._station_config.NVM_EEC_READ:
                                    the_unit.nvm_get_ecc()
                                nvm_write_data_success = True
                            except Exception as e:
                                self._operator_interface.print_to_console(f'msg for write data: {str(e)} \n')
                                if write_tries == max_tries:
                                    raise
                                else:
                                    try:
                                        the_unit.screen_off()
                                        the_unit.screen_on()
                                        if write_in_slow_mod:
                                            the_unit.nvm_speed_mode(mode='low')
                                        time.sleep(1)
                                    except:
                                        pass
                            write_tries += 1

                        self._operator_interface.print_to_console('screen off ...\n')
                        the_unit.screen_off()

                        # double check after flushing the NVRAM.
                        self._operator_interface.print_to_console('screen on ...\n')
                        the_unit.screen_on()
                        if write_in_slow_mod:
                            the_unit.nvm_speed_mode(mode='low')

                        self._operator_interface.print_to_console('read write count for nvram ...\n')
                        write_status = the_unit.nvm_read_statistics()
                        if write_status is not None:
                            post_write_count = int(write_status[1])
                        configuration_success_by_count += 1
                else:
                    post_data_check = True
                    var_check_data = raw_data.copy()
                    self._operator_interface.print_to_console(f'write configuration protected ...MemCmp: {same_mem}\n')
                    # time.sleep(self._station_config.DUT_NVRAM_WRITE_TIMEOUT)

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

                test_log.set_measured_value_by_name_ex('CFG_TemperatureW', var_data.get('TemperatureW'))
                test_log.set_measured_value_by_name_ex('CFG_TemperatureR', var_data.get('TemperatureR'))
                test_log.set_measured_value_by_name_ex('CFG_TemperatureG', var_data.get('TemperatureG'))
                test_log.set_measured_value_by_name_ex('CFG_TemperatureB', var_data.get('TemperatureB'))
                test_log.set_measured_value_by_name_ex('CFG_TemperatureWD', var_data.get('TemperatureWD'))

                test_log.set_measured_value_by_name_ex('CFG_WhitePointGLR', var_data.get('WhitePointGLR'))
                test_log.set_measured_value_by_name_ex('CFG_WhitePointGLG', var_data.get('WhitePointGLG'))
                test_log.set_measured_value_by_name_ex('CFG_WhitePointGLB', var_data.get('WhitePointGLB'))

                test_log.set_measured_value_by_name_ex('CFG_CS', raw_data_cpy[37])
                msg = '-'.join([f'{int(c1, 16):02X}' for c1 in raw_data_cpy[38:41]])
                test_log.set_measured_value_by_name_ex('CFG_VALIDATION_FIELD', msg)

                # self._operator_interface.print_to_console('screen off ...\n')
                # the_unit.screen_off()
                #
                # # double check after flushing the NVRAM.
                # self._operator_interface.print_to_console('screen on ...\n')
                # the_unit.screen_on()
                # if write_in_slow_mod:
                #     the_unit.nvm_speed_mode(mode='low')
                #
                # self._operator_interface.print_to_console('read write count for nvram ...\n')
                # write_status = the_unit.nvm_read_statistics()
                # if write_status is not None:
                #     post_write_count = int(write_status[1])
                test_log.set_measured_value_by_name_ex('POST_WRITE_COUNTS', post_write_count)
                test_log.set_measured_value_by_name_ex('WRITE_COUNTS_CHECK', post_write_count >= write_count)

                self._operator_interface.print_to_console('read configuration from eeprom ...\n')
                raw_data_cpy_cap = [c.upper() for c in raw_data_cpy]
                read_tries = 1
                data_from_nvram = None
                data_from_nvram_cap = None

                while read_tries <= self._max_retries and not post_data_check:
                    if not self._station_config.DUT_SIM:
                        try:
                            data_from_nvram = the_unit.nvm_read_data(data_len=self._nvm_data_len)[2:]
                            data_from_nvram_cap = [c.upper() for c in data_from_nvram]
                            if data_from_nvram_cap == raw_data_cpy_cap:
                                var_check_data = data_from_nvram_cap
                                post_data_check = True
                        except Exception as e2:
                            self._operator_interface.print_to_console(f'msg for read data: {str(e2)}\n')
                    dummy_msg = None
                    if isinstance(data_from_nvram, list):
                        dummy_msg = ','.join(data_from_nvram)
                    self._operator_interface.print_to_console(f"RD_DATA {read_tries}:  {dummy_msg}.\n")
                    read_tries += 1
                # save decoded data.
                if post_data_check and var_check_data:
                    var_check_data_json = self._eep_assistant.decode_raw_data(raw_data=var_check_data)
                    if not os.path.exists(self._station_config.RAW_IMAGE_LOG_DIR):
                        hardware_station_common.utils.os_utils.mkdir_p(self._station_config.RAW_IMAGE_LOG_DIR)
                    post_data_json_fn = os.path.join(self._station_config.RAW_IMAGE_LOG_DIR,
                                                     f'eeprom_session_miz_{serial_number}_confirm_data.json')
                    with open(os.path.join(post_data_json_fn), 'w') as post_json_file:
                        json.dump(var_check_data_json, post_json_file, indent=6)
                test_log.set_measured_value_by_name_ex('POST_DATA_CHECK', post_data_check)

                del data_from_nvram, raw_data_cpy, raw_data_cpy_cap, data_from_nvram_cap
            elif write_count >= self._station_config.NVM_WRITE_COUNT_MAX:
                self._operator_interface.print_to_console(
                    f'Exp: write times: {write_count} exceed max count: {self._station_config.NVM_WRITE_COUNT_MAX}\n')
            elif not judge_by_camera:
                self._operator_interface.print_to_console(f'fail to judge by Camera: {judge_by_camera}\n')

        except (seacliffeepromError, dut.DUTError, Exception) as e:
            self._operator_interface.print_to_console(f"Non-parametric Test Failure, {str(e)}\n")
        finally:
            try:
                the_unit.close()
            except:
                pass
        return self.close_test(test_log)

    def close_test(self, test_log):
        ### Insert code to gracefully restore fixture to known state, e.g. clear_all_relays() ###
        self._overall_result = test_log.get_overall_result()
        self._first_failed_test_result = test_log.get_first_failed_test_result()
        return self._overall_result, self._first_failed_test_result

    def is_ready(self):
        self._fixture.is_ready()

