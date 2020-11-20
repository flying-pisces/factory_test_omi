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
            self._operator_interface.print_to_console("Open Status is \n{0}\n".format(str(self._open)))
        return self._open

    def reset(self):
        ret = self._device.CmdReset()
        if self._verbose:
            self._operator_interface.print_to_console("Open Status is \n{0}\n".format(str(self._log(ret, "CmdReset"))))
        else:
            self._log(ret, "CmdReset")
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
                print("  state = {0} ({1} us)".format(aeState, aeExpo))
            if (aeState == Conoscope.MeasureAEState.MeasureAEState_Done) or \
                    (aeState == Conoscope.MeasureAEState.MeasureAEState_Error) or \
                    (aeState == Conoscope.MeasureAEState.MeasureAEState_Cancel):
                bDone = True

                print("  state = {0} ({1} us)".format(aeState, ret["exposureTimeUs"]))
            else:
                time.sleep(0.1)

    def __check_seq_finish(self):
        done = False
        processStateCurrent = None
        processStepCurrent = None
        print("wait for the sequence to be finished")
        while done is False:
            ret = self._device.CmdCaptureSequenceStatus()
            processState = ret['state']
            processStep = ret['currentSteps']
            processNbSteps = ret['nbSteps']

            if (processStateCurrent is None) or (processStateCurrent != processState) or (
                    processStepCurrent != processStep):
                print("  step {0}/{1} state {2}".format(processStep, processNbSteps, processState))

                processStateCurrent = processState
                processStepCurrent = processStep

            if processState == Conoscope.CaptureSequenceState.CaptureSequenceState_Error:
                done = True
                print("Error happened")
            elif processState == Conoscope.CaptureSequenceState.CaptureSequenceState_Done:
                done = True
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

        if isinstance(exposure_cfg, str):
            if self._station_config.TEST_SEQ_USE_EXPO_FILE:
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

            captureSequenceConfig = {"sensorTemperature": self._station_config.TEST_SENSOR_TEMPERATURE,
                                     "bWaitForSensorTemperature": self._station_config.TEST_SEQ_WAIT_FOR_TEMPERATURE,
                                     "eNd": setup_cfg[1],  # Conoscope.Nd.Nd_1.value,
                                     "eIris": setup_cfg[2],  # Conoscope.Iris.aperture_4mm.value,
                                     "nbAcquisition": 1,
                                     "exposureTimeUs": int(exposure_cfg),
                                     "bAutoExposure": self._station_config.TEST_AUTO_EXPOSURE,
                                     "bUseExpoFile": self._station_config.TEST_SEQ_USE_EXPO_FILE,
                                     'bSaveCapture': self._station_config.TEST_SEQ_SAVE_CAPTURE}
            ret = self._device.CmdCaptureSequence(captureSequenceConfig)
            if ret['Error'] != 0:
                seacliffmotEquipmentError('Fail to CmdCaptureSequence.')
            self.__check_seq_finish()
        elif isinstance(exposure_cfg, int):
            setupConfig = {"sensorTemperature": self._station_config.TEST_SENSOR_TEMPERATURE,
                           "eFilter": setup_cfg[0],  # self._device.Filter.Yb.value,
                           "eNd": setup_cfg[1],  # self._device.Nd.Nd_3.value,
                           "eIris": setup_cfg[2],  # self._device.Iris.aperture_2mm.value
                           'autoExposure': self._station_config.TEST_AUTO_EXPOSURE,
                           }
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
            if not self._station_config.EQUIPMENT_SIM:
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

        print("wait for the sequence to be finished")

        while done is False:
            ret = self._device.CmdCaptureSequenceStatus()
            # LogFunction(ret, "CmdCaptureSequenceStatus")

            processState = ret['state']
            processStep = ret['currentSteps']
            processNbSteps = ret['nbSteps']

            if (processStateCurrent is None) or (processStateCurrent != processState) or (
                    processStepCurrent != processStep):
                print("  step {0}/{1} state {2}".format(processStep, processNbSteps, processState))

                processStateCurrent = processState
                processStepCurrent = processStep

            if processState == Conoscope.CaptureSequenceState.CaptureSequenceState_Error:
                done = True
                print("Error happened")
            elif processState == Conoscope.CaptureSequenceState.CaptureSequenceState_Done:
                done = True
                print("Process Done")

            if done is False:
                time.sleep(1)
            return

    ########### Export ###########
    def initialize(self):
        self.get_config()
        self._operator_interface.print_to_console("Initializing Seacliff MOT Equipment \n")


class MotAlgorithmHelper(object):

    def __init__(self):
        self._noise_thresh = 0.05  # Percent of Y sum to exclude from color plots (use due to color calc noise in dim part of image)
        self._color_thresh = 0.01  # Thresh for color uniformity
        self._lum_thresh = 0.8  # Thresh for brightness uniformity
        self._fixed_chroma_clims = 0  # If 1, then chroma plots range [0 1].  Otherwise auto scale
        self._disp_fov = 60  # Maximum FOV to display.  Use for masking.
        self._chromaticity_fov = [10, 20, 30]  # Limit FOV for chromaticity plot in degrees
        self._disp_ring_spacing = 10  # Spacing, in deg, of rings overlaid on plots
        self._kernel_width = 25  # Width of square smoothing kernel in pixels.
        self._kernel_shape = 'square'  # Use 'circle' or 'square' to change the smoothing kernel shape
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
            image_in = np.flip(image_in, 1)
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
            image_in = np.flip(image_in, 1)

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

        print('stas', stats[0]['Centroid'])
        scenters = []
        sMajorAxisLength = []
        sMinorAxisLength = []
        print('stats num:', len(stats))

        for i, stat in enumerate(stats):
            if stat['MajorAxisLength'] >= axis_length_thresh:
                scenters.append(list(stat['Centroid']))
                sMajorAxisLength.append(stat['MajorAxisLength'])
                sMinorAxisLength.append(stat['MinorAxisLength'])

        print('num stats {0} / {1}'.format(len(scenters), len(stats)))
        num_dots = len(scenters)
        bb = np.nonzero(np.array(sMinorAxisLength) > 50)
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
        stats_summary[0, k] = 'Number of Dots'
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
        del XYZ
        del CXYZ
        return dict(zip(list(stats_summary[0]), list(stats_summary[1])))

    def color_pattern_parametric_export(self, xfilename=r'W255_X_float.bin',
                                        brightness_statistics=True,
                                        color_uniformity=True):
        dirr = os.path.dirname(xfilename)
        fnamebase = os.path.basename(xfilename).lower().split('_x_float.bin')[0]
        filename = ['{0}_{1}_float.bin'.format(fnamebase, c) for c in ['X', 'Y', 'Z']]

        x_angle_arr = np.linspace(-1 * self._cam_fov, self._cam_fov, self._col).reshape(-1, self._col)
        y_angle_arr = np.linspace(-1 * self._cam_fov, self._cam_fov, self._row).reshape(-1, self._row)

        kernel = np.ones((self._kernel_width, self._kernel_width))
        kernel_b = np.sum(kernel)
        kernel = kernel / kernel_b  # normalize
        XYZ = []
        for i in range(0, 3):
            with open(os.path.join(dirr, filename[i]), 'rb') as fin:
                I = np.frombuffer(fin.read(), dtype=np.float32)
            image_in = np.reshape(I, (self._col, self._row))
            # Z = Z'        #Removed for viewing to match DUT orientation
            image_in = np.flip(image_in.T, 1)  # Implement flip for viewing to match DUT orientation
            image_in = cv2.filter2D(image_in, -1, kernel, borderType=cv2.BORDER_CONSTANT)
            XYZ.append(image_in)

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
        v_prime_smoothed = mask * (9 * XYZ[0]) / (XYZ[0] + 15 * XYZ[1] + 3 * XYZ[2])
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
                stdLum = np.std(tmp)
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

        return dict(zip(stats_summary[0, :], stats_summary[1, :]))



def print_to_console(self, msg):
    pass

if __name__ == "__main__":
    import sys
    sys.path.append("../../")
    import types
    import station_config
    import hardware_station_common.operator_interface.operator_interface as operator_interface

    station_config.load_station('seacliff_mot')
    station_config.print_to_console = types.MethodType(print_to_console, station_config)
    station_config._verbose = True
    the_equipment = seacliffmotEquipment(station_config, station_config)
    print(the_equipment.version())
    print(the_equipment.get_config())

    config = {"capturePath": "C:\\oculus\\factory_test_omi\\factory_test_stations\\factory-test_logs\\raw\\AA_seacliff_mot-01_20200612-100304"}
    print(the_equipment.set_config(config))
    print(the_equipment.open())
    the_equipment.measure_and_export(station_config.TESTTYPE)
    print(the_equipment.reset())
    print(the_equipment.close())

    the_equipment.kill()