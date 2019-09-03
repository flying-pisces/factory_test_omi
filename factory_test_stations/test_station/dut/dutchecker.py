#!/usr/bin/env python
# -*- coding:utf-8 -*-

import cv2 as cv
import os
import numpy as np

class dut_checker:
    _cap = None
    _latest_image = None
    _template_dir = None
    _minArea = 6000

    def _blob_areas(self, image1):
        hsv = cv.cvtColor(image1, cv.COLOR_BGR2HSV)
        lower = np.array([127])
        upper = np.array([255])
        img = cv.inRange(hsv[:, :, 2], lower, upper)
        kernel = np.ones((11, 11), dtype=np.uint8)
        img = cv.erode(img, kernel, iterations=1)
        dst = cv.dilate(img, kernel, iterations=1)

        img, contours, hierarchy = cv.findContours(dst.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        cv.drawContours(dst, contours, -1, (0, 0, 255), 3)

        areas = []
        for c in contours:
            area = cv.contourArea(c)
            if self._minArea <= area:
                areas.append(area)
        return areas

    def open(self, cameraindex):
        self._template_dir = os.path.join(os.getcwd(), "dut_verification\\")
        if not os.path.exists(self._template_dir):
            os.makedirs(self._template_dir)
        mode = os.stat(self._template_dir.st_mode | 0o555) & 0o777
        os.chmod(self._template_dir, mode)
        self._cap = cv.VideoCapture(cameraindex)

    def close(self):
        if self._cap is not None:
            self._cap.release()

    def do_checker(self, x, y, w, h):
        if self._cap.isOpened():
            # self._width, self._height = self._cap.get(3), self._cap.get(4)
            ret, frame = self._cap.read()
            if ret:
                self._latest_image = cv.flip(frame, 3)
                return self._blob_areas(self._latest_image)

    def save_log_img(self, name):
        if self._latest_image is not None:
            fn = os.path.join(self._template_dir, name)
            cv.imwrite(fn)
