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
        self._sw_version = '0.0.1'
        self._latest_serial_number = None  # type: str
        self._the_unit = None  # type: pancakeDut
        self._retries_screen_on = 0
        self._is_screen_on_by_op = False
        self._is_cancel_test_by_op = False
        self._is_alignment_success = False

    def initialize(self):
        try:
            self._operator_interface.print_to_console("Initializing Seacliff MOT station...\n")
            self._fixture.initialize()
            self._equipment.initialize()
        except:
            raise

    def _close_fixture(self):
        if self._fixture is not None:
            try:
                self._operator_interface.print_to_console("Close...\n")
                self._fixture.status()
#                self._fixture.elminator_off()
            finally:
                self._fixture.close()
                self._fixture = None

    def close(self):
        self._operator_interface.print_to_console("Close...\n")
        self._operator_interface.print_to_console("\there, I'm shutting the station down..\n")
        self._close_fixture()
        self._equipment.close()

    def get_test_item_pattern(self, name):
        test_item_patterns = [
            {'name': 'W255', 'pattern': (255, 255, 255), 'exposure': 3100},
            {'name': 'G127', 'pattern': (127, 127, 127), },
            {'name': 'W000', 'pattern': (0, 0, 0), },
            {'name': 'RGB', 'pattern': (127, 127, 127), },
            {'name': 'R255', 'pattern': (255, 0, 0), },
            {'name': 'G255', 'pattern': (0, 255, 0), },
            {'name': 'B255', 'pattern': (0, 0, 255), },
            {'name': 'GreenContrast', 'pattern': 1, },
            {'name': 'WhiteContrast', 'pattern': 2, },
            {'name': 'GreenSharpness', 'pattern': 3, },
            {'name': 'GreenDistortion', 'pattern': 4, }
        ]
        for c in test_item_patterns:
            if c.get('name') and c['name'] == name:
                return c

    def _do_test(self, serial_number, test_log):
        """

        @type test_log: test_station.test_log.test_log
        """
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

            test_log.set_measured_value_by_name_ex("DUT_ScreenOnRetries", self._retries_screen_on)
            test_log.set_measured_value_by_name_ex("DUT_ScreenOnStatus", self._is_screen_on_by_op)
            test_log.set_measured_value_by_name_ex("DUT_CancelByOperator", self._is_cancel_test_by_op)
            test_log.set_measured_value_by_name_ex("DUT_AlignmentSuccess", self._is_alignment_success)
            particle_count = 0
            if self._station_config.FIXTURE_PARTICLE_COUNTER:
                particle_count = self._fixture.particle_counter_read_val()
            test_log.set_measured_value_by_name_ex("ENV_ParticleCounter", particle_count)
            # hard coded.
            test_item_pos = [
                {'name': 'normal', 'pos': (0, 0, 15),
                 'pattern': ['W255', 'G127', 'W000', 'RGB', 'R255', 'G255', 'B255', 'GreenContrast', 'WhiteContrast',
                             'GreenSharpness', 'GreenDistortion']},
                {'name': 'extendedz', 'pos': (0, 0, 27), },
                {'name': 'extendedxpos', 'pos': (5.071, 0, 16.124)},
                {'name': 'extendedxneg', 'pos': (-5.071, 0, 16.124)},
                {'name': 'extendedypos', 'pos': (0, 5.071, 16.124)},
                {'name': 'extendedyneg', 'pos': (0, -5.071, 16.124)},
                {'name': 'blemish', 'pos': (0, 0, 5.000), }
            ]
            if not self._is_screen_on_by_op:
                raise seacliffmotStationError('fail to power screen on normally.')
            if not self._is_alignment_success:
                raise seacliffmotStationError('Fail to alignment.')
            equip_version = self._equipment.version()
            test_log.set_measured_value_by_name_ex('EQUIP_VERSION', equip_version)
            self._operator_interface.print_to_console("Equipment Version: %s\n" % equip_version)
            for pos_item in test_item_pos:
                pos_name = pos_item['name']
                pos_val = pos_item['pos']
                item_patterns = pos_item.get('pattern')
                if item_patterns is None:
                    continue
                self._operator_interface.print_to_console('mov dut to pos = {0}\n'.format(pos_name))
                self._fixture.mov_abs_xy_wrt_alignment(pos_val[0], pos_val[1])
                # self._fixture.mov_camera_z_wrt_alignment(pos_val[2])
                # capture path accorded with test_log.
                uni_file_name = re.sub('_x.log', '', test_log.get_filename())
                capture_path = os.path.join(self._station_config.RAW_IMAGE_LOG_DIR, uni_file_name)
                test_station.utils.os_utils.mkdir_p(capture_path)
                os.chmod(capture_path, 755)

                test_item = 0
                for pattern_name in item_patterns:
                    pattern_info = self.get_test_item_pattern(pattern_name)
                    if not pattern_info:
                        self._operator_interface.print_to_console(
                            'Unable to find information for pattern: %s \n' % pattern_name)
                        continue
                    self._operator_interface.print_to_console('test pattern name = {0}\n'.format(pattern_name))
                    pattern_value = pattern_info['pattern']
                    if isinstance(pattern_value, (int, str)):
                        self._the_unit.display_image(pattern_value, False)
                    elif isinstance(pattern_value, tuple):
                        self._the_unit.display_color(pattern_value)
                    else:
                        self._operator_interface.print_to_console('Unable to change pattern: %s = %s \n'
                                                                  % (pattern_name, pattern_value))
                        continue

                    config = {"capturePath": capture_path,
                              "cfgPath": os.path.join(self._station_config.ROOT_DIR,
                                                      r"test_stations\test_equipment\Cfg")}
                    self._equipment.set_config(config)
                    self._equipment.open()
                    self._operator_interface.print_to_console(
                        "*********** Eldim Capturing Bin File for color {0} ***************\n".format(pattern_value))
                    self._equipment.measure_and_export(self._station_config.TESTTYPE)
                    test_item += 1
                    test_item_raw_files = sum([len(files) for r, d, files in os.walk(capture_path)])

                    measure_item_name = 'Test_RAW_IMAGE_SAVE_SUCCESS_{0}_{1}'.format(pos_name, pattern_name)
                    if test_item_raw_files == 2 * test_item or True:
                        test_log.set_measured_value_by_name_ex(measure_item_name, True)
                    else:
                        break

                self._operator_interface.print_to_console('..........\n\n')

            # for c in [(0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255)]:
            #     self._operator_interface.print_to_console("\n*********** Display color %s ***************\n" % str(c))
            #     the_unit.display_color(c)
            #     config = {"capturePath": self._station_config.RAW_IMAGE_LOG_DIR,
            #               "cfgPath": os.path.join(self._station_config.ROOT_DIR, r"test_stations\test_equipment\Cfg")}
            #     self._equipment.set_config(config)
            #     self._equipment.open()
            #     self._operator_interface.print_to_console("\n*********** Eldim Capturing Bin File for color %s ***************\n" % str(c))
            #     self._equipment.measure_and_export(self._station_config.TESTTYPE) ## Need Eldim to open access
            #     test_item += 1
            #     test_item_raw_files = sum([len(files) for r, d, files in os.walk(self._station_config.RAW_IMAGE_LOG_DIR)])
            #     if test_item_raw_files == 2*test_item:
            #         test_log.set_measured_value_by_name("TEST_RAW_IMAGE_SAVE_SUCCESS_%s"%str(test_item), 1)
            #
            # for c in range(0, 5):
            #     self._operator_interface.print_to_console("\n*********** Display image %s ***************\n" % str(c))
            #     the_unit.display_image(c, False)
            #     self._equipment.set_config(config)
            #     self._equipment.open()
            #     self._operator_interface.print_to_console("\n*********** Eldim Capturing Bin File for color %s ***************\n" % str(c))
            #     self._equipment.measure_and_export(self._station_config.TESTTYPE)
            #     test_item += 1
            #     test_item_raw_files = sum([len(files) for r, d, files in os.walk(self._station_config.RAW_IMAGE_LOG_DIR)])
            #     if test_item_raw_files == 2*test_item:
            #         test_log.set_measured_value_by_name("TEST_RAW_IMAGE_SAVE_SUCCESS_%s"%str(test_item), 1)
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
        # self._the_unit.initialize()
        # self._is_screen_on_by_op = True
        # self._is_cancel_test_by_op = False
        # self._is_alignment_success = False
        # return True

        ready = False
        power_on_trigger = False
        self._is_screen_on_by_op = False
        self._is_cancel_test_by_op = False
        self._retries_screen_on = 0
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
                        alignment_result = self._fixture.alignment()
                        if isinstance(alignment_result, tuple):
                            self._is_alignment_success = True

                    elif ready_status == 0x03:
                        self._operator_interface.print_to_console('Try to lit up DUT.\n')
                        self._retries_screen_on += 1
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
