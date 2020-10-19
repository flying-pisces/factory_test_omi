import hardware_station_common.test_station.test_station as test_station
import test_station.test_fixture.test_fixture_seacliff_eeprom as test_fixture
import test_station.dut.dut as dut
import pprint
import types


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
        self._operator_interface.print_to_console("Start write data to DUT. %s\n" % the_unit.serial_number)
        try:
            a_result = 2
            test_log.set_measured_value_by_name_ex("TEST ITEM", a_result)

            test_log.set_measured_value_by_name_ex("Verify Firmware Load", 1001)

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
