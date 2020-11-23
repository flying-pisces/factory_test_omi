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
import hardware_station_common.test_station.test_log

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
    def __init__(self):
        self._headers = {'Content-Type': 'application/json'}
        pass

    def ok_to_test(self, serial_number):
        """
        Query Shop Floor System To Determine if a given Unit is Ok To Be Tested
        """
        return True

    def save_results(self, log):
        """
        Save Relevant Results from the Test Log to the Shop Floor System
        """
        uut_sn = log.get_uut_sn()
        log_metadata = log.get_user_metadata_dict()
        if (log_metadata is not None) and ('test_times' in log_metadata):
            test_times = log_metadata['test_times']

        results_array = log.results_array()
        args = []
        for key in results_array:
            item = results_array[key]
            idx, name, lsl, usl, value = (item._unique_id, item._test_name, item._low_limit,
                                          item._high_limit, item._measured_value)
            res = item.get_pass_fail_string()
            err_code = item.get_error_code_as_string()
            tiemstamp = item.get_measurement_timestamp()
            args.append({
                'ProductID': uut_sn,
                'TestTimes': test_times,
                'Index': idx,
                'TestName': name,
                'MeasuredVal': value,
                'LoLim': lsl,
                'HiLim': usl,
                'Timestamp': tiemstamp,
                'Result': res,
                'ErrorCode': err_code,
            })
        insert_response = self.insert_data('MOT', {'result': args})
        return int(insert_response[3]) == 1

    # <editor-fold desc="API interface provided by Sunny Inc.">
    def get_test_results(self, uut_sn):
        arg = {'proID': uut_sn}
        result_array = []
        resp = requests.post(SF_URL + SF_ACTIONS['GetTestResults'],
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
        resp = requests.post(SF_URL + SF_ACTIONS['ShowCurrentStation'],
                             headers=self._headers,
                             data=json.dumps(arg))
        if resp.status_code == requests.codes.ok:
            xml_string = resp.text
            root = etree.fromstring(xml_string.encode('utf-8'))
            station_keys = ['StationID', 'StationName']
            return tuple([root.find(c, root.nsmap).text for c in station_keys])

    def show_station_list(self):
        resp = requests.post(SF_URL + SF_ACTIONS['ShowStationList'])
        result_array = []
        if resp.status_code == requests.codes.ok:
            # xml_string =  '<?xml version="1.0" encoding="utf-8"?>\r\n<ArrayOfStation xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://tempuri.org/">\r\n  <Station>\r\n    <StationID>1</StationID>\r\n    <StationName>L2Assemble</StationName>\r\n  </Station>\r\n  <Station>\r\n    <StationID>2</StationID>\r\n    <StationName>L1Assemble</StationName>\r\n  </Station>\r\n  <Station>\r\n    <StationID>3</StationID>\r\n    <StationName>3STest</StationName>\r\n  </Station>\r\n  <Station>\r\n    <StationID>4</StationID>\r\n    <StationName>LCDAssemble</StationName>\r\n  </Station>\r\n  <Station>\r\n    <StationID>5</StationID>\r\n    <StationName>VIDDetection</StationName>\r\n  </Station>\r\n</ArrayOfStation>'
            xml_string = resp.text
            root = etree.fromstring(xml_string.encode('utf-8'))
            results = root.findall('Station', root.nsmap)
            station_keys = ['StationID', 'StationName']
            for result in results:
                result_vals = [result.find(c, result.nsmap).text for c in station_keys]
                result_array.append(dict(zip(station_keys, result_vals)))
            return result_array

    def station_start(self, station_id, uut_sn):
        """

        @type station_id: str
        @type uut_sn: str
        """
        arg = {'proID': uut_sn, 'stationID': station_id}
        resp = requests.post(SF_URL + SF_ACTIONS['StationStart'],
                             headers=self._headers,
                             data=json.dumps(arg))
        if resp.status_code == requests.codes.ok:
            xml_string = resp.text
            return xml_string['d']

    def get_all_work_station_by_proid(self, uut_sn):
        arg = {'proID': uut_sn}
        resp = requests.post(SF_URL + SF_ACTIONS['GetAllWorkStationByProID'],
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
    def validate_AAB(self, staion_id, mac_id, uut_sn):
        """
        validate the SN is comfortable for this station_id,
        and the test_times from result should be used in the following processure
        @param staion_id:
        @param mac_id:
        @param uut_sn:
        @return:
        """
        arg = {'data': {'ProductID': uut_sn, 'MacID': mac_id, 'StationID': staion_id}}

        resp = requests.post(SF_AAB_URL + SF_AAB_ACTIONS['ValidateAAB'],
                             headers=self._headers,
                             data=json.dumps(arg))
        if resp.status_code == requests.codes.ok:
            # xml_string = {"d":{"__type":"WebService.AABResult","ProductID":"12345678","TestTimes":"2","Message":"已经检测OK","Result":"0"}}
            xml_string = resp.text
            results_keys = ['ProductID', 'TestTimes', 'Message', 'Result']
            return json.loads(xml_string)['d']

    def insert_AAB_result(self, staion_id, uut_sn, test_times, test_result):
        """
        insert overall result to MES for AAB.
        @type staion_id: str
        @param staion_id:
        @type uut_sn: str
        @param uut_sn:
        @type test_times: int
        @param test_times:
        @param test_result: 1: pass 2: fail
        @return:
        """
        arg = {'data': {'ProductID': uut_sn, 'TestTimes': test_times, 'StationID': staion_id, 'TestResult': test_result}}
        resp = requests.post(SF_AAB_URL + SF_AAB_ACTIONS['InsertAABResult'],
                             headers=self._headers,
                             data=json.dumps(arg))
        if resp.status_code == requests.codes.ok:
            xml_string = resp.text
            results_keys = ['ProductID', 'TestTimes', 'Message', 'Result']
            return json.loads(xml_string)['d']


    def insert_data(self, station_name,  arg):
        """
        insert the log data to MES.
        @param station_name: 'pixel', 'unif', 'mot', ...
        @param arg:
        @return:
        """
        station_name_dic = SF_AAB_ACTIONS_STATIONS.get(station_name.upper())
        if station_name_dic is not None:
            resp = requests.post(SF_AAB_URL + station_name_dic,
                                 headers=self._headers,
                                 data=json.dumps(arg))
            result_array = []
            if resp.status_code == requests.codes.ok:
                xml_string = resp.text
                results_keys = ['ProductID', 'TestTimes', 'Message', 'Result']
                return json.loads(xml_string)['d']

    # </editor-fold>


def ok_to_test(serial):
    print('-------------------{0}'.format(serial))
    return True


def save_results(test_log):
    """

    :type test_log: hardware_station_common.test_station.test_log
    """
    uut_sn = test_log.get_uut_sn()
    log_metadata = test_log.get_user_metadata_dict()
    pprint.pprint('我是SaveResult 测试2滴滴答答的 .... uut_sn {0}, meta = {1}. \n'.format(uut_sn, log_metadata))
    results_array = test_log.results_array()
    pprint.pprint('测试结果 >>>>>>>>>>>>>>>>>>>>>>>>>>> ')
    pprint.pprint([(item._unique_id,
                     item._test_name,
                     item._low_limit,
                     item._high_limit,
                     item._measured_value) for key, item in results_array.items()])
    pprint.pprint('--------------------------------------------------------')
    pprint.pprint('--------------------------------------------------------')
    pprint.pprint('--------------------------------------------------------')
    return True


if __name__ == '__main__':
    sys.path.append('z:\lib\site-packages')
    import requests
    import collections
    from lxml import etree
    # from hardware_station_common.test_station.test_log.shop_floor_interface.shop_floor import ShopFloor
    # from hardware_station_common.test_station.test_log import TestRecord
    d = collections.OrderedDict()
    d['aa'] = 100
    d['bb'] = 200


    sf = ShopFloor_sunny()
    uut_sn = '12345678'
    station_id = '1'

    #
    station_lists = sf.show_station_list()
    da = sf.get_test_results(uut_sn)
    cur_station = sf.show_current_station(uut_sn)
    sf.get_test_results('sample')
    sf.show_current_station('sample')

    sa = sf.validate_AAB(station_id, 'mac_Id', uut_sn)
    sf.insert_AAB_result(station_id, uut_sn, sa['TestTimes'], 2)

    sa = sf.validate_AAB(station_id, 'mac_Id', uut_sn)
    sf.insert_AAB_result(station_id, uut_sn, sa['TestTimes'], 1)

    sf.station_start(station_id, uut_sn)
    
    sf.insert_AAB_result(station_id, uut_sn, 1, 0)
    
    sf.show_station_list()
    sf.get_all_work_station_by_proid('sample')
    sf.station_start('Sample', '3')
    print(dir(requests))
