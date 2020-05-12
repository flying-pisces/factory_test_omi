import hardware_station_common.test_station.test_station as test_station
import test_station.test_fixture.test_fixture_pancake_uniformity as test_fixture_pancake_uniformity
import test_station.test_equipment.test_equipment_pancake_uniformity as test_equipment_pancake_uniformity
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
from factory_test_stations.test_station.test_fixture.test_fixture_project_station import projectstationFixture
from factory_test_stations.test_station.dut.dut import projectDut
import types
from itertools import islice
import cv2
import glob

class pancakeuniformityError(Exception):
    pass

def chk_and_set_measured_value_by_name(test_log, item, value):
    """

    :type test_log: test_station.TestRecord
    """
    if item in test_log.results_array():
        test_log.set_measured_value_by_name(item, value)

class pancakeuniformityStation(test_station.TestStation):
    """
        pancakeuniformity Station
    """

    def __init__(self, station_config, operator_interface):
        self._sw_version = '1.0.3'
        self._runningCount = 0
        test_station.TestStation.__init__(self, station_config, operator_interface)
        self._fixture = test_fixture_pancake_uniformity.pancakeuniformityFixture(station_config, operator_interface)
        if station_config.FIXTURE_SIM:
            self._fixture = projectstationFixture(station_config, operator_interface)
        self._equipment = test_equipment_pancake_uniformity.pancakeuniformityEquipment(station_config)
        if self._station_config.FIXTURE_PARTICLE_COUNTER:
            if self._fixture.particle_counter_state() == 0:
                self._fixture.particle_counter_on()
                self._particle_counter_start_time = datetime.datetime.now()
        self._overall_errorcode = ''
        self._first_failed_test_result = None
        self._lastest_serial_number = None
        self._the_unit = None
        self._is_screen_on_by_op = False
        self._retries_screen_on = 0
        self._is_cancel_test_by_op = False

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

    def close(self):
        if self._fixture is not None:
            self._fixture.close()
            self._fixture = None
        self._equipment.close()
        self._equipment = None

    def _do_test(self, serial_number, test_log):
        # type: (str, test_station.test_log) -> tuple
        self._overall_result = False
        self._overall_errorcode = ''
#        self._operator_interface.operator_input("Manually Loading", "Please Load %s for testing.\n" % serial_number)
        try:
            test_log.set_measured_value_by_name_ex = types.MethodType(chk_and_set_measured_value_by_name, test_log)
            test_log.set_measured_value_by_name_ex('SW_VERSION', self._sw_version)
            test_log.set_measured_value_by_name_ex("DUT_ScreenOnRetries", self._retries_screen_on)
            test_log.set_measured_value_by_name_ex("DUT_ScreenOnStatus", self._is_screen_on_by_op)

            if not self._is_screen_on_by_op:
                raise pancakeuniformityError("DUT Is unable to Power on.")

            test_log.set_measured_value_by_name_ex("MPK_API_Version", self._equipment.version())

            self._operator_interface.print_to_console("Initialize DUT... \n")
            #retries = 0
            #is_screen_on = False
            #try:
            #     if self._station_config.DISP_CHECKER_ENABLE:
            #         self._dut_checker.initialize()
            #         time.sleep(self._station_config.DISP_CHECKER_DLY)
            #
            #     while retries < self._station_config.DUT_ON_MAXRETRY and not is_screen_on:
            #         is_reboot_need = False
            #         retries += 1
            #         try:
            #             is_screen_on = self._the_unit.screen_on() or self._station_config.DUT_SIM
            #         except dut.DUTError as e:
            #             is_screen_on = False
            #         else:
            #             if self._station_config.DISP_CHECKER_ENABLE and is_screen_on:
            #                 self._the_unit.display_image(self._station_config.DISP_CHECKER_IMG_INDEX)
            #                 score = self._dut_checker.do_checker()
            #                 self._operator_interface.print_to_console(
            #                         "dut checker using blob detection. {} \n".format(score))
            #                 is_screen_on = False
            #                 if score is not None:
            #                     arr = np.array(score)
            #                     score_num = np.where((arr >= self._station_config.DISP_CHECKER_L_SCORE)
            #                              & (arr <= self._station_config.DISP_CHECKER_H_SCORE))
            #                     if np.max(arr) < self._station_config.DISP_CHECKER_EXL_SCORE:
            #                         is_screen_on = len(score_num[0]) == self._station_config.DISP_CHECKER_COUNT
            #                     else:
            #                         is_reboot_need = True
            #
            #         if not is_screen_on:
            #             msg = 'Retry power_on {}/{} times.\n'.format(retries,
            #                                                          self._station_config.DUT_ON_MAXRETRY)
            #             self._operator_interface.print_to_console(msg)
            #             self._the_unit.screen_off()
            #             if is_reboot_need:
            #                 self._operator_interface.print_to_console("try to reboot the driver board... \n")
            #                 self._the_unit.reboot()
            #
            #         if self._station_config.DISP_CHECKER_IMG_SAVED:
            #             fn0 = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
            #             fn = '{0}_{1}_{2}.jpg'.format(serial_number, retries, fn0)
            #             self._dut_checker.save_log_img(fn)
            # finally:
            #     self._dut_checker.close()
            #     test_log.set_measured_value_by_name_ex("DUT_ScreenOnRetries", retries)
            #     test_log.set_measured_value_by_name_ex("DUT_ScreenOnStatus", is_screen_on)
            #
            # if not is_screen_on:
            #     raise pancakeuniformityError("DUT Is unable to Power on.")

            self._fixture.elminator_on()
            self._fixture.load()
            self._operator_interface.print_to_console("Read the particle count in the fixture... \n")
            particle_count = 0
            if self._station_config.FIXTURE_PARTICLE_COUNTER:
                particle_count = self._fixture.particle_counter_read_val()
            test_log.set_measured_value_by_name_ex("ENV_ParticleCounter", particle_count)

            self._operator_interface.print_to_console("Set Camera Database. %s\n" % self._station_config.CAMERA_SN)

            uni_file_name = re.sub('_x.log', '.ttxm', test_log.get_filename())
            bak_dir = os.path.join(self._station_config.ROOT_DIR, self._station_config.ANALYSIS_RELATIVEPATH)

            sequencePath = os.path.join(self._station_config.ROOT_DIR, self._station_config.SEQUENCE_RELATIVEPATH)
            if not self._station_config.EQUIPMENT_SIM:
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
                    raise pancakeuniformityError('unable to find ttxm for SN: {}.\n'.format(serial_number))
            self._equipment.set_sequence(sequencePath)

            self._operator_interface.print_to_console('clear registration\n')
            self._equipment.clear_registration()

            self._operator_interface.print_to_console("Close the eliminator in the fixture... \n")
            self._fixture.elminator_off()

            self.uniformity_test_do(self._the_unit, serial_number, test_log)
            self.uniformity_test_alg(serial_number, test_log)
            self.data_export(serial_number, test_log)

        except Exception as e:
            self._operator_interface.print_to_console("Test exception {0}.\n".format(e))
        finally:
            self._operator_interface.print_to_console('release current test resource.\n')
            # noinspection PyBroadException
            try:
                if self._the_unit is not None:
                    self._the_unit.close()
                    self._the_unit = None
                if self._fixture is not None:
                    self._fixture.unload()
                    self._fixture.elminator_off()
            except:
                pass
            # if the_equipment is not None:
            #     the_equipment.uninit()
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
        ready = False
        power_on_trigger = False
        self._is_screen_on_by_op = False
        self._retries_screen_on = 0
        self._is_cancel_test_by_op = False

        serial_number = self._lastest_serial_number
        self._operator_interface.print_to_console("Testing Unit %s\n" % serial_number)
        self._the_unit = dut.pancakeDut(serial_number, self._station_config, self._operator_interface)
        if self._station_config.DUT_SIM:
            self._the_unit = dut.projectDut(serial_number, self._station_config, self._operator_interface)

        timeout_for_btn_idle = 20
        timeout_for_dual = timeout_for_btn_idle
        try:
            self._the_unit.initialize()
            self._fixture.button_enable()

            while timeout_for_dual > 0:
                if ready or self._is_cancel_test_by_op:
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
                            self._is_screen_on_by_op = True
                            ready = True  # Start to test.
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
                        self._is_cancel_test_by_op = True  # Cancel test.
                time.sleep(0.1)
                timeout_for_dual -= 1
        except Exception as e:
            self._operator_interface.print_to_console('Fixture is not ready for reason: {0}.\n'.format(e))
        finally:
            # noinspection PyBroadException
            try:
                self._fixture.button_disable()
                if not ready:
                    self._the_unit.close()
                    self._the_unit = None
                    if not self._is_cancel_test_by_op:
                        self._operator_interface.print_to_console(
                            'Unable to get start signal in %s from fixture.\n' % timeout_for_dual)
                        raise test_station.TestStationSerialNumberError('Fail to Wait for press dual-btn ...')
                    else:
                        self._operator_interface.print_to_console(
                            'Cancel start signal from dual %s.\n' % timeout_for_dual)
            except:
                pass
            self._operator_interface.prompt('', 'SystemButtonFace')

    def data_export(self, serial_number, test_log):
        """
        export csv and png from ttxm database
        :type test_log: test_station.TestRecord
        :type serial_number: str
        """
        for i in range(len(self._station_config.PATTERNS)):
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
                for meas in meas_list:
                    if meas['Measurement Setup'] != self._station_config.MEASUREMENTS[i]:
                        continue

                    id = meas['Measurement ID']
                    export_csv_name = "{}_{}.csv".format(serial_number, self._station_config.PATTERNS[i])
                    export_png_name = "{}_{}.png".format(serial_number, self._station_config.PATTERNS[i])
                    if self._station_config.IS_EXPORT_CSV:
                        self._equipment.export_measurement(id, output_dir, export_csv_name,
                                                           self._station_config.Resolution_Bin_X,
                                                           self._station_config.Resolution_Bin_Y)
                    if self._station_config.IS_EXPORT_PNG:
                        self._equipment.export_measurement(id, output_dir, export_png_name,
                                                           self._station_config.Resolution_Bin_X,
                                                           self._station_config.Resolution_Bin_Y)
                    self._operator_interface.print_to_console("Export data for {}\n"
                                                              .format(self._station_config.PATTERNS[i]))

    def normal_test_item_parse(self, br_pattern, result, test_log):
        """
        :type test_log: test_station.TestRecord
        :type result: []
        :type br_pattern: str
        """
        for resItem in result:
            test_item = (br_pattern + "_" + resItem).replace(" ", "")
            test_item = test_item.replace('\'', '')
            for limit_array in self._station_config.STATION_LIMITS_ARRAYS:
                if limit_array[0] == test_item and \
                        re.match(r'^([-|+]?\d+)(\.\d*)?$', result[resItem], re.IGNORECASE) is not None:
                    self._operator_interface.print_to_console(
                        '{}, {}.\n'.format(test_item, result[resItem]))
                    test_log.set_measured_value_by_name_ex(test_item, float(result[resItem]))
                    self._operator_interface.print_to_console('TEST ITEM: {}, Value: {}\n'
                                                              .format(test_item, result[resItem]))
                    break

    def uniformity_test_do(self, the_unit, serial_number, test_log):
        """
        export csv and png from ttxm database
        :type the_unit: dut.pancakeDut
        :type test_log: test_station.TestRecord
        :type serial_number: str
        """
        centerlv_gls = []
        gls = []
        for i in range(len(self._station_config.PATTERNS)):
            br_pattern = self._station_config.PATTERNS[i]
            self._operator_interface.print_to_console(
                "Panel Measurement Pattern: %s \n" % self._station_config.PATTERNS[i])
            # modified by elton . add random color
            # the_unit.display_color(self._station_config.COLORS[i])
            if isinstance(self._station_config.COLORS[i], tuple):
                the_unit.display_color(self._station_config.COLORS[i])
            elif isinstance(self._station_config.COLORS[i], (str, int)):
                the_unit.display_image(self._station_config.COLORS[i])

            analysis = self._station_config.ANALYSIS[i]
            use_camera = not self._station_config.EQUIPMENT_SIM
            analysis_result = self._equipment.sequence_run_step(analysis, '', use_camera,
                                                                self._station_config.IS_SAVEDB)
            self._operator_interface.print_to_console("sequence run step {}.\n".format(analysis))

            if not analysis_result.has_key(analysis):
                continue
            result = analysis_result[analysis]

            center_lv_key = 'CenterLv'
            if br_pattern[0] == 'W' and \
                    self._station_config.PATTERNS[i][1:4] in self._station_config.GAMMA_CHECK_GLS and \
                    result.has_key(center_lv_key):
                centerlv_gls.append(float(result[center_lv_key]))
                gls.append(float(br_pattern[1:4]))

            self.normal_test_item_parse(br_pattern, result, test_log)
        # gamma ...
        gamma = -1
        if len(gls) > 0 and len(centerlv_gls) > 0:
            norm_gls = np.log10([gl / max(gls) for gl in gls])
            norm_clv = np.log10([centerlv_gl / max(centerlv_gls) for centerlv_gl in centerlv_gls])
            gamma, cov = np.polyfit(norm_gls, norm_clv, 1, cov=False)
        test_log.set_measured_value_by_name_ex("DISPLAY_GAMMA", gamma)

    def uniformity_test_alg(self, serial_number, test_log):
        """
        :type test_log: test_station.TestRecord
        :type serial_number: str
        """
        output_dir = os.path.join(self._station_config.ROOT_DIR,
                                  self._station_config.ANALYSIS_RELATIVEPATH,
                                  serial_number + '_' + test_log._start_time.strftime("%Y%m%d-%H%M%S"))
        if not os.path.exists(output_dir):
            os.mkdir(output_dir, 777)

        points = self._station_config.TEST_POINTS_POS

        for i in range(len(self._station_config.PATTERNS)):
            br_pattern = self._station_config.PATTERNS[i]
            meas_list = self._equipment.get_measurement_list()
            for meas in meas_list:
                if meas['Measurement Setup'] not in self._station_config.MEASUREMENTS[i]:
                    continue

                id = meas['Measurement ID']
                export_csv_name = "{}_{}_register.csv".format(serial_number, self._station_config.PATTERNS[i])
                self._equipment.export_measurement(id, output_dir, export_csv_name,
                                                   self._station_config.Resolution_Bin_X_REGISTER,
                                                   self._station_config.Resolution_Bin_Y_REGISTER)
                lv = []
                cx = []
                cy = []
                fn = os.path.join(output_dir, export_csv_name)
                with open(fn) as f:
                    start_line = self._station_config.Resolution_REGISTER_SKIPTEXT
                    f.seek(0, 0)
                    for line in islice(f, start_line,
                                       start_line + self._station_config.Resolution_Bin_Y_REGISTER):
                        row_data = line.replace('\n', '').split(',')
                        lv.append([float(c) for c in row_data])
                    f.seek(0, 0)
                    start_line += (3 + self._station_config.Resolution_Bin_Y_REGISTER)
                    for line in islice(f, start_line,
                                       start_line + self._station_config.Resolution_Bin_Y_REGISTER):
                        row_data = line.replace('\n', '').split(',')
                        cx.append([float(c) for c in row_data])

                    f.seek(0, 0)
                    start_line += (3 + self._station_config.Resolution_Bin_Y_REGISTER)
                    for line in islice(f, start_line,
                                       start_line + self._station_config.Resolution_Bin_Y_REGISTER):
                        row_data = line.replace('\n', '').split(',')
                        cy.append([float(c) for c in row_data])

                os.remove(fn)
                lv = np.array(lv)
                cx = np.array(cx)
                cy = np.array(cy)

                keys = [x[0] for x in points]

                u = 4 * cx / (-2 * cx + 12 * cy + 3)
                v = 9 * cy / (-2 * cx + 12 * cy + 3)
                center_pos = dict(points)[self._station_config.CENTER_POINT_POS]
                center_u = u[center_pos]
                center_v = v[center_pos]

                lv_data = [lv[x[1]] for x in points]
                u_data = [u[x[1]] for x in points]
                v_data = [v[x[1]] for x in points]

                duv_data = np.sqrt((u_data - center_u)**2 + (v_data - center_v)**2)
                lv_dic = dict(zip(keys, lv_data))
                u_dic = dict(zip(keys, u_data))
                v_dic = dict(zip(keys, v_data))
                duv_dic = dict(zip(keys, duv_data))
                for posIdx, tes_pos in self._station_config.TEST_POINTS_POS:
                    lv = lv_dic[posIdx]
                    test_item = '{}_{}_Lv'.format(br_pattern, posIdx)
                    test_log.set_measured_value_by_name_ex(test_item, lv)

                    duv = duv_dic[posIdx]
                    test_item = '{}_{}_duv'.format(br_pattern, posIdx)
                    test_log.set_measured_value_by_name_ex(test_item, duv)

                max_lv = np.max(lv_data)
                min_lv = np.min(lv_data)
                test_item = '{}_Lv_max_variation'.format(br_pattern)
                test_log.set_measured_value_by_name_ex(test_item, (max_lv - min_lv) / max_lv)

                max_duv = np.max(duv_data)
                test_item = '{}_duv_max'.format(br_pattern)
                test_log.set_measured_value_by_name_ex(test_item, max_duv)

                for posIdx, grp in self._station_config.NEIGHBOR_POINTS:
                    tmp = []
                    for c in grp:
                        duv = duv_dic[c]
                        tmp.append(duv)
                        test_item = '{}_{}_{}_duv'.format(br_pattern, posIdx, c)
                        test_log.set_measured_value_by_name_ex(test_item, duv)
                    max_duv = np.max(tmp)
                    test_item = '{}_{}_neighbor_duv_max'.format(br_pattern, posIdx)
                    test_log.set_measured_value_by_name_ex(test_item, max_duv)