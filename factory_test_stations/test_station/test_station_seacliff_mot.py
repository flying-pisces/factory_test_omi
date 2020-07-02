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

    def __init__(self, station_config, operator_interface):
        test_station.TestStation.__init__(self, station_config, operator_interface)
        self._fixture = None
        self._fixture = test_fixture_seacliff_mot.seacliffmotFixture(station_config, operator_interface)
        if hasattr(station_config, 'FIXTURE_SIM') and station_config.FIXTURE_SIM:
            self._fixture = projectstationFixture(station_config, operator_interface)
        self._equipment = test_equipment_seacliff_mot.seacliffmotEquipment(station_config, operator_interface)
        self._overall_errorcode = ''
        self._first_failed_test_result = None
        self._sw_version = '0.1.1'
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
        self._close_fixture()
        self._equipment.close()
        self._equipment.kill()

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
        return file_names

    def get_export_data(self, filename):
        """
        @type: filename: str
        """
        split_text = os.path.splitext(os.path.basename(filename))[0].split('_')
        data_bin = None
        if 'raw' in split_text:
            row = 6004
            col = 7920
            dtype = np.uint16
        elif 'proc' in split_text:
            row = 6001
            col = 6001
            dtype = np.int16
        elif 'float' in split_text:
            row = 6001
            col = 6001
            dtype = np.float32
        else:
            raise seacliffmotStationError('unsupported bin file. {0}'.format(filename))
        with open(filename, 'rb') as f:
            frame3 = np.frombuffer(f.read(), dtype=dtype)
            data_bin = frame3.reshape(row, col)
        return data_bin

    def _do_test(self, serial_number, test_log):
        """

        @type test_log: test_station.test_log.test_log
        """
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
            test_station.utils.os_utils.mkdir_p(capture_path)
            if not os.path.exists(capture_path):
                os.chmod(capture_path, 777)
            config = {"capturePath": capture_path,
                      "cfgPath": os.path.join(self._station_config.CONOSCOPE_DLL_PATH,
                                              self._station_config.CFG_PATH)}
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

    def is_ready(self):
        serial_number = self._latest_serial_number
        self._operator_interface.print_to_console("Testing Unit %s\n" % serial_number)
        self._the_unit = pancakeDut(serial_number, self._station_config, self._operator_interface)
        if hasattr(self._station_config, 'DUT_SIM') and self._station_config.DUT_SIM:
            self._the_unit = projectDut(serial_number, self._station_config, self._operator_interface)
        return self.is_ready_litup_outside()

    def is_ready_litup_outside(self):
        # TODO:  Initialized the DUT Simply
        ready = False
        power_on_trigger = False
        self._is_screen_on_by_op = False
        self._is_cancel_test_by_op = False
        self._probe_con_status = False
        self._retries_screen_on = 0
        self._module_left_or_right = None
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

                ready_status = self._fixture.is_ready()
                if ready_status is not None:
                    if ready_status == 0x00:  # load DUT automatically and then screen on
                        ready = True  # Start to test.
                        self._is_screen_on_by_op = True
                        if self._retries_screen_on == 0:
                            self._the_unit.screen_on()
                        self._the_unit.display_color((255, 0, 0))
                        self._fixture.power_on_button_status(False)
                        alignment_result = self._fixture.alignment()
                        if isinstance(alignment_result, tuple):
                            self._module_left_or_right = str(alignment_result[4]).upper()
                            self._is_alignment_success = True

                    elif ready_status == 0x03:
                        self._operator_interface.print_to_console('Try to lit up DUT.\n')
                        self._retries_screen_on += 1
                        self._probe_con_status = True
                        # TODO: set the probe statue true.
                        # self._fixture.query_probe_status() == 0
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
                self._fixture.start_button_status(False)
                self._fixture.power_on_button_status(False)
                if not ready:
                    if not self._is_cancel_test_by_op:
                        self._operator_interface.print_to_console(
                            'Unable to get start signal in %s from fixture.\n' % timeout_for_dual)
                    else:
                        self._operator_interface.print_to_console(
                            'Cancel start signal from dual %s.\n' % timeout_for_dual)
                    self._the_unit.close()
            except:
                pass
            self._operator_interface.prompt('', 'SystemButtonFace')

    def data_export(self, serial_number, capture_path,  test_log):
        """
        @param serial_number: str
        @param capture_path: str
        @param test_log: test_station.test_log.test_log
        @return:
        """
        data_items = {}
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
                if len(file_x) == 1 and len(file_y) == 1 and len(file_z) == 1:
                    group_data = [self.get_export_data(fn) for fn in (file_x[0], file_y[0], file_z[0])]
                    data_items[pre_file_name] = np.dstack(group_data)
        pass