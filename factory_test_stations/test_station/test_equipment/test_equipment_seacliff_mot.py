import hardware_station_common.test_station.test_equipment
import json
try:
    from test_station.test_equipment.Conoscope import Conoscope
except:
    from Conoscope import Conoscope
finally:
    pass
import time
import sys
sys.path.append("../")
sys.path.append("../../")
sys.path.append("../../../")


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
                self._operator_interface.print_to_console("Equipment Version is \n" + str(self._version))
        return self._version

    def get_config(self):
        if self._config is None:
            ret = self._device.CmdGetConfig()
            self._config = self._log(ret, "CmdGetConfig")
            if self._verbose:
                self._operator_interface.print_to_console("Current Configuration is \n" + str(self._config))
        return self._config

    def set_config(self, configsetting):
        ret = self._device.CmdSetConfig(configsetting)
        self._config = self._log(ret, "CmdSetConfig")
        if self._verbose:
            self._operator_interface.print_to_console("Current Configuration is \n" + str(self._config))
        return self._config

    ########### Equipment Operation ###########
    def open(self):
        ret = self._device.CmdOpen()
        self._open = self._log(ret, "CmdOpen")
        if self._verbose:
            self._operator_interface.print_to_console("Open Status is \n" + str(self._open))
        return self._open

    def reset(self):
        ret = self._device.CmdReset()
        if self._verbose:
            self._operator_interface.print_to_console("Open Status is \n" + str(self._log(ret, "CmdReset")))
        else:
            self._log(ret, "CmdReset")
        return self._log(ret, "CmdReset")

    def close(self):
        ret = self._device.CmdClose()
        if self._verbose:
            self._operator_interface.print_to_console("Open Status is \n" + str(self._log(ret, "CmdClose")))
        else:
            self._log(ret, "CmdClose")
        return self._log(ret, "CmdClose")

    def kill(self):
        self._device.QuitApplication()

    def is_ready(self):
        pass

    ########### Measure ###########
    def measure_and_export(self, measuretype):
        if measuretype == 0:
            self.__perform_capture()
        elif measuretype == 1:
            self._perform_capture_sequence()
        else:
            self._operator_interface.print_to_console("TestType Setting is Wrong \n" + self._error_message)
        return

    def __perform_capture(self):
        setupConfig = {"sensorTemperature": 25.0,
                       "eFilter": self._device.Filter.Yb.value,
                       "eNd": self._device.Nd.Nd_3.value,
                       "eIris": self._device.Iris.aperture_02.value}
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

        config = {"capturePath": "./CaptureFolder2"}
        ret = self._device.CmdSetConfig(config)
        self._log(ret, "CmdSetup")

        setupConfig = {"sensorTemperature": 25.0,
                       "eFilter": self._device.Filter.Xz.value,
                       "eNd": self._device.Nd.Nd_1.value,
                       "eIris": self._device.Iris.aperture_02.value}
        ret = self._device.CmdSetup(setupConfig)
        self._log(ret, "CmdSetup")

        ret = self._device.CmdSetupStatus()
        self._log(ret, "CmdSetupStatus")

        measureConfig = {"exposureTimeUs": 90000,
                         "nbAcquisition": 1}

        ret = self._device.CmdMeasure(measureConfig)
        self._log(ret, "CmdMeasure")

        ret = self._device.CmdExportRaw()
        self._log(ret, "CmdExportRaw")

        ret = self._device.CmdExportProcessed()
        self._log(ret, "CmdExportProcessed")
        return

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
    config = {"capturePath": "./CaptureFolder1",
              "cfgPath": "./Cfg"}
    print(the_equipment.set_config(config))
    print(the_equipment.open())
    the_equipment.measure_and_export(station_config.TESTTYPE)
    print(the_equipment.reset())
    print(the_equipment.close())

    the_equipment.kill()