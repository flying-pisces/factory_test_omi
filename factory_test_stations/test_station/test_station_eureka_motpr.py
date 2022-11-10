import subprocess
import time

import hardware_station_common.test_station.test_station as test_station
import test_station.test_fixture.test_fixture_eureka_motpr as test_fixture_eureka_motpr
import test_station.test_equipment.test_equipment_eureka_motpr as test_equipment_eureka_motpr
import test_station.dut.eureka_dut as dut_eureka_motpr
from hardware_station_common.utils.io_utils import round_ex
from test_station.test_fixture.test_fixture_project_station import projectstationFixture
#from ..shop_floor_interface import shop_floor_sunny_motpr as mes_motpr
from hardware_station_common.test_station.test_log.shop_floor_interface.shop_floor import ShopFloor

import types
import re
import datetime
import os
import json

class EurekaMotPRError(Exception):
    pass


class EurekaMotPRStation(test_station.TestStation):
    """
        EurekaMotPR Station
    """

    def auto_find_com_ports(self):
        import serial.tools.list_ports
        import serial
        from pymodbus.client.sync import ModbusSerialClient
        from pymodbus.register_read_message import ReadHoldingRegistersResponse

        # <editor-fold desc="port configuration automatically">
        cfg = 'station_config_eureka_motpr.json'
        station_config = {
            'FixtureCom': 'Fixture',
            'ParticleCounter': 'ParticleCounter',
        }
        com_ports = list(serial.tools.list_ports.comports())
        port_list = [(com.device, com.hwid, com.serial_number, com.description)
                     for com in com_ports if com.serial_number]
        if not os.path.exists(cfg):
            station_config['PORT_LIST'] = port_list
            with open(cfg, 'w') as f:
                json.dump(station_config, fp=f, indent=4)
        else:
            with open(cfg, 'r') as f:
                station_config = json.load(f)

        port_err_message = []
        if not self._station_config.FIXTURE_SIM and not self._station_config.IS_PROXY_COMMUNICATION:
            # config the port for fixture
            regex_port = station_config['FixtureCom']
            com_ports = [c[0] for c in port_list if re.search(regex_port, c[2], re.I | re.S)]
            if len(com_ports) != 1:
                port_err_message.append(f'Fixture')
            else:
                self.fixture_port = com_ports[-1]

        # config the port for scanner
        if self._station_config.FIXTURE_PARTICLE_COUNTER:
            regex_port = station_config['ParticleCounter']
            com_ports = [c[0] for c in port_list if re.search(regex_port, c[2], re.I | re.S)]
            if len(com_ports) == 1:
                self.fixture_particle_port = com_ports[-1]
            else:
                port_err_message.append(f'Particle counter')
        # </editor-fold>

        if not self._station_config.FIXTURE_SIM and len(port_err_message) > 0:
            raise EurekaMotPRError(f'Fail to find ports for fixture {";".join(port_err_message)}')


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
            self._latest_serial_number = None
            self._module_left_or_right = 'L'
            self._is_exit = False
            self._shop_floor: ShopFloor = None
            self._ng_continually_msg = []
            self._dut_light_on = False
            self._err_msg_list = {
                1: 'Axis X running error / X轴电机运动异常',
                2: 'Axis Y running error / Y轴电机运动异常',
                3: 'Axis A running error / A轴电机运动异常',
                4: 'Axis Z running error / Z轴电机运动异常',
                5: 'Signal from sensor (pressing plate) is not triggered / DUT盖板未盖上',
                6: 'Signal from sensor (Grating) is not triggered / 安全光栅信号被触发',
                7: 'Signal from sensor (Fixture Door) is not triggered / 治具门未关闭',
                8: 'This command is cancel by operator / 用户取消',
                9: 'Fixture is under warning status / 治具报警状态',
                10: 'Signal from sensor (DUT Door) is not triggered / DUT门气缸异常',
                11: 'Signal from sensor (Axis Z for equipment) is not triggered / Z轴相机支持气缸信号异常',
                12: 'Signal from sensor (Hold DUT on) is not triggered / DUT 夹紧信号异常',
                13: 'Signal from sensor (Raise DUT up or down) is not triggered / DUT升降信号异常',
                14: 'Signal from sensor (DUT pogo pin) is not triggered / DUT Pogo Pin 气缸信号异常',
                15: 'Signal from sensor (DUT Door) is not triggered / DUT 开门信号异常',
                151: 'Signal from sensor ( Door ) is error / DUT开门Sensor异常',
                152: 'Signal from sensor ( Door ) is error / DUT关门Sensor异常',
                16: 'Warning for vacuum / 真空吸信号异常',
                17: 'A Axis out of stroke / A 轴电机超过行程',
                18: 'Z Axis out of stroke / Z 轴电机超过行程',
            }
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

            if self._station_config.AUTO_CFG_COMPORTS:
                self.auto_find_com_ports()
            else:
                self.fixture_particle_port = self._station_config.FIXTURE_PARTICLE_COMPORT

            if hasattr(self._station_config, "FIXTURE_SIM") and self._station_config.FIXTURE_SIM:
                self._fixture.initialize()
            else:
                self.fixture_port = self._station_config.FIXTURE_COMPORT
                self.fixture_particle_port = self._station_config.FIXTURE_PARTICLE_COMPORT

                self._fixture.initialize(fixture_port=self.fixture_port,
                                         particle_port=self.fixture_particle_port,
                                         proxy_port=self._station_config.PROXY_ENDPOINT)

                self._fixture.start_button_status(True)
                self._fixture.power_on_button_status(True)
                self._fixture.vacuum(True)
                if not self._station_config.FIXTURE_SIM and self.alert_handle(self._fixture.unload) != 0:
                    raise EurekaMotPRError(f'Fail to init the fixture.')
                #self.alert_handle(self._fixture.unload_dut)
                self._fixture.start_button_status(False)
                self._fixture.power_on_button_status(False)
                self._fixture.vacuum(False)


        except test_fixture_eureka_motpr.EurekaMotPRFixtureError as e:
            raise e

    def close(self):
        self._is_exit = True
        self._operator_interface.print_to_console("Close...\n")
        self._operator_interface.print_to_console("\there, I'm shutting the station down..\n")
        self._fixture.close()
        mes_exe = os.system(f"tasklist|findstr \"{self._station_config.MES_HELPER_EXE}\"")
        if mes_exe == 0:
            subprocess.Popen(f'taskkill /f /im {self._station_config.MES_HELPER_EXE}.exe')

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


        try:
            ###pr788 ready
            self.set_log4pr788(test_log)
            self._pr788.initialize()

            self._operator_interface.print_to_console("Testing Unit %s\n" % self._the_unit.serial_number)
            self._operator_interface.print_to_console("Initialize DUT... \n")
            test_log.set_measured_value_by_name_ex = types.MethodType(self.chk_and_set_measured_value_by_name, test_log)
            test_log.set_measured_value_by_name_ex('SW_VERSION', self._sw_version)
            sw_ver = f"{self._station_config.SW_VERSION if hasattr(self._station_config, 'SW_VERSION') else 'UNKNOW'}"
            test_log.set_measured_value_by_name_ex(f'SW_Version', sw_ver)

            test_log.set_measured_value_by_name_ex(f'STATION_SN', self._fixture.id())

            if self._dut_light_on:

                self._fixture.load()

                alignment_result = self._fixture.alignment(self._latest_serial_number)
                if isinstance(alignment_result, tuple):
                    self._module_left_or_right = str(alignment_result[4]).upper()
                else:
                    raise test_fixture_eureka_motpr.EurekaMotPRFixtureError(f'Alignment Err')
                # self._fixture.mov_abs_xya(-2410, -110144, 0.8982583241681447)
                # self._fixture._alignment_pos = (-2410, -110144, 0.8982583241681447, 269)

                is_query_temp = (hasattr(self._station_config, 'QUERY_DUT_TEMP_PER_PATTERN')
                                 and self._station_config.QUERY_DUT_TEMP_PER_PATTERN
                                 and not self._station_config.FIXTURE_SIM)

                test_log.set_measured_value_by_name_ex(f'Device_SN', self._pr788.deviceSerialNumber())
                test_log.set_measured_value_by_name_ex(f'Device_Model', self._pr788.deviceModel())
                test_log.set_measured_value_by_name_ex(f'EQUIP_VERSION', self._pr788.deviceGetFirmwareVersion())

                particl_counter = 0
                if hasattr(self._station_config, "FIXTURE_PARTICLE_COUNTER") and self._station_config.FIXTURE_PARTICLE_COUNTER:
                    particl_counter = self._fixture.particle_counter_read_val()
                    print("----------------particlecounter: {}".format(particl_counter))

                test_log.set_measured_value_by_name_ex(f'ENV_ParticleCounter', particl_counter)

                pre_color = None
                W255_LUM = 0
                W000_LUM = 1

                for p_name, pos, test_patterns in self._station_config.TEST_POSITIONS:
                    self._operator_interface.print_to_console(f'Mov to test position {p_name}_{pos}. \n')
                    if not self._station_config.FIXTURE_SIM:
                        if not self._station_config.IS_PROXY_COMMUNICATION:
                            self._fixture.mov_abs_xya(int(pos[0]), int(pos[1]), 0)

                    distance = self._fixture.calib_zero_pos()
                    self._fixture.mov_camera_z(int(distance) - pos[2])
                    time.sleep(2)

                    test_log.set_measured_value_by_name_ex(f'DUT_ModuleType', self._module_left_or_right)

                    for pattern in test_patterns:
                        self._operator_interface.print_to_console(f'start to test pattern {p_name}_{pattern}. \n')
                        info = self._station_config.TEST_PATTERNS.get(pattern)
                        color_code = info['P']
                        if 'Bool_TEST' in info.keys() and not info['Bool_TEST']:
                            test_log.set_measured_value_by_name_ex(f'{p_name}_{pattern}_OnAxis Lum', 0)
                            test_log.set_measured_value_by_name_ex(f'{p_name}_{pattern}_TEMPERATURE', 0)
                            continue
                        if pre_color != color_code:
                            self._operator_interface.print_to_console('Set DUT To Color: {}.\n'.format(color_code))
                            if isinstance(color_code, tuple):
                                self._the_unit.display_color(color_code)
                            elif isinstance(color_code, dict):
                                self._the_unit.display_image(color_code[self._module_left_or_right])
                            pre_color = color_code
                        dut_temp = 30
                        if is_query_temp:
                            self._operator_interface.print_to_console(f'query temperature for {p_name}_{pattern}\n')
                            dut_temp = self._fixture.query_temp(test_fixture_eureka_motpr.QueryTempParts.UUTNearBy)

                        test_log.set_measured_value_by_name_ex(f'{p_name}_{pattern}_TEMPERATURE', dut_temp)

                        time.sleep(0.5)
                        measure_array = []
                        exposure_time = 0
                        if not self._station_config.PR788_Config['Auto_Exposure'] and 'exposure' in info.keys():
                            exposure_time = info.get('exposure')
                        self._pr788.deviceExposure(exposure_time)
                        self._pr788.deviceSetFrequency(self._station_config.PR788_Config['Frequency'])

                        for c in range(self._station_config.SMOOTH_COUNT):
                            lum, x, y = self._pr788.deviceMeasure(test_equipment_eureka_motpr.MeasurementData.New.value)
                            expsure = self._pr788.deviceLastMeasurementInfo()
                            measure_array.append((lum, x, y, expsure[3]))

                        lum = sum([lum for lum, __, __, __ in measure_array]) / len(measure_array)
                        if not isinstance(color_code, dict):
                            x = sum([x for __, x, __, __ in measure_array]) / len(measure_array)
                            y = sum([y for __, __, y, __ in measure_array]) / len(measure_array)
                            exposure = round(sum([z for __, __, __, z in measure_array]) / len(measure_array), 2)
                            test_log.set_measured_value_by_name_ex(f'{p_name}_{pattern}_OnAxis Lum', lum)
                            test_log.set_measured_value_by_name_ex(f'{p_name}_{pattern}_OnAxis x', x)
                            test_log.set_measured_value_by_name_ex(f'{p_name}_{pattern}_OnAxis y', y)
                            test_log.set_measured_value_by_name_ex(f'{p_name}_{pattern}_Exposure', exposure)
                        else:
                            if pattern == 'CW255':
                                W255_LUM = lum
                            elif pattern == 'CW000':
                                W000_LUM = lum
                            test_log.set_measured_value_by_name_ex(f'{p_name}_{pattern}_OnAxis Lum', lum)

                        if self._station_config.SPECTRAL_MEASURE and info.get('spectral') is True:
                            self.spectral_test(test_log, pattern_name=pattern)

                test_log.set_measured_value_by_name_ex(f'Nominal_OnAxisContrast', round(W255_LUM / W000_LUM, 2))

                test_log.set_measured_value_by_name_ex(f'ERR_FIXTURE', False)
                test_log.set_measured_value_by_name_ex(f'ERR_EQUIPMENT', False)
                test_log.set_measured_value_by_name_ex(f'ERR_DUT', False)

            else:
                test_log.set_measured_value_by_name_ex(f'ERR_DUT', True)

        except test_equipment_eureka_motpr.EurekaMotPREquipmentError as e:
            self._operator_interface.print_to_console(f'EQUIPMENT ERR: {str(e)}')
            test_log.set_measured_value_by_name_ex(f'ERR_EQUIPMENT', True)

        except test_fixture_eureka_motpr.EurekaMotPRFixtureError as e:
            self._operator_interface.print_to_console(f'FIXTURE ERR: {str(e)}')
            test_log.set_measured_value_by_name_ex(f'ERR_FIXTURE', True)

        except dut_eureka_motpr.EurekaDUTError as e:
            self._operator_interface.print_to_console(f'DUT ERR: {str(e)}')
            test_log.set_measured_value_by_name_ex(f'ERR_DUT', True)

        except Exception as e:
            self._operator_interface.print_to_console(f'Other ERR: {str(e)}')

        finally:
            self._the_unit.screen_off()
            self._fixture.unload()
            time.sleep(0.5)
            self._the_unit.close()
            self._pr788.close()
            res = self.close_test(test_log)
            if self._station_config.NG_CONTINUALLY_ENABLE:
                if (len(self._ng_continually_msg) >= 3
                        and len(set(self._ng_continually_msg)) == 1 and self._ng_continually_msg[-1] != 0):
                    self._operator_interface.operator_input(title=f'建议联系TE:', msg=f'failures [{self._ng_continually_msg[-1]}] come out continuously for more than 3 times.')

            return res

    def close_test(self, test_log):
        ### Insert code to gracefully restore fixture to known state, e.g. clear_all_relays() ###
        self._overall_result = test_log.get_overall_result()
        self._first_failed_test_result = test_log.get_first_failed_test_result()
        if not self._overall_result:
            self._ng_continually_msg.append(self._first_failed_test_result.get_unique_id())
        else:
            self._ng_continually_msg.append(0)
        #self._ng_continually_msg = self._ng_continually_msg[-4:-1]
        return self._overall_result, self._first_failed_test_result

    def validate_sn(self, serial_num):
        self._latest_serial_number = serial_num
        return test_station.TestStation.validate_sn(self, serial_num)

    def is_ready(self):
        if self._station_config.DUT_SIM:
            self._the_unit = dut_eureka_motpr.projectDut(self._latest_serial_number, self._station_config, self._operator_interface)
        else:
            self._the_unit = dut_eureka_motpr.EurekaDut(self._latest_serial_number, self._station_config, self._operator_interface)

        ###dut init
        self._the_unit.initialize(com_port=self._station_config.DUT_COMPORT,
                                      eth_addr=self._station_config.DUT_ETH_PROXY_ADDR)

        if not self._is_ready_check():
            self._operator_interface.print_to_console(f'--------------------> {self._latest_serial_number}\n')
            self._fixture.start_button_status(False)
            self._operator_interface.prompt('Scan or type the DUT Serial Number', 'SystemButtonFace')
            raise test_station.TestStationSerialNumberError('Station not ready.')
        self._operator_interface.prompt('', 'SystemButtonFace')
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


    def _is_ready_check(self):
        serial_number = self._latest_serial_number
        self._operator_interface.print_to_console("Check Unit %s is ready?\n" % serial_number)
        retry_times = 0
        ready = False
        timeout_for_dual = time.time()
        self._dut_light_on = False
        try:
            self._fixture.flush_data()
            #self._fixture.start_button_status(True)
            self._fixture.power_off_button_status(True)
            time.sleep(self._station_config.FIXTURE_SOCK_DLY)
            ##扫码-->放置产品盖上盖板-->检测盖板是否盖上-->点亮产品-->使能双启动按钮
            #   |                                          |
            #   ^------------------------------------------|
            #                       取消测试
            while not ready or not self._dut_light_on:
                if not self._dut_light_on:
                    coverBoard_status = self._fixture.get_cover_board_status()
                    self._operator_interface.print_to_console("Check coverboard status: {}......\n".format(coverBoard_status))
                    if coverBoard_status == 0:
                        ###disable vacuum
                        self._fixture.vacuum(False)
                        ### cover board is covered
                        ###dut screen on
                        if self._the_unit.screen_on():
                            self._fixture.start_button_status(True)
                            self._dut_light_on = True
                        else:
                            ## if screen is not on ,screen off
                            self._the_unit.screen_off()
                            self._operator_interface.operator_input(title=f'ERROR:',
                                                                        msg=f'产品点亮失败......')
                            self._dut_light_on = False
                            self._fixture.power_off_button_status(False)
                            return True
                    else:
                        continue

                msg_prompt = 'Load DUT, and then Press Start-Btn (Lit up) in %s S...'
                self._operator_interface.prompt(msg_prompt % int(time.time() - timeout_for_dual), 'yellow')
                if True in [self._station_config.DUT_LOAD_WITHOUT_OPERATOR, self._station_config.FIXTURE_SIM]:
                    ready_status = (0x00, 00)
                else:
                    ready_status = self._fixture.is_ready()
                if isinstance(ready_status, tuple) and len(ready_status) == 0x02:
                    ready_status, ready_code = ready_status
                    if ready_status in [0x00] and ready_code == 0:
                        ready = True
                    elif ready_status == 0x00 and ready_code in self._err_msg_list:
                        self._operator_interface.print_to_console(
                            f'Please note: {self._err_msg_list.get(ready_code)}.\n', 'red')
                        self.alert_handle(ready_code)
                    elif ready_status == 0x02:
                        self._the_unit.screen_off()
                        self._fixture.power_off_button_status(False)
                        self._operator_interface.print_to_console('Cancel testing...')
                        break
                time.sleep(0.05)
        except Exception as e:
            self._operator_interface.print_to_console(f'Exception _query_dual_start_v2 ----> {str(e)}')

        return ready

    def alert_handle(self, func):
        if callable(func):
            alert_res = func()
        else:
            alert_res = func
        while alert_res not in [0x00, None] and not self._is_exit:
            if alert_res in [6, 7]:
                self._operator_interface.operator_input('Hint', self._err_msg_list.get(alert_res), msg_type='warning')
                alert_res = self._fixture.reset()
                self._is_cancel_test_by_op = True
            else:
                self._operator_interface.print_to_console(
                    f'Please note --> {alert_res}: {self._err_msg_list.get(alert_res)}.\n', 'red')
                if callable(func):
                    if alert_res in [12, 13, 14]:
                        self._fixture.unload_dut()
                    self._operator_interface.operator_input(
                        'Hint', f'Please note --> {alert_res}: {self._err_msg_list.get(alert_res)}.\n',
                        msg_type='warning')
                    alert_res = func()
                else:
                    break
        return alert_res