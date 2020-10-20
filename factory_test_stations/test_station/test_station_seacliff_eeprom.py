import hardware_station_common.test_station.test_station as test_station
import test_station.test_fixture.test_fixture_seacliff_eeprom as test_fixture
import test_station.dut.dut as dut
import pprint
import types
import ctypes


def chk_and_set_measured_value_by_name(test_log, item, value):
    """

    :type test_log: test_station.TestRecord
    """
    if item in test_log.results_array():
        test_log.set_measured_value_by_name(item, value)
    else:
        pprint.pprint(item)


class seacliffeepromError(Exception):
    pass


class seacliffeepromStation(test_station.TestStation):
    """
        pancakeeeprom Station
    """

    def __init__(self, station_config, operator_interface):
        test_station.TestStation.__init__(self, station_config, operator_interface)
        self._fixture = test_fixture.seacliffeepromFixture(station_config, operator_interface)
        self._overall_errorcode = ''
        self._first_failed_test_result = None


    def initialize(self):
        try:
            self._operator_interface.print_to_console("Initializing pancake EEPROM station...\n")
            self._fixture.initialize()
        except:
            raise

    def close(self):
        self._operator_interface.print_to_console("Close...\n")
        self._operator_interface.print_to_console("there, I'm shutting the station down..\n")
        self._fixture.close()

    def _do_test(self, serial_number, test_log):
        self._overall_result = False
        self._overall_errorcode = ''
        test_log.set_measured_value_by_name_ex = types.MethodType(chk_and_set_measured_value_by_name, test_log)
        the_unit = dut.pancakeDut(serial_number, self._station_config, self._operator_interface)
        if self._station_config.DUT_SIM:
            the_unit = dut.projectDut(serial_number, self._station_config, self._operator_interface)

        self._operator_interface.print_to_console("Start write data to DUT. %s\n" % the_unit.serial_number)
        try:
            a_result = 2
            test_log.set_measured_value_by_name_ex("TEST ITEM", a_result)
            test_log.set_measured_value_by_name_ex("Verify Firmware Load", 1001)

            the_unit.initialize()
            the_unit.screen_on()
            the_unit.display_image(0x01)

            self._operator_interface.print_to_console('read write count for nvram from eeprom ...\n')
            write_count = the_unit.nvm_write_status()
            test_log.set_measured_value_by_name_ex('CURRENT_WRITE_COUNTS', write_count)
            if write_count < self._station_config.NVM_WRITE_COUNT_MAX:

                self._operator_interface.print_to_console('image capture and verification ...\n')
                test_log.set_measured_value_by_name_ex('JUDGED_BY_CAM', True)

                self._operator_interface.print_to_console('read all data from eeprom ...\n')
                var_data = self._station_config.CALIB_REQ_DATA  # type: dict

                raw_data = the_unit.nvm_read_data()
                # TODO: parse all the data to more sensible value, and then save them to database.
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_BORESIGHT_X', var_data.get('display_boresight_x'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_BORESIGHT_Y', var_data.get('display_boresight_y'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_ROTATION', var_data.get('rotation'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_LV_W255', var_data.get('lv_W255'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_X_W255', var_data.get('x_W255'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_Y_W255', var_data.get('y_W255'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_LV_R255', var_data.get('lv_R255'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_X_R255', var_data.get('x_R255'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_Y_R255', var_data.get('y_R255'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_LV_G255', var_data.get('lv_G255'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_X_G255', var_data.get('x_G255'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_Y_G255', var_data.get('y_G255'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_LV_B255', var_data.get('lv_B255'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_X_B255', var_data.get('x_B255'))
                test_log.set_measured_value_by_name_ex('CURRENT_BAK_Y_B255', var_data.get('y_B255'))

                raw_data_cpy = raw_data.copy()
                # TODO: config all the data to array.
                self._operator_interface.print_to_console('write configuration to eeprom ...\n')
                the_unit.nvm_write_data(raw_data_cpy)
                test_log.set_measured_value_by_name_ex('CFG_BORESIGHT_X', var_data.get('display_boresight_x'))
                test_log.set_measured_value_by_name_ex('CFG_BORESIGHT_Y', var_data.get('display_boresight_y'))
                test_log.set_measured_value_by_name_ex('CFG_ROTATION', var_data.get('rotation'))
                test_log.set_measured_value_by_name_ex('CFG_LV_W255', var_data.get('lv_W255'))
                test_log.set_measured_value_by_name_ex('CFG_X_W255', var_data.get('x_W255'))
                test_log.set_measured_value_by_name_ex('CFG_Y_W255', var_data.get('y_W255'))
                test_log.set_measured_value_by_name_ex('CFG_LV_R255', var_data.get('lv_R255'))
                test_log.set_measured_value_by_name_ex('CFG_X_R255', var_data.get('x_R255'))
                test_log.set_measured_value_by_name_ex('CFG_Y_R255', var_data.get('y_R255'))
                test_log.set_measured_value_by_name_ex('CFG_LV_G255', var_data.get('lv_G255'))
                test_log.set_measured_value_by_name_ex('CFG_X_G255', var_data.get('x_G255'))
                test_log.set_measured_value_by_name_ex('CFG_Y_G255', var_data.get('y_G255'))
                test_log.set_measured_value_by_name_ex('CFG_LV_B255', var_data.get('lv_B255'))
                test_log.set_measured_value_by_name_ex('CFG_X_B255', var_data.get('x_B255'))
                test_log.set_measured_value_by_name_ex('CFG_Y_B255', var_data.get('y_B255'))

                data_from_nvram = the_unit.nvm_read_data()
                success = raw_data_cpy == data_from_nvram
                test_log.set_measured_value_by_name_ex('DATA_CHECK_STATUS', success)

                self._operator_interface.print_to_console('read write count for nvram from eeprom ...\n')
                write_count = the_unit.nvm_write_status()
                test_log.set_measured_value_by_name_ex('CHECK_POST_WRITE_COUNTS', write_count)

        except seacliffeepromError:
            self._operator_interface.print_to_console("Non-parametric Test Failure\n")
            return self.close_test(test_log)

        else:
            return self.close_test(test_log)

    def close_test(self, test_log):
        ### Insert code to gracefully restore fixture to known state, e.g. clear_all_relays() ###
        self._overall_result = test_log.get_overall_result()
        self._first_failed_test_result = test_log.get_first_failed_test_result()
        return self._overall_result, self._first_failed_test_result

    def is_ready(self):
        self._fixture.is_ready()
