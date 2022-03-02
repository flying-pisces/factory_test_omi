import hardware_station_common.test_station.test_equipment
import os
import json
import clr

clr.AddReference('System.Drawing')
clr.AddReference('System')
from System.Collections.Generic import List
import System

from System.Drawing import *
from System import String
import numpy as np
import sys
import pprint
import traceback

sys.path.append("../")
sys.path.append("../../")
sys.path.append("../../../")
from datetime import datetime
import logging


class SeacliffOffAxis4EquipmentError(Exception):
    pass


class SeacliffOffAxis4Equipment(hardware_station_common.test_station.test_equipment.TestEquipment):
    def __init__(self, station_config):
        apipath = os.path.join(os.path.join(station_config.ROOT_DIR, station_config.MPKAPI_RELATIVEPATH))
        clr.AddReference(apipath)
        from MPK_API_CS import MPK_API
        self.name = "i16"
        self._verbose = station_config.IS_VERBOSE
        self._station_config = station_config
        self._device = MPK_API()
        self._error_message = self.name + "is out of work"
        self._read_error = False
        self._version = None

    ########### NEW SETUP FUNCTIONS ###########
    def set_database(self, databasePath):
        result = self._device.SetMeasurementDatabase(databasePath)
        if self._verbose:
            pprint.pprint(result)
        return result

    def create_database(self, databasePath):
        result = self._device.CreateMeasurementDatabase(databasePath)
        if self._verbose:
            pprint.pprint(result)
        return result

    def set_sequence(self, sequencePath):
        result = self._device.SetSequence(sequencePath)
        if self._verbose:
            pprint.pprint(result)
        return result

    ###########################################

    def _parse_result(self, apires, param=None, eOnError=True):
        resjson = json.loads(str(apires))
        out = None
        if param is None:
            if len(resjson.values()) == 1:
                out = resjson.values()[0]
            elif len(resjson.values()) > 1:
                out = dict((str(v), int(k)) for k, v in resjson.iteritems())
            else:
                logging.error("Could not parse response message")
        else:
            out = resjson.get(param)
        if self._verbose:
            logging.info("MPK_API_RESULT:{}".format(str(resjson)))
        # logging.debug(out)
        if eOnError:
            error = resjson.get("ErrorCode")
            if error != None and int(error) != 0:
                logging.error("code is: {}:{}".format(int(error), self._err[int(error)]))
                logging.error(traceback.format_exc())
                raise AssertionError("Wrong return code: {}:{} Debug:{}".format(
                    int(error), self._err[int(error)], str(apires).strip("\r\n")))
        return out

    def serialnumber(self):
        response = json.loads(self._device.GetCameraSerial())
        sn = "Camera Serial Number: {0}".format(response['CameraSerial'])
        if self._verbose:
            print(sn)
        return

    def getsn(self, channel=0):
        response = self._device.ReadSerialNumber(channel)
        if self._verbose:
            pprint.pprint(response)
        return

    def version(self):
        if self._version is None:
            response = self._device.GetMpkApiVersionInfo()
            versionjson = json.loads(str(response))
            if self._verbose:
                pprint.pprint(versionjson)
            if 'MpkApiVersionInfo' in versionjson:
                self._version = versionjson['MpkApiVersionInfo']
        return self._version

    def initialize(self):
        response = self._device.InitializeCamera(self._station_config.CAMERA_SN, False, True)
        pres = json.loads(response)
        init_result = "Init Camera Result - ErrorCode: {0}".format(pres['ErrorCode'])  # 0 means return successful
        if self._verbose:
            pprint.pprint(response)
        return init_result

    def close(self):
        response = self._device.CloseCommunication()
        # return int(self._parse_result(response))

    def ready(self):
        response = json.loads(self._device.EquipmentReady())
        msg = "Ready - ErrorCode: {0}".format(response['ErrorCode'])
        if self._verbose:
            print(msg)
        ready_result = response['ErrorCode'] == 'Success'
        return ready_result

    ########### NEW MEASUREMENT FUNCTIONS ###########

    def get_measurement_list(self):
        result = self._device.GetMeasurementList();
        if self._verbose:
            pprint.pprint(result)
        return json.loads(result)

    def get_list_of_meas_IDs(self):
        measList = json.loads(self._device.GetMeasurementList())
        IDlist = []
        for meas in measList:
            IDlist.append(meas["Measurement ID"])
        if self._verbose:
            print(IDlist)
        return IDlist

    def export_measurement(self, imageName, exportPath, exportFilename="", resX=0, resY=0):
        result = self._device.ExportMeasurement(imageName, exportPath, exportFilename, resX, resY)
        if self._verbose:
            pprint.pprint(result)
        return result

    ########### NEW SEQUENCING FUNCTIONS ###########

    def sequence_run_all(self, useCamera, saveImages):
        result = self._device.RunAllSequenceSteps(useCamera, saveImages)
        return result

    def sequence_run_step(self, stepName, patternName, useCamera, saveImages):
        result = self._device.RunSequenceStepByName(stepName, patternName, useCamera, saveImages)
        return json.loads(result)

    def sequence_run_step_list(self, stepList, patternName, useCamera, saveImages):
        stepItems = List[str]()
        for c in stepList:
            stepItems.Add(c)
        result = self._device.RunSequenceStepListByName(stepItems, patternName, useCamera, saveImages)
        if self._verbose:
            pprint.pprint(result)
        return json.loads(result)

    def clear_registration(self):
        result = self._device.ClearRegistration()
        if self._verbose:
            pprint.pprint(result)
        return json.loads(result)
    #################################################
