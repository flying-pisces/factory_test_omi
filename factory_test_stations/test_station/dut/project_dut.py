import os
import time
import re
import numpy as np
import sys
import socket
import serial
import struct
import logging
import datetime
import string
import win32process
import win32event


# projectDut is just an example
class projectDut(object):
    """
        class for pancake uniformity DUT
            this is for doing all the specific things necessary to DUT
    """
    def __init__(self, serial_number, station_config, operator_interface):
        self._operator_interface = operator_interface
        self._station_config = station_config
        self._serial_number = serial_number

    def is_ready(self):
        pass

    def initialize(self, **kwargs):
        self._operator_interface.print_to_console("Initializing pancake Fixture_DUT.\n")

    def close(self):
        self._operator_interface.print_to_console("Closing pancake uniformity Fixture\n")

    def __getattr__(self, item):
        def not_find(*args, **kwargs):
            pass
        if item in ['screen_on', 'screen_off', 'display_color', 'reboot', 'display_image', 'nvm_read_statistics',
                    'nvm_write_data', '_get_color_ext', 'render_image', 'nvm_read_data', 'nvm_speed_mode',
                    'get_module_inplace', 'nvm_get_ecc', 'read_color_sensor', 'display_color_check', '']:
            return not_find