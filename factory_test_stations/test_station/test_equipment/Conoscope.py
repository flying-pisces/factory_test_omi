#!/usr/bin/env python
import threading
import ctypes
import time
from enum import Enum
import json

class Conoscope:
    class Filter(Enum):
        BK7 = 0
        Mirror = 1
        X = 2
        Xz = 3
        Ya = 4
        Yb = 5
        Z = 6
        IrCut = 7
        Invalid = 8

    class Nd(Enum):
        Nd_0 = 0
        Nd_1 = 1
        Nd_2 = 2
        Nd_3 = 3
        Nd_4 = 4
        Invalid = 5

    class Iris(Enum):
        aperture_02 = 0
        aperture_03 = 1
        aperture_04 = 2
        aperture_05 = 3
        Invalid = 4

    class WheelState(Enum):
        WheelState_Idle = 0
        WheelState_Success = 1
        WheelState_Operating = 2
        WheelState_Error = 3

    class TemperatureMonitoringState(Enum):
        TemperatureMonitoringState_NotStarted = 0
        TemperatureMonitoringState_Processing = 1
        TemperatureMonitoringState_Locked = 2
        TemperatureMonitoringState_Aborted = 3
        TemperatureMonitoringState_Error = 4

    class ApplicationThread(threading.Thread):
        def __init__(self, threadID, name, counter):
            threading.Thread.__init__(self)
            self.threadID = threadID
            self.name = name
            self.counter = counter

        def setApi(self, api):
            self.__api = api

        def run(self):
            try:
                self.__api.RunApplication()
            except:
                print("Error executing thread")

    class ConoscopeConfig(ctypes.Structure):
        _fields_ = [
            ("cfgPath", ctypes.c_char_p),
            ("capturePath", ctypes.c_char_p),
            ("autoExposure", ctypes.c_bool),
            ("autoExposurePixelMax", ctypes.c_float)]

    class ConoscopeDebugSettings(ctypes.Structure):
        _fields_ = [
            ("debugMode", ctypes.c_bool),
            ("emulatedCamera", ctypes.c_bool),
            ("dummyRawImagePath", ctypes.c_char_p)]

    class SetupConfig(ctypes.Structure):
        _fields_ = [
            ("sensorTemperature", ctypes.c_float),
            ("eFilter", ctypes.c_int),
            ("eNd", ctypes.c_int),
            ("eIris", ctypes.c_int)]

    class SetupStatus(ctypes.Structure):
        _fields_ = [
            ("eTemperatureMonitoringState", ctypes.c_int),
            ("sensorTemperature", ctypes.c_float),
            ("eWheelStatus", ctypes.c_int),
            ("eFilter", ctypes.c_int),
            ("eNd", ctypes.c_int),
            ("eIris", ctypes.c_int)]

    class MeasureConfig(ctypes.Structure):
        _fields_ = [
            ("exposureTimeUs", ctypes.c_int),
            ("nbAcquisition", ctypes.c_int),
            ("binningFactor", ctypes.c_int),
            ("bTestPattern", ctypes.c_bool)]

    class ProcessingConfig(ctypes.Structure):
        _fields_ = [
            ("bBiasCompensation", ctypes.c_bool),
            ("bSensorDefectCorrection", ctypes.c_bool),
            ("bSensorPrnuCorrection", ctypes.c_bool),
            ("bLinearisation", ctypes.c_bool),
            ("bFlatField", ctypes.c_bool),
            ("bAbsolute", ctypes.c_bool)]

    def __init__(self):
        print("create an instance of the conoscope")

        self.conoscopeConfig = Conoscope.ConoscopeConfig()
        self.conoscopeDebugSettings = Conoscope.ConoscopeDebugSettings()
        self.setupConfig = Conoscope.SetupConfig()
        self.measureConfig = Conoscope.MeasureConfig(200000, 1, 1, False)

        conoscopeDll = ctypes.WinDLL(os.path.join(os.getcwd(), "test_station\\test_equipment\\ConoscopeLib.dll"))

        # hllApiProto = ctypes.WINFUNCTYPE (
        #  ctypes.c_int,      # Return type.
        #  ctypes.c_void_p,   # Parameters 1 ...
        #  ctypes.c_void_p,
        #  ctypes.c_void_p,
        #  ctypes.c_void_p)   # ... thru 4.

        # hllApiParams = (1, "p1", 0), (1, "p2", 0), (1, "p3",0), (1, "p4",0),

        # Actually map the call ("HLLAPI(...)") to a Python name.
        # hllApi = hllApiProto (("HLLAPI", conoscopeDll), hllApiParams)

        # p1 = ctypes.c_int (1)
        # p2 = ctypes.c_char_p (sessionVar)
        # p3 = ctypes.c_int (1)
        # p4 = ctypes.c_int (0)
        # hllApi (ctypes.byref (p1), p2, ctypes.byref (p3), ctypes.byref (p4))

        #RunApplicationProto = ctypes.WINFUNCTYPE(
        #    ctypes.c_char_p)  # Return type.
        #self.__RunApplication = RunApplicationProto(("RunApplication", conoscopeDll)),

        CmdRunApp_Proto = ctypes.WINFUNCTYPE(
            ctypes.c_char_p)  # Return type.
        self.__CmdRunApp = CmdRunApp_Proto(("CmdRunApp", conoscopeDll))

        CmdQuitApp_Proto = ctypes.WINFUNCTYPE(
            ctypes.c_char_p)  # Return type.
        self.__CmdQuitApp = CmdQuitApp_Proto(("CmdQuitApp", conoscopeDll))

        CmdGetVersionProto = ctypes.WINFUNCTYPE(
            ctypes.c_char_p)  # Return type.
        self.__CmdGetVersion = CmdGetVersionProto(("CmdGetVersion", conoscopeDll))

        CmdGetInfoProto = ctypes.WINFUNCTYPE(
            ctypes.c_char_p)  # Return type.
        self.__CmdGetInfo = CmdGetInfoProto(("CmdGetInfo", conoscopeDll))

        CmdOpenProto = ctypes.WINFUNCTYPE(
            ctypes.c_char_p)  # Return type.
        self.__CmdOpen = CmdOpenProto(("CmdOpen", conoscopeDll))

        CmdSetupProto = ctypes.WINFUNCTYPE(
            ctypes.c_char_p,  # Return type.
            ctypes.c_void_p)
        self.__CmdSetup = CmdSetupProto(("CmdSetup", conoscopeDll))

        CmdSetupStatusProto = ctypes.WINFUNCTYPE(
            ctypes.c_char_p,  # Return type.
            ctypes.c_void_p)
        self.__CmdSetupStatus = CmdSetupStatusProto(("CmdSetupStatus", conoscopeDll))

        CmdMeasureProto = ctypes.WINFUNCTYPE(
            ctypes.c_char_p,  # Return type.
            ctypes.c_void_p)
        self.__CmdMeasure = CmdMeasureProto(("CmdMeasure", conoscopeDll))

        CmdExportRawProto = ctypes.WINFUNCTYPE(
            ctypes.c_char_p)  # Return type.
        self.__CmdExportRaw = CmdExportRawProto(("CmdExportRaw", conoscopeDll))

        CmdExportRawBufferProto = ctypes.WINFUNCTYPE(
            ctypes.c_char_p)  # Return type.
        self.__CmdExportRawBuffer = CmdExportRawBufferProto(("CmdExportRawBuffer", conoscopeDll))

        CmdExportProcessedProto = ctypes.WINFUNCTYPE(
            ctypes.c_char_p,  # Return type.
            ctypes.c_void_p)
        self.__CmdExportProcessed = CmdExportProcessedProto(("CmdExportProcessed", conoscopeDll))

        CmdExportProcessedBufferProto = ctypes.WINFUNCTYPE(
            ctypes.c_char_p,  # Return type.
            ctypes.c_void_p)
        self.__CmdExportProcessedBuffer = CmdExportProcessedBufferProto(("CmdExportProcessedBuffer", conoscopeDll))

        CmdCloseProto = ctypes.WINFUNCTYPE(
            ctypes.c_char_p)  # Return type.
        self.__CmdClose = CmdCloseProto(("CmdClose", conoscopeDll))

        CmdResetProto = ctypes.WINFUNCTYPE(
            ctypes.c_char_p)  # Return type.
        self.__CmdReset = CmdResetProto(("CmdReset", conoscopeDll))

        CmdTerminateProto = ctypes.WINFUNCTYPE(
            ctypes.c_char_p)  # Return type.
        self.__CmdTerminate = CmdTerminateProto(("CmdTerminate", conoscopeDll))

        CmdSetConfigProto = ctypes.WINFUNCTYPE(
            ctypes.c_char_p,  # Return type.
            ctypes.c_void_p)
        self.__CmdSetConfig = CmdSetConfigProto(("CmdSetConfig_", conoscopeDll))

        CmdGetConfigProto = ctypes.WINFUNCTYPE(
            ctypes.c_char_p,  # Return type.
            ctypes.c_void_p)
        self.__CmdGetConfig = CmdGetConfigProto(("CmdGetConfig_", conoscopeDll))

        CmdSetDebugConfigProto = ctypes.WINFUNCTYPE(
            ctypes.c_char_p,  # Return type.
            ctypes.c_void_p)
        self.__CmdSetDebugConfig = CmdSetDebugConfigProto(("CmdSetDebugConfig_", conoscopeDll))

        CmdGetDebugConfigProto = ctypes.WINFUNCTYPE(
            ctypes.c_char_p,  # Return type.
            ctypes.c_void_p)
        self.__CmdGetDebugConfig = CmdGetDebugConfigProto(("CmdGetDebugConfig_", conoscopeDll))

        # create a thread to execute application
        try:
            self.__applicationThread = Conoscope.ApplicationThread(1, "AppThread", 1)
            self.__applicationThread.setApi(self)
            self.__applicationThread.start()

            # magic sleep
            time.sleep(0.5)
        except:
            print("Error: unable to start thread")

        # configure the conoscope to default value
        ret = self.CmdGetDebugConfig()

        # configure conoscope in normal mode
        ret = self.CmdSetDebugConfig({"debugMode": False,
                                                "emulatedCamera": False})
        print("instance done")

    def __del__(self):
        print("CONOSCOPE INSTANCE BEING DELETED")

    def __Result(ret):
        return json.loads(ret)

    def __FillStructure(structure, config):
        for field_name, field_type in structure._fields_:
            # print("{0}".format(field_name))

            if field_name in config:
                field_value = config[field_name]

                try:
                    # convert string
                    b_field_value = field_value.encode('utf-8')
                    field_value = b_field_value
                except:
                    # this is not a string
                    pass

                setattr(structure, field_name, field_value)

    def RunApplication(self):
        return self.__CmdRunApp()

    def QuitApplication(self):
        # terminate the dll
        self.__CmdTerminate()

        # stop the thread
        self.__CmdQuitApp()

        # wait for the thread to be finished
        self.__applicationThread.join()

    def CmdGetVersion(self):
        return Conoscope.__Result(self.__CmdGetVersion())

    def CmdGetInfo(self):
        return Conoscope.__Result(self.__CmdGetInfo())

    def CmdOpen(self):
        return Conoscope.__Result(self.__CmdOpen())

    def CmdSetup(self, config):
        Conoscope.__FillStructure(self.setupConfig, config)
        return Conoscope.__Result(self.__CmdSetup(ctypes.byref(self.setupConfig)))

    def CmdSetupStatus(self):
        setupStatus = Conoscope.SetupStatus()

        ret = self.__CmdSetupStatus(ctypes.byref(setupStatus))

        returnVal = Conoscope.__Result(ret)

        # update return value with setup status
        returnVal["eTemperatureMonitoringState"] = Conoscope.TemperatureMonitoringState(setupStatus.eTemperatureMonitoringState)
        returnVal["sensorTemperature"] = setupStatus.sensorTemperature
        returnVal["eWheelState"] = Conoscope.WheelState(setupStatus.eWheelStatus)
        returnVal["eFilter"] = Conoscope.Filter(setupStatus.eFilter)
        returnVal["eNd"] = Conoscope.Nd(setupStatus.eNd)
        returnVal["eIris"] = Conoscope.Iris(setupStatus.eIris)

        return returnVal

    def CmdMeasure(self, config):
        Conoscope.__FillStructure(self.measureConfig, config)

        return Conoscope.__Result(self.__CmdMeasure(ctypes.byref(self.measureConfig)))

    def CmdExportRaw(self):
        return Conoscope.__Result(self.__CmdExportRaw())

    def CmdExportRawBuffer(self):
        print("not implemented correctly")
        return Conoscope.__Result(self.__CmdExportRawBuffer())

    def CmdExportProcessed(self, config={"bBiasCompensation": True,
                                         "bSensorDefectCorrection": True,
                                         "bSensorPrnuCorrection": True,
                                         "bLinearisation": True,
                                         "bFlatField": True,
                                         "bAbsolute": True}):
        processingConfig = Conoscope.ProcessingConfig(False, False, False, False, False, False)
        Conoscope.__FillStructure(processingConfig, config)
        return Conoscope.__Result(self.__CmdExportProcessed(ctypes.byref(processingConfig)))

    def CmdExportProcessedBuffer(self, config={"bBiasCompensation": True,
                                               "bSensorDefectCorrection": True,
                                               "bSensorPrnuCorrection": True,
                                               "bLinearisation": True,
                                               "bFlatField": True,
                                               "bAbsolute": True}):
        processingConfig = Conoscope.ProcessingConfig(False, False, False, False, False, False)
        Conoscope.__FillStructure(processingConfig, config)
        return Conoscope.__Result(self.__CmdExportProcessedBuffer(ctypes.byref(processingConfig)))

    def CmdClose(self):
        return Conoscope.__Result(self.__CmdClose())

    def CmdReset(self):
        return Conoscope.__Result(self.__CmdReset())

    def CmdSetConfig(self, config):
        Conoscope.__FillStructure(self.conoscopeConfig, config)
        ret = Conoscope.__Result(self.__CmdSetConfig(ctypes.byref(self.conoscopeConfig)))
        return ret

    def CmdGetConfig(self):
        return Conoscope.__Result(self.__CmdGetConfig(ctypes.byref(self.conoscopeConfig)))

    def CmdSetDebugConfig(self, config):
        Conoscope.__FillStructure(self.conoscopeDebugSettings, config)
        ret = Conoscope.__Result(self.__CmdSetDebugConfig(ctypes.byref(self.conoscopeDebugSettings)))
        return ret

    def CmdGetDebugConfig(self):
        ret = Conoscope.__Result(self.__CmdGetDebugConfig(ctypes.byref(self.conoscopeDebugSettings)))
        return ret

