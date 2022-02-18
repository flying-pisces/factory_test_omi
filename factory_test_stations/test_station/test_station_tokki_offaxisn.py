import hardware_station_common.test_station.test_station as test_station
import numpy as np
import os
import shutil
import time
import math
import datetime
import re
import filecmp
import test_station.dut as dut
from test_station.test_fixture.test_fixture_tokki_offaxisn import TokkiOffAxisNFixture, TokkiOffAxisNFixtureError
from test_station.test_fixture.test_fixture_project_station import projectstationFixture
from test_station.test_equipment.test_equipment_tokki_offaxisn import TokkiOffAxisNEquipment
from test_station.dut.dut import projectDut, DUTError
import hardware_station_common.utils as hsc_utils
import hardware_station_common.utils.io_utils as io_utils
import types
import glob
import sys
import shutil
import serial
import json


class TokkiOffAxisNStationError(Exception):
    pass


class TokkiOffAxisNStation(test_station.TestStation):
    """
            pancakeoffaxis Station
        """

    def __init__(self, station_config, operator_interface):
        self._sw_version = '3.0.0'
        self._runningCount = 0
        test_station.TestStation.__init__(self, station_config, operator_interface)
        self._fixture = projectstationFixture(station_config, operator_interface)
        if not station_config.FIXTURE_SIM:
            self._fixture = TokkiOffAxisNFixture(station_config, operator_interface)  # type: TokkiOffAxisNFixture

        self._equipment = TokkiOffAxisNEquipment(station_config)  # type: TokkiOffAxisNEquipment
        if self._station_config.FIXTURE_PARTICLE_COUNTER:
            if self._fixture.particle_counter_state() == 0:
                self._fixture.particle_counter_on()
                self._particle_counter_start_time = datetime.datetime.now()
        self._overall_errorcode = ''
        self._first_failed_test_result = None
        self._latest_serial_number = None  # type: str
        self._the_unit = None  # type: pancakeDut
        self._is_screen_on_by_op = False
        self._retries_screen_on = 0
        self._is_cancel_test_by_op = False
        self._ttxm_filelist = []

    def initialize(self):
        raise TokkiOffAxisNStationError(f'Fail to initialize fixture. unable to find com-port')

        self._operator_interface.print_to_console(f"Initializing station...SW: {self._sw_version}\n")
        self._station_config.FIXTURE_COMPORT = None
        self._station_config.FIXTURE_SCANER_COMPORT = None
        self._station_config.FIXTURE_PARTICLE_COMPORT = None
        # <editor-fold desc="port configuration automatically">
        cfg = 'station_config.json'
        station_config = {
            'FixtureCom': 'MYZY',
            'ParticleCounter': 'ParticleCounter',
            'Scanner': 'SR710',
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

        # config the port for fixture
        regex_port = station_config['FixtureCom']
        com_ports = [c[0] for c in port_list if re.search(regex_port, c[2], re.I | re.S)]
        if len(com_ports) != 1:
            self._operator_interface.print_to_console(f'Unable to find fixture Port: {regex_port}', 'red')
        else:
            self._station_config.FIXTURE_COMPORT = com_ports[-1]

        # config the port for scanner
        regex_port = station_config['Scanner']
        com_ports = [c[0] for c in port_list if re.search(regex_port, c[2], re.I | re.S)]
        if len(com_ports) == 1:
            self._station_config.FIXTURE_SCANER_COMPORT = com_ports[-1]
        else:
            self._operator_interface.print_to_console(f'Unable to find scanner Port: {regex_port}\n', 'red')

        # config the port for scanner
        regex_port = station_config['ParticleCounter']
        com_ports = [c[0] for c in port_list if re.search(regex_port, c[2], re.I | re.S)]
        if len(com_ports) == 1:
            self._station_config.FIXTURE_PARTICLE_COMPORT = com_ports[-1]
        else:
            self._operator_interface.print_to_console(f'Unable to find scanner Port: {regex_port}\n', 'red')
        # </editor-fold>

        if (not self._station_config.FIXTURE_SIM and
                (None in [self._station_config.FIXTURE_PARTICLE_COMPORT, self._station_config.FIXTURE_SCANER_COMPORT,
                          self._station_config.FIXTURE_COMPORT])):
            raise TokkiOffAxisNStationError(f'Fail to initialize fixture. unable to find com-port')

        self._fixture.initialize()
        if self._station_config.FIXTURE_PARTICLE_COUNTER and hasattr(self, '_particle_counter_start_time'):
            while ((datetime.datetime.now() - self._particle_counter_start_time)
                   < datetime.timedelta(self._station_config.FIXTRUE_PARTICLE_START_DLY)):
                time.sleep(0.1)
                self._operator_interface.print_to_console('Waiting for initializing particle counter ...\n')

        self._operator_interface.print_to_console("Initialize Camera %s\n" % self._station_config.CAMERA_SN)
        self._equipment.initialize()

    def close(self):
        if self._fixture is not None:
            self._fixture.close()
            self._fixture = None
        self._equipment.close()
        self._equipment = None

    def chk_and_set_measured_value_by_name(self, test_log, item, value, value_msg=None):
        """
        :type test_log: test_station.TestRecord
        """
        if item in test_log.results_array():
            test_log.set_measured_value_by_name(item, value)
            did_pass = test_log.get_test_by_name(item).did_pass()
            if value_msg is None:
                value_msg = value
            self._operator_interface.update_test_value(item, value_msg, 1 if did_pass else -1)

    def _do_test(self, serial_number, test_log):
        # type: (str, test_station.test_log) -> tuple
        test_log.set_measured_value_by_name_ex = types.MethodType(self.chk_and_set_measured_value_by_name, test_log)
        self._overall_result = False
        self._overall_errorcode = ''
        try:
            is_screen_on = False
            self._fixture.flush_data()
            self._operator_interface.print_to_console("Testing Unit %s\n" % serial_number)
            test_log.set_measured_value_by_name_ex('SW_VERSION', self._sw_version)
            test_log.set_measured_value_by_name_ex("DUT_ScreenOnRetries", self._retries_screen_on)
            test_log.set_measured_value_by_name_ex("DUT_ScreenOnStatus", self._is_screen_on_by_op or is_screen_on)

            if not is_screen_on and not self._is_screen_on_by_op:  # dut can't be lit up
                raise TokkiOffAxisNStationError("DUT Is unable to Power on : CancelByOp = {0}, ScreenOn = {1}."
                                          .format(self._is_cancel_test_by_op, is_screen_on))

            test_log.set_measured_value_by_name_ex("MPK_API_Version", self._equipment.version())
            self._operator_interface.print_to_console("Read the particle count in the fixture... \n")
            particle_count = 0
            if self._station_config.FIXTURE_PARTICLE_COUNTER:
                particle_count = self._fixture.particle_counter_read_val()
            test_log.set_measured_value_by_name_ex("ENV_ParticleCounter", particle_count)

            self._operator_interface.print_to_console("Set Camera Database. %s\n" % self._station_config.CAMERA_SN)

            sequencePath = os.path.join(self._station_config.ROOT_DIR, self._station_config.SEQUENCE_RELATIVEPATH)
            self._equipment.set_sequence(sequencePath)

            self._operator_interface.print_to_console("Close the eliminator in the fixture... \n")

            self.offaxis_test_do(serial_number, test_log, self._the_unit)

            if not self._station_config.IS_SAVEDB:
                self._operator_interface.print_to_console("!!!Remove ttxms to save disk-space.!!!\n")
                #  it is sometimes fail to remove ttxm cause the file is occupied by TrueTest
                file_list_to_removed = [c for c in self._ttxm_filelist if os.path.exists(c)]
                [shutil.rmtree(c, ignore_errors=True) for c in file_list_to_removed]
                self._ttxm_filelist = file_list_to_removed.copy()

        except Exception as e:
            self._operator_interface.print_to_console("Test exception {0}.\n".format(e))
        finally:
            self._operator_interface.print_to_console('release current test resource.\n')
            # noinspection PyBroadException
            try:
                if self._the_unit is not None:
                    self._the_unit.close()
                if self._fixture is not None:
                    self._fixture.unload()
                    self._fixture.button_disable()
            except:
                pass
            self._operator_interface.print_to_console('close the test_log for {}.\n'.format(serial_number))
            overall_result, first_failed_test_result = self.close_test(test_log)

            self._runningCount += 1
            self._operator_interface.print_to_console('--- do test finished ---\n')
            return overall_result, first_failed_test_result

    def close_test(self, test_log):
        result_array = test_log.results_array()
        save_pnl_dic = self._station_config.SAVE_PNL_IF_FAIL
        ui_msg = {
            'LA': 'L (左眼)',
            'RA': 'R (右眼)'
        }
        test_log.set_measured_value_by_name_ex('EXT_CTRL_RES', '')
        self._overall_result = test_log.get_overall_result()
        # modified the test result if ok_for_left/right
        if not self._overall_result and set(ui_msg.keys()).issubset(save_pnl_dic.keys()):
            save_pnl_dic_left = [result_array[c].did_pass() for c in save_pnl_dic['LA']]
            save_pnl_dic_right = [result_array[c].did_pass() for c in save_pnl_dic['RA']]
            if (False in save_pnl_dic_left) and (False not in save_pnl_dic_right):
                test_log.set_measured_value_by_name_ex('EXT_CTRL_RES', 'LA')
            elif (False not in save_pnl_dic_left) and (False in save_pnl_dic_right):
                test_log.set_measured_value_by_name_ex('EXT_CTRL_RES', 'RA')
            else:
                test_log.set_measured_value_by_name_ex('EXT_CTRL_RES', 'FAIL')
            ext_ctl_val = result_array['EXT_CTRL_RES'].get_measured_value()
            if ext_ctl_val in ui_msg.keys():
                test_log.get_overall_result()
                self._overall_result = True
                test_log._overall_did_pass = True
                test_log._overall_error_code = 0
                self._operator_interface.update_root_config({'ResultMsgEx': ui_msg[ext_ctl_val]})
            if not self._overall_result and len([k for k, v in result_array.items()
                                                 if v.get_measured_value() is None]) > 0:
                raise test_station.TestStationProcessControlError(f'Fail to test this DUT. 测试产品失败， 请重新测试')
        else:
            test_log.set_measured_value_by_name_ex('EXT_CTRL_RES', 'AA')
            self._operator_interface.update_root_config({'ResultMsgEx': 'L/R(左/右眼)'})

        self._first_failed_test_result = test_log.get_first_failed_test_result()
        return self._overall_result, self._first_failed_test_result

    def validate_sn(self, serial_num):
        if self._station_config.AUTO_SCAN_CODE:
            serial_num = self._fixture.scan_code(self._station_config.FIXTURE_SCANER_COMPORT)
        self._latest_serial_number = serial_num
        return test_station.TestStation.validate_sn(self, serial_num)

    def is_ready(self):
        serial_number = self._latest_serial_number
        self._operator_interface.print_to_console("Testing Unit %s\n" % serial_number)
        self._the_unit = dut.projectDut(serial_number, self._station_config, self._operator_interface)
        if self._station_config.DUT_SIM:
            self._the_unit = dut.projectDut(serial_number, self._station_config, self._operator_interface)
        return self.is_ready_litup_outside()

    def is_ready_litup_outside(self):
        ready = False
        power_on_trigger = False
        self._is_screen_on_by_op = False
        self._is_cancel_test_by_op = False
        self._retries_screen_on = 0
        timeout_for_btn_idle = (20 if not hasattr(self._station_config, 'TIMEOUT_FOR_BTN_IDLE')
                                else self._station_config.TIMEOUT_FOR_BTN_IDLE)

        timeout_for_dual = time.time()
        try:
            self._fixture.button_disable()
            self._fixture.power_on_button_status(True)
            self._the_unit.initialize()
            self._operator_interface.print_to_console("Initialize DUT... \n")
            tm_current = timeout_for_dual
            while tm_current - timeout_for_dual <= timeout_for_btn_idle:
                if ready or self._is_cancel_test_by_op:
                    break
                msg_prompt = 'Load DUT, and then Press PowerOn-Btn(Litup) in %s counts...'
                if power_on_trigger:
                    msg_prompt = 'Press Dual-Btn(Load)/L-Btn(Cancel)/PowerOn-Btn(Re Litup)  in %s counts...'
                tm_data = timeout_for_btn_idle - (tm_current - timeout_for_dual)
                self._operator_interface.prompt(msg_prompt % int(tm_data), 'yellow')
                if self._station_config.FIXTURE_SIM:
                    self._is_screen_on_by_op = True
                    ready = True

                ready_status = self._fixture.is_ready()
                if ready_status is not None:
                    if ready_status == 0x00:  # load DUT automatically and then screen on
                        ready = True  # Start to test.
                        self._is_screen_on_by_op = True
                        if self._retries_screen_on == 0:
                            self._the_unit.screen_on()

                    elif ready_status == 0x03:
                        self._operator_interface.print_to_console('Try to litup DUT.\n')
                        self._retries_screen_on += 1
                        if not power_on_trigger:
                            self._the_unit.screen_on()
                            power_on_trigger = True
                            self._fixture.button_enable()
                            timeout_for_dual = time.time()
                        else:
                            self._the_unit.screen_off()
                            self._the_unit.reboot()  # Reboot
                            self._the_unit.screen_on()
                            power_on_trigger = True
                            timeout_for_dual = time.time()
                    elif ready_status == 0x02:
                        self._is_cancel_test_by_op = True  # Cancel test.
                    elif ready_status == 0x04:
                        self._operator_interface.print_to_console('please load the dut correctly.\n')
                        pass
                time.sleep(0.01)
                tm_current = time.time()
        except Exception as e:
            self._operator_interface.print_to_console('exception msg {0}.\n'.format(e))
        finally:
            # noinspection PyBroadException
            try:
                self._fixture.button_disable()
                self._fixture.power_on_button_status(False)
                if not ready:
                    if not self._is_cancel_test_by_op:
                        self._operator_interface.print_to_console(
                            'Unable to get start signal in %s from fixture.\n' % int(time.time() - timeout_for_dual))
                    else:
                        self._operator_interface.print_to_console(
                            'Cancel start signal from dual %s.\n' % int(time.time() - timeout_for_dual))
                    self._the_unit.close()
                    self._the_unit = None
            except:
                pass
            self._operator_interface.prompt('', 'SystemButtonFace')

    def data_export(self, serial_number, test_log, tposIdx):
        """
        export csv and png from ttxm database
        :type test_log: test_station.TestRecord
        :type serial_number: str
        """
        for posIdx, pos, pos_patterns in self._station_config.TEST_POSITIONS:
            if posIdx != tposIdx:
                continue

            for test_pattern in pos_patterns:
                if test_pattern not in self._station_config.TEST_PATTERNS:
                    continue
                self._operator_interface.print_to_console(f"Panel export for Pattern: {test_pattern}\n")
                if self._station_config.IS_EXPORT_CSV or self._station_config.IS_EXPORT_PNG:
                    output_dir = os.path.join(self._station_config.ROOT_DIR, self._station_config.ANALYSIS_RELATIVEPATH,
                                              serial_number + '_' + test_log._start_time.strftime(
                                                  "%Y%m%d-%H%M%S"))
                    if not os.path.exists(output_dir):
                        os.mkdir(output_dir, 777)
                    meas_list = self._equipment.get_measurement_list()
                    exp_base_file_name = re.sub('_x.log', '', test_log.get_filename())
                    for meas in meas_list:
                        if meas['Measurement Setup'] != test_pattern:
                            continue

                        id = meas['Measurement ID']
                        export_csv_name = "{}_{}_{}.csv".format(serial_number, test_pattern, posIdx)
                        export_png_name = "{}_{}_{}.png".format(serial_number, test_pattern, posIdx)
                        if self._station_config.IS_EXPORT_CSV:
                            self._equipment.export_measurement(id, output_dir, export_csv_name,
                                                               self._station_config.Resolution_Bin_X,
                                                               self._station_config.Resolution_Bin_Y)
                        if self._station_config.IS_EXPORT_PNG:
                            self._equipment.export_measurement(id, output_dir, export_png_name,
                                                               self._station_config.Resolution_Bin_X,
                                                               self._station_config.Resolution_Bin_Y)
                        self._operator_interface.print_to_console("Export data for %s\n" % test_pattern)

    def offaxis_test_do(self, serial_number, test_log: test_station.test_log.TestRecord, the_unit):
        pre_color = None
        for posIdx, pos, pos_patterns in self._station_config.TEST_POSITIONS:
            analysis_result_dic = {}
            self._operator_interface.print_to_console('clear registration\n')
            self._equipment.clear_registration()
            if not self._station_config.EQUIPMENT_SIM:
                uni_file_name = re.sub('_x.log', '', test_log.get_filename())
                bak_dir = os.path.join(self._station_config.ROOT_DIR, self._station_config.ANALYSIS_RELATIVEPATH, 'raw')
                if not os.path.exists(os.path.join(bak_dir, uni_file_name)):
                    hsc_utils.mkdir_p(os.path.join(bak_dir, uni_file_name))
                databaseFileName = os.path.join(bak_dir, uni_file_name, f'{posIdx}.ttxm')
                self._equipment.create_database(databaseFileName)
                self._ttxm_filelist.append(databaseFileName)
            else:
                uut_dirs = [c for c in glob.glob(os.path.join(self._station_config.EQUIPMENT_DEMO_DATABASE, r'*'))
                            if os.path.isdir(c)
                            and os.path.relpath(c, self._station_config.EQUIPMENT_DEMO_DATABASE)
                                .upper().startswith(serial_number.upper())]
                if len(uut_dirs) <= 0:
                    raise FileNotFoundError(f'unable to address data for {serial_number}')
                db_dir = uut_dirs[-1]
                fns = glob.glob1(db_dir, f'{posIdx}.ttxm')
                if len(fns) <= 0:
                    raise FileNotFoundError(f'unable to address data for {serial_number}')
                databaseFileName = os.path.join(db_dir, fns[0])
                self._operator_interface.print_to_console("Set tt_database {}.\n".format(databaseFileName))
                self._equipment.set_database(databaseFileName)

            self._operator_interface.print_to_console("Panel Mov To Pos: {}.\n".format(pos))
            self._fixture.mov_abs_xy(pos[0], pos[1])

            center_item = self._station_config.CENTER_AT_POLE_AZI
            lv_cr_items = {}
            lv_all_items = {}
            for pattern in pos_patterns:
                if pattern not in self._station_config.TEST_PATTERNS:
                    self._operator_interface.print_to_console("Can't find pattern {} for position {}.\n"
                                                              .format(pattern, posIdx))
                    continue
                color_code = self._station_config.TEST_PATTERNS[pattern]['P']
                analysis = self._station_config.TEST_PATTERNS[pattern]['A']
                self._operator_interface.print_to_console(
                    f"Panel Measurement Pattern: {pattern} , Position Id {posIdx}.\n")
                if pre_color != color_code:
                    if isinstance(color_code, tuple):
                        the_unit.display_color(color_code)
                    elif isinstance(color_code, (str, int)):
                        the_unit.display_image(color_code)
                    pre_color = color_code
                    self._operator_interface.print_to_console('Set DUT To Color: {}.\n'.format(pre_color))
                use_camera = not self._station_config.EQUIPMENT_SIM
                if not use_camera:
                    self._equipment.clear_registration()
                analysis_result = self._equipment.sequence_run_step(analysis, '', use_camera, True)
                self._operator_interface.print_to_console("Sequence run step  {}.\n".format(analysis))
                analysis_result_dic[pattern] = analysis_result
                del analysis_result

                # region extract raw data
            for pattern in [c for c in pos_patterns if not self._station_config.DATA_COLLECT_ONLY]:
                analysis = self._station_config.TEST_PATTERNS[pattern]['A']

                lv_dic = {}
                cx_dic = {}
                cy_dic = {}
                center_dic = {}
                duv_dic = {}
                u_dic = {}
                v_dic = {}
                u_values = None
                u_values = None

                analysis_result = analysis_result_dic.get(pattern)
                if isinstance(analysis_result, dict) and analysis in analysis_result:
                    result = analysis_result[analysis]
                    if not isinstance(result, dict):
                        continue
                    for ra in result:
                        r = re.sub(' ', '', ra)
                        raw_test_item = (pattern + "_" + r)
                        test_item = re.sub(r'\((Lv|Luminance|LuminousIntensity)\)', '_Lv', raw_test_item)
                        test_item = re.sub(r'\s|%', '', test_item)

                        lv_match = re.search(r'(P_[0-9.]+\d*_[0-9.]+\d*)\((lv|Luminance|LuminousIntensity)\)', r,
                                             re.I | re.S)
                        if lv_match:
                            lv_dic[lv_match.groups()[0]] = float(result[ra])
                        cx_match = re.search(r'(P_[0-9.]+\d*_[0-9.]+\d*)\(cx\)', r, re.I | re.S)
                        if cx_match:
                            cx_dic[cx_match.groups()[0]] = float(result[ra])
                        cy_match = re.search(r'(P_[0-9.]+\d*_[0-9.]+\d*)\(cy\)', r, re.I | re.S)
                        if cy_match:
                            cy_dic[cy_match.groups()[0]] = float(result[ra])

                        u_match = re.search(r'u\'Values', r, re.I | re.S)
                        if u_match:
                            u_values = result[ra]
                        v_match = re.search(r'v\'Values', r, re.I | re.S)
                        if v_match:
                            v_values = result[ra]

                        center_match = re.search(r'(CenterLv|CenterCx|CenterCy)', r)
                        if center_match:
                            center_dic[center_match.groups()[0]] = float(result[ra])
                        if test_item in test_log.results_array():
                            test_log.set_measured_value_by_name(test_item, float(result[ra]))

                    keys = lv_dic.keys()
                    us = []
                    vs = []
                    if len(keys) == len(cx_dic) == len(cy_dic):
                        for key in keys:
                            cx = cx_dic[key]
                            cy = cy_dic[key]
                            u = 4 * cx / (-2 * cx + 12 * cy + 3)
                            v = 9 * cy / (-2 * cx + 12 * cy + 3)
                            us.append(u)
                            vs.append(v)
                        us_dic = dict(zip(keys, us))
                        vs_dic = dict(zip(keys, vs))
                        us0 = us_dic[center_item]
                        vs0 = vs_dic[center_item]
                        duvs = np.sqrt((np.array(us) - us0) ** 2 + (np.array(vs) - vs0) ** 2)
                        duv_dic = dict(zip(keys, duvs))
                        u_dic.update(us_dic)
                        v_dic.update(vs_dic)
                    lv_all_items[f'{posIdx}_{pattern}'] = lv_dic
                # endregion

                # region Normal Test Item.

                # BrCOMMAND_DISP_POWERON_DLYightness at 30deg polar angle (nits)
                brightness_items = []
                for item in self._station_config.BRIGHTNESS_AT_POLE_AZI:
                    tlv = lv_dic.get('P_%s_%s' % item)
                    if tlv is None:
                        continue
                    brightness_items.append(tlv)
                    test_item = '{}_{}_Lv_{}_{}'.format(posIdx, pattern, *item)
                    test_log.set_measured_value_by_name_ex(test_item, tlv)

                for item in self._station_config.COLOR_PRIMARY_AT_POLE_AZI:
                    u = u_dic.get(f'P_%s_%s' % item)
                    v = v_dic.get(f'P_%s_%s' % item)
                    if u is None or v is None:
                        continue
                    test_item = '{}_{}_u_{}_{}'.format(posIdx, pattern, *item)
                    test_log.set_measured_value_by_name_ex(test_item, u)
                    test_item = '{}_{}_v_{}_{}'.format(posIdx, pattern, *item)
                    test_log.set_measured_value_by_name_ex(test_item, v)

                for p0, p180 in self._station_config.BRIGHTNESS_AT_POLE_ASSEM:
                    lv_x_0 = lv_dic.get('P_%s_%s' % p0)
                    lv_x_180 = lv_dic.get('P_%s_%s' % p180)
                    if lv_x_0 is None or lv_x_180 is None:
                        continue
                    lv_0_0 = lv_dic[center_item]
                    assem = (lv_x_0 - lv_x_180) / lv_0_0
                    test_item = '{}_{}_ASYM_{}_{}_{}_{}'.format(posIdx, pattern, *(p0 + p180))
                    test_log.set_measured_value_by_name_ex(test_item, '{0:.4}'.format(assem))

                # Brightness % @30deg wrt on axis brightness
                brightness_items = []
                for item in self._station_config.BRIGHTNESS_AT_POLE_AZI_PER:
                    tlv = lv_dic.get('P_%s_%s' % item)
                    if tlv is None:
                        continue
                    tlv = tlv / lv_dic[center_item]
                    brightness_items.append(tlv)
                    test_item = '{}_{}_Lv_Proportion_{}_{}'.format(posIdx, pattern, *item)
                    test_log.set_measured_value_by_name_ex(test_item, tlv, io_utils.round_ex(tlv, 3))

                for item in self._station_config.COLORSHIFT_AT_POLE_AZI:
                    duv = duv_dic.get('P_%s_%s' % item)
                    if duv is None:
                        continue
                    test_item = '{}_{}_duv_{}_{}'.format(posIdx, pattern, *item)
                    test_log.set_measured_value_by_name_ex(test_item, duv, io_utils.round_ex(duv, 3))
                if len(lv_dic) > 0:
                    # Max brightness location
                    max_loc = max(lv_dic, key=lv_dic.get)
                    test_item = '{}_{}_Lv_max_pos'.format(posIdx, pattern)
                    test_log.set_measured_value_by_name_ex(test_item, max_loc)
                    inclination, azimuth = tuple(re.split('_', max_loc)[1:])
                    test_item = '{}_{}_Lv_max_pos_theta'.format(posIdx, pattern)
                    test_log.set_measured_value_by_name_ex(test_item, int(inclination))
                    test_item = '{}_{}_Lv_max_pos_phi'.format(posIdx, pattern)
                    test_log.set_measured_value_by_name_ex(test_item, int(azimuth))
                    # endregion

                    if pattern in self._station_config.CR_TEST_PATTERNS:
                        lv_cr_items[pattern] = lv_dic

            # region Constract Test Item

            if len(lv_cr_items) == len(self._station_config.CR_TEST_PATTERNS) == 2:
                # CR at 0deg and 30deg polar angle
                w = self._station_config.CR_TEST_PATTERNS[0]
                d = self._station_config.CR_TEST_PATTERNS[1]

                for item in self._station_config.CR_AT_POLE_AZI:
                    item_key = 'P_%s_%s' % item
                    if not lv_cr_items[w].get(item_key) or not lv_cr_items[d].get(item_key):
                        continue
                    cr = lv_cr_items[w][item_key] / lv_cr_items[d][item_key]
                    test_item = '{}_CR_{}_{}'.format(posIdx, *item)
                    test_log.set_measured_value_by_name_ex(test_item, cr, io_utils.round_ex(cr, 1))
            # endregion

            self.data_export(serial_number, test_log, posIdx)

            if self._station_config.IS_EXPORT_RAW_DATA:
                for export_posIdx, export_raw_data_patterns in self._station_config.EXPORT_RAW_DATA_PATTERN.items():
                    if posIdx != export_posIdx or len(export_raw_data_patterns) <= 0:
                        continue
                    export_raw_data = np.empty(
                        (len(self._station_config.EXPORT_RAW_DATA_PATTERN_POLE),
                         len(self._station_config.EXPORT_RAW_DATA_PATTERN_AZI) * len(export_raw_data_patterns) + 1),
                        np.float)
                    export_raw_data[:, 0] = self._station_config.EXPORT_RAW_DATA_PATTERN_POLE.copy()
                    for pattern_idx, exp_raw_data_pattern in enumerate(export_raw_data_patterns):
                        export_raw_keys = {}
                        for aziIdx, azi_item in enumerate(self._station_config.EXPORT_RAW_DATA_PATTERN_AZI):
                            pname, azi = azi_item
                            export_raw_keys = []
                            for pole in self._station_config.EXPORT_RAW_DATA_PATTERN_POLE:
                                if pole == 0:
                                    export_raw_keys.append(f'P_0_0')
                                elif pole > 0:
                                    export_raw_keys.append(f'P_{pole}_{azi}')
                                else:
                                    export_raw_keys.append(f'P_{-pole}_{azi + 180}')
                            export_raw_values = [lv_all_items[f'{posIdx}_{exp_raw_data_pattern}'].get(c) for c in
                                                 export_raw_keys]
                            export_raw_data[:, pattern_idx * len(
                                self._station_config.EXPORT_RAW_DATA_PATTERN_AZI) + aziIdx + 1] = export_raw_values
                    try:
                        raw_data_dir = os.path.join(os.path.dirname(test_log.get_file_path()), 'raw')
                        if not os.path.exists(raw_data_dir):
                            os.mkdir(raw_data_dir)

                        export_fn = test_log.get_filename().replace('_x.log', f'_raw_export_{posIdx}.csv')
                        with open(os.path.join(raw_data_dir, export_fn), 'w') as f:
                            header = ','
                            header2 = ','
                            header3 = 'Theta,'
                            subItems = ','.join(['' for c in self._station_config.EXPORT_RAW_DATA_PATTERN_AZI])
                            subItem2s = ','.join([c for c, d in self._station_config.EXPORT_RAW_DATA_PATTERN_AZI])
                            subItem3s = ','.join(
                                [f'Phi = {d}' for c, d in self._station_config.EXPORT_RAW_DATA_PATTERN_AZI])
                            header += ','.join([f'{c}{subItems}' for c in export_raw_data_patterns])
                            header2 += ','.join([f'{subItem2s}' for c in export_raw_data_patterns])
                            header3 += ','.join([f'{subItem3s}' for c in export_raw_data_patterns])
                            data_items = [header, header2, header3]

                            for x in range(export_raw_data.shape[0]):
                                data_items.append(','.join([f'{c}' for c in export_raw_data[x, :]]))

                            f.writelines([f'{c}\n' for c in data_items])
                            f.close()

                    except Exception as e:
                        self._operator_interface.print_to_console(f'Fail to save raw data. {str(e)} \n')

            del lv_all_items
        self._operator_interface.print_to_console('complete the off_axis test items.\n')
