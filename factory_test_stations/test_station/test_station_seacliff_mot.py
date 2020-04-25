import hardware_station_common.test_station.test_station as test_station
import test_station.test_fixture.test_fixture_seacliff_mot as test_fixture_seacliff_mot
from test_station.test_fixture.test_fixture_project_station import projectstationFixture
import test_station.test_equipment.test_equipment_seacliff_mot as test_equipment_seacliff_mot
import test_station.dut as dut
import time


class seacliffmotStationError(Exception):
    pass

class seacliffmotStation(test_station.TestStation):
    def __init__(self, station_config, operator_interface):
        test_station.TestStation.__init__(self, station_config, operator_interface)
        self._fixture = test_fixture_seacliff_mot.seacliffmotFixture(station_config, operator_interface)
        if station_config.FIXTURE_SIM:
            self._fixture = projectstationFixture(station_config, operator_interface)
        self._equipment = test_equipment_seacliff_mot.seacliffmotEquipment(station_config, operator_interface)
        self._overall_errorcode = ''
        self._first_failed_test_result = None

    def initialize(self):
        try:
            self._operator_interface.print_to_console("Initializing Seacliff MOT station...\n")
            self._fixture.initialize()
            self._equipment.initialize()
        except:
            raise

    def _close_fixture(self):
        if self._fixture is not None:
            try:
                self._operator_interface.print_to_console("Close...\n")
                self._fixture.status()
                self._fixture.elminator_off()
            finally:
                self._fixture.close()
                self._fixture = None

    def close(self):
        self._operator_interface.print_to_console("Close...\n")
        self._operator_interface.print_to_console("\there, I'm shutting the station down..\n")
        self._close_fixture()
        self._equipment.close()

    def _do_test(self, serial_number, test_log):
        self._overall_result = False
        self._overall_errorcode = ''
        self._fixture.load()
        the_unit = dut.pancakeDut(serial_number, self._station_config, self._operator_interface)
        if self._station_config.DUT_SIM:
            the_unit = dut.projectDut(serial_number, self._station_config, self._operator_interface)
        self._operator_interface.print_to_console("Testing Unit %s\n" % the_unit.serial_number)
        the_unit.initialize()
        self._operator_interface.print_to_console("Initialize DUT... \n")
        retries = 0
        is_screen_on = False
        try:
            the_unit.connect_display()

            the_unit.display_image(self._station_config.DISP_CHECKER_IMG_INDEX)

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

        except seacliffmotStationError:
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
        return True

        self._fixture.is_ready()
        timeout_for_dual = 5
        for idx in range(timeout_for_dual, 0, -1):
            self._operator_interface.prompt('Press the Dual-Start Btn in %s S...\n' % idx, 'yellow');
            time.sleep(1)

        self._operator_interface.print_to_console('Unable to get start signal from fixture.')
        self._operator_interface.prompt('', 'SystemButtonFace')
        raise test_station.TestStationSerialNumberError('Fail to Wait for press dual-btn ...')
