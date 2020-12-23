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


def chk_and_set_measured_value_by_name(test_log, item, value):
    """

    :type test_log: test_station.TestRecord
    """
    if item in test_log.results_array():
        test_log.set_measured_value_by_name(item, value)
    else:
        pprint.pprint(item)


class seacliffmotStationError(Exception):
    pass


class seacliffmotStation(test_station.TestStation):

    _fixture: test_fixture_seacliff_mot.seacliffmotFixture

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
                                    retries = retries + 1
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
                    a_serial.close()

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
        self._sw_version = '0.7.0'
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
        except:
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

    def get_filenames_in_folder(self, parent_dir, pattern):
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

        self._query_dual_start()
        if self._the_unit is None:
            raise test_station.TestStationProcessControlError(f'Fail to query dual_start for DUT {serial_number}.')

        msg0 = 'info --> lit up: {0}, emulator_dut: {1}, emulator_equip: {2}, emulator_fixture: {3},' \
               ' particle:{4}, dut_checker:{5} ver: {6}\n' \
            .format(
                self._station_config.DUT_LITUP_OUTSIDE, self._station_config.DUT_SIM,
                self._station_config.EQUIPMENT_SIM, self._station_config.FIXTURE_SIM,
                self._station_config.FIXTURE_PARTICLE_COUNTER, self._station_config.DISP_CHECKER_ENABLE,
                self._sw_version)
        self._operator_interface.print_to_console(msg0)
        self._overall_result = False
        self._overall_errorcode = ''
        pattern_value = None
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
                os.chmod(capture_path, 777)
            config = dict(self._station_config.CAM_INIT_CONFIG)

            config["capturePath"] = capture_path
            config['cfgPath'] = os.path.join(self._station_config.CONOSCOPE_DLL_PATH, self._station_config.CFG_PATH)

            self._operator_interface.print_to_console("set current config = {0}\n".format(config))
            self._equipment.set_config(config)

            for pos_item in self._station_config.TEST_ITEM_POS:
                pos_name = pos_item['name']
                pos_val = pos_item['pos']
                item_patterns = pos_item.get('pattern')
                if item_patterns is None:
                    continue

                self._operator_interface.print_to_console('mov dut to pos = {0}\n'.format(pos_name))
                self._fixture.mov_abs_xy_wrt_alignment(pos_val[0], pos_val[1])
                self._fixture.mov_camera_z_wrt_alignment(pos_val[2])
                time.sleep(self._station_config.FIXTURE_MECH_STABLE_DLY)

                for pattern_name in item_patterns:
                    pattern_info = self.get_test_item_pattern(pattern_name)
                    if not pattern_info:
                        self._operator_interface.print_to_console(
                            'Unable to find information for pattern: %s \n' % pattern_name)
                        continue
                    self._operator_interface.print_to_console('test pattern name = {0}\n'.format(pattern_name))

                    # <editor-fold desc="Render images while not the same pattern.">
                    if pattern_value != pattern_info['pattern']:
                        pattern_value = pattern_info['pattern']
                        msg = 'try to render image  {0} -> {1} to {2} module.\n'\
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
                        if not pattern_value_valid:
                            self._operator_interface.print_to_console('Unable to change pattern: {0} = {1} \n'
                                                                      .format(pattern_name, pattern_value))
                            continue
                    # </editor-fold>

                    pre_file_name = '{0}_{1}_'.format(pos_name, pattern_name)
                    config = {'fileNamePrepend': pre_file_name}
                    self._operator_interface.print_to_console("set current config = {0}\n".format(config))
                    self._equipment.set_config(config)
                    pattern: dict
                    pattern = [c for c in self._station_config.TEST_ITEM_PATTERNS if c['name'] == pattern_name][-1]
                    exposure_cfg = pattern.get('exposure')  # type: (str, int)
                    file_count_per_capture = self._station_config.FILE_COUNT_INC

                    test_item_raw_files_pre = sum([len(files) for r, d, files in os.walk(capture_path)])
                    test_item_raw_files_post = test_item_raw_files_pre

                    if self._station_config.EQUIPMENT_SIM and not self._station_config.EQUIPMENT_SIM_CAPTURE_FROM_DIR:
                        self._operator_interface.print_to_console(
                            "Skip to Capture Bin File for color {0} in emulator mode\n".format(pattern_value))
                        test_item_raw_files_post += file_count_per_capture
                    else:
                        msg = '********* Eldim Capturing Bin File for color {0} ***************\n'.format(pattern_value)
                        self._operator_interface.print_to_console(msg)
                        self._equipment.do_measure_and_export(pos_name, pattern_name)
                        test_item_raw_files_post = sum([len(files) for r, d, files in os.walk(capture_path)])

                    measure_item_name = 'Test_RAW_IMAGE_SAVE_SUCCESS_{0}_{1}'.format(pos_name, pattern_name)
                    raw_success_save = (test_item_raw_files_pre + file_count_per_capture) == test_item_raw_files_post
                    self._operator_interface.print_to_console(
                        'file count detect {0} --> {1}. \n'.format(test_item_raw_files_pre, test_item_raw_files_post))
                    test_log.set_measured_value_by_name_ex(measure_item_name, raw_success_save)
                self._operator_interface.print_to_console('..........\n\n')

            self._operator_interface.print_to_console("all images captured, now start to analyze data. \n")
            self.data_export(serial_number, capture_path, test_log)
            self.distortion_centroid_parametric_export_ex(capture_path, test_log)
            self.color_pattern_parametric_export_ex(capture_path, test_log)

        except seacliffmotStationError as e:
            self._operator_interface.print_to_console(str(e))
        finally:
            try:
                self._the_unit.close()
                self._fixture.unload()
            except:
                self._the_unit = None
        return self.close_test(test_log)

    def close_test(self, test_log):
        ### Insert code to gracefully restore fixture to known state, e.g. clear_all_relays() ###
        self._overall_result = test_log.get_overall_result()
        self._first_failed_test_result = test_log.get_first_failed_test_result()
        return self._overall_result, self._first_failed_test_result

    def validate_sn(self, serial_num):
        self._latest_serial_number = serial_num
        return test_station.TestStation.validate_sn(self, serial_num)

    def get_free_space_mb(self, folder):
        import ctypes
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value / 1024 / 1024

    def is_ready(self):
        free_space = self.get_free_space_mb(self._station_config.ROOT_DIR)
        limit_free_space = 500
        if free_space < limit_free_space:
            msg = "Unable to start test (total size of free space {0:.1f} less than {1}M.\n"\
                .format(free_space, limit_free_space)
            self._operator_interface.operator_input('WARN', msg=msg, msg_type='warning')
            return False

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
        try:
            self._fixture.power_on_button_status(True)
            timeout_for_btn_idle = 10
            timeout_for_dual = timeout_for_btn_idle
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
                    self._module_left_or_right = 'L'
                    self._fixture._alignment_pos = (0, 0, 0, 0)
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
                        alignment_result = self._fixture.alignment(self._latest_serial_number)
                        if isinstance(alignment_result, tuple):
                            self._module_left_or_right = str(alignment_result[4]).upper()
                            self._is_alignment_success = True

                    elif ready_status == 0x03:
                        self._operator_interface.print_to_console('Try to lit up DUT.\n')
                        self._retries_screen_on += 1
                        self._probe_con_status = True
                        # TODO: set the probe statue true.
                        self._probe_con_status = self._fixture.query_probe_status() == 0
                        if not self._station_config.FIXTURE_SIM and not self._probe_con_status:
                            self._operator_interface.print_to_console('Please check the carrier connection.\n')
                            continue
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
                                self._fixture.start_button_status(True)
                        else:
                            self._fixture.power_on_button_status(True)
                            self._fixture.start_button_status(True)
                    elif ready_status == 0x02:
                        self._is_cancel_test_by_op = True  # Cancel test.
                time.sleep(0.1)
                timeout_for_dual -= 1
        except (seacliffmotStationError, DUTError, RuntimeError) as e:
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
                self._fixture.power_on_button_status(False)
            except Exception as e:
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
                file_x = self.get_filenames_in_folder(capture_path, r'{0}_.*_X_float\.bin'.format(pre_file_name))
                file_y = self.get_filenames_in_folder(capture_path, r'{0}_.*_Y_float\.bin'.format(pre_file_name))
                file_z = self.get_filenames_in_folder(capture_path, r'{0}_.*_Z_float\.bin'.format(pre_file_name))
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

                    self._operator_interface.print_to_console('start to export data for %s\n' % pre_file_name )
                    if self._station_config.AUTO_CVT_BGR_IMAGE_FROM_XYZ:
                        img_base_name = os.path.basename(file_x[0]).split('_X_float.bin')[0]
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
                self._operator_interface.print_to_console('parse data {0} finished.\n'.format(pre_file_name))
        del data_items_XYZ
        pass

    def distortion_centroid_parametric_export_ex(self, capture_path, test_log):
        export_items = ['DispCen_x_cono', 'DispCen_y_cono', 'DispCen_x_display',
                        'DispCen_y_display', 'Disp_Rotate_x', 'Disp_Rotate_y']
        for pos_item in self._station_config.TEST_ITEM_POS:
            pos_name = pos_item['name']
            item_patterns = pos_item.get('pattern')
            if item_patterns is None:
                continue
            analysis_patterns = [c for c in item_patterns if c in self._station_config.ANALYSIS_GRP_DISTORTION]
            for pattern_name in analysis_patterns:
                pattern_info = self.get_test_item_pattern(pattern_name)
                if not pattern_info:
                    continue

                pre_file_name = '{0}_{1}'.format(pos_name, pattern_name)
                file_x = self.get_filenames_in_folder(capture_path, r'{0}_.*_X_float\.bin'.format(pre_file_name))
                file_y = self.get_filenames_in_folder(capture_path, r'{0}_.*_Y_float\.bin'.format(pre_file_name))
                file_z = self.get_filenames_in_folder(capture_path, r'{0}_.*_Z_float\.bin'.format(pre_file_name))
                if len(file_x) != 0 and len(file_y) == len(file_x) and len(file_z) == len(file_x):
                    primary = ['X', 'Y', 'Z']
                    pri_items = dict(zip(primary, [file_x[0], file_y[0], file_z[0]]))
                    for pri_k, pri_v in pri_items.items():
                        try:
                            mot_alg = test_equipment_seacliff_mot.MotAlgorithmHelper()
                            self._operator_interface.print_to_console(
                                'start to export {0}, {1}-{2}\n'.format(pos_name, pattern_name, pri_k))
                            distortion_exports = mot_alg.distortion_centroid_parametric_export(pri_v)
                            for export_item in export_items:
                                export_value = distortion_exports.get(export_item)
                                if export_value is None:
                                    continue
                                measure_item_name = '{0}_{1}_{2}_{3}'.format(pos_name, pattern_name, pri_k, export_item)
                                test_log.set_measured_value_by_name_ex(measure_item_name, export_value)
                        except Exception as e:
                            self._operator_interface.print_to_console(
                                'Fail to export data for pattern: {0}_{1}\n'.format(pos_name, pattern_name))

    def color_pattern_parametric_export_ex(self, capture_path, test_log):
        export_items_type_a = ['Lum_Ratio>0.8MaxLum', 'Lum_Ratio>0.8OnAxisLum', 'Lum_SSR', 'Lum_delta', 'Lum_mean',
                               'u_mean', 'uv_delta<0.01_Ratio', 'uv_delta_to_OnAxis',
                               'v_mean']
        export_items_pattern_normal = ['Max Lum', "Max Lum u'", "Max Lum v'", "Max Lum x(deg)", 'Max Lum y(deg)']
        for pos_item in self._station_config.TEST_ITEM_POS:
            pos_name = pos_item['name']
            item_patterns = pos_item.get('pattern')
            if item_patterns is None:
                continue
            grp = set(self._station_config.ANALYSIS_GRP_COLOR_PATTERN + self._station_config.ANALYSIS_GRP_MONO_PATTERN)
            analysis_patterns = [c for c in item_patterns if c in grp]
            for pattern_name in analysis_patterns:
                pattern_info = self.get_test_item_pattern(pattern_name)
                if not pattern_info:
                    continue

                pre_file_name = '{0}_{1}'.format(pos_name, pattern_name)
                file_x = self.get_filenames_in_folder(capture_path, r'{0}_.*_X_float\.bin'.format(pre_file_name))
                file_y = self.get_filenames_in_folder(capture_path, r'{0}_.*_Y_float\.bin'.format(pre_file_name))
                file_z = self.get_filenames_in_folder(capture_path, r'{0}_.*_Z_float\.bin'.format(pre_file_name))
                if len(file_x) != 0 and len(file_y) == len(file_x) and len(file_z) == len(file_x):
                    try:
                        mot_alg = test_equipment_seacliff_mot.MotAlgorithmHelper()
                        self._operator_interface.print_to_console(
                            'start to export {0}, {1}\n'.format(pos_name, pattern_name))
                        color_exports = mot_alg.color_pattern_parametric_export(file_x[0],
                             brightness_statistics=(pattern_name in self._station_config.ANALYSIS_GRP_MONO_PATTERN),
                             color_uniformity=(pattern_name in self._station_config.ANALYSIS_GRP_COLOR_PATTERN))
                        lum_u_v_keys = ['Lum', 'u\'', 'v\'']
                        for pole, azi in self._station_config.DATA_AT_POLE_AZI:
                            keys = ['{0}(x={1}deg,y={2}deg)'.format(c, pole, azi) for c in lum_u_v_keys]
                            measure_items = ['{0}_{1}deg_{2}deg'.format(c, pole, azi) for c in lum_u_v_keys]
                            test_values = [color_exports.get(c) for c in keys]
                            for measure_item, test_value in zip(measure_items, test_values):
                                measure_item_name = '{0}_{1}_{2}'.format(pos_name, pattern_name, measure_item)
                                test_log.set_measured_value_by_name_ex(measure_item_name, test_value)

                        for deg in self._station_config.DATA_STATUS_DEGS:
                            measure_items = ['{0}_{1}deg'.format(c, deg) for c in export_items_type_a]
                            test_values = [color_exports.get(c) for c in measure_items]
                            for measure_item, test_value in zip(measure_items, test_values):
                                measure_item_name = '{0}_{1}_{2}'.format(pos_name, pattern_name, measure_item)
                                test_log.set_measured_value_by_name_ex(measure_item_name, test_value)

                        test_values = [color_exports.get(c) for c in measure_items]
                        measure_item_names = ['{0}_{1}_{2}'.format(pos_name, pattern_name, c.replace(' ', ''))
                                              for c in measure_items]
                        [test_log.set_measured_value_by_name_ex(measure_item_name, export_value)
                         for measure_item_name, export_value in zip(measure_item_names, test_values)]

                        for export_item, export_value in color_exports.items():
                            if export_item is None:
                                continue
                            export_item_without_blank = export_item.replace(' ', '_')
                            measure_item_name = '{0}_{1}_{2}'.format(pos_name, pattern_name, export_item_without_blank)
                            test_log.set_measured_value_by_name_ex(measure_item_name, export_value)

                    except Exception as e:
                        self._operator_interface.print_to_console(
                            'Fail to export data for pattern: {0}_{1}, {2}\n'.format(pos_name, pattern_name, e.args))
