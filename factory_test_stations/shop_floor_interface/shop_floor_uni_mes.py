import gc
import json
import time
import socket
import struct
import traceback
from queue import Queue
from threading import Thread


# Socket发送端
class SocketSender(object):
    def __init__(self, host, port, thread_queue=Queue(10)):
        self.host = host
        self.port = port
        self.thread_queue = thread_queue
        self.addr = (self.host, self.port)
        self.conn = None
        self.running = False
        self.connected = False

    # 开始连接
    def start(self):
        self.running = True
        reconnection_num = 0
        while self.running:
            try:
                self.conn = socket.socket()
                self.conn.connect((self.host, self.port))
                self.connected = True
                self.recv((self.host, self.port))
                reconnection_num = 0
            except Exception as e:
                self.connected = False
                reconnection_num += 1
                if reconnection_num == 1:
                    print('Reconnecting ...')
                time.sleep(0.1)

    # 停止连接
    def stop(self):
        break_data = {'function': 'break'}
        print(f'{self.addr}, send: {break_data}')
        package = json.dumps(break_data).encode('utf-8')
        package_len = struct.pack('i', len(package))
        self.conn.send(package_len)
        self.conn.send(package)
        self.running = False
        self.connected = False
        self.conn.close()
        self.conn = None

    # 接收
    def recv(self, addr):
        print(f'{addr}, connected')
        while self.running:
            try:
                header = self.conn.recv(4)
                if len(header) == 0:
                    continue
                package_len = struct.unpack('i', header)[0]
                # 数据流
                package_bytes = b''
                while self.running:
                    b_data = self.conn.recv(package_len)
                    package_bytes += b_data
                    package_len -= len(b_data)
                    if package_len == 0:
                        package = json.loads(package_bytes.decode('utf-8'))
                        self.thread_queue.put(package)
                        print(f'{addr}, recv: {package}')
                        break
                del package_bytes
                gc.collect()
            except Exception as e:
                print(f'{addr}, forcing a connection to close/n{traceback.format_exc()}')
                self.conn.close()
                break
            time.sleep(0.1)

    # 发送
    def send(self, data):
        print(f'{self.addr}, send: {data}')
        package = json.dumps(data).encode('utf-8')
        package_len = struct.pack('i', len(package))
        self.conn.send(package_len)
        self.conn.send(package)


# 初始化通信连接 (ps:连接为长连接)
socket_sender = SocketSender("127.0.0.1", 5669)


# 初始化
def initialize(*args, **kwargs):
    # 子线程启动连接, 并监听
    t = Thread(target=socket_sender.start)
    t.daemon = True
    t.start()
    while not socket_sender.connected:
        time.sleep(0.1)


# 关闭
def close():
    socket_sender.stop()


def call_template(data):
    try:
        socket_sender.send(data)
        # 监听返回信息
        while True:
            result = socket_sender.thread_queue.get()
            break
        if result['parameter']['status'] == 'success':
            return True, None
        else:
            return False, result['parameter']['message']
    except Exception as e:
        return False, f'The request failed\n{traceback.format_exc()}'


# SN验证
def ok_to_test(serial_number):
    data = {'function': 'ok_to_test',
            'parameter': {'serial_number': serial_number}}
    return call_template(data)


# 测试结果上传
def save_results(test_log):
    data = {'function': 'save_results',
            'parameter': {
                'log_file_path': test_log if isinstance(test_log, str) else test_log.get_file_path()}}
    return call_template(data)


# 测试结果上传
def save_results_from_logs(log_file_path):
    data = {'function': 'save_results',
            'parameter': {
                'log_file_path': log_file_path if isinstance(log_file_path, str) else log_file_path.get_file_path()}}
    return call_template(data)


# 登录
def login_system(user_name, password):
    data = {'function': 'login_system',
            'parameter': {'user_name': user_name,
                          'password': password}}
    return call_template(data)


if __name__ == '__main__':
    # 初始化ShopFloor
    initialize()
    # 登录
    # status, msg = login_system('admin', '123456')
    # print(status, msg)
    # 开始测试
    # status, msg = ok_to_test('6LBF23D001B7ALC')
    # print(status, msg)
    # 结果上传
    # status, msg = save_results('D:/Project/发我的文件/test_station产出的结果文件/'
    #                            '6LBF23D001B7ALC_seacliff_offaxis-0000_20220610-144225_P.log')
    # print(status, msg)
    while True:
        select_id = input('\n'
                          '1: Login to MES\n'
                          '2. SN validation\n'
                          '3. Upload test results\n'
                          'Enter the test ID: ')
        # 登录
        if select_id == '1':
            username = input('username: ')
            password = input('password: ')
            username = username if username else 'admin'
            password = password if password else '123456'
            status, msg = login_system(username, password)
            print(status, msg)
        # SN验证
        elif select_id == '2':
            pnl_id = input('sn: ')
            pnl_id = pnl_id if pnl_id else '2308L9L26402D3'
            status, msg = ok_to_test(pnl_id)
            print(status, msg)
        # 测试结果上传
        elif select_id == '3':
            path = input('file path: ')
            path = path if path else \
                'D:/Project/发我的文件/BOE现场日志/20220704/2308L9L26402D3_seacliff_bluni_si-0004_20220704-164018_P.log'
            # 'D:/Project/发我的文件/BOE现场日志/20220719/2308L9U27K01ZZ_seacliff_bluni_si-0007_20220719-142637_P.log'
            status, msg = save_results(path)
            print(status, msg)
