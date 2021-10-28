from typing import Callable
import hardware_station_common.test_station.test_station as test_station
import psutil
import test_station.test_fixture.test_fixture_seacliff_vid as test_fixture_seacliff_vid
from test_station.test_fixture.test_fixture_project_station import projectstationFixture
import test_station.test_equipment.test_equipment_seacliff_vid as test_equipment_seacliff_vid
from test_station.dut.dut import pancakeDut, projectDut, DUTError
import time
import os
import types
import re
import pprint
import glob
import numpy as np
import sys
import cv2
import multiprocessing as mp
import json
import collections
import math


class seacliffvidError(Exception):
    pass


class seacliffvidStation(test_station.TestStation):
    """
        seacliffvid Station
    """

    def __init__(self, station_config, operator_interface):
        test_station.TestStation.__init__(self, station_config, operator_interface)
        self._fixture = test_fixture_seacliff_vid.seacliffvidFixture(station_config, operator_interface)
        self._overall_errorcode = ''
        self._first_failed_test_result = None


    def initialize(self):
        try:
            self._operator_interface.print_to_console("Initializing seacliff vid station...\n")
            self._fixture.initialize()
        except:
            raise

    def close(self):
        self._operator_interface.print_to_console("Close...\n")
        self._operator_interface.print_to_console("\there, I'm shutting the station down..\n")
        self._fixture.close()

    def _do_test(self, serial_number, test_log):
        self._overall_result = False
        self._overall_errorcode = ''

        the_unit = pancakeDut(serial_number, self._station_config, self._operator_interface)
        self._operator_interface.print_to_console("Testing Unit %s\n" % the_unit.serial_number)
        try:

            ### implement tests here.  Note that the test name matches one in the station_limits file ###
            a_result = 2
            test_log.set_measured_value_by_name("TEST ITEM", a_result)

        except seacliffvidError:
            self._operator_interface.print_to_console("Non-parametric Test Failure\n")
            return self.close_test(test_log)

        else:
            return self.close_test(test_log)

    def close_test(self, test_log):
        ### Insert code to gracefully restore fixture to known state, e.g. clear_all_relays() ###
        self._overall_result = test_log.get_overall_result()
        self._first_failed_test_result = test_log.get_first_failed_test_result()
        return self._overall_result, self._first_failed_test_result

    def is_ready(self):
        self._fixture.is_ready()
