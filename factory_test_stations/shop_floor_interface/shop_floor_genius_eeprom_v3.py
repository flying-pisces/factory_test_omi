__author__ = 'elton.tian'
__version__ = '3.0.0'
"""
Change List:
0.0.1:  Init Version, 
0.0.2:  Add option for InLot.
0.0.3:  Adjust to support UTC.
0.0.4:  Relase thread for upload automatically when closing.
0.0.5:  if not all the item tested, set MultiErrCode to 99999 .
0.0.6:  all test items upload to mes.
2.0.0:  new test items based MOT 1.2.x
3.0.0:  new test items based on MOT 1.2.4

"""

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
import logging
import time
import threading
import suds.client
import shutil
import glob
import tkinter.simpledialog
import tkinter as tk
import datetime
import stat
import psutil

MACHINE_TYPE = 'EEPROM_WRITING'
STATION_ID = 'seacliff_eeprom-01'
MAC_ID_FILER = '本地'
HostProgressName = 'seacliff_eeprom_run.exe'
MES_IT_MAIL_NOTIFICATION = True

MES_RECV_MAIL_LIST = ['Rays.wang@gseo.com', ]
MES_CC_MAIL_LIST = ['Allen.Chiang@gseo.com', 'gladys.lin@gseo.com', ]

# MES_RECV_MAIL_LIST = ['elton.tian@myzygroup.com', ]
# MES_CC_MAIL_LIST = []

# SN FOR TEST: 2308L0208K02KW、2308L0208K02M1、2308L0208K02MR
# MAIL IP : 192.168.100.5, Port : 25

MES_CTRL_PWD = 'MES123'
MES_IN_LOT_CTRL = True  # required by Rays. 12/21/2020

SF_EEPROM_DIRS = r'c:\oculus\run\seacliff_eeprom\session_data'
SHOP_FLOOR_BAK_DIR = r'c:\shop_floor_to_be_uploaded'
SHOP_FLOOR_FAIL_TO_UPLOAD = r'c:\shop_floor_fails'
SW_VERSION_MISMATCH_LOGS_DIR = r'c:\shop_floor_fails\version_mismatch_logs'
SHOP_FLOOR_BAK_DIR_FILTER = f'*_{STATION_ID}_*.log'
# URL should end with ?WSDL
SF_URL = 'http://192.168.100.96:8012/InLotWS/Service/P5385InLotWS.asmx?WSDL'
SF_LOADER_URL = 'http://192.168.100.96:8012/LoaderWS/Service/SummaryLoader.asmx?WSDL'
SF_MAIL_URL = 'http://192.168.100.96:8011/MailWS/GseoWS.asmx?WSDL'
MES_CHK_OFFLINE = {}
_ex_shop_floor = None
CALIB_REQ_DATA_FILENAME = r'c:\oculus\run\seacliff_eeprom\session_data'

SW_VERSION = '1.2.3'

class ShopFloorError(Exception):
    pass


class ShopFloor_genius(object):
    def __init__(self, machine_type, station_id):
        self._machine_type = machine_type
        self._station_id = station_id
        self._headers = {'Content-Type': 'application/json'}
        self._time_out = 3  # timeout for web-service.
        self._max_retries = 3

        # <editor-fold desc="LOG_2_MES">
        self._mes_dic = {
            'MODEL_NAME': '',
            'UUT_SERIAL_NUMBER': 'UUT_Serial_Number',
            'STATION_ID': 'Station_ID',
            'START_TIME': 'Start_Time',
            'END_TIME': 'End_Time',
            'OVERALL_RESULT': 'Overall_Result',
            'OVERALL_ERRORCODE': '',
            'ELAPSED_SECONDS': 'ELAPSED_SECONDS',
            'SW_VERSION': 'SW_VERSION',
            'DUT_POWER_ON_INFO': 'DUT_POWER_ON_INFO',
            'DUT_POWER_ON_RES': 'DUT_POWER_ON_RES',
            'JUDGED_BY_CAM': 'JUDGED_BY_CAM',
            'PRE_WRITE_COUNTS': 'PRE_WRITE_COUNTS',
            'CFG_BORESIGHT_X': 'CFG_BORESIGHT_X',
            'CFG_BORESIGHT_Y': 'CFG_BORESIGHT_Y',
            'CFG_ROTATION': 'CFG_ROTATION',
            'CFG_LV_W255': 'CFG_LV_W255',
            'CFG_X_W255': 'CFG_X_W255',
            'CFG_Y_W255': 'CFG_Y_W255',
            'CFG_LV_R255': 'CFG_LV_R255',
            'CFG_X_R255': 'CFG_X_R255',
            'CFG_Y_R255': 'CFG_Y_R255',
            'CFG_LV_G255': 'CFG_LV_G255',
            'CFG_X_G255': 'CFG_X_G255',
            'CFG_Y_G255': 'CFG_Y_G255',
            'CFG_LV_B255': 'CFG_LV_B255',
            'CFG_X_B255': 'CFG_X_B255',
            'CFG_Y_B255': 'CFG_Y_B255',
            'CFG_TEMPERATUREW': 'CFG_TemperatureW',
            'CFG_TEMPERATURER': 'CFG_TemperatureR',
            'CFG_TEMPERATUREG': 'CFG_TemperatureG',
            'CFG_TEMPERATUREB': 'CFG_TemperatureB',
            'CFG_TEMPERATUREWD': 'CFG_TemperatureWD',
            'CFG_WHITEPOINTGLR': 'CFG_WhitePointGLR',
            'CFG_WHITEPOINTGLG': 'CFG_WhitePointGLG',
            'CFG_WHITEPOINTGLB': 'CFG_WhitePointGLB',
            'CFG_CS': 'CFG_CS',
            'CFG_VALIDATION_FIELD': 'CFG_VALIDATION_FIELD',
            'POST_WRITE_COUNTS': 'POST_WRITE_COUNTS',
            'WRITE_COUNTS_CHECK': 'WRITE_COUNTS_CHECK',
            'POST_DATA_CHECK': 'POST_DATA_CHECK',
        }
        self._mes_mot_dic = {
            "NOR_RGBBHT_DISPCEN_X_DISPLAY": "normal_RGBBoresight_DispCen_x_display",
            "NOR_RGBBHT_DISPCEN_Y_DISPLAY": "normal_RGBBoresight_DispCen_y_display",
            "NOR_RGBBHT_DISP_ROTATE_X": "normal_RGBBoresight_Disp_Rotate_x",
            "NOR_W255_ONAXIS_LUM": "normal_W255_OnAxis Lum",
            "NOR_RGBBHT_R_LUM_CORRECTED": "normal_RGBBoresight_R_Lum_corrected",
            "NOR_RGBBHT_G_LUM_CORRECTED": "normal_RGBBoresight_G_Lum_corrected",
            "NOR_RGBBHT_B_LUM_CORRECTED": "normal_RGBBoresight_B_Lum_corrected",
            "NOR_W255_ONAXIS_X": "normal_W255_OnAxis x",
            "NOR_W255_ONAXIS_Y": "normal_W255_OnAxis y",
            "NOR_RGBBHT_R_X_CORRECTED": "normal_RGBBoresight_R_x_corrected",
            "NOR_RGBBHT_R_Y_CORRECTED": "normal_RGBBoresight_R_y_corrected",
            "NOR_RGBBHT_G_X_CORRECTED": "normal_RGBBoresight_G_x_corrected",
            "NOR_RGBBHT_G_Y_CORRECTED": "normal_RGBBoresight_G_y_corrected",
            "NOR_RGBBHT_B_X_CORRECTED": "normal_RGBBoresight_B_x_corrected",
            "NOR_RGBBHT_B_Y_CORRECTED": "normal_RGBBoresight_B_y_corrected",
            "NOR_W255_MODULE_TEMPERATURE": "normal_W255_Module Temperature",
            "UUT_TEMP_NOR_RGBBHT": "UUT_TEMPERATURE_normal_RGBBoresight",
            "UUT_TEMP_NOR_RGBBHT": "UUT_TEMPERATURE_normal_RGBBoresight",
            "UUT_TEMP_NOR_RGBBHT": "UUT_TEMPERATURE_normal_RGBBoresight",
            "NOR_WHTDOT_MODULE_TEMPERATURE": "normal_WhiteDot_Module Temperature",
            "NOR_WHTDOT_WP_R_TO_DDIC": "normal_WhiteDot_WP R to DDIC",
            "NOR_WHTDOT_WP_G_TO_DDIC": "normal_WhiteDot_WP G to DDIC",
            "NOR_WHTDOT_WP_B_TO_DDIC": "normal_WhiteDot_WP B to DDIC",
                             }
        # </editor-fold>

    def save_results(self, uut_sn, log_items):
        """
        Save Relevant Results from the Test Log to the Shop Floor System
        """
        args = []
        err_codes = []
        log_2_mes = {}
        sub_test_res = []
        for k in self._mes_dic.keys():
            log_2_mes[k] = None
        for log_item in log_items[1:]:
            idx, name, value, lsl, usl, timestamp, res, err_code = tuple(log_item)
            for it in [k for k, d in self._mes_dic.items() if d == name]:
                log_2_mes[it] = value
                if (res in ['FAIL', None]) and int(idx) > 0:
                    err_codes.append(idx)
                    sub_test_res.append(res)
        if None in sub_test_res:
            err_codes = [99999]  # to indicate the test-flow is not executed completely

        # 日期格式转换-用于数据上传
        log_2_mes['START_TIME'] = datetime.datetime.strptime(log_2_mes['START_TIME'], '%Y%m%d-%H%M%S')
        log_2_mes['END_TIME'] = datetime.datetime.strptime(log_2_mes['END_TIME'], '%Y%m%d-%H%M%S')

        log_2_mes['MODEL_NAME'] = self._machine_type
        log_2_mes['OVERALL_ERRORCODE'] = ';'.join(err_codes)
        insert_response = self.lcd_avi_myzy_log_loader(log_2_mes)
        return insert_response

    # parse dataset from inlog_res
    def parse_tbl_data(self, res):
        res_tbl_items = {}
        for log in res.LOG.diffgram[0].DocumentElement[0].Log:
            dd = dict(log)
            for k, v in self._mes_mot_dic.items():
                if dd.get(k) is None:
                    continue
                res_tbl_items[k] = dd.get(k)[0]
        return res_tbl_items

    def insert_mot_data_in_json(self, uut_sn, dic):
        res = False
        try:
            if not os.path.exists(CALIB_REQ_DATA_FILENAME):
                os.makedirs(CALIB_REQ_DATA_FILENAME)
            os.chmod(CALIB_REQ_DATA_FILENAME, os.stat(CALIB_REQ_DATA_FILENAME).st_mode | stat.S_IRWXU)

            if set(self._mes_mot_dic.keys()).issubset(dic.keys()):
                try:
                    for k, v in self._mes_mot_dic.items():
                        dic[v] = dic[k]
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
                    logging.error('Fail to parse data from MES.'.format(str(e)))
            calib_data_json_fn = os.path.join(CALIB_REQ_DATA_FILENAME, f'eeprom_session_miz_{uut_sn}.json')
            with open(calib_data_json_fn, 'w') as json_file:
                json.dump(dic, json_file, indent=6)
        except Exception as e:
            logging.error('Fail to save json-file: {0}'.format(str(e)))
        return res


    # <editor-fold desc="API interface provided by Genius Inc.">
    def p5385_in_lot_info(self, uut_sn):
        count = 0
        success = False
        res = None
        res_simple_data = {}
        while count < self._max_retries and (not success):
            try:
                client = suds.client.Client(SF_URL, timeout=self._time_out)
                res = client.service.GetInLotInfo(self._machine_type, uut_sn, '', '', '')
                if res is not None:
                    res_simple_data['STATUS'] = res.STATUS
                    res_simple_data['LOT'] = res.LOT
                    res_simple_data['STATION'] = res.STATION
                    res_simple_data['PART_NO'] = res.PART_NO
                if hasattr(res, 'STATUS') and (res.STATUS == 'SUCCESS'):
                    success = True
            except Exception as e:
                logging.error(f'Fail to call P5385_in_lot. Ex: {str(e)}')
            count += 1
        logging.info(f"Inlot: {count}, success: {success} <= {res_simple_data}")
        return res

    def lcd_avi_myzy_log_loader(self, lcd_avi_data):
        count = 0
        success = False
        res = None
        while count < self._max_retries and (not success):
            try:
                client = suds.client.Client(SF_LOADER_URL, timeout=self._time_out)
                res = client.service.EEPROM_Overall_LOG_Loader(lcd_avi_data)
                if res is not None:
                    success = True
            except Exception as e:
                logging.error(f'Fail to call lcd_avi_myzy_log_loader. Ex:{str(e)}')
            count += 1
        logging.info(f'lcd_avi: {count}, success: {success}')
        return res

    def gseo_mail_ws(self, subject, content):
        mail_vm = {}
        mail_vm['TO'] = ','.join(MES_RECV_MAIL_LIST)  # 多人時, 用逗號分開
        mail_vm['CC'] = ','.join(MES_CC_MAIL_LIST)  # 無CC, 可給空白
        mail_vm['SUBJECT'] = subject  # 格式: [Exception Notice]-[@站點名稱]：yyyy-MM-dd HH:mm:ss
        mail_vm['CONTENT'] = content
        mail_vm['FILE_NAME'] = None
        mail_vm['FILE_BYTE'] = None
        count = 0
        success = False
        res = None
        while count < self._max_retries and (not success):
            try:
                client = suds.client.Client(SF_MAIL_URL, timeout=10)
                res = client.service.SendMail(mail_vm)
            except Exception as e:
                logging.error(f'Fail to call sendMail. retries = {count+1}, Ex: {str(e)}')
            count += 1
        logging.info(f'Geo mail WS: {count}, SUBJECT: {subject}, CONTENT: {content} --> res: {res}')
        return res
    # </editor-fold>


def daemon_upload(*add):
    global _ex_shop_floor, MES_CHK_OFFLINE
    logging.info(f'Start daemon thread for upload --> {HostProgressName}.')
    ind = 0
    is_sent_mail_when_fail = True
    min_time_interval = 3 * 60
    loop_interval_seconds = 30
    current_process_id = None
    exist_pids = psutil.pids()
    for c in exist_pids:
        if psutil.pid_exists(c) and psutil.Process(c).name() == HostProgressName:
            current_process_id = c
            break

    while current_process_id is not None and psutil.pid_exists(current_process_id):
        file_to_upload = None
        if os.path.exists(SHOP_FLOOR_BAK_DIR):
            fns = sorted(glob.glob(os.path.join(SHOP_FLOOR_BAK_DIR, SHOP_FLOOR_BAK_DIR_FILTER))
                         , key=os.path.getmtime)
            if len(fns) == 0:
                is_sent_mail_when_fail = True
            if len(fns) > 0 and (abs(os.path.getmtime(fns[0]) - time.time()) > min_time_interval):
                file_to_upload = fns[0]
        if ((file_to_upload is not None)
                and os.path.exists(file_to_upload)
                and (not MES_CHK_OFFLINE.get('mes_chk_offline'))):
            print(f'try to pick up logs -- {ind} ...==> 1/{len(fns)} \n')
            try:
                save_results_from_logs_res = save_results_from_logs(file_to_upload)
                if save_results_from_logs_res[0]:
                    is_sent_mail_when_fail = True
                    loop_interval_seconds = 1
                    logging.debug(f'Success to upload to Mes : {os.path.basename(file_to_upload)}')
                    os.remove(file_to_upload)
                else:
                    # 网络反馈为None，判定为网络异常。如果反馈为非None且不是版本号错误，移动这个log到shop_floor_fails文件夹中。
                    # 版本号不匹配的log移动到SW_VERSION_MISMATCH_LOGS_DIR中
                    if save_results_from_logs_res[1] is not None:
                        if save_results_from_logs_res[1] == 'version mismatch':
                            shutil.move(file_to_upload, SW_VERSION_MISMATCH_LOGS_DIR)
                        else:
                            shutil.move(file_to_upload, SHOP_FLOOR_FAIL_TO_UPLOAD)
                    # None或者异常信息都要发邮件
                    if is_sent_mail_when_fail and MES_IT_MAIL_NOTIFICATION:
                        message_text = f'{MACHINE_TYPE}: {STATION_ID} FAIL TO SEND LOGS TO MES.' \
                                       f'===>{save_results_from_logs_res[1]}'
                        # [Exception Notice] - [ @ 站點名稱]：yyyy - MM - dd HH: mm:ss
                        dt = datetime.datetime.now()
                        subject_msg = f'[專案代號:5385][Exception Notice] - [{MACHINE_TYPE}]:{dt:%Y-%m-%d}'
                        print(f'Try to send mail {subject_msg}')
                        res = _ex_shop_floor.gseo_mail_ws(subject_msg, message_text)
                        if res == 'SUCCESS':
                            is_sent_mail_when_fail = False
                            loop_interval_seconds = 20
                        else:
                            logging.error(f'Fail to send mail. {res}')
            except Exception as e:
                logging.error(f'Fail to upload data {MES_RECV_MAIL_LIST}, err: {str(e)}')
        ind += 1
        time.sleep(loop_interval_seconds)
    logging.info('stop daemon thread for upload.')


def ok_to_test(serial):
    global _ex_shop_floor, MES_CHK_OFFLINE
    msg = None
    if (not MES_IN_LOT_CTRL) or MES_CHK_OFFLINE.get('mes_chk_offline'):
        ok_to_test_res = True
    else:
        ok_to_test_res = False
        validate_res = {}
        try:
            if not os.path.exists(SF_EEPROM_DIRS):
                os.makedirs(SF_EEPROM_DIRS)
            os.chmod(SF_EEPROM_DIRS, os.stat(SF_EEPROM_DIRS).st_mode | stat.S_IRWXU)

            validate_res = _ex_shop_floor.p5385_in_lot_info(serial)
            if hasattr(validate_res, 'STATUS'):
                inspection = None
                if validate_res.STATUS.upper() == 'SUCCESS':
                    inspection = validate_res.INSPECTION_RESULT
                    if validate_res.INSPECTION_RESULT in ['PASS']:
                        get_mot_data_res = _ex_shop_floor.parse_tbl_data(validate_res)
                        if get_mot_data_res:
                            # 截取所需内容并以dict形式保存在本地（json文件）
                            if _ex_shop_floor.insert_mot_data_in_json(serial, get_mot_data_res):
                                ok_to_test_res = True
                            else:
                                msg = '过站检测失败, 本地JSON文件保存失败.'
                        else:
                            msg = '过站检测失败, 无法解析接收的数据.'
                    else:
                        msg = '过站检测失败 站点状态: {0}, 前站结果: {1}'.format(validate_res.STATUS, inspection)
                else:
                    msg = '过站检测失败 站点状态: {0}'.format(validate_res.STATUS)
            else:
                msg = '过站检测失败 网络异常'
            if not ok_to_test_res:
                tkinter_showinfo(msg)

        except Exception as e:
            logging.error('ok to test exp: {0}'.format(str(e)))
            # 连接不成功， 则调整到是否切换离线模式
            dialog_title = '连接服务器失败'
            root: tk.Tk = tk.Tk()
            root.withdraw()
            root.update()
            input_pwd = tkinter.simpledialog.askstring(dialog_title, '如需转入离线模式，请输入密码: ', show='*')
            if (input_pwd is not None) and (input_pwd.upper() == MES_CTRL_PWD):
                MES_CHK_OFFLINE['mes_chk_offline'] = True
                msg = dialog_title + '已转入离线模式'
                ok_to_test_res = True
            elif input_pwd is not None:
                msg = '密码输入错误，无法进入离线模式'
                tkinter.simpledialog.messagebox.showinfo(dialog_title, '密码输入错误')
            root.destroy()

    return ok_to_test_res, msg


def save_results(test_log):
    """

    :type test_log: hardware_station_common.test_station.test_log.TestRecord
    """
    res = False
    try:
        recs = save_results_from_logs(test_log.get_file_path(), log_upload_after_test=True)
        res, msg = recs
    except Exception as e:
        logging.error(f'Exception --> {str(e)}')
        msg = f'Exception --> {str(e)}'
    return res, msg


def save_results_from_logs(log_file_path, log_upload_after_test=False):
    global _ex_shop_floor, MES_CHK_OFFLINE
    web_res_msg = None
    save_result_res = False

    with open(log_file_path) as file:
        contents = file.readlines()

    log_items = [c.splitlines(keepends=False)[0].split(', ') for c in contents]
    uut_sn = [c[2] for c in log_items if c[1] == 'UUT_Serial_Number'][0]
    overall_result = [c[2] for c in log_items if c[1] == 'Overall_Result'][0]
    overall_errcode = [c[2] for c in log_items if c[1] == 'Overall_ErrorCode'][0]
    sw_version = [c[2] for c in log_items if c[1] == 'SW_VERSION'][0]

    logging.info('测试结果上传MES 系统 >>>>>>>>>>>>>>>>>>>>>>>>>>> {0}, ErrCode = {1}'
                 .format(uut_sn, overall_errcode))
    try:
        if not os.path.exists(SHOP_FLOOR_BAK_DIR):
            os.makedirs(SHOP_FLOOR_BAK_DIR)
            os.chmod(SHOP_FLOOR_BAK_DIR, 0o777)
        if not os.path.exists(SHOP_FLOOR_FAIL_TO_UPLOAD):
            os.makedirs(SHOP_FLOOR_FAIL_TO_UPLOAD)
            os.chmod(SHOP_FLOOR_FAIL_TO_UPLOAD, 0o777)
        if not os.path.exists(SW_VERSION_MISMATCH_LOGS_DIR):
            os.makedirs(SW_VERSION_MISMATCH_LOGS_DIR)
            os.chmod(SW_VERSION_MISMATCH_LOGS_DIR, 0o777)

        if sw_version == SW_VERSION:
            if not MES_CHK_OFFLINE.get('mes_chk_offline'):
                web_res_msg = _ex_shop_floor.save_results(uut_sn, log_items)
                if web_res_msg == 'SUCCESS':
                    logging.info('上传结果完成' + '=' * 30)
                    save_result_res = True
                else:
                    logging.info('上传测试结果失败 >>>>>>>>>>>>>>>>>>>>>>>>>>> ')
            else:  # 离线测试时，数据自动保存到临时文件夹，由后台线程负责统一执行数据上传
                bak_log_file_path = os.path.join(SHOP_FLOOR_BAK_DIR, os.path.basename(log_file_path))  # 网络异常时，数组转存
                if ((not os.path.exists(bak_log_file_path)) or
                        (not os.path.samefile(bak_log_file_path, log_file_path))):
                    shutil.copyfile(log_file_path, bak_log_file_path)
                save_result_res = True
        else:
            web_res_msg = 'version mismatch'
    except Exception as e:
        logging.error('ok to test exp: {0}'.format(str(e)))
    if not save_result_res:
        bak_log_file_path = os.path.join(SHOP_FLOOR_BAK_DIR, os.path.basename(log_file_path))  # 网络异常时，数组转存
        if ((not os.path.exists(bak_log_file_path)) or
                (not os.path.samefile(bak_log_file_path, log_file_path))):
            shutil.copyfile(log_file_path, bak_log_file_path)
        msg = f'上传MES失败 ，数据转存至 {bak_log_file_path}'
        logging.info(f'{msg} --> {web_res_msg}')
        print(msg)
        if (not MES_CHK_OFFLINE.get('mes_chk_offline')) and log_upload_after_test:  # 在线上传时，如不成功，需要执行报警提示
            tkinter_showinfo(msg)

    logging.info('{0}***********************************{1}....\n'.format(uut_sn, log_file_path))
    return save_result_res, web_res_msg


def tkinter_showinfo(msg):
    root = tk.Tk()
    root.withdraw()
    root.update()
    tkinter.simpledialog.messagebox.showinfo('提示', msg)
    root.destroy()


def initialize(station_config):
    global _ex_shop_floor, MES_CHK_OFFLINE
    logger = logging.getLogger()
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    log_fn = time.strftime('%Y_%m_%d', time.localtime(time.time()))

    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    fn = os.path.join(os.path.curdir, '../shop_floor_interface/logs',
                                      'sf_i_{0}_{1}_{2}.log'.format(MACHINE_TYPE, STATION_ID, log_fn))
    log_dir = os.path.dirname(fn)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        os.chmod(log_dir, 0o777)
    fhlr = logging.FileHandler(fn)
    fhlr.setFormatter(formatter)
    logger.setLevel('INFO')
    logger.addHandler(fhlr)

    _ex_shop_floor = ShopFloor_genius(MACHINE_TYPE, STATION_ID)  # type: ShopFloor_genius

    daemon_thr = threading.Thread(target=daemon_upload, args=())
    daemon_thr.setDaemon(True)
    daemon_thr.start()
    MES_CHK_OFFLINE = {}


if __name__ == '__main__':
    logging.info('----------------------------')
    logging.debug('+' * 20)
    initialize(None)
    log_dir = r'c:\oculus\run\shop_floor_interface'
    fn_name = r'P1-123456789_seacliff_mot-04_20211125-154400_P.log'
    # serial_numbers = ['P1-123456789', 'P1-234567890', 'P1-234567890', 'P1-999999999', 'M210814102250']
    serial_numbers = ['P1-123456789', 'P1-234567890',]
    for serial_number in serial_numbers:
        res = ok_to_test(serial_number)
        # da = save_results_from_logs(os.path.join(log_dir, fn_name), log_upload_after_test=True)
        # logging.info('----------------------------{0}__{1}_{2}'.format(serial_number, res, da))
    # input('aaa')
