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
from verifiction.particle_counter import ParticleCounter
from verifiction.dut_checker import DutChecker
from factory_test_stations.test_station.test_fixture.test_fixture_project_station import projectstationFixture
from factory_test_stations.test_station.dut.dut import  projectDut
import types
from itertools import islice
import cv2

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
        self._runningCount = 0
        test_station.TestStation.__init__(self, station_config, operator_interface)
        self._fixture = test_fixture_pancake_uniformity.pancakeuniformityFixture(station_config, operator_interface)
        if station_config.FIXTURE_SIM:
            self._fixture = projectstationFixture(station_config, operator_interface)
        self._equipment = test_equipment_pancake_uniformity.pancakeuniformityEquipment(station_config)
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

        self._operator_interface.print_to_console("Initialize Camera %s\n" %self._station_config.CAMERA_SN)
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
        self._overall_result = False
        self._overall_errorcode = ''
#        self._operator_interface.operator_input("Manually Loading", "Please Load %s for testing.\n" % serial_number)
        self._fixture.elminator_on()
        self._fixture.load()
        try:
            self._operator_interface.print_to_console("Testing Unit %s\n" %serial_number)
            the_unit = dut.pancakeDut(serial_number, self._station_config, self._operator_interface)
            if self._station_config.DUT_SIM:
                the_unit = dut.projectDut(serial_number, self._station_config, self._operator_interface)
            test_log.set_measured_value_by_name_ex = types.MethodType(chk_and_set_measured_value_by_name, test_log)

            test_log.set_measured_value_by_name_ex("TT_Version", self._equipment.version())

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
                    except dut.DUTError as e:
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
                        msg = 'Retry power_on {}/{} times.\n'.format(retries,
                                                                     self._station_config.DUT_ON_MAXRETRY)
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
                raise pancakeuniformityError("DUT Is unable to Power on.")

            self._operator_interface.print_to_console("Read the particle count in the fixture... \n")
            particle_count = 0
            if self._station_config.FIXTURE_PARTICLE_COUNTER:
                particle_count = self._particle_counter.particle_counter_read_val()
            test_log.set_measured_value_by_name_ex("ENV_ParticleCounter", particle_count)

            self._operator_interface.print_to_console("Set Camera Database. %s\n" % self._station_config.CAMERA_SN)

            uni_file_name = re.sub('_x.log', '.ttxm', test_log.get_filename())
            bak_dir = os.path.join(self._station_config.ROOT_DIR, self._station_config.ANALYSIS_RELATIVEPATH)
            databaseFileName = os.path.join(bak_dir, uni_file_name)
            sequencePath = os.path.join(self._station_config.ROOT_DIR, self._station_config.SEQUENCE_RELATIVEPATH)
            if self._station_config.EQUIPMENT_SIM:
                databaseFileName = self._station_config.EQUIPMENT_DEMO_DATABASE
                self._equipment.set_database(databaseFileName)
            else:
                self._equipment.create_database(databaseFileName)
            self._equipment.set_sequence(sequencePath)

            self._operator_interface.print_to_console('clear registration\n')
            self._equipment.clear_registration()

            self._operator_interface.print_to_console("Close the eliminator in the fixture... \n")
            self._fixture.elminator_off()

            centerlv_gls = []
            gls = []

            '''
            centercolordifference255 = 0.0

            for i in  range(len(self._station_config.PATTERNS)):
                self._operator_interface.print_to_console(
                    "Panel Measurement Pattern: %s \n" %self._station_config.PATTERNS[i])
                # modified by elton . add random color
                # the_unit.display_color(self._station_config.COLORS[i])
                if isinstance(self._station_config.COLORS[i], tuple):
                    the_unit.display_color(self._station_config.COLORS[i])
                elif isinstance(self._station_config.COLORS[i], (str, int)):
                    the_unit.display_image(self._station_config.COLORS[i])

                imagekey = self._station_config.PATTERNS[i]
                analysis = self._station_config.ANALYSIS[i] + " " + self._station_config.PATTERNS[i]
                use_camera = not self._station_config.EQUIPMENT_SIM
                analysis_result = self._equipment.sequence_run_step(analysis, '', use_camera, self._station_config.IS_SAVEDB)
                self._operator_interface.print_to_console("sequence run step {}.\n".format(analysis))

                for c, result in analysis_result.items():
                    if c != analysis:
                        continue
                    for resItem in result:
                        test_item = (self._station_config.PATTERNS[i] + "_" + resItem).replace(" ", "")
                        test_item = test_item.replace('\'', '')

                        has_test_item = False
                        for limit_array in self._station_config.STATION_LIMITS_ARRAYS:
                            if limit_array[0] == test_item:
                                has_test_item = True
                        if not has_test_item:
                            continue

                        if re.match(r'^([-|+]?\d+)(\.\d*)?$', result[resItem], re.IGNORECASE) is not None:
                            self._operator_interface.print_to_console('{}, {}.\n'.format(test_item, result[resItem]))
                            test_log.set_measured_value_by_name_ex(test_item, float(result[resItem]))
                            self._operator_interface.print_to_console('TEST ITEM: {}, Value: {}\n'
                                                                      .format(test_item, result[resItem]))
                        # if '255' in self._station_config.PATTERNS[i] and 'Center Color (C' in r['Name']:
                        #     self._operator_interface.print_to_console("\n" + test_item + ": \t" + r['Value'] + "\n")
                        #     test_log.set_measured_value_by_name(test_item, float(r['Value']))
                        # elif 'W' in self._station_config.PATTERNS[i] and 'CenterColorDifference'in r['Name']:
                        #     if 'W255' in self._station_config.PATTERNS[i]:
                        #         centercolordifference255 = float(r['Value'])
                        #     else:
                        #         test_value = abs(float(r['Value'])-centercolordifference255)
                        #         test_log.set_measured_value_by_name(test_item, test_value)
                        # else:
                        #     test_log.set_measured_value_by_name(test_item, float(r['Value']))
                        #
                        # if self._station_config.PATTERNS[i][0] == 'W' and \
                        #         self._station_config.PATTERNS[i][1:4] in self._station_config.GAMMA_CHECK_GLS and \
                        #         r['Name'] == 'CenterLv':
                        #     centerlv_gls.append(float(r['Value']))
                        #     gls.append(float(self._station_config.PATTERNS[i][1:4]))

                self._operator_interface.print_to_console("close run step {}.\n"
                                                          .format(self._station_config.PATTERNS[i]))
               
                mesh_data = the_equipment.get_last_mesh()

                if os.path.exists(os.path.join(output_dir, filename)):
                    the_equipment.delete_file(os.path.join(output_dir, filename))

                if mesh_data != {}:
                    output_data = StringIO.StringIO()
                    np.savez_compressed(output_data, **mesh_data)
                    npzdata = output_data.getvalue()
                    ## LEAVE for the logging of npzdata
                    ## LEAVE for the logging of npzdata
                    # also calculate some statistical infdir()o about the measurement
                    for c in ["Lv", "Cx", "Cy","u'", "v'"]:
                        cdata = mesh_data.get(c)
                        filename = the_unit.serial_number + "_" + c + "_" +self._station_config.PATTERNS[i] + ".csv"
                        unit_log_path = os.path.join(output_dir, filename)
                        self._operator_interface.print_to_console(
                            "\n Saving Jacob's data of: %s \n" % unit_log_path)
                        np.savetxt(unit_log_path, cdata, delimiter=',')
#                        if cdata is not None:
#                            cmean = np.mean(cdata, dtype=np.float32)
#                            cmax = cdata.max()
#                            cmin = cdata.min()
#                            cstd = np.std(cdata, dtype=np.float32)


            ### implement tests here.  Note thadir(t the test name matches one in the station_limits file ###
            '''
            self.uniformity_test_do(the_unit, serial_number, test_log)
            self.uniformity_test_alg(serial_number, test_log)
            self.data_export(serial_number, test_log)

        except Exception, e:
            self._operator_interface.print_to_console("Test exception {}.\n".format(e.message))
        finally:
            self._operator_interface.print_to_console('release current test resource.\n')
            if the_unit is not None:
                the_unit.close()
            if self._fixture is not None:
                self._fixture.unload()
                self._fixture.elminator_off()
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

    def is_ready(self):
        self._fixture.is_ready()

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
        if self._station_config.Resolution_Bin_REGISTER_PATTERN not in self._station_config.PATTERNS:
            return

        points = self._station_config.TEST_POINTS_POS

        for i in range(len(self._station_config.PATTERNS)):
            br_pattern = self._station_config.PATTERNS[i]
            meas_list = self._equipment.get_measurement_list()
            for meas in meas_list:
                if meas['Measurement Setup'] != self._station_config.MEASUREMENTS[i]:
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

                u = 2 * cx / (-2 * cx + 12 * cy + 3)
                v = 9 * cy / (-2 * cx + 12 * cy + 3)
                center_pos = dict(points)['P1']
                center_u = u[center_pos[0]]
                center_v = v[center_pos[1]]

                lv_data = [lv[x[1]] for x in points]
                u_data = [u[x[1]] for x in points]
                v_data = [v[x[1]] for x in points]

                duv = np.sqrt((u - center_u)**2 + (v - center_v)**2)
                lv_points = dict(zip(keys, lv_data))
                u_points = dict(zip(keys, u_data))
                v_points = dict(zip(keys, v_data))

                cv_lv = np.std(np.array(lv), dtype=np.float32) / np.mean(np.array(lv))
                test_item = '{}_Brightness_Variation'.format(br_pattern)
                test_log.set_measured_value_by_name_ex(test_item, cv_lv)

                cv_color = np.std(np.array(duv), dtype=np.float32) / np.mean(np.array(duv))
                test_item = '{}_Color_Variation'.format(br_pattern)
                test_log.set_measured_value_by_name_ex(test_item, cv_color)
                duv_dic = dict(zip(keys, duv))
                grps = [['P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9'],
                       ['P1', 'P3', 'P9'],
                       ['P2', 'P1', 'P4'],
                       ['P3', 'P1', 'P5'],
                       ['P4', 'P1', 'P6'],
                       ['P5', 'P1', 'P7'],
                       ['P6', 'P1', 'P8'],
                       ['P7', 'P1', 'P9'],
                       ['P8', 'P1', 'P2']]
                for grp in grps:
                    tmp = []
                    for c in grp:
                        tmp.append(duv_dic[c])
                    cv_color = np.std(np.array(tmp), dtype=np.float32)/np.mean(np.array(tmp))
                    test_item = '{}_Max_Neighbor_Color_Variation'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, cv_color)
                pass
