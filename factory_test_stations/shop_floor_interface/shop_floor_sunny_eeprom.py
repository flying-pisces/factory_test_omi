__author__ = 'elton.tian'

# !/usr/bin/env python
# pylint: disable=R0921
# pylint: disable=F0401
# Mimic Generic Interface to Factory Shop Floor Systems
import os
import sys
import importlib
import json
from enum import Enum
import pprint
from psutil import net_if_addrs
import logging
import time
import tkinter.simpledialog
import requests
import tkinter as tk
import datetime
from lxml import etree
import stat


# import hardware_station_common.test_station.test_log
#MES_CHK_OFFLINE: dict
MES_CTRL_PWD = 'MES123'
MES_IN_LOT_CTRL = True  # required by Haha. 1/11/2021

SF_URL = 'http://192.168.217.250:9092/WebService.asmx/'
SF_AAB_URL = 'http://192.168.217.250:9092/WSDetection.asmx/'
SF_MOT_DATA_URL = 'http://192.168.217.250:9092/WSGetDetectionData.asmx/'

CALIB_REQ_DATA_FILENAME = r'c:\oculus\run\seacliff_eeprom\session_data'

SF_AAB_ACTIONS = {
    'ValidateAAB': 'ValidateAAB',
    'InsertAABResult': 'InsertAABResult',
    'GetMotData': 'GetMotData',
}

SF_AAB_ACTIONS_STATIONS = {
    'MOT': 'InsertMOTData',
    'PNL': 'InsertPanelData',
    'EEP': 'InsertEepromData',
}

SF_ACTIONS = {
    'GetTestResults': 'GetDetectResult',
    'ShowCurrentStation': 'ShowCurrentStation',
    'ShowStationList': 'ShowStationList',
    'StationStart': 'StationStart',
    'GetAllWorkStationByProID': 'GetAllWorkStationByProID',
}


class ShopFloorError(Exception):
    pass


class ShopFloor_sunny(object):
    def __init__(self, machine_type, station_id):
        self._machine_type = machine_type
        self._station_id = station_id
        self._headers = {'Content-Type': 'application/json'}
        self._test_times = 0
        self._mac_id = None
        self._time_out = 3
        self._max_retries = 3

    def save_results(self, uut_sn, log_items):
        """
        Save Relevant Results from the Test Log to the Shop Floor System
        """
        test_times = self._test_times

        args = []
        for log_item in log_items[1:]:
            idx, name, value, lsl, usl, timestamp, res, err_code = tuple(log_item)
            args.append({
                'ProductID': uut_sn,
                'TestTimes': test_times,
                'Index': idx,
                'TestName': name,
                'MeasuredVal': value,
                'LoLim': lsl,
                'HiLim': usl,
                'Timestamp': timestamp,
                'Result': res,
                'ErrorCode': err_code,
            })
        return self.insert_data(self._machine_type, {'result': args})

    # <editor-fold desc="API interface provided by Sunny Inc.">
    def get_test_results(self, uut_sn):
        arg = {'proID': uut_sn}
        result_array = []
        resp = requests.post(SF_URL + SF_ACTIONS['GetTestResults'], timeout=self._time_out,
                             headers=self._headers,
                             data=json.dumps(arg))
        if resp.status_code == requests.codes.ok:
            xml_string = resp.text
            root = etree.fromstring(xml_string.encode('utf-8'))
            results = root.findall('DetectionResult/DetectionResult', root.nsmap)
            result_keys = ['Index', 'TestName', 'MeasuredVal', 'LoLim', 'HiLim', 'Result', 'ErrorCode']
            for result in results:
                result_vals = [result.find(c, result.nsmap).text for c in result_keys]
                result_array.append(dict(zip(result_keys, result_vals)))
            return result_array

    def show_current_station(self, uut_sn):
        arg = {'proID': uut_sn}
        resp = requests.post(SF_URL + SF_ACTIONS['ShowCurrentStation'], timeout=self._time_out,
                             headers=self._headers,
                             data=json.dumps(arg))
        if resp.status_code == requests.codes.ok:
            xml_string = resp.text
            root = etree.fromstring(xml_string.encode('utf-8'))
            station_keys = ['StationID', 'StationName']
            return tuple([root.find(c, root.nsmap).text for c in station_keys])

    def show_station_list(self):
        resp = requests.post(SF_URL + SF_ACTIONS['ShowStationList'], timeout=self._time_out)
        result_array = []
        if resp.status_code == requests.codes.ok:
            xml_string = resp.text
            root = etree.fromstring(xml_string.encode('utf-8'))
            results = root.findall('Station', root.nsmap)
            station_keys = ['StationID', 'StationName']
            for result in results:
                result_vals = [result.find(c, result.nsmap).text for c in station_keys]
                result_array.append(dict(zip(station_keys, result_vals)))
            return result_array

    def station_start(self, uut_sn):
        """

        @type uut_sn: str
        """
        arg = {'proID': uut_sn, 'stationID': self._station_id}
        resp = requests.post(SF_URL + SF_ACTIONS['StationStart'], timeout=self._time_out,
                             headers=self._headers,
                             data=json.dumps(arg))
        if resp.status_code == requests.codes.ok:
            xml_string = resp.text
            return xml_string['d']

    def get_all_work_station_by_proid(self, uut_sn):
        arg = {'proID': uut_sn}
        resp = requests.post(SF_URL + SF_ACTIONS['GetAllWorkStationByProID'], timeout=self._time_out,
                             headers=self._headers,
                             data=json.dumps(arg))
        if resp.status_code == requests.codes.ok:
            result_array = []
            xml_string = resp.text
            root = etree.fromstring(xml_string.encode('utf-8'))
            results = root.findall('ProCurrentStation', root.nsmap)
            station_keys = ['ProductID', 'StationID', 'StationName']
            for result in results:
                result_vals = [result.find(c, result.nsmap).text for c in station_keys]
                result_array.append(dict(zip(station_keys, result_vals)))
            return result_array

    # </editor-fold>

    # <editor-fold desc='API interface provided by sunny for AAB'>
    def validate_AAB(self, uut_sn):
        """
        validate the SN is comfortable for this station_id,
        and the test_times from result should be used in the following processure
        @param mac_id:
        @param uut_sn:
        @return:
        """
        arg = {'data': {'ProductID': uut_sn, 'MacID': self._mac_id, 'StationID': self._station_id,
                        'MachineType': self._machine_type}}
        logging.info('---> validate aab : {0}'.format(json.dumps(arg)))
        count = 0
        success = False
        res = None
        while count < self._max_retries and (not success):
            try:
                resp = requests.post(SF_AAB_URL + SF_AAB_ACTIONS['ValidateAAB'], timeout=self._time_out,
                                     headers=self._headers,
                                     data=json.dumps(arg))
                logging.debug('<--- {0}'.format(json.dumps(resp.text, ensure_ascii=False, indent=4)))
                if resp.status_code == requests.codes.ok:
                    # xml_string = {"d":{"__type":"WebService.AABResult","ProductID":"12345678","TestTimes":"2",
                    # "Message":"已经检测OK","Result":"0"}}
                    xml_string = resp.text
                    results_keys = ['ProductID', 'TestTimes', 'Message', 'Result', 'LastStation']
                    res = json.loads(xml_string)['d']
                    success = True
            except:
                pass
            count += 1
        return res

    def get_mot_data(self, uut_sn):
        arg = {'ProductID': uut_sn}
        logging.info('---> get mot data : {0}'.format(json.dumps(arg)))
        count = 0
        success = False
        res = {}
        resp = None
        while count < self._max_retries and (not success):
            try:
                resp = requests.post(SF_MOT_DATA_URL + SF_AAB_ACTIONS['GetMotData'], timeout=5,
                                     headers=self._headers,
                                     data=json.dumps(arg))
                logging.debug('<--- {0}'.format(json.dumps(resp.text, ensure_ascii=False, indent=4)))
                if resp.status_code == requests.codes.ok:
                    xml_string = resp.text

                    for dic in json.loads(xml_string)['d']:
                        test_name = dic['TestName']
                        test_val = dic['MeasuredVal']
                        res[test_name] = test_val

                    success = True
            except Exception as e:
                logging.error(f'---> fail to got mot data. exp: {str(e)}')
            count += 1
        if not success:
            logging.info('---> fail to  got mot data : {0}'.format(json.dumps(arg)))
            logging.info(f'<--- {resp}')
        return res

    @staticmethod
    def insert_mot_data_in_json(serial, dic):
        res = False
        try:
            if not os.path.exists(CALIB_REQ_DATA_FILENAME):
                os.makedirs(CALIB_REQ_DATA_FILENAME)
            os.chmod(CALIB_REQ_DATA_FILENAME, os.stat(CALIB_REQ_DATA_FILENAME).st_mode | stat.S_IRWXU)

            exp_mes_items = ["normal_GreenDistortion_Y_DispCen_x_display",
                             "normal_GreenDistortion_Y_DispCen_y_display",
                             "normal_GreenDistortion_Y_Disp_Rotate_x",
                             "normal_W255_Lum_0.0deg_0.0deg",
                             "normal_W255_u'_0.0deg_0.0deg",
                             "normal_W255_v'_0.0deg_0.0deg",
                             "normal_R255_Lum_0.0deg_0.0deg",
                             "normal_G255_Lum_0.0deg_0.0deg",
                             "normal_B255_Lum_0.0deg_0.0deg",
                             "normal_R255_u'_0.0deg_0.0deg",
                             "normal_R255_v'_0.0deg_0.0deg",
                             "normal_G255_u'_0.0deg_0.0deg",
                             "normal_G255_v'_0.0deg_0.0deg",
                             "normal_B255_u'_0.0deg_0.0deg",
                             "normal_B255_v'_0.0deg_0.0deg"]

            mes_inlot_dic = [
                'display_boresight_x',
                'display_boresight_y',
                'rotation',
                'lv_W255',
                'x_W255',
                'y_W255',
                'lv_R255',
                'x_R255',
                'y_R255',
                'lv_G255',
                'x_G255',
                'y_G255',
                'lv_B255',
                'x_B255',
                'y_B255',
            ]
            calc_x = lambda u, v: (9 * u / (6 * u - 16 * v + 12))
            calc_y = lambda u, v: (4 * v / (6 * u - 16 * v + 12))

            if set(exp_mes_items).issubset(dic.keys()):
                try:
                    dic['display_boresight_x'] = float(dic['normal_GreenDistortion_Y_DispCen_x_display'])
                    dic['display_boresight_y'] = float(dic['normal_GreenDistortion_Y_DispCen_y_display'])
                    dic['rotation'] = float(dic['normal_GreenDistortion_Y_Disp_Rotate_x'])
                    dic['lv_W255'] = float(dic['normal_W255_Lum_0.0deg_0.0deg'])
                    dic['lv_R255'] = float(dic['normal_R255_Lum_0.0deg_0.0deg'])
                    dic['lv_G255'] = float(dic['normal_G255_Lum_0.0deg_0.0deg'])
                    dic['lv_B255'] = float(dic['normal_B255_Lum_0.0deg_0.0deg'])

                    dic['x_W255'] = calc_x(float(dic["normal_W255_u'_0.0deg_0.0deg"]),
                                           float(dic["normal_W255_v'_0.0deg_0.0deg"]))
                    dic['y_W255'] = calc_y(float(dic["normal_W255_u'_0.0deg_0.0deg"]),
                                           float(dic["normal_W255_v'_0.0deg_0.0deg"]))

                    dic['x_R255'] = calc_x(float(dic["normal_R255_u'_0.0deg_0.0deg"]),
                                           float(dic["normal_R255_v'_0.0deg_0.0deg"]))
                    dic['y_R255'] = calc_y(float(dic["normal_R255_u'_0.0deg_0.0deg"]),
                                           float(dic["normal_R255_v'_0.0deg_0.0deg"]))

                    dic['x_G255'] = calc_x(float(dic["normal_G255_u'_0.0deg_0.0deg"]),
                                           float(dic["normal_G255_v'_0.0deg_0.0deg"]))
                    dic['y_G255'] = calc_y(float(dic["normal_G255_u'_0.0deg_0.0deg"]),
                                           float(dic["normal_G255_v'_0.0deg_0.0deg"]))

                    dic['x_B255'] = calc_x(float(dic["normal_B255_u'_0.0deg_0.0deg"]),
                                           float(dic["normal_B255_v'_0.0deg_0.0deg"]))
                    dic['y_B255'] = calc_y(float(dic["normal_B255_u'_0.0deg_0.0deg"]),
                                           float(dic["normal_B255_v'_0.0deg_0.0deg"]))
                    res = True
                except Exception as e:
                    logging.error('Fail to parse data from MES.'.format(str(e)))
            calib_data_json_fn = os.path.join(CALIB_REQ_DATA_FILENAME, f'eeprom_session_miz_{serial}.json')
            with open(calib_data_json_fn, 'w') as json_file:
                json.dump(dic, json_file, indent=6)
        except Exception as e:
            logging.error('Fail to save json-file: {0}'.format(str(e)))
        return res

    def insert_AAB_result(self, uut_sn, test_times, test_result):
        """
        insert overall result to MES for AAB.
        @type uut_sn: str
        @param uut_sn:
        @type test_times: int
        @param test_times:
        @param test_result: 1: pass 2: fail
        @return:
        """
        arg = {'data': {'ProductID': uut_sn,
                        'TestTimes': test_times,
                        'StationID': self._station_id,
                        'TestResult': test_result,
                        'MachineType': self._machine_type,
                        }}
        logging.info('---> validate aab : {0}'.format(json.dumps(arg)))
        count = 0
        success = False
        res = None
        resp = None
        while count < self._max_retries and (not success):
            try:
                resp = requests.post(SF_AAB_URL + SF_AAB_ACTIONS['InsertAABResult'], timeout=self._time_out,
                                     headers=self._headers,
                                     data=json.dumps(arg))
                logging.debug('<--- {0}'.format(json.dumps(resp.text, ensure_ascii=False, indent=4)))
                if resp.status_code == requests.codes.ok:
                    xml_string = resp.text
                    results_keys = ['ProductID', 'TestTimes', 'Message', 'Result', 'LastStation']
                    res = json.loads(xml_string)['d']
                    success = True
            except Exception as e:
                logging.error(f'---> fail to insert aab_result. exp: {str(e)}')
            count += 1
        if not success:
            logging.info(f'---> fail to insert aab result. {json.dumps(arg)}')
            logging.info(f'<--- {resp}')
        return res

    def insert_data(self, station_name, arg):
        """
        insert the log data to MES.
        @param station_name: 'pixel', 'unif', 'mot', ...
        @param arg:
        @return:
        """
        count = 0
        success = False
        res = None
        resp = None
        station_name_dic = SF_AAB_ACTIONS_STATIONS.get(station_name.upper())
        if station_name_dic is not None:
            while count < self._max_retries and (not success):
                try:
                    logging.debug('---> validate aab : {0}'.format(json.dumps(arg)))
                    resp = requests.post(SF_AAB_URL + station_name_dic, timeout=self._time_out,
                                         headers=self._headers,
                                         data=json.dumps(arg))
                    logging.debug('<--- {0}'.format(json.dumps(resp.text, ensure_ascii=False, indent=4)))
                    result_array = []
                    if resp.status_code == requests.codes.ok:
                        xml_string = resp.text
                        results_keys = ['ProductID', 'TestTimes', 'Message', 'Result']
                        res = int(json.loads(xml_string)['d']['Result']) == 1
                        success = True
                except Exception as e:
                    logging.error(f'---> fail to insert data. exp: {str(e)}')
                count += 1
        if not success:
            logging.info('---> fail to  insert data : {0}'.format(json.dumps(arg)))
            logging.info(f'<--- {resp}')
        return res
    # </editor-fold>


def get_mac_id(if_name_filter='本地'):
    net_ifs = [(k, v) for k, v in net_if_addrs().items() if if_name_filter.upper() in k.upper()]
    cur_net_if = []
    for net_k, net_if in net_ifs:
        mac = None
        ipv4 = None
        ipv6 = None
        for snic in net_if:
            if snic.family.name in ['AF_LINK', 'AF_PACKET']:
                mac = snic.address
            elif snic.family.name in ['AF_INET']:
                ipv4 = snic.address
            elif snic.family.name in ['AF_INET6']:
                ipv6 = snic.address
        if mac:
            cur_net_if.append({'if_name': net_k, 'mac': mac, 'ipv4': ipv4, 'ipv6': ipv6})
    msg = [(c['if_name'], c['mac']) for c in cur_net_if]
    print(f'TRYING TO GET MAC_ADDR: {if_name_filter}--> {msg}')
    return cur_net_if


def ok_to_test(serial):
    logging.info('***********************************{0}\n'.format(serial))
    _ex_shop_floor._test_times = 0
    ok_to_test_res = False
    ok_to_test_res_json_data = False
    msg = None

    if (not MES_IN_LOT_CTRL) or MES_CHK_OFFLINE.get('mes_chk_offline'):
        ok_to_test_res = True
    else:
        try:
            mac_interfaces = get_mac_id(if_name_filter=MAC_ID_FILER)
            if len(mac_interfaces) <= 0:
                raise IndexError(f'获取机台MAC地址异常 {MAC_ID_FILER}')
            _ex_shop_floor._mac_id = mac_interfaces[0].get('mac')
            validate_res = _ex_shop_floor.validate_AAB(serial)
            if validate_res is None:
                raise BaseException(f'Fail to OK_TO_TEST, Return {validate_res}')
            if int(validate_res['Result']) == 1:
                _ex_shop_floor._test_times = validate_res['TestTimes']
                ok_to_test_res = True
            else:
                logging.info('Fail to OK_TO_TEST {0}, LastStation {1}'
                             .format(validate_res['Message'], validate_res['LastStation']))
        except Exception as e:
            logging.error('ok to test exp: {0}'.format(str(e)))
            # 连接不成功， 则调整到是否切换离线模式
            dialog_title = '连接服务器失败'
            root = tk.Tk()
            root.withdraw()
            input_pwd = tkinter.simpledialog.askstring(dialog_title, '如需转入离线模式，请输入密码: ', show='*')
            if (input_pwd is not None) and (input_pwd.upper() == MES_CTRL_PWD):
                MES_CHK_OFFLINE['mes_chk_offline'] = True
            elif input_pwd is not None:
                tkinter.simpledialog.messagebox.showinfo(dialog_title, '密码输入错误')

    if ok_to_test_res:
        try:
        # 获取Mot中的数据
            get_mot_data_res = _ex_shop_floor.get_mot_data(serial)
            if get_mot_data_res:
                # 截取所需内容并以dict形式保存在本地（json文件）
                ok_to_test_res_json_data = _ex_shop_floor.insert_mot_data_in_json(serial, get_mot_data_res)
        except:
            pass
    if ok_to_test_res and (not ok_to_test_res_json_data):
        logging.error(f'从MES获取数据失败 OK: {ok_to_test_res}, MES DATA: {ok_to_test_res_json_data}')

    return ok_to_test_res and ok_to_test_res_json_data


def save_results(test_log):
    """

    :type test_log: hardware_station_common.test_station.test_log.TestRecord
    """
    return save_results_from_logs(test_log.get_file_path())


def save_results_from_logs(log_file_path):
    with open(log_file_path) as file:
        contents = file.readlines()

    log_items = [c.splitlines(keepends=False)[0].split(', ') for c in contents]
    uut_sn = [c[2] for c in log_items if c[1] == 'UUT_Serial_Number'][0]
    overall_result = [c[2] for c in log_items if c[1] == 'Overall_Result'][0]
    overall_errcode = [c[2] for c in log_items if c[1] == 'Overall_ErrorCode'][0]

    test_times = _ex_shop_floor._test_times
    save_result_res = False
    logging.info('测试结果上传MES 系统 >>>>>>>>>>>>>>>>>>>>>>>>>>> {0}, Test_Times = {1}'.format(uut_sn, test_times))
    try:
        if _ex_shop_floor.save_results(uut_sn, log_items):
            if (not MES_IN_LOT_CTRL) or MES_CHK_OFFLINE.get('mes_chk_offline'):
                save_result_res = True
                logging.error(f'离线状态， 数据不过站. MES_IN_LOT_CTRL: {MES_IN_LOT_CTRL}')
            else:
                res = 1 if overall_result == 'PASS' else 2
                ab_res = _ex_shop_floor.insert_AAB_result(uut_sn=uut_sn, test_times=test_times, test_result=res)
                if ab_res is None:
                    raise BaseException(f'Fail to Insert_AAB_Result, Return {ab_res}')
                if int(ab_res['Result']) == 1:
                    logging.info('上传AAB结果完成' + '=' * 30)
                    save_result_res = True
                else:
                    logging.info('上传AAB测试结果失败 >>>>>>>>>>>>>>>>>>>>>>>>>>> {0}'.format(ab_res['Message']))
        else:
            logging.info('上传测试结果失败 >>>>>>>>>>>>>>>>>>>>>>>>>>> ')
    except Exception as e:
        logging.error('数据上传失败，请查明原因: {0}'.format(str(e)))
    logging.info('{0}*****************************save_results_from_logs = {1} \n'.format(uut_sn, save_result_res))
    if not save_result_res:
        tkinter.simpledialog.messagebox.showinfo('error', '数据上传失败, 请检测网络状态')
    del log_items, contents
    return save_result_res


MACHINE_TYPE = 'Eep'
STATION_ID = 'seacliff_eeprom-02'
MAC_ID_FILER = 'Ethernet'

logger = logging.getLogger()
if not logger.hasHandlers():
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    log_fn = time.strftime('%Y_%m_%d', time.localtime(time.time()))
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    chlr = logging.StreamHandler()
    chlr.setFormatter(logging.Formatter('%(levelname)s      %(message)s'))
    chlr.setLevel('INFO')
    log_dir = os.path.join(os.path.curdir, '../shop_floor_interface/logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        os.chmod(log_dir, 0o777)

    fn = os.path.join(log_dir, 'SFI_{0}_{1}_{2}.log'.format(MACHINE_TYPE, STATION_ID, log_fn))
    fhlr = logging.FileHandler(fn)
    fhlr.setFormatter(formatter)
    logger.setLevel('INFO')
    logger.addHandler(chlr)
    logger.addHandler(fhlr)
    MES_CHK_OFFLINE = {}
    _ex_shop_floor = ShopFloor_sunny(MACHINE_TYPE, STATION_ID)  # type: ShopFloor_sunny


if __name__ == '__main__':
    import requests
    import collections
    from lxml import etree

    # from hardware_station_common.test_station.test_log.shop_floor_interface.shop_floor import ShopFloor
    # from hardware_station_common.test_station.test_log import TestRecord
    logging.info('----------------------------')
    logging.debug('+' * 20)
    serial_number = 'T1237567891234'
    logging.info('----------------------------{0}'.format(serial_number))
    ok_to_test(serial_number)

    s = _ex_shop_floor.get_mot_data(serial_number)
    s = json.loads('{"InsId": 2, "name": "lege-happy", "CreationTime": "2019-04-23T03:18:02Z"}')
    _ex_shop_floor.insert_mot_data_in_json(s)

    # if ok_to_test(serial_number):
    #     save_results_from_logs(r'C:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\EFGG_project_station-01_20201202-140709_F.log')
    # else:
    #     print('Fail to OK_TO_TEST.')
    # pass
    # _ex_shop_floor._mac_id = get_mac_id()[0].get('mac')

    # station_lists = _ex_shop_floor.show_station_list()
    # da = sf.get_test_results(uut_sn)
    # cur_station = sf.show_current_station(uut_sn)
    # sf.get_test_results('sample')
    # sf.show_current_station('sample')
    # sa = _ex_shop_floor.validate_AAB(serial_number)
    # _ex_shop_floor.insert_AAB_result(serial_number, sa['TestTimes'], 2)
    #
    # sa = _ex_shop_floor.validate_AAB(serial_number)
    # _ex_shop_floor.insert_AAB_result(serial_number, sa['TestTimes'], 1)
