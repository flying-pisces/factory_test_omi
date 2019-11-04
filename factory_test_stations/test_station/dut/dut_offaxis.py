import hardware_station_common.test_station.dut
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
import cv2

import dut

class pancakeDutOffAxis(dut.pancakeDut):
    def __init__(self, serialNumber, station_config, operatorInterface):
        dut.pancakeDut.__init__(self, serialNumber, station_config, operatorInterface)

    def readColorSensor(self):
        dut.pancakeDut._write_serial(self._station_config.COMMAND_DISP_GETCOLOUR)
        response = dut.pancakeDut._read_response()
        rev = dut.pancakeDut._prase_respose(self._station_config.COMMAND_DISP_GETCOLOUR, response)
        if int(rev[0]) != 0:
            raise dut.DUTError('Read color sensor failed. \n')
        return tuple(map(lambda x: int(x, 16), rev))

    def display_color_check(self, color):
        color1 = np.uint8([[color]])
        hsv = cv2.cvtColor(color1, cv2.COLOR_BGR2HSV)
        h, s, v = tuple(hsv[0,0,:])
        return (self.station_config.DISP_CHECKER_L_HsvH <= h <= self.station_config.DISP_CHECKER_H_HsvH and
                self._station_config.DISP_CHECKER_L_HsvS <= s <= self._station_config.DISP_CHECKER_H_HsvS )

def print_to_console(self, msg):
    pass

if __name__ == "__main__" :
    import sys
    import types
    sys.path.append(r'..\..')
    import station_config
    import logging
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logging.getLogger(__name__).addHandler(ch)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    station_config.load_station('pancake_pixel')
    # station_config.load_station('pancake_uniformity')
    station_config.print_to_console = types.MethodType(print_to_console, station_config)

    the_unit = pancakeDutOffAxis(station_config, station_config, station_config)
    for idx in range(0, 100):

        print 'Loop ---> {}'.format(idx)

        pics = []
        # for i in range(3, 5):
        #     pics.append(r'img\line_{}.bmp'.format(i))
        #     # pics.append(r'img\line_r_{}.bmp'.format(i))
        #
        # for i in range(4, 11, 2):
        #     pics.append(r'img\spot_{}.bmp'.format(i))
        #     # pics.append(r'img\spot_r_{}.bmp'.format(i))

        for c in os.listdir('img'):
            if c.endswith(".bmp"):
                pics.append(r'img\{}'.format(c))

        print 'pic - count {0}'.format(len(pics))

        the_unit.render_image(pics)

        time.sleep(1)

        the_unit.initialize()
        try:
            the_unit.connect_display()
            # the_unit.screen_on()
            # time.sleep(1)
            # the_unit.display_color()
            # time.sleep(1)
            # print the_unit.vsync_microseconds()
            # for c in [(0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255)]:
            for c in range(0, len(pics)):
                the_unit.display_image(c, True)
                # the_unit.display_color(c)
                time.sleep(0.5)
            the_unit.screen_off()
        except DUTOffAxisError as e:
            print e.message
        finally:
            time.sleep(2)
            the_unit.close()