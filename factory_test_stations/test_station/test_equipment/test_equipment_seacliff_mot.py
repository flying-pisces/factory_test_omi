import hardware_station_common.test_station.test_equipment
import json
import os
import shutil
import pprint
try:
    from test_station.test_equipment.Conoscope import Conoscope
except:
    from Conoscope import Conoscope
finally:
    pass
import time


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
        self._device = Conoscope(self._station_config.EQUIPMENT_SIM)
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

        # TODO:
        if self._station_config.EQUIPMENT_SIM:
            ret = self._device.CmdSetDebugConfig(
                {'dummyRawImagePath': r'C:\Users\Jason\Desktop\rawdata\20200529_131128_filt_Yb_nd_3_iris_2_raw_1.bin'})

        if setup_cfg is not None:
            setupConfig = {"sensorTemperature": self._station_config.TEST_SENSOR_TEMPERATURE,
                           "eFilter": setup_cfg[0],  # self._device.Filter.Yb.value,
                           "eNd": setup_cfg[1],  # self._device.Nd.Nd_3.value,
                           "eIris": setup_cfg[2],  # self._device.Iris.aperture_2mm.value
                           'autoExposure': False
                           }
            ret = self._device.CmdSetup(setupConfig)
            self._log(ret, "CmdSetup")
            if ret['Error'] != 0:
                seacliffmotEquipmentError('Fail to CmdSetup.')

            ret = self._device.CmdSetupStatus()
            self._log(ret, "CmdSetupStatus")
            if ret['Error'] != 0:
                raise seacliffmotEquipmentError('Fail to CmdSetupStatus.')

        if isinstance(exposure_cfg, str):
            capture_seq_exposure = os.path.join(self._station_config.CONOSCOPE_DLL_PATH,
                                                'algorithm', exposure_cfg + '.json')
            target_seq_name = os.path.join(self._station_config.CONOSCOPE_DLL_PATH, 'CaptureSequenceExposureTime.json')
            if not os.path.exists(capture_seq_exposure):
                raise seacliffmotEquipmentError('Fail to Find config for {0}.'.format(capture_seq_exposure))
            shutil.copyfile(capture_seq_exposure, target_seq_name)

            self.__check_seq_finish()

            captureSequenceConfig = {"sensorTemperature": self._station_config.TEST_SENSOR_TEMPERATURE,
                                     "bWaitForSensorTemperature": False,
                                     "eNd": self._station_config.TEST_SEQ_ND,  # Conoscope.Nd.Nd_1.value,
                                     "eIris": self._station_config.TEST_SEQ_EIRIS,  # Conoscope.Iris.aperture_4mm.value,
                                     "nbAcquisition": 1,
                                     "bAutoExposure": False,
                                     "bUseExpoFile": True}
            ret = self._device.CmdCaptureSequence(captureSequenceConfig)
            if ret['Error'] != 0:
                seacliffmotEquipmentError('Fail to CmdCaptureSequence.')
            self.__check_seq_finish()
        elif isinstance(exposure_cfg, int):
            measureConfig = {"exposureTimeUs": exposure_cfg,
                             "nbAcquisition": 1}
            ret = self._device.CmdMeasure(measureConfig)
            self._log(ret, "CmdMeasure")
            if ret['Error'] != 0:
                raise seacliffmotEquipmentError('Fail to CmdMeasure.')

            ret = self._device.CmdExportRaw()
            self._log(ret, "CmdExportRaw")
            if ret['Error'] != 0:
                raise seacliffmotEquipmentError('Fail to CmdExportRaw.')

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