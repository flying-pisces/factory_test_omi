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
from skimage import measure
import os
import scipy
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

    def __init__(self, is_verbose=False):
        self._verbose = is_verbose
        self._noise_thresh = 0.05  # Percent of Y sum to exclude from color plots (use due to color calc noise in dim part of image)
        self._color_thresh = 0.01  # Thresh for color uniformity
        self._lum_thresh = 0.8  # Thresh for brightness uniformity
        self._fixed_chroma_clims = 0  # If 1, then chroma plots range [0 1].  Otherwise auto scale
        self._disp_fov = 60  # Maximum FOV to display.  Use for masking.
        self._chromaticity_fov = [10, 20, 30]  # Limit FOV for chromaticity plot in degrees
        self._disp_ring_spacing = 10  # Spacing, in deg, of rings overlaid on plots
        self._save_plots = 1  # Save output plots as PNG and SVG/EMF into same dirr as file
        # ----- Begin code -----#
        self._cam_fov = 60
        self._row = 6001
        self._col = 6001
        self._pixel_spacing = 0.02  # Degrees per pixel

        self._mask_fov = 30
        self._x_autocollimator = 0
        self._y_autocollimator = 0
        self._fig_ind = 0
        np.seterr(invalid='ignore')

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

    def distortion_centroid_parametric_export(self, filename=r'/normal_GreenDistortion_X_float.bin'):
        dirr = os.path.dirname(filename)

        x_angle_arr = np.linspace(-1 * self._cam_fov, self._cam_fov, self._col).reshape(-1, self._col)
        y_angle_arr = np.linspace(-1 * self._cam_fov, self._cam_fov, self._row).reshape(-1, self._col)
        #
        image_in = None
        with open(filename, 'rb') as f:
            frame3 = np.frombuffer(f.read(), dtype=np.float32)
            image_in = frame3.reshape(self._col, self._row).T
            image_in = cv2.rotate(image_in, 0)
        if self._verbose:
            print(f'Read bin files named {os.path.basename(filename)}\n')

        XYZ = image_in
        CXYZ = image_in
        angle_arr = np.linspace(0, 2 * np.pi, 361)

        disp_fov = self._cam_fov

        disp_fov_ring_x = disp_fov * np.sin(angle_arr)
        disp_fov_ring_y = disp_fov * np.cos(angle_arr)

        col_deg_arr = np.tile(x_angle_arr, (self._row, 1))
        row_deg_arr = np.tile(y_angle_arr.T, (1, self._col))

        radius_deg_arr = (col_deg_arr ** 2 + row_deg_arr ** 2) ** (1 / 2)
        mask = np.ones((self._row, self._col))
        # mask[np.where(radius_deg_arr > disp_fov)] = 0
        mask[np.where(radius_deg_arr > self._mask_fov)] = 0

        masked_tristim = XYZ * mask
        max_XYZ_val = np.max(masked_tristim)

        Lumiance_thresh = 10
        axis_length_thresh = 10
        if self._verbose:
            print(XYZ.shape, np.max(XYZ))

        # label_image = np.uint8(np.where(XYZ > Lumiance_thresh,255,0))
        # XYZ = cv2.blur(XYZ,(3,3))
        label_image = cv2.inRange(masked_tristim, 10, 255) // 255

        aa_image = np.zeros((self._row + 1, self._col + 1), dtype=np.int)
        aa_image[1:, 1:] = label_image
        label_image = aa_image

        bb_image = np.zeros((self._row + 1, self._col + 1), dtype=np.float)
        bb_image[1:, 1:] = CXYZ
        CXYZ = bb_image

        label_image = measure.label(label_image, connectivity=2)
        stats = measure.regionprops(label_image)
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

        c1 = np.polyfit(x1, y1, 1)
        k1 = np.degrees(np.arctan(c1[0]))

        x2 = centroid[y_points, 0].reshape(-1)
        y2 = centroid[y_points, 1].reshape(-1)

        c2 = np.polyfit(x2, y2, 1)
        k2 = np.degrees(np.arctan(c2[0]))
        #
        # plt.plot(centroid[:, 1], centroid[:, 0], 'x')
        # plt.plot(image_center[1], image_center[0], 's')
        # plt.plot(x1, np.polyval(c1, x1))
        # plt.plot(x2, np.polyval(c2, x2))
        # plt.xlabel('X / pixels')
        # plt.ylabel('Y / pixels')
        # plt.title('Center of Dots')
        #
        # Data = [filename[-11:], max_XYZ_val, num_dots, image_center[1], image_center[0], k1, k2]
        # end = time.time()
        # print(end - start)
        # print('filename:',filename)
        # print('final Data', Data)
        # plt.show()
        # with open('DATA.csv', 'a+', encoding='utf-8') as f:
        #     csv_writer = csv.writer(f)
        #     csv_writer.writerow(Data)
        # return Data

        x_deg = self._x_autocollimator
        y_deg = self._y_autocollimator
        # col_ind and row_ind are the x and y pixel value of the cross-pattern
        # from autocollimator in Eldim conoscope. After autocollimator alignment,
        # these value should be the center pixel of the image, which should be
        # (3001,3001) in Matlab, and (3000,3000) in Python
        col_ind = np.nonzero(np.abs(x_angle_arr - x_deg) == np.min(np.abs(x_angle_arr - x_deg)))[1][0]
        row_ind = np.nonzero(np.abs(y_angle_arr - y_deg) == np.min(np.abs(y_angle_arr - y_deg)))[1][0]
        display_center = [None, None]
        display_center[0] = 0.4563 * (image_center[0] - (col_ind + 1))
        display_center[1] = 0.4563 * (image_center[1] - (row_ind + 1))

        k = 0
        stats_summary = np.empty((2, 9), dtype=object)
        # stats_summary = cell(2,1)
        stats_summary[0, k] = dirr
        stats_summary[1, k] = os.path.join(dirr, os.path.basename(filename))
        k = k + 1
        stats_summary[0, k] = 'Max Lum'
        stats_summary[1, k] = max_XYZ_val
        k = k + 1
        stats_summary[0, k] = 'Number Of Dots'
        stats_summary[1, k] = num_dots
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
        # del XYZ, CXYZ
        del XYZ, CXYZ, x_angle_arr, y_angle_arr, image_in, col_deg_arr, row_deg_arr, radius_deg_arr, mask
        del masked_tristim, label_image, stats, bb, centroid, x_points, y_points, image_center

        return dict(zip(list(stats_summary[0]), list(stats_summary[1])))

    @staticmethod
    def read_image_raw(bin_filename):
        I = None
        with open(bin_filename, 'rb') as fin:
            I = np.frombuffer(fin.read(), dtype=np.float32)
        image_in = np.reshape(I, (6001, 6001))
        # Z = Z'        #Removed for viewing to match DUT orientation
        del I
        return image_in

    def color_pattern_parametric_export(self, xfilename=r'W255_X_float.bin',
                                        brightness_statistics=True,
                                        color_uniformity=True, multi_process=False):
        dirr = os.path.dirname(xfilename)
        fnamebase = os.path.basename(xfilename).lower().split('_x_float.bin')[0]
        filename = ['{0}_{1}_float.bin'.format(fnamebase, c) for c in ['X', 'Y', 'Z']]

        x_angle_arr = np.linspace(-1 * self._cam_fov, self._cam_fov, self._col).reshape(-1, self._col)
        y_angle_arr = np.linspace(-1 * self._cam_fov, self._cam_fov, self._row).reshape(-1, self._row)

        # xyz_array = []
        # for i in range(0, 3):
        #     with open(os.path.join(dirr, filename[i]), 'rb') as fin:
        #         I = np.frombuffer(fin.read(), dtype=np.float32)
        #     image_in = np.reshape(I, (self._col, self._row))
        #     # Z = Z'        #Removed for viewing to match DUT orientation
        #     image_in = np.flip(image_in.T, 1)  # Implement flip for viewing to match DUT orientation
        #     # image_in = cv2.filter2D(image_in, -1, kernel, borderType=cv2.BORDER_CONSTANT)
        #     xyz_array.append(image_in)
        file_names = [os.path.join(dirr, c) for c in filename]
        if multi_process:
            pool = mp.Pool(mp.cpu_count())
            XYZ_t = pool.map(MotAlgorithmHelper.read_image_raw, file_names)
            pool.close()
        else:
            XYZ_t = [MotAlgorithmHelper.read_image_raw(c) for c in file_names]
        if self._verbose:
            print(f'Read bin files named {fnamebase}\n')
        XYZ = []
        for image_in in XYZ_t:
            image_in = cv2.rotate(image_in, 0)  # Implement flip for viewing to match DUT orientation
            image_in = cv2.filter2D(image_in, -1, MotAlgorithmHelper._kernel, borderType=cv2.BORDER_CONSTANT)
            XYZ.append(image_in)
        del XYZ_t

        # cv2.namedWindow('img',0)
        # cv2.imshow('img',image_in)
        # cv2.waitKey(1000)
        # path = 'XYZ.pkl'
        # f = open(path, 'wb')
        # pickle.dump(XYZ, f)
        # f.close()

        # f1 = open(path, 'rb')
        # XYZ = pickle.load(f1)
        # print(len(XYZ))

        ## Save parametric data
        # Create viewing masks
        col_deg_arr = np.tile(x_angle_arr, (self._row, 1))
        row_deg_arr = np.tile(y_angle_arr.T, (1, self._col))
        radius_deg_arr = (col_deg_arr ** 2 + row_deg_arr ** 2) ** (1 / 2)
        mask = np.ones((self._row, self._col))
        mask[radius_deg_arr > self._disp_fov] = 0
        chromaticity_mask = np.ones((self._row, self._col, 3))  # 3 field mask defined by chromaticity_fov
        chromaticity_mask1 = np.ones((self._row, self._col))
        chromaticity_mask1[radius_deg_arr > self._chromaticity_fov[0]] = 0
        chromaticity_mask[:, :, 0] = chromaticity_mask1
        chromaticity_mask2 = np.ones((self._row, self._col))
        chromaticity_mask2[radius_deg_arr > self._chromaticity_fov[1]] = 0
        chromaticity_mask[:, :, 1] = chromaticity_mask2
        chromaticity_mask3 = np.ones((self._row, self._col))
        chromaticity_mask3[radius_deg_arr > self._chromaticity_fov[2]] = 0
        chromaticity_mask[:, :, 2] = chromaticity_mask3
        cam_fov_mask = np.ones((self._row, self._col))
        cam_fov_mask[radius_deg_arr > self._cam_fov] = 0

        # Perform CIE and RGB color calculations and mask to disp_fov
        u_prime_smoothed = mask * (4 * XYZ[0]) / (XYZ[0] + 15 * XYZ[1] + 3 * XYZ[2])
        u_prime_smoothed[np.isnan(u_prime_smoothed)] = 0
        v_prime_smoothed = mask * (9 * XYZ[1]) / (XYZ[0] + 15 * XYZ[1] + 3 * XYZ[2])
        v_prime_smoothed[np.isnan(v_prime_smoothed)] = 0

        tmp_XYZ = XYZ[1] * mask
        XYZ_mask = np.zeros((self._row, self._col))
        XYZ_mask[tmp_XYZ > self._noise_thresh * np.max(tmp_XYZ)] = 1

        u_prime_smoothed_masked = u_prime_smoothed * XYZ_mask
        v_prime_smoothed_masked = v_prime_smoothed * XYZ_mask
        # Find max value location for brightness
        masked_tristim = XYZ[1] * mask
        max_Y_val = np.max(masked_tristim)
        [rowsOfMaxes, colsOfMaxes] = np.nonzero(masked_tristim == max_Y_val)
        rowsOfMaxes = rowsOfMaxes[0]
        colsOfMaxes = colsOfMaxes[0]
        max_Y_xloc_deg = x_angle_arr[0, colsOfMaxes]
        max_Y_yloc_deg = y_angle_arr[0, rowsOfMaxes]
        max_Y_xloc_pix = colsOfMaxes
        max_Y_yloc_pix = rowsOfMaxes

        # Output Statistics
        k = 0
        x_deg = 0
        y_deg = 0
        col_ind_onaxis = np.nonzero(np.abs(x_angle_arr - x_deg) == np.min(np.abs(x_angle_arr - x_deg)))[1][0]
        row_ind_onaxis = np.nonzero(np.abs(y_angle_arr - y_deg) == np.min(np.abs(y_angle_arr - y_deg)))[1][0]
        # On-axis and off-axis brightness and color values
        x_sample_arr = [0, -1 * self._chromaticity_fov[2], -1 * self._chromaticity_fov[1],
                        -1 * self._chromaticity_fov[0],
                        self._chromaticity_fov[0],
                        self._chromaticity_fov[1], self._chromaticity_fov[2], 0, 0, 0, 0, 0, 0]
        y_sample_arr = [0, 0, 0, 0, 0, 0, 0, -1 * self._chromaticity_fov[2], -1 * self._chromaticity_fov[1],
                        -1 * self._chromaticity_fov[0],
                        self._chromaticity_fov[0], self._chromaticity_fov[1], self._chromaticity_fov[2]]

        stats_summary = np.empty((2, 3 * len(x_sample_arr) + 1 + 12 + 20), dtype=object)
        stats_summary[0, k] = dirr
        stats_summary[1, k] = dirr + fnamebase
        k = k + 1

        for i in range(0, len(x_sample_arr)):
            x_deg = x_sample_arr[i]
            y_deg = y_sample_arr[i]
            col_ind = np.nonzero(np.abs(x_angle_arr - x_deg) == np.min(np.abs(x_angle_arr - x_deg)))[1][0]
            row_ind = np.nonzero(np.abs(y_angle_arr - y_deg) == np.min(np.abs(y_angle_arr - y_deg)))[1][0]
            stats_summary[0, k] = 'Lum(x=' + str(x_angle_arr[0, col_ind]) + 'deg,y=' + str(
                y_angle_arr[0, row_ind]) + 'deg)'
            stats_summary[1, k] = XYZ[1][row_ind][col_ind]
            k = k + 1
            stats_summary[0, k] = 'u\'(x=' + str(x_angle_arr[0, col_ind]) + 'deg,y=' + str(
                y_angle_arr[0, row_ind]) + 'deg)'
            stats_summary[1, k] = u_prime_smoothed_masked[row_ind, col_ind]
            k = k + 1
            stats_summary[0, k] = 'v\'(x=' + str(x_angle_arr[0, col_ind]) + 'deg,y=' + str(
                y_angle_arr[0, row_ind]) + 'deg)'
            stats_summary[1, k] = v_prime_smoothed_masked[row_ind, col_ind]
            k = k + 1
            del col_ind, row_ind
        if brightness_statistics:
            # Max brightness
            stats_summary[0, k] = 'Max Lum'
            stats_summary[1, k] = max_Y_val
            k = k + 1
            stats_summary[0, k] = 'Max Lum u\''
            stats_summary[1, k] = u_prime_smoothed_masked[max_Y_yloc_pix, max_Y_xloc_pix]
            k = k + 1
            stats_summary[0, k] = 'Max Lum v\''
            stats_summary[1, k] = v_prime_smoothed_masked[max_Y_yloc_pix, max_Y_xloc_pix]
            k = k + 1
            stats_summary[0, k] = 'Max Lum x(deg)'
            stats_summary[1, k] = max_Y_xloc_deg
            k = k + 1
            stats_summary[0, k] = 'Max Lum y(deg)'
            stats_summary[1, k] = max_Y_yloc_deg
            k = k + 1

            # Brightness uniformity
            Y = XYZ[1]
            for i in range(0, 3):
                tmp_chromaticity_mask = chromaticity_mask[:, :, i]
                tmp = Y[tmp_chromaticity_mask == 1]
                meanLum = np.mean(tmp)
                deltaLum = np.max(tmp) - np.min(tmp)
                stdLum = np.std(tmp, ddof=1)
                percentLum_onaxis = np.sum(tmp > self._lum_thresh * Y[row_ind_onaxis, col_ind_onaxis]) / len(tmp)
                percentLum_max = np.sum(tmp > self._lum_thresh * max_Y_val) / len(tmp)
                # save data to cell
                stats_summary[0, k] = 'Lum_mean_' + str(self._chromaticity_fov[i]) + 'deg'
                stats_summary[1, k] = meanLum
                k = k + 1
                stats_summary[0, k] = 'Lum_delta_' + str(self._chromaticity_fov[i]) + 'deg'
                stats_summary[1, k] = deltaLum
                k = k + 1
                stats_summary[0, k] = 'Lum_SSR_' + str(self._chromaticity_fov[i]) + 'deg'
                stats_summary[1, k] = stdLum
                k = k + 1
                stats_summary[0, k] = 'Lum_Ratio>' + str(self._lum_thresh) + 'OnAxisLum_' + str(
                    self._chromaticity_fov[i]) + 'deg'
                stats_summary[1, k] = percentLum_onaxis
                k = k + 1
                stats_summary[0, k] = 'Lum_Ratio>' + str(self._lum_thresh) + 'MaxLum_' + str(
                    self._chromaticity_fov[i]) + 'deg'
                stats_summary[1, k] = percentLum_max
                k = k + 1
                del tmp_chromaticity_mask
            del Y
        if color_uniformity:
            # color uniformity
            for i in range(0, 3):
                tmp_chromaticity_mask = chromaticity_mask[:, :, i]
                tmpu_prime = u_prime_smoothed_masked[tmp_chromaticity_mask == 1]
                tmpv_prime = v_prime_smoothed_masked[tmp_chromaticity_mask == 1]
                tmpdeltau_prime = tmpu_prime - u_prime_smoothed_masked[row_ind_onaxis, col_ind_onaxis]
                tmpdeltav_prime = tmpv_prime - v_prime_smoothed_masked[row_ind_onaxis, col_ind_onaxis]
                tmpdeltauv_prime = np.sqrt(tmpdeltau_prime ** 2 + tmpdeltav_prime ** 2)
                meanu_prime = np.mean(tmpu_prime)
                meanv_prime = np.mean(tmpv_prime)
                percentuv = np.sum(tmpdeltauv_prime < self._color_thresh) / len(tmpdeltauv_prime)
                deltauv = np.max(tmpdeltauv_prime)
                # save data to cell
                stats_summary[0, k] = 'u\'_mean_' + str(self._chromaticity_fov[i]) + 'deg'
                stats_summary[1, k] = meanu_prime
                k = k + 1
                stats_summary[0, k] = 'v\'_mean_' + str(self._chromaticity_fov[i]) + 'deg'
                stats_summary[1, k] = meanv_prime
                k = k + 1
                stats_summary[0, k] = 'u\'v\'_delta_to_OnAxis_' + str(self._chromaticity_fov[i]) + 'deg'
                stats_summary[1, k] = deltauv
                k = k + 1
                stats_summary[0, k] = 'u\'v\'_delta<' + str(self._color_thresh) + '_Ratio_' + str(
                    self._chromaticity_fov[i]) + 'deg'
                stats_summary[1, k] = percentuv
                k = k + 1
                del tmpv_prime, tmpu_prime, tmp_chromaticity_mask
        # del XYZ
        del XYZ, filename, x_angle_arr, y_angle_arr, file_names, col_deg_arr, row_deg_arr, radius_deg_arr
        del chromaticity_mask, chromaticity_mask1, chromaticity_mask2, chromaticity_mask3,
        del cam_fov_mask, u_prime_smoothed, v_prime_smoothed, tmp_XYZ, XYZ_mask, u_prime_smoothed_masked,
        del v_prime_smoothed_masked, masked_tristim, max_Y_xloc_deg, max_Y_yloc_deg,
        del col_ind_onaxis, row_ind_onaxis, x_sample_arr, y_sample_arr

        return dict(zip(stats_summary[0, 0:k], stats_summary[1, 0:k]))

    @staticmethod
    def calc_gl_for_brightdot(np_luv):
        x = 9 * np_luv[:, 1] / (6 * np_luv[:, 1] - 16 * np_luv[:, 2] + 12)
        y = 4 * np_luv[:, 2] / (6 * np_luv[:, 1] - 16 * np_luv[:, 2] + 12)
        Y_rgb_measure = np_luv[:, 0][1:]
        x_w, y_w, Y_w = 0.3127, 0.329, np_luv[0, 0]
        x_r, y_r = x[1], y[1]
        x_g, y_g = x[2], y[2]
        x_b, y_b = x[3], y[3]
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
        gray_levels = np.round(np.power(Lum_after / Lum_before, 1 / Gamma) * 255)
        return [int(c) for c in gray_levels]

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
        return XYZ

    def white_dot_pattern_parametric_export(self, XYZ_W, GL, xfilename=r'WhiteDot_X_float.bin', export_csv=False, n_dots=15):
        # ----- Begin code -----#
        cam_fov = 60
        mask_fov = 30
        row = 6001
        col = 6001
        pixel_spacing = 0.02  # Degrees per pixel
        kernel_width = 20  # Width of square smoothing kernel in pixels.
        kernel_shape = 'square'  # Use 'circle' or 'square' to change the smoothing kernel shape
        x_w = 0.3127  # color x for D65
        y_w = 0.3290  # color y for D65
        # XYZ_W = np.ones((3, 3, 3))
        Lum_W = XYZ_W[:, :, 1]
        Color_x_W = XYZ_W[:, :, 0] / (XYZ_W[:, :, 0] + XYZ_W[:, :, 1] + XYZ_W[:, :, 2])
        Color_y_W = XYZ_W[:, :, 1] / (XYZ_W[:, :, 0] + XYZ_W[:, :, 1] + XYZ_W[:, :, 2])
        # LumRatio_W = Lum_W(3001,3001)./Lum_W
        # dColor_x_W = Color_x_W-Color_x_W(3001,3001)
        # dColor_y_W = Color_y_W-Color_y_W(3001,3001)
        ##
        # Read in the WhiteDot image
        dirr = os.path.dirname(xfilename)
        fnamebase = os.path.basename(xfilename).lower().split('_x_float.bin')[0]
        filename = ['{0}_{1}_float.bin'.format(fnamebase, c) for c in ['X', 'Y', 'Z']]

        primary = ['X', 'Y', 'Z']

        x_angle_arr = np.linspace(-1 * cam_fov, cam_fov, col)
        y_angle_arr = np.linspace(-1 * cam_fov, cam_fov, row)

        kernel = np.ones((kernel_width, kernel_width))

        kernel = kernel / np.sum(kernel)  # normalize
        XYZ = []
        XYZ_t = [MotAlgorithmHelper.read_image_raw(os.path.join(dirr, c)) for c in filename]
        for image_in in XYZ_t:
            image_in = np.rot90(image_in.T, 3)
            image_in = np.flip(image_in, 0)
            # image_in = cv2.rotate(image_in, 0)

            XYZ.append(image_in)
        del XYZ_t
        XYZ = np.stack(XYZ, axis=2)
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

        masked_tristim = Y * mask
        max_XYZ_val = np.max(masked_tristim)

        Lumiance_thresh = 10
        Length_thresh = 10
        Img = cv2.inRange(masked_tristim, 10, 255) // 255
        # figure,imagesc(x_angle_arr,y_angle_arr,Img)
        Img = measure.label(Img, connectivity=2)
        stats = measure.regionprops(Img)
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
        R_output = []

        if Size[0] == n_dots ** 2:
            Lum = np.empty((n_dots ** 2,), dtype=np.object)
            Color_x = np.empty(Lum.shape, dtype=np.object)
            Color_y = np.empty(Lum.shape, dtype=np.object)
            Color_x_corrected = np.empty(Lum.shape, dtype=np.object)
            Lum_corrected = np.empty(Lum.shape, dtype=np.object)
            Color_y_corrected = np.empty(Lum.shape, dtype=np.object)

            for i in range(0, n_dots**2):
                d = 25
                # np.trunc the index about center.
                cx1 = int(np.trunc(centroid[i, 1] - d))
                cx2 = int(np.trunc(centroid[i, 1] + d)) + 1
                cy1 = int(np.trunc(centroid[i, 0] - d))
                cy2 = int(np.trunc(centroid[i, 0] + d)) + 1
                im = XYZ[cx1:cx2, cy1:cy2, :]

                X_center = cv2.filter2D(im[:, :, 0], -1, kernel, borderType=cv2.BORDER_CONSTANT)
                Y_center = cv2.filter2D(im[:, :, 1], -1, kernel, borderType=cv2.BORDER_CONSTANT)
                Z_center = cv2.filter2D(im[:, :, 2], -1, kernel, borderType=cv2.BORDER_CONSTANT)
                #
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
            Lum2Dq = MotAlgorithmHelper.interp2(XX, YY, Lum2D, xq, yq)

            Color_x_2Dq = MotAlgorithmHelper.interp2(XX, YY, Color_x_2D, xq, yq)
            Color_y_2Dq = MotAlgorithmHelper.interp2(XX, YY, Color_y_2D, xq, yq)
            Lum2Dq_corrected = MotAlgorithmHelper.interp2(XX, YY, Lum2D_corrected, xq, yq)
            Color_x_2Dq_corrected = MotAlgorithmHelper.interp2(XX, YY, Color_x_2D_corrected, xq, yq)
            Color_y_2Dq_corrected = MotAlgorithmHelper.interp2(XX, YY, Color_y_2D_corrected, xq, yq)

            dx = Color_x_2Dq - x_w
            dy = Color_y_2Dq - y_w
            dxdy = np.sqrt(dx ** 2 + dy ** 2)
            dx_corrected = Color_x_2Dq_corrected - x_w
            dy_corrected = Color_y_2Dq_corrected - y_w
            dxdy_corrected = np.sqrt(dx_corrected ** 2 + dy_corrected ** 2)

            # GL = [100, 100, 100]
            if np.min(GL) < 255 - (n_dots - 1) * 2:
                Lum_WP_output = np.nan
                Color_WP_x_output = np.nan
                Color_WP_y_output = np.nan
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
                Lum_WP_output = Lum2Dq[row, col]
                Color_WP_x_output = Color_x_2Dq[row, col]
                Color_WP_y_output = Color_y_2Dq[row, col]
                dxdy_WP_output = np.sqrt((Color_WP_x_output - x_w) ** 2 + (Color_WP_y_output - y_w) ** 2)
                Lum_WP_output_corrected = Lum2Dq_corrected[row, col]
                Color_WP_x_output_corrected = Color_x_2Dq_corrected[row, col]
                Color_WP_y_output_corrected = Color_y_2Dq_corrected[row, col]
                dxdy_WP_output_corrected = np.sqrt(
                    (Color_WP_x_output_corrected - x_w) ** 2 + (Color_WP_y_output_corrected - y_w) ** 2)

            R_output, G_output, B_output = np.empty((5,), np.object),  np.empty((5,), np.object),  np.empty((5,), np.object)
            Lum_output = np.empty((5,), np.object)
            Color_x_output = np.empty((5,), np.object)
            Color_y_output = np.empty((5,), np.object)
            dxdy_output_corrected = np.empty((5,), np.object)
            dxdy_output = np.empty((5,), np.object)
            Color_x_output = np.empty((5,), np.object)

            min_ext = lambda data: (np.min(data), np.argmin(data))
            for i in range(0, 1):
                min_val, idx = min_ext(dxdy)

                row, col = MotAlgorithmHelper.ind2sub(dxdy.shape, idx)
                row = row[0]
                col = col[0]
                if GL[2] == 255:
                    R_output[i] = Xq[row, col]
                    G_output[i] = Yq[row, col]
                    B_output[i] = 255
                elif GL[1] == 255:
                    R_output[i] = Xq[row, col]
                    G_output[i] = 255
                    B_output[i] = Yq[row, col]
                else:
                    R_output[i] = 255
                    G_output[i] = Xq[row, col]
                    B_output[i] = Yq[row, col]

                Lum_output[i] = Lum2Dq[row, col]
                Color_x_output[i] = Color_x_2Dq[row, col]
                Color_y_output[i] = Color_y_2Dq[row, col]
                dxdy_output[i] = dxdy[row, col]
                dxdy[row, col] = 1

            R_output_corrected = np.empty((5,), np.object)
            G_output_corrected = np.empty((5,), np.object)
            B_output_corrected = np.empty((5,), np.object)
            Lum_output_corrected = np.empty((5,), np.object)
            Color_x_output_corrected = np.empty((5,), np.object)
            Color_y_output_corrected = np.empty((5,), np.object)

            for i in range(0, 1):
                min_val, idx = min_ext(dxdy_corrected)
                row, col = MotAlgorithmHelper.ind2sub(dxdy_corrected.shape, idx)
                row = row[0]
                col = col[0]
                if GL[2] == 255:
                    R_output_corrected[i] = Xq[row, col]
                    G_output_corrected[i] = Yq[row, col]
                    B_output_corrected[i] = 255
                elif GL[1] == 255:
                    R_output_corrected[i] = Xq[row, col]
                    G_output_corrected[i] = 255
                    B_output_corrected[i] = Yq[row, col]
                else:
                    R_output_corrected[i] = 255
                    G_output_corrected[i] = Xq[row, col]
                    B_output_corrected[i] = Yq[row, col]

                Lum_output_corrected[i] = Lum2Dq_corrected[row, col]
                Color_x_output_corrected[i] = Color_x_2Dq_corrected[row, col]
                Color_y_output_corrected[i] = Color_y_2Dq_corrected[row, col]
                dxdy_output_corrected[i] = dxdy_corrected[row, col]
                dxdy_corrected[row, col] = 1

        # Output Statistics
        k = 0
        stats_summary = np.empty((2, 82), dtype=object)
        stats_summary[0, k] = 'dir'
        stats_summary[1, k] = os.path.join(dirr, fnamebase)
        k = k + 1

        stats_summary[0, k] = 'WP0 R'
        stats_summary[1, k] = GL[0]
        k = k + 1
        stats_summary[0, k] = 'WP0 G'
        stats_summary[1, k] = GL[1]
        k = k + 1
        stats_summary[0, k] = 'WP0 B'
        stats_summary[1, k] = GL[2]
        k = k + 1
        stats_summary[0, k] = 'WP0 Lum'
        stats_summary[1, k] = Lum_WP_output
        k = k + 1
        stats_summary[0, k] = 'WP0 x'
        stats_summary[1, k] = Color_WP_x_output
        k = k + 1
        stats_summary[0, k] = 'WP0 y'
        stats_summary[1, k] = Color_WP_y_output
        k = k + 1
        stats_summary[0, k] = 'WP0 dxy to d65'
        stats_summary[1, k] = dxdy_WP_output
        k = k + 1
        stats_summary[0, k] = 'WP0_corrected Lum'
        stats_summary[1, k] = Lum_WP_output_corrected
        k = k + 1
        stats_summary[0, k] = 'WP0_corrected x'
        stats_summary[1, k] = Color_WP_x_output_corrected
        k = k + 1
        stats_summary[0, k] = 'WP0_corrected y'
        stats_summary[1, k] = Color_WP_y_output_corrected
        k = k + 1
        stats_summary[0, k] = 'WP0_corrected dxy to d65'
        stats_summary[1, k] = dxdy_WP_output_corrected
        k = k + 1

        for i in range(0, 1):
            stats_summary[0, k] = 'WP_meas_' + str(i + 1) + ' R'
            stats_summary[1, k] = R_output[i]
            k = k + 1
            stats_summary[0, k] = 'WP_meas_' + str(i + 1) + ' G'
            stats_summary[1, k] = G_output[i]
            k = k + 1
            stats_summary[0, k] = 'WP_meas_' + str(i + 1) + ' B'
            stats_summary[1, k] = B_output[i]
            k = k + 1
            stats_summary[0, k] = 'WP_meas_' + str(i + 1) + ' Lum'
            stats_summary[1, k] = Lum_output[i]
            k = k + 1
            stats_summary[0, k] = 'WP_meas_' + str(i + 1) + ' x'
            stats_summary[1, k] = Color_x_output[i]
            k = k + 1
            stats_summary[0, k] = 'WP_meas_' + str(i + 1) + ' y'
            stats_summary[1, k] = Color_y_output[i]
            k = k + 1
            stats_summary[0, k] = 'WP_meas_' + str(i + 1) + ' dxy to d65'
            stats_summary[1, k] = dxdy_output[i]
            k = k + 1

        for i in range(0, 1):
            stats_summary[0, k] = 'WP_corrected_meas_' + str(i + 1) + ' R'
            stats_summary[1, k] = R_output_corrected[i]
            k = k + 1
            stats_summary[0, k] = 'WP_corrected_meas_' + str(i + 1) + ' G'
            stats_summary[1, k] = G_output_corrected[i]
            k = k + 1
            stats_summary[0, k] = 'WP_corrected_meas_' + str(i + 1) + ' B'
            stats_summary[1, k] = B_output_corrected[i]
            k = k + 1
            stats_summary[0, k] = 'WP_corrected_meas_' + str(i + 1) + ' Lum'
            stats_summary[1, k] = Lum_output_corrected[i]
            k = k + 1
            stats_summary[0, k] = 'WP_corrected_meas_' + str(i + 1) + ' x'
            stats_summary[1, k] = Color_x_output_corrected[i]
            k = k + 1
            stats_summary[0, k] = 'WP_corrected_meas_' + str(i + 1) + ' y'
            stats_summary[1, k] = Color_y_output_corrected[i]
            k = k + 1
            stats_summary[0, k] = 'WP_corrected_meas_' + str(i + 1) + ' dxy to d65'
            stats_summary[1, k] = dxdy_output_corrected[i]
            k = k + 1
        if export_csv:
            with open(os.path.join(os.path.expanduser('~/Desktop'), 'abcd.csv'), 'w',
                      encoding='utf-8', newline='') as csv_file:
                wr = csv.DictWriter(csv_file, fieldnames=stats_summary[0, :])
                wr.writeheader()
                wr.writerow(dict(zip(stats_summary[0, :], stats_summary[1, :])))
        del XYZ, XYZ_W,
        del Lum_WP_output, Color_WP_x_output, Color_WP_y_output, dxdy_WP_output, Lum_WP_output_corrected,
        del Color_WP_x_output_corrected, Color_WP_y_output_corrected, dxdy_WP_output_corrected,
        del R_output, G_output, B_output
        return dict(zip(*stats_summary))

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



    fn = r'C:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\raw\WhitePointCorrection'
    summarys = []
    with open(os.path.join(fn, 'aaa.csv'), encoding='utf-8') as text:
        rows = csv.reader(text, delimiter=',', )
        for row in rows:
            summarys.append(row)
    _exported_parametric = dict(zip(summarys[0], summarys[1]))
    ref_patterns = ['W255', 'R255', 'G255', 'B255']
    ref_luv = []
    for pattern in ref_patterns:
        items = [f" normal_{pattern}_{c}_0.0deg_0.0deg" for c in ["Lum", "u'", "v'"]]
        ref_luv.append(tuple([float(_exported_parametric[c]) for c in items]))

    gl = MotAlgorithmHelper.calc_gl_for_brightdot(np.array(ref_luv))

    x_bin = 'normal_W255_20210306_084517_nd_0_iris_5_X_float.bin'
    aa = MotAlgorithmHelper()
    XYZ = aa.white_dot_pattern_w255_read(os.path.join(fn, x_bin))
    XYZ_W = np.stack(XYZ, axis=2)
    # x_bin = 'normal_WhiteDot7_20210306_084914_nd_0_iris_5_X_float.bin'
    x_bin = 'normal_WhiteDotV2_20201218_031726_nd_0_iris_5_X_float.bin'
    exp = aa.white_dot_pattern_parametric_export(XYZ_W, gl, os.path.join(fn, x_bin), export_csv=True, n_dots=21)
    pass

    # station_config.load_station('seacliff_mot')
    # station_config.print_to_console = types.MethodType(print_to_console, station_config)
    # station_config._verbose = True
    # the_equipment = seacliffmotEquipment(station_config, station_config)
    # print(the_equipment.version())
    # print(the_equipment.get_config())
    #
    # config = {"capturePath": "C:\\oculus\\factory_test_omi\\factory_test_stations\\factory-test_logs\\raw\\AA_seacliff_mot-01_20200612-100304"}
    # print(the_equipment.set_config(config))
    # print(the_equipment.open())
    # the_equipment.measure_and_export(station_config.TESTTYPE)
    # print(the_equipment.reset())
    # print(the_equipment.close())
    #
    # the_equipment.kill()