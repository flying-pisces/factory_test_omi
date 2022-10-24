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
import importlib
import sys


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

        self._error_message = self.name + "is out of work"
        self._version = None
        self._config = None
        self._open = None
        self._conoscope = None
        self._quit = False

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
        self._quit = False
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
        self._quit = True
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

    def __check_seq_finish(self):
        done = False
        processStateCurrent = None
        processStepCurrent = None
        self._operator_interface.print_to_console("wait for the sequence to be finished.\n")
        while not done and not self._quit:
            ret = self._device.CmdCaptureSequenceStatus()
            if not isinstance(ret, dict):
                raise seacliffmotEquipmentError(f'Fail to check seq finish.. Ret {str(ret)}')
            processState = int(ret['state'].value)
            processStep = ret['currentSteps']
            processNbSteps = ret['nbSteps']

            if (processStateCurrent is None) or (processStateCurrent != processState) or (
                    processStepCurrent != processStep):
                self._operator_interface.print_to_console(
                    "---->  step {0}/{1} state {2}\n".format(processStep, processNbSteps, ret['state']))

                processStateCurrent = processState
                processStepCurrent = processStep

            if processState == 7:  # Conoscope.CaptureSequenceState.CaptureSequenceState_Error:
                done = True
                self._operator_interface.print_to_console("---->Error happened\n", 'red')
                raise seacliffmotEquipmentError(f'Fail to check seq finish.. {str(processState)}')
            elif processState == 6:  # conoscope.Conoscope.CaptureSequenceState.CaptureSequenceState_Done:
                done = True
                self._operator_interface.print_to_console("---->Process Done\n")

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
            if int(processState.value) not in [0, 6]:  # CaptureSequenceState_NotStarted , CaptureSequenceState_Done
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
        else:
            raise seacliffmotEquipmentError(f'Not support for this config. {exposure_cfg}')

    ########### Export ###########
    def initialize(self):
        conoscope_pth = r'test_station\test_equipment'
        assert hasattr(self._station_config, 'VERSION_REVISION_LIST'), 'Please update config to support multi conoscope'
        try:
            eq_list = [(k, v) for k, v in self._station_config.VERSION_REVISION_LIST.items()
                       if self._station_config.VERSION_REVISION_EQUIPMENT in v]
            if len(eq_list) > 0:
                cono, __ = eq_list[0]
                sys.path.append(conoscope_pth)
                self._conoscope = importlib.import_module(cono)
                self._conoscope.Conoscope.DLL_PATH = self._station_config.CONOSCOPE_DLL_PATH
                self._conoscope.Conoscope.VERSION_REVISION = self._station_config.VERSION_REVISION_EQUIPMENT
                self._device = self._conoscope.Conoscope(emulate_camera=self._station_config.EQUIPMENT_SIM,
                                                         emulate_wheel=self._station_config.EQUIPMENT_WHEEL_SIM,
                                                         emulate_spectro=self._station_config.EQUIPMENT_SPECTRO_SIM)
        except ModuleNotFoundError as e:
            raise seacliffmotEquipmentError(f'Except: {str(e)}, PATH: {conoscope_pth}')
        except Exception as e:
            self._operator_interface.print_to_console(f'Fail to init conoscope. {str(e)}')
            raise seacliffmotEquipmentError(f'Fail to init {str(e)}')

        self.get_config()
        self._operator_interface.print_to_console("Initializing Seacliff MOT Equipment \n")


def print_to_console(self, msg):
    pass


if __name__ == '__main__':
    import sys
    import types
    from MotAlgo.AlgoSeacliff import MotAlgorithmHelper
    sys.path.append(r'..\..')
    import station_config

    station_config.load_station('seacliff_mot')
    station_config.print_to_console = types.MethodType(print_to_console, station_config)
    the_unit = seacliffmotEquipment(station_config, station_config)
    the_unit.initialize()

    the_unit.close()
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
