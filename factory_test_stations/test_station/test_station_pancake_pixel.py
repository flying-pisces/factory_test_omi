import hardware_station_common.test_station.test_station as test_station
import test_station.test_fixture.test_fixture_pancake_pixel as test_fixture_pancake_pixel
import test_station.test_equipment.test_equipment_pancake_pixel as test_equipment_pancake_pixel
import test_station.dut as dut
import hardware_station_common.test_station.test_station as test_station
import os
import shutil
import time
import math
import datetime
import re
import filecmp
import numpy as np

class pancakepixelError(Exception):
    pass


class pancakepixelStation(test_station.TestStation):
    """
        pancakepixel Station
    """

    def __init__(self, station_config, operator_interface):
        self._runningCount = 0
        test_station.TestStation.__init__(self, station_config, operator_interface)
        self._fixture = test_fixture_pancake_pixel.pancakepixelFixture(station_config, operator_interface)
        # self._equipment = test_equipment_pancake_pixel.pancakepixelEquipment(station_config, operator_interface)
        self._overall_errorcode = ''
        self._first_failed_test_result = None


    def initialize(self):
        try:
            self._operator_interface.print_to_console("Initializing station...\n")
            self._fixture.initialize()
            dbfn = os.path.join(self._station_config.ROOT_DIR, self._station_config.DATABASE_RELATIVEPATH)
            empytdb = os.path.join(self._station_config.ROOT_DIR, self._station_config.EMPTY_DATABASE_RELATIVEPATH)
            if self._station_config.RESTART_TEST_COUNT != 1 and\
                self._station_config.IS_SAVEDB and \
                    os.path.exists(dbfn) and not filecmp.cmp(dbfn, empytdb):
                dbfnbak = "{0}_{1}_autobak.ttxm".format(self._station_config.STATION_TYPE, datetime.datetime.now().strftime("%y%m%d%H%M%S"))
                self._operator_interface.print_to_console("backup ttxm raw database to {}...\n".format(dbfnbak))
                self.backup_database(dbfnbak, True)

            self._operator_interface.print_to_console("Empty ttxm raw database ...\n")
            shutil.copyfile(empytdb, dbfn)
        except:
            raise

    def close(self):
        self._operator_interface.print_to_console("Close...\n")
        self._operator_interface.print_to_console("\n..shutting the station down..\n")
        self._fixture.status()
        try:
            self._fixture.elminator_off()
            self._fixture.unload()
        finally:
            self._fixture.close()


    def _do_test(self, serial_number, test_log):
        self._overall_result = False
        self._overall_errorcode = ''
        #        self._operator_interface.operator_input("Manually Loading", "Please Load %s for testing.\n" % serial_number)
        self._fixture.elminator_on()
        self._fixture.load()
        '''
        # ttxm is occupy by process, can't override it correctly.
        if self._station_config.RESTART_TEST_COUNT == 1:
            self._operator_interface.print_to_console("Empty ttxm raw database ...\n")
            try:
                ttxmpth = os.path.join(self._station_config.ROOT_DIR, self._station_config.DATABASE_RELATIVEPATH)
                dirname = os.path.dirname(ttxmpth)
                shutil.rmtree(dirname)
                if not os.path.exists(dirname):
                    os.mkdir(dirname, 777)

                shutil.copyfile(
                    os.path.join(self._station_config.ROOT_DIR, self._station_config.EMPTY_DATABASE_RELATIVEPATH),
                    os.path.join(self._station_config.ROOT_DIR, self._station_config.DATABASE_RELATIVEPATH))
            except Exception, e:
                self._operator_interface.print_to_console("Fail to create new raw database.{}\n".format(e.message))
        '''
        try:
            self._operator_interface.print_to_console("Testing Unit %s\n" % serial_number)
            the_unit = dut.pancakeDut(serial_number, self._station_config, self._operator_interface)

            if not the_unit.initialize():
                self._fixture.powercycle_dut()
                starttime = datetime.datetime.now()
                while (datetime.datetime.now() - starttime) < datetime.timedelta(
                        seconds=self._station_config.DUT_MAX_WAIT_TIME):
                    self._operator_interface.print_to_console("\n\tWaiting for PTB to boot.......\n")
                    time.sleep(5)

            the_unit.connect_display(self._station_config.DISPLAY_CYCLE_TIME, self._station_config.LAUNCH_TIME)
            the_equipment = test_equipment_pancake_pixel.pancakepixelEquipment(self._station_config.IS_VERBOSE,
                                                                                         self._station_config.FOCUS_DISTANCE,
                                                                                         self._station_config.APERTURE,
                                                                                         self._station_config.IS_AUTOEXPOSURE,
                                                                                         self._station_config.LEFT,
                                                                                         self._station_config.TOP,
                                                                                         self._station_config.WIDTH,
                                                                                         self._station_config.HEIGHT)

            self._operator_interface.print_to_console("Initialize Camera %s\n" % self._station_config.CAMERA_SN)
            the_equipment.init(self._station_config.CAMERA_SN)
            color_cal_id = the_equipment.get_colorcal_key(self._station_config.COLOR_CAL)
            scale_cal_id = the_equipment.get_imagescalecal_key(self._station_config.SCALE_CAL)
            shift_cal_id = the_equipment.get_colorshiftcal_key(self._station_config.SHIFT_CAL)
            rect = the_equipment._rect

            the_equipment.flush_measurement_setups()
            the_equipment.flush_measurements()
            the_equipment.prepare_for_run()

            attempts = 0
            is_rawdata_save = True

            try:
                for i in range(len(self._station_config.PATTERNS)):
                    self._operator_interface.print_to_console(
                        "Panel Measurement Pattern: %s" % self._station_config.PATTERNS[i])

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
                            exp_time_list[exp_index] = float(
                                int(exp_time_list[exp_index] * 1000.0 / vsync_us) * vsync_us) / 1000.0
                            self._operator_interface.print_to_console(
                                "\nAdjusted Timing in millesecond: %s\n" % exp_time_list[exp_index])

                    the_equipment.measurementsetup(self._station_config.PATTERNS[i], exp_time_list[0],
                                                   exp_time_list[1], exp_time_list[2], exp_time_list[2],
                                                   self._station_config.FOCUS_DISTANCE, self._station_config.APERTURE,
                                                   self._station_config.IS_AUTOEXPOSURE, rect,
                                                   self._station_config.DISTANCE_UNIT,
                                                   self._station_config.SPECTRAL_RESPONSE, self._station_config.ROTATION)
                    the_equipment.setcalibrationid(self._station_config.PATTERNS[i], color_cal_id, scale_cal_id,
                                                   shift_cal_id)
                    imagekey = self._station_config.PATTERNS[i]
                    flag = the_equipment.capture(self._station_config.PATTERNS[i], imagekey, self._station_config.IS_SAVEDB)
                    self._operator_interface.print_to_console("\n".format(str(flag)))

                    export_name = "{}_{}".format(serial_number, self._station_config.PATTERNS[i])
                    output_dir = os.path.join(self._station_config.ROOT_DIR, self._station_config.ANALYSIS_RELATIVEPATH,
                                              the_unit.serial_number + '_' + test_log._start_time.strftime("%Y%m%d-%H%M%S"))
                    if not os.path.exists(output_dir):
                        os.mkdir(output_dir, 777)
                    time.sleep(1)
                    while attempts < 3:
                        try:
                            the_equipment.export_data(self._station_config.PATTERNS[i], output_dir, export_name)
                            break
                        except:
                            attempts += 1
                            self._operator_interface.print_to_console(
                                "\n try to export data for {} times\n".format(attempts))
                    is_rawdata_save = is_rawdata_save and os.path.exists(os.path.join(output_dir, export_name + '.npz'))
                    override = ''
                    the_equipment.run_analysis_by_name(self._station_config.ANALYSIS[i],
                                                       self._station_config.PATTERNS[i],
                                                       override)

                    analysis_result = the_equipment.get_last_results()

                    for r in list(analysis_result):
                        test_item = self._station_config.PATTERNS[i] + "_" + r[0]
                        test_log.set_measured_value_by_name(test_item, int(r[2]))

                test_log.set_measured_value_by_name("SaveRawImage_success", is_rawdata_save)
            except pancakepixelError:
                self._operator_interface.print_to_console("Non-parametric Test Failure\n")
                # return self.close_test(test_log)
            finally:
                the_equipment.uninit()
                the_unit.close()
                self._fixture.button_enable()
                # self.close_test(test_log)

        except Exception, e:
            self._operator_interface.print_to_console("Test exception . {}".format(e))

        self._fixture.unload()
        self._fixture.elminator_off()
        overall_result, first_failed_test_result = self.close_test(test_log)

        # SN-YYMMDDHHMMS-P.ttxm for pass unit and  SN-YYMMDDHHMMS-F.ttxm for failed
        if self._station_config.RESTART_TEST_COUNT == 1\
            and self._station_config.IS_SAVEDB:
            dbfn = test_log.get_filename()
            if overall_result:
                dbfn = re.sub('x.log', 'P.ttxm', test_log.get_filename())
            else:
                dbfn = re.sub('x.log', 'F.ttxm', test_log.get_filename())
            self.backup_database(dbfn)
        self._runningCount += 1
        self._operator_interface.print_to_console(r'--- do test finish ---')
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
        if self._station_config.RESTART_TEST_COUNT <= self._runningCount or dbsize >= self._station_config.DB_MAX_SIZE:
            # dbfn = "{0}_{1}_autobak.ttxm".format(self._station_id, datetime.datetime.now().strftime("%y%m%d%H%M%S"))
            # self.backup_database(dbfn)
            self._operator_interface.print_to_console('database will be renamed automatically while software restarted next time.')
            return True

        return False