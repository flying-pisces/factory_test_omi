import hardware_station_common.test_station.dut as dut
import os
import time
import re
import numpy as np
import sys
import socket
import serial
import struct
import logging
import time
import string
import win32process
import win32event
import pywintypes

from factory_test_stations.test_station.dut.displayserver import DisplayServer

class DUT_cleanroom(dut):
  def __init__(self):
    super(DUT_cleanroom, self).__init__(type(self).__name__)
    self._display_server = None

  def initialize(self):
    custom_adb_path = "adb"
    self._display_server = DisplayServer(custom_adb_path=custom_adb_path)
    self._display_server.kill_server


  def connect_display(self, display_cycle_time=2, launch_time=4):
    if self.first_boot:
        self.first_boot = False
        # this should be set once, but run at least once on boot to ensure system settings are correct
        self._display_server.disable_animations()
        self._display_server.set_screen_timeout()
        self._display_server.set_displayserver_permissions()

    if self._display_server.is_connected() == False:
        self._display_server.connect()
    time.sleep(1)
    self._display_server.screen_off()
    time.sleep(display_cycle_time)
    self._display_server.screen_on()
    time.sleep(display_cycle_time)
    self._display_server.launch_displayserver()
    time.sleep(launch_time)
    self.panel_type_reboot = False
    return True

  def disconnect_display(self):
    retval = False
    self.screen_off()
    if self._display_server != None:
        retval = self._display_server.disconnect()
    return retval

  def screen_on(self):
    self._display_server.screen_on()

  def launch_displayserver(self):
    self._display_server.launch_displayserver()

  # -------------------------------------------------------------------------------------------------------------------- #
  def display_image(self, filename):
    """Display an image on the display.

    Args:
      filename: name of .pnd file to put on screen
    """
    self._display_server.display_image(filename)
    time.sleep(self.get_user_param('dut_displaysleeptime'))

  def display_color(self, color=(255,255,255)):
    self._display_server.display_color(color)
    time.sleep(self.get_user_param('dut_displaysleeptime'))

  def load_fragment_shader(self, shadername='frag.glsl'):
    self._display_server.load_fragment_shader(shadername)

  def vsync_microseconds(self):
    return(self._display_server.get_median_vsync_microseconds())
# -------------------------------------------------------------------------------------------------------------------- #
  def screen_off(self):
    if self._display_server != None and self._display_server.is_connected():
      self._display_server.screen_off()

  def send_data_as_file(self, data, remote_filename):
    self._display_server.send_data_as_file(data, remote_filename)

  def send_file(self, file, remote_filename):
    self._display_server.send_file(file, remote_filename)

  def ptb_detected(self):
      return len(self._display_server.list_devices())

  def ptb_booted(self):
      return self._display_server.is_ready()
  def get_displayserver_version(self):
      return self._display_server.version()
  def get_os_version(self):
      return self._display_server.get_build_fingerprint()


if __name__ == "__main__":
    the_unit = DUT_cleanroom()
    the_unit.initialize_user_parameters(the_unit.default_user_parameters())
    the_unit.initialize()
    print the_unit.ptb_detected()
    the_unit.connect_display()
    the_unit.screen_on()
    the_unit.launch_displayserver()
    the_unit.display_color()
    print the_unit.vsync_microseconds()

    FILENAME = "white.png"
    the_unit.display_image(FILENAME)
    time.sleep(5)
    the_unit.screen_off()
    time.sleep(5)
    print "Disconnecting display"
    the_unit.disconnect_display()

    #print(dir(the_unit))
    #print(type(the_unit))


