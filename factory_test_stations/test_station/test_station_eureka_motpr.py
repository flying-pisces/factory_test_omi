import time

import hardware_station_common.test_station.test_station as test_station
import test_station.test_fixture.test_fixture_eureka_motpr as test_fixture_eureka_motpr
import test_station.test_equipment.test_equipment_eureka_motpr as test_equipment_eureka_motpr
import test_station.dut.eureka_dut as dut_eureka_motpr
from hardware_station_common.utils.io_utils import round_ex
from test_station.test_fixture.test_fixture_project_station import projectstationFixture
import types
import re
import datetime
import os

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

            self._pr788 = test_equipment_eureka_motpr.EurekaMotPREquipment(station_config, operator_interface)

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
            test_log.set_measured_value_by_name_ex = types.MethodType(self.chk_and_set_measured_value_by_name, test_log)

            self._operator_interface.print_to_console("Testing Unit %s\n" % self._the_unit.serial_number)
            test_log.set_measured_value_by_name_ex('SW_VERSION', self._sw_version)

            ###fixture load


            ###dut init
            self._the_unit.initialize(com_port=self._station_config.DUT_COMPORT,
                                      eth_addr=self._station_config.DUT_ETH_PROXY_ADDR)

            ###pr788 ready
            self.set_log4pr788(test_log)
            self._pr788.initialize()

            test_log.set_measured_value_by_name_ex(f'Device_SN', self._pr788.deviceSerialNumber())
            test_log.set_measured_value_by_name_ex(f'Device_Model', self._pr788.deviceModel())
            test_log.set_measured_value_by_name_ex(f'Device_Firmware_Ver', self._pr788.deviceGetFirmwareVersion())

            ###dut screen on
            self._the_unit.screen_on()
            time.sleep(0.5)
            pre_color = None

            for p_name, pos, test_patterns in self._station_config.TEST_POSITIONS:
                self._operator_interface.print_to_console(f'Mov to test position {p_name}_{pos}. \n')
                for pattern in test_patterns:
                    self._operator_interface.print_to_console(f'start to test pattern {p_name}_{pattern}. \n')
                    info = self._station_config.TEST_PATTERNS.get(pattern)
                    color_code = info['P']
                    if pre_color != color_code:
                        self._operator_interface.print_to_console('Set DUT To Color: {}.\n'.format(color_code))
                        if isinstance(color_code, tuple):
                            self._the_unit.display_color(color_code)
                        elif isinstance(color_code, (str, int)):
                            self._the_unit.display_image(color_code)
                        pre_color = color_code

                        time.sleep(0.5)
                        measure_array = []

                        if not self._station_config.PR788_Config['Auto_Exposure'] and 'exposure' in info.keys():
                            self._pr788.deviceExposure(info.get('exposure'))

                        for c in range(self._station_config.SMOOTH_COUNT):
                            lum, x, y = self._pr788.deviceMeasure(test_equipment_eureka_motpr.MeasurementData.New.value)
                            expsure = self._pr788.deviceLastMeasurementInfo()
                            measure_array.append((lum, x, y, expsure[3]))

                        lum = sum([lum for lum, __, __, __ in measure_array]) / len(measure_array)
                        x = sum([x for __, x, __, __ in measure_array]) / len(measure_array)
                        y = sum([y for __, __, y, __ in measure_array]) / len(measure_array)
                        exposure = round(sum([z for __, __, __, z in measure_array]) / len(measure_array), 2)
                        test_log.set_measured_value_by_name_ex(f'{p_name}_{pattern}_OnAxis Lum', lum)
                        test_log.set_measured_value_by_name_ex(f'{p_name}_{pattern}_OnAxis x', x)
                        test_log.set_measured_value_by_name_ex(f'{p_name}_{pattern}_OnAxis y', y)
                        test_log.set_measured_value_by_name_ex(f'{p_name}_{pattern}_Exposure', exposure)
                        if self._station_config.SPECTRAL_MEASURE and info.get('spectral') is True:
                            self.spectral_test(test_log, pattern_name=pattern)

            self._the_unit.screen_off()

        except EurekaMotPRError:
            pass
            # self._the_unit.close()
            # self._operator_interface.print_to_console("Non-parametric Test Failure\n")
            #return self.close_test(test_log)

        finally:
            self._the_unit.close()
            self._pr788.close()
            return self.close_test(test_log)

    def close_test(self, test_log):
        ### Insert code to gracefully restore fixture to known state, e.g. clear_all_relays() ###
        self._overall_result = test_log.get_overall_result()
        self._first_failed_test_result = test_log.get_first_failed_test_result()
        return self._overall_result, self._first_failed_test_result

    def is_ready(self):
        # self._fixture.is_ready()
        return True

    def login(self, active, usr, pwd):
        self._operator_interface.print_to_console(f'Login to system: {usr} , active={active}\n')
        self._operator_interface.update_root_config({
            'IsUsrLogin': str(active)
        })
        return True

    def spectral_test(self, test_log, pattern_name):
        '''
        test spectral and write test log to file
        :param test_log:
        :param pattern_name:
        :return:
        '''
        uni_file_name = re.sub('_x.log', '', test_log.get_filename())
        capture_path = os.path.join(self._station_config.PR788_Config['Log_Path'], uni_file_name)
        file_path = os.path.join(capture_path, f'{pattern_name}.raw')
        if not os.path.exists(capture_path):
            test_station.utils.os_utils.mkdir_p(capture_path)
            os.chmod(capture_path, 0o777)
        spectralData = self._pr788.deviceSpectralMeasure(test_equipment_eureka_motpr.MeasurementData.New.value)
        spectralData = spectralData.replace('\n', '')
        with open(file_path, 'w') as f:
            f.write(spectralData)

    def set_log4pr788(self, test_log):
        uni_file_name = re.sub('_x.log', '', test_log.get_filename())
        capture_path = os.path.join(self._station_config.PR788_Config['Log_Path'], uni_file_name)
        file_path = os.path.join(capture_path, 'pr788.txt')
        if not os.path.exists(capture_path):
            test_station.utils.os_utils.mkdir_p(capture_path)
            os.chmod(capture_path, 0o777)

        self._pr788.deviceOpenLog(file_path)

