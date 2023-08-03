__author__ = 'elton.tian'
__version__ = '0.0.1'

import io

"""
Change List:
0.0.1:  Init Version, 
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
import psutil
from ftplib import FTP, error_perm
import posixpath
from pathlib import Path


class ShopFloorError(Exception):
    pass


class ShopFloor_ZR(object):

    def __init__(self, station_config):
        self._machine_type = station_config.STATION_TYPE
        self._station_id = station_config.STATION_NUMBER
        self._ftp_usr = station_config.FTP_USR
        self._ftp_pwd = station_config.FTP_PWD
        self._ftp_addr = station_config.FTP_ADDR
        self._ftp: FTP = None
        self._ftp_station_dir = station_config.FTP_STATION_DIR

    def initialize(self):
        self._ftp = FTP()
        self._ftp.connect(*self._ftp_addr)

    def makedirs_cwd(self, target_dir):
        res = False
        try:
            self._ftp.cwd(target_dir)
            res = True
        except error_perm as e:
            path_parts = Path(target_dir).as_posix().split(posixpath.sep)
            self._ftp.cwd(posixpath.sep)
            for c in path_parts:
                if c not in self._ftp.nlst():
                    self._ftp.mkd(c)
                self._ftp.cwd(c)
            res = True
        return res

    def save_results(self, sn, log_items):
        """
        Save Relevant Results from the Test Log to the Shop Floor System
        """
        res = False
        res_msg = ''
        uut_sn = [c[2] for c in log_items if c[1] == 'UUT_Serial_Number'][0]
        overall_result = [c[2] for c in log_items if c[1] == 'Overall_Result'][0]
        overall_errcode = [c[2] for c in log_items if c[1] == 'Overall_ErrorCode'][0]
        starttime = datetime.datetime.strptime([c[2] for c in log_items if c[1] == 'Start_Time'][0], "%Y%m%d-%H%M%S")

        if any([name for idx, name, value, lsl, usl, res, err_code in log_items[1:] if res is None]):
            err_code = '99999'
        else:
            err_code = overall_errcode

        header = ','.join([name for idx, name, value, lsl, usl, res, err_code in log_items[1:]])
        lsl = ','.join([lsl for idx, name, value, lsl, usl, res, err_code in log_items[1:]])
        usl = ','.join([usl for idx, name, value, lsl, usl, res, err_code in log_items[1:]])
        val = ','.join([value for idx, name, value, lsl, usl, res, err_code in log_items[1:]])
        if uut_sn != sn:
            logging.error(f'Fail to call upload data: {uut_sn} != {sn}')
            res_msg = f'FAIL TO ANALYSIS {uut_sn} != {sn}'
        else:
            logging.debug(f'Send data to server ---> {uut_sn}')
            self._ftp.login(self._ftp_usr, self._ftp_pwd)
            try:
                raw_data = '\n'.join([header, lsl, usl, val]).encode(encoding='utf-8')
                if 'PASS'.lower() == overall_result.lower():
                    fn = f'{uut_sn}_MZ_MZ_OK_{starttime:%Y%m%d%H%M%S}.csv'
                    target_dir = f'{self._ftp_station_dir}/OK/{starttime:%Y%m%d}'
                elif 'FAIL'.lower() == overall_result.lower():
                    fn = f'{uut_sn}_MZ_MZ_NG_{err_code}_{starttime:%Y%m%d%H%M%S}.csv'
                    target_dir = f'{self._ftp_station_dir}/NG/{starttime:%Y%m%d}'
                if self.makedirs_cwd(target_dir):
                    self._ftp.storbinary('STOR ' + f'{fn}', io.BytesIO(raw_data))
                    res = True
                else:
                    res_msg = f'Fail to create folder: {target_dir}'
            except Exception as e:
                res_msg = str(e)
            finally:
                self._ftp.quit()
                logging.debug(f'Send data to server End: {(res, res_msg)}---> {uut_sn}')
        return res, res_msg

    def close(self):
        self._ftp.close()


def save_results_from_logs(log_file_path):
    try:
        _ex_shop_floor.initialize()
        res = False, 'Unknown'
        with open(log_file_path) as file:
            contents = file.readlines()
        log_items = [c.splitlines(keepends=False)[0].split(', ') for c in contents]
        uut_sn = [c[2] for c in log_items if c[1] == 'UUT_Serial_Number'][0]
        res = _ex_shop_floor.save_results(uut_sn, log_items)
    except Exception as e:
        logging.error(f'Fail to save data --> e:{str(e)}')
    finally:
        _ex_shop_floor.close()

    return res


def save_results(test_log):
    return save_results_from_logs(test_log.get_file_path())


def ok_to_test(serial):
    return True, ''


def initialize(station_config):
    global _ex_shop_floor
    station_type = station_config.STATION_TYPE
    station_number = station_config.STATION_NUMBER
    logger = logging.getLogger()
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    log_fn = time.strftime('%Y_%m_%d', time.localtime(time.time()))

    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    fn = os.path.join(os.path.curdir, '../shop_floor_interface/logs',
                                      'sf_i_{0}_{1}_{2}.log'.format(station_type, station_number, log_fn))
    log_dir = os.path.dirname(fn)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        os.chmod(log_dir, 0o777)
    fhlr = logging.FileHandler(fn)
    fhlr.setFormatter(formatter)
    logger.setLevel('INFO')
    logger.addHandler(fhlr)

    _ex_shop_floor = ShopFloor_ZR(station_config)  # type: ShopFloor_genius


def login_system(usr, pwd):
    if usr == 'MZ' and pwd == 'MZ':
        return True, None
    return False, f'{usr}/{pwd} is not match'


class Cfg(object):
    def __init__(self):
        self.STATION_TYPE = 'Seacliff_OffAxis'
        self.STATION_NUMBER = '0000'
        self.FTP_USR = 'mz'
        self.FTP_PWD = 'MZ123456'
        self.FTP_ADDR = ('192.168.10.234', 21)
        self.FTP_STATION_DIR = '1'


if __name__ == '__main__':
    cfg = Cfg()
    initialize(cfg)
    fns = ['2308L1019K0235_seacliff_offaxis-0002_20220310-185607_F.log',
           '2308L6U23F02LD_seacliff_offaxis-0002_20220326-134929_P.log']

    dirs = r'c:\oculus\factory_test_omi\factory_test_stations\factory-test_logs'

    for c in fns:
        fn = os.path.join(dirs, c)
        print(f'upload {c}  ---> {cfg}')
        save_results_from_logs(fn)
    pass
