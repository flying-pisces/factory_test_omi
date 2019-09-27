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


class pancakeuniformityError(Exception):
    pass


class pancakeuniformityStation(test_station.TestStation):
    """
        pancakeuniformity Station
    """

    def __init__(self, station_config, operator_interface):
        self._runningCount = 0
        test_station.TestStation.__init__(self, station_config, operator_interface)
        self._fixture = test_fixture_pancake_uniformity.pancakeuniformityFixture(station_config, operator_interface)
        # self._equipment = test_equipment_pancake_uniformity.pancakeuniformityEquipment(station_config, operator_interface)
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
        dbfn = os.path.join(self._station_config.ROOT_DIR, self._station_config.DATABASE_RELATIVEPATH)
        empytdb = os.path.join(self._station_config.ROOT_DIR, self._station_config.EMPTY_DATABASE_RELATIVEPATH)
        if self._station_config.RESTART_TEST_COUNT != 1 and \
                self._station_config.IS_SAVEDB and \
                os.path.exists(dbfn) and not filecmp.cmp(dbfn, empytdb):
            dbfnbak = "{0}_{1}_autobak.ttxm".format(self._station_config.STATION_TYPE,
                                                    datetime.datetime.now().strftime("%y%m%d%H%M%S"))
            self._operator_interface.print_to_console("backup ttxm raw database to {}...\n".format(dbfnbak))
            self.backup_database(dbfnbak, True)

        self._operator_interface.print_to_console("Empty ttxm raw database ...\n")
        shutil.copyfile(empytdb, dbfn)

        if self._station_config.FIXTURE_PARTICLE_COUNTER and hasattr(self, '_particle_counter_start_time'):
            while ((datetime.datetime.now() - self._particle_counter_start_time)
                   < datetime.timedelta(self._station_config.FIXTRUE_PARTICLE_START_DLY)):
                time.sleep(0.1)
                self._operator_interface.print_to_console('Waiting for initializing particle counter ...\n')

        if self._station_config.DISP_CHECKER_ENABLE:
            self._operator_interface.print_to_console('Initializing camera dut checker...\n')
            self._dut_checker.initialize()
            time.sleep(self._station_config.DISP_CHECKER_DLY)

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
                self._particle_counter.particle_counter_off()
            finally:
                self._particle_counter.close()
                self._particle_counter = None

    def close(self):
        self._close_fixture()
        self._close_particle_counter()

    def _do_test(self, serial_number, test_log):
        self._overall_result = False
        self._overall_errorcode = ''
#        self._operator_interface.operator_input("Manually Loading", "Please Load %s for testing.\n" % serial_number)
        self._fixture.elminator_on()
        self._fixture.load()
        try:
            self._operator_interface.print_to_console("Testing Unit %s\n" %serial_number)
            the_unit = dut.pancakeDut(serial_number, self._station_config, self._operator_interface)

            the_unit.initialize()
            self._operator_interface.print_to_console("Initialize DUT... \n")
            retries = 1
            is_screen_on = False
            try:
                self._dut_checker.initialize()
                while retries < self._station_config.DUT_ON_MAXRETRY and not is_screen_on:
                    try:
                        is_screen_on = the_unit.screen_on()
                    except dut.displayCtrl.displayCtrlMyzyError as e:
                        is_screen_on = False
                    else:
                        if self._station_config.DISP_CHECKER_ENABLE and is_screen_on:
                            score = self._dut_checker.do_checker()
                            is_screen_on = (
                                        score is not None and max(score) >= self._station_config.DISP_CHECKER_L_SCORE)

                    if not is_screen_on:
                        msg = 'Retry power_on {}/{} times.\n'.format(retries + 1,
                                                                     self._station_config.DUT_ON_MAXRETRY)
                        self._operator_interface.print_to_console(msg)
                        the_unit.screen_off()

                    if self._station_config.DISP_CHECKER_IMG_SAVED:
                        fn0 = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
                        fn = '{0}_{1}_{2}.jpg'.format(serial_number, retries, fn0)
                        self._dut_checker.save_log_img(fn)

                    retries += 1
            finally:
                self._dut_checker.close()
                test_log.set_measured_value_by_name("DUT_ScreenOnRetries", retries)
                test_log.set_measured_value_by_name("DUT_ScreenOnStatus", is_screen_on)

            self._operator_interface.print_to_console("Read the particle count in the fixture... \n")
            particle_count = self._particle_counter.particle_counter_read_val()
            test_log.set_measured_value_by_name("ENV_ParticleCounter", particle_count)

            the_equipment = test_equipment_pancake_uniformity.pancakeuniformityEquipment(self._station_config.IS_VERBOSE, self._station_config.FOCUS_DISTANCE,
                                            self._station_config.APERTURE, self._station_config.IS_AUTOEXPOSURE,
                                            self._station_config.LEFT,
                                            self._station_config.TOP,
                                            self._station_config.WIDTH,
                                            self._station_config.HEIGHT)

            self._operator_interface.print_to_console("Initialize Camera %s\n" %self._station_config.CAMERA_SN)
            the_equipment.init(self._station_config.CAMERA_SN)
            color_cal_id = the_equipment.get_colorcal_key(self._station_config.COLOR_CAL)
            scale_cal_id = the_equipment.get_imagescalecal_key(self._station_config.SCALE_CAL)
            shift_cal_id = the_equipment.get_colorshiftcal_key(self._station_config.SHIFT_CAL)
            rect = the_equipment._rect

            the_equipment.flush_measurement_setups()
            the_equipment.flush_measurements()
            the_equipment.prepare_for_run()

            self._operator_interface.print_to_console("Close the eliminator in the fixture... \n")
            self._fixture.elminator_off()

            centerlv_gls = []
            gls = []
            centercolordifference255 = 0.0
            attempts = 0

            for i in range(len(self._station_config.PATTERNS)):
                self._operator_interface.print_to_console(
                    "Panel Measurement Pattern: %s" %self._station_config.PATTERNS[i])
                # modified by elton . add random color
                # the_unit.display_color(self._station_config.COLORS[i])
                if isinstance(self._station_config.COLORS[i], tuple):
                    the_unit.display_color(self._station_config.COLORS[i])
                elif isinstance(self._station_config.COLORS[i], str):
                    the_unit.display_image(self._station_config.COLORS[i])

                if math.isnan(the_unit.vsync_microseconds()):
                    vsync_us = self._station_config.DEFAULT_VSYNC_US
                    exp_time_list = self._station_config.EXPOSURE[i]
                else:
                    vsync_us = the_unit.vsync_microseconds()
                    exp_time_list = self._station_config.EXPOSURE[i]
                    for exp_index in range(len(exp_time_list)):
                        exp_time_list[exp_index] = float(int(exp_time_list[exp_index]*1000.0/vsync_us)*vsync_us)/1000.0
                        self._operator_interface.print_to_console(
                                "\nAdjusted Timing in millesecond: %s\n" % exp_time_list[exp_index])

                the_equipment.measurementsetup(self._station_config.PATTERNS[i], exp_time_list[0],
                                               exp_time_list[1], exp_time_list[2], exp_time_list[2],
                                               self._station_config.FOCUS_DISTANCE, self._station_config.APERTURE,
                                               self._station_config.IS_AUTOEXPOSURE, rect, self._station_config.DISTANCE_UNIT,
                                               self._station_config.SPECTRAL_RESPONSE, self._station_config.ROTATION)
                the_equipment.setcalibrationid(self._station_config.PATTERNS[i],color_cal_id, scale_cal_id, shift_cal_id)
                imagekey = self._station_config.PATTERNS[i]
                flag = the_equipment.capture(self._station_config.PATTERNS[i], imagekey, self._station_config.IS_SAVEDB)
                self._operator_interface.print_to_console("\n".format(str(flag)))

                export_name = "{}_{}".format(serial_number, self._station_config.PATTERNS[i])
                output_dir = os.path.join(self._station_config.ROOT_DIR , self._station_config.ANALYSIS_RELATIVEPATH, the_unit.serial_number + '_' + test_log._start_time.strftime("%Y%m%d-%H%M%S"))
                if not os.path.exists(output_dir):
                    os.mkdir(output_dir,777)
                time.sleep(1)
                while attempts < 3:

                    try:
                        the_equipment.export_data(self._station_config.PATTERNS[i], output_dir, export_name)
                        break
                    except:
                        attempts += 1
                        self._operator_interface.print_to_console("\n try to export data for {} times\n".format(attempts))


                override = ''
                the_equipment.run_analysis_by_name(self._station_config.ANALYSIS[i], self._station_config.PATTERNS[i],
                                                   override)

                filename = export_name + ".csv "
                analysis_result = the_equipment.get_last_results()

                for r in analysis_result:
                    if '255' in self._station_config.PATTERNS[i] and 'Center Color (C' in r[0]:
                        test_item = str(self._station_config.PATTERNS[i] + "_" + r[0]).replace(" ", "")
                        self._operator_interface.print_to_console("\n" + test_item + ": \t" + r[2] + "\n")
                        test_log.set_measured_value_by_name(test_item, float(r[2]))
                    elif 'W' in self._station_config.PATTERNS[i] and 'CenterColorDifference'in r[0]:
                        if 'W255' in self._station_config.PATTERNS[i]:
                            centercolordifference255 = float(r[2])
                        else:
                            test_item = self._station_config.PATTERNS[i] + "_" + r[0]
                            test_value = abs(float(r[2])-centercolordifference255)
                            test_log.set_measured_value_by_name(test_item, test_value)
                    else:
                        for limit_array in self._station_config.STATION_LIMITS_ARRAYS:
                            test_item = self._station_config.PATTERNS[i] + "_" + r[0]
                            if limit_array[0] == test_item:
                                test_log.set_measured_value_by_name(test_item, float(r[2]))
                                break


                    if self._station_config.PATTERNS[i][0] == 'W' and self._station_config.PATTERNS[i][1:4] in self._station_config.GAMMA_CHECK_GLS and r[0] == 'CenterLv':
                        centerlv_gls.append(float(r[2]))
                        gls.append(float(self._station_config.PATTERNS[i][1:4]))


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

            norm_gls = np.log10([gl / max(gls) for gl in gls])
            norm_clv = np.log10([centerlv_gl / max(centerlv_gls) for centerlv_gl in centerlv_gls])
            gamma, cov = np.polyfit(norm_gls, norm_clv, 1, cov=False)
            test_log.set_measured_value_by_name("DISPLAY_GAMMA", gamma)

        except Exception, e:
            self._operator_interface.print_to_console("Test exception . {}".format(e.message))
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

            # SN-YYMMDDHHMMS-P.ttxm for pass unit and  SN-YYMMDDHHMMS-F.ttxm for failed
            if  self._station_config.RESTART_TEST_COUNT == 1\
                and self._station_config.IS_SAVEDB:
                dbfn = test_log.get_filename()
                if overall_result:
                    dbfn = re.sub('x.log', 'P.ttxm', test_log.get_filename())
                else:
                    dbfn = re.sub('x.log', 'F.ttxm', test_log.get_filename())
                self.backup_database(dbfn)

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

    def backup_database(self, dbfn, ismov = False):
        bak_dir = os.path.join(self._station_config.ROOT_DIR, self._station_config.DATABASE_RELATIVEPATH_BAK)
        if not os.path.exists(bak_dir):
            os.mkdir(bak_dir, 777)
        if ismov:
            shutil.move(os.path.join(self._station_config.ROOT_DIR, self._station_config.DATABASE_RELATIVEPATH),
                        os.path.join(bak_dir, dbfn))
        else:
            shutil.copyfile(os.path.join(self._station_config.ROOT_DIR, self._station_config.DATABASE_RELATIVEPATH),
                        os.path.join(bak_dir, dbfn))

    def force_restart(self):
        if not self._station_config.IS_SAVEDB:
            return False

        dbsize = os.path.getsize(os.path.join(self._station_config.ROOT_DIR, self._station_config.DATABASE_RELATIVEPATH))
        dbsize = dbsize / 1024  # kb
        dbsize = dbsize / 1024  # mb
        if self._station_config.RESTART_TEST_COUNT <= self._runningCount \
                or dbsize >= self._station_config.DB_MAX_SIZE:
            # dbfn = "{0}_{1}_autobak.ttxm".format(self._station_id, datetime.datetime.now().strftime("%y%m%d%H%M%S"))
            # self.backup_database(dbfn)
            self.close()
            self._operator_interface.print_to_console('database will be renamed automatically while software restarted next time.\n')
            return True

        return False

