#!/usr/bin/env python
# -*- coding:utf-8 -*-

import cv2 as cv
import os
import numpy as np


class DutCheckerError(Exception):
    pass


class DutChecker(object):
    def __init__(self, station_config):
        self._cap = None
        self._latest_image = None
        self._template_dir = None
        self._minArea = station_config.DISP_CHECKER_MIN
        self._station_config = station_config
        self._dst = None

    def _blob_areas(self, image1):
        hsv = cv.cvtColor(image1, cv.COLOR_BGR2HSV)
        h, s, v = cv.split(hsv)

        kernel = np.ones((5, 5), dtype=np.uint8)
        erode_v = cv.erode(v, kernel, iterations=1)
        dilate_v = cv.dilate(erode_v, kernel, iterations=1)

        dst = cv.threshold(dilate_v, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
        img, contours, hierarchy = cv.findContours(dst, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)

        color_v = cv.cvtColor(v, cv.COLOR_GRAY2BGR)
        self._dst = cv.drawContours(color_v, contours, -1, (0, 0, 255), 1, lineType=cv.LINE_8)
        areas = []
        for c in contours:
            area = cv.contourArea(c)
            if self._minArea <= area:
                areas.append(area)
        return areas

    def initialize(self):
        self._template_dir = os.path.join(os.getcwd(), "dut_verification\\")
        if not os.path.exists(self._template_dir):
            os.makedirs(self._template_dir)
        mode = (os.stat(self._template_dir).st_mode | 0o555) & 0o777
        os.chmod(self._template_dir, mode)
        self._cap = cv.VideoCapture(self._station_config.DISP_CHECKER_CAMERA_INDEX)
        if self._cap is None:
            raise DutCheckerError('Unable to initialize camera checker.')

    def close(self):
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def do_checker(self):
        if self._cap is not None and self._cap.isOpened():
            # self._width, self._height = self._cap.get(3), self._cap.get(4)
            ret, frame = self._cap.read()
            if ret:
                ret, frame = self._cap.read() #read once more to ensure the image.
                if ret:
                    self._latest_image = cv.flip(frame, 3)
                    return self._blob_areas(self._latest_image)
            raise DutCheckerError('Fail to capture image from camera checker.')

    def save_log_img(self, name):
        if self._latest_image is not None:
            fn = os.path.join(self._template_dir, name)
            cv.imwrite(fn, self._latest_image)
        if self._dst is not  None:
            fn = os.path.join(self._template_dir, 'dst_'+name)
            cv.imwrite(fn, self._dst)

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
    station_config.DISP_CHECKER_CAMERA_INDEX = 1
    # station_config.load_station('pancake_uniformity')
    station_config.print_to_console = types.MethodType(print_to_console, station_config)

    the_unit = DutChecker(station_config)
    the_unit.initialize()

    for c in range(1, 100):
        print the_unit.do_checker()
        the_unit.save_log_img("x.bmp")
        pass

    the_unit.close()
