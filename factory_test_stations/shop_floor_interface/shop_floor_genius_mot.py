__author__ = 'elton.tian'
__version__ = '0.0.4'
"""
Change List:
0.0.1:  Init Version, 
0.0.2:  Add option for InLot.
0.0.3:  Adjust to support UTC.
0.0.4:  Support for MOT
        Relase thread for upload automatically when closing.
0.0.5:  if not all the item tested, set MultiErrCode to 99999 .
0.0.6:  all test items upload to mes.
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


MES_IT_MAIL_NOTIFICATION = True

MES_RECV_MAIL_LIST = ['Rays.wang@gseo.com', ]
MES_CC_MAIL_LIST = ['Allen.Chiang@gseo.com', 'gladys.lin@gseo.com', ]

# MES_RECV_MAIL_LIST = ['elton.tian@myzygroup.com', ]
# MES_CC_MAIL_LIST = []

# SN FOR TEST: 2308L0208K02KW、2308L0208K02M1、2308L0208K02MR
# MAIL IP : 192.168.100.5, Port : 25

MES_CTRL_PWD = 'MES123'
MES_IN_LOT_CTRL = False  # required by Rays. 12/21/2020

SHOP_FLOOR_BAK_DIR = r'c:\shop_floor_to_be_uploaded'
SHOP_FLOOR_FAIL_TO_UPLOAD = r'c:\shop_floor_fails'
MACHINE_TYPE = 'MODULE_OPTICAL_TEST'
STATION_ID = 'seacliff_mot-04'
MAC_ID_FILER = '本地'
HostProgressName = 'seacliff_mot_run.exe'
SHOP_FLOOR_BAK_DIR_FILTER = f'*_{STATION_ID}_*.log'
# URL should end with ?WSDL
SF_URL = 'http://192.168.100.96:8012/InLotWS/Service/P5385InLotWS.asmx?WSDL'
SF_LOADER_URL = 'http://192.168.100.96:8012/LoaderWS/Service/SummaryLoader.asmx?WSDL'
SF_MAIL_URL = 'http://192.168.100.96:8011/MailWS/GseoWS.asmx?WSDL'
MES_CHK_OFFLINE: dict


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
            'STARTTIME': 'Start_Time',
            'ENDTIME': 'End_Time',
            'OVERALLRESULT': 'Overall_Result',
            'OVERALLERRORCODE': '',

            'ELAPSED_SECONDS': 'elapsed_seconds',
            'SW_VERSION': "SW_VERSION",
            'EQUIP_VERSION': "EQUIP_VERSION",
            'DUT_MODULETYPE': "DUT_ModuleType",
            'CARRIER_PROBECONNECTSTATUS': "Carrier_ProbeConnectStatus",
            'DUT_SCREENONRETRIES': "DUT_ScreenOnRetries",
            'DUT_SCREENONSTATUS': "DUT_ScreenOnStatus",
            'DUT_CANCELBYOPERATOR': "DUT_CancelByOperator",
            'ENV_PARTICLECOUNTER': "ENV_ParticleCounter",
            'ENV_AMBIENTTEMP': "ENV_AmbientTemp",
            'DUT_ALIGNMENTSUCCESS': "DUT_AlignmentSuccess",
            'TEST_RAW_IMG_SUCCESS_W255': "Test_RAW_IMAGE_SAVE_SUCCESS_normal_W255",
            'TEST_RAW_IMG_SUCCESS_R255': "Test_RAW_IMAGE_SAVE_SUCCESS_normal_R255",
            'TEST_RAW_IMG_SUCCESS_G255': "Test_RAW_IMAGE_SAVE_SUCCESS_normal_G255",
            'TEST_RAW_IMG_SUCCESS_B255': "Test_RAW_IMAGE_SAVE_SUCCESS_normal_B255",
            'TEST_RAW_IMG_SUCCESS_GREEN': "Test_RAW_IMAGE_SAVE_SUCCESS_normal_GreenDistortion",
            'NORMAL_W255_LUM_N10DEG_0DEG': "normal_W255_Lum_-10.0deg_0.0deg",
            'NORMAL_W255_U_N10DEG_0DEG': "normal_W255_u'_-10.0deg_0.0deg",
            'NORMAL_W255_V_N10DEG_0DEG': "normal_W255_v'_-10.0deg_0.0deg",
            'NORMAL_W255_LUM_N20DEG_0DEG': "normal_W255_Lum_-20.0deg_0.0deg",
            'NORMAL_W255_U_N20DEG_0DEG': "normal_W255_u'_-20.0deg_0.0deg",
            'NORMAL_W255_V_N20DEG_0DEG': "normal_W255_v'_-20.0deg_0.0deg",
            'NORMAL_W255_LUM_N30DEG_0DEG': "normal_W255_Lum_-30.0deg_0.0deg",
            'NORMAL_W255_U_N30DEG_0DEG': "normal_W255_u'_-30.0deg_0.0deg",
            'NORMAL_W255_V_N30DEG_0DEG': "normal_W255_v'_-30.0deg_0.0deg",
            'NORMAL_W255_LUM_0DEG_N10DEG': "normal_W255_Lum_0.0deg_-10.0deg",
            'NORMAL_W255_U_0DEG_N10DEG': "normal_W255_u'_0.0deg_-10.0deg",
            'NORMAL_W255_V_0DEG_N10DEG': "normal_W255_v'_0.0deg_-10.0deg",
            'NORMAL_W255_LUM_0DEG_N20DEG': "normal_W255_Lum_0.0deg_-20.0deg",
            'NORMAL_W255_U_0DEG_N20DEG': "normal_W255_u'_0.0deg_-20.0deg",
            'NORMAL_W255_V_0DEG_N20DEG': "normal_W255_v'_0.0deg_-20.0deg",
            'NORMAL_W255_LUM_0DEG_N30DEG': "normal_W255_Lum_0.0deg_-30.0deg",
            'NORMAL_W255_U_0DEG_N30DEG': "normal_W255_u'_0.0deg_-30.0deg",
            'NORMAL_W255_V_0DEG_N30DEG': "normal_W255_v'_0.0deg_-30.0deg",
            'NORMAL_W255_LUM_0DEG_0DEG': "normal_W255_Lum_0.0deg_0.0deg",
            'NORMAL_W255_U_0DEG_0DEG': "normal_W255_u'_0.0deg_0.0deg",
            'NORMAL_W255_V_0DEG_0DEG': "normal_W255_v'_0.0deg_0.0deg",
            'NORMAL_W255_LUM_0DEG_10DEG': "normal_W255_Lum_0.0deg_10.0deg",
            'NORMAL_W255_U_0DEG_10DEG': "normal_W255_u'_0.0deg_10.0deg",
            'NORMAL_W255_V_0DEG_10DEG': "normal_W255_v'_0.0deg_10.0deg",
            'NORMAL_W255_LUM_0DEG_20DEG': "normal_W255_Lum_0.0deg_20.0deg",
            'NORMAL_W255_U_0DEG_20DEG': "normal_W255_u'_0.0deg_20.0deg",
            'NORMAL_W255_V_0DEG_20DEG': "normal_W255_v'_0.0deg_20.0deg",
            'NORMAL_W255_LUM_0DEG_30DEG': "normal_W255_Lum_0.0deg_30.0deg",
            'NORMAL_W255_U_0DEG_30DEG': "normal_W255_u'_0.0deg_30.0deg",
            'NORMAL_W255_V_0DEG_30DEG': "normal_W255_v'_0.0deg_30.0deg",
            'NORMAL_W255_LUM_10EG_0EG': "normal_W255_Lum_10.0deg_0.0deg",
            'NORMAL_W255_U_10DEG_0DEG': "normal_W255_u'_10.0deg_0.0deg",
            'NORMAL_W255_V_10DEG_0DEG': "normal_W255_v'_10.0deg_0.0deg",
            'NORMAL_W255_LUM_20DEG_0DEG': "normal_W255_Lum_20.0deg_0.0deg",
            'NORMAL_W255_U_20DEG_0DEG': "normal_W255_u'_20.0deg_0.0deg",
            'NORMAL_W255_V_20DEG_0DEG': "normal_W255_v'_20.0deg_0.0deg",
            'NORMAL_W255_LUM_30DEG_0DEG': "normal_W255_Lum_30.0deg_0.0deg",
            'NORMAL_W255_U_30DEG_0DEG': "normal_W255_u'_30.0deg_0.0deg",
            'NORMAL_W255_V_30DEG_0EG': "normal_W255_v'_30.0deg_0.0deg",
            'NORMAL_W255_MAX_LUM': "normal_W255_Max_Lum",
            'NORMAL_W255_MAX_LUM_U': "normal_W255_Max_Lum_u'",
            'NORMAL_W255_MAX_LUM_V': "normal_W255_Max_Lum_v'",
            'NORMAL_W255_MAX_LUM_X_DEG': "normal_W255_Max_Lum_x(deg)",
            'NORMAL_W255_MAX_LUM_Y_DEG': "normal_W255_Max_Lum_y(deg)",
            'NORMAL_W255_LUM_MEAN_10DEG': "normal_W255_Lum_mean_10deg",
            'NORMAL_W255_LUM_MEAN_20DEG': "normal_W255_Lum_mean_20deg",
            'NORMAL_W255_LUM_MEAN_30DEG': "normal_W255_Lum_mean_30deg",
            'NORMAL_W255_LUM_DELTA_10DEG': "normal_W255_Lum_delta_10deg",
            'NORMAL_W255_LUM_DELTA_20DEG': "normal_W255_Lum_delta_20deg",
            'NORMAL_W255_LUM_DELTA_30DEG': "normal_W255_Lum_delta_30deg",
            'NORMAL_W255_LUM_SSR_10DEG': "normal_W255_Lum_SSR_10deg",
            'NORMAL_W255_LUM_SSR_20DEG': "normal_W255_Lum_SSR_20deg",
            'NORMAL_W255_LUM_SSR_30DEG': "normal_W255_Lum_SSR_30deg",
            'NORMAL_W255_LUM_R_ONAXIS_10DEG': "normal_W255_Lum_Ratio>0.8OnAxisLum_10deg",
            'NORMAL_W255_LUM_R_ONAXIS_20DEG': "normal_W255_Lum_Ratio>0.8OnAxisLum_20deg",
            'NORMAL_W255_LUM_R_ONAXIS_30DEG': "normal_W255_Lum_Ratio>0.8OnAxisLum_30deg",
            'NORMAL_W255_LUM_R_MAX_10DEG': "normal_W255_Lum_Ratio>0.8MaxLum_10deg",
            'NORMAL_W255_LUM_R_MAX_20DEG': "normal_W255_Lum_Ratio>0.8MaxLum_20deg",
            'NORMAL_W255_LUM_R_MAX_30DEG': "normal_W255_Lum_Ratio>0.8MaxLum_30deg",
            'NORMAL_W255_U_MEAN_10DEG': "normal_W255_u'_mean_10deg",
            'NORMAL_W255_U_MEAN_20DEG': "normal_W255_u'_mean_20deg",
            'NORMAL_W255_U_MEAN_30DEG': "normal_W255_u'_mean_30deg",
            'NORMAL_W255_V_MEAN_10DEG': "normal_W255_v'_mean_10deg",
            'NORMAL_W255_V_MEAN_20DEG': "normal_W255_v'_mean_20deg",
            'NORMAL_W255_V_MEAN_30DEG': "normal_W255_v'_mean_30deg",
            'NORMAL_W255_UV_ONAXIS_10DEG': "normal_W255_u'v'_delta_to_OnAxis_10deg",
            'NORMAL_W255_UV_ONAXIS_20DEG': "normal_W255_u'v'_delta_to_OnAxis_20deg",
            'NORMAL_W255_UV_ONAXIS_30DEG': "normal_W255_u'v'_delta_to_OnAxis_30deg",
            'NORMAL_W255_UV__RATIO_10DEG': "normal_W255_u'v'_delta<0.01_Ratio_10deg",
            'NORMAL_W255_UV_RATIO_20DEG': "normal_W255_u'v'_delta<0.01_Ratio_20deg",
            'NORMAL_W255_UV_RATIO_30DEG': "normal_W255_u'v'_delta<0.01_Ratio_30deg",
            'NORMAL_W255_EXPTIME_FILTERX': "normal_W255_ExposureTime_Filter_X",
            'NORMAL_W255_EXPTIME_FILTERXZ': "normal_W255_ExposureTime_Filter_Xz",
            'NORMAL_W255_EXPTIME_FILTERYA': "normal_W255_ExposureTime_Filter_Ya",
            'NORMAL_W255_EXPTIME_FILTERYB': "normal_W255_ExposureTime_Filter_Yb",
            'NORMAL_W255_EXPTIME_FILTERZ': "normal_W255_ExposureTime_Filter_Z",
            'NORMAL_R255_LUM_N10DEG_0DEG': "normal_R255_Lum_-10.0deg_0.0deg",
            'NORMAL_R255_U_N10DEG_0DEG': "normal_R255_u'_-10.0deg_0.0deg",
            'NORMAL_R255_V_N10DEG_0DEG': "normal_R255_v'_-10.0deg_0.0deg",
            'NORMAL_R255_LUM_N20DEG_0DEG': "normal_R255_Lum_-20.0deg_0.0deg",
            'NORMAL_R255_U_N20DEG_0DEG': "normal_R255_u'_-20.0deg_0.0deg",
            'NORMAL_R255_V_N20DEG_0DEG': "normal_R255_v'_-20.0deg_0.0deg",
            'NORMAL_R255_LUM_N30DEG_0DEG': "normal_R255_Lum_-30.0deg_0.0deg",
            'NORMAL_R255_U_N30DEG_0DEG': "normal_R255_u'_-30.0deg_0.0deg",
            'NORMAL_R255_V_N30DEG_0DEG': "normal_R255_v'_-30.0deg_0.0deg",
            'NORMAL_R255_LUM_0DEG_N10DEG': "normal_R255_Lum_0.0deg_-10.0deg",
            'NORMAL_R255_U_0DEG_N10DEG': "normal_R255_u'_0.0deg_-10.0deg",
            'NORMAL_R255_V_0DEG_N10DEG': "normal_R255_v'_0.0deg_-10.0deg",
            'NORMAL_R255_LUM_0DEG_N20DEG': "normal_R255_Lum_0.0deg_-20.0deg",
            'NORMAL_R255_U_0DEG_N20DEG': "normal_R255_u'_0.0deg_-20.0deg",
            'NORMAL_R255_V_0DEG_N20DEG': "normal_R255_v'_0.0deg_-20.0deg",
            'NORMAL_R255_LUM_0DEG_N30DEG': "normal_R255_Lum_0.0deg_-30.0deg",
            'NORMAL_R255_U_0DEG_N30DEG': "normal_R255_u'_0.0deg_-30.0deg",
            'NORMAL_R255_V_0DEG_N30DEG': "normal_R255_v'_0.0deg_-30.0deg",
            'NORMAL_R255_LUM_0DEG_0DEG': "normal_R255_Lum_0.0deg_0.0deg",
            'NORMAL_R255_U_0DEG_0DEG': "normal_R255_u'_0.0deg_0.0deg",
            'NORMAL_R255_V_0DEG_0DEG': "normal_R255_v'_0.0deg_0.0deg",
            'NORMAL_R255_LUM_0DEG_10DEG': "normal_R255_Lum_0.0deg_10.0deg",
            'NORMAL_R255_U_0DEG_10DEG': "normal_R255_u'_0.0deg_10.0deg",
            'NORMAL_R255_V_0DEG_10DEG': "normal_R255_v'_0.0deg_10.0deg",
            'NORMAL_R255_LUM_0DEG_20DEG': "normal_R255_Lum_0.0deg_20.0deg",
            'NORMAL_R255_U_0DEG_20DEG': "normal_R255_u'_0.0deg_20.0deg",
            'NORMAL_R255_V_0DEG_20DEG': "normal_R255_v'_0.0deg_20.0deg",
            'NORMAL_R255_LUM_0DEG_30DEG': "normal_R255_Lum_0.0deg_30.0deg",
            'NORMAL_R255_U_0DEG_30DEG': "normal_R255_u'_0.0deg_30.0deg",
            'NORMAL_R255_V_0DEG_30DEG': "normal_R255_v'_0.0deg_30.0deg",
            'NORMAL_R255_LUM_10DEG_0DEG': "normal_R255_Lum_10.0deg_0.0deg",
            'NORMAL_R255_U_10DEG_0DEG': "normal_R255_u'_10.0deg_0.0deg",
            'NORMAL_R255_V_10DEG_0DEG': "normal_R255_v'_10.0deg_0.0deg",
            'NORMAL_R255_LUM_20DEG_0DEG': "normal_R255_Lum_20.0deg_0.0deg",
            'NORMAL_R255_U_20DEG_0DEG': "normal_R255_u'_20.0deg_0.0deg",
            'NORMAL_R255_V_20DEG_0DEG': "normal_R255_v'_20.0deg_0.0deg",
            'NORMAL_R255_LUM_30DEG_0DEG': "normal_R255_Lum_30.0deg_0.0deg",
            'NORMAL_R255_U_30DEG_0DEG': "normal_R255_u'_30.0deg_0.0deg",
            'NORMAL_R255_V_30DEG_0DEG': "normal_R255_v'_30.0deg_0.0deg",
            'NORMAL_R255_U_MEAN_10DEG': "normal_R255_u'_mean_10deg",
            'NORMAL_R255_U_MEAN_20DEG': "normal_R255_u'_mean_20deg",
            'NORMAL_R255_U_MEAN_30DEG': "normal_R255_u'_mean_30deg",
            'NORMAL_R255_V_MEAN_10DEG': "normal_R255_v'_mean_10deg",
            'NORMAL_R255_V_MEAN_20DEG': "normal_R255_v'_mean_20deg",
            'NORMAL_R255_V_MEAN_30DEG': "normal_R255_v'_mean_30deg",
            'NORMAL_R255_UV_ONAXIS_10DEG': "normal_R255_u'v'_delta_to_OnAxis_10deg",
            'NORMAL_R255_UV_ONAXIS_20DEG': "normal_R255_u'v'_delta_to_OnAxis_20deg",
            'NORMAL_R255_UV_ONAXIS_30DEG': "normal_R255_u'v'_delta_to_OnAxis_30deg",
            'NORMAL_R255_UV_RATIO_10DEG': "normal_R255_u'v'_delta<0.01_Ratio_10deg",
            'NORMAL_R255_UV_RATIO_20DEG': "normal_R255_u'v'_delta<0.01_Ratio_20deg",
            'NORMAL_R255_UV_RATIO_30DEG': "normal_R255_u'v'_delta<0.01_Ratio_30deg",
            'NORMAL_R255_EXPTIME_FILTERX': "normal_R255_ExposureTime_Filter_X",
            'NORMAL_R255_EXPTIME_FILTERXZ': "normal_R255_ExposureTime_Filter_Xz",
            'NORMAL_R255_EXPTIME_FILTERYA': "normal_R255_ExposureTime_Filter_Ya",
            'NORMAL_R255_EXPTIME_FILTERYB': "normal_R255_ExposureTime_Filter_Yb",
            'NORMAL_R255_EXPTIME_FILTERZ': "normal_R255_ExposureTime_Filter_Z",
            'NORMAL_G255_LUM_N10DEG_0DEG': "normal_G255_Lum_-10.0deg_0.0deg",
            'NORMAL_G255_U_N10DEG_0DEG': "normal_G255_u'_-10.0deg_0.0deg",
            'NORMAL_G255_V_N10DEG_0DEG': "normal_G255_v'_-10.0deg_0.0deg",
            'NORMAL_G255_LUM_N20DEG_0DEG': "normal_G255_Lum_-20.0deg_0.0deg",
            'NORMAL_G255_U_N20DEG_0DEG': "normal_G255_u'_-20.0deg_0.0deg",
            'NORMAL_G255_V_N20DEG_0DEG': "normal_G255_v'_-20.0deg_0.0deg",
            'NORMAL_G255_LUM_N30DEG_0DEG': "normal_G255_Lum_-30.0deg_0.0deg",
            'NORMAL_G255_U_N30DEG_0DEG': "normal_G255_u'_-30.0deg_0.0deg",
            'NORMAL_G255_V_N30DEG_0DEG': "normal_G255_v'_-30.0deg_0.0deg",
            'NORMAL_G255_LUM_0DEG_N10DEG': "normal_G255_Lum_0.0deg_-10.0deg",
            'NORMAL_G255_U_0DEG_N10DEG': "normal_G255_u'_0.0deg_-10.0deg",
            'NORMAL_G255_V_0DEG_N10DEG': "normal_G255_v'_0.0deg_-10.0deg",
            'NORMAL_G255_LUM_0DEG_N20DEG': "normal_G255_Lum_0.0deg_-20.0deg",
            'NORMAL_G255_U_0DEG_N20DEG': "normal_G255_u'_0.0deg_-20.0deg",
            'NORMAL_G255_V_0DEG_N20DEG': "normal_G255_v'_0.0deg_-20.0deg",
            'NORMAL_G255_LUM_0DEG_N30DEG': "normal_G255_Lum_0.0deg_-30.0deg",
            'NORMAL_G255_U_0DEG_N30DEG': "normal_G255_u'_0.0deg_-30.0deg",
            'NORMAL_G255_V_0DEG_N30DEG': "normal_G255_v'_0.0deg_-30.0deg",
            'NORMAL_G255_LUM_0DEG_0DEG': "normal_G255_Lum_0.0deg_0.0deg",
            'NORMAL_G255_U_0DEG_0DEG': "normal_G255_u'_0.0deg_0.0deg",
            'NORMAL_G255_V_0DEG_0DEG': "normal_G255_v'_0.0deg_0.0deg",
            'NORMAL_G255_LUM_0DEG_10DEG': "normal_G255_Lum_0.0deg_10.0deg",
            'NORMAL_G255_U_0DEG_10DEG': "normal_G255_u'_0.0deg_10.0deg",
            'NORMAL_G255_V_0DEG_10DEG': "normal_G255_v'_0.0deg_10.0deg",
            'NORMAL_G255_LUM_0DEG_20DEG': "normal_G255_Lum_0.0deg_20.0deg",
            'NORMAL_G255_U_0DEG_20DEG': "normal_G255_u'_0.0deg_20.0deg",
            'NORMAL_G255_V_0DEG_20DEG': "normal_G255_v'_0.0deg_20.0deg",
            'NORMAL_G255_LUM_0DEG_30DEG': "normal_G255_Lum_0.0deg_30.0deg",
            'NORMAL_G255_U_0DEG_30DEG': "normal_G255_u'_0.0deg_30.0deg",
            'NORMAL_G255_V_0DEG_30DEG': "normal_G255_v'_0.0deg_30.0deg",
            'NORMAL_G255_LUM_10DEG_0DEG': "normal_G255_Lum_10.0deg_0.0deg",
            'NORMAL_G255_U_10DEG_0DEG': "normal_G255_u'_10.0deg_0.0deg",
            'NORMAL_G255_V_10DEG_0DEG': "normal_G255_v'_10.0deg_0.0deg",
            'NORMAL_G255_LUM_20DEG_0DEG': "normal_G255_Lum_20.0deg_0.0deg",
            'NORMAL_G255_U_20DEG_0DEG': "normal_G255_u'_20.0deg_0.0deg",
            'NORMAL_G255_V_20DEG_0DEG': "normal_G255_v'_20.0deg_0.0deg",
            'NORMAL_G255_LUM_30DEG_0DEG': "normal_G255_Lum_30.0deg_0.0deg",
            'NORMAL_G255_U_30DEG_0DEG': "normal_G255_u'_30.0deg_0.0deg",
            'NORMAL_G255_V_30DEG_0DEG': "normal_G255_v'_30.0deg_0.0deg",
            'NORMAL_G255_U_MEAN_10DEG': "normal_G255_u'_mean_10deg",
            'NORMAL_G255_U_MEAN_20DEG': "normal_G255_u'_mean_20deg",
            'NORMAL_G255_U_MEAN_30DEG': "normal_G255_u'_mean_30deg",
            'NORMAL_G255_V_MEAN_10DEG': "normal_G255_v'_mean_10deg",
            'NORMAL_G255_V_MEAN_20DEG': "normal_G255_v'_mean_20deg",
            'NORMAL_G255_V_MEAN_30DEG': "normal_G255_v'_mean_30deg",
            'NORMAL_G255_UV_ONAXIS_10DEG': "normal_G255_u'v'_delta_to_OnAxis_10deg",
            'NORMAL_G255_UV_ONAXIS_20DEG': "normal_G255_u'v'_delta_to_OnAxis_20deg",
            'NORMAL_G255_UV_ONAXIS_30DEG': "normal_G255_u'v'_delta_to_OnAxis_30deg",
            'NORMAL_G255_UV_RATIO_10DEG': "normal_G255_u'v'_delta<0.01_Ratio_10deg",
            'NORMAL_G255_UV_RATIO_20DEG': "normal_G255_u'v'_delta<0.01_Ratio_20deg",
            'NORMAL_G255_UV_RATIO_30DEG': "normal_G255_u'v'_delta<0.01_Ratio_30deg",
            'NORMAL_G255_EXPTIME_FILTERX': "normal_G255_ExposureTime_Filter_X",
            'NORMAL_G255_EXPTIME_FILTERXZ': "normal_G255_ExposureTime_Filter_Xz",
            'NORMAL_G255_EXPTIME_FILTERYA': "normal_G255_ExposureTime_Filter_Ya",
            'NORMAL_G255_EXPTIME_FILTERYB': "normal_G255_ExposureTime_Filter_Yb",
            'NORMAL_G255_EXPTIME_FILTERZ': "normal_G255_ExposureTime_Filter_Z",
            'NORMAL_B255_LUM_N10DEG_0DEG': "normal_B255_Lum_-10.0deg_0.0deg",
            'NORMAL_B255_U_N10DEG_0DEG': "normal_B255_u'_-10.0deg_0.0deg",
            'NORMAL_B255_V_N10DEG_0DEG': "normal_B255_v'_-10.0deg_0.0deg",
            'NORMAL_B255_LUM_N20DEG_0DEG': "normal_B255_Lum_-20.0deg_0.0deg",
            'NORMAL_B255_U_N20DEG_0DEG': "normal_B255_u'_-20.0deg_0.0deg",
            'NORMAL_B255_V_N20DEG_0DEG': "normal_B255_v'_-20.0deg_0.0deg",
            'NORMAL_B255_LUM_N30DEG_0DEG': "normal_B255_Lum_-30.0deg_0.0deg",
            'NORMAL_B255_U_N30DEG_0DEG': "normal_B255_u'_-30.0deg_0.0deg",
            'NORMAL_B255_V_N30DEG_0DEG': "normal_B255_v'_-30.0deg_0.0deg",
            'NORMAL_B255_LUM_0DEG_N10DEG': "normal_B255_Lum_0.0deg_-10.0deg",
            'NORMAL_B255_U_0DEG_N10DEG': "normal_B255_u'_0.0deg_-10.0deg",
            'NORMAL_B255_V_0DEG_N10DEG': "normal_B255_v'_0.0deg_-10.0deg",
            'NORMAL_B255_LUM_0DEG_N20DEG': "normal_B255_Lum_0.0deg_-20.0deg",
            'NORMAL_B255_U_0DEG_N20DEG': "normal_B255_u'_0.0deg_-20.0deg",
            'NORMAL_B255_V_0DEG_N20DEG': "normal_B255_v'_0.0deg_-20.0deg",
            'NORMAL_B255_LUM_0DEG_N30DEG': "normal_B255_Lum_0.0deg_-30.0deg",
            'NORMAL_B255_U_0DEG_N30DEG': "normal_B255_u'_0.0deg_-30.0deg",
            'NORMAL_B255_V_0DEG_N30DEG': "normal_B255_v'_0.0deg_-30.0deg",
            'NORMAL_B255_LUM_0DEG_0DEG': "normal_B255_Lum_0.0deg_0.0deg",
            'NORMAL_B255_U_0DEG_0DEG': "normal_B255_u'_0.0deg_0.0deg",
            'NORMAL_B255_V_0DEG_0DEG': "normal_B255_v'_0.0deg_0.0deg",
            'NORMAL_B255_LUM_0DEG_10DEG': "normal_B255_Lum_0.0deg_10.0deg",
            'NORMAL_B255_U_0DEG_10DEG': "normal_B255_u'_0.0deg_10.0deg",
            'NORMAL_B255_V_0DEG_10DEG': "normal_B255_v'_0.0deg_10.0deg",
            'NORMAL_B255_LUM_0DEG_20DEG': "normal_B255_Lum_0.0deg_20.0deg",
            'NORMAL_B255_U_0DEG_20DEG': "normal_B255_u'_0.0deg_20.0deg",
            'NORMAL_B255_V_0DEG_20DEG': "normal_B255_v'_0.0deg_20.0deg",
            'NORMAL_B255_LUM_0DEG_30DEG': "normal_B255_Lum_0.0deg_30.0deg",
            'NORMAL_B255_U_0DEG_30DEG': "normal_B255_u'_0.0deg_30.0deg",
            'NORMAL_B255_V_0DEG_30DEG': "normal_B255_v'_0.0deg_30.0deg",
            'NORMAL_B255_LUM_10DEG_0DEG': "normal_B255_Lum_10.0deg_0.0deg",
            'NORMAL_B255_U_10DEG_0DEG': "normal_B255_u'_10.0deg_0.0deg",
            'NORMAL_B255_V_10DEG_0DEG': "normal_B255_v'_10.0deg_0.0deg",
            'NORMAL_B255_LUM_20DEG_0DEG': "normal_B255_Lum_20.0deg_0.0deg",
            'NORMAL_B255_U_20DEG_0DEG': "normal_B255_u'_20.0deg_0.0deg",
            'NORMAL_B255_V_20DEG_0DEG': "normal_B255_v'_20.0deg_0.0deg",
            'NORMAL_B255_LUM_30DEG_0DEG': "normal_B255_Lum_30.0deg_0.0deg",
            'NORMAL_B255_U_30DEG_0DEG': "normal_B255_u'_30.0deg_0.0deg",
            'NORMAL_B255_V_30DEG_0DEG': "normal_B255_v'_30.0deg_0.0deg",
            'NORMAL_B255_U_MEAN_10DEG': "normal_B255_u'_mean_10deg",
            'NORMAL_B255_U_MEAN_20DEG': "normal_B255_u'_mean_20deg",
            'NORMAL_B255_U_MEAN_30DEG': "normal_B255_u'_mean_30deg",
            'NORMAL_B255_V_MEAN_10DEG': "normal_B255_v'_mean_10deg",
            'NORMAL_B255_V_MEAN_20DEG': "normal_B255_v'_mean_20deg",
            'NORMAL_B255_V_MEAN_30DEG': "normal_B255_v'_mean_30deg",
            'NORMAL_B255_UV_ONAXIS_10DEG': "normal_B255_u'v'_delta_to_OnAxis_10deg",
            'NORMAL_B255_UV_ONAXIS_20DEG': "normal_B255_u'v'_delta_to_OnAxis_20deg",
            'NORMAL_B255_UV_ONAXIS_30DEG': "normal_B255_u'v'_delta_to_OnAxis_30deg",
            'NORMAL_B255_UV_RATIO_10DEG': "normal_B255_u'v'_delta<0.01_Ratio_10deg",
            'NORMAL_B255_UV_RATIO_20DEG': "normal_B255_u'v'_delta<0.01_Ratio_20deg",
            'NORMAL_B255_UV_RATIO_30DEG': "normal_B255_u'v'_delta<0.01_Ratio_30deg",
            'NORMAL_B255_EXPTIME_FILTERX': "normal_B255_ExposureTime_Filter_X",
            'NORMAL_B255_EXPTIME_FILTERXZ': "normal_B255_ExposureTime_Filter_Xz",
            'NORMAL_B255_EXPTIME_FILTERYA': "normal_B255_ExposureTime_Filter_Ya",
            'NORMAL_B255_EXPTIME_FILTERYB': "normal_B255_ExposureTime_Filter_Yb",
            'NORMAL_B255_EXPTIME_FILTERZ': "normal_B255_ExposureTime_Filter_Z",
            'NORMAL_GRDIST_Y_MAXLUM': "normal_GreenDistortion_Y_MaxLum",
            'NORMAL_GRDIST_Y_NUMOFDOTS': "normal_GreenDistortion_Y_NumberOfDots",
            'NORMAL_GRDIST_Y_DISPCEN_X_CONO': "normal_GreenDistortion_Y_DispCen_x_cono",
            'NORMAL_GRDIST_Y_DISPCEN_Y_CONO': "normal_GreenDistortion_Y_DispCen_y_cono",
            'NORMAL_GRDIST_Y_DISPCEN_X_DISP': "normal_GreenDistortion_Y_DispCen_x_display",
            'NORMAL_GRDIST_Y_DISPCEN_Y_DISP': "normal_GreenDistortion_Y_DispCen_y_display",
            'NORMAL_GRDIST_Y_DISP_ROTATE_X': "normal_GreenDistortion_Y_Disp_Rotate_x",
            'NORMAL_GRDIST_Y_DISP_ROTATE_Y': "normal_GreenDistortion_Y_Disp_Rotate_y",
            'NORMAL_GRDIST_EXPTIME_FILTERX': "normal_GreenDistortion_ExposureTime_Filter_X",
            'NORMAL_GRDIST_EXPTIME_FILTERXZ': "normal_GreenDistortion_ExposureTime_Filter_Xz",
            'NORMAL_GRDIST_EXPTIME_FILTERYA': "normal_GreenDistortion_ExposureTime_Filter_Ya",
            'NORMAL_GRDIST_EXPTIME_FILTERYB': "normal_GreenDistortion_ExposureTime_Filter_Yb",
            'NORMAL_GRDIST_EXPTIME_FILTERZ': "normal_GreenDistortion_ExposureTime_Filter_Z",
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
        log_2_mes['STARTTIME'] = datetime.datetime.strptime(log_2_mes['STARTTIME'], '%Y%m%d-%H%M%S')
        log_2_mes['ENDTIME'] = datetime.datetime.strptime(log_2_mes['ENDTIME'], '%Y%m%d-%H%M%S')

        log_2_mes['MODEL_NAME'] = self._machine_type
        log_2_mes['OVERALLERRORCODE'] = ';'.join(err_codes)
        insert_response = self.lcd_avi_myzy_log_loader(log_2_mes)
        return insert_response

    # <editor-fold desc="API interface provided by Genius Inc.">
    def p5385_in_lot_info(self, uut_sn):
        count = 0
        success = False
        res = None
        while count < self._max_retries and (not success):
            try:
                client = suds.client.Client(SF_URL, timeout=self._time_out)
                res = client.service.GetInLotInfo(self._machine_type, uut_sn, '', '', '')
                if hasattr(res, 'STATUS') and (res.STATUS == 'SUCCESS'):
                    success = True
            except Exception as e:
                logging.error(f'Fail to call P5385_in_lot. Ex: {str(e)}')
            count += 1
        logging.info(f'Inlot: {count}, success: {success} <= {res}')
        return res

    def lcd_avi_myzy_log_loader(self, lcd_avi_data):
        count = 0
        success = False
        res = None
        while count < self._max_retries and (not success):
            try:
                client = suds.client.Client(SF_LOADER_URL, timeout=self._time_out)
                res = client.service.MOT_Overall_LOG_Loader(lcd_avi_data)
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
                    if save_results_from_logs_res[1] is not None:
                        os.remove(file_to_upload)
                    elif is_sent_mail_when_fail and MES_IT_MAIL_NOTIFICATION:  # 网络反馈为None，判定为网络异常
                        message_text = f'{MACHINE_TYPE}: {STATION_ID} FAIL TO SEND LOGS TO MES.'
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
    if (not MES_IN_LOT_CTRL) or MES_CHK_OFFLINE.get('mes_chk_offline'):
        ok_to_test_res = True
    else:
        ok_to_test_res = False
        try:
            validate_res = _ex_shop_floor.p5385_in_lot_info(serial)
            if hasattr(validate_res, 'STATUS'):
                inspection = None
                op_status = None
                if validate_res.STATUS.upper() == 'SUCCESS':
                    inspection = validate_res.INSPECTION_RESULT
                    op_status = validate_res.OPERATION_STATUS
                    if validate_res.INSPECTION_RESULT in ['PASS']:
                        ok_to_test_res = True
                msg = '过站检测失败 站点状态: {0}, 前站结果: {1}, OP_STATUS: {2}'.format(validate_res.STATUS, inspection, op_status)
            else:
                msg = '过站检测失败 网络异常'
            if not ok_to_test_res:
                tkinter.simpledialog.messagebox.showinfo('提示', msg)

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

    return ok_to_test_res


def save_results(test_log):
    """

    :type test_log: hardware_station_common.test_station.test_log.TestRecord
    """
    res = False
    try:
        res = save_results_from_logs(test_log.get_file_path(), log_upload_after_test=True)[0]
    except Exception as e:
        logging.error(f'Exception --> {str(e)}')
    return res


def save_results_from_logs(log_file_path, log_upload_after_test=False):
    web_res_msg = None
    save_result_res = False

    with open(log_file_path) as file:
        contents = file.readlines()

    log_items = [c.splitlines(keepends=False)[0].split(', ') for c in contents]
    uut_sn = [c[2] for c in log_items if c[1] == 'UUT_Serial_Number'][0]
    overall_result = [c[2] for c in log_items if c[1] == 'Overall_Result'][0]
    overall_errcode = [c[2] for c in log_items if c[1] == 'Overall_ErrorCode'][0]

    logging.info('测试结果上传MES 系统 >>>>>>>>>>>>>>>>>>>>>>>>>>> {0}, ErrCode = {1}'
                 .format(uut_sn, overall_errcode))
    try:
        if not os.path.exists(SHOP_FLOOR_BAK_DIR):
            os.makedirs(SHOP_FLOOR_BAK_DIR)
            os.chmod(SHOP_FLOOR_BAK_DIR, 0o777)
        if not os.path.exists(SHOP_FLOOR_FAIL_TO_UPLOAD):
            os.makedirs(SHOP_FLOOR_FAIL_TO_UPLOAD)
            os.chmod(SHOP_FLOOR_FAIL_TO_UPLOAD, 0o777)

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
    except Exception as e:
        logging.error('ok to test exp: {0}'.format(str(e)))
    if not save_result_res:
        msg = f'上传MES 失败 {uut_sn}'
        bak_log_file_path = os.path.join(SHOP_FLOOR_BAK_DIR, os.path.basename(log_file_path))  # 网络异常时，数组转存
        if web_res_msg is not None:  # 非网络异常时，数据转存
            bak_log_file_path = os.path.join(SHOP_FLOOR_FAIL_TO_UPLOAD, os.path.basename(log_file_path))
        if ((not os.path.exists(bak_log_file_path)) or
                (not os.path.samefile(bak_log_file_path, log_file_path))):
            shutil.copyfile(log_file_path, bak_log_file_path)
            msg += f'，数据转存至 {bak_log_file_path}'
        logging.info(f'{msg} --> {web_res_msg}')
        print(msg)
        if (not MES_CHK_OFFLINE.get('mes_chk_offline')) and log_upload_after_test:  # 在线上传时，如不成功，需要执行报警提示
            tkinter.simpledialog.messagebox.showinfo('提示', msg)

    logging.info('{0}***********************************{1}....\n'.format(uut_sn, log_file_path))
    return save_result_res, web_res_msg


logger = logging.getLogger()
if not logger.hasHandlers():
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    log_fn = time.strftime('%Y_%m_%d', time.localtime(time.time()))

    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    chlr = logging.StreamHandler()
    chlr.setFormatter(logging.Formatter('%(levelname)s      %(message)s'))
    chlr.setLevel('INFO')
    fn = os.path.join(os.path.curdir, '../shop_floor_interface/logs',
                                      'sf_i_{0}_{1}_{2}.log'.format(MACHINE_TYPE, STATION_ID, log_fn))
    log_dir = os.path.dirname(fn)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        os.chmod(log_dir, 0o777)
    fhlr = logging.FileHandler(fn)
    fhlr.setFormatter(formatter)
    logger.setLevel('INFO')
    logger.addHandler(chlr)
    logger.addHandler(fhlr)

    _ex_shop_floor = ShopFloor_genius(MACHINE_TYPE, STATION_ID)  # type: ShopFloor_genius

    daemon_thr = threading.Thread(target=daemon_upload, args=())
    daemon_thr.setDaemon(True)
    daemon_thr.start()
    MES_CHK_OFFLINE = {}


if __name__ == '__main__':
    logging.info('----------------------------')
    logging.debug('+' * 20)
    log_dir = r'c:\oculus\factory_test_omi\factory_test_stations\factory-test_logs'
    fn_name = r''
    serial_numbers = ['P1-123456789', 'P1-234567890', 'P1-234567890', 'P1-999999999']
    for serial_number in serial_numbers:
        logging.info('----------------------------{0}'.format(serial_number))
        ok_to_test(serial_number)
