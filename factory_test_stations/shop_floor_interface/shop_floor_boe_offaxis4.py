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


class ShopFloorError(Exception):
    pass


def ok_to_test(serial):
    print(f'ok_to_test {serial}')
    global _ex_shop_floor, MES_CHK_OFFLINE
    return True, f''


def save_results(test_log):
    """

    :type test_log: hardware_station_common.test_station.test_log.TestRecord
    """
    return save_results_from_logs(test_log.get_file_path())


def save_results_from_logs(log_file_path):
    global _ex_shop_floor, MES_CHK_OFFLINE
    msg = None
    with open(log_file_path, 'r') as file:
        contents = file.readlines()
    # return True

    log_items = [c.splitlines(keepends=False)[0].split(', ') for c in contents]
    uut_sn = [c[2] for c in log_items if c[1] == 'UUT_Serial_Number'][0]
    overall_result = [c[2] for c in log_items if c[1] == 'Overall_Result'][0]
    overall_errcode = [c[2] for c in log_items if c[1] == 'Overall_ErrorCode'][0]
    print(f'save_results_from_logs {uut_sn}')
    save_result_res = False
    pass

    del log_items, contents
    return True, msg


def initialize(station_config):
    pass



def login_system(usr, pwd):
    return True, None
