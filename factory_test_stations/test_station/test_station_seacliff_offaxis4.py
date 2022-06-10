import pprint
import socket
import hardware_station_common.test_station.test_station as test_station
import numpy as np
import os
import shutil
import time
import math
import datetime
import re
import filecmp
from test_station.dut import DUTError, pancakeDut
from test_station.test_fixture.test_fixture_seacliff_offaxis4 import SeacliffOffAxis4Fixture, SeacliffOffAxis4FixtureError
from test_station.test_fixture.test_fixture_project_station import projectstationFixture
from test_station.test_equipment.test_equipment_seacliff_offaxis4 import SeacliffOffAxis4Equipment, SeacliffOffAxis4EquipmentError
from test_station.dut.dut import projectDut, DUTError
from hardware_station_common.test_station.test_log.shop_floor_interface.shop_floor import ShopFloor
import hardware_station_common.utils as hsc_utils
from hardware_station_common.utils.io_utils import round_ex
import types
import glob
import sys
import shutil
import threading
from queue import Queue
import serial
import json
import socketserver
import urllib3
import keyboard


ms_client_list = {}
ms_receive_message_queue = Queue()
USER_SHUTDOWN_STATION = False


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    ip = None
    port = None
    timeout = 0.01

    def setup(self):
        self.ip = self.client_address[0].strip()
        self.port = self.client_address[1]
        self.request.settimeout(self.timeout)
        print(f'IP {self.ip} port: {self.port} is connected.')
        ms_client_list.update({f'{self.ip}': self.request})

    def handle(self):
        active = True
        end_char = b'@_@'
        total_data = b''
        while not USER_SHUTDOWN_STATION and active:
            try:
                rev_msg = self.request.recv(512)
                total_data += rev_msg
                while end_char in total_data:
                    cmd = total_data[:total_data.find(end_char)].decode(encoding='utf-8')
                    ms_receive_message_queue.put((self.ip, json.loads(cmd)))
                    print(f'handle---------{self.ip}__{cmd}-----------\n')
                    time.sleep(0.005)
                    total_data = total_data[(total_data.find(end_char) + len(end_char)):]
            except socket.timeout as e:
                pass
            except Exception as e:
                active = False
            time.sleep(0.01)

    def finish(self):
        print('client is disconnect!')
        ms_client_list.pop(f'{self.ip}')


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def client_msg(port, message, ip='localhost'):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        sock.sendall(message.encode('utf-8'))
        time.sleep(0.01)
        response = sock.recv(1024).decode('utf-8')
    return response


class SeacliffOffAxis4StationError(Exception):
    pass


class SeacliffOffAxis4Station(test_station.TestStation):
    def __init__(self, station_config, operator_interface):
        self._sw_version = '1.1.3'
        self._runningCount = 0
        test_station.TestStation.__init__(self, station_config, operator_interface)

        if self._station_config.IS_STATION_MASTER:
            self._fixture = projectstationFixture(station_config, operator_interface)
            if not station_config.FIXTURE_SIM:
                self._fixture = SeacliffOffAxis4Fixture(station_config, operator_interface)  # type: SeacliffOffAxis4Fixture
        radiantApiSettings = r'C:\Radiant Vision Systems Data\TrueTest\AppData\Config\TT_API AppSettings.json'
        if os.path.exists(radiantApiSettings):
            os.remove(radiantApiSettings)
        self._equipment = SeacliffOffAxis4Equipment(station_config)  # type: SeacliffOffAxis4Equipment
        self._overall_errorcode = ''
        self._first_failed_test_result = None
        self._ttxm_filelist = []
        self._is_slot_under_testing = False
        self._local_ctrl_queue = Queue(maxsize=0)
        self._work_flow_ctrl_event = threading.Semaphore(value=0)

        self._work_flow_ctrl_event_err_msg = None
        self._fixture_query_command = Queue(maxsize=0)
        self._shop_floor = None  # type: ShopFloor
        self._mutex = threading.Lock()

        self._major_ctrl_queue = Queue(maxsize=0)
        self._is_major_ctrl_under_testing = False

        self._multi_station_dic = dict([(k, {
            'SN': None,
            'IsPWR': False,
            'IP': None,
            'IsRunning': False,
            'IsActive': False,
            'IsAutoScanCode': False,
        }) for k in self._station_config.SUB_STATION_INFO.keys()])

        self.btn_status = {
            'DUAL_START': False,
            'PWR_A': False,
            'PWR_B': False,
            'VACCUM_A': False,
            'VACCUM_B': False,
        }
        self._station_status = {
            'Login': False,
        }
        self._err_msg_list = {
            1: 'Axis Z running error',
            2: 'This command is cancel by operator',
            3: 'DUT transfer is timeout',
            4: 'Signal from sensor (Door/Grating) is error',
            5: 'Signal from sensor (pressing plate) is not triggered',
        }
        self._the_unit = {}   # type: pancakeDut
        self.fixture_scanner_ports = {}
        self.fixture_port = None
        self.fixture_particle_port = None
        self._pool_manager = urllib3.PoolManager()

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

    def initialize(self):
        self._operator_interface.print_to_console(f"Initializing station...SW: {self._sw_version}\n")
        self._operator_interface.update_root_config({'IsStartLoopFromKeyboard': 'false'})
        self._operator_interface.update_root_config(
        {
            'IsScanCodeAutomatically': str(self._station_config.AUTO_SCAN_CODE),
            'ShowLogin': str(self._station_config.IS_STATION_MASTER),
        })

        # <editor-fold desc="Master">
        try:
            if self._station_config.IS_MULTI_STATION_MANAGER:
                msg = client_msg(port=self._station_config.MULTI_STATION_MANAGER_ADDR[1],
                                 message='00,OPEN',
                                 ip=self._station_config.MULTI_STATION_MANAGER_ADDR[0])
                online_substation = msg.split(';')
                self._operator_interface.print_to_console(f'Sub station: {online_substation}')
            if self._station_config.IS_STATION_MASTER:
                for k, v in self._station_config.SUB_STATION_INFO.items():
                    self._multi_station_dic[k]['IP'] = v['IP']

        except Exception as e:
            self._operator_interface.print_to_console(f'Fail to init this station as Master. {str(e)}\n')
        # </editor-fold>
        if self._station_config.IS_STATION_MASTER:
            # <editor-fold desc="port configuration automatically">
            cfg = 'station_config_seacliff_offaxis4x.json'
            station_config = {
                'FixtureCom': 'Fixture',
                'ScannerA': 'SR71001A',
                'ScannerB': 'SR71002A',
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
            # config the port for fixture
            regex_port = station_config['FixtureCom']
            com_ports = [c[0] for c in port_list if re.search(regex_port, c[2], re.I | re.S)]
            if len(com_ports) != 1:
                port_err_message.append(f'Fixture')
            else:
                self.fixture_port = com_ports[-1]

            # config the port for scanner
            for c in ['A', 'B']:
                reg_p = f'Scanner{c}'
                regex_port = station_config[reg_p]
                com_ports = [c[0] for c in port_list if re.search(regex_port, c[2], re.I | re.S)]
                if len(com_ports) > 0:
                    self.fixture_scanner_ports[c] = com_ports[-1]
                else:
                    port_err_message.append(f'Scanner {c}')

            # config the port for scanner
            if self._station_config.FIXTURE_PARTICLE_COUNTER and self._station_config.IS_MULTI_STATION_MANAGER:
                regex_port = station_config['ParticleCounter']
                com_ports = [c[0] for c in port_list if re.search(regex_port, c[2], re.I | re.S)]
                if len(com_ports) == 1:
                    self.fixture_particle_port = com_ports[-1]
                else:
                    port_err_message.append(f'Particle counter')
            # </editor-fold>
            if not self._station_config.FIXTURE_SIM and len(port_err_message) > 0:
                raise SeacliffOffAxis4StationError(f'Fail to find ports for fixture {";".join(port_err_message)}')

            server = ThreadedTCPServer(self._station_config.STATION_MASTER_ADDR, ThreadedTCPRequestHandler)
            server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()

            self._fixture.initialize(fixture_port=self.fixture_port,
                                     particle_port=self.fixture_particle_port)

            self._fixture.set_tri_color('y')
            for bk in ['A', 'B']:
                self._fixture.vacuum(False, bk_mode=bk)
                self._fixture.power_on_button_status(True, bk_mode=bk)
            self._fixture.button_enable()
            if not self._station_config.FIXTURE_SIM and self.alert_handle(self._fixture.unload()) != 0:
                raise SeacliffOffAxis4StationError(f'Fail to init the fixture.')
            for bk in ['A', 'B']:
                self._fixture.vacuum(False, bk_mode=bk)
                self._fixture.power_on_button_status(False, bk_mode=bk)
            self._fixture.button_disable()
            self._fixture.set_tri_color('g')

            if (self._station_config.IS_MULTI_STATION_MANAGER
                    and self._station_config.FIXTURE_PARTICLE_COUNTER):
                if self._fixture.particle_counter_state() == 0:
                    self._fixture.particle_counter_on()
                    particle_counter_start_time = datetime.datetime.now()

                    while ((datetime.datetime.now() - particle_counter_start_time)
                           < datetime.timedelta(self._station_config.FIXTRUE_PARTICLE_START_DLY)):
                        time.sleep(0.1)

        self._is_slot_under_testing = False

        conoscope_sn = 'None' if not self._station_config.EQUIPMENT_SIM else 'Demo'
        conoscope_sn_count = 5
        while re.match(r'^none$', conoscope_sn, re.I | re.S) and conoscope_sn_count > 0:
            conoscope_sn = self._equipment.serialnumber()
            conoscope_sn_count -= 1
            time.sleep(0.2)
        self._station_config.CAMERA_SN = conoscope_sn
        self._operator_interface.print_to_console("Initialize Camera SN = %s\n" % self._station_config.CAMERA_SN)
        if self._station_config.IS_STATION_MASTER:
            equ_res, equ_msg = self._equipment.initialize()
            threading.Thread(target=self._fixture_query_thr, daemon=True).start()
            if self._station_config.IS_MULTI_STATION_MANAGER:
                threading.Thread(target=self._station_monitor_ctrl_thr,
                                 daemon=True).start()  # read particle-counter from device.
            threading.Thread(target=self._station_master_ctrl_thr, daemon=True).start()  # used for master station.
            threading.Thread(target=self._btn_scan_thr, daemon=True).start()
            threading.Thread(target=self._station_slave_ctrl_thr, daemon=True).start()  # used for slave station.
            threading.Thread(target=self._http_local_client, daemon=True).start()
            self._shop_floor = ShopFloor()
        else:
            equ_res, equ_msg = self._equipment.initialize()
            threading.Thread(target=self._station_slave_ctrl_thr, daemon=True).start()  # used for slave station.
            threading.Thread(target=self._http_local_client, daemon=True).start()
        # threading.Thread(target=self._auto_backup_thr, daemon=True).start()
        if not equ_res:
            raise SeacliffOffAxis4StationError(f'Fail to init the conoscope: {equ_msg}')
        self._operator_interface.print_to_console(f'Wait for testing...', 'green')
        if self._station_config.FIXTURE_SIM:
            keyboard.add_hotkey('ctrl+q', self._fixture_btn_emulator, args=(self, None))

    def data_backup(self, source_path, target_path):
        if not os.path.exists(target_path):
            os.makedirs(target_path)
        if os.path.exists(source_path):
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    src_file = os.path.join(root, file)
                    shutil.move(src_file, target_path)

    # backup the raw data automatically
    def _auto_backup_thr(self):
        raw_dir = os.path.join(self._station_config.ROOT_DIR, self._station_config.ANALYSIS_RELATIVEPATH, 'raw')
        bak_dir = raw_dir
        if hasattr(self._station_config, 'ANALYSIS_RELATIVEPATH_BAK'):
            bak_dir = os.path.join(self._station_config.ROOT_DIR, self._station_config.ANALYSIS_RELATIVEPATH_BAK, 'raw')
        ex_file_list = []

        def date_time_check(fn):
            tm = None
            try:
                xx = fn[fn.rindex('_') + 1:]
                tm = datetime.datetime.strptime(xx, '%Y%m%d-%H%M%S').timestamp()
            except:
                pass
            return tm

        while not USER_SHUTDOWN_STATION:
            if self._is_slot_under_testing:
                time.sleep(0.5)
                continue
            if not(os.path.exists(bak_dir) and os.path.exists(raw_dir) and not os.path.samefile(bak_dir, raw_dir)):
                time.sleep(0.5)
                continue

            cur_time = datetime.datetime.now().hour + datetime.datetime.now().minute / 60
            if not (any([c1 <= cur_time <= c2 for c1, c2 in self._station_config.DATA_CLEAN_SCHEDULE]) and \
                    os.path.exists(raw_dir)):
                time.sleep(0.5)
                continue

            # backup all the data automatically

            uut_raw_dir = [(c, date_time_check(c)) for c in os.listdir(raw_dir)
                           if os.path.isdir(os.path.join(raw_dir, c))
                           and date_time_check(c)
                           and c not in ex_file_list]
            # backup all the raw data which is created about 8 hours ago.
            uut_raw_dir_old = [c for c, d in uut_raw_dir if
                               time.time() - d > self._station_config.DATA_CLEAN_SAVED_MINUTES]
            if len(uut_raw_dir_old) <= 0:
                time.sleep(1)
                continue
            n1 = uut_raw_dir_old[-1]
            try:
                self.data_backup(os.path.join(raw_dir, n1), os.path.join(os.path.join(bak_dir, n1)))

                # shutil.rmtree(os.path.join(raw_dir, n1))
            except Exception as e:
                ex_file_list.append(n1)
                self._operator_interface.print_to_console(f'Fail to backup file to {bak_dir}. Exp = {str(e)}')

    @staticmethod
    def _fixture_btn_emulator(self, cmd):
        self._operator_interface.print_to_console(f'emulator signal for dual-start: {self._is_slot_under_testing}')
        if not self._is_slot_under_testing and self._fixture_query_command.empty():
            self._fixture_query_command.put(('power_on', 'A'))
            self._fixture_query_command.put('dual_start')

    def __append_local_client_msg_q(self, cmd, args=None):
        cmd_text = json.dumps({'CMD': cmd, 'ARG': args})
        self._local_ctrl_queue.put(f'{cmd_text}@_@')

    def _http_local_client(self):
        local_client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        local_client_sock.connect(self._station_config.STATION_MASTER_ADDR)
        end_char = b'@_@'
        total_data = b''
        sock_exception = False
        while not USER_SHUTDOWN_STATION:
            try:
                local_client_sock.settimeout(0.010)
                rev_msg = local_client_sock.recv(512)
                if rev_msg != b'':
                    print(f'raw =============================recv command -------->{rev_msg}\n')
                    total_data += rev_msg
                while end_char in total_data:
                    cmd = total_data[:total_data.find(end_char)].decode(encoding='utf-8')
                    self._major_ctrl_queue.put(json.loads(cmd))
                    if self._station_config.IS_VERBOSE:
                        print(f'recv command -------->{cmd}')
                    time.sleep(0.02)
                    total_data = total_data[(total_data.find(end_char)+len(end_char)):]
            except socket.timeout as e:
                pass
            except Exception as e:
                if not sock_exception:
                    self._operator_interface.print_to_console(f'Fail to loop http_local_client. {str(e)} \n', 'red')
                    sock_exception = True

            if not self._local_ctrl_queue.empty():
                cmd = self._local_ctrl_queue.get()
                if isinstance(cmd, str):
                    local_client_sock.sendall(cmd.encode('utf-8'))
                    if self._station_config.IS_VERBOSE:
                        print(f'Send command to master --> {cmd}')
            time.sleep(0.01)

    def trans_ip_2_station_index(self, ip):
        tmp = [k for k, v in self._multi_station_dic.items() if v['IP'] == ip]
        return tmp[0] if len(tmp) == 1 else None

    def trans_station_index_2_ip(self, station_index):
        assert station_index in self._multi_station_dic.keys()
        return self._multi_station_dic[station_index]['IP']

    def send_command(self, station_index, cmd, args=None, err=None):
        try:
            self._mutex.acquire()
            assert station_index in self._multi_station_dic.keys()
            stationIp = self.trans_station_index_2_ip(station_index)
            if not stationIp:
                self._operator_interface.print_to_console(f'slot {station_index} is not connected.')
            elif not(stationIp in ms_client_list):
                self._operator_interface.print_to_console(f'socket for slot {station_index} is not connected.', 'red')
            else:
                psock = ms_client_list[stationIp]
                cmd_text = {'CMD': cmd, 'ARG': args, 'ERR': err}
                psock.sendall(f'{json.dumps(cmd_text)}@_@'.encode())
                if self._station_config.IS_VERBOSE:
                    print(f'send command --> {station_index}-------->{cmd}')
        except Exception as e:
            self._operator_interface.print_to_console(f'Fail to send command to {station_index}.  cmd = {cmd}, ex={str(e)}', 'red')
        finally:
            self._mutex.release()

    def _station_slave_ctrl_thr(self):
        status_bak = None
        while not USER_SHUTDOWN_STATION:
            time.sleep(0.05)
            current_status = {'active_status': self._station_config.IS_STATION_ACTIVE,
                              'auto_scan_code': self._station_config.AUTO_SCAN_CODE}
            if not self._station_config.AUTO_SCAN_CODE:
                current_status['ui_serial_number'] = self._operator_interface.current_serial_number()
            if current_status != status_bak:
                self.__append_local_client_msg_q('StatusChange', current_status)
                status_bak = current_status
            try:
                if not self._major_ctrl_queue.empty():
                    command = self._major_ctrl_queue.get()
                    if self._station_config.IS_VERBOSE:
                        print(f'station_slave_ctrl rev command <----  {command}')
                    cmd = command.get('CMD')
                    cmd_err = command.get('ERR')
                    self._work_flow_ctrl_event_err_msg = cmd_err
                    cmd1 = command.get('ARG')
                    if cmd == 'NextPatternAck':
                        self._work_flow_ctrl_event.release()
                    if cmd == 'MovToPosAck':
                        self._work_flow_ctrl_event.release()
                    elif cmd == 'FinishTestAck':
                        # TODO:
                        # 等待关闭DUT与MES 数据上传
                        self._work_flow_ctrl_event.release()
                    elif cmd == 'start_loop' and isinstance(cmd1, str):
                        self._operator_interface.print_to_console(f'Receive Start Loop: {cmd1}')
                        self._is_slot_under_testing = True
                        self._operator_interface.update_root_config({'SN': cmd1})
                        self._operator_interface.active_start_loop(cmd1)
                    elif cmd == 'UPDATE_SN':
                        self._operator_interface.update_root_config({'SN': cmd1 if cmd1 else ''})
                    elif cmd == 'StatusChangeMaster':
                        status = json.loads(cmd1)
                        self._station_config.FACEBOOK_IT_ENABLED = status.get('Login')
                        self._operator_interface.update_root_config({'IsUsrLogin': f'{self._station_config.FACEBOOK_IT_ENABLED}'})
                    elif cmd == 'CloseApp':
                        self._operator_interface.close_application()
            except Exception as e:
                self._operator_interface.print_to_console(f'Fail to slave_ctrl_thr: {str(e)}', 'red')

    def _station_master_ctrl_thr(self):
        while not USER_SHUTDOWN_STATION:
            try:
                if not ms_receive_message_queue.empty():
                    command = ms_receive_message_queue.get()
                    # if self._station_config.IS_VERBOSE:
                    print(f'station master ctrl thread. {command}\n')
                    if isinstance(command, tuple):  # command get from slave-station
                        ip = command[0]
                        cmd = command[1].get('CMD')
                        arg1 = command[1].get('ARG')
                        station_index = self.trans_ip_2_station_index(ip)
                        if station_index is None:
                            self._operator_interface.print_to_console(
                                f'Fail to find {ip} for this master station', 'red')
                        elif cmd == 'FinishTest':
                            self._multi_station_dic[station_index]['IsRunning'] = False
                            self._the_unit[station_index].screen_off()
                            self._operator_interface.print_to_console(f'Station {station_index} Finished.')
                            self.send_command(station_index, 'FinishTestAck')
                            if all([not c['IsRunning'] for k, c in self._multi_station_dic.items() if c['IsActive']]):
                                self._fixture_query_command.put('unload')
                        elif cmd == 'NextPattern' and isinstance(arg1, str):  # message slave ---> master
                            self.render_pattern(station_index, arg1)
                            self.send_command(station_index, 'NextPatternAck')
                        elif cmd == 'MovToPos' and isinstance(arg1, str):
                            x, y = tuple([int(c) for c in arg1.split(',')])
                            # self._fixture.mov_abs_xy(x, y)  # may be some error in multi-thread.
                            self.send_command(station_index, 'MovToPosAck')
                        elif cmd == 'StatusChange' and isinstance(arg1, dict):
                            self._multi_station_dic[station_index]['IsAutoScanCode'] = arg1.get('auto_scan_code')
                            self._multi_station_dic[station_index]['IsActive'] = arg1.get('active_status')
                            if arg1.get('auto_scan_code') is False and 'ui_serial_number' in arg1:
                                self._multi_station_dic[station_index]['SN'] = arg1.get('ui_serial_number')

                        # elif cmd == 'start_loop':  # master ---> master
                        #     self._is_under_testing = True
                        #     sn = self._multi_station_dic['A']['SN']
                        #     # TODO:
                        #     sn = 'T004'
                        #     self._operator_interface.update_root_config({'SN': sn})
                        #     self._operator_interface.active_start_loop(sn)
            except Exception as e:
                self._operator_interface.print_to_console(f'Fail to master_ctrl: {str(e)}', 'red')
            finally:
                time.sleep(0.05)

    def _station_monitor_ctrl_thr(self):
        partical_counter_data = []
        partical_counter_data_grp_len = 10
        if not (os.path.exists(self._station_config.SHARED_DATA_PATH)
                and os.path.isdir(self._station_config.SHARED_DATA_PATH)):
            hsc_utils.mkdir_p(self._station_config.SHARED_DATA_PATH)
        # save the latest readings from the particle counter to disk, the sub-stations should read it from network-disk.
        while not USER_SHUTDOWN_STATION:
            try:
                val = self._fixture.particle_counter_read_val() if self._station_config.FIXTURE_PARTICLE_COUNTER else 0
                if val is None:
                    continue
                partical_counter_data.append(val)
                if len(partical_counter_data) >= partical_counter_data_grp_len:
                    with open(os.path.join(self._station_config.SHARED_DATA_PATH, 'particles.json'), 'w') as f:
                        json.dump({'particles': partical_counter_data}, f, indent=2)
                    partical_counter_data.clear()
            except SeacliffOffAxis4FixtureError as e:
                self._operator_interface.print_to_console(f'Fail to read particle count {str(e)}', 'red')
            finally:
                time.sleep(0.1)

    def _web_request_cmd(self, method, channel):
        res = None
        try:
            r = self._pool_manager.request('GET', method, fields={'id': channel}, timeout=1)
            if r.status == 200:
                res = r.data.decode(encoding='utf-8')
        except Exception as e:
            self._operator_interface.print_to_console(f'Fail to query: {method}: {channel}: {str(e)}')
        return res

    def _fixture_query_thr(self):
        while not USER_SHUTDOWN_STATION:
            time.sleep(0.01)
            try:
                if self._fixture_query_command.empty():
                    grp_btn_ab_status = False
                    for k, v in self._multi_station_dic.items():
                        pwr_status = False
                        if not v['IsRunning'] and v['IsActive']:
                            pwr_status = True
                        if pwr_status != self.btn_status[f'PWR_{k}']:
                            self._fixture_query_command.put(f'pwron_status:{k}_{pwr_status}')

                    grp = [v for k, v in self._multi_station_dic.items() if v['IsActive']]
                    if (len(grp) > 0
                            and all([c['SN'] is not None and c['IsPWR'] for c in grp])  # SN should be set correctly
                            and all([not c['IsRunning'] for c in grp])):  # Not running
                        grp_btn_ab_status = True  # if so, should change the status for dual start button
                    if grp_btn_ab_status != self.btn_status['DUAL_START']:
                        self._fixture_query_command.put(f'dual_start:{grp_btn_ab_status}')
                        self._operator_interface.print_to_console(
                            f'Change dual_start status: {self.btn_status["DUAL_START"]} -> {grp_btn_ab_status}')
                    time.sleep(0.05)
                    continue  # Try to change the status of the fixture
                cmd = self._fixture_query_command.get()
                if self._station_config.IS_VERBOSE:
                    print(f'fixture query command: {cmd}\n')
                if isinstance(cmd, str) and re.match('StatusChangeMaster', cmd, re.I):
                    for channel, v in self._multi_station_dic.items():
                        self.send_command(channel, 'StatusChangeMaster', json.dumps(self._station_status, indent=2))

                elif isinstance(cmd, str) and re.match('pwron_status:[A|B]_(?:true|false)', cmd, re.I | re.S):
                    cmd1 = cmd.split(':')[1].split('_')[0]
                    cmd2 = cmd.split(':')[1].split('_')[1].lower() in ['true']
                    if cmd2:
                        self._fixture.power_on_button_status(True, bk_mode=cmd1)
                    else:
                        self._fixture.power_on_button_status(False, bk_mode=cmd1)
                    self.btn_status[f'PWR_{cmd1}'] = cmd2
                elif isinstance(cmd, str) and re.match('vacuum_status:[A|B]_(?:true|false)', cmd, re.I | re.S):
                    cmd1 = cmd.split(':')[1].split('_')[0]
                    cmd2 = cmd.split(':')[1].split('_')[1].lower() in ['true']
                    if cmd2:
                        self._fixture.vacuum(True, bk_mode=cmd1)
                    else:
                        self._fixture.vacuum(False, bk_mode=cmd1)
                    self.btn_status[f'VACCUM_{cmd1}'] = cmd2
                elif isinstance(cmd, str) and re.match('dual_start:(?:true|false)', cmd, re.I | re.S):
                    cmd1 = cmd.split(':')[1].lower() in ['true']
                    if cmd1:
                        self._fixture.button_enable()
                    else:
                        self._fixture.button_disable()
                    self.btn_status['DUAL_START'] = cmd1
                elif isinstance(cmd, str) and re.match(r'mov_pos:\d+,\d+', cmd, re.I | re.S):
                    x, y = tuple([int(c) for c in cmd.split(':')[1].split(',')])
                    self._fixture.mov_abs_xy(x, y)
                    self._fixture_query_command.put(f'dual_start_post')
                elif cmd == 'dual_start':
                    self._is_major_ctrl_under_testing = True
                    self.btn_status['DUAL_START'] = False
                    # self._fixture.load()  # carry the DUTs to the expected position automatically.
                    self._fixture_query_command.put('pwron_status:A_False')
                    self._fixture_query_command.put('pwron_status:B_False')
                    self._fixture_query_command.put('vacuum_status:A_False')
                    self._fixture_query_command.put('vacuum_status:B_False')
                    self._fixture_query_command.put('mov_pos:0,0')
                elif cmd == 'dual_start_post':
                    for k, v in self._multi_station_dic.items():
                        if v['IsActive']:  # and v['SN']:
                            self.send_command(k, 'start_loop', self._multi_station_dic[k]['SN'])
                            self._multi_station_dic[k]['IsRunning'] = True
                        # it says the dual btn was disabled
                elif cmd == 'unload':
                    self.alert_handle(self._fixture.unload())
                    for channel, v in self._multi_station_dic.items():
                        if v['IsActive']:
                            self._update_sn(channel, None)
                            web_scanner_id = self._station_config.SUB_STATION_INFO[channel]['WebScannerId']
                            self._web_request_cmd(self._station_config.WEB_SCAN_CLR, web_scanner_id)
                    self._is_major_ctrl_under_testing = False
                elif isinstance(cmd, tuple) and len(cmd) == 2 and cmd[0] == 'power_on':
                    channel = cmd[1].upper()
                    if not self._multi_station_dic[channel]['IsActive']:
                        continue
                    assert channel in self._station_config.SUB_STATION_INFO.keys()
                    if self._multi_station_dic[channel]['SN'] is not None and self._multi_station_dic[channel]['IsPWR']:
                        self._the_unit[channel].screen_off()
                        self._the_unit[channel] = None
                        if self._multi_station_dic[channel]['IsAutoScanCode'] is True:
                            self._update_sn(channel, None)
                        self._the_unit[channel] = None
                        self._multi_station_dic[channel]['IsPWR'] = False
                        continue
                    if self._multi_station_dic[channel]['IsAutoScanCode'] is True:
                        if self._station_config.AUTO_SCAN_USE_WEB_SCAN:
                            web_scanner_id = self._station_config.SUB_STATION_INFO[channel]['WebScannerId']
                            sn = self._web_request_cmd(self._station_config.WEB_SCAN_REQ, web_scanner_id)
                        else:
                            sn = self._fixture.scan_code(self.fixture_scanner_ports[channel])
                    else:
                        sn = self._multi_station_dic[channel]['SN']
                    if not isinstance(sn, str) or len(sn.strip()) == 0 or 'ERROR' in sn:
                        self._operator_interface.print_to_console(f'Unable to scan code Station:{channel} --> SN:{sn}\n', 'red')
                        continue
                    if not self.validate_sn(serial_num=sn):
                        self._operator_interface.print_to_console(f'Fail to validate Serial Number : {sn}\n', 'red')
                    else:
                        sf_res = self._shop_floor.ok_to_test(serial_number=sn)
                        if sf_res is True or (isinstance(sf_res, tuple) and sf_res[0]):
                            self._fixture.vacuum(False, channel)
                            if channel in self._station_config.DUT_ADDR:
                                v = self._station_config.DUT_ADDR[channel]
                                self._the_unit[channel] = projectDut(sn, self._station_config, self._operator_interface)
                                if not self._station_config.DUT_SIM:
                                    self._the_unit[channel] = pancakeDut(sn, self._station_config, self._operator_interface)
                                self._the_unit[channel].initialize(eth_addr=v['eth'], com_port=v['com'])
                            pw_res = self._the_unit[channel].screen_on(ignore_err=True)
                            if self._station_config.DUT_SIM or pw_res is True:
                                self._multi_station_dic[channel]['IsPWR'] = True
                                self._update_sn(channel, sn)
                                self._operator_interface.print_to_console(f'Set SN {sn} to slot_{channel}.')
                                if all([v['SN'] is not None for k, v in self._multi_station_dic.items() if v['IsActive']]):
                                    pass
                                    # Active dual start button
                            else:
                                self._operator_interface.print_to_console(f'Fail to power on: {sn}, {pw_res}\n', 'red')
                                self._the_unit[channel].screen_off()
                                self._the_unit[channel] = None
                        else:
                            self._operator_interface.print_to_console(f'MES response info: {sn}, {sf_res}\n', 'red')
            except Exception as e:
                self._operator_interface.print_to_console(f'Fail to fixture_query_thr : {str(e)}\n', 'red')

    def _update_sn(self, station_index, sn):
        self._multi_station_dic[station_index]['SN'] = sn
        self.send_command(station_index, 'UPDATE_SN', sn)

    def _btn_scan_thr(self):
        while not USER_SHUTDOWN_STATION:
            time.sleep(0.05)
            if not self._fixture_query_command.empty() or self._is_major_ctrl_under_testing or not self._fixture:
                continue

            try:
                key_ret_info = self._fixture.is_ready()
                query_key_cmd_list = {
                    0: 'dual_start',
                    3: ('power_on', 'A'),
                    4: ('power_on', 'B'),
                    1: ('power_on', 'B'),
                }
                if isinstance(key_ret_info, tuple):
                    ready_key, ready_code = key_ret_info
                    if ready_key in query_key_cmd_list and ready_code == 0:
                        self._fixture_query_command.put(query_key_cmd_list.get(ready_key))
                    elif ready_key == 0 and ready_code in self._err_msg_list:
                        self._operator_interface.print_to_console(f'Please note: {self._err_msg_list.get(ready_code)}.\n')
                        self.alert_handle(ready_code)
                    else:
                        self._operator_interface.print_to_console(f'Recv command not handled: {ready_key} \n')
            except Exception as e:
                self._operator_interface.print_to_console(f'Fail to btn scan thread : {str(e)}\n', 'red')

    def alert_handle(self, ready_code):
        alert_res = ready_code
        while alert_res in [4, 5]:
            self._operator_interface.operator_input('Hint', self._err_msg_list.get(alert_res), msg_type='warning',
                                                    msgbtn=0)
            alert_res = self._fixture.reset()
        if alert_res not in [0, None]:
            self._operator_interface.print_to_console(f'Please note: {self._err_msg_list.get(alert_res)}.\n', 'red')
        return alert_res

    def render_pattern(self, station_index, test_pattern):
        assert station_index in self._multi_station_dic.keys()
        assert test_pattern in self._station_config.TEST_PATTERNS

        pattern_color = self._station_config.TEST_PATTERNS.get(test_pattern)['P']
        if isinstance(pattern_color, tuple):
            self._the_unit[station_index].display_color(pattern_color)
        elif isinstance(pattern_color, (str, int)):
            self._the_unit[station_index].display_image(pattern_color)
        self._operator_interface.print_to_console(f'Set DUT {station_index} To Color: {pattern_color}.\n')

    def close(self):
        global USER_SHUTDOWN_STATION
        try:
            for k, v in self._multi_station_dic.items():
                if v.get('IP') is not None:
                    self.send_command(k, 'CloseApp')
            time.sleep(0.05)
        except:
            pass
        USER_SHUTDOWN_STATION = True
        try:
            self._fixture.close()
            self._fixture = None
        except:
            pass
        try:
            self._equipment.close()
            self._equipment = None
        except:
            pass

    def _do_test(self, serial_number, test_log):
        # type: (str, test_station.test_log) -> tuple
        test_log.set_measured_value_by_name_ex = types.MethodType(self.chk_and_set_measured_value_by_name, test_log)
        self._overall_result = False
        self._overall_errorcode = ''
        self._work_flow_ctrl_event_err_msg = None
        try:
            # self._fixture.flush_data()
            self._operator_interface.print_to_console("Testing Unit %s\n" % serial_number)
            test_log.set_measured_value_by_name_ex('SW_VERSION', self._sw_version)

            test_log.set_measured_value_by_name_ex("MPK_API_Version", self._equipment.version())
            self._operator_interface.print_to_console("Read the particle count in the fixture... \n")
            particle_count = 0
            if self._station_config.FIXTURE_PARTICLE_COUNTER:
                particles = None
                particles_read_timeout = 0
                while not isinstance(particles, list) and particles_read_timeout < 10:
                    try:
                        if os.path.exists(os.path.join(self._station_config.SHARED_DATA_PATH, 'particles.json')):
                            with open(os.path.join(self._station_config.SHARED_DATA_PATH, 'particles.json'), 'r') as f:
                                particles = json.load(f)['particles']
                    except Exception as e:
                        pass
                    particles_read_timeout += 1
                    time.sleep(0.01)
                if isinstance(particles, list) and len(particles) > 1:
                    particle_count = int(np.average(particles))
                else:
                    self._operator_interface.print_to_console(f'Fail to read particles. data = {particles} \n')
            test_log.set_measured_value_by_name_ex("ENV_ParticleCounter", particle_count)

            self._operator_interface.print_to_console("Set Camera Database. %s\n" % self._station_config.CAMERA_SN)

            sequencePath = os.path.join(self._station_config.ROOT_DIR, self._station_config.SEQUENCE_RELATIVEPATH)
            self._equipment.set_sequence(sequencePath)

            self._operator_interface.print_to_console("Close the eliminator in the fixture... \n")

            self.offaxis_test_do(serial_number, test_log)

            if not self._station_config.IS_SAVEDB:
                self._operator_interface.print_to_console("!!!Remove ttxms to save disk-space.!!!\n")
                #  it is sometimes fail to remove ttxm cause the file is occupied by TrueTest
                file_list_to_removed = [c for c in self._ttxm_filelist if os.path.exists(c)]
                [shutil.rmtree(c, ignore_errors=True) for c in file_list_to_removed]
                self._ttxm_filelist = file_list_to_removed.copy()

        except Exception as e:
            self._operator_interface.print_to_console("Test exception {0}.\n".format(e))
        finally:
            self._operator_interface.print_to_console('close the test_log for {}.\n'.format(serial_number))
            overall_result, first_failed_test_result = self.close_test(test_log)

            self.__append_local_client_msg_q('FinishTest')
            self._work_flow_ctrl_event.acquire()
            self._operator_interface.print_to_console(
                f'release current test resource. {self._work_flow_ctrl_event_err_msg}\n',
                'red' if self._work_flow_ctrl_event_err_msg else None)

            self._runningCount += 1
            self._operator_interface.print_to_console('--- do test finished ---\n')
            return overall_result, first_failed_test_result

    def close_test(self, test_log):
        result_array = test_log.results_array()
        ui_msg = {
            'LA': 'L (左眼)',
            'RA': 'R (右眼)',
            'AA': 'L/R(左/右眼)',
            'FAIL': 'FAIL'
        }

        # based ERS provided by Vic
        test_log.set_measured_value_by_name_ex('EXT_CTRL_RES', '')
        ext_ctrl_duv_any = self._station_config.EXT_CTRL_duv_ANY
        ext_ctrl_lv_any = self._station_config.EXT_CTRL_Lv_ANY
        ext_ctrl_asym_duv = self._station_config.EXT_CTRL_ASYM_duv
        ext_ctrl_cr_duv = self._station_config.EXT_CTRL_CR_ANY
        ext_ctrl_duv_lr_all = self._station_config.EXT_CTRL_duv_LR_ALL

        all_spec_items = []
        [all_spec_items.extend(c['Items']) for c in
         ext_ctrl_duv_any + ext_ctrl_lv_any + ext_ctrl_asym_duv + ext_ctrl_cr_duv]

        if any(result_array[c].get_measured_value() is None for c in all_spec_items):
            raise test_station.TestStationProcessControlError(f'Fail to test this DUT. 测试产品失败， 请重新测试')

        def ext_fail_check(array):
            sub_items = []
            for item in array:
                lsl, usl = item.get('SPEC')
                items = item.get('Items')
                sub_items.append([lsl <= result_array[c].get_measured_value() <= usl for c in items])
            return sub_items

        def ext_value_check(array):
            sub_items = []
            for item in array:
                items = item.get('Items')
                sub_items.append([result_array[c].get_measured_value() for c in items])
            return sub_items

        duv_any_result = ext_fail_check(ext_ctrl_duv_any)
        asym_duv_result = ext_fail_check(ext_ctrl_asym_duv)
        lv_any_result = ext_fail_check(ext_ctrl_lv_any)
        cr_duv_result = ext_fail_check(ext_ctrl_cr_duv)
        duv_lr_all_result = ext_fail_check(ext_ctrl_duv_lr_all)
        test_log.set_measured_value_by_name_ex('EXT_ANY_duv', np.array(duv_any_result).all())
        test_log.set_measured_value_by_name_ex('EXT_ASYM_duv', np.array(asym_duv_result).all(axis=1).any())
        test_log.set_measured_value_by_name_ex('EXT_RES_Lv', np.array(lv_any_result).all())
        test_log.set_measured_value_by_name_ex('EXT_RES_CR', np.array(cr_duv_result).all())

        ext_ctl_val = 'FAIL'
        if (np.array(duv_any_result).all() and np.array(asym_duv_result).all(axis=1).any()
                and np.array(lv_any_result).all() and np.array(cr_duv_result).all()):
            # if Max duv =< 0.01 at all azimuth
            ext_values = ext_value_check(ext_ctrl_duv_lr_all)
            max_ext_values = np.array(ext_values).max(axis=1)
            if np.array(asym_duv_result).all():
                if np.array(duv_lr_all_result).all(axis=1)[0] and np.array(duv_lr_all_result).all(axis=1)[1]:
                    ext_ctl_val = 'AA'
                    self._operator_interface.print_to_console(f'Max duv <= (to be verified)   at all  azimuth  Φ')
                else:
                    if max_ext_values[0] > max_ext_values[1]:
                        ext_ctl_val = 'LA'
                        self._operator_interface.print_to_console(
                            f'Max duv {max_ext_values}  at azimuth  Φ 180 <  Max duv at  Φ  0 degree')
                    else:
                        ext_ctl_val = 'RA'
                        self._operator_interface.print_to_console(
                            f'Max duv {max_ext_values} at azimuth  Φ 180 >  Max duv at  Φ  0 degree')
            # np.array(duv_any_result).all()
            elif np.array(asym_duv_result).all(axis=1)[0] and not np.array(asym_duv_result).all(axis=1)[1]:
                ext_ctl_val = 'RA'
                self._operator_interface.print_to_console(
                    f'Max duv {max_ext_values} <= (to be verified ) at  Φ  0 azimuth deg , Ok  for Right')
            elif not np.array(asym_duv_result).all(axis=1)[0] and np.array(asym_duv_result).all(axis=1)[1]:
                ext_ctl_val = 'LA'
                self._operator_interface.print_to_console(
                    f'Max duv {max_ext_values} <= (to be verified ) at Φ 180 azimuth deg , OK for left')
            else:
                raise test_station.TestStationProcessControlError(f'Fail to test this DUT. 测试产品失败， 请重新测试')

        test_log.set_measured_value_by_name_ex('EXT_CTRL_RES', ext_ctl_val)
        test_log.get_overall_result()
        if ext_ctl_val in ['LA', 'RA', 'AA']:
            self._overall_result = True
            test_log._overall_did_pass = True
            test_log._overall_error_code = 0
        self._operator_interface.update_root_config({'ResultMsgEx': ui_msg.get(ext_ctl_val)})

        # save_pnl_dic = self._station_config.SAVE_PNL_IF_FAIL
        # ui_msg = {
        #     'LA': 'L (左眼)',
        #     'RA': 'R (右眼)'
        # }
        # test_log.set_measured_value_by_name_ex('EXT_CTRL_RES', '')
        # self._overall_result = test_log.get_overall_result()
        # # modified the test result if ok_for_left/right
        # if not self._overall_result and set(ui_msg.keys()).issubset(save_pnl_dic.keys()):
        #     save_pnl_dic_left = [result_array[c].did_pass() for c in save_pnl_dic['LA']]
        #     save_pnl_dic_right = [result_array[c].did_pass() for c in save_pnl_dic['RA']]
        #     ext_ctl_val = None
        #     if (False in save_pnl_dic_left) and (False not in save_pnl_dic_right):
        #         test_log.set_measured_value_by_name_ex('EXT_CTRL_RES', 'LA')
        #         ext_ctl_val = 'LA'
        #     elif (False not in save_pnl_dic_left) and (False in save_pnl_dic_right):
        #         test_log.set_measured_value_by_name_ex('EXT_CTRL_RES', 'RA')
        #         ext_ctl_val = 'RA'
        #     else:
        #         test_log.set_measured_value_by_name_ex('EXT_CTRL_RES', 'FAIL')
        #         ext_ctl_val = 'FAIL'
        #     if ext_ctl_val in ui_msg.keys():
        #         test_log.get_overall_result()
        #         self._overall_result = True
        #         test_log._overall_did_pass = True
        #         test_log._overall_error_code = 0
        #         self._operator_interface.update_root_config({'ResultMsgEx': ui_msg[ext_ctl_val]})
        #     if not self._overall_result and len([k for k, v in result_array.items()
        #                                          if v.get_measured_value() is None]) > 0:
        #         raise test_station.TestStationProcessControlError(f'Fail to test this DUT. 测试产品失败， 请重新测试')
        # else:
        #     test_log.set_measured_value_by_name_ex('EXT_CTRL_RES', 'AA')
        #     self._operator_interface.update_root_config({'ResultMsgEx': 'L/R(左/右眼)'})

        self._first_failed_test_result = test_log.get_first_failed_test_result()
        return self._overall_result, self._first_failed_test_result

    def validate_sn(self, serial_num):
        return test_station.TestStation.validate_sn(self, serial_num)

    def is_ready(self):
        return True

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

    def offaxis_test_do(self, serial_number, test_log: test_station.test_log.TestRecord):
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

            # if self._station_config.IS_STATION_MASTER:
            #     self._operator_interface.print_to_console("Panel Mov To Pos: {}.\n".format(pos))
            #     self.__append_local_client_msg_q('MovToPos', f'{pos[0]},{pos[1]}')
            #     self._work_flow_ctrl_event.acquire()

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

                self.__append_local_client_msg_q('NextPattern', f'{pattern}')
                self._work_flow_ctrl_event.acquire()

                if self._work_flow_ctrl_event_err_msg:
                    raise SeacliffOffAxis4StationError(
                        f'Fail to show next pattern {pattern}. {self._work_flow_ctrl_event_err_msg}')
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

                        lv_match = re.search(r'(P_[0-9.]+\d*_[0-9.]+\d*)\((lv|Luminance|LuminousIntensity)\)', r, re.I | re.S)
                        if lv_match:
                            lv_dic[lv_match.groups()[0]] = float(result[ra])
                        cx_match = re.search(r'(P_[0-9.]+\d*_[0-9.]+\d*)\(cx\)', r, re.I|re.S)
                        if cx_match:
                            cx_dic[cx_match.groups()[0]] = float(result[ra])
                        cy_match = re.search(r'(P_[0-9.]+\d*_[0-9.]+\d*)\(cy\)', r, re.I|re.S)
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
                        duvs = np.sqrt((np.array(us) - us0)**2 + (np.array(vs) - vs0)**2)
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
                    test_log.set_measured_value_by_name_ex(test_item, round_ex(tlv, 1))

                for item in self._station_config.COLOR_PRIMARY_AT_POLE_AZI:
                    u = u_dic.get(f'P_%s_%s' % item)
                    v = v_dic.get(f'P_%s_%s' % item)
                    if u is None or v is None:
                        continue
                    test_item = '{}_{}_u_{}_{}'.format(posIdx, pattern, *item)
                    test_log.set_measured_value_by_name_ex(test_item, round_ex(u, ndigits=4))
                    test_item = '{}_{}_v_{}_{}'.format(posIdx, pattern, *item)
                    test_log.set_measured_value_by_name_ex(test_item, round_ex(v, ndigits=4))

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
                    test_log.set_measured_value_by_name_ex(test_item, tlv, round_ex(tlv, 3))

                for item in self._station_config.COLORSHIFT_AT_POLE_AZI:
                    duv = duv_dic.get('P_%s_%s' % item)
                    if duv is None:
                        continue
                    test_item = '{}_{}_duv_{}_{}'.format(posIdx, pattern, *item)
                    test_log.set_measured_value_by_name_ex(test_item, duv, round_ex(duv, 3))
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
                    test_log.set_measured_value_by_name_ex(test_item, cr, round_ex(cr, 1))
            # endregion

            self.data_export(serial_number, test_log, posIdx)

            if self._station_config.IS_EXPORT_RAW_DATA:
                for export_posIdx, export_raw_data_patterns in self._station_config.EXPORT_RAW_DATA_PATTERN.items():
                    if posIdx != export_posIdx or len(export_raw_data_patterns) <= 0:
                        continue
                    export_raw_data = np.empty(
                        (len(self._station_config.EXPORT_RAW_DATA_PATTERN_POLE),
                         len(self._station_config.EXPORT_RAW_DATA_PATTERN_AZI) * len(export_raw_data_patterns) + 1), np.float)
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
                        uni_file_name = re.sub('_x.log', '', test_log.get_filename())
                        bak_dir = os.path.join(self._station_config.ROOT_DIR,
                                               self._station_config.ANALYSIS_RELATIVEPATH, 'raw')
                        raw_data_dir = os.path.join(bak_dir, uni_file_name)
                        if not os.path.exists(raw_data_dir):
                            hsc_utils.mkdir_p(raw_data_dir)

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

    def login(self, active, usr, pwd):
        login_success = False
        if not active:
            login_success = True
            self._station_status['Login'] = False
        else:
            try:
                login_msg = self._shop_floor.login(usr, pwd)
                if (login_msg is True) or (isinstance(login_msg, tuple) and login_msg[0] is True):
                    self._station_status['Login'] = True
                    login_success = True
                else:
                    self._operator_interface.print_to_console(f'Fail to login usr:{usr}, Data = {login_msg}')
            except Exception as e:
                self._operator_interface.print_to_console(f'Fail to login usr:{usr}, Except={str(e)}')
        self._fixture_query_command.put(f'StatusChangeMaster')
        return login_success
