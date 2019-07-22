import hardware_station_common.test_station.test_equipment
import os
import json
import clr
clr.AddReference('System.Drawing')
apipath = os.path.join(r'C:\oculus\factory_test_omi\factory_test_stations\test_station\test_equipment\MPK_API.dll')
clr.AddReference(apipath)
from MPK_API import *
from System.Drawing import *
from System import String
import numpy as np
import sys
sys.path.append("../")
sys.path.append("../../")
sys.path.append("../../../")
from datetime import datetime
import StringIO
import logging


class pancakepixelEquipmentError(Exception):
    pass


class pancakepixelEquipment(hardware_station_common.test_station.test_equipment.TestEquipment):
    def __init__(self, verbose=False, focus_distance=0.55, lens_aperture=8.0, auto_exposure=False, cx=0, cy=0, cl=0,
                 cw=0):
        self.name = "y29"
        self._verbose = verbose
        self._device = MPK_API()
        self._error_message = self.name + "is out of work"
        self._read_error = False
        self._focus_distance = focus_distance;  # dimension of m
        self._lens_aperture = lens_aperture;
        self._auto_exposure = auto_exposure;
        self._rect = Rectangle(cx, cy, cl, cw);


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
        response = self._device.GetCameraSerial()
        sn = str(String.Format("Camera Serial Number: {0}", response['CameraSerial']))
        if self._verbose:
            print(sn)
        return

    def version(self):
        response = self._device.GetMpkApiVersionInfo()
        versionjson = json.loads(str(response))
        versioninfo = str(versionjson.values())
        if self._verbose:
            print(versionjson)
        return versioninfo

    def init(self, sn):
        response = self._device.InitializeCamera(sn, True, True)
        init_result = int(str(String.Format("Init Camera Result - ErrorCode: {0}", response['ErrorCode'])).split(":")[
                              1])  # 0 means return successful
        if self._verbose:
            print(init_result)
        return init_result

    def uninit(self):
        response = self._device.CloseCommunication()
        return int(self._parse_result(response))

    #####################################################################################################
    ######### Measurement Setup ##################
    # CreateMeasurementSetup(patternName as String, redEFilterxposure as Single, greenFilterExposure as Single,
    #                       blueFilterExposure as Single, xbFilterExposure as Single, focusDistance as Single,
    #                       lenAperture as Single, autoAdjustExposure as Boolean, subframeRegion as Rectangle)
    def measurementsetup(self, pattern, eR, eG, eB, eXB, focus, aperture, is_autoexp, rect, distance_unit,
                         spectral_response, rotation):
        meas_setup = self._device.CreateMeasurementSetup(pattern,
                                                         eR, eG, eB, eXB,
                                                         focus,
                                                         aperture,
                                                         is_autoexp, rect, distance_unit, spectral_response, rotation)
        response = int(str(String.Format("Measurement Setup Result for " + pattern + " - ErrorCode: {0}",
                                         meas_setup['ErrorCode'])).split(":")[1])
        if self._verbose:
            print response
        return response

    # colorCals = mpkapi.GetColorCalibrationList()
    # print('Color Cals:')
    # print(colorCals)
    def get_colorcal_key(self, cc_name):
        response = str(self._device.GetColorCalibrationList()).replace('\r\n', '')
        cc_json = json.loads(response)
        if cc_name in cc_json.values():
            for key, value in cc_json.iteritems():
                if cc_name == value:
                    break
        else:
            raise pancakepixelEquipmentError("Color calibration not in list {}".format(cc_json.values))
        return int(key)

    def get_colorshiftcal_key(self, cc_name):
        response = str(self._device.GetColorShiftCalibrationList()).replace('\r\n', '')
        cc_json = json.loads(response)
        if cc_name in cc_json.values():
            for key, value in cc_json.iteritems():
                if cc_name == value:
                    break
        else:
            raise pancakepixelEquipmentError("Shift calibration not in list {}".format(cc_json.values))
        return int(key)

    def get_imagescalecal_key(self, cc_name):
        response = str(self._device.GetImageScaleCalibrationList()).replace('\r\n', '')
        cc_json = json.loads(response)
        if cc_name in cc_json.values():
            for key, value in cc_json.iteritems():
                if cc_name == value:
                    break
        else:
            raise pancakepixelEquipmentError("Scale calibration not in list {}".format(cc_json.values))
        return int(key)

    ######################
    # SetCalibration(measurementSetupName As String, colorCalibrationID As Integer, imageScaleID As Integer, colorShiftID As Integer)

    # setwhitecalibration = mpkapi.SetCalibrations("White", 20, 3, 4)
    # print('Set Calibrations for White')
    # print(setwhitecalibration)

    def setcalibrationid(self, meassetup, colorcalibrationid, imagescaleid, colorshiftid):
        response = self._device.SetCalibrations(meassetup, colorcalibrationid, imagescaleid, colorshiftid)
        if self._verbose:
            print(response)

    # resultSN1 = mpkapi.SetSerialNumber("SN1", 0)
    # print('Serial 1 Set')
    # print(resultSN1)
    def setsn(self, sn, channel=0):
        response = self._device.SetSerialNumber(sn, channel)
        if self._verbose:
            print(response)

    # getSerialResult1 = mpkapi.ReadSerialNumbers(0)
    # print(getSerialResult1)

    def getsn(self, channel=0):
        response = self._device.ReadSerialNumber(channel)
        if self._verbose:
            print(response)

    #####################################################################################################
    ## Camera Control

    # CaptureMeasurement(measurementSetupName as String, imageKey as String, saveToDatabase as Boolean)
    def capture(self, pattern, imagekey="photopickey", SaveToDatabase=False):
        response = self._device.CaptureMeasurement(pattern, imagekey, SaveToDatabase)
        if self._verbose:
            print(
                String.Format("Measurement Capture Result for " + pattern + " - Image Key: {0}", response['Imagekey']))
        return String.Format("Measurement Capture Result for " + pattern + " - Image Key: {0}", response['Imagekey'])

    #####################################################################################################
    ## Image Analysis

    # result = mpkapi.PrepareForRun()
    # print(String.Format("Prepare For Run - ErrorCode: {0}", result['ErrorCode']))

    def prepare_for_run(self):
        response = self._device.PrepareForRun()
        return not bool(int(self._parse_result(response)))

    def get_last_results(self):
        response = self._device.GetLastResults()
        results = []
        for i in range(response.get_Count()):
            res_str = str(response.get_Item(i).encode('ascii', 'ignore'))
            results.append(res_str.split(","))
        return results

    def get_raw_data(self, imageHandle):
        start_time = datetime.now()
        response = self._device.GetRawData(imageHandle)
        num_chan = response.get_Count()
        ## channel will be Lv, Cx, Cy, u', v'
        ret = {}
        for c in range(num_chan):
            chan = ['Lv', "Cx", "Cy", "u'", "v'"][c]
            d = response.get_Item(c)
            xl = d.GetLength(0)
            yl = d.GetLength(1)
            arr = np.array(list(d), np.float32).reshape((xl, yl))
            arr = np.rot90(arr, 3)
            arr = np.fliplr(arr)
            ret[chan] = arr
        print "Loaded camera measurement in {}".format(str(datetime.now() - start_time))
        return ret

    def export_data(self, imageHandle, path, filename):
        raw = self.get_raw_data(imageHandle)
        np.savez_compressed(os.path.join(path, filename), **raw)

    def run_analysis_by_name(self, analysisName, imageKey, xmlParameterSet=""):
        if isinstance(imageKey, list):
            imageKey = Array[String](imageKey)
        response = self._device.RunAnalysisByName(analysisName, imageKey, xmlParameterSet)
        print(response)

    #        return self._parse_result(response)

    def prepareanalysis(self):
        response = str(self._device.PrepareForRun).replace('\r\n', '')
        prepareforrunjson = json.loads(response)
        isprepareforrun = "0" in prepareforrunjson.values()
        if self._verbose:
            print(response)
        return isprepareforrun

    def get_last_mesh(self):
        start_time = datetime.now()
        response = self._device.GetLastMeshData()
        num_chan = response.get_Count()
        # channels are in the order Lv, Cx, Cy, u', v'.
        ret = {}
        for c in range(num_chan):
            chan = ['Lv', "Cx", "Cy", "u'", "v'"][c]

            d = response.get_Item(c)
            xl = d.GetLength(0)
            yl = d.GetLength(1)
            arr = np.array(list(d), np.float32).reshape((xl, yl))
            arr = np.rot90(arr, 3)
            arr = np.fliplr(arr)
            ret[chan] = arr
        print "Loaded analysis measurement in {}".format(str(datetime.now() - start_time))
        return ret

#####################################################################################################
## flush measurements
    def flush_measurements(self):
        response = self._device.FlushMeasurements()
        return self._parse_result(response)

    def flush_measurement_setups(self):
        response = self._device.FlushMeasurementSetups()
        return self._parse_result(response)

    def clean_analysis_dir(self, simulate=False):
        try:
          self.clean_dir(self.analysis_dir, simulate=simulate)
          for f in os.listdir(self.analysis_dir):
            file_path = os.path.join(self.analysis_dir, f)
            if os.path.isdir(file_path):
                mesh_path = os.path.join(file_path, "Mesh")
                self.clean_dir(mesh_path, extension=[".csv", ".txt"],simulate=simulate)
        except Exception as e:
          raise pancakepixelEquipmentError(e)

if __name__ == "__main__":
    import sys
    sys.path.append(r'../../')
    import test_station
    verbose = True
    is_autoexp = False
    cx = 0  # Left
    cy = 0  # Top
    cl = 0  # Width
    cw = 0  # Height
    rect = Rectangle(cx, cy, cl, cw)
    eR = 113.0
    eG = 113.0
    eB = 113.0
    eXB = 113.0
    focus = 0.471
    aperture = 8.0
    distance_unit = 'Millimeters'
    spectral_response = 'Photometric'
    rotation = 90
    the_instrument = pancakepixelEquipment(verbose, focus, aperture, is_autoexp, cx, cy, cl, cw)
    sn = the_instrument.serialnumber()
    sn = "91738177"
    version = the_instrument.version()
    the_instrument.init(sn)
    the_instrument.flush_measurement_setups()
    the_instrument.flush_measurements()
    the_instrument.prepare_for_run()

    pattern = "W255"
    the_instrument.measurementsetup(pattern, eR, eG, eB, eXB, focus, aperture, is_autoexp, rect, distance_unit,
                                    spectral_response, rotation)

    #    the_instrument.measurementsetup("White", 113, 113, 113)

    color_cal = 'camera_color_cal1'
    scale_cal = 'image_scale_cal1'
    shift_cal = '(None)'

    colorcalibrationid = the_instrument.get_colorcal_key(color_cal)
    imagescaleid = the_instrument.get_imagescalecal_key(scale_cal)
    colorshiftid = the_instrument.get_colorshiftcal_key(shift_cal)

    the_instrument.setcalibrationid(pattern, colorcalibrationid, imagescaleid, colorshiftid)
    imagekey = pattern
    is_savedb = True
    flag = the_instrument.capture(pattern, imagekey, True)
    # print flag

    export_name = "tempdata"
    output_dir = os.getcwd()
    the_instrument.export_data(pattern, output_dir, export_name)
    analysis_item = "ParticleDefectsW"
    override = ""
    the_instrument.run_analysis_by_name(analysis_item, pattern, override)
    filename = export_name + ".csv"
    analysis_result = the_instrument.get_last_results()
    mesh_data = the_instrument.get_last_mesh()


