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
import Pmw


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
                                           validate={"validator": "real", "min": -127, "max": 127})
        self._boresight_y = Pmw.EntryField(master, labelpos=tk.W, label_text="boresight_y", value="0",
                                           validate={"validator": "real", "min": -127, "max": 127})
        self._boresight_r = Pmw.EntryField(master, labelpos=tk.W, label_text="rotation_r", value="0",
                                           validate={"validator": "real", "min": -1, "max": 1})

        self._w255_lv = Pmw.EntryField(master, labelpos=tk.W, label_text="W255_Lv", value="0",
                                           validate={"validator": "real", "min": 0, "max": 255})
        self._w255_x = Pmw.EntryField(master, labelpos=tk.W, label_text="W255_x", value="0",
                                           validate={"validator": "real", "min": 0, "max": 1})
        self._w255_y = Pmw.EntryField(master, labelpos=tk.W, label_text="W255_y", value="0",
                                           validate={"validator": "real", "min": 0, "max": 1})

        self._r255_lv = Pmw.EntryField(master, labelpos=tk.W, label_text="R255_Lv", value="0",
                                           validate={"validator": "real", "min": 0, "max": 255})
        self._r255_x = Pmw.EntryField(master, labelpos=tk.W, label_text="R255_x", value="0",
                                           validate={"validator": "real", "min": 0, "max": 1})
        self._r255_y = Pmw.EntryField(master, labelpos=tk.W, label_text="R255_y", value="0",
                                           validate={"validator": "real", "min": 0, "max": 1})

        self._g255_lv = Pmw.EntryField(master, labelpos=tk.W, label_text="G255_Lv", value="0",
                                           validate={"validator": "real", "min": 0, "max": 255})
        self._g255_x = Pmw.EntryField(master, labelpos=tk.W, label_text="G255_x", value="0",
                                           validate={"validator": "real", "min": 0, "max": 1})
        self._g255_y = Pmw.EntryField(master, labelpos=tk.W, label_text="G255_y", value="0",
                                           validate={"validator": "real", "min": 0, "max": 1})

        self._b255_lv = Pmw.EntryField(master, labelpos=tk.W, label_text="B255_Lv", value="0",
                                           validate={"validator": "real", "min": 0, "max": 255})
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
        return dict(self._value_dic)

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
        if (hasattr(self._station_config, 'IS_PRINT_TO_LOG')
                and self._station_config.IS_PRINT_TO_LOG):
            sys.stdout = self
            sys.stderr = self
            sys.stdin = None
        self._fixture = test_fixture.seacliffeepromFixture(station_config, operator_interface)
        self._equip = test_equipment.seacliffeepromEquipment(station_config, operator_interface)
        self._overall_errorcode = ''
        self._first_failed_test_result = None
        self._sw_version = '0.2.0'


    def initialize(self):
        try:
            self._operator_interface.print_to_console("Initializing pancake EEPROM station...\n")
            if self._station_config.AUTO_CFG_COMPORTS:
                self.auto_find_com_ports()

            msg = "find ports DUT = {0}. \n" \
                .format(self._station_config.DUT_COMPORT)
            self._operator_interface.print_to_console(msg)

            self._fixture.initialize()
            self._equip.initialize()
        except:
            raise

    def close(self):
        self._operator_interface.print_to_console("Close...\n")
        self._operator_interface.print_to_console("there, I'm shutting the station down..\n")
        self._fixture.close()

    # <editor-fold desc="Data Convert">

    def cvt_hex2_to_float_S8_7(self, array, pos_idx):
        arr = array[pos_idx:(pos_idx + 2)].copy()
        s = [int(c, 16) for c in arr]
        s0 = s[0]
        s1 = s[1]
        sign = 1
        if s0 & (1 << 7):
            sign = -1
        return sign * ((s0 & 0x7F) + s1 * 1 / (0x01 << 8))

    def cvt_hex1_to_decimal_S0_7(self, array, pos_idx):
        s = array[pos_idx:(pos_idx + 1)].copy()
        s0 = int(s[0], 16)
        sign = 1
        if s0 & (1 << 7):
            sign = -1
        return sign * ((s0 & 0x7F) * 1 / (0x01 << 7))

    def cvt_hex2_to_decimal_U0_13(self, array, pos_idx):
        arr = array[pos_idx:(pos_idx + 2)].copy()
        s = [int(c, 16) for c in arr]
        s0 = s[0]
        s1 = s[1]
        return ((s0 & 0x1F) * (0x01 << 8) + s1) / (1 << 13)

    def cvt_hex1_to_int_S7_0(self, array, pos_idx):
        s = array[pos_idx:(pos_idx + 1)].copy()
        s0 = int(s[0], 16)
        sign = 1
        if s0 & (1 << 7):
            sign = -1
        return sign * (s0 & 0x7F)

    def hex_ext(self, val):
        return '0x%02X'%val

    def cvt_float_to_hex2_S8_7(self, value):  # -10.5 --> 0x8A, 0x80
        """
        [-127.000 ~ 127.000]
        @type value: float
        """
        decimal, integral = math.modf(value)
        if value < 0:
            decimal = abs(decimal)
            integral = int(abs(integral)) | (1 << 7)
        s0 = self.hex_ext(int(integral))
        s1 = self.hex_ext(int(decimal * (1 << 8)))
        return [s0, s1]

    def cvt_decimal_to_hex1_S0_7(self, value):
        """
       [-1 ~ 1]
       @type value: float
       """
        decimal, integral = math.modf(value)
        sign_hex = 0x00
        if value < 0:
            decimal = abs(decimal)
            sign_hex = (1 << 7)
        s1 = self.hex_ext(int(decimal * (1 << 7)) | sign_hex)
        return [s1, ]

    def cvt_decimal_to_hex2_U0_13(self, value):
        """
        [0 ~ 1]
        @type value: unsign int
        """
        v = int(value * (1 << 13))
        s1 = self.hex_ext(v & 0xff)
        s0 = self.hex_ext(v >> 8 & 0x1f)
        return [s0, s1]

    def cvt_int_to_hex1_S7_0(self, value):
        """
        [-127 ~ 127]
        @type value: int
        @return:
        """
        sign_hex = 0x00
        integral = value
        if value < 0:
            integral = int(abs(value))
            sign_hex = (1 << 7)
        s1 = self.hex_ext(int(integral) | sign_hex)
        return [s1, ]
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

        self._operator_interface.print_to_console("Start write data to DUT. %s\n" % the_unit.serial_number)
        test_log.set_measured_value_by_name_ex('SW_VERSION', self._sw_version)
        try:
            calib_data = self._station_config.CALIB_REQ_DATA
            if self._station_config.USER_INPUT_CALIB_DATA:
                dlg = EEPROMUserInputDialog(self._station_config, self._operator_interface,
                                            'EEPROM Parameter for SN:{0}'.format(serial_number))
                while dlg.is_looping:
                    self._operator_interface.wait(0.5, None, False)
                calib_data = dlg.current_cfg()
            if calib_data is None:
                raise seacliffeepromError('unable to get enough parameters for {0}'.format(serial_number))

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

            if 0 <= write_count < self._station_config.NVM_WRITE_COUNT_MAX:
                # TODO: capture the image to determine the status of DUT.
                self._operator_interface.print_to_console('image capture and verification ...\n')
                judge_by_camera = False
                for idx, check_cfg in enumerate(self._station_config.CAMERA_CHECK_CFG):
                    pattern = check_cfg.get('pattern')
                    chk_lsl = check_cfg.get('chk_lsl')
                    chk_usl = check_cfg.get('chk_usl')
                    determine = check_cfg.get('determine')
                    self._operator_interface.print_to_console('check image with {0} ...\n'.format(pattern))
                    the_unit.display_color(pattern)
                    if not self._station_config.CAMERA_VERIFY_ENABLE:
                        continue
                    percent = int(self._fixture.CheckImage(pattern, chk_lsl, chk_usl) * 100)
                    self._operator_interface.print_to_console(
                        'check result with pattern: {0}:{1} ...{2}\n'.format(pattern, determine, percent))
                    if (determine is None) or (determine[0] <= percent <= determine[1]):
                        judge_by_camera = True
                    else:
                        judge_by_camera = False
                    if not judge_by_camera:
                        break
                if self._station_config.FIXTURE_SIM:
                    judge_by_camera = True
                test_log.set_measured_value_by_name_ex('JUDGED_BY_CAM', judge_by_camera)
                if judge_by_camera:
                    self._operator_interface.print_to_console('read all data from eeprom ...\n')

                    var_data = dict(calib_data)  # type: dict

                    raw_data = ['0x00'] * 45
                    if not self._station_config.DUT_SIM:
                        raw_data = the_unit.nvm_read_data()[2:]
                    # mark: convert raw data before flush to dict.
                    var_data['display_boresight_x'] = self.cvt_hex2_to_float_S8_7(raw_data, 0)
                    var_data['display_boresight_y'] = self.cvt_hex2_to_float_S8_7(raw_data, 2)
                    var_data['rotation'] = self.cvt_hex1_to_decimal_S0_7(raw_data, 4)

                    var_data['lv_W255'] = self.cvt_hex1_to_int_S7_0(raw_data, 5)
                    var_data['x_W255'] = self.cvt_hex2_to_decimal_U0_13(raw_data, 6)
                    var_data['y_W255'] = self.cvt_hex2_to_decimal_U0_13(raw_data, 8)

                    var_data['lv_R255'] = self.cvt_hex1_to_int_S7_0(raw_data, 10)
                    var_data['lv_G255'] = self.cvt_hex1_to_int_S7_0(raw_data, 11)
                    var_data['lv_B255'] = self.cvt_hex1_to_int_S7_0(raw_data, 12)

                    var_data['x_R255'] = self.cvt_hex2_to_decimal_U0_13(raw_data, 13)
                    var_data['y_R255'] = self.cvt_hex2_to_decimal_U0_13(raw_data, 15)

                    var_data['x_G255'] = self.cvt_hex2_to_decimal_U0_13(raw_data, 17)
                    var_data['y_G255'] = self.cvt_hex2_to_decimal_U0_13(raw_data, 19)

                    var_data['x_B255'] = self.cvt_hex2_to_decimal_U0_13(raw_data, 21)
                    var_data['y_B255'] = self.cvt_hex2_to_decimal_U0_13(raw_data, 23)

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

                    raw_data_cpy = raw_data.copy()  # place holder for all the bytes.
                    var_data = dict(calib_data)  # type: dict
                    raw_data_cpy[0:2] = self.cvt_float_to_hex2_S8_7(var_data['display_boresight_x'])
                    raw_data_cpy[2:4] = self.cvt_float_to_hex2_S8_7(var_data['display_boresight_y'])
                    raw_data_cpy[4:5] = self.cvt_decimal_to_hex1_S0_7(var_data['rotation'])
                    raw_data_cpy[5:6] = self.cvt_int_to_hex1_S7_0(var_data['lv_W255'])
                    raw_data_cpy[6:8] = self.cvt_decimal_to_hex2_U0_13(var_data['x_W255'])
                    raw_data_cpy[8:10] = self.cvt_decimal_to_hex2_U0_13(var_data['y_W255'])

                    raw_data_cpy[10:11] = self.cvt_int_to_hex1_S7_0(var_data['lv_R255'])
                    raw_data_cpy[11:12] = self.cvt_int_to_hex1_S7_0(var_data['lv_G255'])
                    raw_data_cpy[12:13] = self.cvt_int_to_hex1_S7_0(var_data['lv_B255'])

                    raw_data_cpy[13:15] = self.cvt_decimal_to_hex2_U0_13(var_data['x_R255'])
                    raw_data_cpy[15:17] = self.cvt_decimal_to_hex2_U0_13(var_data['y_R255'])

                    raw_data_cpy[17:19] = self.cvt_decimal_to_hex2_U0_13(var_data['x_G255'])
                    raw_data_cpy[19:21] = self.cvt_decimal_to_hex2_U0_13(var_data['y_G255'])

                    raw_data_cpy[21:23] = self.cvt_decimal_to_hex2_U0_13(var_data['x_B255'])
                    raw_data_cpy[23:25] = self.cvt_decimal_to_hex2_U0_13(var_data['y_B255'])

                    # TODO: config all the data to array.

                    print('Write configuration...........\n')
                    self._operator_interface.print_to_console('write configuration to eeprom ...\n')
                    if not self._station_config.NVM_WRITE_PROTECT:
                        the_unit.nvm_write_data(raw_data_cpy)
                    else:
                        self._operator_interface.print_to_console('write configuration protected ...\n')
                        print('WR_DATA:  \n' + ','.join(raw_data_cpy))
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

                    self._operator_interface.print_to_console('screen off ...\n')
                    the_unit.screen_off()

                    # TODO: it is able to do verification after flushing the NVRAM.
                    self._operator_interface.print_to_console('screen on ...\n')
                    the_unit.screen_on()
                    self._operator_interface.print_to_console('read configuration from eeprom ...\n')
                    data_from_nvram = raw_data_cpy.copy()
                    if not self._station_config.DUT_SIM:
                        data_from_nvram = the_unit.nvm_read_data()
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

            the_unit.close()
        except seacliffeepromError:
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
        self._fixture.is_ready()
