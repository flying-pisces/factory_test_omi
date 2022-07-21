import time

import hardware_station_common.test_station.test_station as test_station
import test_station.test_fixture.test_fixture_eureka_motpr as test_fixture_eureka_motpr
import test_station.dut.eureka_dut as dut_eureka_motpr
from hardware_station_common.utils.io_utils import round_ex
from test_station.test_fixture.test_fixture_project_station import projectstationFixture
import types

class EurekaMotPRError(Exception):
    pass


class EurekaMotPRStation(test_station.TestStation):
    """
        EurekaMotPR Station
    """

    def __init__(self, station_config, operator_interface):
        test_station.TestStation.__init__(self, station_config, operator_interface)
        try:
            self._fixture = test_fixture_eureka_motpr.EurekaMotPRFixture(station_config, operator_interface)
            if hasattr(station_config, 'FIXTURE_SIM') and station_config.FIXTURE_SIM:
                self._fixture = projectstationFixture(station_config, operator_interface)
            self._overall_errorcode = ''
            self._first_failed_test_result = ''
            self._sw_version = '0.0.0'
        except Exception as e:
            print(str(e))

    def initialize(self):
        try:
            self._operator_interface.update_root_config(
                {
                    'IsScanCodeAutomatically': 'False',
                    'ShowLogin': 'True',
                })
            self._operator_interface.print_to_console("Initializing eureka MotPR station...\n")
            self._fixture.initialize()
        except:
            raise

    def close(self):
        self._operator_interface.print_to_console("Close...\n")
        self._operator_interface.print_to_console("\there, I'm shutting the station down..\n")
        self._fixture.close()

    def chk_and_set_measured_value_by_name(self, test_log, item, value, value_msg=None):
        """
        :type test_log: test_station.TestRecord
        """
        exp_format_dic = {
            'OnAxis Lum': 1, 'OnAxis x': 4, 'OnAxis y': 4,
            'Lum_Ratio>0.7MaxLum_30deg': 2, "u'v'_delta_to_OnAxis_30deg": 4,
            "DispCen_x_display": 1, "DispCen_y_display": 1, "Disp_Rotate_x": 2,
            'R_x_corrected': 4, 'R_y_corrected': 4,
            'G_x_corrected': 3, 'G_y_corrected': 4,
            'B_x_corrected': 3, 'B_y_corrected': 4,
            'Instantaneous % of On-axis': 3,
        }
        if item in test_log.results_array():
            test_log.set_measured_value_by_name(item, value)
            did_pass = test_log.get_test_by_name(item).did_pass()
            if value_msg is None:
                value_msg = value
                disp_format = [(k, v) for k, v in exp_format_dic.items() if k in item]
                if any(disp_format) and isinstance(value, float):
                    value_msg = round_ex(value, disp_format[0][1])
            if hasattr(self._operator_interface, 'update_test_value'):
                self._operator_interface.update_test_value(item, value_msg, 1 if did_pass else -1)

    def _do_test(self, serial_number, test_log):
        self._overall_result = False
        self._overall_errorcode = ''
        if self._station_config.DUT_SIM:
            self._the_unit = dut_eureka_motpr.projectDut(serial_number, self._station_config, self._operator_interface)
        else:
            self._the_unit = dut_eureka_motpr.EurekaDut(serial_number, self._station_config, self._operator_interface)

        self._operator_interface.print_to_console("Testing Unit %s\n" % self._the_unit.serial_number)
        try:
            self._operator_interface.print_to_console("Testing Unit %s\n" % self._the_unit.serial_number)
            self._operator_interface.print_to_console("Initialize DUT... \n")
            time.sleep(1)
            test_log.set_measured_value_by_name_ex = types.MethodType(self.chk_and_set_measured_value_by_name, test_log)

            self._operator_interface.print_to_console("Testing Unit %s\n" % self._the_unit.serial_number)
            test_log.set_measured_value_by_name_ex('SW_VERSION', self._sw_version)

            test_log.set_measured_value_by_name_ex('Nominal_W255_OnAxis Lum', 119.2)
            test_log.set_measured_value_by_name_ex('Nominal_W255_OnAxis x', 0.33)
            test_log.set_measured_value_by_name_ex('Nominal_W255_OnAxis y', 0.34)

            test_log.set_measured_value_by_name_ex('Nominal_R255_OnAxis Lum', 28)
            test_log.set_measured_value_by_name_ex('Nominal_R255_OnAxis x', 0.62)
            test_log.set_measured_value_by_name_ex('Nominal_R255_OnAxis y', 0.34)

            test_log.set_measured_value_by_name_ex('Nominal_G255_OnAxis Lum', 72)
            test_log.set_measured_value_by_name_ex('Nominal_G255_OnAxis x', 0.32)
            test_log.set_measured_value_by_name_ex('Nominal_G255_OnAxis y', 0.58)

            test_log.set_measured_value_by_name_ex('Nominal_B255_OnAxis Lum', 11)
            test_log.set_measured_value_by_name_ex('Nominal_B255_OnAxis x',  0.18)
            test_log.set_measured_value_by_name_ex('Nominal_B255_OnAxis y', 0.04)

        except EurekaMotPRError:
            self._the_unit.close()
            self._operator_interface.print_to_console("Non-parametric Test Failure\n")
            return self.close_test(test_log)

        else:
            self._the_unit.close()
            return self.close_test(test_log)

    def close_test(self, test_log):
        ### Insert code to gracefully restore fixture to known state, e.g. clear_all_relays() ###
        self._overall_result = test_log.get_overall_result()
        self._first_failed_test_result = test_log.get_first_failed_test_result()
        return self._overall_result, self._first_failed_test_result

    def is_ready(self):
        self._fixture.is_ready()

    def login(self, active, usr, pwd):
        self._operator_interface.print_to_console(f'Login to system: {usr} , active={active}\n')
        self._operator_interface.update_root_config({
            'IsUsrLogin': str(active)
        })
        return True
