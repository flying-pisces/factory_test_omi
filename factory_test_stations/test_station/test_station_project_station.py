import hardware_station_common.test_station.test_station as test_station
import test_station.test_fixture.test_fixture_project_station as test_fixture_project_station
import test_station.dut as dut


class projectstationError(Exception):
    pass


class projectstationStation(test_station.TestStation):
    """
        projectstation Station
    """

    def __init__(self, station_config, operator_interface):
        test_station.TestStation.__init__(self, station_config, operator_interface)
        self._fixture = test_fixture_project_station.projectstationFixture(station_config, operator_interface)
        self._overall_errorcode = ''
        self._first_failed_test_resulta = None


    def initialize(self):
        try:
            self._operator_interface.print_to_console("Initializing project station station...\n")
            self._fixture.initialize()
        except:
            raise

    def close(self):
        self._operator_interface.print_to_console("Close...\n")
        self._operator_interface.print_to_console("\there, I'm shutting the station down..\n")
        self._fixture.close()

    def _do_test(self, serial_number, test_log):
        self._overall_result = False
        self._overall_errorcode = ''

        the_unit = dut.projectDut(serial_number, self._station_config, self._operator_interface)
        self._operator_interface.print_to_console("Testing Unit %s\n" % the_unit.serial_number)
        try:

            ### implement tests here.  Note that the test name matches one in the station_limits file ###
            a_result = 1.1
            self._operator_interface.wait(a_result, "\n***********Testing Item 1 ***************\n")

            test_log.set_measured_value_by_name("TEST ITEM 1", a_result)
            self._operator_interface.print_to_console("Log the test item 1 value %f\n" % a_result)

            a_result = 1.4
            self._operator_interface.wait(a_result, "\n***********Testing Item 2 ***************\n")
            test_log.set_measured_value_by_name("TEST ITEM 2", a_result)
            self._operator_interface.print_to_console("Log the test item 2 value %f\n" % a_result)

            a_result = 1.8
            self._operator_interface.wait(a_result, "\n***********Testing Item 3 ***************\n")
            test_log.set_measured_value_by_name("TEST ITEM 3", a_result)
            self._operator_interface.print_to_console("Log the test item 3 value %f\n" % a_result)

        except projectstationError:
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
