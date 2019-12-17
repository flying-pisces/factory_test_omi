import hardware_station_common.test_station.test_station as test_station
import test_station.test_fixture.test_fixture_pancake_pixel as test_fixture_pancake_pixel
import test_station.test_equipment.test_equipment_pancake_pixel as test_equipment_pancake_pixel
import test_station.dut as dut
import os
import shutil
import time
import math
import datetime
import re
import filecmp
import numpy as np
from itertools import islice
from verifiction.particle_counter import ParticleCounter
from verifiction.dut_checker import DutChecker
from test_fixture.test_fixture_project_station import projectstationFixture
import pprint
import types
import glob


class pancakepixelError(Exception):
    pass

def chk_and_set_measured_value_by_name(test_log, item, value):
    """

    :type test_log: test_station.TestRecord
    """
    if item in test_log.results_array():
        test_log.set_measured_value_by_name(item, value)
    pass

class pancakepixelStation(test_station.TestStation):
    """
        pancakepixel Station
    """

    def __init__(self, station_config, operator_interface):
        self._sw_version = '1.0.2'
        self._runningCount = 0
        test_station.TestStation.__init__(self, station_config, operator_interface)
        self._fixture = test_fixture_pancake_pixel.pancakepixelFixture(station_config, operator_interface)
        if station_config.FIXTURE_SIM:
            self._fixture = projectstationFixture(station_config, operator_interface)
        self._equipment = test_equipment_pancake_pixel.pancakepixelEquipment(station_config)
        self._particle_counter = ParticleCounter(station_config)
        if self._station_config.FIXTURE_PARTICLE_COUNTER:
            self._particle_counter.initialize()
            if self._particle_counter.particle_counter_state() == 0:
                self._particle_counter.particle_counter_on()
                self._particle_counter_start_time = datetime.datetime.now()
        self._dut_checker = DutChecker(station_config)
        self._overall_errorcode = ''
        self._first_failed_test_result = None

    def initialize(self):
        self._operator_interface.print_to_console("Initializing station...\n")
        self._fixture.initialize()

        if self._station_config.FIXTURE_PARTICLE_COUNTER and hasattr(self, '_particle_counter_start_time'):
            while ((datetime.datetime.now() - self._particle_counter_start_time)
                   < datetime.timedelta(self._station_config.FIXTRUE_PARTICLE_START_DLY)):
                time.sleep(0.1)
                self._operator_interface.print_to_console('Waiting for initializing particle counter ...\n')
        self._equipment.initialize()

    def _close_fixture(self):
        if self._fixture is not None:
            try:
                self._operator_interface.print_to_console("Close...\n")
                self._fixture.status()
                self._fixture.elminator_off()
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
        self._operator_interface.print_to_console('CWD is {}\n'.format(os.getcwd()))
        #        self._operator_interface.operator_input("Manually Loading", "Please Load %s for testing.\n" % serial_number)
        self._fixture.elminator_on()
        self._fixture.load()

        try:
            self._operator_interface.print_to_console("Testing Unit %s\n" % serial_number)
            the_unit = dut.pancakeDut(serial_number, self._station_config, self._operator_interface)
            if self._station_config.DUT_SIM:
                the_unit = dut.projectDut(serial_number, self._station_config, self._operator_interface)
            test_log.set_measured_value_by_name_ex('SW_VERSION', self._sw_version)
            test_log.set_measured_value_by_name_ex("MPK_API_Version", self._equipment.version())

            the_unit.initialize()
            self._operator_interface.print_to_console("Initialize DUT... \n")
            retries = 0
            is_screen_on = False
            try:
                if self._station_config.DISP_CHECKER_ENABLE:
                    self._dut_checker.initialize()
                    time.sleep(self._station_config.DISP_CHECKER_DLY)
                while retries < self._station_config.DUT_ON_MAXRETRY and not is_screen_on:
                    is_reboot_need = False
                    retries += 1
                    try:
                        is_screen_on = the_unit.screen_on() or self._station_config.DUT_SIM
                    except dut.DUTError:
                        is_screen_on = False
                    else:
                        if self._station_config.DISP_CHECKER_ENABLE and is_screen_on:
                            the_unit.display_image(self._station_config.DISP_CHECKER_IMG_INDEX)
                            score = self._dut_checker.do_checker()
                            self._operator_interface.print_to_console(
                                "dut checker using blob detection. {} \n".format(score))
                            is_screen_on = False
                            if score is not None:
                                arr = np.array(score)
                                score_num = np.where((arr >= self._station_config.DISP_CHECKER_L_SCORE)
                                                     & (arr <= self._station_config.DISP_CHECKER_H_SCORE))
                                if np.max(arr) < self._station_config.DISP_CHECKER_EXL_SCORE:
                                    is_screen_on = len(score_num[0]) == self._station_config.DISP_CHECKER_COUNT
                                else:
                                    is_reboot_need = True

                    if not is_screen_on:
                        msg = 'Retry power_on {}/{} times.\n'.format(retries, self._station_config.DUT_ON_MAXRETRY)
                        self._operator_interface.print_to_console(msg)
                        the_unit.screen_off()
                        if is_reboot_need:
                            self._operator_interface.print_to_console("try to reboot the driver board... \n")
                            the_unit.reboot()

                    if self._station_config.DISP_CHECKER_IMG_SAVED:
                        fn0 = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
                        fn = '{0}_{1}_{2}.jpg'.format(serial_number, retries, fn0)
                        self._dut_checker.save_log_img(fn)
            finally:
                self._dut_checker.close()
                test_log.set_measured_value_by_name_ex("DUT_ScreenOnRetries", retries)
                test_log.set_measured_value_by_name_ex("DUT_ScreenOnStatus", is_screen_on)

            if not is_screen_on:
                raise pancakepixelError("DUT Is unable to Power on.")

            self._operator_interface.print_to_console("Read the particle count in the fixture... \n")
            particle_count = 0
            if self._station_config.FIXTURE_PARTICLE_COUNTER:
                particle_count = self._particle_counter.particle_counter_read_val()
            test_log.set_measured_value_by_name_ex("ENV_ParticleCounter", particle_count)

            self._operator_interface.print_to_console("Set Camera Database. %s\n" % self._station_config.CAMERA_SN)

            uni_file_name = re.sub('_x.log', '.ttxm', test_log.get_filename())
            bak_dir = os.path.join(self._station_config.ROOT_DIR, self._station_config.ANALYSIS_RELATIVEPATH)

            sequencePath = os.path.join(self._station_config.ROOT_DIR,
                                        self._station_config.SEQUENCE_RELATIVEPATH)
            if not self._station_config.EQUIPMENT_SIM:
                databaseFileName = os.path.join(bak_dir, uni_file_name)
                self._equipment.create_database(databaseFileName)
            else:
                db_dir = self._station_config.EQUIPMENT_DEMO_DATABASE
                fns = glob.glob1(db_dir, '%s_.ttxm' % (serial_number))
                if len(fns) > 0:
                    databaseFileName = os.path.join(db_dir, fns[0])
                    self._operator_interface.print_to_console("Set tt_database {}.\n".format(databaseFileName))
                    self._equipment.set_database(databaseFileName)
                else:
                    raise pancakepixelError('unable to find ttxm for SN: %s \n' % (serial_number))
            self._equipment.set_sequence(sequencePath)

            self._operator_interface.print_to_console('clear registration\n')
            self._equipment.clear_registration()

            self._operator_interface.print_to_console("Close the eliminator in the fixture... \n")
            self._fixture.elminator_off()

            self.bright_subpixel_do(the_unit, serial_number, test_log)
            self.dark_subpixel_do(the_unit, serial_number, test_log)
            self.data_export(serial_number, test_log)

        except Exception, e:
            self._operator_interface.print_to_console("Test exception . {}\n".format(e))
        finally:
            self._operator_interface.print_to_console('release current test resource.\n')
            if the_unit is not None:
                the_unit.close()
            if self._fixture is not None:
                self._fixture.unload()
                self._fixture.elminator_off()

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

    def is_ready(self):
        self._fixture.is_ready()

    def calc_blemish_index(self, pattern, zdata, test_log):
        self._operator_interface.print_to_console("calc blemish_index {}.\n".format(pattern))
        test_item = pattern + "_" + "BlemishIndex"
        if test_item not in test_log.results_array():
            return
        # Algorithm For blemish_index
        blemish_index = 0

        if len(zdata) > 0:
            npdata = np.array(zdata)
            size_list = npdata[:, 0]
            locax_list = npdata[:, 1]
            locay_list = npdata[:, 2]
            pixel_list = npdata[:, 3]
            constrast_lst = npdata[:, 4]
            abs_contrast = np.abs(constrast_lst)
            location_r = np.sqrt(np.power(np.array(locax_list) - self._station_config.LOCATION_X0, 2)
                                 * np.power(np.array(locay_list) - self._station_config.LOCATION_Y0, 2))
            location_index = []
            size_index = []
            for id in range(len(locax_list)):
                tmp_local_index = 0
                tmp_size_index = 0
                if location_r[id] <= self._station_config.LOCATION_L:
                    tmp_local_index = 2
                elif self._station_config.LOCATION_L < location_r[id] <= self._station_config.LOCATION_U:
                    tmp_local_index = 1
                elif location_r[id] > self._station_config.LOCATION_U:
                    tmp_local_index = 0

                if size_list[id] <= self._station_config.SIZE_L:
                    tmp_size_index = 0
                elif self._station_config.SIZE_L < size_list[id] <= self._station_config.SIZE_U:
                    tmp_size_index = 1
                elif size_list[id] > self._station_config.SIZE_U:
                    tmp_size_index = 2

                location_index.append(tmp_local_index)
                size_index.append(tmp_size_index)

            defect_index = abs_contrast * np.array(location_index) * np.array(size_index)
            blemish_index = np.sum(defect_index)
            if self._station_config.IS_VERBOSE:
                print 'constrast_{}:{}'.format(pattern, constrast_lst)
                print 'locationX_{}:{}'.format(pattern, locax_list)
                print 'locationY_{}:{}'.format(pattern, locay_list)
                print 'size     _{}:{}'.format(pattern, size_list)
                print 'pixel    _{}:{}'.format(pattern, pixel_list)
        test_log.set_measured_value_by_name_ex(test_item, blemish_index)

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

    def bright_subpixel_do(self, the_unit, serial_number, test_log):
        """
        export csv and png from ttxm database
        :type the_unit: dut.pancakeDut
        :type test_log: test_station.TestRecord
        :type serial_number: str
        """
        avg_lv_register_patterns = []
        for idx, br_pattern in enumerate(self._station_config.PATTERNS_BRIGHT):
            if br_pattern not in self._station_config.PATTERNS:
                self._operator_interface.print_to_console("unable to find pattern: %s\n" % br_pattern)
                continue
            i = self._station_config.PATTERNS.index(br_pattern)
            self._operator_interface.print_to_console(
                "Panel Measurement Pattern: %s\n" % self._station_config.PATTERNS[i])

            # modified by elton . add random color
            if isinstance(self._station_config.COLORS[i], tuple):
                the_unit.display_color(self._station_config.COLORS[i])
            elif isinstance(self._station_config.COLORS[i], (str, int)):
                the_unit.display_image(self._station_config.COLORS[i])

            # analysis = self._station_config.ANALYSIS[i] + " " + self._station_config.PATTERNS[i]
            analysis = self._station_config.ANALYSIS[i]
            use_camera = not self._station_config.EQUIPMENT_SIM
            if not use_camera:
                self._equipment.clear_registration()
            analysis_result = self._equipment.sequence_run_step(analysis, '', use_camera, self._station_config.IS_SAVEDB)
            self._operator_interface.print_to_console("sequence run step {}.\n".format(analysis))

            if 0 <= idx <= 1:  # the first 2 patterns are used to register.
                meas_list = self._equipment.get_measurement_list()
                for meas in meas_list:
                    if meas['Measurement Setup'] != self._station_config.MEASUREMENTS[i]:
                        continue
                    output_dir = os.path.join(self._station_config.ROOT_DIR,
                                              self._station_config.ANALYSIS_RELATIVEPATH,
                                              serial_number + '_' + test_log._start_time.strftime("%Y%m%d-%H%M%S"))
                    if not os.path.exists(output_dir):
                        os.mkdir(output_dir, 777)
                    id = meas['Measurement ID']
                    export_csv_name = "{}_{}_register.csv".format(serial_number, self._station_config.PATTERNS[i])
                    self._equipment.export_measurement(id, output_dir, export_csv_name,
                                                       self._station_config.Resolution_Bin_X_REGISTER,
                                                       self._station_config.Resolution_Bin_Y_REGISTER)
                    lv = []
                    fn = os.path.join(output_dir, export_csv_name)
                    with open(fn) as f:
                        for line in islice(f, self._station_config.Resolution_REGISTER_SKIPTEXT,
                                           self._station_config.Resolution_Bin_Y_REGISTER):
                            row_data = line.replace('\n', '').split(',')
                            lv.append([float(c) for c in row_data])
                    avg = np.array(lv).mean()
                    avg_lv_register_patterns.append(avg)
                    os.remove(fn)
            else:
                size_list = []
                locax_list = []
                locay_list = []
                pixel_list = []
                constrast_lst = []
                for c, result in analysis_result.items():
                    if not isinstance(result, dict) or not result.has_key('NumDefects'):
                        continue
                    num = int(result['NumDefects'])
                    self._operator_interface.print_to_console("prase numDefect {}, Num={}.\n"
                                                              .format(self._station_config.PATTERNS[i], num))
                    for id in range(1, num + 1):
                        size_key = 'Size_{}'.format(id)
                        locax_key = 'LocX_{}'.format(id)
                        locay_key = 'LocY_{}'.format(id)
                        contrast_key = 'Contrast_{}'.format(id)
                        pixel_key = 'Pixels_{}'.format(id)
                        if (result.has_key(size_key) and
                                result.has_key(locax_key) and
                                result.has_key(locay_key) and
                                result.has_key(contrast_key) and
                                result.has_key(pixel_key)):
                            size_list.append(float(result[size_key]))
                            locax_list.append(float(result[locax_key]))
                            locay_list.append(float(result[locay_key]))
                            pixel_list.append(float(result[pixel_key]))
                            constrast_lst.append(float(result[contrast_key]))

                    self._operator_interface.print_to_console("prase normal test item {}.\n"
                                                              .format(self._station_config.PATTERNS[i]))
                    self.normal_test_item_parse(br_pattern, result, test_log)

                    pos_items = zip(locax_list, locay_list)
                    super_brighter_count = 0
                    min_super_sepa_distance = 0
                    super_dimmer_count = 0
                    min_super_dimmer_distance = 0
                    quality_brighter_count = 0
                    min_qual_brighter_sepa_distance = 0
                    quality_dimmeru_count = 0
                    min_qual_dimu_sepa_distance = 0
                    quality_dimmerl_count = 0
                    min_qual_diml_sepa_distance = 0
                    if num > 0 and len(constrast_lst) > 0:
                        abs_contrast = np.abs(constrast_lst)
                        location_r = np.sqrt(np.power(np.array(locax_list) - self._station_config.LOCATION_X0, 2)
                                             + np.power(np.array(locay_list) - self._station_config.LOCATION_Y0, 2))
                        con_r = zip(abs_contrast, location_r)

                        defects = [c > avg_lv_register_patterns[0] and
                                                              d <= self._station_config.SUPER_QUALITY_AREA_R
                                                              for c, d in con_r]

                        super_brighter_count = defects.count(True)
                        min_super_sepa_distance = self.calc_separate_distance(pos_items, defects)

                        defects = [c <= avg_lv_register_patterns[0] and
                                              d <= self._station_config.SUPER_QUALITY_AREA_R
                                              for c, d in con_r]

                        super_dimmer_count = defects.count(True)
                        min_super_dimmer_distance = self.calc_separate_distance(pos_items, defects)

                        defects = [c > avg_lv_register_patterns[1] and
                            self._station_config.QUALITY_AREA_R >= d > self._station_config.SUPER_QUALITY_AREA_R
                            for c, d in con_r]
                        quality_brighter_count = defects.count(True)
                        min_bri_sepa_distance = self.calc_separate_distance(pos_items, defects)

                        defects = [ avg_lv_register_patterns[0] < c <= avg_lv_register_patterns[1] and
                             self._station_config.QUALITY_AREA_R >= d > self._station_config.SUPER_QUALITY_AREA_R
                             for c, d in con_r]
                        quality_dimmeru_count = defects.count(True)
                        min_qual_dimu_sepa_distance = self.calc_separate_distance(pos_items, defects)

                        defects = [ avg_lv_register_patterns[0] >= c and
                             self._station_config.QUALITY_AREA_R >= d > self._station_config.SUPER_QUALITY_AREA_R
                             for c, d in con_r]
                        quality_dimmerl_count = defects.count(True)
                        min_qual_diml_sepa_distance = self.calc_separate_distance(pos_items, defects)

                    test_item = '{}_SuperQuality_Brighter_NumDefects'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, super_brighter_count)
                    test_item = '{}_SuperQuality_Brighter_MinSeparationDistance'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, min_super_sepa_distance)
                    test_item = '{}_SuperQuality_Brighter_Res'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, super_brighter_count == 0 or
                                                           super_brighter_count <= self._station_config.SUPER_AREA_DEFECTS_COUNT_L)
                    test_item = '{}_SuperQuality_Dimmer_NumDefects'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, super_dimmer_count)
                    test_item = '{}_SuperQuality_Dimmer_MinSeparationDistance'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, min_super_dimmer_distance)
                    test_item = '{}_SuperQuality_Dimmer_Res'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, super_dimmer_count == 0 or
                                                           super_dimmer_count <= self._station_config.SUPER_AREA_DEFECTS_COUNT_H and
                                                           min_super_dimmer_distance >= self._station_config.SEPARATION_DISTANCE)
                    test_item = '{}_Quality_Brighter_NumDefects'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, quality_brighter_count)
                    test_item = '{}_Quality_Brighter_MinSeparationDistance'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, min_qual_brighter_sepa_distance)
                    test_item = '{}_Quality_Brighter_Res'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, quality_brighter_count == 0 or
                                                           quality_brighter_count <= self._station_config.QUALITY_AREA_DEFECTS_COUNT_B)
                    test_item = '{}_Quality_DimmerU_NumDefects'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, quality_dimmeru_count)
                    test_item = '{}_Quality_DimmerU_MinSeparationDistance'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, min_qual_dimu_sepa_distance)
                    test_item = '{}_Quality_DimmerU_Res'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, quality_dimmeru_count == 0 or
                                                           quality_dimmeru_count <= self._station_config.QUALITY_AREA_DEFECTS_COUNT_DU
                                                           and min_qual_dimu_sepa_distance >= self._station_config.SEPARATION_DISTANCE)
                    test_item = '{}_Quality_DimmerL_NumDefects'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, quality_dimmerl_count)
                    test_item = '{}_Quality_DimmerL_MinSeparationDistance'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, min_qual_diml_sepa_distance)
                    test_item = '{}_Quality_DimmerL_Res'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, quality_dimmerl_count == 0 or
                                                           quality_dimmerl_count <= self._station_config.QUALITY_AREA_DEFECTS_COUNT_DL
                                                           and min_qual_diml_sepa_distance >= self._station_config.SEPARATION_DISTANCE_L)

                    self.calc_blemish_index(br_pattern,
                        zip(size_list, locax_list, locay_list, pixel_list, constrast_lst), test_log)

    def calc_separate_distance(self, defect_positions, mask_pos):
        distance_items = []
        pos_items = []
        for pos, value in enumerate(mask_pos):
            if not value:
                continue
            pos_items.append(pos)
        num = len(pos_items)
        x = np.array(defect_positions)[:, 0][pos_items]
        y = np.array(defect_positions)[:, 1][pos_items]
        for row in range(num):
            for col in range(num):
                if row != col:
                    dis = ((x[col] - x[row]) ** 2 + (y[col] - y[row]) ** 2) ** 0.5
                    distance_items.append(dis)
        if len(distance_items) <= 1:
            return 0
        return min(distance_items)

    def normal_test_item_parse(self, br_pattern, result, test_log):
        """
        :type test_log: test_station.TestRecord
        :type result: []
        :type br_pattern: str
        """
        for resItem in result:
            test_item = (br_pattern + "_" + resItem).replace(" ", "")
            for limit_array in self._station_config.STATION_LIMITS_ARRAYS:
                if limit_array[0] == test_item and \
                        re.match(r'^([-|+]?\d+)(\.\d*)?$', result[resItem], re.IGNORECASE) is not None:
                    self._operator_interface.print_to_console(
                        '{}, {}.\n'.format(test_item, result[resItem]))
                    test_log.set_measured_value_by_name_ex(test_item, float(result[resItem]))
                    self._operator_interface.print_to_console('TEST ITEM: {}, Value: {}\n'
                                                              .format(test_item, result[resItem]))
                    break

    def dark_subpixel_do(self, the_unit, serial_number, test_log):
        for idx, br_pattern in enumerate(self._station_config.PATTERNS_DARK):
            if br_pattern not in self._station_config.PATTERNS:
                self._operator_interface.print_to_console("unable to find pattern: %s\n" % br_pattern)
                continue
            i = self._station_config.PATTERNS.index(br_pattern)
            self._operator_interface.print_to_console(
                "Panel Measurement Pattern: %s\n" % self._station_config.PATTERNS[i])

            # modified by elton . add random color
            if isinstance(self._station_config.COLORS[i], tuple):
                the_unit.display_color(self._station_config.COLORS[i])
            elif isinstance(self._station_config.COLORS[i], (str, int)):
                the_unit.display_image(self._station_config.COLORS[i])

            # analysis = self._station_config.ANALYSIS[i] + " " + self._station_config.PATTERNS[i]
            analysis = self._station_config.ANALYSIS[i]
            use_camera = not self._station_config.EQUIPMENT_SIM
            if not use_camera:
                self._equipment.clear_registration()
            analysis_result = self._equipment.sequence_run_step(analysis, '', use_camera, self._station_config.IS_SAVEDB)
            self._operator_interface.print_to_console("sequence run step {}.\n".format(analysis))

            size_list = []
            locax_list = []
            locay_list = []
            pixel_list = []
            constrast_lst = []
            for c, result in analysis_result.items():
                if not isinstance(result, dict) or not result.has_key('NumDefects'):
                    continue
                num = int(result['NumDefects'])
                self._operator_interface.print_to_console("prase numDefect {}, Num={}.\n"
                                                          .format(self._station_config.PATTERNS[i], num))
                for id in range(1, num + 1):
                    size_key = 'Size_{}'.format(id)
                    locax_key = 'LocX_{}'.format(id)
                    locay_key = 'LocY_{}'.format(id)
                    contrast_key = 'Contrast_{}'.format(id)
                    pixel_key = 'Pixels_{}'.format(id)
                    if (result.has_key(size_key) and
                            result.has_key(locax_key) and
                            result.has_key(locay_key) and
                            result.has_key(contrast_key) and
                            result.has_key(pixel_key)):
                        size_list.append(float(result[size_key]))
                        locax_list.append(float(result[locax_key]))
                        locay_list.append(float(result[locay_key]))
                        pixel_list.append(float(result[pixel_key]))
                        constrast_lst.append(float(result[contrast_key]))

                self._operator_interface.print_to_console("prase normal test item {}.\n"
                                                          .format(self._station_config.PATTERNS[i]))
                self.normal_test_item_parse(br_pattern, result, test_log)

                pos_items = zip(locax_list, locay_list)

                super_quality_count = 0
                min_super_sepa_distance = 0
                quality_count = 0
                min_qaul_sepa_distance = 0

                if num > 0 and len(constrast_lst) > 0:
                    abs_contrast = np.abs(constrast_lst)
                    location_r = np.sqrt(np.power(np.array(locax_list) - self._station_config.LOCATION_X0, 2)
                                         + np.power(np.array(locay_list) - self._station_config.LOCATION_Y0, 2))
                    con_r = zip(abs_contrast, location_r)

                    defects = [d < self._station_config.SUPER_QUALITY_AREA_R
                               for c, d in con_r]
                    super_quality_count = defects.count(True)

                    min_super_sepa_distance = self.calc_separate_distance(pos_items, defects)

                    defects = [self._station_config.QUALITY_AREA_R >= d > self._station_config.SUPER_QUALITY_AREA_R
                               for c, d in con_r]
                    quality_count = defects.count(True)

                    min_qaul_sepa_distance = self.calc_separate_distance(pos_items, defects)

                test_item = '{}_SuperQuality_NumDefects'.format(br_pattern)
                test_log.set_measured_value_by_name_ex(test_item, super_quality_count)
                test_item = '{}_SuperQuality_MinSeparationDistance'.format(br_pattern)
                test_log.set_measured_value_by_name_ex(test_item, min_super_sepa_distance)
                test_item = '{}_SuperQuality_Res'.format(br_pattern)
                test_log.set_measured_value_by_name_ex(test_item,
                                                       super_quality_count == 0 or
                                                       self._station_config.DARK_SUPER_AREA_DEFECTS_COUNT_L <= super_quality_count
                                                       <= self._station_config.DARK_SUPER_AREA_DEFECTS_COUNT_H and
                                                       min_super_sepa_distance >= self._station_config.SEPARATION_DISTANCE)

                test_item = '{}_Quality_NumDefects'.format(br_pattern)
                test_log.set_measured_value_by_name_ex(test_item, quality_count)
                test_item = '{}_Quality_MinSeparationDistance'.format(br_pattern)
                test_log.set_measured_value_by_name_ex(test_item, min_qaul_sepa_distance)
                test_item = '{}_Quality_Res'.format(br_pattern)
                test_log.set_measured_value_by_name_ex(test_item,
                                                       quality_count == 0 or
                                                       self._station_config.DARK_SUPER_AREA_DEFECTS_COUNT_L <= quality_count
                                                       <= self._station_config.DARK_SUPER_AREA_DEFECTS_COUNT_H and
                                                       min_qaul_sepa_distance >= self._station_config.SEPARATION_DISTANCE)
                self.calc_blemish_index(br_pattern,
                     zip(size_list, locax_list, locay_list, pixel_list, constrast_lst), test_log)
