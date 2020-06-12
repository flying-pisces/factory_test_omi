#!/usr/bin/env python
import json
from Conoscope import Conoscope
import time
from enum import Enum

def LogFunction(ret, functionName):
    print("  {0}".format(functionName))

    try:
        # case of return value is a string
        # print("  -> {0}".format(ret))
        returnData = json.loads(ret)
    except:
        # case of return is already a dict
        returnData = ret

    try:
        # display return data
        for key, value in returnData.items():
            print("      {0:<20}: {1}".format(key, value))
    except:
        print("  invalid return value")

class TestType(Enum):
    Capture = 0
    CaptureAE = 1
    CaptureSequence = 2


def main_f(testType):
    print("connect to conoscope")
    conoscope = Conoscope(True)

    ret = conoscope.CmdGetVersion()
    LogFunction(ret, "CmdGetVersion")

    ret = conoscope.CmdGetConfig()
    LogFunction(ret, "CmdGetConfig")

    config = {"capturePath": "./CaptureFolder1",
              "cfgPath": "./Cfg"}

    config = {"capturePath": "./CaptureFolder1",
              "cfgPath": "./Cfg",
              "fileNamePrepend": "",
              "fileNameAppend": "",
              "exportFileNameFormat": "",
              "exportFormat": Conoscope.ExportFormat.BinJpg.value}

    ret = conoscope.CmdSetConfig(config)
    LogFunction(ret, "CmdSetConfig")

    ret = conoscope.CmdOpen()
    LogFunction(ret, "CmdOpen")

    if testType == TestType.Capture:
        __perform_capture(conoscope)
    elif testType == TestType.CaptureAE:
        ret, errorMessage = __perform_captureAE(conoscope)
    elif testType == TestType.CaptureSequence:
        __perform_capture_sequence(conoscope)

    print("*************")
    if ret == 0:
        print(" TEST SUCCESS " + errorMessage)
    else:
        print(" TEST FAILURE " + errorMessage)
    print("*************")

    # ret = conoscope.CmdReset()
    # LogFunction(ret, "CmdReset")

    ret = conoscope.CmdClose()
    LogFunction(ret, "CmdClose")

    # end the application
    conoscope.QuitApplication()

    print("Done")
    return


def __perform_capture(conoscope):
    setupConfig = {"sensorTemperature": 25.0,
                   "eFilter": Conoscope.Filter.Yb.value,
                   "eNd": Conoscope.Nd.Nd_3.value,
                   "eIris": Conoscope.Iris.aperture_4mm.value}
    ret = conoscope.CmdSetup(setupConfig)
    LogFunction(ret, "CmdSetup")

    ret = conoscope.CmdSetupStatus()
    LogFunction(ret, "CmdSetupStatus")

    measureConfig = {"exposureTimeUs": 100000,
                     "nbAcquisition": 1}

    ret = conoscope.CmdMeasure(measureConfig)
    LogFunction(ret, "CmdMeasure")

    ret = conoscope.CmdExportRaw()
    LogFunction(ret, "CmdExportRaw")

    ret = conoscope.CmdExportProcessed()
    LogFunction(ret, "CmdExportProcessed")

    # change capture path

    config = {"capturePath": "./CaptureFolder2"}
    ret = conoscope.CmdSetConfig(config)
    LogFunction(ret, "CmdSetup")

    setupConfig = {"sensorTemperature": 25.0,
                   "eFilter": Conoscope.Filter.Xz.value,
                   "eNd": Conoscope.Nd.Nd_1.value,
                   "eIris": Conoscope.Iris.aperture_2mm.value}
    ret = conoscope.CmdSetup(setupConfig)
    LogFunction(ret, "CmdSetup")

    ret = conoscope.CmdSetupStatus()
    LogFunction(ret, "CmdSetupStatus")

    measureConfig = {"exposureTimeUs": 90000,
                     "nbAcquisition": 1}

    ret = conoscope.CmdMeasure(measureConfig)
    LogFunction(ret, "CmdMeasure")

    ret = conoscope.CmdExportRaw()
    LogFunction(ret, "CmdExportRaw")

    ret = conoscope.CmdExportProcessed()
    LogFunction(ret, "CmdExportProcessed")


def __measureAE(conoscope, measureConfig):
    ret = conoscope.CmdMeasureAEStatus()
    LogFunction(ret, "CmdMeasureAEStatus")
    aeState = ret["state"]

    # check the measurement is not processing
    # if Conoscope.MeasureAEState(conoscope.measureAEStatus.state) == Conoscope.MeasureAEState.MeasureAEState_NotStarted:
    if aeState == Conoscope.MeasureAEState.MeasureAEState_NotStarted or \
        aeState == Conoscope.MeasureAEState.MeasureAEState_Done :
        # set start values

        # launch measurement
        ret = conoscope.CmdMeasureAE(measureConfig)
        LogFunction(ret, "CmdMeasureAE")

        # wait for the measurement is done
        bDone = False
        aeExpo = 0

        while bDone is not True:
            ret = conoscope.CmdMeasureAEStatus()
            # LogFunction(ret, "CmdMeasureAEStatus")
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

    return ret


def __perform_captureAE(conoscope):
    setupConfig = {"sensorTemperature": 25.0,
                   "eFilter": Conoscope.Filter.Yb.value,
                   "eNd": Conoscope.Nd.Nd_3.value,
                   "eIris": Conoscope.Iris.aperture_4mm.value}
    ret = conoscope.CmdSetup(setupConfig)
    LogFunction(ret, "CmdSetup")

    if ret['Error'] != 0:
        return 1, "1 - setup"

    ret = conoscope.CmdSetupStatus()
    LogFunction(ret, "CmdSetupStatus")

    if ret['Error'] != 0:
        return 1, "1 - setupStatus"

    # process measurement AE
    measureConfig = {"exposureTimeUs": 10000,
                     "nbAcquisition": 1}
    ret = __measureAE(conoscope, measureConfig)

    if ret['Error'] != 0:
        return 1, "1 - MeasureAE"

    ret = conoscope.CmdExportRaw()
    LogFunction(ret, "CmdExportRaw")

    if ret['Error'] != 0:
        return 1, "1 - exportRaw"

    ret = conoscope.CmdExportProcessed()
    LogFunction(ret, "CmdExportProcessed")

    if ret['Error'] != 0:
        return 1, "1 - exportProcessed"

    # change capture path
    #config = {"capturePath": "./CaptureFolder2"}
    #ret = conoscope.CmdSetConfig(config)
    #LogFunction(ret, "CmdSetup")

    setupConfig = {"sensorTemperature": 25.0,
                   "eFilter": Conoscope.Filter.Xz.value,
                   "eNd": Conoscope.Nd.Nd_1.value,
                   "eIris": Conoscope.Iris.aperture_2mm.value}
    ret = conoscope.CmdSetup(setupConfig)
    LogFunction(ret, "CmdSetup")

    if ret['Error'] != 0:
        return 1, "2- setup"

    ret = conoscope.CmdSetupStatus()
    LogFunction(ret, "CmdSetupStatus")

    if ret['Error'] != 0:
        return 1, "2- setupStatus"

    # process measurement AE
    measureConfig = {"exposureTimeUs": 10000,
                     "nbAcquisition": 1}
    ret = __measureAE(conoscope, measureConfig)

    if ret['Error'] != 0:
        return 1, "2- measureAE"

    ret = conoscope.CmdExportRaw()
    LogFunction(ret, "CmdExportRaw")

    if ret['Error'] != 0:
        return 1, "2- exportRaw"

    ret = conoscope.CmdExportProcessed()
    LogFunction(ret, "CmdExportProcessed")

    if ret['Error'] != 0:
        return 1, "2- exportProcessed"

    return 0, "Done"

def __perform_capture_sequence(conoscope):
    # check capture sequence
    ret = conoscope.CmdGetCaptureSequence()
    LogFunction(ret, "CmdGetCaptureSequence")

    captureSequenceConfig = {"sensorTemperature": 24.0,
                             "bWaitForSensorTemperature": False,
                             "eNd": Conoscope.Nd.Nd_1.value,
                             "eIris": Conoscope.Iris.aperture_4mm.value,
                             "exposureTimeUs": 12000,
                             "nbAcquisition": 1,
                             "bAutoExposure": False,
                             "bUseExpoFile": False}

    ret = conoscope.CmdCaptureSequence(captureSequenceConfig)
    LogFunction(ret, "CmdCaptureSequence")

    # wait for the end of the processing
    done = False

    processStateCurrent = None
    processStepCurrent = None

    print("wait for the sequence to be finished")

    while done is False:
        ret = conoscope.CmdCaptureSequenceStatus()
        # LogFunction(ret, "CmdCaptureSequenceStatus")

        processState = ret['state']
        processStep = ret['currentSteps']
        processNbSteps = ret['nbSteps']

        if(processStateCurrent is None) or (processStateCurrent != processState) or (processStepCurrent != processStep):
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

def __perform_capture(conoscope):
    setupConfig = {"sensorTemperature": 25.0,
                   "eFilter": Conoscope.Filter.Yb.value,
                   "eNd": Conoscope.Nd.Nd_3.value,
                   "eIris": Conoscope.Iris.aperture_4mm.value}
    ret = conoscope.CmdSetup(setupConfig)
    LogFunction(ret, "CmdSetup")

    ret = conoscope.CmdSetupStatus()
    LogFunction(ret, "CmdSetupStatus")

    measureConfig = {"exposureTimeUs": 100000,
                     "nbAcquisition": 1}

    ret = conoscope.CmdMeasure(measureConfig)
    LogFunction(ret, "CmdMeasure")

    ret = conoscope.CmdExportRaw()
    LogFunction(ret, "CmdExportRaw")

    ret = conoscope.CmdExportProcessed()
    LogFunction(ret, "CmdExportProcessed")

    # change capture path

    config = {"capturePath": "./CaptureFolder2"}
    ret = conoscope.CmdSetConfig(config)
    LogFunction(ret, "CmdSetup")

    setupConfig = {"sensorTemperature": 25.0,
                   "eFilter": Conoscope.Filter.Xz.value,
                   "eNd": Conoscope.Nd.Nd_1.value,
                   "eIris": Conoscope.Iris.aperture_2mm.value}
    ret = conoscope.CmdSetup(setupConfig)
    LogFunction(ret, "CmdSetup")

    ret = conoscope.CmdSetupStatus()
    LogFunction(ret, "CmdSetupStatus")

    measureConfig = {"exposureTimeUs": 90000,
                     "nbAcquisition": 1}

    ret = conoscope.CmdMeasure(measureConfig)
    LogFunction(ret, "CmdMeasure")

    ret = conoscope.CmdExportRaw()
    LogFunction(ret, "CmdExportRaw")

    ret = conoscope.CmdExportProcessed()
    LogFunction(ret, "CmdExportProcessed")


if __name__ == '__main__':
    print("--- START ---")

    # print the menu options
    for item in TestType:
        print("  {0: <5} {1}".format(item.value, item.name))

    validInput = False

    while validInput is False:

        inputValue = input()
        try:
            inputInt = int(inputValue)
            inputTestType = TestType(inputInt)
            validInput = True
        except:
            print("invalid value")
            validInput = False

    main_f(inputTestType)

    print("--- DONE ---")
    

