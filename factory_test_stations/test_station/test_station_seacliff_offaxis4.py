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
import hardware_station_common.utils.os_utils as os_utils
import types
import glob
import sys
import shutil
import threading
from queue import Queue
import serial
import json
import socketserver


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
        self._sw_version = '1.0.0'
        self._runningCount = 0
        test_station.TestStation.__init__(self, station_config, operator_interface)

        if self._station_config.IS_STATION_MASTER:
            self._fixture = projectstationFixture(station_config, operator_interface)
            if not station_config.FIXTURE_SIM:
                self._fixture = SeacliffOffAxis4Fixture(station_config, operator_interface)  # type: SeacliffOffAxis4Fixture

        self._equipment = SeacliffOffAxis4Equipment(station_config)  # type: SeacliffOffAxis4Equipment
        self._overall_errorcode = ''
        self._first_failed_test_result = None
        self._ttxm_filelist = []
        self._is_slot_under_testing = False
        self._local_ctrl_queue = Queue(maxsize=0)
        self._work_flow_ctrl_event = threading.Event()
        self._work_flow_ctrl_event_err_msg = None
        self._fixture_query_command = Queue(maxsize=0)
        self._shop_floor = None  # type: ShopFloor
        self._mutex = threading.Lock()

        self._major_ctrl_queue = Queue(maxsize=0)
        self._is_major_ctrl_under_testing = False

        self._multi_station_dic = dict([(k, {
            'SN': None,
            'IP': None,
            'IsRunning': False,
            'IsActive': False,
        }) for k in self._station_config.SUB_STATION_INFO.keys()])

        self.btn_status = {
            'DUAL_START': False,
            'PWR_A': False,
            'PWR_B': False,
            'VACCUM_A': False,
            'VACCUM_B': False,
        }

        self._the_unit = {}   # type: pancakeDut
        self.fixture_scanner_ports = {}
        self.fixture_port = None
        self.fixture_particle_port = None

    def chk_and_set_measured_value_by_name(self, test_log, item, value):
        """
        :type test_log: test_station.TestRecord
        """
        if item in test_log.results_array():
            test_log.set_measured_value_by_name(item, value)
            did_pass = test_log.get_test_by_name(item).did_pass()
            self._operator_interface.update_test_value(item, value, 1 if did_pass else -1)

    def initialize(self):
        self._operator_interface.update_root_config({'IsScanCodeAutomatically': str(self._station_config.AUTO_SCAN_CODE)})
        self._operator_interface.print_to_console(f"Initializing station...SW: {self._sw_version} SP2\n")
        self._operator_interface.update_root_config({'IsStartLoopFromKeyboard': 'false'})

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

        if self._station_config.IS_STATION_MASTER:
            self._fixture.initialize(fixture_port=self.fixture_port,
                                     particle_port=self.fixture_particle_port)
            if (self._station_config.IS_MULTI_STATION_MANAGER
                    and self._station_config.FIXTURE_PARTICLE_COUNTER):
                if self._fixture.particle_counter_state() == 0:
                    self._fixture.particle_counter_on()
                    particle_counter_start_time = datetime.datetime.now()

                    while ((datetime.datetime.now() - particle_counter_start_time)
                           < datetime.timedelta(self._station_config.FIXTRUE_PARTICLE_START_DLY)):
                        time.sleep(0.1)

        self._is_slot_under_testing = False
        self._shop_floor = ShopFloor()
        threading.Thread(target=self._fixture_query_thr, daemon=True).start()
        threading.Thread(target=self._station_monitor_ctrl_thr, daemon=True).start()  # read particle-counter from device.
        if self._station_config.IS_STATION_MASTER:
            server = ThreadedTCPServer(self._station_config.STATION_MASTER_ADDR, ThreadedTCPRequestHandler)
            server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()

            self._operator_interface.print_to_console("Initialize Camera %s\n" % self._station_config.CAMERA_SN)
            self._equipment.initialize()
            threading.Thread(target=self._station_master_ctrl_thr, daemon=True).start()  # used for master station.
            threading.Thread(target=self._btn_scan_thr, daemon=True).start()

            threading.Thread(target=self._station_slave_ctrl_thr, daemon=True).start()  # used for slave station.
            threading.Thread(target=self._http_local_client, daemon=True).start()
        else:
            self._operator_interface.print_to_console("Initialize Camera %s\n" % self._station_config.CAMERA_SN)
            self._equipment.initialize()
            threading.Thread(target=self._station_slave_ctrl_thr, daemon=True).start()  # used for slave station.
            threading.Thread(target=self._http_local_client, daemon=True).start()

        self._operator_interface.print_to_console(f'Wait for testing...', 'green')

    def _fixture_btn_emulator(self, arg):
        self._operator_interface.print_to_console(f'emulator signal for dual-start: {self._is_slot_under_testing}')
        if not self._is_slot_under_testing and self._fixture_query_command.empty():
            self._fixture_query_command.put('dual_start')

    def __append_local_client_msg_q(self, cmd, args=None):
        cmd_text = json.dumps({'CMD': cmd, 'ARG': args})
        self._local_ctrl_queue.put(f'{cmd_text}@_@')

    def _http_local_client(self):
        local_client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        local_client_sock.connect(self._station_config.SERV_ADDR)
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
        active_status_bak = None
        while not USER_SHUTDOWN_STATION:
            time.sleep(0.05)
            if active_status_bak is None or active_status_bak != self._station_config.IS_STATION_ACTIVE:
                active_status_bak = self._station_config.IS_STATION_ACTIVE
                self.__append_local_client_msg_q('ActiveStatus', active_status_bak)
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
                        self._work_flow_ctrl_event.set()
                    if cmd == 'MovToPosAck':
                        self._work_flow_ctrl_event.set()
                    elif cmd == 'FinishTestAck':
                        # TODO:
                        # 等待关闭DUT与MES 数据上传
                        self._work_flow_ctrl_event.set()
                    elif cmd == 'start_loop' and isinstance(cmd1, str):
                        self._is_slot_under_testing = True
                        self._work_flow_ctrl_event.clear()
                        self._operator_interface.update_root_config({'SN': cmd1})
                        self._operator_interface.active_start_loop(cmd1)
                        self._work_flow_ctrl_event.set()
                    elif cmd == 'UPDATE_SN':
                        self._operator_interface.update_root_config({'SN': cmd1 if cmd1 else ''})
                    elif cmd == 'CloseApp':
                        sys.exit(0)
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
                            self._fixture.mov_abs_xy(x, y)
                            self.send_command(station_index, 'MovToPosAck')
                        elif cmd == 'ActiveStatus' and isinstance(arg1, bool):
                            self._multi_station_dic[station_index]['IsActive'] = arg1
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
        if not self._station_config.IS_MULTI_STATION_MANAGER:
            self._operator_interface.print_to_console(f'the particles from be read from local-files.')
            return
        partical_counter_data = []
        partical_counter_data_grp_len = 10
        if not (os.path.exists(self._station_config.SHARED_DATA_PATH)
                and os.path.isdir(self._station_config.SHARED_DATA_PATH)):
            os_utils.mkdir_p(self._station_config.SHARED_DATA_PATH)
        # save the latest readings from the particle counter to disk, the sub-stations should read it from network-disk.
        while not USER_SHUTDOWN_STATION:
            try:
                val = self._fixture.particle_counter_read_val() if self._station_config.FIXTURE_PARTICLE_COUNTER else 0
                if val is None:
                    continue
                partical_counter_data.append(val)
                if len(partical_counter_data) >= partical_counter_data_grp_len:
                    with open(os.path.join(self._station_config.SHARED_DATA_PATH, 'particles.json'), 'w') as f:
                        json.dump(f, {'particles': partical_counter_data}, indent=2)
                    partical_counter_data.clear()
            except SeacliffOffAxis4FixtureError as e:
                self._operator_interface.print_to_console(f'Fail to read particle count {str(e)}', 'red')
            finally:
                time.sleep(0.1)

    def _fixture_query_thr(self):
        while True:
            time.sleep(0.01)
            try:
                if self._fixture_query_command.empty():
                    continue
                cmd = self._fixture_query_command.get()
                if self._station_config.IS_VERBOSE:
                    print(f'fixture query command: {cmd}\n')
                if isinstance(cmd, str) and re.match('pwron_status:[A|B]_(?:true|false)', cmd, re.I | re.S):
                    cmd1 = cmd.split(':')[1].split('_')[0]
                    cmd2 = cmd.split(':')[1].split('_')[1].lower() in ['true']
                    if cmd2:
                        self._fixture.power_on_button_status(True, bk_mode=cmd1)
                    else:
                        self._fixture.power_on_button_status(False, bk_mode=cmd1)
                    self.btn_status[f'PWR_{cmd1}'] = cmd2
                elif isinstance(cmd, str) and re.match('dual_start:(?:true|false)', cmd, re.I | re.S):
                    cmd1 = cmd.split(':')[1].lower() in ['true']
                    if cmd1:
                        self._fixture.button_enable()
                    else:
                        self._fixture.button_disable()
                    self.btn_status['DUAL_START'] = cmd1
                elif cmd == 'dual_start':
                    self._is_major_ctrl_under_testing = True
                    self.btn_status['DUAL_START'] = False
                    # self._fixture.load()  # carry the DUTs to the expected position automatically.
                    self._fixture_query_command.put('pwron_status:A_False')
                    self._fixture_query_command.put('pwron_status:B_False')
                    self._fixture_query_command.put(f'dual_start_post')
                elif cmd == 'dual_start_post':
                    for k, v in self._multi_station_dic.items():
                        if v['IsActive']:  # and v['SN']:
                            self.send_command(k, 'start_loop', self._multi_station_dic[k]['SN'])
                            self._multi_station_dic[k]['IsRunning'] = True
                        # it says the dual btn was disabled
                elif cmd == 'unload':
                    self._fixture.unload()
                    for channel, v in self._multi_station_dic.items():
                        if v['IsActive']:
                            self._update_sn(channel, None)
                    self._is_major_ctrl_under_testing = False
                elif isinstance(cmd, tuple) and len(cmd) == 2 and cmd[0] == 'power_on':
                    channel = cmd[1].upper()
                    if not self._multi_station_dic[channel]['IsActive']:
                        continue
                    assert channel in self._station_config.SUB_STATION_INFO.keys()
                    if self._multi_station_dic[channel]['SN'] is not None:
                        self._the_unit[channel].screen_off()
                        self._the_unit[channel] = None
                        self._update_sn(channel, None)
                        self._the_unit[channel] = None
                        continue
                    sn = datetime.datetime.now().strftime('%m%d%H%M%S')
                    # sn = self._fixture.scan_code(self.fixture_scanner_ports[channel])
                    if not isinstance(sn, str) or 'ERROR' in sn:
                        self._operator_interface.print_to_console(f'Unable to scan code for station: {sn}\n', 'red')
                        continue
                    if not self.validate_sn(serial_num=sn):
                        self._operator_interface.print_to_console(f'Fail to validate Serial Number : {sn}\n', 'red')
                    else:
                        sf_res = self._shop_floor.ok_to_test(serial_number=sn)
                        if sf_res is True or (isinstance(sf_res, tuple) and sf_res[0]):
                            self._fixture.vacuum(False, channel)
                            if channel in self._station_config.DUT_ETH_PROXY_ADDR:
                                v = self._station_config.DUT_ETH_PROXY_ADDR[channel]
                                self._the_unit[channel] = projectDut(sn, self._station_config, self._operator_interface)
                                if not self._station_config.DUT_SIM:
                                    self._the_unit[channel] = pancakeDut(sn, self._station_config, self._operator_interface)
                                self._the_unit[channel].initialize(eth_addr=v)
                            pw_res = self._the_unit[channel].screen_on(ignore_err=True)
                            if pw_res is True:
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
            grp_btn_ab_status = False
            time.sleep(0.05)
            if not self._fixture_query_command.empty() or self._is_major_ctrl_under_testing:
                continue

            for k, v in self._multi_station_dic.items():
                pwr_status = False
                if not v['IsRunning'] and v['IsActive']:
                    pwr_status = True
                if pwr_status != self.btn_status[f'PWR_{k}']:
                    self._fixture_query_command.put(f'pwron_status:{k}_{pwr_status}')

            grp = [v for k, v in self._multi_station_dic.items() if v['IsActive']]
            if (len(grp) > 0
                    and all([c['SN'] is not None for c in grp])  # SN should be set correctly
                    and all([not c['IsRunning'] for c in grp])):  # Not running
                grp_btn_ab_status = True  # if so, should change the status for dual start button
            if grp_btn_ab_status != self.btn_status['DUAL_START']:
                self._fixture_query_command.put(f'dual_start:{grp_btn_ab_status}')
                time.sleep(0.05)

            if self._fixture:
                ready_key = self._fixture.is_ready()
                query_key_cmd_list = {
                    0: 'dual_start',
                    3: ('power_on', 'A'),
                    4: ('power_on', 'B'),
                    1: ('power_on', 'B'),
                }
                if ready_key in query_key_cmd_list:
                    self._fixture_query_command.put(query_key_cmd_list.get(ready_key))
                elif ready_key is not None:
                    self._operator_interface.print_to_console(f'Recv command not handled: {ready_key} \n')

    def render_pattern(self, station_index, test_pattern):
        assert station_index in self._multi_station_dic.keys()
        assert test_pattern in self._station_config.PATTERNS

        i = self._station_config.PATTERNS.index(test_pattern)
        pattern = self._station_config.PATTERNS[i]
        pre_color = self._station_config.COLORS[i]
        if isinstance(self._station_config.COLORS[i], tuple):
            self._the_unit[station_index].display_color(self._station_config.COLORS[i])
        elif isinstance(self._station_config.COLORS[i], (str, int)):
            self._the_unit[station_index].display_image(self._station_config.COLORS[i])
        self._operator_interface.print_to_console(f'Set DUT {station_index} To Color: {pre_color}.\n')

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
            self._work_flow_ctrl_event.wait()
            self._operator_interface.print_to_console(
                f'release current test resource. {self._work_flow_ctrl_event_err_msg}\n',
                'red' if self._work_flow_ctrl_event_err_msg else None)

            self._runningCount += 1
            self._operator_interface.print_to_console('--- do test finished ---\n')
            return overall_result, first_failed_test_result

    def close_test(self, test_log):
        self._overall_result = test_log.get_overall_result()
        self._first_failed_test_result = test_log.get_first_failed_test_result()
        self._is_slot_under_testing = False
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
        pos_patterns = None
        for posIdx, pos, pos_patterns in self._station_config.POSITIONS:
            if posIdx != tposIdx:
                continue

            for test_pattern in pos_patterns:
                i = self._station_config.PATTERNS.index(test_pattern)
                if i < 0:
                    continue
                self._operator_interface.print_to_console(
                    "Panel export for Pattern: %s\n" % self._station_config.PATTERNS[i])
                if self._station_config.IS_EXPORT_CSV or self._station_config.IS_EXPORT_PNG:
                    output_dir = os.path.join(self._station_config.ROOT_DIR, self._station_config.ANALYSIS_RELATIVEPATH,
                                              serial_number + '_' + test_log._start_time.strftime(
                                                  "%Y%m%d-%H%M%S"))
                    if not os.path.exists(output_dir):
                        os.mkdir(output_dir, 777)
                    meas_list = self._equipment.get_measurement_list()
                    exp_base_file_name = re.sub('_x.log', '', test_log.get_filename())
                    measurement = self._station_config.MEASUREMENTS[i]
                    for meas in meas_list:
                        if meas['Measurement Setup'] != measurement:
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
        pos_items = self._station_config.POSITIONS
        pre_color = None
        for posIdx, pos, pos_patterns in pos_items:
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
            self.__append_local_client_msg_q('MovToPos', f'{pos[0]},{pos[1]}')
            self._work_flow_ctrl_event.wait()
            # self._fixture.mov_abs_xy(pos[0], pos[1])

            center_item = self._station_config.CENTER_AT_POLE_AZI
            lv_cr_items = {}
            lv_all_items = {}
            for test_pattern in pos_patterns:
                if test_pattern not in pos_patterns:
                    self._operator_interface.print_to_console("Can't find pattern {} for position {}.\n"
                                                              .format(test_pattern, posIdx))
                    continue
                self.__append_local_client_msg_q('NextPattern', f'{test_pattern}')
                self._work_flow_ctrl_event.wait()
                if self._work_flow_ctrl_event_err_msg:
                    raise SeacliffOffAxis4StationError(
                        f'Fail to show next pattern {test_pattern}. {self._work_flow_ctrl_event_err_msg}')
                i = self._station_config.PATTERNS.index(test_pattern)

                pattern = self._station_config.PATTERNS[i]
                analysis = self._station_config.ANALYSIS[i]
                self._operator_interface.print_to_console(
                    "Panel Measurement Pattern: %s , Position Id %s.\n" % (pattern, posIdx))

                use_camera = not self._station_config.EQUIPMENT_SIM
                if not use_camera:
                    self._equipment.clear_registration()
                analysis_result = self._equipment.sequence_run_step(analysis, '', use_camera, True)
                self._operator_interface.print_to_console("Sequence run step  {}.\n".format(analysis))
                analysis_result_dic[pattern] = analysis_result.copy()

                # region extract raw data
            for test_pattern in [c for c in pos_patterns if not self._station_config.DATA_COLLECT_ONLY]:
                i = self._station_config.PATTERNS.index(test_pattern)
                pattern = self._station_config.PATTERNS[i]
                analysis = self._station_config.ANALYSIS[i]

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
                    lv_all_items[f'{posIdx}_{test_pattern}'] = lv_dic
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
                    assem = (lv_x_0 - lv_x_180)/lv_0_0
                    test_item = '{}_{}_ASYM_{}_{}_{}_{}'.format(posIdx, pattern, *(p0+p180))
                    test_log.set_measured_value_by_name_ex(test_item, '{0:.4}'.format(assem))

                # Brightness % @30deg wrt on axis brightness
                brightness_items = []
                for item in self._station_config.BRIGHTNESS_AT_POLE_AZI_PER:
                    tlv = lv_dic.get('P_%s_%s' % item)
                    if tlv is None:
                        continue
                    tlv = round_ex(tlv / lv_dic[center_item], 3)
                    brightness_items.append(tlv)
                    test_item = '{}_{}_Lv_Proportion_{}_{}'.format(posIdx, pattern, *item)
                    test_log.set_measured_value_by_name_ex(test_item, tlv)

                for item in self._station_config.COLORSHIFT_AT_POLE_AZI:
                    duv = duv_dic.get('P_%s_%s' % item)
                    if duv is None:
                        continue
                    test_item = '{}_{}_duv_{}_{}'.format(posIdx, pattern, *item)
                    test_log.set_measured_value_by_name_ex(test_item, round_ex(duv, 3))
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
                    test_log.set_measured_value_by_name_ex(test_item, round_ex(cr, ndigits=1))
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
                            export_raw_values = [lv_all_items[f'{posIdx}_{exp_raw_data_pattern}'].get(c) for c in export_raw_keys]
                            export_raw_data[:, pattern_idx * len(self._station_config.EXPORT_RAW_DATA_PATTERN_AZI) + aziIdx + 1] = export_raw_values
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
                            subItem3s = ','.join([f'Phi = {d}' for c, d in self._station_config.EXPORT_RAW_DATA_PATTERN_AZI])
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
