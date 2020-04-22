#!/usr/bin/env python
import json
from Conoscope import Conoscope
import time

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

def main_f():
    print("connect to conoscope")

    conoscope = Conoscope()

    ret = conoscope.CmdGetVersion()
    LogFunction(ret, "CmdGetVersion")

    ret = conoscope.CmdGetConfig()
    LogFunction(ret, "CmdGetConfig")

    config = {"capturePath": "./CaptureFolder1",
              "cfgPath": "./Cfg"}

    ret = conoscope.CmdSetConfig(config)
    LogFunction(ret, "CmdSetConfig")

    ret = conoscope.CmdOpen()
    LogFunction(ret, "CmdOpen")

    setupConfig = {"sensorTemperature": 25.0,
                   "eFilter": Conoscope.Filter.X.value,
                   "eNd": Conoscope.Nd.Nd_0.value,
                   "eIris": Conoscope.Iris.aperture_02.value}
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
                   "eIris": Conoscope.Iris.aperture_02.value}
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

    ret = conoscope.CmdReset()
    LogFunction(ret, "CmdReset")

    ret = conoscope.CmdClose()
    LogFunction(ret, "CmdClose")

    # end the application
    conoscope.QuitApplication()

    print("Done")
    return


if __name__ == '__main__':
    print("--- START ---")
    main_f()
    print("--- DONE ---")
    

