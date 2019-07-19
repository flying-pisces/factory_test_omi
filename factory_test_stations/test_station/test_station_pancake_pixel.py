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

class pancakepixelError(Exception):
    pass


class pancakepixelStation(test_station.TestStation):
    """
        pancakepixel Station
    """

    def __init__(self, station_config, operator_interface):
        test_station.TestStation.__init__(self, station_config, operator_interface)
        self._fixture = test_fixture_pancake_pixel.pancakepixelFixture(station_config, operator_interface)
        self._equipment = test_equipment_pancake_pixel.pancakepixelEquipment(station_config, operator_interface)
        self._overall_errorcode = ''
        self._first_failed_test_result = None


    def initialize(self):
        try:
            self._operator_interface.print_to_console("Initializing station...\n")
            self._fixture.initialize()
            self._operator_interface.print_to_console("Empty ttxm raw database ...\n")
            shutil.copyfile(os.path.join(self._station_config.ROOT_DIR, self._station_config.EMPTY_DATABASE_RELATIVEPATH),
                            os.path.join(self._station_config.ROOT_DIR, self._station_config.DATABASE_RELATIVEPATH))
        except:
            raise

    def close(self):
        self._operator_interface.print_to_console("Close...\n")
        self._operator_interface.print_to_console("\n..shutting the station down..\n")
        self._fixture.status()
        self._fixture.unload()
        self._fixture.close()


    def _do_test(self, serial_number, test_log):
        self._overall_result = False
        self._overall_errorcode = ''
        #        self._operator_interface.operator_input("Manually Loading", "Please Load %s for testing.\n" % serial_number)
        self._fixture.load()

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
                    test_log.set_measured_value_by_name("SaveRawImage_success", is_rawdata_save)
            except pancakepixelError:
                self._operator_interface.print_to_console("Non-parametric Test Failure\n")
                # return self.close_test(test_log)
                test_log.set_measured_value_by_name("SaveRawImage_success", is_rawdata_save)
            finally:
                the_unit.close()
                self._fixture.button_enable()
                # self.close_test(test_log)

        except Exception, e:
            self._operator_interface.print_to_console("Test exception . {}".format(e))

        self._fixture.unload()
        overall_result, first_failed_test_result = self.close_test(test_log)

        # SN-YYMMDDHHMMS-P.ttxm for pass unit and  SN-YYMMDDHHMMS-F.ttxm for failed
        dbfn = ""
        if overall_result:
            dbfn = "{0}-{1}-P.ttxm".format(the_unit.serial_number, datetime.datetime.now().strftime("%y%m%d%H%M%S"))
        else:
            dbfn = "{0}-{1}-F.ttxm".format(the_unit.serial_number, datetime.datetime.now().strftime("%y%m%d%H%M%S"))

        shutil.copy(os.path.join(self._station_config.ROOT_DIR, self._station_config.DATABASE_RELATIVEPATH),
                    os.path.join(self._station_config.DATABASE_RELATIVEPATH_BAK, dbfn))
        return overall_result, first_failed_test_result

    def close_test(self, test_log):
        ### Insert code to gracefully restore fixture to known state, e.g. clear_all_relays() ###
        self._overall_result = test_log.get_overall_result()
        self._first_failed_test_result = test_log.get_first_failed_test_result()

        return self._overall_result, self._first_failed_test_result



    def is_ready(self):
        self._fixture.is_ready()
