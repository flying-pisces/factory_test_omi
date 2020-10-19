import os
import json
import sys
import traceback
from datetime import datetime
import time
import re
import numpy as np
import logging
import pprint
import serial
import serial.tools.list_ports
import clr
clr.AddReference('System.Drawing')
clr.AddReference('System')
clr.AddReference('System.Collections')
import System
apipath = os.path.join(r"C:\Program Files\Radiant Vision Systems\TrueTest 1.7\MPK_API.dll")
clr.AddReference(apipath)
from MPK_API_CS import *
from System.Drawing import *
from System import String
import hardware_station_common.test_station.test_equipment


COMMAND_IDO = "IDO\r\n"  # information
COMMAND_ZRC = "ZRC\r\n"  # zero cal
COMMAND_XYZ = "XYZ\r\n"  # measurement


class pancakemuniEquipmentError(Exception):
    pass


class pancakemuniEquipment(hardware_station_common.test_station.test_equipment.TestEquipment):
    _serial_port: serial.Serial

    def __init__(self, station_config):
        self.name = "y29"
        self._verbose = station_config.IS_VERBOSE
        self._device = MPK_API()
        self._station_config = station_config
        self._error_message = self.name + "is out of work"
        self._read_error = False
        self._version = None
        self._serial_port = None
        self._busy_ca = False
        self._port_ca = station_config.CA_PORT
        self._end_delimiter_ca = '\r\n'

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
                out = dict((str(v),int(k)) for k,v in resjson.iteritems())
            else:
                logging.error("Could not parse response message")
        else:
            out = resjson.get(param)
        if self._verbose:
            logging.info("MPK_API_RESULT:{}".format(str(resjson)))
        #logging.debug(out)
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
            print(response)
        return

    def version(self):
        if self._version is None:
            response = self._device.GetMpkApiVersionInfo()
            versionjson = json.loads(str(response))
            if self._verbose:
                pprint.pprint(versionjson)
            self._version = versionjson.get('MpkApiVersionInfo')
        return self._version

    def initialize(self):
        response = self._device.InitializeCamera(self._station_config.CAMERA_SN, False, True)
        pres = json.loads(response)
        self._serial_port = None
        self._busy_ca = False
        try:
            self._serial_port = serial.Serial(self._fixture_port,
                                              38400,
                                              parity='E',
                                              bytesize=7,
                                              stopbits=2,
                                              timeout=6,
                                              xonxoff=False,
                                              rtscts=False)
        except:
            self._serial_port = None
        if self._serial_port and not self._serial_port.isOpen():
            self._serial_port.open()

        init_result = "Init Camera Result - ErrorCode: {0}".format(pres['ErrorCode'])  # 0 means return successful
        if self._verbose:
            print(init_result)
        if not self._serial_port:
            print('Unable to connect to {0} for CA-310'.format(self._port_ca))
            time.sleep(.2)
        return init_result

    def close(self):
        self._busy_ca = True
        if self._serial_port:
            self._serial_port.close()
        self._device.CloseCommunication()

    def ready(self):
        response = json.loads(self._device.EquipmentReady())
        msg = "Ready - ErrorCode: {0}".format(response['ErrorCode'])
        if self._verbose:
            pprint.pprint(msg)
        ready_result = response['ErrorCode'] == 'Success'
        return ready_result

    def get_measurement_list(self):
        result = self._device.GetMeasurementList();
        if self._verbose:
            pprint.pprint(result)
        return json.loads(result)

    def get_list_of_meas(self):
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

    def sequence_run_step(self, stepName, patternName = '', useCamera = True, saveImages = True):
        result = self._device.RunSequenceStepByName(stepName, patternName, useCamera, saveImages)
        return json.loads(result)

    def sequence_run_step_list(self, stepList, patternName="", useCamera = True, saveImages = True):
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

    # <editor-fold desc="CA310">
    def test_connection(self):
        if not self._serial_port:
            return False
        self._write_serial(COMMAND_IDO)
        time.sleep(.5)
        rsp = self._read_response()
        if rsp and rsp[0] != "" and rsp[0][0][:2] == 'OK':
            return True
        else:
            return False

    def _write_serial(self, input_bytes):
        bytes_written = None
        while self._busy:
            time.sleep(.1)
        print('writing to ca: {0}'.format(input_bytes))
        if self._serial_port:
            self._busy = True
            try:
                self._serial_port.flush()
                bytes_written = self._serial_port.write(input_bytes.encode())
            except:
                pass
        return bytes_written

    def _read_response(self, timeout=5):
        response = ""
        cmd = None
        try:
            if self._serial_port:
                tim = time.time()
                while (re.search(self._end_delimiter_ca, response, re.IGNORECASE)
                       and time.time() - tim < timeout):
                    line_in = self._serial_port.readline()
                    if line_in != b'':
                        response += line_in.decode()
                # this used to throw assertion errors, now it logs them
            if response is "":
                print("Instrument returned no data, check instrument is connected and in remote mode")
            elif response[0:2] == "ER":
                print("Instrument returned error, maybe instrument is not in remote mode: {}".format(response))
            else:
                parsed = response.split()
                data = None
                cmd = response
                if len(parsed) > 1:
                    data = parsed[1].split(";")
                    cmd = parsed[0].split(",")
            self._busy = False
        except:
            self._busy = False
        return cmd, data

        ######################
        # info
        ######################

    def info(self):
        self._write_serial(COMMAND_IDO)
        response = self._read_response()
        return response

        ######################
        # Configuration
        ######################

    def zero_cal(self):
        self._write_serial(COMMAND_ZRC)
        time.sleep(1)
        response = self._read_response()
        return response

        ######################
        # Measurement
        ######################

    def measure_XYZ(self):
        self._write_serial(COMMAND_XYZ)
        cmd, data = self._read_response()
        return data

    def measure_xyLv(self):
        X, Y, Z = self.measureXYZ()
        xp = X / (X + Y + Z)
        yp = Y / (X + Y + Z)
        Lv = Y
        return xp, yp, Lv
    # </editor-fold>


if __name__ == "__main__":
    import sys

    sys.path.append(r'..\..')
    import station_config

    verbose = True
    newDatabaseName = str(datetime.now().strftime("%y%m%d%H%M%S")) + ".ttxm"
    databasePath = r"C:\Radiant Vision Systems Data\TrueTest\\" + newDatabaseName
    databasePath = r'G:\oculus_sunny_t3\pixel\1PR000000Q9265_pancake_pixel-01_20191217-161952.ttxm'
    sequencePath = r"C:\oculus\factory_test_omi\factory_test_stations\test_station\test_equipment\algorithm\Y29 particle Defect.seqxc"

    station_config.load_station('pancake_pixel')
    station_config.CAMERA_SN = "Demo"
    the_instrument = pancakemuniEquipment(station_config)

    ver = the_instrument.version()
    pprint.pprint(ver)

    pprint.pprint("ready before init :{}".format(the_instrument.ready()))
    isinit = the_instrument.initialize()
    pprint.pprint("ready after init :{}".format(the_instrument.ready()))
    # print  "PrepareForRun after init:{}" .format(the_instrument.prepare_for_run())

    # the_instrument.create_database(databasePath)
    the_instrument.set_database(databasePath)
    the_instrument.set_sequence(sequencePath)
    ss2 = the_instrument.sequence_run_step('ParticleDefects W255', '', False, False)
    print(ss2)
