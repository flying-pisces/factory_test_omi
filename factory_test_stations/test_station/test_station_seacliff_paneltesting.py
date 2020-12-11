import os
import shutil
import time
import math
import datetime
import re
import filecmp
import numpy as np
from itertools import islice
import pprint
import types
import glob
import sys
from test_station.test_fixture.test_fixture_project_station import projectstationFixture
import hardware_station_common.test_station.test_station as test_station
import test_station.test_fixture.test_fixture_seacliff_paneltesting as test_fixture_paneltesting
import test_station.test_equipment.test_equipment_seacliff_paneltesting as test_equipment
import test_station.dut as dut
import hardware_station_common.utils.gui_utils as gui_utils


class seacliffpaneltestingError(Exception):
    pass


def chk_and_set_measured_value_by_name(test_log, item, value):
    """

    :type test_log: test_station.TestRecord
    """
    if item in test_log.results_array():
        test_log.set_measured_value_by_name(item, value)
    pass

class pancakemuniStation(test_station.TestStation):
    """
        pancakepixel Station
    """

    def __init__(self, station_config, operator_interface):
        self._sw_version = '0.1.2'
        self._runningCount = 0
        test_station.TestStation.__init__(self, station_config, operator_interface)
        if hasattr(self._station_config, 'IS_PRINT_TO_LOG') and self._station_config.IS_PRINT_TO_LOG:
            sys.stdout = self
            sys.stderr = self
            sys.stdin = None
        self._fixture = test_fixture_paneltesting.seacliffpaneltestingFixture(station_config, operator_interface)
        if station_config.FIXTURE_SIM:
            self._fixture = projectstationFixture(station_config, operator_interface)
            pass
        self._equipment = test_equipment.pancakemuniEquipment(station_config, operator_interface)
        if self._station_config.FIXTURE_PARTICLE_COUNTER:
            if self._fixture.particle_counter_state() == 0:
                self._fixture.particle_counter_on()
                self._particle_counter_start_time = datetime.datetime.now()
        self._overall_errorcode = ''
        self._first_failed_test_result = None
        self._lastest_serial_number = None
        self._the_unit = None
        self._is_screen_on_by_op = False
        self._retries_screen_on = 0
        self._is_cancel_test_by_op = False
        self._unif_raw_data = {}
        self._raw_image_dir = os.path.join(self._station_config.ROOT_DIR, self._station_config.RAW_IMAGE_LOG_DIR)
        if self._station_config.EQUIPMENT_SIM:
            self._raw_image_dir = self._station_config.EQUIPMENT_DEMO_DATABASE

    def write(self, msg):
        """
        @type msg: str
        @return:
        """
        if msg is not None:
            if msg.endswith('\n') or msg.endswith('\r\n') or msg.endswith('\r'):
                pass
            else:
                msg += os.linesep
            self._operator_interface.print_to_console(msg)

    def auto_find_com_ports(self):
        import serial.tools.list_ports
        import serial
        from pymodbus.client.sync import ModbusSerialClient
        from pymodbus.register_read_message import ReadHoldingRegistersResponse

        self._operator_interface.print_to_console("auto config com ports...\n")
        self._station_config.DUT_COMPORT = None
        self._station_config.CA_PORT = None
        self._station_config.FIXTURE_COMPORT = None
        self._station_config.FIXTURE_PARTICLE_COMPORT = None

        com_ports = list(serial.tools.list_ports.comports())
        pprint.pprint(f'Ports = {[(com.device, com.hwid, com.description) for com in com_ports]} \n')

        for com in com_ports:
            hit_success = False
            if self._station_config.FIXTURE_PARTICLE_COUNTER \
                    and self._station_config.FIXTURE_PARTICLE_COMPORT is None\
                    and (self._station_config.FIXTURE_PARTICLE_COMPORT_FILTER in com.hwid):
                try:
                    timeout_modbus = 5 if not hasattr(self._station_config, 'PARTICLE_COUNTER_TIMEOUT') \
                        else self._station_config.PARTICLE_COUNTER_TIMEOUT
                    modbus_client = ModbusSerialClient(method='rtu', baudrate=9600, bytesize=8,
                                                       parity='N', stopbits=1,
                                                       port=com.device, timeout=timeout_modbus)
                    if modbus_client is not None:
                        retries = 1
                        while retries < 5:
                            rs = modbus_client.read_holding_registers(self._station_config.FIXTRUE_PARTICLE_ADDR_STATUS,
                                                                      2, unit=self._station_config.FIXTURE_PARTICLE_ADDR)
                            # type: ReadHoldingRegistersResponse
                            if rs is None or rs.isError():
                                retries = retries + 1
                                time.sleep(0.3)
                                continue
                            val = rs.registers[0]
                            self._station_config.FIXTURE_PARTICLE_COMPORT = com.device
                            hit_success = True
                except Exception as e:
                    pass
                finally:
                    modbus_client.close()

            if hit_success:
                continue
            if self._station_config.FIXTURE_COMPORT is None:
                try:
                    a_serial = serial.Serial(com.device, 115200, parity='N', stopbits=1, bytesize=8,
                                             timeout=1, xonxoff=0, rtscts=0)
                    if a_serial is not None:
                        a_serial.flush()
                        a_serial.write('CMD_ID\r\n'.encode())
                        msg = a_serial.readline()
                        if 'ID' in msg.decode(encoding='utf-8').upper():
                            self._station_config.FIXTURE_COMPORT = com.device
                            hit_success = True
                except Exception as e:
                    pass
                finally:
                    a_serial.close()

            if self._station_config.DUT_COMPORT is None:
                try:
                    a_serial = serial.Serial(com.device, 115200, parity='N', stopbits=1, bytesize=8,
                                             timeout=1, xonxoff=0, rtscts=0)
                    if a_serial is not None:
                        a_serial.flush()
                        a_serial.write('$c.VERSION,mcu\r\n'.encode())
                        ver_mcu = a_serial.readline()
                        if '$P.VERSION' in ver_mcu.decode(encoding='utf-8').upper():
                            a_serial.flush()
                            a_serial.write('$c.DUT.POWEROFF\r\n'.encode())
                            pw_msg = a_serial.readline()
                            if pw_msg != b'':
                                print('Ver_MCU: {0}, POWER_OFF: {1}'.format(ver_mcu, pw_msg.decode()))
                            self._station_config.DUT_COMPORT = com.device
                            hit_success = True
                except Exception as e:
                    pass
                finally:
                    a_serial.close()

            if hit_success:
                continue
            if self._station_config.CA_PORT is None:
                try:
                    a_serial = serial.Serial(com.device, 38400, parity='E', stopbits=2,
                                             bytesize=7, timeout=6, xonxoff=0, rtscts=0)
                    if a_serial is not None:
                        a_serial.flush()
                        a_serial.write('IDO\r\n'.encode())
                        msg = a_serial.readline()
                        if 'CA-MP410' in msg.decode(encoding='utf-8').upper():
                            self._station_config.CA_PORT = com.device
                except Exception as e:
                    pass
                finally:
                    a_serial.close()

    def initialize(self):
        self._operator_interface.print_to_console(f"Initializing station... SW_VER:{self._sw_version}\n")
        try:
            if self._station_config.AUTO_CFG_COMPORTS:
                self.auto_find_com_ports()

            msg = "find ports FIXTURE = {0}, CA = {1}, DUT = {2}, PARTICLE COUNTER = {3}. \n"\
                .format(self._station_config.FIXTURE_COMPORT, self._station_config.CA_PORT,
                        self._station_config.DUT_COMPORT, self._station_config.FIXTURE_PARTICLE_COMPORT)
            self._operator_interface.print_to_console(msg)

            self._fixture.initialize()
            if self._station_config.FIXTURE_PARTICLE_COUNTER and hasattr(self, '_particle_counter_start_time'):
                while ((datetime.datetime.now() - self._particle_counter_start_time)
                       < datetime.timedelta(self._station_config.FIXTRUE_PARTICLE_START_DLY)):
                    time.sleep(0.1)
                    self._operator_interface.print_to_console('Waiting for initializing particle counter ...\n')
            self._equipment.initialize()
            self._operator_interface.print_to_console('close the drawer automatically...\n')
            res = gui_utils.messagebox.askyesno('Hint', 'Please make sure the Carrier is unblocked.')
            if not res:
                raise test_station.TestStationError('Unable to initialize successful.')
            self._fixture.load()
            self._operator_interface.print_to_console("Calibrate the CA410...\n")
            self._equipment.zero_cal()
            self._operator_interface.print_to_console('open the drawer automatically...\n')
            self._fixture.unload()
        except (test_fixture_paneltesting.seacliffpaneltestingFixtureError,
                test_equipment.pancakemuniEquipmentError) as e:
            raise test_station.TestStationError('Unable to initialized.')

    def close(self):
        if self._fixture is not None:
            self._fixture.close()
            self._fixture = None
        self._equipment.close()
        self._equipment = None

    def _do_test(self, serial_number, test_log):
        # type: (str, test_station.test_log) -> tuple
        del self._unif_raw_data
        test_log.set_measured_value_by_name_ex = types.MethodType(chk_and_set_measured_value_by_name, test_log)
        self._overall_result = False
        self._overall_errorcode = ''
        self._unif_raw_data = {}
        self._operator_interface.print_to_console('CWD is {}\n'.format(os.getcwd()))

        try:
            if not os.path.exists(self._raw_image_dir):
                test_station.utils.mkdir_p(self._raw_image_dir)
            self._operator_interface.print_to_console("Testing Unit %s\n" % serial_number)
            test_log.set_measured_value_by_name_ex('SW_VERSION', self._sw_version)
            test_log.set_measured_value_by_name_ex("DUT_ScreenOnRetries", self._retries_screen_on)
            test_log.set_measured_value_by_name_ex("DUT_ScreenOnStatus", self._is_screen_on_by_op)

            if not self._is_screen_on_by_op:
                raise seacliffpaneltestingError("DUT Is unable to Power on.")

            test_log.set_measured_value_by_name_ex("MPK_API_Version", self._equipment.version())
            firmware_version = self._fixture.version()
            test_log.set_measured_value_by_name_ex("FW_VERSION_FIXTURE", firmware_version)

            self._operator_interface.print_to_console("Initialize DUT... \n")
            self._fixture.load()
            self._operator_interface.print_to_console("Read the particle count in the fixture... \n")
            particle_count = 0
            if self._station_config.FIXTURE_PARTICLE_COUNTER:
                particle_count = self._fixture.particle_counter_read_val()
            test_log.set_measured_value_by_name_ex("ENV_ParticleCounter", particle_count)

            self._operator_interface.print_to_console("Set Camera Database. %s\n" % self._station_config.CAMERA_SN)

            uni_file_name = re.sub('_x.log', '.ttxm', test_log.get_filename())

            sequencePath = os.path.join(self._station_config.ROOT_DIR,
                                        self._station_config.SEQUENCE_RELATIVEPATH)
            if not self._station_config.EQUIPMENT_SIM:
                databaseFileName = os.path.join(self._raw_image_dir, uni_file_name)
                self._equipment.create_database(databaseFileName)
            else:
                db_dir = self._raw_image_dir
                fns = glob.glob1(db_dir, '%s_*.ttxm' % (serial_number))
                if len(fns) > 0:
                    databaseFileName = os.path.join(db_dir, fns[0])
                    self._operator_interface.print_to_console("Set tt_database {}.\n".format(databaseFileName))
                    self._equipment.set_database(databaseFileName)
                else:
                    raise seacliffpaneltestingError('unable to find ttxm for SN: %s \n' % (serial_number))
            self._equipment.set_sequence(sequencePath)

            self._operator_interface.print_to_console('clear registration\n')
            self._equipment.clear_registration()

            # self._operator_interface.print_to_console("Move CA to safe location... \n")
            # self._fixture.mov_abs_xy_wrt_dut(*self._station_config.CA_SAFE_LOCATION)

            self._operator_interface.print_to_console("Start testing subpixel for bright... \n")
            self.bright_subpixel_do(self._the_unit, serial_number, test_log)
            self._operator_interface.print_to_console("Start testing subpixel for dark... \n")
            self.dark_subpixel_do(self._the_unit, serial_number, test_log)
            self._operator_interface.print_to_console("Start exporting ... \n")
            self.data_export(serial_number, test_log)
            self._operator_interface.print_to_console("start uniformity testing ... \n")

            self._fixture.mov_abs_xy_wrt_dut(0, 0)
            self._fixture.ca_postion_z(True)
            self.uniformity_test_do(self._the_unit, serial_number, test_log)
            self._operator_interface.print_to_console('calc uniformity...\n')
            self.uniformity_test_alg(serial_number, test_log)

        except Exception as e:
            self._operator_interface.print_to_console("Test exception . {0}\n".format(e))
            self._operator_interface.operator_input('Exception', f'{str(e)}', msg_type='error')
        finally:
            self._operator_interface.print_to_console('release current test resource.\n')
            # noinspection PyBroadException
            try:
                if self._the_unit is not None:
                    self._the_unit.close()
                    self._the_unit = None
                if self._fixture is not None:
                    self._fixture.unload()
            except:
                pass

            self._operator_interface.print_to_console('close the test_log for {}.\n'.format(serial_number))
            overall_result, first_failed_test_result = self.close_test(test_log)

            self._runningCount += 1
            self._operator_interface.print_to_console('--- do test finished ---\n')
            return overall_result, first_failed_test_result

    def close_test(self, test_log):
        ### Insert code to gracefully restore fixture to known state, e.g. clear_all_relays() ###
        self._overall_result = test_log.get_overall_result()
        self._first_failed_test_result = test_log.get_first_failed_test_result()

        return self._overall_result, self._first_failed_test_result

    def validate_sn(self, serial_num):
        self._lastest_serial_number = serial_num
        return test_station.TestStation.validate_sn(self, serial_num)

    def get_free_space_mb(self, folder):
        import ctypes
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value / 1024 / 1024

    def is_ready(self):
        free_space = self.get_free_space_mb(self._station_config.ROOT_DIR)
        limit_free_space = 500
        if free_space < limit_free_space:
            msg = "Unable to start test (total size of free space {0:.1f} less than {1}M.\n"\
                .format(free_space, limit_free_space)
            self._operator_interface.operator_input('WARN', msg=msg, msg_type='warning')
            return False

        ready = False
        self._is_cancel_test_by_op = False
        power_on_trigger = False
        self._is_screen_on_by_op = False
        self._retries_screen_on = 0

        serial_number = self._lastest_serial_number
        self._operator_interface.print_to_console("Testing Unit %s\n" % serial_number)
        self._the_unit = dut.pancakeDut(serial_number, self._station_config, self._operator_interface)
        if self._station_config.DUT_SIM:
            self._the_unit = dut.projectDut(serial_number, self._station_config, self._operator_interface)

        timeout_for_btn_idle = 20
        timeout_for_dual = timeout_for_btn_idle
        try:
            self._the_unit.initialize()
            self._fixture.start_button_status(False)
            self._fixture.power_on_button_status(True)
            while timeout_for_dual > 0:
                if ready or self._is_cancel_test_by_op:
                    break
                msg_prompt = 'Load DUT, and then Press L-Btn(Cancel)/R-Btn(Litup) in %s S...'
                if power_on_trigger:
                    msg_prompt = 'Press Dual-Btn(Load)/L-Btn(Cancel)/R-Btn(Re Litup)  in %s S...'
                self._operator_interface.prompt(msg_prompt % timeout_for_dual, 'yellow');
                if self._station_config.FIXTURE_SIM:
                    self._is_screen_on_by_op = True
                    ready = True
                    continue

                if (hasattr(self._station_config, 'DUT_LOAD_WITHOUT_OPERATOR')
                        and self._station_config.DUT_LOAD_WITHOUT_OPERATOR is True):
                    self._fixture.load()
                    ready_status = 0x00
                else:
                    ready_status = self._fixture.is_ready()

                if ready_status is not None:
                    if ready_status == 0x00:  # dual-start button indicate to test.
                        ready = True  # Start to test.
                        self._is_screen_on_by_op = True
                        if not power_on_trigger:
                            self._the_unit.screen_on()
                            self._operator_interface.print_to_console('Press L-Btn(Cancel)/R-Btn(Litup) to lit up firstly.\n')
                    elif ready_status == 0x03 or ready_status == 0x02:  # left button / power on button.
                        self._operator_interface.print_to_console('Try to litup DUT.\n')
                        self._retries_screen_on += 1
                        if not power_on_trigger:
                            self._the_unit.screen_on()
                            # self._the_unit.display_image(self._station_config.DISP_CHECKER_IMG_INDEX)
                            power_on_trigger = True
                            self._fixture.power_on_button_status(False)
                            self._fixture.start_button_status(True)
                            timeout_for_dual = timeout_for_btn_idle
                        else:
                            self._fixture.start_button_status(False)
                            self._the_unit.screen_off()
                            self._the_unit.reboot()  # Reboot
                            self._the_unit.screen_on()
                            self._fixture.start_button_status(True)
                            # self._the_unit.display_image(self._station_config.DISP_CHECKER_IMG_INDEX)
                            power_on_trigger = True
                            timeout_for_dual = timeout_for_btn_idle
                    elif ready_status == 0x01:   # right button
                        self._is_cancel_test_by_op = True  # Cancel test.
                time.sleep(0.1)
                timeout_for_dual -= 1

        except Exception as e:
            self._operator_interface.print_to_console('Fixture is not ready for reason: %s.\n' % e)
        finally:
            # noinspection PyBroadException
            try:
                self._fixture.power_on_button_status(False)
                self._fixture.start_button_status(False)
                if not ready:
                    if not self._is_cancel_test_by_op:
                        self._operator_interface.print_to_console(
                            'Unable to get start signal in %s from fixture.\n' % timeout_for_dual)
                    else:
                        self._operator_interface.print_to_console(
                            'Cancel start signal from dual %s.\n' % timeout_for_dual)
                    self._the_unit.close()
                    self._the_unit = None
            except:
                pass
            self._operator_interface.prompt('', 'SystemButtonFace')

    def get_pattern_colour(self, pattern):
        return self._station_config.PATTERN_COLORS.get(pattern)

    def calc_blemish_index(self, pattern, npdata, test_log):
        self._operator_interface.print_to_console("calc blemish_index {}.\n".format(pattern))
        test_item = pattern + "_" + "BlemishIndex"
        npdata_shape = np.shape(npdata)
        if test_item not in test_log.results_array():
            return
        # Algorithm For blemish_index
        blemish_index = 0
        if npdata_shape[1] > 0 and npdata_shape[0] == 5:
            size_list = npdata[0, :]
            locax_list = npdata[1, :]
            locay_list = npdata[2, :]
            pixel_list = npdata[3, :]
            constrast_lst = npdata[4, :]
            abs_contrast = np.abs(constrast_lst)
            location_r = np.sqrt(np.power(np.array(locax_list) - self._station_config.LOCATION_X0, 2)
                                 * np.power(np.array(locay_list) - self._station_config.LOCATION_Y0, 2))
            location_index = []
            size_index = []
            for id in range(len(locax_list)):
                tmp_local_index = 0
                tmp_size_index = 0
                if location_r[id] <= self._station_config.LOCATION_L:
                    tmp_local_index = 2
                elif self._station_config.LOCATION_L < location_r[id] <= self._station_config.LOCATION_U:
                    tmp_local_index = 1
                elif location_r[id] > self._station_config.LOCATION_U:
                    tmp_local_index = 0

                if size_list[id] <= self._station_config.SIZE_L:
                    tmp_size_index = 0
                elif self._station_config.SIZE_L < size_list[id] <= self._station_config.SIZE_U:
                    tmp_size_index = 1
                elif size_list[id] > self._station_config.SIZE_U:
                    tmp_size_index = 2

                location_index.append(tmp_local_index)
                size_index.append(tmp_size_index)

            defect_index = abs_contrast * np.array(location_index) * np.array(size_index)
            blemish_index = np.sum(defect_index)
            if self._station_config.IS_VERBOSE:
                print('constrast_{}:{}'.format(pattern, constrast_lst))
                print('locationX_{}:{}'.format(pattern, locax_list))
                print('locationY_{}:{}'.format(pattern, locay_list))
                print('size     _{}:{}'.format(pattern, size_list))
                print('pixel    _{}:{}'.format(pattern, pixel_list))
        test_log.set_measured_value_by_name_ex(test_item, blemish_index)

    def data_export(self, serial_number, test_log):
        """
        export csv and png from ttxm database
        :type test_log: test_station.TestRecord
        :type serial_number: str
        """
        for pattern, __ in self._station_config.PATTERN_COLORS.items():
            if self._station_config.IS_EXPORT_CSV or self._station_config.IS_EXPORT_PNG:
                self._operator_interface.print_to_console("Panel export for Pattern: %s\n" % pattern)
                output_dir = os.path.join(self._station_config.ROOT_DIR, self._station_config.ANALYSIS_RELATIVEPATH,
                                          serial_number + '_' + test_log._start_time.strftime(
                                              "%Y%m%d-%H%M%S"))
                if not os.path.exists(output_dir):
                    os.mkdir(output_dir, 0o777)
                meas_list = self._equipment.get_measurement_list()
                exp_base_file_name = re.sub('_x.log', '', test_log.get_filename())
                for meas in meas_list:
                    if meas['Measurement Setup'] != pattern:
                        continue

                    id = meas['Measurement ID']
                    export_csv_name = "{}_{}.csv".format(serial_number, pattern)
                    export_png_name = "{}_{}.png".format(serial_number, pattern)
                    if self._station_config.IS_EXPORT_CSV:
                        self._equipment.export_measurement(id, output_dir, export_csv_name,
                                                           self._station_config.Resolution_Bin_X,
                                                           self._station_config.Resolution_Bin_Y)
                    if self._station_config.IS_EXPORT_PNG:
                        self._equipment.export_measurement(id, output_dir, export_png_name,
                                                           self._station_config.Resolution_Bin_X,
                                                           self._station_config.Resolution_Bin_Y)
                    self._operator_interface.print_to_console("Export data for {}\n".format(pattern))

    def bright_subpixel_do(self, the_unit, serial_number, test_log):
        """
        export csv and png from ttxm database
        :type the_unit: dut.pancakeDut
        :type test_log: test_station.TestRecord
        :type serial_number: str
        """
        avg_lv_register_patterns = []
        for idx, br_pattern in enumerate(self._station_config.PATTERNS_BRIGHT):
            pattern_color = self.get_pattern_colour(br_pattern)
            if isinstance(pattern_color, tuple):
                the_unit.display_color(pattern_color)
            elif isinstance(pattern_color, (str, int)):
                the_unit.display_image(pattern_color)
            else:
                continue

            analysis = self._station_config.ANALYSIS.get(br_pattern)
            use_camera = not self._station_config.EQUIPMENT_SIM
            if not use_camera:
                self._equipment.clear_registration()
            analysis_result = self._equipment.sequence_run_step(analysis, '', use_camera, self._station_config.IS_SAVEDB)
            self._operator_interface.print_to_console("sequence run step {}.\n".format(analysis))

            if 0 <= idx <= 1:  # the first 2 patterns are used to register.
                meas_list = self._equipment.get_measurement_list()
                for meas in meas_list:
                    if meas['Measurement Setup'] != br_pattern:
                        continue
                    output_dir = os.path.join(self._raw_image_dir,
                                              serial_number + '_' + test_log._start_time.strftime("%Y%m%d-%H%M%S"))
                    if not os.path.exists(output_dir):
                        os.mkdir(output_dir, 777)
                    id = meas['Measurement ID']
                    export_csv_name = "{}_{}_register.csv".format(serial_number, br_pattern)
                    self._equipment.export_measurement(id, output_dir, export_csv_name,
                                                       self._station_config.Resolution_Bin_X_REGISTER,
                                                       self._station_config.Resolution_Bin_Y_REGISTER)
                    lv = []
                    fn = os.path.join(output_dir, export_csv_name)
                    with open(fn) as f:
                        for line in islice(f, self._station_config.Resolution_REGISTER_SKIPTEXT,
                                           self._station_config.Resolution_Bin_Y_REGISTER):
                            row_data = line.replace('\n', '').split(',')
                            lv.append([float(c) for c in row_data])
                    avg = np.array(lv).mean()
                    avg_lv_register_patterns.append(avg)
                    os.remove(fn)
                    os.removedirs(output_dir)
            else:
                size_list = []
                locax_list = []
                locay_list = []
                pixel_list = []
                constrast_lst = []
                for c, result in analysis_result.items():
                    if not isinstance(result, dict) or not result.get('NumDefects'):
                        continue
                    num = int(result['NumDefects'])
                    self._operator_interface.print_to_console("prase numDefect {}, Num={}.\n".format(br_pattern, num))
                    for id in range(1, num + 1):
                        size_key = 'Size_{}'.format(id)
                        locax_key = 'LocX_{}'.format(id)
                        locay_key = 'LocY_{}'.format(id)
                        contrast_key = 'Contrast_{}'.format(id)
                        pixel_key = 'Pixels_{}'.format(id)
                        if (result.get(size_key) and
                                result.get(locax_key) and
                                result.get(locay_key) and
                                result.get(contrast_key) and
                                result.get(pixel_key)):
                            size_list.append(float(result[size_key]))
                            locax_list.append(float(result[locax_key]))
                            locay_list.append(float(result[locay_key]))
                            pixel_list.append(float(result[pixel_key]))
                            constrast_lst.append(float(result[contrast_key]))

                    self._operator_interface.print_to_console("prase normal test item {}.\n".format(br_pattern))
                    self.normal_test_item_parse(br_pattern, result, test_log)

                    pos_items = (locax_list, locay_list)
                    super_brighter_count = 0
                    min_super_sepa_distance = 0
                    super_dimmer_count = 0
                    min_super_dimmer_distance = 0
                    quality_brighter_count = 0
                    min_qual_brighter_sepa_distance = 0
                    quality_dimmeru_count = 0
                    min_qual_dimu_sepa_distance = 0
                    quality_dimmerl_count = 0
                    min_qual_diml_sepa_distance = 0
                    if num > 0 and len(constrast_lst) > 0:
                        abs_contrast = np.abs(constrast_lst)
                        location_r = np.sqrt(np.power(np.array(locax_list) - self._station_config.LOCATION_X0, 2)
                                             + np.power(np.array(locay_list) - self._station_config.LOCATION_Y0, 2))

                        defects = [c > avg_lv_register_patterns[0] and
                                                              d <= self._station_config.SUPER_QUALITY_AREA_R
                                                              for c, d in zip(abs_contrast, location_r)]

                        super_brighter_count = defects.count(True)
                        min_super_sepa_distance = self.calc_separate_distance(pos_items, defects)

                        defects = [c <= avg_lv_register_patterns[0] and
                                              d <= self._station_config.SUPER_QUALITY_AREA_R
                                              for c, d in zip(abs_contrast, location_r)]

                        super_dimmer_count = defects.count(True)
                        min_super_dimmer_distance = self.calc_separate_distance(pos_items, defects)

                        defects = [c > avg_lv_register_patterns[1] and
                            self._station_config.QUALITY_AREA_R >= d > self._station_config.SUPER_QUALITY_AREA_R
                            for c, d in zip(abs_contrast, location_r)]
                        quality_brighter_count = defects.count(True)
                        min_bri_sepa_distance = self.calc_separate_distance(pos_items, defects)

                        defects = [avg_lv_register_patterns[0] < c <= avg_lv_register_patterns[1] and
                             self._station_config.QUALITY_AREA_R >= d > self._station_config.SUPER_QUALITY_AREA_R
                             for c, d in zip(abs_contrast, location_r)]
                        quality_dimmeru_count = defects.count(True)
                        min_qual_dimu_sepa_distance = self.calc_separate_distance(pos_items, defects)

                        defects = [ avg_lv_register_patterns[0] >= c and
                             self._station_config.QUALITY_AREA_R >= d > self._station_config.SUPER_QUALITY_AREA_R
                             for c, d in zip(abs_contrast, location_r)]
                        quality_dimmerl_count = defects.count(True)
                        min_qual_diml_sepa_distance = self.calc_separate_distance(pos_items, defects)

                    test_item = '{}_SuperQuality_Brighter_NumDefects'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, super_brighter_count)
                    test_item = '{}_SuperQuality_Brighter_MinSeparationDistance'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, min_super_sepa_distance)
                    test_item = '{}_SuperQuality_Brighter_Res'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, super_brighter_count == 0 or
                                                           super_brighter_count <= self._station_config.SUPER_AREA_DEFECTS_COUNT_L)
                    test_item = '{}_SuperQuality_Dimmer_NumDefects'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, super_dimmer_count)
                    test_item = '{}_SuperQuality_Dimmer_MinSeparationDistance'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, min_super_dimmer_distance)
                    test_item = '{}_SuperQuality_Dimmer_Res'.format(br_pattern)
                    super_quality_dimmer_res = (super_dimmer_count == 0 or
                        super_dimmer_count <= self._station_config.SUPER_AREA_DEFECTS_COUNT_H and
                                (super_dimmer_count == 1 or min_super_dimmer_distance >= self._station_config.SEPARATION_DISTANCE))
                    test_log.set_measured_value_by_name_ex(test_item, super_quality_dimmer_res)
                    test_item = '{}_Quality_Brighter_NumDefects'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, quality_brighter_count)
                    test_item = '{}_Quality_Brighter_MinSeparationDistance'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, min_qual_brighter_sepa_distance)
                    test_item = '{}_Quality_Brighter_Res'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, quality_brighter_count == 0 or
                                                           quality_brighter_count <= self._station_config.QUALITY_AREA_DEFECTS_COUNT_B)
                    test_item = '{}_Quality_DimmerU_NumDefects'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, quality_dimmeru_count)
                    test_item = '{}_Quality_DimmerU_MinSeparationDistance'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, min_qual_dimu_sepa_distance)
                    test_item = '{}_Quality_DimmerU_Res'.format(br_pattern)
                    qual_dimmerU_res = (quality_dimmeru_count == 0 or
                        quality_dimmeru_count <= self._station_config.QUALITY_AREA_DEFECTS_COUNT_DU and
                                (quality_dimmeru_count == 1 or min_qual_dimu_sepa_distance >= self._station_config.SEPARATION_DISTANCE))
                    test_log.set_measured_value_by_name_ex(test_item, qual_dimmerU_res)
                    test_item = '{}_Quality_DimmerL_NumDefects'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, quality_dimmerl_count)
                    test_item = '{}_Quality_DimmerL_MinSeparationDistance'.format(br_pattern)
                    test_log.set_measured_value_by_name_ex(test_item, min_qual_diml_sepa_distance)
                    test_item = '{}_Quality_DimmerL_Res'.format(br_pattern)
                    qual_dimmerL_res = (quality_dimmerl_count == 0 or
                        quality_dimmerl_count <= self._station_config.QUALITY_AREA_DEFECTS_COUNT_DL and
                                (quality_dimmerl_count == 1 or min_qual_diml_sepa_distance >= self._station_config.SEPARATION_DISTANCE_L))
                    test_log.set_measured_value_by_name_ex(test_item, qual_dimmerL_res)

                    self.calc_blemish_index(br_pattern,
                                            np.vstack([size_list, locax_list, locay_list, pixel_list, constrast_lst]), test_log)

    @staticmethod
    def calc_separate_distance(defect_positions, mask_pos):
        distance_items = []
        mask_pos_items = []
        for pos, value in enumerate(mask_pos):
            if not value:
                continue
            mask_pos_items.append(pos)
        num = len(mask_pos_items)
        x = np.array(defect_positions[0])[mask_pos_items]
        y = np.array(defect_positions[1])[mask_pos_items]
        for row in range(num):
            for col in range(num):
                if row != col:
                    dis = ((x[col] - x[row]) ** 2 + (y[col] - y[row]) ** 2) ** 0.5
                    distance_items.append(dis)
        if len(distance_items) <= 1:
            return 0
        return min(distance_items)

    def normal_test_item_parse(self, br_pattern, result, test_log):
        """
        :type test_log: test_station.TestRecord
        :type result: []
        :type br_pattern: str
        """
        for resItem in result:
            test_item = (br_pattern + "_" + resItem).replace(" ", "")
            if test_item in test_log.results_array() and \
                    re.match(r'^([-|+]?\d+)(\.\d*)?$', result[resItem], re.IGNORECASE):
                self._operator_interface.print_to_console(
                    '{}, {}.\n'.format(test_item, result[resItem]))
                test_log.set_measured_value_by_name_ex(test_item, float(result[resItem]))
                self._operator_interface.print_to_console('TEST ITEM: {}, Value: {}\n'
                                                          .format(test_item, result[resItem]))

    def dark_subpixel_do(self, the_unit, serial_number, test_log):
        for idx, br_pattern in enumerate(self._station_config.PATTERNS_DARK):
            self._operator_interface.print_to_console(
                "Panel Measurement Pattern: %s\n" % br_pattern)
            pattern_color = self.get_pattern_colour(br_pattern)
            if isinstance(pattern_color, tuple):
                the_unit.display_color(pattern_color)
            elif isinstance(pattern_color, (str, int)):
                the_unit.display_image(pattern_color)
            else:
                continue

            analysis = self._station_config.ANALYSIS.get(br_pattern)
            use_camera = not self._station_config.EQUIPMENT_SIM
            if not use_camera:
                self._equipment.clear_registration()
            analysis_result = self._equipment.sequence_run_step(analysis, '', use_camera, self._station_config.IS_SAVEDB)
            self._operator_interface.print_to_console("sequence run step {}.\n".format(analysis))

            size_list = []
            locax_list = []
            locay_list = []
            pixel_list = []
            constrast_lst = []
            for c, result in analysis_result.items():
                if not isinstance(result, dict) or not result.get('NumDefects'):
                    continue
                num = int(result['NumDefects'])
                self._operator_interface.print_to_console("prase numDefect {}, Num={}.\n".format(br_pattern, num))
                for id in range(1, num + 1):
                    size_key = 'Size_{}'.format(id)
                    locax_key = 'LocX_{}'.format(id)
                    locay_key = 'LocY_{}'.format(id)
                    contrast_key = 'Contrast_{}'.format(id)
                    pixel_key = 'Pixels_{}'.format(id)
                    if (result.get(size_key) and
                            result.get(locax_key) and
                            result.get(locay_key) and
                            result.get(contrast_key) and
                            result.get(pixel_key)):
                        size_list.append(float(result[size_key]))
                        locax_list.append(float(result[locax_key]))
                        locay_list.append(float(result[locay_key]))
                        pixel_list.append(float(result[pixel_key]))
                        constrast_lst.append(float(result[contrast_key]))

                self._operator_interface.print_to_console("prase normal test item {0}.\n".format(br_pattern))
                self.normal_test_item_parse(br_pattern, result, test_log)

                pos_items = (locax_list, locay_list)

                super_quality_count = 0
                min_super_sepa_distance = 0
                quality_count = 0
                min_qaul_sepa_distance = 0

                if num > 0 and len(constrast_lst) > 0:
                    abs_contrast = np.abs(constrast_lst)
                    location_r = np.sqrt(np.power(np.array(locax_list) - self._station_config.LOCATION_X0, 2)
                                         + np.power(np.array(locay_list) - self._station_config.LOCATION_Y0, 2))

                    defects = [d <= self._station_config.SUPER_QUALITY_AREA_R
                               for c, d in zip(abs_contrast, location_r)]
                    super_quality_count = defects.count(True)

                    min_super_sepa_distance = self.calc_separate_distance(pos_items, defects)

                    defects = [self._station_config.QUALITY_AREA_R >= d > self._station_config.SUPER_QUALITY_AREA_R
                               for c, d in zip(abs_contrast, location_r)]
                    quality_count = defects.count(True)

                    min_qaul_sepa_distance = self.calc_separate_distance(pos_items, defects)

                test_item = '{}_SuperQuality_NumDefects'.format(br_pattern)
                test_log.set_measured_value_by_name_ex(test_item, super_quality_count)
                test_item = '{}_SuperQuality_MinSeparationDistance'.format(br_pattern)
                test_log.set_measured_value_by_name_ex(test_item, min_super_sepa_distance)
                test_item = '{}_SuperQuality_Res'.format(br_pattern)
                super_qual_res = (
                        super_quality_count == 0 or
                        (self._station_config.DARK_SUPER_AREA_DEFECTS_COUNT_L <= super_quality_count
                            <= self._station_config.DARK_SUPER_AREA_DEFECTS_COUNT_H and
                                (super_quality_count == 1
                                    or min_super_sepa_distance >= self._station_config.SEPARATION_DISTANCE)))
                test_log.set_measured_value_by_name_ex(test_item, super_qual_res)

                test_item = '{}_Quality_NumDefects'.format(br_pattern)
                test_log.set_measured_value_by_name_ex(test_item, quality_count)
                test_item = '{}_Quality_MinSeparationDistance'.format(br_pattern)
                test_log.set_measured_value_by_name_ex(test_item, min_qaul_sepa_distance)
                test_item = '{}_Quality_Res'.format(br_pattern)
                qual_res = (
                        quality_count == 0 or
                            (self._station_config.DARK_QUALITY_AREA_DEFECTS_COUNT_L <= quality_count
                                <= self._station_config.DARK_QUALITY_AREA_DEFECTS_COUNT_H and
                                    (quality_count == 1
                                        or min_qaul_sepa_distance >= self._station_config.SEPARATION_DISTANCE)))
                test_log.set_measured_value_by_name_ex(test_item, qual_res)
                self.calc_blemish_index(br_pattern,
                     np.vstack([size_list, locax_list, locay_list, pixel_list, constrast_lst]), test_log)

    def uniformity_test_do(self, the_unit, serial_number, test_log):
        """
        export csv and png from ttxm database
        :type the_unit: dut.pancakeDut
        :type test_log: test_station.TestRecord
        :type serial_number: str
        """
        centerlv_gls = []
        gls = []
        for idx, br_pattern in enumerate(self._station_config.UNIF_PATTERNS):
            self._operator_interface.print_to_console("Panel Measurement Pattern: %s \n" % br_pattern)
            pattern_color = self.get_pattern_colour(br_pattern)
            if isinstance(pattern_color, tuple):
                the_unit.display_color(pattern_color)
            elif isinstance(pattern_color, (str, int)):
                the_unit.display_image(pattern_color)
            else:
                continue
            dly = (self._station_config.FIXTURE_CA_STABLE_DLY
                   if hasattr(self._station_config, 'FIXTURE_CA_STABLE_DLY') else 0.05)
            for unif_name, unif_pos in self._station_config.TEST_POINTS_POS:
                self._operator_interface.print_to_console('Move DUT to POS {0}\n'.format(unif_name))
                self._fixture.mov_abs_xy_wrt_dut(*unif_pos)
                time.sleep(dly)
                self._operator_interface.print_to_console('Read data {0}_{1}\n'.format(br_pattern, unif_name))
                xylv = self._equipment.measure_xyLv()
                if (xylv is not None) and (isinstance(xylv, tuple)):
                    x, y, lv = xylv
                    if (unif_name, br_pattern) in self._station_config.GAMMA_CHECK_GLS:
                        centerlv_gls.append(lv)
                        gls.append(float(br_pattern[1:4]))
                    self._unif_raw_data['{0}_{1}'.format(br_pattern, unif_name)] = (x, y, lv)
        # gamma ...
        gamma = None
        if len(gls) > 0 and len(centerlv_gls) > 0:
            norm_gls = np.log10([gl / max(gls) for gl in gls])
            norm_clv = np.log10([centerlv_gl / max(centerlv_gls) for centerlv_gl in centerlv_gls])
            gamma, cov = np.polyfit(norm_gls, norm_clv, 1, cov=False)
        test_log.set_measured_value_by_name_ex("DISPLAY_GAMMA", gamma)

    def uniformity_test_alg(self, serial_number, test_log):
        """
        :type test_log: test_station.TestRecord
        :type serial_number: str
        """
        points = self._station_config.TEST_POINTS_POS

        for idx, br_pattern in enumerate(self._station_config.UNIF_PATTERNS):
            lv = []
            cx = []
            cy = []

            for unif_name, __ in points:
                vals = self._unif_raw_data.get('{0}_{1}'.format(br_pattern, unif_name))
                if not isinstance(vals, tuple):
                    continue
                cx.append(vals[0])
                cy.append(vals[1])
                lv.append(vals[2])
            if not (len(cx) == len(cy) == len(lv) != 0):
                continue

            lv = np.array(lv)
            cx = np.array(cx)
            cy = np.array(cy)

            keys = [x for x, __ in points]

            u = 4 * cx / (-2 * cx + 12 * cy + 3)
            v = 9 * cy / (-2 * cx + 12 * cy + 3)
            center_pos = [c for c, __ in points].index(self._station_config.CENTER_POINT_POS)
            center_u = u[center_pos]
            center_v = v[center_pos]

            # lv_data = [lv[x[1]] for x in points]
            # u_data = [u[x[1]] for x in points]
            # v_data = [v[x[1]] for x in points]
            lv_data = lv
            u_data = u
            v_data = v

            duv_data = np.sqrt((u_data - center_u)**2 + (v_data - center_v)**2)
            lv_dic = dict(zip(keys, lv_data))
            u_dic = dict(zip(keys, u_data))
            v_dic = dict(zip(keys, v_data))
            duv_dic = dict(zip(keys, duv_data))
            for posIdx, tes_pos in self._station_config.TEST_POINTS_POS:
                lv = lv_dic[posIdx]
                test_item = '{}_{}_Lv'.format(br_pattern, posIdx)
                test_log.set_measured_value_by_name_ex(test_item, lv)

                duv = duv_dic[posIdx]
                test_item = '{}_{}_duv'.format(br_pattern, posIdx)
                test_log.set_measured_value_by_name_ex(test_item, duv)

            max_lv = np.max(lv_data)
            min_lv = np.min(lv_data)
            test_item = '{}_Lv_max_variation'.format(br_pattern)
            test_log.set_measured_value_by_name_ex(test_item, (max_lv - min_lv) / max_lv)

            max_duv = np.max(duv_data)
            test_item = '{}_duv_max'.format(br_pattern)
            test_log.set_measured_value_by_name_ex(test_item, max_duv)

            for posIdx, grp in self._station_config.NEIGHBOR_POINTS:
                tmp = []
                for c in grp:
                    duv = duv_dic[c]
                    tmp.append(duv)
                    test_item = '{}_{}_{}_duv'.format(br_pattern, posIdx, c)
                    test_log.set_measured_value_by_name_ex(test_item, duv)
                max_duv = np.max(tmp)
                test_item = '{}_{}_neighbor_duv_max'.format(br_pattern, posIdx)
                test_log.set_measured_value_by_name_ex(test_item, max_duv)
