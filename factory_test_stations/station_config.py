__author__ = 'chuckyin'
#!/usr/bin/env python
# pylint: disable 
# Important note: for True/False settings, these do NOT need quotes.
# but they do need capital first letter.  (i.e. True or False)
import os
import sys

import platform
import psutil
import requests
import logging
try:
    import suds.client
except ImportError:
    try:
        # Try the Python 3 compatible version
        from suds import client as suds_client
        import types
        suds = types.ModuleType('suds')
        suds.client = suds_client
    except ImportError:
        # Provide a stub if suds is not available
        class suds:
            class client:
                pass
import tkinter.simpledialog
import lxml
from lxml import etree

# Cross-platform sound support
try:
    if platform.system() == "Windows":
        import winsound
    else:
        # On non-Windows platforms, provide a stub for winsound
        class winsound:
            @staticmethod
            def Beep(frequency, duration):
                # Use system bell or print for non-Windows platforms
                try:
                    import os
                    if platform.system() == "Darwin":  # macOS
                        os.system("afplay /System/Library/Sounds/Ping.aiff")
                    elif platform.system() == "Linux":
                        os.system("echo -e '\a'")  # Terminal bell
                except:
                    print(f"Beep: {frequency}Hz for {duration}ms")
            
            @staticmethod
            def PlaySound(sound, flags):
                try:
                    import os
                    if platform.system() == "Darwin":  # macOS
                        os.system("afplay /System/Library/Sounds/Ping.aiff")
                    elif platform.system() == "Linux":
                        os.system("echo -e '\a'")  # Terminal bell
                except:
                    print(f"PlaySound: {sound}")
except ImportError:
    # Fallback if winsound is not available
    class winsound:
        @staticmethod
        def Beep(frequency, duration):
            print(f"Beep: {frequency}Hz for {duration}ms")
        
        @staticmethod
        def PlaySound(sound, flags):
            print(f"PlaySound: {sound}")


###################################
# station_type
#
# Valid values are 'UNIF', 'MURA'
STATION_NUMBER = 0
STATION_TYPE = ''


def load_station(station):
    global STATION_NUMBER
    global STATION_TYPE
    if not STATION_TYPE:
        STATION_TYPE = station
        STATION_NUMBER = 0
    #  add by elton:1028/2019
    config_path = os.getcwd()
    bak_cwd = os.getcwd()
    if os.path.exists(__file__):
        config_path = os.path.dirname(os.path.realpath(__file__))

    station_config_file = os.path.join(config_path, 'config', ('station_config_' + STATION_TYPE + '.py'))
    station_limits_file = os.path.join(config_path, 'config', ('station_limits_' + STATION_TYPE + '.py'))
    print(station_config_file)
    print(station_limits_file)
    try:
        #execfile(station_config_file, globals())  # imports station_config into current namespace
        #execfile(station_limits_file, globals())
        exec(open(station_config_file).read(), globals())
        #exec(open(station_limits_file).read(), globals())
    except:
        raise
    finally:
        os.path.curdir = bak_cwd
