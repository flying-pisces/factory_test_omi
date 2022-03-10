__author__ = 'chuckyin'
#!/usr/bin/env python
# pylint: disable 
# Important note: for True/False settings, these do NOT need quotes.
# but they do need capital first letter.  (i.e. True or False)
import os
import sys

import winsound
import psutil
import requests
import logging
import suds.client
import tkinter.simpledialog
import lxml
from lxml import etree
import importlib


###################################
# station_type
#
def load_station(station):
    #  add by elton:1028/2019
    config_path = os.getcwd()
    bak_cwd = os.getcwd()
    if os.path.exists(__file__):
        config_path = os.path.dirname(os.path.realpath(__file__))

    station_config_file = os.path.join(config_path, 'config', ('station_config_' + station))
    print(station_config_file)
    try:
        station_config_file_pth = os.path.dirname(station_config_file)
        sys.path.append(station_config_file_pth)
        cfg = importlib.__import__(os.path.basename(station_config_file), fromlist=[station_config_file_pth])
        globals().update(dict([(k, v) for k, v in cfg.__dict__.items() if k not in globals().keys()]))
        if 'STATION_TYPE' not in globals().keys():
            globals().update({
                'STATION_TYPE': station,
                'STATION_NUMBER': 0,
            })
    except Exception as e:
        print(f'Fail to load config =================={str(e)}=====================\n')
    finally:
        os.path.curdir = bak_cwd
