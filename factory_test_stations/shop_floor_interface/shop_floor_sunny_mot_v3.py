# -*- encoding:utf-8 -*-
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
# MES_CHK_OFFLINE: dict
# MES_CTRL_PWD = 'MES123'
MES_IN_LOT_CTRL = True  # required by Haha. 1/11/2021

SF_LOADER_URL = 'http://10.99.10.126:8100/api/MesTransferBind/'
SF_MESDATA_URL = 'http://10.99.10.126:8100/api/MesData/'

CALIB_REQ_DATA_FILENAME = r'c:\oculus\run\seacliff_eeprom\session_data'

SF_GET_ACTIONS = {
    'MOT': 'GetMotData?ProductID='
}

SF_BD_ACTIONS = {
    'Bind': 'InspectionBindCode',
    'Down': 'InspectionDownCode',
}

SF_ACTIONS_STATIONS = {
    'MOT': 'InsertMOTData',
    'PNL': 'InsertPanelData',
    'EEP': 'InsertEepromData',
    'MDT': 'InsertMDTData',
}

# bluni
# MACHINE_TYPE = 'PNL'
# STATION_ID = 'seacliff_bluni-001'
# MAC_ID_FILER = 'Ethernet 2'
# MES_CHK_OFFLINE = {}

# mot
MACHINE_TYPE = 'MOT'
STATION_ID = 'seacliff_mot-03'
MAC_ID_FILER = 'DUT'
MES_CHK_OFFLINE = {}

# eeprom
# MACHINE_TYPE = 'Eep'
# STATION_ID = 'seacliff_eeprom-02'
# MAC_ID_FILER = 'DUT'
# MES_CHK_OFFLINE = {}


class ShopFloorError(Exception):
    pass


class ShopFloor_sunny(object):
    logger = logging.getLogger('mes-logger')

    def __init__(self, machine_type, station_id):
        self._machine_type = machine_type
        self._station_id = station_id
        self._headers = {'Content-Type': 'application/json'}
        self._test_times = {}
        self._mac_id = None
        self._time_out = 3
        self._max_retries = 3

    def save_results(self, uut_sn, log_items):
        """
        Save Relevant Results from the Test Log to the Shop Floor System
        """
        test_times = self._test_times[uut_sn]

        args = []
        for log_item in log_items[1:]:
            idx, name, value, lsl, usl, timestamp, res, err_code = tuple(log_item)
            args.append({
                'ProductID': uut_sn,
                'CTimes': test_times,
                'Index': idx,
                'TestName': name,
                'MeasuredVal': value,
                'LoLim': lsl,
                'HiLim': usl,
                'Timestamp': timestamp,
                'Result': res,
                'ErrorCode': err_code,
            })
        return self.insert_data(self._machine_type, args)

    # <editor-fold desc="API interface provided by Sunny Inc.">
    def get_mot_data(self, uut_sn):
        arg = {'ProductID': uut_sn}
        ShopFloor_sunny.logger.info('---> get mot data : {0}'.format(json.dumps(arg)))
        count = 0
        success = False
        res = None
        resp = None
        while count < self._max_retries and (not success):
            try:
                resp = requests.get(SF_MESDATA_URL + SF_GET_ACTIONS['MOT'] + uut_sn, timeout=5,
                                    headers=self._headers,
                                    data=json.dumps(arg))
                ShopFloor_sunny.logger.debug('<--- {0}'.format(json.dumps(resp.text, ensure_ascii=False, indent=4)))
                if resp.status_code == requests.codes.ok:
                    xml_string = resp.text
                    res = json.loads(xml_string)
                    ShopFloor_sunny.logger.info(f"Success to got mot data. Result: {res['Result']}")
                    success = True
                else:
                    res = '<--- {0}'.format(json.dumps(resp.text, ensure_ascii=False, indent=4))
            except Exception as e:
                ShopFloor_sunny.logger.error(f'---> fail to got mot data. exp: {str(e)}')
                res = f'---> fail to got mot data. exp: {str(e)}'
            count += 1
        if not success:
            ShopFloor_sunny.logger.info('---> fail to  got mot data : {0}'.format(json.dumps(arg)))
            ShopFloor_sunny.logger.info(f'<--- {resp}')
        return res

    @staticmethod
    def insert_mot_data_in_json(serial, dic):
        res = False
        try:
            if not os.path.exists(CALIB_REQ_DATA_FILENAME):
                os.makedirs(CALIB_REQ_DATA_FILENAME)
            os.chmod(CALIB_REQ_DATA_FILENAME, os.stat(CALIB_REQ_DATA_FILENAME).st_mode | stat.S_IRWXU)

            exp_mes_items = ["normal_RGBBoresight_DispCen_x_display",
                             "normal_RGBBoresight_DispCen_y_display",
                             "normal_RGBBoresight_Disp_Rotate_x",
                             "normal_W255_OnAxis Lum",
                             "normal_RGBBoresight_R_Lum_corrected",
                             "normal_RGBBoresight_G_Lum_corrected",
                             "normal_RGBBoresight_B_Lum_corrected",
                             "normal_W255_OnAxis x",
                             "normal_W255_OnAxis y",
                             "normal_RGBBoresight_R_x_corrected",
                             "normal_RGBBoresight_R_y_corrected",
                             "normal_RGBBoresight_G_x_corrected",
                             "normal_RGBBoresight_G_y_corrected",
                             "normal_RGBBoresight_B_x_corrected",
                             "normal_RGBBoresight_B_y_corrected",

                             "normal_W255_Module Temperature",
                             "UUT_TEMPERATURE_normal_RGBBoresight",
                             "UUT_TEMPERATURE_normal_RGBBoresight",
                             "UUT_TEMPERATURE_normal_RGBBoresight",
                             "normal_WhiteDot_Module Temperature",

                             "normal_WhiteDot_WP R to DDIC",
                             "normal_WhiteDot_WP G to DDIC",
                             "normal_WhiteDot_WP B to DDIC",
                             ]

            if set(exp_mes_items).issubset(dic.keys()):
                try:
                    dic['display_boresight_x'] = float(dic['normal_RGBBoresight_DispCen_x_display'])
                    dic['display_boresight_y'] = float(dic['normal_RGBBoresight_DispCen_y_display'])
                    dic['rotation'] = float(dic['normal_RGBBoresight_Disp_Rotate_x'])
                    dic['lv_W255'] = float(dic['normal_W255_OnAxis Lum'])
                    dic['lv_R255'] = float(dic['normal_RGBBoresight_R_Lum_corrected'])
                    dic['lv_G255'] = float(dic['normal_RGBBoresight_G_Lum_corrected'])
                    dic['lv_B255'] = float(dic['normal_RGBBoresight_B_Lum_corrected'])

                    dic['x_W255'] = float(dic["normal_W255_OnAxis x"])
                    dic['y_W255'] = float(dic["normal_W255_OnAxis y"])

                    dic['x_R255'] = float(dic["normal_RGBBoresight_R_x_corrected"])
                    dic['y_R255'] = float(dic["normal_RGBBoresight_R_y_corrected"])

                    dic['x_G255'] = float(dic["normal_RGBBoresight_G_x_corrected"])
                    dic['y_G255'] = float(dic["normal_RGBBoresight_G_y_corrected"])

                    dic['x_B255'] = float(dic["normal_RGBBoresight_B_x_corrected"])
                    dic['y_B255'] = float(dic["normal_RGBBoresight_B_y_corrected"])

                    dic['TemperatureW'] = float(dic['normal_W255_Module Temperature'])
                    dic['TemperatureR'] = float(dic['UUT_TEMPERATURE_normal_RGBBoresight'])
                    dic['TemperatureG'] = float(dic['UUT_TEMPERATURE_normal_RGBBoresight'])
                    dic['TemperatureB'] = float(dic['UUT_TEMPERATURE_normal_RGBBoresight'])
                    dic['TemperatureWD'] = float(dic['normal_WhiteDot_Module Temperature'])
                    dic['WhitePointGLR'] = int(dic['normal_WhiteDot_WP R to DDIC'])
                    dic['WhitePointGLG'] = int(dic['normal_WhiteDot_WP G to DDIC'])
                    dic['WhitePointGLB'] = int(dic['normal_WhiteDot_WP B to DDIC'])

                    res = True
                except Exception as e:
                    ShopFloor_sunny.logger.error('Fail to parse data from MES.'.format(str(e)))
                    res = 'Fail to parse data from MES.'.format(str(e))
            calib_data_json_fn = os.path.join(CALIB_REQ_DATA_FILENAME, f'eeprom_session_miz_{serial}.json')
            with open(calib_data_json_fn, 'w') as json_file:
                json.dump(dic, json_file, indent=6)
        except Exception as e:
            ShopFloor_sunny.logger.error('Fail to save json-file: {0}'.format(str(e)))
            res = 'Fail to save json-file: {0}'.format(str(e))
        return res
    # </editor-fold>

    # <editor-fold desc='API interface provided by sunny for AAB'>
    def load_dut(self, uut_sn):
        """
        validate the SN is comfortable for this station_id,
        and the test_times from result should be used in the following processure
        @param mac_id:
        @param uut_sn:
        @return:
        """
        arg = {'ProductID': uut_sn, 'Mac': self._mac_id.replace('-', ':'), 'Pos': '1'}
        ShopFloor_sunny.logger.info('---> validate load : {0}'.format(json.dumps(arg)))
        count = 0
        success = False
        res = None
        resp = None
        while count < self._max_retries and (not success):
            try:
                resp = requests.post(SF_LOADER_URL + SF_BD_ACTIONS['Bind'], timeout=self._time_out,
                                     headers=self._headers,
                                     data=json.dumps(arg))
                ShopFloor_sunny.logger.debug('<--- {0}'.format(json.dumps(resp.text, ensure_ascii=False, indent=4)))
                if resp.status_code == requests.codes.ok:
                    # xml_string = '{"Status": true, "Message": "上传成功", "Result": {"ctimes": "1"}',
                    # "Timestamp": 1635900237108}
                    xml_string = resp.text
                    results_keys = ['Status', 'Message', 'Result', 'Timestamp']
                    res = json.loads(xml_string)
                    ShopFloor_sunny.logger.info(f"Success to validate. Result: {res['Result']}")
                    success = True
                else:
                    res = f'<--- {0}'.format(json.dumps(resp.text, ensure_ascii=False, indent=4))
            except Exception as e:
                res = f'---> fail to validate load. Exp: {str(e)}'
                ShopFloor_sunny.logger.error(res)
            count += 1
        if not success:
            ShopFloor_sunny.logger.error(f'fail to validate load. {json.dumps(arg)}')
            ShopFloor_sunny.logger.info(f'<--- {resp}')
        return res

    def unload_dut(self, uut_sn, test_times, test_result):
        """
        insert overall result to MES for AAB.
        @type uut_sn: str
        @param uut_sn:
        @type test_times: int
        @param test_times:
        @param test_result: 1: pass 2: fail
        @return:
        """
        arg = {'ProductID': uut_sn,
               'Mac': self._mac_id.replace('-', ':'),
               'Pos': '1',
               'CTimes': str(test_times),
               'CResult': str(test_result),
               }
        ShopFloor_sunny.logger.info('---> validate unload : {0}'.format(json.dumps(arg)))
        count = 0
        success = False
        res = None
        resp = None
        while count < self._max_retries and (not success):
            try:
                resp = requests.post(SF_LOADER_URL + SF_BD_ACTIONS['Down'], timeout=self._time_out,
                                     headers=self._headers,
                                     data=json.dumps(arg))
                ShopFloor_sunny.logger.debug('<--- {0}'.format(json.dumps(resp.text, ensure_ascii=False, indent=4)))
                if resp.status_code == requests.codes.ok:
                    xml_string = resp.text
                    results_keys = ['Status', 'Message', 'Result', 'Timestamp']
                    res = json.loads(xml_string)
                    success = True
                else:
                    res = '<--- {0}'.format(json.dumps(resp.text, ensure_ascii=False, indent=4))
            except Exception as e:
                res = f'---> fail to validate unload. exp: {str(e)}'
                ShopFloor_sunny.logger.error(res)
            count += 1
        if not success:
            ShopFloor_sunny.logger.info(f'---> fail to validate unload. {json.dumps(arg)}')
            ShopFloor_sunny.logger.info(f'<--- {resp}')
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
        station_name_dic = SF_ACTIONS_STATIONS.get(station_name.upper())
        if station_name_dic is not None:
            while count < self._max_retries and (not success):
                try:
                    ShopFloor_sunny.logger.debug('---> validate insert data : {0}'.format(json.dumps(arg)))
                    resp = requests.post(SF_MESDATA_URL + station_name_dic, timeout=self._time_out,
                                         headers=self._headers,
                                         data=json.dumps(arg))
                    ShopFloor_sunny.logger.debug('<--- {0}'.format(json.dumps(resp.text, ensure_ascii=False, indent=4)))
                    result_array = []
                    if resp.status_code == requests.codes.ok:
                        xml_string = resp.text
                        results_keys = ['Status', 'Message', 'Result', 'Timestamp']
                        res = json.loads(xml_string)
                        success = True
                    else:
                        res = '<--- {0}'.format(json.dumps(resp.text, ensure_ascii=False, indent=4))
                except Exception as e:
                    res = f'---> fail to validate insert data. Exp: {str(e)}'
                    ShopFloor_sunny.logger.error(res)
                count += 1
        if not success:
            ShopFloor_sunny.logger.info('---> fail to validate insert data : {0}'.format(json.dumps(arg)))
            ShopFloor_sunny.logger.info(f'<--- {resp}')
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
    global _ex_shop_floor, MES_CHK_OFFLINE
    msg = None

    ShopFloor_sunny.logger.info('MES: ***********************************{0}\n'.format(serial))
    print('MES: ***********************************{0}'.format(serial))
    _ex_shop_floor._test_times[serial] = 0
    # return True

    ok_to_test_res = False
    try:
        mac_interfaces = get_mac_id(if_name_filter=MAC_ID_FILER)
        if len(mac_interfaces) <= 0:
            raise ShopFloorError(f'获取机台MAC地址异常 {MAC_ID_FILER}')
        _ex_shop_floor._mac_id = mac_interfaces[0].get('mac')
        if MES_IN_LOT_CTRL:
            validate_res = _ex_shop_floor.load_dut(serial)
            if validate_res is None or isinstance(validate_res, str):
                raise ShopFloorError(f'Fail to OK_TO_TEST, Return {validate_res}')
            if validate_res['Status']:
                ShopFloor_sunny.logger.info('MES上料完成' + '=' * 30)
                _ex_shop_floor._test_times[serial] = validate_res['Result']['ctimes']
                ok_to_test_res = True
            else:
                ShopFloor_sunny.logger.info('Fail to OK_TO_TEST {0}'.format(validate_res['Message']))
                msg = 'Fail to OK_TO_TEST {0}'.format(validate_res['Message'])
        else:
            ok_to_test_res = True

        # <editor-fold desc='Just for Eeprom'>
        if MACHINE_TYPE == 'Eep' and ok_to_test_res:
            # 获取Mot中的数据
            get_mot_data_res = _ex_shop_floor.get_mot_data(serial)
            if get_mot_data_res is None or isinstance(get_mot_data_res, str):
                ok_to_test_res = False
                raise ShopFloorError(f'Fail to got mot data, Return {get_mot_data_res}')
            if get_mot_data_res['Status']:
                res = {}
                for dic in get_mot_data_res['Result']:
                    test_name = dic['TestName']
                    test_val = dic['MeasuredVal']
                    res[test_name] = test_val
                ShopFloor_sunny.logger.info('获取MOT中的数据完成' + '=' * 30)
                # 截取所需内容并以dict形式保存在本地（json文件）
                ok_to_test_res_json_data = _ex_shop_floor.insert_mot_data_in_json(serial, res)
                if ok_to_test_res_json_data is True:
                    ShopFloor_sunny.logger.info('截取所需内容并以dict形式保存在本地（json文件）完成' + '=' * 30)
                else:
                    ok_to_test_res = False
                    msg = '<--- 从MOT获取的数据保存失败: {0}'.format(ok_to_test_res_json_data)
                    ShopFloor_sunny.logger.error(msg)
            else:
                ok_to_test_res = False
                msg = '<--- fail to got mot data: {0}'.format(get_mot_data_res['Message'])
                ShopFloor_sunny.logger.error(msg)
        # </editor-fold>
    except Exception as e:
        msg = 'ok to test exp: {0}'.format(str(e))
        ShopFloor_sunny.logger.error(msg)
        # 连接不成功， 则调整到是否切换离线模式
        # dialog_title = '连接服务器失败'
        # root = tk.Tk()
        # root.withdraw()
        # root.update()
        # input_pwd = tkinter.simpledialog.askstring(dialog_title, '如需转入离线模式，请输入密码: ', show='*')
        # if (input_pwd is not None) and (input_pwd.upper() == MES_CTRL_PWD):
        #     MES_CHK_OFFLINE['mes_chk_offline'] = True
        # elif input_pwd is not None:
        #     tkinter.simpledialog.messagebox.showinfo(dialog_title, '密码输入错误')
        # root.destroy()
    return ok_to_test_res, msg


def save_results(test_log):
    """

    :type test_log: hardware_station_common.test_station.test_log.TestRecord
    """
    return save_results_from_logs(test_log.get_file_path())


def save_results_from_logs(log_file_path):
    global _ex_shop_floor, MES_CHK_OFFLINE
    msg = None
    with open(log_file_path) as file:
        contents = file.readlines()
    # return True

    log_items = [c.splitlines(keepends=False)[0].split(', ') for c in contents]
    uut_sn = [c[2] for c in log_items if c[1] == 'UUT_Serial_Number'][0]
    overall_result = [c[2] for c in log_items if c[1] == 'Overall_Result'][0]
    overall_errcode = [c[2] for c in log_items if c[1] == 'Overall_ErrorCode'][0]
    if uut_sn not in _ex_shop_floor._test_times:
        msg = f'Unable to find test_times for {uut_sn}.'
        ShopFloor_sunny.logger.error(msg)
        return False, msg

    test_times = _ex_shop_floor._test_times[uut_sn]
    save_result_res = False
    ShopFloor_sunny.logger.info(
        '测试结果上传MES 系统 >>>>>>>>>>>>>>>>>>>>>>>>>>> {0}, Test_Times = {1}'.format(uut_sn, test_times))
    try:
        save_feedback = _ex_shop_floor.save_results(uut_sn, log_items)
        if save_feedback is None or isinstance(save_feedback, str):
            raise ShopFloorError(f'Fail to save results. Return {save_feedback}')
        if save_feedback['Status']:
            ShopFloor_sunny.logger.info('上传测试结果完成' + '=' * 30)
            if (not MES_IN_LOT_CTRL) or MES_CHK_OFFLINE.get('mes_chk_offline'):
                save_result_res = True
                ShopFloor_sunny.logger.error(f'离线状态， 数据不过站. MES_IN_LOT_CTRL: {MES_IN_LOT_CTRL}')
            else:
                res = 0 if overall_result == 'PASS' else 1
                ab_res = _ex_shop_floor.unload_dut(uut_sn=uut_sn, test_times=test_times, test_result=res)
                if ab_res is None or isinstance(ab_res, str):
                    raise ShopFloorError(f'Fail to unload DUT, Return {ab_res}')
                if ab_res['Status']:
                    ShopFloor_sunny.logger.info('MES下料完成' + '=' * 30)
                    save_result_res = True
                else:
                    msg = 'MES下料失败 >>>>>>>>>>>>>>>>>>>>>>>>>>> {0}'.format(ab_res['Message'])
                    ShopFloor_sunny.logger.error(msg)
        else:
            msg = '上传测试结果失败 >>>>>>>>>>>>>>>>>>>>>>>>>>> {0}'.format(save_feedback['Message'])
            ShopFloor_sunny.logger.error(msg)
    except Exception as e:
        msg = '数据上传或MES下料失败，请查明原因: {0}'.format(str(e))
        ShopFloor_sunny.logger.error(msg)
    ShopFloor_sunny.logger.info(
        '{0}*****************************save_results_from_logs = {1} \n'.format(uut_sn, save_result_res))
    # if not save_result_res:
    #     dialog_title = '数据上传失败, 请检测网络状态'
    #     root = tk.Tk()
    #     root.withdraw()
    #     root.update()
    #     input_pwd = tkinter.simpledialog.askstring(dialog_title, '如需转入离线模式，请输入密码: ', show='*')
    #     if (input_pwd is not None) and (input_pwd.upper() == MES_CTRL_PWD):
    #         MES_CHK_OFFLINE['mes_chk_offline'] = True
    #     elif input_pwd is not None:
    #         tkinter.simpledialog.messagebox.showinfo(dialog_title, '密码输入错误')
    #     root.destroy()
    del log_items, contents
    return save_result_res, msg


def initialize(station_config):
    global _ex_shop_floor, MES_CHK_OFFLINE

    logger = logging.getLogger('mes-logger')
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    log_fn = time.strftime('%Y_%m_%d', time.localtime(time.time()))
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    log_dir = os.path.join(os.path.curdir, '../shop_floor_interface/logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        os.chmod(log_dir, 0o777)

    fn = os.path.join(log_dir, 'SFI_{0}_{1}_{2}.log'.format(MACHINE_TYPE, STATION_ID, log_fn))
    fhlr = logging.FileHandler(fn, encoding='utf-8')
    fhlr.setFormatter(formatter)
    logger.setLevel('DEBUG')
    logger.addHandler(fhlr)
    logger.debug('-----------Shop Floor Interface === MES ------------------------Initialised.')
    # MES_CHK_OFFLINE = {}
    _ex_shop_floor = ShopFloor_sunny(MACHINE_TYPE, STATION_ID)  # type: ShopFloor_sunny
    MES_CHK_OFFLINE['mes_chk_offline'] = False


if __name__ == '__main__':
    global _ex_shop_floor
    # import requests
    import collections
    from lxml import etree

    # from hardware_station_common.test_station.test_log.shop_floor_interface.shop_floor import ShopFloor
    # from hardware_station_common.test_station.test_log import TestRecord
    logging.info('----------------------------')
    logging.debug('+' * 20)
    serial_number = '3B09B13CBJ000F'
    initialize(None)
    logging.info('----------------------------{0}'.format(serial_number))
    if ok_to_test(serial_number)[0]:
        save_results_from_logs(r'C:\oculus\run\shop_floor_interface\3B09B13CBJ000F_seacliff_mot-07_20211122-141855_P.log')
        pass
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
