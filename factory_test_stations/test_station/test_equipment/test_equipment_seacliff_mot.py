# -*- coding:utf-8 -*-
import hardware_station_common.test_station.test_equipment
import json
import os
import shutil
import pprint
import re
import time
import glob

# MotAlgorithmHelper
import numpy as np
from skimage import measure
import cv2
import multiprocessing as mp
import hardware_station_common.utils.thread_utils as thread_utils
from skimage.measure import regionprops, label
import os
import scipy
# from scipy.interpolate import interp2d
import matplotlib.pyplot as plt
import matplotlib
import csv

try:
    from test_station.test_equipment.Conoscope import Conoscope
except:
    from Conoscope import Conoscope
finally:
    pass


class seacliffmotEquipmentError(Exception):
    pass

class seacliffmotEquipment(hardware_station_common.test_station.test_equipment.TestEquipment):
    """
        class for project station Equipment
            this is for doing all the specific things necessary to interface with equipment
    """
    def __init__(self, station_config, operator_interface):
        _dll_path = None
        hardware_station_common.test_station.test_equipment.TestEquipment.__init__(self, station_config, operator_interface)
        self.name = "eldim"
        self._verbose = station_config.IS_VERBOSE
        self._station_config = station_config
        Conoscope.DLL_PATH = self._station_config.CONOSCOPE_DLL_PATH
        Conoscope.VERSION_REVISION = self._station_config.VERSION_REVISION_EQUIPMENT
        self._device = Conoscope(self._station_config.EQUIPMENT_SIM, self._station_config.EQUIPMENT_WHEEL_SIM)
        self._error_message = self.name + "is out of work"
        self._version = None
        self._config = None
        self._open = None

    ## Eldim specific return.
    def _log(self, ret, functionName):
        if self._verbose:
            print("  {0}".format(functionName))
        try:
            # case of return value is a string
            # print("  -> {0}".format(ret))
            returnData = json.loads(ret)
        except:
            # case of return is already a dict
            returnData = ret
        return returnData
        # try:
        #     # display return data
        #     for key, value in returnData.items():
        #         print("      {0:<20}: {1}".format(key, value))
        # except:
        #     print("  invalid return value")

    ########### IDENTIFY SELF ###########

    def version(self):
        if self._version is None:
            ret = self._device.CmdGetVersion()
            self._version = self._log(ret, "CmdGetVersion")
            if self._verbose:
                self._operator_interface.print_to_console("Equipment Version is \n{0}\n".format(str(self._version)))
        return self._version

    def get_config(self):
        if self._config is None:
            ret = self._device.CmdGetConfig()
            self._config = self._log(ret, "CmdGetConfig")
            if self._verbose:
                self._operator_interface.print_to_console("Current Configuration is \n{0}\n".format(str(self._config)))
        return self._config

    def set_config(self, configsetting):
        ret = self._device.CmdSetConfig(configsetting)
        self._config = self._log(ret, "CmdSetConfig")
        if self._verbose:
            self._operator_interface.print_to_console("Current Configuration is \n{0}\n".format(str(self._config)))
        return self._config

    ########### Equipment Operation ###########
    def open(self):
        ret = self._device.CmdOpen()
        self._open = self._log(ret, "CmdOpen")
        if self._verbose:
           print("Open Status is \n{0}\n".format(str(self._open)))
        return self._open

    def reset(self):
        ret = self._device.CmdReset()
        if self._verbose:
           print("Open Status is \n{0}\n".format(str(self._log(ret, "CmdReset"))))
        return self._log(ret, "CmdReset")

    def close(self):
        ret = self._device.CmdClose()
        if self._verbose:
            self._operator_interface.print_to_console("Open Status is \n{0}\n".format(str(self._log(ret, "CmdClose"))))
        else:
            self._log(ret, "CmdClose")
        return self._log(ret, "CmdClose")

    def kill(self):
        self._device.QuitApplication()

    def is_ready(self):
        pass

    ########### Measure ###########
    def __check_ae_finish(self):
        # wait for the measurement is done
        bDone = False
        aeExpo = 0
        while bDone is not True:
            ret = self._device.CmdMeasureAEStatus()
            aeState = ret["state"]
            if aeExpo != ret["exposureTimeUs"]:
                aeExpo = ret["exposureTimeUs"]
                if self._verbose:
                    print("  state = {0} ({1} us)".format(aeState, aeExpo))
            if (aeState == Conoscope.MeasureAEState.MeasureAEState_Done) or \
                    (aeState == Conoscope.MeasureAEState.MeasureAEState_Error) or \
                    (aeState == Conoscope.MeasureAEState.MeasureAEState_Cancel):
                bDone = True
                if self._verbose:
                    print("  state = {0} ({1} us)".format(aeState, ret["exposureTimeUs"]))
            else:
                time.sleep(0.1)

    def __check_seq_finish(self):
        done = False
        processStateCurrent = None
        processStepCurrent = None
        self._operator_interface.print_to_console("wait for the sequence to be finished.\n")
        while done is False:
            ret = self._device.CmdCaptureSequenceStatus()
            processState = ret['state']
            processStep = ret['currentSteps']
            processNbSteps = ret['nbSteps']

            if (processStateCurrent is None) or (processStateCurrent != processState) or (
                    processStepCurrent != processStep):
                if self._verbose:
                    print("  step {0}/{1} state {2}".format(processStep, processNbSteps, processState))

                processStateCurrent = processState
                processStepCurrent = processStep

            if processState == Conoscope.CaptureSequenceState.CaptureSequenceState_Error:
                done = True
                if self._verbose:
                    print("Error happened")
            elif processState == Conoscope.CaptureSequenceState.CaptureSequenceState_Done:
                done = True
                if self._verbose:
                    print("Process Done")

            if done is False:
                time.sleep(0.05)

    def do_measure_and_export(self, pos_name, pattern_name):
        """
        @type pos_name: str
        @type pattern_name: str
        """
        pattern = [c for c in self._station_config.TEST_ITEM_PATTERNS if c['name'] == pattern_name][-1]  # type: dict
        setup_cfg = pattern.get('setup')  # type: dict
        exposure_cfg = pattern.get('exposure')  # type: (int, str)
        if setup_cfg is None:
            raise seacliffmotEquipmentError('Fail to set setup_config.')
        out_image_mode = 0
        if pattern.get('oi_mode'):
            out_image_mode = pattern.get('oi_mode')

        current_config = self._device.CmdGetConfig()
        capture_path = current_config['CapturePath']
        path_prefix = os.path.basename(capture_path).split('_')[0]
        filename_prepend = current_config['FileNamePrepend']

        file_names = []
        uut_dirs = [c for c in glob.glob(os.path.join(self._station_config.RAW_IMAGE_LOG_DIR, r'*'))
                   if os.path.isdir(c)
                   and os.path.relpath(c, self._station_config.RAW_IMAGE_LOG_DIR).startswith(path_prefix)]
        for uut_dir in uut_dirs:
            for home, dirs, files in os.walk(os.path.join(self._station_config.RAW_IMAGE_LOG_DIR, uut_dir)):
                for file_name in files:
                    if re.search(r'\.bin', file_name, re.I) and re.search(filename_prepend, file_name, re.I):
                        file_names.append(os.path.join(home, file_name))

        if isinstance(exposure_cfg, str) or isinstance(exposure_cfg, tuple):
            if self._station_config.SEQ_CAP_INIT_CONFIG['bUseExpoFile']:
                capture_seq_exposure = os.path.join(self._station_config.SEQUENCE_RELATIVEPATH, pattern_name + '.json')
                target_seq_name = os.path.join(self._station_config.CONOSCOPE_DLL_PATH, 'CaptureSequenceExposureTime.json')
                if not os.path.exists(capture_seq_exposure):
                    raise seacliffmotEquipmentError('Fail to Find config for {0}.'.format(capture_seq_exposure))
                shutil.copyfile(capture_seq_exposure, target_seq_name)

            json_file = os.path.join(self._station_config.CONOSCOPE_DLL_PATH, 'captureSequenceCaptures.json')
            if os.path.exists(json_file):
                os.remove(json_file)
            if self._station_config.EQUIPMENT_SIM:
                seq_filters = ['X', 'Xz', 'Ya', 'Yb', 'Z']
                proc_files = {}
                for f in seq_filters:
                    filter_name = 'Filter_{0}'.format(f)
                    proc_files[filter_name] = None
                    fns = [c for c in file_names if re.match('{0}.*_filt_{1}_.*_proc_.*'.format(filename_prepend, f),
                                                             os.path.basename(c), re.I)]
                    if len(fns) > 0:
                        proc_files[filter_name] = fns[-1]
                capture_sequence_captures = {'FilePath': proc_files}
                with open(json_file, 'w') as f:
                    json.dump(capture_sequence_captures, f, sort_keys=True, indent=4)
                self._operator_interface.print_to_console('update capture_sequence_captures.\n')
                msg = json.dumps(capture_sequence_captures, sort_keys=True, indent=4)
                self._operator_interface.print_to_console(msg)

            # assert the initialize status is correct.
            ret = self._device.CmdCaptureSequenceStatus()
            processState = ret['state']
            if not (processState == Conoscope.CaptureSequenceState.CaptureSequenceState_NotStarted or
                    processState == Conoscope.CaptureSequenceState.CaptureSequenceState_Done):
                raise seacliffmotEquipmentError('Fail to CmdMeasureSequence.{0}'.format(processState))

            captureSequenceConfig = self._station_config.SEQ_CAP_INIT_CONFIG.copy()
            captureSequenceConfig["eNd"] = setup_cfg[1]  # Conoscope.Nd.Nd_1.value,
            captureSequenceConfig["eIris"] = setup_cfg[2]  # Conoscope.Iris.aperture_4mm.value,
            captureSequenceConfig['eOuputImage'] = out_image_mode  # Conoscope.ComposeOuputImage

            if isinstance(exposure_cfg, tuple) and captureSequenceConfig['bAutoExposure']:
                captureSequenceConfig['exposureTimeUs_FilterX'] = exposure_cfg[0]
                captureSequenceConfig['exposureTimeUs_FilterXz'] = exposure_cfg[1]
                captureSequenceConfig['exposureTimeUs_FilterYa'] = exposure_cfg[2]
                captureSequenceConfig['exposureTimeUs_FilterYb'] = exposure_cfg[3]
                captureSequenceConfig['exposureTimeUs_FilterZ'] = exposure_cfg[4]
            ret = self._device.CmdCaptureSequence(captureSequenceConfig)
            if ret['Error'] != 0:
                seacliffmotEquipmentError('Fail to CmdCaptureSequence.')
            self.__check_seq_finish()
            del captureSequenceConfig
        elif isinstance(exposure_cfg, int):
            setupConfig = self._station_config.MEASURE_CAP_INIT_CONFIG.copy()

            setupConfig["eFilter"] = setup_cfg[0]  # self._device.Filter.Yb.value,
            setupConfig["eNd"] = setup_cfg[1]  # self._device.Nd.Nd_3.value,
            setupConfig["eIris"] = setup_cfg[2]  # self._device.Iris.aperture_2mm.value

            ret = self._device.CmdSetup(setupConfig)
            self._log(ret, "CmdSetup")
            if ret['Error'] != 0:
                seacliffmotEquipmentError('Fail to CmdSetup.')

            ret = self._device.CmdSetupStatus()
            self._log(ret, "CmdSetupStatus")
            if ret['Error'] != 0:
                raise seacliffmotEquipmentError('Fail to CmdSetupStatus.')

            # equipment_sim
            if self._station_config.EQUIPMENT_SIM:
                fns = [c for c in file_names if re.match('{0}.*_filt_.*_raw_.*'.format(filename_prepend),
                                                         os.path.basename(c), re.I)]
                if len(fns) > 0:
                    self._operator_interface.print_to_console('update capture dummy {0}.\n'.format(fns[-1]))
                    self._device.CmdSetDebugConfig({'dummyRawImagePath': fns[-1]})

            measureConfig = {"exposureTimeUs": exposure_cfg,
                             "nbAcquisition": 1}
            if not self._station_config.TEST_AUTO_EXPOSURE:
                ret = self._device.CmdMeasure(measureConfig)
                self._log(ret, "CmdMeasure")
                if ret['Error'] != 0:
                    raise seacliffmotEquipmentError('Fail to CmdMeasure.')
            else:
                #  measureAE
                ret = self._device.CmdMeasureAEStatus()
                aeState = ret['state']
                if not (aeState == Conoscope.MeasureAEState.MeasureAEState_NotStarted or
                        aeState == Conoscope.MeasureAEState.MeasureAEState_Done):
                    raise seacliffmotEquipmentError('Fail to CmdMeasureAE.{0}'.format(aeState))
                ret = self._device.CmdMeasureAE(measureConfig)
                self._log(ret, "CmdMeasureAEStatus")
                self.__check_ae_finish()
            # only export raw while not in emulated mode.
            if (not self._station_config.EQUIPMENT_SIM) and self._station_config.TEST_SEQ_SAVE_CAPTURE:
                ret = self._device.CmdExportRaw()
                self._log(ret, "CmdExportRaw")
                if ret['Error'] != 0:
                    raise seacliffmotEquipmentError('Fail to CmdExportRaw.')
            # export processed data.
            ret = self._device.CmdExportProcessed()
            self._log(ret, "CmdExportProcessed")
            if ret['Error'] != 0:
                raise seacliffmotEquipmentError('Fail to CmdExportProcessed.')

    def measure_and_export(self, measuretype):
        if measuretype == 0:
            self.__perform_capture()
        elif measuretype == 1:
            self._perform_capture_sequence()
        else:
            self._operator_interface.print_to_console("TestType Setting is Wrong \n{0}\n".format(self._error_message))
        return

    def __perform_capture(self):
        setupConfig = {"sensorTemperature": 25.0,
                       "eFilter": self._device.Filter.Yb.value,
                       "eNd": self._device.Nd.Nd_3.value,
                       "eIris": self._device.Iris.aperture_2mm.value}
        ret = self._device.CmdSetup(setupConfig)
        self._log(ret, "CmdSetup")

        ret = self._device.CmdSetupStatus()
        self._log(ret, "CmdSetupStatus")

        measureConfig = {"exposureTimeUs": 100000,
                         "nbAcquisition": 1}

        ret = self._device.CmdMeasure(measureConfig)
        self._log(ret, "CmdMeasure")

        ret = self._device.CmdExportRaw()
        self._log(ret, "CmdExportRaw")

        ret = self._device.CmdExportProcessed()
        self._log(ret, "CmdExportProcessed")

        # change capture path

        # config = {"capturePath": "./CaptureFolder2"}
        # ret = self._device.CmdSetConfig(config)
        # self._log(ret, "CmdSetup")
        #
        # setupConfig = {"sensorTemperature": 25.0,
        #                "eFilter": self._device.Filter.Xz.value,
        #                "eNd": self._device.Nd.Nd_1.value,
        #                "eIris": self._device.Iris.aperture_02.value}
        # ret = self._device.CmdSetup(setupConfig)
        # self._log(ret, "CmdSetup")
        #
        # ret = self._device.CmdSetupStatus()
        # self._log(ret, "CmdSetupStatus")
        #
        # measureConfig = {"exposureTimeUs": 90000,
        #                  "nbAcquisition": 1}
        #
        # ret = self._device.CmdMeasure(measureConfig)
        # self._log(ret, "CmdMeasure")
        #
        # ret = self._device.CmdExportRaw()
        # self._log(ret, "CmdExportRaw")
        #
        # ret = self._device.CmdExportProcessed()
        # self._log(ret, "CmdExportProcessed")
        # return

    def __perform_capture_sequence(self):
        # check capture sequence
        ret = self._device.CmdGetCaptureSequence()
        self._log(ret, "CmdGetCaptureSequence")

        captureSequenceConfig = {"sensorTemperature": 24.0,
                                 "bWaitForSensorTemperature": False,
                                 "eNd": Conoscope.Nd.Nd_1.value,
                                 "eIris": Conoscope.Iris.aperture_4mm.value,
                                 "exposureTimeUs": 12000,
                                 "nbAcquisition": 1,
                                 "bAutoExposure": False,
                                 "bUseExpoFile": False}

        ret = self._device.CmdCaptureSequence(captureSequenceConfig)
        self._log(ret, "CmdCaptureSequence")

        # wait for the end of the processing
        done = False

        processStateCurrent = None
        processStepCurrent = None

        self._operator_interface.print_to_console("wait for the sequence to be finished.\n")

        while done is False:
            ret = self._device.CmdCaptureSequenceStatus()
            # LogFunction(ret, "CmdCaptureSequenceStatus")

            processState = ret['state']
            processStep = ret['currentSteps']
            processNbSteps = ret['nbSteps']

            if (processStateCurrent is None) or (processStateCurrent != processState) or (
                    processStepCurrent != processStep):
                if self._verbose:
                    print("  step {0}/{1} state {2}".format(processStep, processNbSteps, processState))

                processStateCurrent = processState
                processStepCurrent = processStep

            if processState == Conoscope.CaptureSequenceState.CaptureSequenceState_Error:
                done = True
                if self._verbose:
                    print("Error happened")
            elif processState == Conoscope.CaptureSequenceState.CaptureSequenceState_Done:
                done = True
                if self._verbose:
                    print("Process Done")

            if done is False:
                time.sleep(1)
            return

    ########### Export ###########
    def initialize(self):
        self.get_config()
        self._operator_interface.print_to_console("Initializing Seacliff MOT Equipment \n")


class MotAlgorithmHelper(object):
    _kernel_width = 25  # Width of square smoothing kernel in pixels.
    _kernel_shape = 'square'  # Use 'circle' or 'square' to change the smoothing kernel shape
    _kernel = np.ones((_kernel_width, _kernel_width))
    kernel_b = np.sum(_kernel)
    _kernel = _kernel / kernel_b  # normalize

    def __init__(self, coeff, is_verbose=False, save_plots=True):
        self._verbose = is_verbose
        self._save_plots = save_plots
        self._cam_fov = 60
        self._row = 6001
        self._col = 6001
        self._exp_dir = 'exp'
        self._ColorMatrix_ = np.array(coeff)

        np.seterr(invalid='ignore', divide='ignore')

    @classmethod
    def get_export_data(cls, filename, station_config=None):
        """
        @type: filename: str
        """
        split_text = os.path.splitext(os.path.basename(filename))[0].split('_')
        file_size_def = {
            'raw': (6004, 7920, np.uint16),
            'proc': (6001, 6001, np.int16),
            'float': (6001, 6001, np.float32),
        }
        if 'raw' in split_text:
            row, col, dtype = file_size_def['raw']
        elif 'proc' in split_text:
            row, col, dtype = file_size_def['proc']
        elif 'float' in split_text:
            row, col, dtype = file_size_def['float']
        if (station_config is not None) and station_config.CAM_INIT_CONFIG['bUseRoi']:
            row = station_config.CAM_INIT_CONFIG['RoiYBottom'] - station_config.CAM_INIT_CONFIG['RoiYTop']
            col = station_config.CAM_INIT_CONFIG['RoiXRight'] - station_config.CAM_INIT_CONFIG['RoiXLeft']
        if not dtype:
            raise seacliffmotEquipmentError('unsupported bin file. {0}'.format(filename))
        with open(filename, 'rb') as f:
            frame3 = np.frombuffer(f.read(), dtype=dtype)
            image_in = frame3.reshape(col, row).T
            image_in = cv2.rotate(image_in, 0)
        return image_in

    def distortion_centroid_parametric_export(self, filename=r'/normal_GreenDistortion_X_float.bin', module_temp=30):
        ModuleTemp = module_temp
        mask_fov = 30
        x_autocollimator = 0
        y_autocollimator = 0
        dirr = os.path.dirname(filename)
        fnamebase = os.path.basename(filename).lower().split('_x_float.bin')[0]
        x_angle_arr = np.linspace(-1 * self._cam_fov, self._cam_fov, self._col).reshape(-1, self._col)
        y_angle_arr = np.linspace(-1 * self._cam_fov, self._cam_fov, self._row).reshape(-1, self._col)
        #
        image_in = None
        with open(filename, 'rb') as f:
            frame3 = np.frombuffer(f.read(), dtype=np.float32)
            image_in = frame3.reshape(self._col, self._row).T
            image_in = np.rot90(image_in, 3)
        if self._verbose:
            print(f'Read bin files named {os.path.basename(filename)}\n')

        XYZ = image_in
        CXYZ = image_in
        del image_in
        angle_arr = np.linspace(0, 2 * np.pi, 361)

        disp_fov = self._cam_fov

        disp_fov_ring_x = disp_fov * np.sin(angle_arr)
        disp_fov_ring_y = disp_fov * np.cos(angle_arr)

        col_deg_arr = np.tile(x_angle_arr, (self._row, 1))
        row_deg_arr = np.tile(y_angle_arr.T, (1, self._col))

        radius_deg_arr = (col_deg_arr ** 2 + row_deg_arr ** 2) ** (1 / 2)
        mask = np.ones((self._row, self._col))
        # mask[np.where(radius_deg_arr > disp_fov)] = 0
        mask[np.where(radius_deg_arr > mask_fov)] = 0

        masked_tristim = XYZ * mask
        max_XYZ_val = np.max(masked_tristim)
        del radius_deg_arr, mask

        Lumiance_thresh = 10
        axis_length_thresh = 10
        if self._verbose:
            print(XYZ.shape, np.max(XYZ))

        # label_image = np.uint8(np.where(XYZ > Lumiance_thresh,255,0))
        # XYZ = cv2.blur(XYZ,(3,3))
        label_image = cv2.inRange(masked_tristim, 10, 255) // 255
        del masked_tristim

        aa_image = np.zeros((self._row + 1, self._col + 1), dtype=np.int)
        aa_image[1:, 1:] = label_image
        label_image = aa_image

        bb_image = np.zeros((self._row + 1, self._col + 1), dtype=np.float32)
        bb_image[1:, 1:] = CXYZ
        CXYZ = bb_image

        del aa_image, bb_image

        label_image = label(label_image, connectivity=2)
        stats = regionprops(label_image)
        del label_image
        if self._verbose:
            print('stas', stats[0]['Centroid'])
        scenters = []
        sMajorAxisLength = []
        sMinorAxisLength = []
        if self._verbose:
            print('stats num:', len(stats))

        # for i, stat in enumerate(stats):
        #     if stat['MajorAxisLength'] >= axis_length_thresh:
        #         scenters.append(list(stat['Centroid']))
        #         sMajorAxisLength.append(stat['MajorAxisLength'])
        #         sMinorAxisLength.append(stat['MinorAxisLength'])
        for stat in [c for c in stats if c['MajorAxisLength'] >= axis_length_thresh]:
            scenters.append(list(stat['Centroid']))
            sMajorAxisLength.append(stat['MajorAxisLength'])
            sMinorAxisLength.append(stat['MinorAxisLength'])
        if self._verbose:
            print('num stats {0} / {1}'.format(len(scenters), len(stats)))
        num_dots = len(scenters)
        bb = np.nonzero(np.array(sMinorAxisLength) > 50)
        if self._verbose:
            print('sMinorAxisLength,max', np.max(sMinorAxisLength))
            print('majorlenght:', np.max(sMajorAxisLength))

        centroid = np.zeros((num_dots, 2))
        for i in range(0, num_dots):
            mlen = sMajorAxisLength[i]
            d = np.floor(sMajorAxisLength[i] / 2) + 1

            scenter = scenters[i]
            scentery = scenters[i][1]
            scentera = int(np.floor(scenters[i][1] - d))
            scenterb = int(np.floor(scenters[i][1] + d))
            scenterc = int(np.floor(scenters[i][0] - d))
            scenterd = int(np.floor(scenters[i][0] + d))
            im = CXYZ[scenterc:scenterd + 1, scentera:scenterb + 1]
            [rows, cols] = im.shape
            x = np.ones((rows, 1)) * np.arange(1, cols + 1)  # # Matrix with each pixel set to its x coordinate
            y = np.arange(1, rows + 1).reshape(rows, -1) * np.ones(
                (1, cols))  # #   "     "     "    "    "  "   "  y    "
            area = np.sum(im)

            # hhhhh = np.float32(im)
            # print('i = {0}, col = {1}   row = {2}, area = {3}'.format(i, rows, cols, area))

            hx = np.sum(np.float32(im) * x)
            hy = np.sum(np.float32(im) * y)

            meanx = np.sum(np.float32(im) * x) / area - d - 1
            meany = np.sum(np.float32(im) * y) / area - d - 1
            centroid[i, 1] = int(scenters[i][0]) + meany
            centroid[i, 0] = meanx + int(scenters[i][1])
            del im

        image_center = centroid[bb, :].reshape(2, )
        # centroid = np.array(sorted(centroid, key=lambda xx: xx[0]))

        temp1 = centroid[:, 0]
        temp2 = image_center[0]
        y_points = np.nonzero(np.abs(centroid[:, 0] - image_center[0]) < 50)
        x_points = np.nonzero(np.abs(centroid[:, 1] - image_center[1]) < 50)

        x1 = centroid[x_points, 0].reshape(-1)
        y1 = centroid[x_points, 1].reshape(-1)

        c1 = self.polyfit_ex(x1, y1, 1)
        k1 = np.degrees(np.arctan(c1[0]))

        x2 = centroid[y_points, 0].reshape(-1)
        y2 = centroid[y_points, 1].reshape(-1)

        c2 = self.polyfit_ex(x2, y2, 1)
        k2 = np.degrees(np.arctan(c2[0]))

        x_deg = x_autocollimator
        y_deg = y_autocollimator
        # col_ind and row_ind are the x and y pixel value of the cross-pattern
        # from autocollimator in Eldim conoscope. After autocollimator alignment,
        # these value should be the center pixel of the image, which should be
        # (3001,3001) in Matlab, and (3000,3000) in Python
        col_ind = np.nonzero(np.abs(x_angle_arr - x_deg) == np.min(np.abs(x_angle_arr - x_deg)))[1][0]
        row_ind = np.nonzero(np.abs(y_angle_arr - y_deg) == np.min(np.abs(y_angle_arr - y_deg)))[1][0]
        del x_angle_arr, y_angle_arr, x_points, y_points,
        display_center = [None, None]
        display_center[0] = 0.4563 * (image_center[0] - (col_ind + 1))
        display_center[1] = 0.4563 * (image_center[1] - (row_ind + 1))

        k = 0
        stats_summary = np.empty((2, 100), dtype=object)
        # stats_summary = cell(2,1)
        stats_summary[0, k] = 'dir'
        stats_summary[1, k] = os.path.join(dirr, fnamebase)
        # k = k + 1
        # stats_summary[0, k] = 'Max Lum'
        # stats_summary[1, k] = max_XYZ_val
        # k = k + 1
        # stats_summary[0, k] = 'Number Of Dots'
        # stats_summary[1, k] = num_dots
        k = k + 1
        stats_summary[0, k] = 'Module Temperature'
        stats_summary[1, k] = ModuleTemp
        k = k + 1
        stats_summary[0, k] = 'DispCen_x_cono'
        stats_summary[1, k] = image_center[0]
        k = k + 1
        stats_summary[0, k] = 'DispCen_y_cono'
        stats_summary[1, k] = image_center[1]
        k = k + 1
        stats_summary[0, k] = 'DispCen_x_display'
        stats_summary[1, k] = display_center[0]
        k = k + 1
        stats_summary[0, k] = 'DispCen_y_display'
        stats_summary[1, k] = display_center[1]
        k = k + 1
        stats_summary[0, k] = 'Disp_Rotate_x'
        stats_summary[1, k] = k1
        k = k + 1
        stats_summary[0, k] = 'Disp_Rotate_y'
        stats_summary[1, k] = k2
        k = k + 1

        del XYZ, CXYZ, col_deg_arr, row_deg_arr
        del stats, bb, centroid, image_center
        del scenters, sMajorAxisLength, sMinorAxisLength
        return dict(np.transpose(stats_summary[:, 0:k]))

    @staticmethod
    def read_image_raw(bin_filename):
        I = None
        with open(bin_filename, 'rb') as fin:
            I = np.frombuffer(fin.read(), dtype=np.float32)
        image_in = np.reshape(I, (6001, 6001))
        # Z = Z'        #Removed for viewing to match DUT orientation
        del I
        return image_in

    def color_pattern_parametric_export_RGB(self, primary='r', module_temp=30, xfilename=r'R255_X_float.bin'):
        # ----- Adjustable Parameters for Output -----#
        # startdirr = 'C:\Users\xiaobotian\Desktop\FMOT\MOT data\20200704 MOT data\C3-LH0007_SEACLIFF_MOT-01_20200703-235556\19043959\20200703_235715_nd_0_iris_5_X_float.bin'
        ModuleTemp = module_temp
        TargetTemp = 47
        dLum_R = -0.02253
        dColor_x_R = 0.000121
        dColor_y_R = -0.00047
        dLum_G = -0.01266
        dColor_x_G = 0.000733
        dColor_y_G = -0.00103
        dLum_B = -0.01019
        dColor_x_B = -0.000012
        dColor_y_B = -0.00016

        coeff = {
            'r': (dLum_R, dColor_x_R, dColor_y_R),
            'g': (dLum_G, dColor_x_G, dColor_y_G),
            'b': (dLum_B, dColor_x_B, dColor_y_B),
        }

        dLum, dColor_x, dColor_y = coeff[primary]
        # # Color offsite is used for MOT correlation
        Color_x_offsite = 0
        Color_y_offsite = 0
        # # Data processin setting

        noise_thresh = 0.05  # Percent of Y sum to exclude from color plots (use due to color calc noise in dim part of image)
        color_thresh = 0.01  # Thresh for color uniformity
        lum_thresh = 0.7  # Thresh for brightness uniformity v3.0
        fixed_chroma_clims = 0  # If 1, then chroma plots range [0 1].  Otherwise auto scale
        disp_fov = 60  # Maximum FOV to display.  Use for masking.
        chromaticity_fov = 30  # Limit FOV for chromaticity plot in degrees v3.0
        disp_ring_spacing = 10  # Spacing, in deg, of rings overlaid on plots
        kernel_width = 25  # Width of square smoothing kernel in pixels.
        kernel_shape = 'square'  # Use 'circle' or 'square' to change the smoothing kernel shape

        # ----- Begin code -----#
        cam_fov = 60
        row = 6001
        col = 6001
        pixel_spacing = 0.02  # Degrees per pixel

        dirr = os.path.dirname(xfilename)
        fnamebase = os.path.basename(xfilename).lower().split('_x_float.bin')[0]
        filename = ['{0}_{1}_float.bin'.format(fnamebase, c) for c in ['X', 'Y', 'Z']]
        primary = ['X', 'Y', 'Z']

        x_angle_arr = np.linspace(-1 * cam_fov, cam_fov, col).reshape(-1, col)
        y_angle_arr = np.linspace(-1 * cam_fov, cam_fov, row).reshape(-1, row)

        kernel = np.ones((kernel_width, kernel_width))
        kernel_b = np.sum(kernel)
        kernel = kernel / kernel_b  # normalize
        XYZ = []
        for f_name in filename:
            with open(os.path.join(dirr, f_name), 'rb') as fin:
                I = np.frombuffer(fin.read(), dtype=np.float32)
            image_in = np.reshape(I, (col, row)).T
            image_in = np.rot90(image_in, 3)
            image_in = np.flip(image_in, 0)

            image_in = cv2.filter2D(image_in, -1, kernel, borderType=cv2.BORDER_CONSTANT)
            XYZ.append(image_in)
            del image_in, I

        XYZ = np.stack(XYZ, axis=2)
        XYZ_1D = np.reshape(XYZ, (self._row * self._col, 3))
        XYZ_1D_ColorCorrected = self._ColorMatrix_.dot(XYZ_1D.T)
        XYZ = np.reshape(XYZ_1D_ColorCorrected.T, (self._row, self._col, 3))
        del XYZ_1D, XYZ_1D_ColorCorrected,
        ## Save parametric data
        # Create viewing masks
        col_deg_arr = np.tile(x_angle_arr, (row, 1))
        row_deg_arr = np.tile(y_angle_arr.T, (1, col))
        radius_deg_arr = (col_deg_arr ** 2 + row_deg_arr ** 2) ** (1 / 2)
        mask = np.ones((row, col))
        mask[radius_deg_arr > disp_fov] = 0
        chromaticity_mask = np.ones((row, col))
        chromaticity_mask[radius_deg_arr > chromaticity_fov] = 0

        cam_fov_mask = np.ones((row, col))
        cam_fov_mask[radius_deg_arr > cam_fov] = 0
        del radius_deg_arr, chromaticity_mask, cam_fov_mask

        # Perform CIE and RGB color calculations and mask to disp_fov
        # y are ued for absolute color value, color u' and v' are used for
        # calculate color uniformity
        x_smoothed = mask * (XYZ[:, :, 0]) / (XYZ[:, :, 0] + XYZ[:, :, 1] + XYZ[:, :, 2])
        x_smoothed[np.isnan(x_smoothed)] = 0
        x_smoothed = x_smoothed + Color_x_offsite
        y_smoothed = mask * (XYZ[:, :, 1]) / (XYZ[:, :, 0] + XYZ[:, :, 1] + XYZ[:, :, 2])
        y_smoothed[np.isnan(y_smoothed)] = 0
        y_smoothed = y_smoothed + Color_y_offsite

        tmp_XYZ = mask * XYZ[:, :, 1]
        XYZ_mask = np.zeros((row, col))
        XYZ_mask[tmp_XYZ > noise_thresh * np.max(tmp_XYZ)] = 1

        x_smoothed_masked = x_smoothed * XYZ_mask
        y_smoothed_masked = y_smoothed * XYZ_mask
        x_smoothed_masked_TargetTemp = x_smoothed_masked + (TargetTemp - ModuleTemp) * dColor_x
        y_smoothed_masked_TargetTemp = y_smoothed_masked + (TargetTemp - ModuleTemp) * dColor_y

        # np.nonzero max value location for brightness
        Lum_masked = mask * XYZ[:, :, 1]
        Lum_masked_TargetTemp = Lum_masked * (1 + (TargetTemp - ModuleTemp) * dLum)
        max_Y_val = np.max(Lum_masked[:])
        [rowsOfMaxes, colsOfMaxes] = np.nonzero(np.array(Lum_masked) == np.array(max_Y_val))

        max_Y_xloc_deg = x_angle_arr[0, colsOfMaxes]
        max_Y_yloc_deg = y_angle_arr[0, rowsOfMaxes]
        max_Y_xloc_pix = colsOfMaxes
        max_Y_yloc_pix = rowsOfMaxes

        # Output Statistics
        # dirr='chenyuyi'
        del mask, x_smoothed, y_smoothed, tmp_XYZ, XYZ_mask, XYZ, col_deg_arr, row_deg_arr
        k = 0

        x_deg = 0
        y_deg = 0
        col_ind_onaxis = np.nonzero(np.abs(x_angle_arr - x_deg) == np.min(np.abs(x_angle_arr - x_deg)))[1][0]
        row_ind_onaxis = np.nonzero(np.abs(y_angle_arr - y_deg) == np.min(np.abs(y_angle_arr - y_deg)))[1][0]
        # On-axis and off-axis brightness and color values
        x_deg = 0
        y_deg = 0
        col_ind = np.nonzero(np.abs(x_angle_arr - x_deg) == np.min(np.abs(x_angle_arr - x_deg)))[1][0]
        row_ind = np.nonzero(np.abs(y_angle_arr - y_deg) == np.min(np.abs(y_angle_arr - y_deg)))[1][0]
        stats_summary = np.empty((2, 100), np.object)
        stats_summary[0, k] = 'dir'
        stats_summary[1, k] = os.path.join(dirr, fnamebase)
        k = k + 1
        stats_summary[0, k] = 'Module Temperature'
        stats_summary[1, k] = ModuleTemp
        k = k + 1
        stats_summary[0, k] = 'OnAxis Lum'
        stats_summary[1, k] = Lum_masked[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = 'OnAxis x'
        stats_summary[1, k] = x_smoothed_masked[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = 'OnAxis y'
        stats_summary[1, k] = y_smoothed_masked[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = 'OnAxis Lum at 47C'
        stats_summary[1, k] = Lum_masked_TargetTemp[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = 'OnAxis x at 47C'
        stats_summary[1, k] = x_smoothed_masked_TargetTemp[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = 'OnAxis y at 47C'
        stats_summary[1, k] = y_smoothed_masked_TargetTemp[row_ind, col_ind]
        k += 1
        del Lum_masked, Lum_masked_TargetTemp,
        del colsOfMaxes, rowsOfMaxes, y_angle_arr, x_angle_arr
        del x_smoothed_masked, x_smoothed_masked_TargetTemp, y_smoothed_masked_TargetTemp, y_smoothed_masked
        return dict(np.transpose(stats_summary[:, 0:k]))

    def color_pattern_parametric_export_W255(self, ModuleLR='L', module_temp=30, xfilename=r'W255_X_float.bin'):
        # TargetTemp is the target temperature, and dLum, dColor is the
        # luminance and color drift per degree
        ModuleTemp = module_temp
        TargetTemp = 47
        dLum = -0.01135
        dColor_x = -0.00051
        dColor_y = -0.00058
        # Color offsite is used for MOT correlation
        Color_x_offsite = 0
        Color_y_offsite = 0
        chromaticity_fov = 30

        lum_thresh = 0.7
        noise_thresh = 0.05
        disp_fov = 60

        dirr = os.path.dirname(xfilename)
        fnamebase = os.path.basename(xfilename).lower().split('_x_float.bin')[0]
        filename = ['{0}_{1}_float.bin'.format(fnamebase, c) for c in ['X', 'Y', 'Z']]

        x_angle_arr = np.linspace(-1 * self._cam_fov, self._cam_fov, self._col).reshape(-1, self._col)
        y_angle_arr = np.linspace(-1 * self._cam_fov, self._cam_fov, self._row).reshape(-1, self._row)

        file_names = [os.path.join(dirr, c) for c in filename]
        XYZ_t = [MotAlgorithmHelper.read_image_raw(c) for c in file_names]
        if self._verbose:
            print(f'Read bin files named {fnamebase}\n')
        XYZ = []
        for c in XYZ_t:
            image_in = np.rot90(c.T, 3)
            image_in = np.flip(image_in, 0)
            image_in = cv2.filter2D(image_in, -1, MotAlgorithmHelper._kernel, borderType=cv2.BORDER_CONSTANT)
            XYZ.append(image_in)
            del image_in
        del XYZ_t
        XYZ = np.stack(XYZ, axis=2)

        XYZ_1D = np.reshape(XYZ, (self._row * self._col, 3))
        XYZ_1D_ColorCorrected = self._ColorMatrix_.dot(XYZ_1D.T)
        XYZ = np.reshape(XYZ_1D_ColorCorrected.T, (self._row, self._col, 3))
        del XYZ_1D, XYZ_1D_ColorCorrected

        ## Save parametric data
        # Create viewing masks
        col_deg_arr = np.tile(x_angle_arr, (self._row, 1))
        row_deg_arr = np.tile(y_angle_arr.T, (1, self._col))
        radius_deg_arr = (col_deg_arr ** 2 + row_deg_arr ** 2) ** (1 / 2)
        mask = np.ones((self._row, self._col))
        mask[radius_deg_arr > disp_fov] = 0
        chromaticity_mask = np.ones((self._row, self._col))  # 3 field mask defined by chromaticity_fov

        chromaticity_mask[radius_deg_arr > chromaticity_fov] = 0
        cam_fov_mask = np.ones((self._row, self._col))
        cam_fov_mask[radius_deg_arr > self._cam_fov] = 0
        del col_deg_arr, row_deg_arr, radius_deg_arr

        # Perform CIE and RGB color calculations and mask to disp_fov
        # y are ued for absolute color value, color u' and v' are used for
        # calculate color uniformity
        x_smoothed = mask * (XYZ[:, :, 0]) / (XYZ[:, :, 0] + XYZ[:, :, 1] + XYZ[:, :, 2])
        x_smoothed[np.isnan(x_smoothed)] = 0
        x_smoothed = x_smoothed + Color_x_offsite
        y_smoothed = mask * (XYZ[:, :, 1]) / (XYZ[:, :, 0] + XYZ[:, :, 1] + XYZ[:, :, 2])
        y_smoothed[np.isnan(y_smoothed)] = 0
        y_smoothed = y_smoothed + Color_y_offsite

        # Perform CIE and RGB color calculations and mask to disp_fov
        u_prime_smoothed = mask * (4 * XYZ[:, :, 0]) / (XYZ[:, :, 0] + 15 * XYZ[:, :, 1] + 3 * XYZ[:, :, 2])
        u_prime_smoothed[np.isnan(u_prime_smoothed)] = 0
        v_prime_smoothed = mask * (9 * XYZ[:, :, 1]) / (XYZ[:, :, 0] + 15 * XYZ[:, :, 1] + 3 * XYZ[:, :, 2])
        v_prime_smoothed[np.isnan(v_prime_smoothed)] = 0

        tmp_XYZ = XYZ[:, :, 1] * mask
        XYZ_mask = np.zeros((self._row, self._col))
        XYZ_mask[tmp_XYZ > noise_thresh * np.max(tmp_XYZ)] = 1

        x_smoothed_masked = x_smoothed * XYZ_mask
        y_smoothed_masked = y_smoothed * XYZ_mask
        u_prime_smoothed_masked = u_prime_smoothed * XYZ_mask
        v_prime_smoothed_masked = v_prime_smoothed * XYZ_mask
        x_smoothed_masked_TargetTemp = x_smoothed_masked + (TargetTemp - ModuleTemp) * dColor_x
        y_smoothed_masked_TargetTemp = y_smoothed_masked + (TargetTemp - ModuleTemp) * dColor_y

        # Find max value location for brightness
        Lum_masked = mask * XYZ[:, :, 1]
        Lum_masked_TargetTemp = Lum_masked * (1 + (TargetTemp - ModuleTemp) * dLum)
        max_Y_val = np.max(Lum_masked)
        [rowsOfMaxes, colsOfMaxes] = np.nonzero(Lum_masked == max_Y_val)
        rowsOfMaxes = rowsOfMaxes[0]
        colsOfMaxes = colsOfMaxes[0]
        max_Y_xloc_deg = x_angle_arr[0, colsOfMaxes]
        max_Y_yloc_deg = y_angle_arr[0, rowsOfMaxes]
        max_Y_xloc_pix = colsOfMaxes
        max_Y_yloc_pix = rowsOfMaxes
        del x_smoothed, y_smoothed, u_prime_smoothed, v_prime_smoothed, mask

        # Output Statistics
        k = 0
        x_deg = 0
        y_deg = 0
        col_ind_onaxis = np.nonzero(np.abs(x_angle_arr - x_deg) == np.min(np.abs(x_angle_arr - x_deg)))[1][0]
        row_ind_onaxis = np.nonzero(np.abs(y_angle_arr - y_deg) == np.min(np.abs(y_angle_arr - y_deg)))[1][0]

        stats_summary = np.empty((2, 100), dtype=object)
        stats_summary[0, k] = 'dir'
        stats_summary[1, k] = os.path.join(dirr, fnamebase)
        k = k + 1
        stats_summary[0, k] = 'Module Temperature'
        stats_summary[1, k] = ModuleTemp
        k = k + 1

        x_deg = 0
        y_deg = 0
        col_ind = np.nonzero(np.abs(x_angle_arr - x_deg) == np.min(np.abs(x_angle_arr - x_deg)))[1][0]
        row_ind = np.nonzero(np.abs(y_angle_arr - y_deg) == np.min(np.abs(y_angle_arr - y_deg)))[1][0]
        stats_summary[0, k] = 'OnAxis Lum'
        stats_summary[1, k] = Lum_masked[row_ind][col_ind]
        k = k + 1
        stats_summary[0, k] = 'OnAxis x'
        stats_summary[1, k] = x_smoothed_masked[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = 'OnAxis y'
        stats_summary[1, k] = y_smoothed_masked[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = 'OnAxis Lum at 47C'
        stats_summary[1, k] = Lum_masked_TargetTemp[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = 'OnAxis x at 47C'
        stats_summary[1, k] = x_smoothed_masked_TargetTemp[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = 'OnAxis y at 47C'
        stats_summary[1, k] = y_smoothed_masked_TargetTemp[row_ind, col_ind]
        k = k + 1

        # sky luminance and color
        x_deg = 0
        y_deg = -chromaticity_fov
        col_ind = np.nonzero(abs(x_angle_arr - x_deg) == np.min(min(abs(x_angle_arr - x_deg))))[1][0]
        row_ind = np.nonzero(abs(y_angle_arr - y_deg) == np.min(min(abs(y_angle_arr - y_deg))))[1][0]
        stats_summary[0, k] = f'Sky Lum({chromaticity_fov}deg)'
        stats_summary[1, k] = Lum_masked[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = f'Sky x({chromaticity_fov}deg)'
        stats_summary[1, k] = x_smoothed_masked[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = f'Sky y({chromaticity_fov}deg)'
        stats_summary[1, k] = y_smoothed_masked[row_ind, col_ind]
        k = k + 1
        # % Ground luminance and color
        x_deg = 0
        y_deg = chromaticity_fov
        col_ind = np.nonzero(abs(x_angle_arr - x_deg) == np.min(min(abs(x_angle_arr - x_deg))))[1][0]
        row_ind = np.nonzero(abs(y_angle_arr - y_deg) == np.min(min(abs(y_angle_arr - y_deg))))[1][0]
        stats_summary[0, k] = f'Ground Lum({chromaticity_fov}deg)'
        stats_summary[1, k] = Lum_masked[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = f'Ground x({chromaticity_fov}deg)'
        stats_summary[1, k] = x_smoothed_masked[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = f'Ground y({chromaticity_fov}deg)'
        stats_summary[1, k] = y_smoothed_masked[row_ind, col_ind]
        k = k + 1
        # % Nasal luminance and color
        if ModuleLR == 'L':
            x_deg = chromaticity_fov
            y_deg = 0
        else:
            x_deg = -chromaticity_fov
            y_deg = 0

        col_ind = np.nonzero(abs(x_angle_arr - x_deg) == np.min(min(abs(x_angle_arr - x_deg))))[1][0]
        row_ind = np.nonzero(abs(y_angle_arr - y_deg) == np.min(min(abs(y_angle_arr - y_deg))))[1][0]
        stats_summary[0, k] = f'Nasal Lum({chromaticity_fov}deg)'
        stats_summary[1, k] = Lum_masked[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = f'Nasal x({chromaticity_fov}deg)'
        stats_summary[1, k] = x_smoothed_masked[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = f'Nasal y({chromaticity_fov}deg)'
        stats_summary[1, k] = y_smoothed_masked[row_ind, col_ind]
        k = k + 1
        # % Temporal luminance and color
        if ModuleLR == 'L':
            x_deg = -chromaticity_fov
            y_deg = 0
        else:
            x_deg = chromaticity_fov
            y_deg = 0

        col_ind = np.nonzero(abs(x_angle_arr - x_deg) == np.min(min(abs(x_angle_arr - x_deg))))[1][0]
        row_ind = np.nonzero(abs(y_angle_arr - y_deg) == np.min(min(abs(y_angle_arr - y_deg))))[1][0]
        stats_summary[0, k] = f'Temporal Lum({chromaticity_fov}deg)'
        stats_summary[1, k] = Lum_masked[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = f'Temporal x({chromaticity_fov}deg)'
        stats_summary[1, k] = x_smoothed_masked[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = f'Temporal y({chromaticity_fov}deg)'
        stats_summary[1, k] = y_smoothed_masked[row_ind, col_ind]
        k = k + 1

        # Sky Nasal luminance and color
        if ModuleLR == 'L':
            x_deg = chromaticity_fov * 1.414 / 2
            y_deg = -chromaticity_fov * 1.414 / 2
        else:
            x_deg = -chromaticity_fov * 1.414 / 2
            y_deg = -chromaticity_fov * 1.414 / 2

        col_ind = np.nonzero(abs(x_angle_arr - x_deg) == np.min(min(abs(x_angle_arr - x_deg))))[1][-1]
        row_ind = np.nonzero(abs(y_angle_arr - y_deg) == np.min(min(abs(y_angle_arr - y_deg))))[1][-1]
        stats_summary[0, k] = f'Sky_Nasal Lum({chromaticity_fov}deg)'
        stats_summary[1, k] = Lum_masked[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = f'Sky_Nasal x({chromaticity_fov}deg)'
        stats_summary[1, k] = x_smoothed_masked[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = f'Sky_Nasal y({chromaticity_fov}deg)'
        stats_summary[1, k] = y_smoothed_masked[row_ind, col_ind]
        k = k + 1
        # Sky Temporal luminance and color
        if ModuleLR == 'L':
            x_deg = -chromaticity_fov * 1.414 / 2
            y_deg = -chromaticity_fov * 1.414 / 2
        else:
            x_deg = chromaticity_fov * 1.414 / 2
            y_deg = -chromaticity_fov * 1.414 / 2
        col_ind = np.nonzero(abs(x_angle_arr - x_deg) == np.min(min(abs(x_angle_arr - x_deg))))[1][-1]
        row_ind = np.nonzero(abs(y_angle_arr - y_deg) == np.min(min(abs(y_angle_arr - y_deg))))[1][-1]
        stats_summary[0, k] = f'Sky_Temporal Lum({chromaticity_fov}deg)'
        stats_summary[1, k] = Lum_masked[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = f'Sky_Temporal x({chromaticity_fov}deg)'
        stats_summary[1, k] = x_smoothed_masked[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = f'Sky_Temporal y({chromaticity_fov}deg)'
        stats_summary[1, k] = y_smoothed_masked[row_ind, col_ind]
        k = k + 1
        # Ground Nasal luminance and color
        if ModuleLR == 'L':
            x_deg = chromaticity_fov * 1.414 / 2
            y_deg = chromaticity_fov * 1.414 / 2
        else:
            x_deg = -chromaticity_fov * 1.414 / 2
            y_deg = chromaticity_fov * 1.414 / 2
        col_ind = np.nonzero(abs(x_angle_arr - x_deg) == np.min(min(abs(x_angle_arr - x_deg))))[1][-1]
        row_ind = np.nonzero(abs(y_angle_arr - y_deg) == np.min(min(abs(y_angle_arr - y_deg))))[1][-1]
        stats_summary[0, k] = f'Ground_Nasal Lum({chromaticity_fov}deg)'
        stats_summary[1, k] = Lum_masked[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = f'Ground_Nasal x({chromaticity_fov}deg)'
        stats_summary[1, k] = x_smoothed_masked[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = f'Ground_Nasal y({chromaticity_fov}deg)'
        stats_summary[1, k] = y_smoothed_masked[row_ind, col_ind]
        k = k + 1
        # % Ground Temporal luminance and color
        if ModuleLR == 'L':
            x_deg = -chromaticity_fov * 1.414 / 2
            y_deg = chromaticity_fov * 1.414 / 2
        else:
            x_deg = chromaticity_fov * 1.414 / 2
            y_deg = chromaticity_fov * 1.414 / 2
        col_ind = np.nonzero(abs(x_angle_arr - x_deg) == np.min(min(abs(x_angle_arr - x_deg))))[1][-1]
        row_ind = np.nonzero(abs(y_angle_arr - y_deg) == np.min(min(abs(y_angle_arr - y_deg))))[1][-1]
        stats_summary[0, k] = f'Ground_Temporal Lum({chromaticity_fov}deg)'
        stats_summary[1, k] = Lum_masked[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = f'Ground_Temporal x({chromaticity_fov}deg)'
        stats_summary[1, k] = x_smoothed_masked[row_ind, col_ind]
        k = k + 1
        stats_summary[0, k] = f'Ground_Temporal y({chromaticity_fov}deg)'
        stats_summary[1, k] = y_smoothed_masked[row_ind, col_ind]
        k = k + 1
        # %%
        del col_ind, row_ind

        # % Max brightness
        stats_summary[0, k] = 'Max Lum'
        stats_summary[1, k] = max_Y_val
        k = k + 1
        stats_summary[0, k] = 'Max Lum x'
        stats_summary[1, k] = x_smoothed_masked[max_Y_yloc_pix, max_Y_xloc_pix]
        k = k + 1
        stats_summary[0, k] = 'Max Lum y'
        stats_summary[1, k] = y_smoothed_masked[max_Y_yloc_pix, max_Y_xloc_pix]
        k = k + 1
        stats_summary[0, k] = 'Max Lum x(deg)'
        stats_summary[1, k] = max_Y_xloc_deg
        k = k + 1
        stats_summary[0, k] = 'Max Lum y(deg)'
        stats_summary[1, k] = max_Y_yloc_deg
        k = k + 1
        # % Brightness uniformity
        Y = XYZ[:, :, 1]

        tmp_chromaticity_mask = chromaticity_mask
        tmp = Y[tmp_chromaticity_mask == 1]
        meanLum = np.mean(tmp)
        deltaLum = np.max(tmp) - np.min(tmp)
        stdLum = np.std(tmp, ddof=1)
        percentLum_5 = np.percentile(tmp, 5)
        percentLum_95 = np.percentile(tmp, 95)
        percentLum_onaxis = np.sum(tmp > lum_thresh * Y[row_ind_onaxis, col_ind_onaxis]) / len(tmp)
        percentLum_max = np.sum(tmp > lum_thresh * max_Y_val) / len(tmp)

        # %save data to cell
        stats_summary[0, k] = f'Lum_mean_{chromaticity_fov}deg'
        stats_summary[1, k] = meanLum
        k = k + 1
        stats_summary[0, k] = f'Lum_delta_{chromaticity_fov}deg'
        stats_summary[1, k] = deltaLum
        k = k + 1
        stats_summary[0, k] = f'Lum 5%{chromaticity_fov}deg'
        stats_summary[1, k] = percentLum_5
        k = k + 1
        stats_summary[0, k] = f'Lum 95%{chromaticity_fov}deg'
        stats_summary[1, k] = percentLum_95
        k = k + 1
        stats_summary[0, k] = f'Lum_Ratio>{lum_thresh}OnAxisLum_{chromaticity_fov}deg'
        stats_summary[1, k] = percentLum_onaxis
        k = k + 1
        stats_summary[0, k] = f'Lum_Ratio>{lum_thresh}MaxLum_{chromaticity_fov}deg'
        stats_summary[1, k] = percentLum_max
        k = k + 1

        #% color uniformity

        tmp_chromaticity_mask = chromaticity_mask
        tmpu_prime = u_prime_smoothed_masked[tmp_chromaticity_mask == 1]
        tmpv_prime = v_prime_smoothed_masked[tmp_chromaticity_mask == 1]
        tmpdeltau_prime = tmpu_prime - u_prime_smoothed_masked[row_ind_onaxis, col_ind_onaxis]
        tmpdeltav_prime = tmpv_prime - v_prime_smoothed_masked[row_ind_onaxis, col_ind_onaxis]
        tmpdeltauv_prime = np.sqrt(tmpdeltau_prime ** 2 + tmpdeltav_prime ** 2)
        meanu_prime = np.mean(tmpu_prime)
        meanv_prime = np.mean(tmpv_prime)
        percentuv_95 = np.percentile(tmpdeltauv_prime, 95)
        deltauv = np.percentile(tmpdeltauv_prime, 99.9)
        # %save data to cell
        stats_summary[0, k] = f"u'_mean_{chromaticity_fov}deg"
        stats_summary[1, k] = meanu_prime
        k = k + 1
        stats_summary[0, k] = f"v'_mean_{chromaticity_fov}deg"
        stats_summary[1, k] = meanv_prime
        k = k + 1
        stats_summary[0, k] = f"u'v'_delta_to_OnAxis_{chromaticity_fov}deg"
        stats_summary[1, k] = deltauv
        k = k + 1
        stats_summary[0, k] = f"du'v' 95%{chromaticity_fov}deg"
        stats_summary[1, k] = percentuv_95
        k += 1

        temp_status_s = dict(np.transpose(stats_summary))
        stats_summary[0, k] = f"Luminance Temporal Instantaneous % of On-axis"
        stats_summary[1, k] = temp_status_s[f'Temporal Lum({chromaticity_fov}deg)'] / temp_status_s['OnAxis Lum']
        k += 1

        stats_summary[0, k] = f"Luminance Ground Instantaneous % of On-axis"
        stats_summary[1, k] = temp_status_s[f'Ground Lum({chromaticity_fov}deg)'] / temp_status_s['OnAxis Lum']
        k += 1

        stats_summary[0, k] = f"Luminance Sky Instantaneous % of On-axis"
        stats_summary[1, k] = temp_status_s[f'Sky Lum({chromaticity_fov}deg)'] / temp_status_s['OnAxis Lum']
        k += 1

        stats_summary = stats_summary[:, 0:k]

        ## save images
        # NasalFOV 35~40
        # Temporal FOV 50~55
        # Sky FOV 45~50
        # Ground FOV 45~50
        if self._save_plots:
            disp_fov = 50
            # deternp.mine module left or right
            x_deg = 40
            y_deg = 0
            col_ind = np.nonzero(np.abs(x_angle_arr - x_deg) == np.min(np.abs(x_angle_arr - x_deg)))[1][0]
            row_ind = np.nonzero(np.abs(y_angle_arr - y_deg) == np.min(np.abs(y_angle_arr - y_deg)))[1][0]
            if Y[row_ind, col_ind] / max_Y_val > 0.2:
                Module = 'R'
                x_deg_max = 50
                x_deg_min = -35
                col_ind_max = np.nonzero(np.abs(x_angle_arr - x_deg_max) == np.min(np.abs(x_angle_arr - x_deg_max)))[1][0]
                col_ind_min = np.nonzero(np.abs(x_angle_arr - x_deg_min) == np.min(np.abs(x_angle_arr - x_deg_min)))[1][0]
            else:
                Module = 'L'
                x_deg_max = 35
                x_deg_min = -50
                col_ind_max = np.nonzero(np.abs(x_angle_arr - x_deg_max) == np.min(np.abs(x_angle_arr - x_deg_max)))[1][0]
                col_ind_min = np.nonzero(np.abs(x_angle_arr - x_deg_min) == np.min(np.abs(x_angle_arr - x_deg_min)))[1][0]

            y_deg_max = 45
            y_deg_min = -45
            row_ind_max = np.nonzero(np.abs(y_angle_arr - y_deg_max) == np.min(np.abs(y_angle_arr - y_deg_max)))[1][0]
            row_ind_min = np.nonzero(np.abs(y_angle_arr - y_deg_min) == np.min(np.abs(y_angle_arr - y_deg_min)))[1][0]

            # Create array of angle rings to display
            angle_arr = np.linspace(0, 2 * np.pi, 361)
            # for i in range(0,chromaticity_fov.shape[1]):
            polar_ring_x = chromaticity_fov * np.sin(angle_arr)
            polar_ring_y = chromaticity_fov * np.cos(angle_arr)

            # Create array of angle ring to show area where chromaticity calculations
            # are performed
            chroma_ring_x = chromaticity_fov * np.sin(angle_arr)
            chroma_ring_y = chromaticity_fov * np.cos(angle_arr)
            # Create array of angle ring to show area where masking occurs
            disp_fov_ring_x = disp_fov * np.sin(angle_arr)
            disp_fov_ring_y = disp_fov * np.cos(angle_arr)
            # plot brightness images
            title_label_Yonly = 'Brightness - Smoothed Data'

            subtitle_label_Yonly = f'Max: {max_Y_val:.2f}nits at x={max_Y_xloc_deg:.2f}°,y={max_Y_yloc_deg:.2f}°'
            clims_smooth = [0, np.max(XYZ[row_ind_min - 1:row_ind_max, col_ind_min - 1:col_ind_max, 1])]

            plt.figure()
            plt.subplot(2, 2, 1)
            # colorbar
            # colormap jet
            # axis image
            # axis equal
            # x = x_angle_arr[0, :]
            # y = y_angle_arr[0, :]
            # dx = (x[1] - x[0]) / 2
            # dy = (y[1] - y[0]) / 2
            # x_ = [x[0] - dx] + [a + dx for a in x]  # x axis
            # y_ = [y[0] - dy] + [a + dy for a in y]  # y axis
            # xx, yy = np.meshgrid(x_, y_)
            # plt.pcolor(xx, yy, Y, cmap='jet')
            plt.gca().set_aspect('equal', adjustable='box')
            plt.imshow(Y, cmap='jet',
                       extent=[np.min(x_angle_arr), np.max(x_angle_arr), np.max(y_angle_arr), np.min(y_angle_arr)])
            plt.colorbar()

            plt.title(f'{title_label_Yonly}\n{subtitle_label_Yonly}')
            plt.xlabel('X angle (deg)')
            plt.ylabel('Y angle (deg)')
            # hold on
            plt.plot([-1 * disp_fov, disp_fov], [0, 0], Color='w', linewidth=1)
            plt.plot([0, 0], [-1 * disp_fov, disp_fov], Color='w', linewidth=1)
            # for i in range(0, polar_ring_x.shape[0]):
            plt.plot(polar_ring_x, polar_ring_y, color='w', linewidth=1)

            plt.plot(max_Y_xloc_deg, max_Y_yloc_deg, c='w', marker='+')

            plt.xlim([-disp_fov, disp_fov])
            plt.ylim([disp_fov, -disp_fov])
            # hold off
            plt.subplot(2, 2, 2)
            plt.plot(x_angle_arr[0, col_ind_min - 1:col_ind_max],
                     XYZ[3001, col_ind_min - 1:col_ind_max, 1] / max_Y_val, linewidth=1)
            plt.xticks([-disp_fov, -chromaticity_fov, 0, chromaticity_fov, disp_fov])
            plt.xlabel('X angle (deg)')
            plt.ylabel('Normalized Brightness')
            plt.title('Normalized Brightness - x')
            # hold on
            plt.plot([-1 * chromaticity_fov, -1 * chromaticity_fov], [0, 1], color='r', linestyle='--', linewidth=1)
            plt.plot([chromaticity_fov, chromaticity_fov], [0, 1], color='r', linestyle='--', linewidth=1)

            plt.plot([0, 0], [0, 1], color='r', linestyle='--', linewidth=1)
            plt.plot([x_deg_min, x_deg_max], [0.8, 0.8], color='r', linestyle='--', linewidth=1)
            # hold off
            plt.subplot(2, 2, 3)
            plt.plot(y_angle_arr[0, row_ind_min - 1:row_ind_max],
                     XYZ[row_ind_min - 1:row_ind_max, 3001, 1] / max_Y_val, linewidth=1)
            plt.xticks([-disp_fov, -chromaticity_fov, 0, chromaticity_fov, disp_fov])
            plt.xlabel('Y angle (deg)')
            plt.ylabel('Normalized Brightness')
            plt.title('Normalized Brightness - y')
            plt.xlim([-disp_fov, disp_fov])

            # hold on,
            plt.plot([-1 * chromaticity_fov, -1 * chromaticity_fov], [0, 1], color='r', linestyle='--', linewidth=1)
            plt.plot([chromaticity_fov, chromaticity_fov], [0, 1], color='r', linestyle='--', linewidth=1)
            plt.plot([0, 0], [0, 1], color='r', linestyle='--', linewidth=1)
            plt.plot([y_deg_min, y_deg_max], [0.8, 0.8], color='r', linestyle='--', linewidth=1)

            # hold off
            tmp_histo = XYZ[:, :, 1]
            tmp_histo = tmp_histo * chromaticity_mask
            nbins = np.int(np.round((np.max(tmp_histo) - np.min(tmp_histo)) / 5))
            plt.subplot(2, 2, 4)
            cc = tmp_histo[tmp_histo != 0]
            weights = np.ones_like(cc) / float(len(cc))
            rst = plt.hist(cc, density=True, range=(np.int(np.min(cc)), np.max(cc)), weights=weights,
                          bins=nbins, histtype='bar', edgecolor='b', stacked=False)
            plt.xlabel('Luminance (nits)')
            plt.ylabel('Percentage')
            plt.gca().yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(np.sum(rst[0]), decimals=0, symbol=None))
            plt.gca().yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(np.sum(rst[0])/20))
            # ytix = get(gca, 'YTick')
            # set(gca, 'YTick',ytix, 'YTickLabel',ytix*100)
            plt.title('Lum Histo 0-30° FOV')
            plt.tight_layout()
            if not os.path.exists(os.path.join(dirr, self._exp_dir)):
                os.makedirs(os.path.join(dirr, self._exp_dir))
            plt.savefig(os.path.join(dirr, self._exp_dir, fnamebase + '_plot_Brightness.png'))
            plt.clf()

            # plot delta u'v' image
            Delta_u_prime_smoothed_masked = (u_prime_smoothed_masked - u_prime_smoothed_masked[3001, 3001]) * XYZ_mask
            Delta_v_prime_smoothed_masked = (v_prime_smoothed_masked - v_prime_smoothed_masked[3001, 3001]) * XYZ_mask
            Delta_uv_prime_smoothed_masked = np.sqrt(
                Delta_u_prime_smoothed_masked ** 2 + Delta_v_prime_smoothed_masked ** 2)
            plt.figure()
            plt.subplot(221)  # imagesc(x_angle_arr,y_angle_arr,Delta_uv_prime_smoothed_masked)
            # caxis([0,0.02])colorbarcolormap jetaxis equal
            plt.imshow(Delta_uv_prime_smoothed_masked, cmap='jet', vmin=0, vmax=0.02,
                       extent=[np.min(x_angle_arr), np.max(x_angle_arr), np.max(y_angle_arr), np.min(y_angle_arr)])
            plt.colorbar()
            plt.xlabel('X angle (deg)')
            plt.ylabel('Y angle (deg)')
            plt.xlim([-disp_fov, disp_fov])
            plt.ylim([disp_fov, -disp_fov])
            plt.title("Δu'v'")
            # hold on
            plt.plot([-1 * disp_fov, disp_fov], [0, 0], color='w', linewidth=1)
            plt.plot([0, 0], [-1 * disp_fov, disp_fov], color='w', linewidth=1)
            plt.plot(polar_ring_x, polar_ring_y, color='w', linewidth=1)

            plt.plot(max_Y_xloc_deg, max_Y_yloc_deg, c='w', marker='+')
            plt.subplot(222)
            plt.plot(x_angle_arr[0, col_ind_min:col_ind_max], Delta_uv_prime_smoothed_masked[3001, col_ind_min:col_ind_max])
            plt.xticks([-disp_fov, -chromaticity_fov, 0, chromaticity_fov, disp_fov])
            plt.title("Δu'v' along x")
            plt.xlim([-disp_fov, disp_fov])
            plt.ylim([0, 0.02])
            plt.xlabel('X angle (deg)')
            plt.ylabel("Δu'v'")
            plt.title("Δu'v' along x")
            plt.xlim([-disp_fov, disp_fov])
            # hold on,
            plt.plot([-1 * chromaticity_fov, -1 * chromaticity_fov], [0, 1], color='r', linestyle='--', linewidth=1)
            plt.plot([chromaticity_fov, chromaticity_fov], [0, 1], color='r', linestyle='--', linewidth=1)
            plt.plot([y_deg_min, y_deg_max], [0.01, 0.01], color='r', linestyle='--', linewidth=1)
            plt.plot([y_deg_min, y_deg_max], [0.005, 0.005], color='r', linestyle='--', linewidth=1)
            # hold off
            plt.subplot(2, 2, 3)
            plt.plot(y_angle_arr[0, row_ind_min:row_ind_max], Delta_uv_prime_smoothed_masked[row_ind_min:row_ind_max, 3001])
            plt.xlim([-disp_fov, disp_fov])
            plt.ylim([0, 0.02])
            # xticks([-disp_fov -chromaticity_fov 0 chromaticity_fov disp_fov])
            plt.xlabel('Y angle (deg)')
            plt.ylabel("Δu'v'")
            plt.title("Δu'v' along y")
            # hold on,
            plt.plot([-1 * chromaticity_fov, -1 * chromaticity_fov], [0, 1], color='r', linestyle='--', linewidth=1)
            plt.plot([chromaticity_fov, chromaticity_fov], [0, 1], color='r', linestyle='--', linewidth=1)
            plt.plot([y_deg_min, y_deg_max], [0.01, 0.01], color='r', linestyle='--', linewidth=1)
            plt.plot([y_deg_min, y_deg_max], [0.005, 0.005], color='r', linestyle='--', linewidth=1)
            # hold off
            tmp_histo = Delta_uv_prime_smoothed_masked
            tmp_histo = tmp_histo * chromaticity_mask
            nbins = np.int(np.round((np.max(tmp_histo) - np.min(tmp_histo)) / 0.0005))
            plt.subplot(2, 2, 4)
            cc = tmp_histo[tmp_histo != 0]
            weights = np.ones_like(cc) / float(len(tmp_histo))
            rst = plt.hist(cc, density=True, bins=nbins, histtype='bar', edgecolor='b', weights=weights,
                           range=[np.int(np.min(cc)), np.max(cc)])
            plt.gca().yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(np.sum(rst[0]), decimals=0, symbol=None))
            plt.gca().yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(np.sum(rst[0]) / 20))
            plt.gca().xaxis.get_major_formatter().set_powerlimits((0, 1))
            plt.xlabel("Δu'v'")
            plt.ylabel('Percentage')
            # set(gca, 'YTick',ytix, 'YTickLabel',ytix*100)
            plt.title("Δu'v' Histo 0-30° FOV")
            plt.tight_layout()

            plt.savefig(os.path.join(dirr, self._exp_dir, fnamebase + '_plot_duv.png'))
            plt.clf()

            RGB = np.zeros(XYZ.shape)
            RGB[:, :, 0] = 0.41847 * XYZ[:, :, 0] - 0.15866 * XYZ[:, :, 1] - 0.082835 * XYZ[:, :, 2]
            RGB[:, :, 1] = -0.09169 * XYZ[:, :, 0] + 0.25243 * XYZ[:, :, 1] - 0.015708 * XYZ[:, :, 2]
            RGB[:, :, 2] = 0.00092090 * XYZ[:, :, 0] - 0.0025498 * XYZ[:, :, 1] + 0.17860 * XYZ[:, :, 2]

            # Mask and normalize RGB image for display
            RGB = RGB * np.stack([cam_fov_mask] * 3, axis=2)
            RGB = RGB / np.max(RGB)

            plt.figure()
            plt.imshow(RGB,
                       extent=[np.min(x_angle_arr), np.max(x_angle_arr), np.max(y_angle_arr), np.min(y_angle_arr)])
            plt.xlabel('X angle (deg)')
            plt.ylabel('Y angle (deg)')
            plt.xlim([-disp_fov, disp_fov])
            plt.ylim([disp_fov, -disp_fov])
            plt.title('RGB Image')
            plt.tight_layout()
            plt.savefig(os.path.join(dirr, self._exp_dir, fnamebase + '_RGB_color.png'))
            plt.clf()
            del RGB, angle_arr, cc,
            del Delta_v_prime_smoothed_masked, Delta_uv_prime_smoothed_masked, Delta_u_prime_smoothed_masked
            del tmp_histo, weights

        del tmp_chromaticity_mask, Y
        del XYZ, filename, x_angle_arr, y_angle_arr
        del chromaticity_mask
        del cam_fov_mask, tmp_XYZ, XYZ_mask, u_prime_smoothed_masked,
        del v_prime_smoothed_masked, max_Y_xloc_deg, max_Y_yloc_deg,
        del col_ind_onaxis, row_ind_onaxis,
        del Lum_masked, Lum_masked_TargetTemp
        del tmp, tmpdeltauv_prime, tmpdeltau_prime, tmpdeltav_prime, tmpu_prime, tmpv_prime,
        del x_smoothed_masked, x_smoothed_masked_TargetTemp,
        del y_smoothed_masked, y_smoothed_masked_TargetTemp,

        return dict(np.transpose(stats_summary))

    @staticmethod
    def calc_gl_for_brightdot(W255_stats_summary, WRGBBoresight_stats_summary, module_temp=30):
        # % load temperature of whitedot pattern
        ModuleTemp = module_temp
        # % set color drift coefficients
        TargetTemp = 47
        #1115
        dLum_W = -0.01135
        dColor_x_W = -0.00051
        dColor_y_W = -0.00058
        dLum_R = -0.01601
        dColor_x_R = 0
        dColor_y_R = -0.00033
        dLum_G = -0.00977
        dColor_x_G = 0.00061
        dColor_y_G = -0.00074
        dLum_B = -0.00873
        dColor_x_B = 0
        dColor_y_B = 0

        x_w = 0.3127 - (TargetTemp - ModuleTemp) * dColor_x_W
        y_w = 0.329 - (TargetTemp - ModuleTemp) * dColor_y_W
        #1115
        Temp_W = WRGBBoresight_stats_summary["Module Temperature"]
        Temp_R = WRGBBoresight_stats_summary["Module Temperature"]
        Temp_G = WRGBBoresight_stats_summary["Module Temperature"]
        Temp_B = WRGBBoresight_stats_summary["Module Temperature"]

        # Temp_W = W255_stats_summary["Module Temperature"]
        # Temp_R = R255_stats_summary["Module Temperature"]
        # Temp_G = G255_stats_summary["Module Temperature"]
        # Temp_B = B255_stats_summary["Module Temperature"]

        Y_w = W255_stats_summary["OnAxis Lum"] * (1 + (ModuleTemp - Temp_W) * dLum_W)
        Y_r = WRGBBoresight_stats_summary["R_Lum_corrected"] * (1 + (ModuleTemp - Temp_R) * dLum_R)
        Y_g = WRGBBoresight_stats_summary["G_Lum_corrected"] * (1 + (ModuleTemp - Temp_G) * dLum_G)
        Y_b = WRGBBoresight_stats_summary["B_Lum_corrected"] * (1 + (ModuleTemp - Temp_B) * dLum_B)

        x_r = WRGBBoresight_stats_summary["R_x_corrected"] + (ModuleTemp - Temp_R) * dColor_x_R
        y_r = WRGBBoresight_stats_summary["R_y_corrected"] + (ModuleTemp - Temp_R) * dColor_y_R
        x_g = WRGBBoresight_stats_summary["G_x_corrected"] + (ModuleTemp - Temp_G) * dColor_x_G
        y_g = WRGBBoresight_stats_summary["G_y_corrected"] + (ModuleTemp - Temp_G) * dColor_y_G
        x_b = WRGBBoresight_stats_summary["B_x_corrected"] + (ModuleTemp - Temp_B) * dColor_x_B
        y_b = WRGBBoresight_stats_summary["B_y_corrected"] + (ModuleTemp - Temp_B) * dColor_y_B
        Y_rgb_measure = [Y_r, Y_g, Y_b]

        w255 = np.array([Y_w * x_w / y_w, Y_w, Y_w * (1 - x_w - y_w) / y_w])
        m = np.array([[x_r / y_r, x_g / y_g, x_b / y_b],
                      [1, 1, 1],
                      [(1 - x_r - y_r) / y_r, (1 - x_g - y_g) / y_g, (1 - x_b - y_b) / y_b]])
        Y_rgb = np.dot(np.linalg.pinv(m), w255)
        Y_scale = Y_rgb / Y_rgb_measure
        # Lum for R255, G255, B255
        Lum_before = Y_rgb_measure
        # Lum for Red, Green and Blue for D65
        Lum_after = Y_rgb / np.max(Y_scale)
        Gamma = 2.2
        gray_levels = np.round(np.power(Lum_after / Lum_before, 1 / Gamma) * 255).astype(np.int)

        return {'GL': gray_levels,
                'x_w': x_w,
                'y_w': y_w,
                'ModuleTemp': ModuleTemp}

    @staticmethod
    def interp2(xx, yy, z, xi, yi):
        f = scipy.interpolate.interp2d(
            xx.astype(np.float64), yy.astype(np.float64), z.astype(np.float64), kind='linear')
        return f(xi, yi)

    @staticmethod
    def sub2ind(array_shape, rows, cols):
        ind = rows * array_shape[1] + cols
        ind[ind < 0] = -1
        ind[ind >= array_shape[0] * array_shape[1]] = -1
        return ind

    @staticmethod
    def ind2sub(array_shape, xind):
        if isinstance(xind, np.ndarray):
            ind = xind.astype(np.int)
        elif isinstance(xind, np.int64):
            ind = np.array([xind])
        else:
            raise NotImplementedError(f'Not support by ind2sub {type(xind)}')

        ind[ind < 0] = -1
        ind[ind >= array_shape[0] * array_shape[1]] = -1
        rows = (ind.astype('int') // array_shape[1])
        cols = ind % array_shape[1]
        return (rows, cols)

    def white_dot_pattern_w255_read(self, xfilename=r'W255_X_float.bin', multi_process=False):
        dirr = os.path.dirname(xfilename)
        fnamebase = os.path.basename(xfilename).lower().split('_x_float.bin')[0]
        filename = ['{0}_{1}_float.bin'.format(fnamebase, c) for c in ['X', 'Y', 'Z']]
        XYZ = []

        file_names = [os.path.join(dirr, c) for c in filename]
        if multi_process:
            pool = mp.Pool(mp.cpu_count())
            XYZ_t = pool.map(MotAlgorithmHelper.read_image_raw, file_names)
            pool.close()
        else:
            XYZ_t = [MotAlgorithmHelper.read_image_raw(c) for c in file_names]
        if self._verbose:
            print(f'Read bin files named {fnamebase}\n')
        for image_in in XYZ_t:
            # Z = Z'        #Removed for viewing to match DUT orientation
            image_in = np.rot90(image_in.T, 3)
            image_in = cv2.flip(image_in, 0)
            # image_in = cv2.rotate(image_in, 0)  # Implement flip for viewing to match DUT orientation
            image_in = cv2.filter2D(image_in, -1, MotAlgorithmHelper._kernel, borderType=cv2.BORDER_CONSTANT)
            XYZ.append(image_in)
        XYZ = np.stack(XYZ, axis=2)
        XYZ_1D = np.reshape(XYZ, (self._row * self._col, 3))
        XYZ_1D_ColorCorrected = self._ColorMatrix_.dot(XYZ_1D.T)
        XYZ = np.reshape(XYZ_1D_ColorCorrected.T, (self._row, self._col, 3))
        del XYZ_1D, XYZ_1D_ColorCorrected, image_in, XYZ_t
        return XYZ

    def white_dot_pattern_parametric_export(self, XYZ_W, GL, x_w, y_w, temp_w,
                                            module_temp=30, xfilename=r'WhiteDot_X_float.bin'):
        ModuleTemp = module_temp
        Temp_W = temp_w
        cam_fov = 60
        mask_fov = 30
        row = 6001
        col = 6001
        pixel_spacing = 0.02  # Degrees per pixel
        kernel_width = 14 # Width of square smoothing kernel in pixels.
        kernel_shape = 'square'  # Use 'circle' or 'square' to change the smoothing kernel shape
        # x_w = 0.3127  # color x for D65  version_1.0
        # y_w = 0.3290  # color y for D65
        n_dots = 21
        # XYZ_W = np.ones((3, 3, 3))
        dLum_W = -0.01135
        dColor_x_W = -0.00051
        dColor_y_W = -0.00058
        Lum_W = XYZ_W[:, :, 1] * (1 + (ModuleTemp - Temp_W)*dLum_W)
        Color_x_W = XYZ_W[:, :, 0] / (XYZ_W[:, :, 0] + XYZ_W[:, :, 1] + XYZ_W[:, :, 2]) + (ModuleTemp-Temp_W)*dColor_x_W
        Color_y_W = XYZ_W[:, :, 1] / (XYZ_W[:, :, 0] + XYZ_W[:, :, 1] + XYZ_W[:, :, 2]) + (ModuleTemp-Temp_W)*dColor_y_W
        # LumRatio_W = Lum_W(3001,3001)./Lum_W
        # dColor_x_W = Color_x_W-Color_x_W(3001,3001)
        # dColor_y_W = Color_y_W-Color_y_W(3001,3001)
        ##
        ''' Read in the WhiteDot image version_1.0
        # dirr = os.path.dirname(xfilename)
        # fnamebase = os.path.basename(xfilename).lower().split('_x_float.bin')[0]
        # filename = ['{0}_{1}_float.bin'.format(fnamebase, c) for c in ['X', 'Y', 'Z']]
        '''
        # file_path = tkinter.filedialog.askopenfilename(title='Select the bin file',
        #                                                filetypes=[('bin', '*.bin'), ('All Files', '*')],
        #                                                initialdir='K:\\RL_part\WhitePointCorrection',
        #                                                initialfile='normal_W255_20210306_084517_nd_0_iris_5_X_float.bin')

        dirr = os.path.dirname(xfilename)
        fnamebase = os.path.basename(xfilename).lower().split('_x_float.bin')[0]
        filename = ['{0}_{1}_float.bin'.format(fnamebase, c) for c in ['X', 'Y', 'Z']]
        primary = ['X', 'Y', 'Z']

        x_angle_arr = np.linspace(-1 * cam_fov, cam_fov, col)
        y_angle_arr = np.linspace(-1 * cam_fov, cam_fov, row)

        kernel = np.ones((kernel_width, kernel_width))

        kernel = kernel / np.sum(kernel)  # normalize
        XYZ = []
        XYZ_smooth = []
        XYZ_t = [MotAlgorithmHelper.read_image_raw(os.path.join(dirr, c)) for c in filename]
        for image_in in XYZ_t:
            image_in = np.rot90(image_in.T, 3)
            image_in = np.flip(image_in, 0)
            # image_in = cv2.rotate(image_in, 0)
            XYZ.append(image_in)
            image_in_smooth = cv2.filter2D(image_in, -1, kernel, borderType=cv2.BORDER_CONSTANT)
            XYZ_smooth.append(image_in_smooth)
            del image_in_smooth
        del XYZ_t
        XYZ = np.stack(XYZ, axis=2)

        XYZ_smooth = np.stack(XYZ_smooth, axis=2)
        XYZ_1D = np.reshape(XYZ_smooth, (self._row * self._col, 3))
        XYZ_1D_ColorCorrected = self._ColorMatrix_.dot(XYZ_1D.T)
        XYZ_smooth = np.reshape(XYZ_1D_ColorCorrected.T, (self._row, self._col, 3))

        Y = XYZ[:, :, 1]
        del XYZ_1D, XYZ, XYZ_1D_ColorCorrected

        # Create array of angle rings to display
        angle_arr = np.linspace(0, 2 * np.pi, 361)

        disp_fov = cam_fov
        # Create array of angle ring to show area where masking occurs
        disp_fov_ring_x = disp_fov * np.sin(angle_arr)
        disp_fov_ring_y = disp_fov * np.cos(angle_arr)

        # Create viewing masks

        col_deg_arr = np.tile(x_angle_arr, (row, 1))
        row_deg_arr = np.tile(y_angle_arr.T, (col, 1)).T
        # print(row_deg_arr.shape)
        radius_deg_arr = (col_deg_arr ** 2 + row_deg_arr ** 2) ** (1 / 2)
        mask = np.ones((row, col))
        # mask(radius_deg_arr > mask_fov) = 0#有问题
        mask[np.where(radius_deg_arr > mask_fov)] = 0

        masked_tristim = Y * mask
        max_XYZ_val = np.max(masked_tristim)

        Lumiance_thresh = 10
        Length_thresh = 10
        Img = cv2.inRange(masked_tristim, 10, 255) // 255
        # figure,imagesc(x_angle_arr,y_angle_arr,Img)
        Img = label(Img, connectivity=2)
        stats = regionprops(Img)
        scenters = []
        sMajorAxisLength = []
        sMinorAxisLength = []

        for i, stat in enumerate(stats):
            if stat['MajorAxisLength'] >= Length_thresh:
                scenters.append(list(stat['Centroid']))
                sMajorAxisLength.append(stat['MajorAxisLength'])
                sMinorAxisLength.append(stat['MinorAxisLength'])

        # print('num stats 0 / 1'.format(len(scenters), len(stats)))
        num_dots = len(scenters)

        a = np.nonzero(np.array(sMajorAxisLength) < Length_thresh)
        b = np.nonzero(np.array(sMinorAxisLength) > 50)

        centroid = np.zeros((num_dots, 2))
        for i in range(0, num_dots):
            mlen = sMajorAxisLength[i]
            d = np.floor(sMajorAxisLength[i] / 2) + 1

            scenter = scenters[i]
            scentery = scenters[i][1]
            scentera = int(np.floor(scenters[i][1] - d))
            scenterb = int(np.floor(scenters[i][1] + d))
            scenterc = int(np.floor(scenters[i][0] - d))
            scenterd = int(np.floor(scenters[i][0] + d))
            im = Y[scenterc:scenterd + 1, scentera:scenterb + 1]
            [rows, cols] = im.shape
            x = np.ones((rows, 1)) * np.arange(1, cols + 1)  # # Matrix with each pixel set to its x coordinate
            y = np.arange(1, rows + 1).reshape(rows, -1) * np.ones((1, cols))
            area = np.sum(im)

            hx = np.sum(np.float32(im) * x)
            hy = np.sum(np.float32(im) * y)

            meanx = np.sum(np.float32(im) * x) / area - d - 1
            meany = np.sum(np.float32(im) * y) / area - d - 1
            centroid[i, 1] = int(scenters[i][0]) + meany
            centroid[i, 0] = meanx + int(scenters[i][1])

        I = np.lexsort(centroid.T[:1, :])
        Centroid = centroid[I, :]

        Centroid2 = np.empty(Centroid.shape, np.object)
        for i in range(0, n_dots):
            Centroid_temp = Centroid[i * n_dots:(i + 1) * n_dots, :]
            I = np.lexsort(Centroid_temp.T[:2, :])
            Centroid_temp = Centroid_temp[I, :]
            Centroid2[i * n_dots:(i + 1) * n_dots, :] = Centroid_temp  # 有问题

        centroid = Centroid2
        del Centroid2

        # figure,plot(centroid(:,1),centroid(:,2),'.')
        # plt.figure(1)
        # plt.plot(centroid[:,0],centroid[:,1],'.')
        Size = np.shape(centroid)
        Lum_WP_output = []
        Color_WP_x_output = []
        Color_WP_y_output = []
        dxdy_WP_output = []
        Lum_WP_output_corrected = []
        Color_WP_x_output_corrected = []
        Color_WP_y_output_corrected = []
        dxdy_WP_output_corrected = []

        if Size[0] == n_dots ** 2:
            Lum = np.empty((n_dots ** 2,), dtype=np.object)
            Color_x = np.empty(Lum.shape, dtype=np.object)
            Color_y = np.empty(Lum.shape, dtype=np.object)
            Color_x_corrected = np.empty(Lum.shape, dtype=np.object)
            Lum_corrected = np.empty(Lum.shape, dtype=np.object)
            Color_y_corrected = np.empty(Lum.shape, dtype=np.object)

            for i in range(0, n_dots ** 2):
                d = 25
                # np.trunc the index about center.
                cx1 = int(np.trunc(centroid[i, 1] - d))
                cx2 = int(np.trunc(centroid[i, 1] + d)) + 1
                cy1 = int(np.trunc(centroid[i, 0] - d))
                cy2 = int(np.trunc(centroid[i, 0] + d)) + 1
                im = XYZ_smooth[cx1:cx2, cy1:cy2, :]
                '''verson_1.0
                X_center = cv2.filter2D(im[:, :, 0], -1, kernel, borderType=cv2.BORDER_CONSTANT)
                Y_center = cv2.filter2D(im[:, :, 1], -1, kernel, borderType=cv2.BORDER_CONSTANT)
                Z_center = cv2.filter2D(im[:, :, 2], -1, kernel, borderType=cv2.BORDER_CONSTANT)
                '''
                X_center = im[:, :, 0]
                Y_center = im[:, :, 1]
                Z_center = im[:, :, 2]

                Lum[i] = Y_center[26, 26]
                Color_x[i] = X_center[26, 26] / (X_center[26, 26] + Y_center[26, 26] + Z_center[26, 26])
                Color_y[i] = Y_center[26, 26] / (X_center[26, 26] + Y_center[26, 26] + Z_center[26, 26])

                cx0 = int(np.trunc(centroid[i, 1]))
                cy0 = int(np.trunc(centroid[i, 0]))
                LumRatio_W = Lum_W[3000, 3000] / Lum_W[cx0, cy0]
                dColor_x_W = Color_x_W[3000, 3000] - Color_x_W[cx0, cy0]
                dColor_y_W = Color_y_W[3000, 3000] - Color_y_W[cx0, cy0]
                Lum_corrected[i] = Lum[i] * LumRatio_W
                Color_x_corrected[i] = Color_x[i] + dColor_x_W
                Color_y_corrected[i] = Color_y[i] + dColor_y_W

            xx = np.arange(255 - (n_dots - 1) * 2, 256, 2)
            yy = np.arange(255 - (n_dots - 1) * 2, 256, 2)
            [XX, YY] = np.meshgrid(xx, yy)
            Lum2D = np.reshape(Lum, (n_dots, n_dots)).T
            Color_x_2D = np.reshape(Color_x, (n_dots, n_dots)).T
            Color_y_2D = np.reshape(Color_y, (n_dots, n_dots)).T
            Lum2D_corrected = np.reshape(Lum_corrected, (n_dots, n_dots)).T
            Color_x_2D_corrected = np.reshape(Color_x_corrected, (n_dots, n_dots)).T
            Color_y_2D_corrected = np.reshape(Color_y_corrected, (n_dots, n_dots)).T

            xq = np.arange(255 - (n_dots - 1) * 2, 256, 1)
            yq = np.arange(255 - (n_dots - 1) * 2, 256, 1)
            [Xq, Yq] = np.meshgrid(xq, xq)
            XX, YY = xx, yy
            Lum2Dq = self.interp2(XX, YY, Lum2D, xq, yq)

            Color_x_2Dq = self.interp2(XX, YY, Color_x_2D, xq, yq)
            Color_y_2Dq = self.interp2(XX, YY, Color_y_2D, xq, yq)
            Lum2Dq_corrected = self.interp2(XX, YY, Lum2D_corrected, xq, yq)
            Color_x_2Dq_corrected = self.interp2(XX, YY, Color_x_2D_corrected, xq, yq)
            Color_y_2Dq_corrected = self.interp2(XX, YY, Color_y_2D_corrected, xq, yq)
            # version_3.0_add
            Lum_255 = Lum2Dq_corrected[40, 40]
            Color_x_255 = Color_x_2Dq_corrected[40, 40]
            Color_y_255 = Color_y_2Dq_corrected[40, 40]

            Lum2Dq_corrected = Lum2Dq_corrected*Lum_W[3000, 3000]/Lum_255
            Color_x_2Dq_corrected = Color_x_2Dq_corrected+Color_x_W[3000, 3000]-Color_x_255
            Color_y_2Dq_corrected = Color_y_2Dq_corrected+Color_y_W[3000, 3000]-Color_y_255

            dx = Color_x_2Dq - x_w
            dy = Color_y_2Dq - y_w
            dxdy = np.sqrt(dx ** 2 + dy ** 2)
            dx_corrected = Color_x_2Dq_corrected - x_w
            dy_corrected = Color_y_2Dq_corrected - y_w
            dxdy_corrected = np.sqrt(dx_corrected ** 2 + dy_corrected ** 2)
            # version_3.0_add
            if GL[2] == 255:
                Xlabel_name = 'R Light Level'
                Ylabel_name = 'G Light Levle'
            elif GL[1] == 255:
                Xlabel_name = 'R Light Level'
                Ylabel_name = 'B Light Levle'
            else:
                Xlabel_name = 'G Light Level'
                Ylabel_name = 'B Light Levle'
            if self._save_plots:
                plt.figure()
                plt.subplot(2, 2, 1)
                plt.xlim([np.min(xx), np.max(xx)])
                plt.ylim([np.max(yy), np.min(yy)])
                plt.imshow(Lum2D_corrected.astype(np.float32), extent=[np.min(xx), np.max(xx), np.max(yy), np.min(yy)])
                plt.colorbar()
                plt.xlabel(Xlabel_name)
                plt.ylabel(Ylabel_name)
                plt.title('Lum')
                plt.subplot(2, 2, 2)
                plt.xlim([np.min(xx), np.max(xx)])
                plt.ylim([np.max(yy), np.min(yy)])
                plt.imshow(Color_x_2D_corrected.astype(np.float32), extent=[np.min(xx), np.max(xx), np.max(yy), np.min(yy)])
                plt.colorbar(),
                plt.xlabel(Xlabel_name)
                plt.ylabel(Ylabel_name)
                plt.title('Color x')
                plt.subplot(2, 2, 3)
                plt.xlim([np.min(xx), np.max(xx)])
                plt.ylim([np.max(yy), np.min(yy)])
                plt.imshow(Color_y_2D_corrected.astype(np.float32), extent=[np.min(xx), np.max(xx), np.max(yy), np.min(yy)])
                plt.colorbar()
                plt.xlabel(Xlabel_name)
                plt.ylabel(Ylabel_name)
                plt.title('Color y')
                plt.xlim([np.min(xx), np.max(xx)])
                plt.ylim([np.max(yy), np.min(yy)])
                plt.subplot(2, 2, 4)
                plt.imshow(dxdy_corrected.astype(np.float32), extent=[np.min(xx), np.max(xx), np.max(yy), np.min(yy)])
                plt.colorbar()
                plt.xlabel(Xlabel_name)
                plt.ylabel(Ylabel_name)
                plt.title('Color Δxy to target white')
                plt.tight_layout()
                if not os.path.exists(os.path.join(dirr, self._exp_dir)):
                    os.makedirs(os.path.join(dirr, self._exp_dir))
                plt.savefig(os.path.join(dirr, self._exp_dir, fnamebase + '_plot_dxy.png'))
                plt.clf()

            # GL = [100, 100, 100]
            if np.min(GL) < 255 - (n_dots - 1) * 2:
                Lum_WP_output_corrected = np.nan
                Color_WP_x_output_corrected = np.nan
                Color_WP_y_output_corrected = np.nan
            else:
                if GL[2] == 255:
                    row = GL[1]
                    col = GL[0]
                elif GL[1] == 255:
                    row = GL[2]
                    col = GL[0]
                else:
                    row = GL[2]
                    col = GL[1]

                row = row - (255 - (n_dots - 1) * 2)
                col = col - (255 - (n_dots - 1) * 2)
                Lum_WP_output_corrected = Lum2Dq_corrected[row, col]
                Color_WP_x_output_corrected = Color_x_2Dq_corrected[row, col]
                Color_WP_y_output_corrected = Color_y_2Dq_corrected[row, col]

            min_ext = lambda data: (np.min(data), np.argmin(data))
            min_val, idx = min_ext(dxdy_corrected)

            row, col = MotAlgorithmHelper.ind2sub(dxdy_corrected.shape, idx)
            row = row[0]
            col = col[0]
            if GL[2] == 255:
                R_output_corrected = Xq[row, col]
                G_output_corrected = Yq[row, col]
                B_output_corrected = 255
            elif GL[1] == 255:
                R_output_corrected = Xq[row, col]
                G_output_corrected = 255
                B_output_corrected = Yq[row, col]
            else:
                R_output_corrected = 255
                G_output_corrected = Xq[row, col]
                B_output_corrected = Yq[row, col]

            # version3.0
            Lum_output_corrected = Lum2Dq_corrected[row, col]
            Color_x_output_corrected = Color_x_2Dq_corrected[row, col]
            Color_y_output_corrected = Color_y_2Dq_corrected[row, col]
            dxdy_output_corrected = dxdy_corrected[row, col]

            RGB_output2DDIC = [R_output_corrected, G_output_corrected, B_output_corrected]
            if R_output_corrected == 215 or G_output_corrected == 215 or B_output_corrected == 215:
                RGB_output2DDIC = GL

            del dxdy_output_corrected, Lum, Color_x, Color_y, Color_x_corrected, Color_y_corrected, Lum_corrected
            del Lum2D, Color_x_2D, Color_y_2D, Color_x_2D_corrected, Color_y_2D_corrected, Lum2D_corrected,

        # Output Statistics
        k = 0
        stats_summary = np.empty((2, 100), dtype=object)
        stats_summary[0, k] = 'dir'
        stats_summary[1, k] = os.path.join(dirr, fnamebase)
        k = k + 1
        # Record temperature
        stats_summary[0, k] = 'Module Temperature'
        stats_summary[1, k] = ModuleTemp
        k = k + 1
        stats_summary[0, k] = 'Target color x'
        stats_summary[1, k] = x_w
        k = k + 1
        stats_summary[0, k] = 'Target color y'
        stats_summary[1, k] = y_w
        k = k + 1
        stats_summary[0, k] = 'WP255 Lum'
        stats_summary[1, k] = Lum_255
        k = k + 1
        stats_summary[0, k] = 'WP255 x'
        stats_summary[1, k] = Color_x_255
        k = k + 1
        stats_summary[0, k] = 'WP255 y'
        stats_summary[1, k] = Color_y_255
        k = k + 1
        stats_summary[0, k] = 'WP R Quest Algo'
        stats_summary[1, k] = GL[0]
        k = k + 1
        stats_summary[0, k] = 'WP G Quest Algo'
        stats_summary[1, k] = GL[1]
        k = k + 1
        stats_summary[0, k] = 'WP B Quest Algo'
        stats_summary[1, k] = GL[2]
        k = k + 1
        stats_summary[0, k] = 'WP Lum Quest Algo'
        stats_summary[1, k] = Lum_WP_output_corrected
        k = k + 1
        stats_summary[0, k] = 'WP x  Quest Algo'
        stats_summary[1, k] = Color_WP_x_output_corrected
        k = k + 1
        stats_summary[0, k] = 'WP y  Quest Algo'
        stats_summary[1, k] = Color_WP_y_output_corrected
        k = k + 1
        stats_summary[0, k] = 'WP R Seacliff Algo'
        stats_summary[1, k] = R_output_corrected
        k = k + 1
        stats_summary[0, k] = 'WP G Seacliff Algo'
        stats_summary[1, k] = G_output_corrected
        k = k + 1
        stats_summary[0, k] = 'WP B Seacliff Algo'
        stats_summary[1, k] = B_output_corrected
        k = k + 1
        stats_summary[0, k] = 'WP Lum Seacliff Algo'
        stats_summary[1, k] = Lum_output_corrected
        k = k + 1
        stats_summary[0, k] = 'WP x Seacliff Algo'
        stats_summary[1, k] = Color_x_output_corrected
        k = k + 1
        stats_summary[0, k] = 'WP y Seacliff Algo'
        stats_summary[1, k] = Color_y_output_corrected
        k = k + 1
        stats_summary[0, k] = 'WP R to DDIC'
        stats_summary[1, k] = RGB_output2DDIC[0]
        k = k + 1
        stats_summary[0, k] = 'WP G to DDIC'
        stats_summary[1, k] = RGB_output2DDIC[1]
        k = k + 1
        stats_summary[0, k] = 'WP B to DDIC'
        stats_summary[1, k] = RGB_output2DDIC[2]
        k = k + 1

        del XYZ_W,
        del Lum_WP_output, Color_WP_x_output, Color_WP_y_output, dxdy_WP_output, Lum_WP_output_corrected,
        del Color_WP_x_output_corrected, Color_WP_y_output_corrected, dxdy_WP_output_corrected,
        del Lum_255, Color_x_255, Color_y_255,
        del dxdy_corrected, dx_corrected, dy_corrected
        del XYZ_smooth, angle_arr, mask, masked_tristim, Img,
        return dict(np.transpose(stats_summary[:, 0:k]))

    def polyfit_ex(self, x, y, deg):
        c = None
        try:
            c = np.polyfit(x, y, deg)
        except np.linalg.LinAlgError as e:
            c = np.polyfit(x, y, deg)
        return c

    def rgbboresight_parametric_export(self, module_temp=30, xfilename=r'rgbboresight_x_float.bin'):
        ##Load module temperature
        ModuleTemp = module_temp
        TargetTemp = 47
        dLum_R = -0.01601
        dColor_x_R = 0
        dColor_y_R = -0.00033
        dLum_G = -0.00977
        dColor_x_G = 0.00061
        dColor_y_G = -0.00074
        dLum_B = -0.00873
        dColor_x_B = 0
        dColor_y_B = 0
        #1115 add.correction coefficients for R, G, B luminance and color offsite
        Ratio_R = 0.8980
        dColorx_R_offsite = -0.0099
        dColory_R_offsite = 0.0013
        Ratio_G = 0.9027
        dColorx_G_offsite = -0.0041
        dColory_G_offsite = -0.0022
        Ratio_B = 0.9693
        dColorx_B_offsite = 0.0034
        dColory_B_offsite = 0.0021
        cam_fov = 60
        mask_fov = 30
        row = 6001
        col = 6001
        pixel_spacing = 0.02  # Degrees per pixel
        kernel_width = 25  # Width of square smoothing kernel in pixels.
        kernel_shape = 'square'  # Use 'circle' or 'square' to change the smoothing kernel shape

        # Display center after autocollimator alignment. After alignment, the
        # cross-pattern of autocollimator is located at (0deg,0deg) field
        x_autocollimator = 0
        y_autocollimator = 0

        fig_ind = 0

        dirr = os.path.dirname(xfilename)
        fnamebase = os.path.basename(xfilename).lower().split('_x_float.bin')[0]
        filename = ['{0}_{1}_float.bin'.format(fnamebase, c) for c in ['X', 'Y', 'Z']]

        #   dir = 'K:\\RL_part\WhitePointCorrection'
        #   filename = 'normal_W255_20210306_084517_nd_0_iris_5_X_float.bin'
        # fnamebase = filename[0:np.size(filename) - 12]  # 有问题
        # filename = ['{}{}'.format(fnamebase, c) for c in ['X_float.bin', 'Y_float.bin', 'Z_float.bin']]
        primary = ['X', 'Y', 'Z']

        x_angle_arr = np.linspace(-1 * cam_fov, cam_fov, col)
        y_angle_arr = np.linspace(-1 * cam_fov, cam_fov, row)

        kernel = np.ones((kernel_width, kernel_width))
        kernel = kernel / np.sum(kernel)  # normalize

        XYZ = []
        XYZ_smooth = []
        XYZ_t = [MotAlgorithmHelper.read_image_raw(os.path.join(dirr, c)) for c in filename]

        for c in XYZ_t:
            image_in = np.rot90(c.T, 3)
            XYZ.append(image_in)
            image_in_smooth = cv2.filter2D(image_in, -1, kernel, borderType=cv2.BORDER_CONSTANT)
            XYZ_smooth.append(image_in_smooth)
            del image_in_smooth, image_in

        XYZ = np.stack(XYZ, axis=2)
        XYZ_smooth = np.stack(XYZ_smooth, axis=2)
        XYZ_1D = np.reshape(XYZ_smooth, (self._row * self._col, 3))
        XYZ_1D_ColorCorrected = self._ColorMatrix_.dot(XYZ_1D.T)
        XYZ_smooth = np.reshape(XYZ_1D_ColorCorrected.T, (self._row, self._col, 3))
        del XYZ_t, XYZ_1D, XYZ_1D_ColorCorrected,
        Y = XYZ[:, :, 1]
        # Create array of angle rings to display
        angle_arr = np.linspace(0, 2 * np.pi, 361)
        disp_fov = cam_fov
        # Create array of angle ring to show area where masking occurs
        disp_fov_ring_x = disp_fov * np.sin(angle_arr)
        disp_fov_ring_y = disp_fov * np.cos(angle_arr)
        # Create viewing masks
        col_deg_arr = np.tile(x_angle_arr, (row, 1))
        row_deg_arr = np.tile(y_angle_arr.T, (col, 1)).T
        # print(row_deg_arr.shape)
        radius_deg_arr = (col_deg_arr ** 2 + row_deg_arr ** 2) ** (1 / 2)
        mask = np.ones((row, col))
        # mask(radius_deg_arr > mask_fov) = 0#有问题
        mask[np.where(radius_deg_arr > mask_fov)] = 0

        masked_tristim = XYZ[:, :, 1] * mask

        Lumiance_thresh = 10
        Length_thresh = 10
        Img = cv2.inRange(masked_tristim, Lumiance_thresh, 255) // 255
        Img = label(Img, connectivity=2)
        statsRG = regionprops(Img)
        scentersRG = []
        sMajorAxisLengthRG = []
        sMinorAxisLengthRG = []
        statsRG = sorted(statsRG, key=lambda c: c['centroid'])
        for i, stat in enumerate(statsRG):
            if stat['MajorAxisLength'] >= Length_thresh:
                scentersRG.append(list(stat['centroid']))
                sMajorAxisLengthRG.append(stat['MajorAxisLength'])
                sMinorAxisLengthRG.append(stat['MinorAxisLength'])

        if self._verbose:
            print('num stats {0} / {1}'.format(len(scentersRG), len(statsRG)))
        num_dots = len(scentersRG)

        a = np.nonzero(np.array(sMajorAxisLengthRG) < Length_thresh)
        b = np.nonzero(np.array(sMinorAxisLengthRG) > 50)

        centroidRG = np.zeros((num_dots, 2))
        for i in range(0, num_dots):
            mlen = sMajorAxisLengthRG[i]
            d = np.floor(sMajorAxisLengthRG[i] / 2) + 1

            scenter = scentersRG[i]
            scentery = scentersRG[i][1]
            scentera = np.int(np.floor(scentersRG[i][1] - d))
            scenterb = np.int(np.floor(scentersRG[i][1] + d))
            scenterc = np.int(np.floor(scentersRG[i][0] - d))
            scenterd = np.int(np.floor(scentersRG[i][0] + d))
            im = Y[scenterc:scenterd + 1, scentera:scenterb + 1]
            [rows, cols] = im.shape
            x = np.ones((rows, 1)) * np.arange(1, cols + 1)  # # Matrix with each pixel set to its x coordinate
            y = np.arange(1, rows + 1).reshape(rows, -1) * np.ones((1, cols))  # # """" " "y  "
            area = np.sum(im)

            # hhhhh = np.float32(im)
            # print('i = {0}, col = {1}   row = {2}, area = {3}'.format(i, rows, cols, area))

            hx = np.sum(np.float32(im) * x)
            hy = np.sum(np.float32(im) * y)

            meanx = np.sum(np.float32(im) * x) / area - d - 1
            meany = np.sum(np.float32(im) * y) / area - d - 1
            centroidRG[i, 1] = int(scentersRG[i][0]) + meany
            centroidRG[i, 0] = meanx + int(scentersRG[i][1])

        masked_tristim = XYZ[:, :, 2] * mask
        Lumiance_thresh = 30
        Length_thresh = 50
        Img = cv2.inRange(masked_tristim, Lumiance_thresh, 255) // 255
        Img = label(Img, connectivity=2)
        statsB = regionprops(Img)
        scentersB = []
        sMajorAxisLengthB = []
        sMinorAxisLengthB = []

        for i, stat in enumerate(statsB):
            if stat['MajorAxisLength'] >= Length_thresh:
                scentersB.append(list(stat['centroid']))
                sMajorAxisLengthB.append(stat['MajorAxisLength'])
                sMinorAxisLengthB.append(stat['MinorAxisLength'])

        if self._verbose:
            print('num stats {0} / {1}'.format(len(scentersB), len(statsB)))
        num_dots = len(scentersB)

        a = np.nonzero(np.array(sMajorAxisLengthB) < Length_thresh)
        b = np.nonzero(np.array(sMinorAxisLengthB) > 50)

        centroidB = np.zeros((num_dots, 2))
        for i in range(0, num_dots):
            mlen = sMajorAxisLengthB[i]
            d = np.floor(sMajorAxisLengthB[i] / 2) + 1

            scenter = scentersB[i]
            scentery = scentersB[i][1]
            scentera = int(np.floor(scentersB[i][1] - d))
            scenterb = int(np.floor(scentersB[i][1] + d))
            scenterc = int(np.floor(scentersB[i][0] - d))
            scenterd = int(np.floor(scentersB[i][0] + d))
            im = Y[scenterc:scenterd + 1, scentera:scenterb + 1]
            [rows, cols] = im.shape
            x = np.ones((rows, 1)) * np.arange(1, cols + 1)  # # Matrix with each pixel set to its x coordinate
            y = np.arange(1, rows + 1).reshape(rows, -1) * np.ones((1, cols))  # # " " "  " "" " y"
            area = np.sum(im)

            # hhhhh = np.float32(im)
            # print('i = {0}, col = {1}   row = {2}, area = {3}'.format(i, rows, cols, area))

            hx = np.sum(np.float32(im) * x)
            hy = np.sum(np.float32(im) * y)

            meanx = np.sum(np.float32(im) * x) / area - d - 1
            meany = np.sum(np.float32(im) * y) / area - d - 1
            centroidB[i, 1] = int(scentersB[i][0]) + meany
            centroidB[i, 0] = meanx + int(scentersB[i][1])

        b = np.nonzero(np.array(sMinorAxisLengthRG) > 50)
        centroidColor = centroidRG[b, :].reshape((-1, 2))
        b = np.nonzero(np.array(sMinorAxisLengthB) > 50)
        centroidColor = np.vstack((centroidColor, centroidB[b, :].reshape(-1, 2)))

        Size = centroidColor.shape
        RGB = np.empty(XYZ.shape)
        RGB[:, :, 0] = 0.41847 * XYZ[:, :, 0] - 0.15866 * XYZ[:, :, 1] - 0.082835 * XYZ[:, :, 2]
        RGB[:, :, 1] = -0.09169 * XYZ[:, :, 0] + 0.25243 * XYZ[:, :, 1] - 0.015708 * XYZ[:, :, 2]
        RGB[:, :, 2] = 0.00092090 * XYZ[:, :, 0] - 0.0025498 * XYZ[:, :, 1] + 0.17860 * XYZ[:, :, 2]
        RGB = RGB / np.max(RGB)
        #     figure,imagesc(RGB)
        RGB_smooth = np.empty(XYZ_smooth.shape)
        RGB_smooth[:, :, 0] = 0.41847 * XYZ_smooth[:, :, 0] - 0.15866 * XYZ_smooth[:, :, 1] - 0.082835 * XYZ_smooth[:,
                                                                                                         :, 2]
        RGB_smooth[:, :, 1] = -0.09169 * XYZ_smooth[:, :, 0] + 0.25243 * XYZ_smooth[:, :, 1] - 0.015708 * XYZ_smooth[:,
                                                                                                          :, 2]
        RGB_smooth[:, :, 2] = 0.00092090 * XYZ_smooth[:, :, 0] - 0.0025498 * XYZ_smooth[:, :, 1] + 0.17860 * XYZ_smooth[
                                                                                                             :, :, 2]
        RGB_smooth = RGB_smooth / np.max(RGB_smooth)
        #     figure,imagesc(RGB_smooth)

        # Perform CIE and RGB color calculations and mask to disp_fov
        little_x = mask * (XYZ[:, :, 0]) / (XYZ[:, :, 0] + XYZ[:, :, 1] + XYZ[:, :, 2])
        little_x[np.isnan(little_x)] = 0
        little_y = mask * (XYZ[:, :, 1]) / (XYZ[:, :, 0] + XYZ[:, :, 1] + XYZ[:, :, 2])
        little_y[np.isnan(little_y)] = 0

        little_x_smoothed = mask * (XYZ_smooth[:, :, 0]) / (
                XYZ_smooth[:, :, 0] + XYZ_smooth[:, :, 1] + XYZ_smooth[:, :, 2])
        little_x_smoothed[np.isnan(little_x_smoothed)] = 0
        little_y_smoothed = mask * (XYZ_smooth[:, :, 1]) / (
                XYZ_smooth[:, :, 0] + XYZ_smooth[:, :, 1] + XYZ_smooth[:, :, 2])
        little_y_smoothed[np.isnan(little_y_smoothed)] = 0

        # figure,subplot(1,2,1),imagesc(little_x)caxis([0.1,0.7])
        # title('Color x')
        # subplot(1,2,2),imagesc(little_y)caxis([0.1,0.7])
        # title('Color y')
        # figure,subplot(1,2,1),imagesc(little_x_smoothed)caxis([0.1,0.7])
        # title('Color x smoothed')
        # subplot(1,2,2),imagesc(little_y_smoothed)caxis([0.1,0.7])
        # title('Color y smoothed')
        Lxy = np.empty((centroidColor.shape[0], 5))
        for i in range(0, Size[0]):
            # fix the index about center.
            y_coord = np.fix(centroidColor[i, 1]).astype(np.int)
            x_coord = np.fix(centroidColor[i, 0]).astype(np.int)

            Lxy[i, 0] = XYZ_smooth[y_coord, x_coord, 1]
            Lxy[i, 1] = little_x_smoothed[y_coord, x_coord]
            Lxy[i, 2] = little_y_smoothed[y_coord, x_coord]
            Lxy[i, 3] = centroidColor[i, 0]
            Lxy[i, 4] = centroidColor[i, 1]
        lxyshape = Lxy.shape
        LxyR = np.empty((0, lxyshape[1]))
        LxyG = np.empty((0, lxyshape[1]))
        LxyB = np.empty((0, lxyshape[1]))
        nR = 0
        nG = 0
        nB = 0
        for i in range(0, Size[0]):
            if Lxy[i, 1] > 0.6:
                LxyR = np.concatenate((LxyR, [Lxy[i, :]]))
            if Lxy[i, 2] > 0.6:
                LxyG = np.concatenate((LxyG, [Lxy[i, :]]))
            if Lxy[i, 1] < 0.2 and Lxy[i, 2] < 0.1:
                LxyB = np.concatenate((LxyB, [Lxy[i, :]]))

        LxyR_mean = np.mean(LxyR, 0)
        LxyG_mean = np.mean(LxyG, 0)
        LxyB_mean = np.mean(LxyB, 0)

        x_mean = np.mean(LxyG[:, 3])
        y_mean = np.mean(LxyG[:, 4])

        Image_center = np.array([x_mean, y_mean])
        # Image_center=np.array([3011.5,2987.5])    #test
        b = np.nonzero(np.array(sMinorAxisLengthRG) < 50)  # 有问题
        centroidDisp = centroidRG[b, :].reshape((-1, 2))
        y_points = np.nonzero(np.abs(centroidDisp[:, 0] - Image_center[0]) < 50)
        x_points = np.nonzero(np.abs(centroidDisp[:, 1] - Image_center[1]) < 50)

        x1 = centroidDisp[x_points, 0].reshape(-1) + 1
        y1 = centroidDisp[x_points, 1].reshape(-1) + 1
        c1 = self.polyfit_ex(x1.flatten(), y1.flatten(), 1)
        k1 = np.rad2deg(np.arctan(c1[0]))

        x2 = centroidDisp[y_points, 0].reshape(-1) + 1
        y2 = centroidDisp[y_points, 1].reshape(-1) + 1
        c2 = self.polyfit_ex(x2.flatten(), y2.flatten(), 1)
        k2 = np.rad2deg(np.arctan(c2[0]))

        # calculate display offsite
        x_deg = x_autocollimator
        y_deg = y_autocollimator
        # col_ind and row_ind are the x and y pixel value of the cross-pattern
        # from autocollimator in Eldim conoscope. After autocollimator alignment,
        # these value should be the center pixel of the image, which should be
        # (3001,3001) in Matlab, and (3000,3000) in Python
        col_ind = np.array(np.nonzero(np.abs(x_angle_arr - x_deg) == np.min(np.abs(x_angle_arr - x_deg))))
        row_ind = np.array(np.nonzero(np.abs(y_angle_arr - y_deg) == np.min(np.abs(y_angle_arr - y_deg))))
        Display_center = np.empty(Image_center.shape)
        Display_center[0] = 0.4563 * (Image_center[0] - col_ind[0])
        Display_center[1] = 0.4563 * (Image_center[1] - row_ind[0])

        d = 400
        rt1 = np.int(np.fix(Image_center[1]) - d)
        rt2 = np.int(np.fix(Image_center[1]) + d)
        rt3 = np.int(np.fix(Image_center[0]) - d)
        rt4 = np.int(np.fix(Image_center[0]) + d)

        # figure,imagesc(I)

        # plt.switch_backend('agg')
        #
        if self._save_plots:
            I = RGB[rt1:(rt2+1), rt3:(rt4+1), :]
            I[I <= 0] = 0
            plt.figure()
            plt.imshow(I, extent=[-d * pixel_spacing, d * pixel_spacing, d * pixel_spacing, -d * pixel_spacing])
            for i in range(0, Lxy.shape[0]):
                # different with M-Code.
                # xt = np.fix(Lxy[i, 3] - Image_center[0]) - 25
                # yt = np.fix(Lxy[i, 4] - Image_center[1])
                xt = np.fix(Lxy[i, 3] - Image_center[0]) - 45
                yt = np.fix(Lxy[i, 4] - Image_center[1]) + 25
                txt = f'{Lxy[i, 1]:.4f}\n{Lxy[i, 2]:.4f}'
                plt.text(xt * pixel_spacing, yt * pixel_spacing, txt, fontsize=8, color='white')
            plt.xlim(-d * pixel_spacing, d * pixel_spacing)
            plt.ylim(d * pixel_spacing, -d * pixel_spacing)
            plt.xlabel('X / deg')
            plt.ylabel('Y / deg')
            if not os.path.exists(os.path.join(dirr, self._exp_dir)):
                os.makedirs(os.path.join(dirr, self._exp_dir))
            plt.savefig(os.path.join(dirr, self._exp_dir, f'{fnamebase}_RGB.png'))
            plt.clf()

            plt.figure()
            plt.plot(centroidRG[:, 0], centroidRG[:, 1], 'x')
            # scentersRG should  be aligned.
            plt.plot(np.array(scentersRG)[:, 1] + 1, np.array(scentersRG)[:, 0] + 1, '.')
            plt.plot(Image_center[0] + 1, Image_center[1] + 1, 's')
            plt.plot(x1, np.polyval(c1, x1), linewidth=2)
            plt.plot(x2, np.polyval(c2, x2), linewidth=2)
            plt.xlabel('X / pixels')
            plt.ylabel('Y / pixels')
            plt.title('Center of Dots')
            plt.legend(['Dots Centroid', 'Dots Center', 'Image Center', 'X fit', 'Y fit'])

            plt.savefig(os.path.join(dirr, self._exp_dir, f'{fnamebase}_Boresight.png'))
            plt.clf()
            del I

        R_Lum = LxyR_mean[0]
        R_x = LxyR_mean[1]
        R_y = LxyR_mean[2]
        #1115 add
        R_Lum_corrected = R_Lum / Ratio_R
        R_x_corrected = R_x - dColorx_R_offsite
        R_y_corrected = R_y - dColory_R_offsite
        R_Lum_TargetTemp = R_Lum_corrected*(1+(TargetTemp-ModuleTemp)*dLum_R)
        R_x_TargetTemp = R_x_corrected+(TargetTemp-ModuleTemp)*dColor_x_R
        R_y_TargetTemp = R_y_corrected+(TargetTemp-ModuleTemp)*dColor_y_R

        G_Lum = LxyG_mean[0]
        G_x = LxyG_mean[1]
        G_y = LxyG_mean[2]
        #1115 add
        G_Lum_corrected = G_Lum / Ratio_G
        G_x_corrected = G_x - dColorx_G_offsite
        G_y_corrected = G_y - dColory_G_offsite
        G_Lum_TargetTemp = G_Lum_corrected*(1+(TargetTemp-ModuleTemp)*dLum_G)
        G_x_TargetTemp = G_x_corrected+(TargetTemp-ModuleTemp)*dColor_x_G
        G_y_TargetTemp = G_y_corrected+(TargetTemp-ModuleTemp)*dColor_y_G

        B_Lum = LxyB_mean[0]
        B_x = LxyB_mean[1]
        B_y = LxyB_mean[2]
        #1115 add
        B_Lum_corrected = B_Lum / Ratio_B
        B_x_corrected = B_x - dColorx_B_offsite
        B_y_corrected = B_y - dColory_B_offsite
        B_Lum_TargetTemp = B_Lum_corrected*(1+(TargetTemp-ModuleTemp)*dLum_B)
        B_x_TargetTemp = B_x_corrected+(TargetTemp-ModuleTemp)*dColor_x_B
        B_y_TargetTemp = B_y_corrected+(TargetTemp-ModuleTemp)*dColor_y_B

        # Output Statistics
        k = 0
        stats_summary = np.empty((2, 100), dtype=object)
        stats_summary[0, k] = 'dir'
        stats_summary[1, k] = os.path.join(dirr, fnamebase)
        k = k + 1

        stats_summary[0, k] = 'Module Temperature'
        stats_summary[1, k] = ModuleTemp
        k = k + 1
        stats_summary[0, k] = 'R_Lum'
        stats_summary[1, k] = R_Lum
        k = k + 1
        stats_summary[0, k] = 'R_x'
        stats_summary[1, k] = R_x
        k = k + 1
        stats_summary[0, k] = 'R_y'
        stats_summary[1, k] = R_y
        #1115 add
        k = k + 1
        stats_summary[0, k] = 'R_Lum_corrected'
        stats_summary[1, k] = R_Lum_corrected
        k = k + 1
        stats_summary[0, k] = 'R_x_corrected'
        stats_summary[1, k] = R_x_corrected
        k = k + 1
        stats_summary[0, k] = 'R_y_corrected'
        stats_summary[1, k] = R_y_corrected
        k = k + 1
        stats_summary[0, k] = 'R_Lum at 47C'
        stats_summary[1, k] = R_Lum_TargetTemp
        k = k + 1
        stats_summary[0, k] = 'R_x at 47C'
        stats_summary[1, k] = R_x_TargetTemp
        k = k + 1
        stats_summary[0, k] = 'R_y at 47C'
        stats_summary[1, k] = R_y_TargetTemp
        k = k + 1
        stats_summary[0, k] = 'G_Lum'
        stats_summary[1, k] = G_Lum
        k = k + 1
        stats_summary[0, k] = 'G_x'
        stats_summary[1, k] = G_x
        k = k + 1
        stats_summary[0, k] = 'G_y'
        stats_summary[1, k] = G_y
        k = k + 1
        stats_summary[0, k] = 'G_Lum_corrected'
        stats_summary[1, k] = G_Lum_corrected
        k = k + 1
        stats_summary[0, k] = 'G_x_corrected'
        stats_summary[1, k] = G_x_corrected
        k = k + 1
        stats_summary[0, k] = 'G_y_corrected'
        stats_summary[1, k] = G_y_corrected
        k = k + 1
        stats_summary[0, k] = 'G_Lum at 47C'
        stats_summary[1, k] = G_Lum_TargetTemp
        k = k + 1
        stats_summary[0, k] = 'G_x at 47C'
        stats_summary[1, k] = G_x_TargetTemp
        k = k + 1
        stats_summary[0, k] = 'G_y at 47C'
        stats_summary[1, k] = G_y_TargetTemp
        k = k + 1
        stats_summary[0, k] = 'B_Lum'
        stats_summary[1, k] = B_Lum
        k = k + 1
        stats_summary[0, k] = 'B_x'
        stats_summary[1, k] = B_x
        k = k + 1
        stats_summary[0, k] = 'B_y'
        stats_summary[1, k] = B_y
        k = k + 1
        #1115 Add
        stats_summary[0, k] = 'B_Lum_corrected'
        stats_summary[1, k] = B_Lum_corrected
        k = k + 1
        stats_summary[0, k] = 'B_x_corrected'
        stats_summary[1, k] = B_x_corrected
        k = k + 1
        stats_summary[0, k] = 'B_y_corrected'
        stats_summary[1, k] = B_y_corrected
        k = k + 1
        stats_summary[0, k] = 'B_Lum at 47C'
        stats_summary[1, k] = B_Lum_TargetTemp
        k = k + 1
        stats_summary[0, k] = 'B_x at 47C'
        stats_summary[1, k] = B_x_TargetTemp
        k = k + 1
        stats_summary[0, k] = 'B_y at 47C'
        stats_summary[1, k] = B_y_TargetTemp
        k = k + 1
        stats_summary[0, k] = 'DispCen_x_cono'
        stats_summary[1, k] = Image_center[0] + 1
        k = k + 1
        stats_summary[0, k] = 'DispCen_y_cono'
        stats_summary[1, k] = Image_center[1] + 1
        k = k + 1
        stats_summary[0, k] = 'DispCen_x_display'
        stats_summary[1, k] = Display_center[0]
        k = k + 1
        stats_summary[0, k] = 'DispCen_y_display'
        stats_summary[1, k] = Display_center[1]
        k = k + 1
        stats_summary[0, k] = 'Disp_Rotate_x'
        stats_summary[1, k] = k1
        k = k + 1
        del XYZ, XYZ_smooth, Img, RGB, RGB_smooth
        del B_Lum, B_Lum_TargetTemp, B_x_TargetTemp, B_x, B_y_TargetTemp, B_y
        del Y, little_y, little_x, little_x_smoothed, little_y_smoothed
        del mask, masked_tristim, radius_deg_arr, row_deg_arr, x_angle_arr, y_angle_arr
        return dict(np.transpose(stats_summary[:, 0:k]))


def print_to_console(self, msg):
    pass


if __name__ == "__main__":
    import sys
    sys.path.append("../../")
    import types
    import station_config

    import hardware_station_common.operator_interface.operator_interface as operator_interface
    import csv

    x = np.arange(20, 90.1, 10)
    y = np.arange(0, 20.1, 5)
    z = np.array([[8.9, 10.32, 11.3, 12.5, 13.9, 15.3, 17.8, 21.3],
                  [8.7, 10.8, 11, 12.1, 13.2, 14.8, 16.55, 20.8],
                  [8.3, 9.65, 10.88, 12, 13.2, 14.6, 16.4, 20.5],
                  [8.1, 9.4, 10.7, 11.9, 13.1, 14.5, 16.2, 20.3],
                  [8.1, 9.2, 10.8, 12, 13.2, 14.8, 16.9, 20.9]])

    xi = np.arange(20, 91)
    yi = np.arange(0, 21)
    zi = MotAlgorithmHelper.interp2(x, y, z, xi, yi)

    w_bin_re = '*_W255_*_X_float.bin'
    r_bin_re = '*_R255_*_X_float.bin'
    g_bin_re = '*_G255_*_X_float.bin'
    b_bin_re = '*_B255_*_X_float.bin'
    br_bin_re = '*_RGBBoresight_*_X_float.bin'
    wd_bin_re = '*_WhiteDot_*_X_float.bin'
    COLORMATRIX_COEFF = [[0.9941, -0.0076, -0.0066], [0.0009, 0.9614, -0.0025], [-0.0021, 0.0020, 0.9723]]
    aa = MotAlgorithmHelper(COLORMATRIX_COEFF, is_verbose=False, save_plots=True)
    raw_data_dir = r"c:\ShareData\Oculus_RawData\003_seacliff_mot-06_20210811-093524"
    bins = tuple([glob.glob(os.path.join(raw_data_dir, c))
                  for c in [w_bin_re, r_bin_re, g_bin_re, b_bin_re, br_bin_re, wd_bin_re]])

    w_bin, r_bin, g_bin, b_bin, br_bin, wd_bin = tuple([c[0] if len(c) > 0 else None for c in bins])

    m_temp = {
        'W255': 28.9,
        'R255': 29.2,
        'G255': 29.4,
        'B255': 29.8,
        'RGBBoresight': 29.9,
        'WhiteDot': 30.3,
    }
    start_time = time.time()
    end_time = []
    w255_result = aa.color_pattern_parametric_export_W255(
        xfilename=os.path.join(raw_data_dir, w_bin), ModuleLR='R', module_temp=m_temp['W255'])
    end_time.append(time.time())
    # r255_result = aa.color_pattern_parametric_export_RGB('r', module_temp=m_temp['R255'],
    #                                                      xfilename=os.path.join(raw_data_dir, r_bin))
    # end_time.append(time.time())
    # g255_result = aa.color_pattern_parametric_export_RGB('g', module_temp=m_temp['G255'],
    #                                                      xfilename=os.path.join(raw_data_dir, g_bin))
    # end_time.append(time.time())
    # b255_result = aa.color_pattern_parametric_export_RGB('b', module_temp=m_temp['B255'],
    #                                                      xfilename=os.path.join(raw_data_dir, b_bin))
    # end_time.append(time.time())
    boresight_result = aa.rgbboresight_parametric_export(module_temp=m_temp['RGBBoresight'],
        xfilename=os.path.join(raw_data_dir, br_bin))
    end_time.append(time.time())

    # np.save('data.npy', [w255_result, r255_result, g255_result, b255_result, boresight_result])
    # w255_result, r255_result, g255_result, b255_result, boresight_result = np.load('data.npy', allow_pickle=True)

    # distortion_result = aa.distortion_centroid_parametric_export(
    #     filename=os.path.join(raw_data_dir, gd_bin), module_temp=m_temp['GreenDistortion'])

    XYZ_W = aa.white_dot_pattern_w255_read(os.path.join(raw_data_dir, w_bin))
    end_time.append(time.time())
    gl_whitedot = aa.calc_gl_for_brightdot(w255_result, boresight_result, module_temp=m_temp['WhiteDot'])
    whitedot_result = aa.white_dot_pattern_parametric_export(XYZ_W,
                        gl_whitedot['GL'], gl_whitedot['x_w'], gl_whitedot['y_w'], temp_w=m_temp['W255'],
                        module_temp=m_temp['WhiteDot'],
                        xfilename=os.path.join(raw_data_dir, wd_bin))
    end_time.append(time.time())
    raw_data = [w255_result, boresight_result, whitedot_result]
    if not os.path.exists(os.path.join(raw_data_dir, 'exp')):
        os.makedirs(os.path.join(raw_data_dir, 'exp'))
    with open(os.path.join(raw_data_dir, 'exp', f'export.txt'), 'a', newline='') as f:
        for idx, raw in enumerate(raw_data):
            f.write('+'*10 + '\n')
            data = [f'{k}, {v}' for k, v in raw.items()]
            f.write('\n'.join(data))
            f.write('\n' + '-'*10 + '\n'*3)
    for idx, tm in enumerate(end_time):
        print(f'IDX: {idx}, Elapse: {(tm-start_time)}')
