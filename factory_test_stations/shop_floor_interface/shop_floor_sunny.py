__author__ = 'elton.tian'

#!/usr/bin/env python
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

# import hardware_station_common.test_station.test_log

if __name__ != '__main__':
    import requests
    from lxml import etree

FACEBOOK_IT_ENABLED = False

SF_URL = 'http://192.168.217.250:9092/WebService.asmx/'
SF_AAB_URL = 'http://192.168.217.250:9092/WSDetection.asmx/'

SF_AAB_ACTIONS = {
    'ValidateAAB': 'ValidateAAB',
    'InsertAABResult': 'InsertAABResult',
}

SF_AAB_ACTIONS_STATIONS = {
    'PIXEL': 'InsertPixelData',
    'UNIF': 'InsertUniformityData',
    'MOT': 'InsertMOTData',
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
        self._time_out = 0.5

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
        insert_response = self.insert_data(self._machine_type, {'result': args})
        return int(insert_response['Result']) == 1

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
        logging.debug('---> validate aab : {0}'.format(json.dumps(arg)))
        resp = requests.post(SF_AAB_URL + SF_AAB_ACTIONS['ValidateAAB'], timeout=self._time_out,
                             headers=self._headers,
                             data=json.dumps(arg))
        logging.debug('<--- {0}'.format(json.dumps(resp.text, ensure_ascii=False, indent=4)))
        if resp.status_code == requests.codes.ok:
            # xml_string = {"d":{"__type":"WebService.AABResult","ProductID":"12345678","TestTimes":"2",
            # "Message":"已经检测OK","Result":"0"}}
            xml_string = resp.text
            results_keys = ['ProductID', 'TestTimes', 'Message', 'Result', 'LastStation']
            return json.loads(xml_string)['d']

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
        logging.debug('---> validate aab : {0}'.format(json.dumps(arg)))
        resp = requests.post(SF_AAB_URL + SF_AAB_ACTIONS['InsertAABResult'], timeout=self._time_out,
                             headers=self._headers,
                             data=json.dumps(arg))
        logging.debug('<--- {0}'.format(json.dumps(resp.text, ensure_ascii=False, indent=4)))
        if resp.status_code == requests.codes.ok:
            xml_string = resp.text
            results_keys = ['ProductID', 'TestTimes', 'Message', 'Result', 'LastStation']
            return json.loads(xml_string)['d']

    def insert_data(self, station_name, arg):
        """
        insert the log data to MES.
        @param station_name: 'pixel', 'unif', 'mot', ...
        @param arg:
        @return:
        """
        station_name_dic = SF_AAB_ACTIONS_STATIONS.get(station_name.upper())
        if station_name_dic is not None:
            logging.debug('---> validate aab : {0}'.format(json.dumps(arg)))
            resp = requests.post(SF_AAB_URL + station_name_dic, timeout=self._time_out,
                                 headers=self._headers,
                                 data=json.dumps(arg))
            logging.debug('<--- {0}'.format(json.dumps(resp.text, ensure_ascii=False, indent=4)))
            result_array = []
            if resp.status_code == requests.codes.ok:
                xml_string = resp.text
                results_keys = ['ProductID', 'TestTimes', 'Message', 'Result']
                return json.loads(xml_string)['d']
    # </editor-fold>


def get_mac_id(if_name_filter='本地'):
    net_ifs = [(k, v) for k, v in net_if_addrs().items() if if_name_filter in k]
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
    try:
        _ex_shop_floor._mac_id = get_mac_id(if_name_filter=MAC_ID_FILER)[0].get('mac')
        validate_res = _ex_shop_floor.validate_AAB(serial)
        if int(validate_res['Result']) == 1:
            _ex_shop_floor._test_times = validate_res['TestTimes']
            ok_to_test_res = True
        else:
            logging.info('Fail to OK_TO_TEST {0}, LastStation {1}'
                         .format(validate_res['Message'], validate_res['LastStation']))
    except Exception as e:
        logging.error('ok to test exp: {0}'.format(str(e)))
    return ok_to_test_res


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
            res = 1 if overall_result == 'PASS' else 2
            ab_res = _ex_shop_floor.insert_AAB_result(uut_sn=uut_sn, test_times=test_times, test_result=res)
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
    return save_result_res


MACHINE_TYPE = 'MOT'
STATION_ID = 1
MAC_ID_FILER = 'Ethernet 4'

logger = logging.getLogger()
if not logger.hasHandlers():
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    log_fn = time.strftime('%Y_%m_%d', time.localtime(time.time()))
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    chlr = logging.StreamHandler()
    chlr.setFormatter(formatter)
    chlr.setLevel('INFO')
    fn = os.path.join(os.path.curdir, 'shop_floor_interface'
                                      '{0}_{1}_{2}.log'.format(MACHINE_TYPE, STATION_ID, log_fn))
    fhlr = logging.FileHandler(fn)
    fhlr.setFormatter(formatter)
    logger.setLevel('DEBUG')
    logger.addHandler(chlr)
    logger.addHandler(fhlr)
    _ex_shop_floor = ShopFloor_sunny(MACHINE_TYPE, STATION_ID)  # type: ShopFloor_sunny

if __name__ == '__main__':
    import requests
    import collections
    from lxml import etree

    # from hardware_station_common.test_station.test_log.shop_floor_interface.shop_floor import ShopFloor
    # from hardware_station_common.test_station.test_log import TestRecord
    logging.info('----------------------------')
    logging.debug('+' * 20)
    serial_number = '12345678999'
    logging.info('----------------------------{0}'.format(serial_number))
    if ok_to_test(serial_number):
        save_results_from_logs(r'C:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\EFGG_project_station-01_20201202-140709_F.log')
    else:
        print('Fail to OK_TO_TEST.')
    pass
    # _ex_shop_floor._mac_id = get_mac_id()[0].get('mac')
    #
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
