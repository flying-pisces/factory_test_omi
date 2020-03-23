import hardware_station_common.test_station.test_station as test_station
import test_station.test_fixture.test_fixture_pancake_offaxis as test_fixture_pancake_offaxis
import test_station.test_equipment.test_equipment_pancake_offaxis as test_equipment_pancake_offaxis
import test_station.dut as dut
import StringIO
import numpy as np
import os
import shutil
import time
import math
import datetime
import re
import filecmp
from verifiction.particle_counter import ParticleCounter
from verifiction.dut_checker import DutChecker
from dut.dut_offaxis import pancakeDutOffAxis
from dut.dut import projectDut
from test_fixture.test_fixture_project_station import projectstationFixture
import pprint
import types
import glob


class pancakeoffaxisError(Exception):
    pass

def chk_and_set_measured_value_by_name(test_log, item, value):
    """

    :type test_log: test_station.TestRecord
    """
    if item in test_log.results_array():
        test_log.set_measured_value_by_name(item, value)
    pass

class pancakeoffaxisStation(test_station.TestStation):
    """
        pancakeoffaxis Station
    """

    def __init__(self, station_config, operator_interface):
        self._sw_version = '1.0.2'
        self._runningCount = 0
        test_station.TestStation.__init__(self, station_config, operator_interface)
        self._fixture = test_fixture_pancake_offaxis.pancakeoffaxisFixture(station_config, operator_interface)
        if station_config.FIXTURE_SIM:
            self._fixture = projectstationFixture(station_config, operator_interface)
        self._equipment = test_equipment_pancake_offaxis.pancakeoffaxisEquipment(station_config)
        self._particle_counter = ParticleCounter(station_config)
        if self._station_config.FIXTURE_PARTICLE_COUNTER:
            self._particle_counter.initialize()
            if self._particle_counter.particle_counter_state() == 0:
                self._particle_counter.particle_counter_on()
                self._particle_counter_start_time = datetime.datetime.now()
        self._overall_errorcode = ''
        self._first_failed_test_result = None
        self._lastest_serial_number = None
        self._the_unit = None
        self._is_screen_on_by_op = False
        self._retries_screen_on = 0


    def initialize(self):
        self._operator_interface.print_to_console("Initializing station...\n")
        self._fixture.initialize()

        if self._station_config.FIXTURE_PARTICLE_COUNTER and hasattr(self, '_particle_counter_start_time'):
            while ((datetime.datetime.now() - self._particle_counter_start_time)
                   < datetime.timedelta(self._station_config.FIXTRUE_PARTICLE_START_DLY)):
                time.sleep(0.1)
                self._operator_interface.print_to_console('Waiting for initializing particle counter ...\n')

        self._operator_interface.print_to_console("Initialize Camera %s\n" %self._station_config.CAMERA_SN)
        self._equipment.initialize()

    def _close_fixture(self):
        if self._fixture is not None:
            try:
                self._operator_interface.print_to_console("Close...\n")
            finally:
                self._fixture.close()
                self._fixture = None

    def _close_particle_counter(self):
        if self._particle_counter is not None:
            try:
                pass
                # turn off the particle_counter manually.
                # self._particle_counter.particle_counter_off()
            finally:
                self._particle_counter.close()
                self._particle_counter = None

    def close(self):
        self._close_fixture()
        self._close_particle_counter()
        self._equipment.close()

    def _do_test(self, serial_number, test_log):
        # type: (str, test_station.test_log) -> tuple
        test_log.set_measured_value_by_name_ex = types.MethodType(chk_and_set_measured_value_by_name, test_log)
        self._overall_result = False
        self._overall_errorcode = ''
        # self._operator_interface.operator_input("Manually Loading", "Please Load %s for testing.\n" % serial_number)
        try:
            is_screen_on = False
            self._fixture.flush_data()
            self._operator_interface.print_to_console("Testing Unit %s\n" %serial_number)
            try:
                if not hasattr(self._station_config, 'DUT_LITUP_OUTSIDE') or not self._station_config.DUT_LITUP_OUTSIDE:
                    self._the_unit.initialize()
                    self._operator_interface.print_to_console("Initialize DUT... \n")
                    self._retries_screen_on = 0
                    while self._retries_screen_on < self._station_config.DUT_ON_MAXRETRY and not is_screen_on:
                        is_reboot_need = False
                        self._retries_screen_on += 1
                        try:
                            is_screen_on = self._the_unit.screen_on() or self._station_config.DUT_SIM
                        except dut.DUTError as e:
                            is_screen_on = False
                        else:
                            if self._station_config.DISP_CHECKER_ENABLE and is_screen_on:
                                self._the_unit.display_color(self._station_config.DISP_CHECKER_COLOR)
                                if self._retries_screen_on == 1:  # only move the axis in the first loop.
                                    pos = self._station_config.DISP_CHECKER_LOCATION
                                    self._fixture.mov_abs_xy(pos[0], pos[1])
                                color = self._the_unit.readColorSensor()
                                is_screen_on = self._the_unit.display_color_check(color)
                                if self._retries_screen_on % 3 == 0:  # reboot the driver board to avoid exp from driver board.
                                    is_reboot_need = True

                        if not is_screen_on:
                            msg = 'Retry power_on {}/{} times.\n'.format(self._retries_screen_on,
                                                                         self._station_config.DUT_ON_MAXRETRY)
                            self._operator_interface.print_to_console(msg)
                            self._the_unit.screen_off()
                            if is_reboot_need:
                                self._operator_interface.print_to_console("try to reboot the driver board... \n")
                                self._the_unit.reboot()
            finally:
                test_log.set_measured_value_by_name_ex('SW_VERSION', self._sw_version)
                test_log.set_measured_value_by_name_ex("DUT_ScreenOnRetries", self._retries_screen_on)
                test_log.set_measured_value_by_name_ex("DUT_ScreenOnStatus", self._is_screen_on_by_op or is_screen_on)

            if not is_screen_on and not self._retries_screen_on:  # dut can't be lit up
                raise pancakeoffaxisError("DUT Is unable to Power on.")

            test_log.set_measured_value_by_name_ex("MPK_API_Version", self._equipment.version())
            self._operator_interface.print_to_console("Read the particle count in the fixture... \n")
            particle_count = 0
            if self._station_config.FIXTURE_PARTICLE_COUNTER:
                particle_count = self._particle_counter.particle_counter_read_val()
            test_log.set_measured_value_by_name_ex("ENV_ParticleCounter", particle_count)

            self._operator_interface.print_to_console("Set Camera Database. %s\n" % self._station_config.CAMERA_SN)

            sequencePath = os.path.join(self._station_config.ROOT_DIR, self._station_config.SEQUENCE_RELATIVEPATH)
            self._equipment.set_sequence(sequencePath)
            if not self._station_config.USE_MULTI_DB:
                if not self._station_config.EQUIPMENT_SIM:
                    uni_file_name = re.sub('_x.log', '.ttxm', test_log.get_filename())
                    bak_dir = os.path.join(self._station_config.ROOT_DIR, self._station_config.ANALYSIS_RELATIVEPATH)
                    databaseFileName = os.path.join(bak_dir, uni_file_name)
                    self._equipment.create_database(databaseFileName)
                else:
                    db_dir = self._station_config.EQUIPMENT_DEMO_DATABASE
                    fns = glob.glob1(db_dir, '%s_*.ttxm' % (serial_number))
                    if len(fns) > 0:
                        databaseFileName = os.path.join(db_dir, fns[0])
                        self._operator_interface.print_to_console("Set tt_database {}.\n".format(databaseFileName))
                        self._equipment.set_database(databaseFileName)
                    else:
                        raise pancakeoffaxisError('unable to find ttxm for SN: %s' % (serial_number))

            self._operator_interface.print_to_console("Close the eliminator in the fixture... \n")

            self.offaxis_test_do(serial_number, test_log, self._the_unit)

        except Exception, e:
            self._operator_interface.print_to_console("Test exception {}.\n".format(e.message))
        finally:
            self._operator_interface.print_to_console('release current test resource.\n')
            if self._the_unit is not None:
                self._the_unit.close()
            if self._fixture is not None:
                self._fixture.unload()
                self._fixture.button_disable()
            self._operator_interface.print_to_console('close the test_log for {}.\n'.format(serial_number))
            overall_result, first_failed_test_result = self.close_test(test_log)

            self._runningCount += 1
            self._operator_interface.print_to_console('--- do test finished ---\n')
            return overall_result, first_failed_test_result


    def close_test(self, test_log):
        ### Insert code to gracefully restore fixture to known state, e.g. clear_all_relays() ###
        self._overall_result = test_log.get_overall_result()
        self._first_failed_test_result = test_log.get_first_failed_test_result()
        return self._overall_result, self._first_failed_test_result

    def validate_sn(self, serial_num):
        self._lastest_serial_number = serial_num
        return test_station.TestStation.validate_sn(self, serial_num)

    def is_ready(self):
        serial_number = self._lastest_serial_number
        self._operator_interface.print_to_console("Testing Unit %s\n" % serial_number)
        self._the_unit = dut.pancakeDut(serial_number, self._station_config, self._operator_interface)
        if self._station_config.DUT_SIM:
            self._the_unit = dut.projectDut(serial_number, self._station_config, self._operator_interface)
        if not hasattr(self._station_config, 'DUT_LITUP_OUTSIDE') or not self._station_config.DUT_LITUP_OUTSIDE:
            return self.is_ready_litup_inside()
        else:
            return self.is_ready_litup_outside()

    def is_ready_litup_outside(self):
        ready = False
        cancel = False
        power_on_trigger = False
        self._is_screen_on_by_op = False
        self._retries_screen_on = 0
        try:
            self._fixture.button_enable()
            timeout_for_btn_idle = 20
            timeout_for_dual = timeout_for_btn_idle
            self._the_unit.initialize()
            self._operator_interface.print_to_console("Initialize DUT... \n")
            while timeout_for_dual > 0:
                if ready or cancel:
                    break
                msg_prompt = 'Load DUT, and then Press L-Btn(Cancel)/R-Btn(Litup) in %s S...'
                if power_on_trigger:
                    msg_prompt = 'Press Dual-Btn(Load)/L-Btn(Cancel)/R-Btn(Re Litup)  in %s S...'
                self._operator_interface.prompt(msg_prompt % timeout_for_dual, 'yellow');
                if self._station_config.FIXTURE_SIM:
                    self._is_screen_on_by_op = True
                    ready = True
                ready_status = self._fixture.is_ready()
                if ready_status is not None:
                    if ready_status == 0x00:
                        if not power_on_trigger:
                            self._operator_interface.print_to_console(
                                'Press L-Btn(Cancel)/R-Btn(Litup) to lit up firstly.\n')
                        else:
                            ready = True  # Start to test.
                            self._is_screen_on_by_op = True
                    elif ready_status == 0x01:
                        self._operator_interface.print_to_console('Try to litup DUT.\n')
                        self._retries_screen_on += 1
                        if not power_on_trigger:
                            self._the_unit.screen_on()
                            # self._the_unit.display_image(self._station_config.DISP_CHECKER_IMG_INDEX)
                            power_on_trigger = True
                            timeout_for_dual = timeout_for_btn_idle
                        else:
                            self._the_unit.screen_off()
                            self._the_unit.reboot()  # Reboot
                            self._the_unit.screen_on()
                            # self._the_unit.display_image(self._station_config.DISP_CHECKER_IMG_INDEX)
                            power_on_trigger = True
                            timeout_for_dual = timeout_for_btn_idle
                    elif ready_status == 0x02:
                        cancel = True  # Cancel test.
                time.sleep(0.1)
                timeout_for_dual -= 1
            if not ready:
                if not cancel:
                    self._operator_interface.print_to_console(
                        'Unable to get start signal in %s from fixture.\n' % timeout_for_dual)
                else:
                    self._operator_interface.print_to_console(
                        'Cancel start signal from dual %s.\n' % timeout_for_dual)
                self._the_unit.close()
                self._the_unit = None
                raise test_station.TestStationSerialNumberError('Fail to Wait for press dual-btn ...')
        finally:
            try:
                self._fixture.button_disable()
            except:
                pass
            self._operator_interface.prompt('', 'SystemButtonFace')

    def is_ready_litup_inside(self):
        ready = False
        try:
            self._fixture.button_enable()
            timeout_for_dual = 20
            for idx in range(timeout_for_dual, 0, -1):
                self._operator_interface.prompt('Press the Dual-Start Btn in %s S...'%idx, 'yellow');
                if self._fixture.is_ready() or self._station_config.FIXTURE_SIM:
                    ready = True
                    break
                time.sleep(1)
            if not ready:
                self._operator_interface.print_to_console('Unable to get start signal in %s from fixture.\n'%timeout_for_dual)
                raise test_station.TestStationSerialNumberError('Fail to Wait for press dual-btn ...')
        finally:
            try:
                self._fixture.button_disable()
            except:
                pass
            self._operator_interface.prompt('', 'SystemButtonFace')

    def data_export(self, serial_number, test_log, tposIdx):
        """
        export csv and png from ttxm database
        :type test_log: test_station.TestRecord
        :type serial_number: str
        """
        pos_patterns = None
        for posIdx, pos, pos_patterns in self._station_config.POSITIONS:
            if posIdx != tposIdx:
                continue

            for test_pattern in pos_patterns:
                i = self._station_config.PATTERNS.index(test_pattern)
                if i < 0:
                    continue
                self._operator_interface.print_to_console(
                    "Panel export for Pattern: %s\n" % self._station_config.PATTERNS[i])
                if self._station_config.IS_EXPORT_CSV or self._station_config.IS_EXPORT_PNG:
                    output_dir = os.path.join(self._station_config.ROOT_DIR, self._station_config.ANALYSIS_RELATIVEPATH,
                                              serial_number + '_' + test_log._start_time.strftime(
                                                  "%Y%m%d-%H%M%S"))
                    if not os.path.exists(output_dir):
                        os.mkdir(output_dir, 777)
                    meas_list = self._equipment.get_measurement_list()
                    exp_base_file_name = re.sub('_x.log', '', test_log.get_filename())
                    measurement = self._station_config.MEASUREMENTS[i]
                    if not self._station_config.USE_MULTI_DB :
                        measurement = '{}_{}'.format(measurement, posIdx)
                    for meas in meas_list:
                        if meas['Measurement Setup'] != measurement:
                            continue

                        id = meas['Measurement ID']
                        export_csv_name = "{}_{}_{}.csv".format(serial_number, test_pattern, posIdx)
                        export_png_name = "{}_{}_{}.png".format(serial_number, test_pattern, posIdx)
                        if self._station_config.IS_EXPORT_CSV:
                            self._equipment.export_measurement(id, output_dir, export_csv_name,
                                                               self._station_config.Resolution_Bin_X,
                                                               self._station_config.Resolution_Bin_Y)
                        if self._station_config.IS_EXPORT_PNG:
                            self._equipment.export_measurement(id, output_dir, export_png_name,
                                                               self._station_config.Resolution_Bin_X,
                                                               self._station_config.Resolution_Bin_Y)
                        self._operator_interface.print_to_console("Export data for %s\n" % test_pattern)

    def offaxis_test_do(self, serial_number, test_log, the_unit):
        pos_items = self._station_config.POSITIONS
        pre_color = None
        for posIdx, pos, pos_patterns in pos_items:
            self._operator_interface.print_to_console('clear registration\n')
            self._equipment.clear_registration()
            if self._station_config.USE_MULTI_DB:
                if not self._station_config.EQUIPMENT_SIM:
                    uni_file_name = re.sub('_x.log', '_{}.ttxm'.format(posIdx), test_log.get_filename())
                    bak_dir = os.path.join(self._station_config.ROOT_DIR, self._station_config.ANALYSIS_RELATIVEPATH)
                    databaseFileName = os.path.join(bak_dir, uni_file_name)
                    self._equipment.create_database(databaseFileName)
                else:
                    db_dir = self._station_config.EQUIPMENT_DEMO_DATABASE
                    fns = glob.glob1(db_dir, '%s_*_%s.ttxm'%(serial_number, posIdx))
                    if len(fns) > 0:
                        databaseFileName = os.path.join(db_dir, fns[0])
                        self._operator_interface.print_to_console("Set tt_database {}.\n".format(databaseFileName))
                        self._equipment.set_database(databaseFileName)

            self._operator_interface.print_to_console("Panel Mov To Pos: {}.\n".format(pos))
            self._fixture.mov_abs_xy(pos[0], pos[1])

            center_item = self._station_config.CENTER_AT_POLE_AZI
            lv_cr_items = {}

            for test_pattern in pos_patterns:
                if test_pattern not in pos_patterns:
                    self._operator_interface.print_to_console("Can't find pattern {} for position {}.\n"
                                                              .format(test_pattern, posIdx))
                    continue
                i = self._station_config.PATTERNS.index(test_pattern)

                pattern = self._station_config.PATTERNS[i]
                analysis = self._station_config.ANALYSIS[i]
                if not self._station_config.USE_MULTI_DB:
                    analysis = '{}_{}'.format(analysis, posIdx)
                self._operator_interface.print_to_console(
                    "Panel Measurement Pattern: %s , Position Id %s.\n" % (pattern, posIdx))
                # the_unit.display_color(self._station_config.COLORS[i])
                if pre_color != self._station_config.COLORS[i]:
                    if isinstance(self._station_config.COLORS[i], tuple):
                        the_unit.display_color(self._station_config.COLORS[i])
                    elif isinstance(self._station_config.COLORS[i], (str, int)):
                        the_unit.display_image(self._station_config.COLORS[i])
                    pre_color = self._station_config.COLORS[i]
                    self._operator_interface.print_to_console('Set DUT To Color: {}.\n'.format(pre_color))
                use_camera = not self._station_config.EQUIPMENT_SIM
                if not use_camera:
                    self._equipment.clear_registration()
                analysis_result = self._equipment.sequence_run_step(analysis, '', use_camera, self._station_config.IS_SAVEDB)
                self._operator_interface.print_to_console("Sequence run step  {}.\n".format(analysis))

                lv_dic = {}
                cx_dic = {}
                cy_dic = {}
                center_dic = {}
                u_dic = {}
                v_dic = {}
                duv_dic = {}
                u_values = None
                u_values = None

                # region extract raw data

                for c, result in analysis_result.items():
                    if c != analysis:
                        continue
                    for ra in result:
                        r = re.sub(' ', '', ra)
                        raw_test_item = (pattern + "_" + r)
                        test_item = re.sub(r'\((Lv|Luminance)\)', '_Lv', raw_test_item)
                        test_item = re.sub(r'\s|%', '', test_item)

                        lv_match = re.search(r'(P_\d+_\d+)\((lv|Luminance)\)', r, re.I | re.S)
                        if lv_match:
                            lv_dic[lv_match.groups()[0]] = float(result[ra])
                        cx_match = re.search(r'(P_\d+_\d+)\(cx\)', r, re.I|re.S)
                        if cx_match:
                            cx_dic[cx_match.groups()[0]] = float(result[ra])
                        cy_match = re.search(r'(P_\d+_\d+)\(cy\)', r, re.I|re.S)
                        if cy_match:
                            cy_dic[cy_match.groups()[0]] = float(result[ra])

                        u_match = re.search(r'u\'Values', r, re.I | re.S)
                        if u_match:
                            u_values = result[ra]
                        v_match = re.search(r'v\'Values', r, re.I | re.S)
                        if v_match:
                            v_values = result[ra]

                        center_match = re.search(r'(CenterLv|CenterCx|CenterCy)', r)
                        if center_match:
                            center_dic[center_match.groups()[0]] = float(result[ra])
                        if test_item in test_log.results_array():
                            test_log.set_measured_value_by_name(test_item, float(result[ra]))

                    keys = lv_dic.keys()
                    us = []
                    vs = []
                    us_dic = {}
                    vs_dic = {}
                    for key in keys:
                        cx = cx_dic[key]
                        cy = cy_dic[key]
                        u = 4 * cx / (-2 * cx + 12 * cy + 3)
                        v = 9 * cy / (-2 * cx + 12 * cy + 3)
                        us.append(u)
                        vs.append(v)
                    us_dic = dict(zip(keys, us))
                    vs_dic = dict(zip(keys, vs))
                    us0 = us_dic[center_item]
                    vs0 = vs_dic[center_item]
                    duvs = np.sqrt((np.array(us) - us0)**2 + (np.array(vs) - vs0)**2)
                    duv_dic = dict(zip(keys, duvs))

                # endregion

                # region Normal Test Item.

                # Brightness at 30deg polar angle (nits)
                brightness_items = []
                for item in self._station_config.BRIGHTNESS_AT_POLE_AZI:
                    tlv = lv_dic['P_%d_%d' % item]
                    brightness_items.append(tlv)
                    test_item = '{}_{}_Lv_{}_{}'.format(posIdx, pattern, *item)
                    test_log.set_measured_value_by_name_ex(test_item, tlv)

                for p0, p180 in self._station_config.BRIGHTNESS_AT_POLE_ASSEM:
                    lv_x_0 = lv_dic['P_%d_%d' % p0]
                    lv_x_180 = lv_dic['P_%d_%d' % p180]
                    lv_0_0 = lv_dic[center_item]
                    assem = (lv_x_0 - lv_x_180)/lv_0_0
                    test_item = '{}_{}_ASYM_{}_{}_{}_{}'.format(posIdx, pattern, *(p0+p180))
                    test_log.set_measured_value_by_name_ex(test_item, '{0:.4}'.format(assem))

                # Brightness % @30deg wrt on axis brightness
                brightness_items = []
                for item in self._station_config.BRIGHTNESS_AT_POLE_AZI_PER:
                    tlv = lv_dic['P_%d_%d' % item] / lv_dic[center_item]
                    brightness_items.append(tlv)
                    test_item = '{}_{}_Lv_Proportion_{}_{}'.format(posIdx, pattern, *item)
                    test_log.set_measured_value_by_name_ex(test_item, tlv)

                for item in self._station_config.COLORSHIFT_AT_POLE_AZI:
                    duv = duv_dic['P_%d_%d' % item]
                    test_item = '{}_{}_duv_{}_{}'.format(posIdx, pattern, *item)
                    test_log.set_measured_value_by_name_ex(test_item, duv)

                # Max brightness location
                max_loc = max(lv_dic, key=lv_dic.get)
                test_item = '{}_{}_Lv_max_pos'.format(posIdx, pattern)
                test_log.set_measured_value_by_name_ex(test_item, max_loc)
                inclination, azimuth = tuple(re.split('_', max_loc)[1:])
                test_item = '{}_{}_Lv_max_pos_theta'.format(posIdx, pattern)
                test_log.set_measured_value_by_name_ex(test_item, int(inclination))
                test_item = '{}_{}_Lv_max_pos_phi'.format(posIdx, pattern)
                test_log.set_measured_value_by_name_ex(test_item, int(azimuth))
                # endregion

                if pattern in self._station_config.CR_TEST_PATTERNS:
                    lv_cr_items[pattern] = lv_dic

            # region Constract Test Item

            if len(lv_cr_items) == len(self._station_config.CR_TEST_PATTERNS) == 2:
                # CR at 0deg and 30deg polar angle
                w = self._station_config.CR_TEST_PATTERNS[0]
                d = self._station_config.CR_TEST_PATTERNS[1]

                for item in self._station_config.CR_AT_POLE_AZI:
                    item_key = 'P_%d_%d' % item
                    cr = lv_cr_items[w][item_key] / lv_cr_items[d][item_key]
                    test_item = '{}_CR_{}_{}'.format(posIdx, *item)
                    test_log.set_measured_value_by_name_ex(test_item, cr)
            # endregion

            self.data_export(serial_number, test_log, posIdx)

        self._operator_interface.print_to_console('complete the off_axis test items.\n')
