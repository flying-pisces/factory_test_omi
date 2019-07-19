import os
import json
import clr
clr.AddReference('System.Drawing')
apipath = os.path.join(os.getcwd(), "MPK_API.dll")
from MPK_API import *
clr.AddReference(apipath)
from System.Drawing import *
from System import String
import numpy as np
import sys
sys.path.append("../")
sys.path.append("../../")
sys.path.append("../../../")
import hardware_station_common.test_station.test_equipment
from datetime import datetime
import StringIO

class pancakeuniformityEquipmentError(Exception):
    pass

class pancakeuniformityEquipment(hardware_station_common.test_station.test_equipment.TestEquipment):
    def __init__(self, verbose=False, focus_distance=0.55, lens_aperture=8.0, auto_exposure=False, cx =0, cy =0, cl =0, cw =0):
        self.name = "i16"
        self._verbose = verbose
        self._device = MPK_API()
        self._error_message = self.name + "is out of work"
        self._read_error = False
        self._focus_distance = focus_distance; #dimension of m
        self._lens_aperture = lens_aperture;
        self._auto_exposure = auto_exposure;
        self._rect = Rectangle(cx, cy, cl, cw);
     
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
        init_result = int(str(String.Format("Init Camera Result - ErrorCode: {0}", response['ErrorCode'])).split(":")[1]) # 0 means return successful
        if self._verbose:
            print(init_result)
        return init_result
#####################################################################################################
######### Measurement Setup ##################
    # CreateMeasurementSetup(patternName as String, redEFilterxposure as Single, greenFilterExposure as Single,
#                       blueFilterExposure as Single, xbFilterExposure as Single, focusDistance as Single,
#                       lenAperture as Single, autoAdjustExposure as Boolean, subframeRegion as Rectangle) 
    def measurementsetup(self, pattern, eR, eG, eB, eXB, focus, aperture, is_autoexp, rect, distance_unit, spectral_response, rotation):
        meas_setup = self._device.CreateMeasurementSetup(pattern,
                                           eR, eG, eB, eXB,
                                           focus,
                                           aperture,
                                           is_autoexp, rect, distance_unit, spectral_response, rotation)
        response = int(str(String.Format("Measurement Setup Result for " + pattern +" - ErrorCode: {0}", meas_setup['ErrorCode'])).split(":")[1])
        if self._verbose:
            print response
        return response 
#colorCals = mpkapi.GetColorCalibrationList()
#print('Color Cals:')
#print(colorCals)
    def get_colorcal_key(self, cc_name):
        response = str(self._device.GetColorCalibrationList()).replace('\r\n', '')
        cc_json = json.loads(response)
        if cc_name in cc_json.values():
            for key, value in cc_json.iteritems():
                if cc_name == value:
                    break
        else:
            raise auounifEquipmentError("Color calibration not in list {}".format(cc_json.values))
        return int(key)
    
    def get_colorshiftcal_key(self, cc_name):
        response = str(self._device.GetColorShiftCalibrationList()).replace('\r\n', '')
        cc_json = json.loads(response)
        if cc_name in cc_json.values():
            for key, value in cc_json.iteritems():
                if cc_name == value:
                    break
        else:
            raise auounifEquipmentError("Shift calibration not in list {}".format(cc_json.values))
        return int(key)
    
    def get_imagescalecal_key(self, cc_name):
        response = str(self._device.GetImageScaleCalibrationList()).replace('\r\n', '')
        cc_json = json.loads(response)
        if cc_name in cc_json.values():
            for key, value in cc_json.iteritems():
                if cc_name == value:
                    break
        else:
            raise auounifEquipmentError("Scale calibration not in list {}".format(cc_json.values))
        return int(key)



######################
#SetCalibration(measurementSetupName As String, colorCalibrationID As Integer, imageScaleID As Integer, colorShiftID As Integer)

#setwhitecalibration = mpkapi.SetCalibrations("White", 20, 3, 4)
#print('Set Calibrations for White')
#print(setwhitecalibration)

    def setcalibrationid(self, meassetup, colorcalibrationid, imagescaleid, colorshiftid):
        response = self._device.SetCalibrations(meassetup, colorcalibrationid, imagescaleid, colorshiftid)
        if self._verbose:
            print(response)


#resultSN1 = mpkapi.SetSerialNumber("SN1", 0)
#print('Serial 1 Set')
#print(resultSN1)
    def setsn(self, sn, channel=0):
        response = self._device.SetSerialNumber(sn, channel)
        if self._verbose:
            print(response)

#getSerialResult1 = mpkapi.ReadSerialNumbers(0)
#print(getSerialResult1)
            
    def getsn(self, channel=0):
        response = self._device.ReadSerialNumber(channel)
        if self._verbose:
            print(response)
#####################################################################################################
## Camera Control

# CaptureMeasurement(measurementSetupName as String, imageKey as String, saveToDatabase as Boolean)
    def capture(self, pattern, imagekey="photopickey", SaveToDatabase = False):
        response = self._device.CaptureMeasurement(pattern, imagekey, SaveToDatabase)
        if self._verbose:
            print(String.Format("Measurement Capture Result for " + pattern + " - Image Key: {0}", response['Imagekey']))
        return String.Format("Measurement Capture Result for " + pattern + " - Image Key: {0}", response['Imagekey'])
        

#####################################################################################################
## Image Analysis

#result = mpkapi.PrepareForRun()
#print(String.Format("Prepare For Run - ErrorCode: {0}", result['ErrorCode']))


    def get_raw_data(self, imageHandle):
        start_time =datetime.now()
        response = self._device.GetRawData(imageHandle)
        num_chan = response.get_Count()
        ## channel will be Lv, Cx, Cy, u', v'
        ret = {}
        for c in range(num_chan):
            chan = ['Lv', "Cx", "Cy", "u'", "v'"][c]
            d = response.get_Item(c)
            xl = d.GetLength(0)
            yl = d.GetLength(1)
            arr = np.array(list(d), np.float32).reshape((xl,yl))
            arr = np.rot90(arr, 3)
            arr = np.fliplr(arr)
            ret[chan] = arr
        print "Loaded camera measurement in {}".format(str(datetime.now() - start_time))
        return ret

    def export_data(self, imageHandle, path, filename):
        raw = self.get_raw_data(imageHandle)
        np.savez_compressed(os.path.join(path, filename), **raw)

    def run_analysis_by_name(self,analysisName, imageKey, xmlParameterSet=""):
        if isinstance(imageKey, list):
            imageKey = Array[String](imageKey)
        response = self._device.RunAnalysisByName(analysisName, imageKey, xmlParameterSet)
#        return self._parse_result(response)

    def prepareanalysis(self):
        response = str(self._device.PrepareForRun).replace('\r\n', '')
        prepareforrunjson = json.loads(response)
        isprepareforrun = "0" in prepareforrunjson.values()
        if self._verbose:
            print(response)
        return isprepareforrun
            
    def get_last_results(self):
        response = self._device.GetLastResults()
        results = []
        for i in range(response.get_Count()):
            res_str = str(response.get_Item(i).encode('ascii','ignore'))
            results.append(res_str.split(","))
        return results

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
            arr = np.array(list(d), np.float32).reshape((xl,yl))
            arr = np.rot90(arr, 3)
            arr = np.fliplr(arr)
            ret[chan] = arr
        print "Loaded analysis measurement in {}".format(str(datetime.now() - start_time))
        return ret


if __name__ == "__main__":
    verbose=True
    is_autoexp=False
    cx = 1847 #Left
    cy = 997 #Top
    cl = 1120 #Width
    cw = 1204 #Height
    rect = Rectangle(cx, cy, cl, cw)
    eR = 113.0
    eG = 113.0
    eB = 113.0
    eXB = 113.0
    focus = 0.575
    aperture = 8.0
    distance_unit = 'Millimeters'
    spectral_response = 'Photometric'
    rotation = 0
    the_instrument = pancakeuniformityEquipment(verbose, focus, aperture, is_autoexp, cx, cy, cl, cw)
    sn = the_instrument.serialnumber()
    sn = "159486608"
    version = the_instrument.version()
    the_instrument.init(sn)
    pattern = "W255"
    the_instrument.measurementsetup(pattern, eR, eG, eB, eXB, focus, aperture, is_autoexp, rect, distance_unit, spectral_response, rotation)

#    the_instrument.measurementsetup("White", 113, 113, 113)

    color_cal = 'camera_color_cal'
    scale_cal = 'image_scale_cal'
    shift_cal = '159486608 Color Shift Correction'

    colorcalibrationid = the_instrument.get_colorcal_key(color_cal)
    imagescaleid = the_instrument.get_imagescalecal_key(scale_cal)
    colorshiftid = the_instrument.get_colorshiftcal_key(shift_cal)


    colorcalibrationid = the_instrument.get_colorcal_key(color_cal)
    imagescaleid = the_instrument.get_imagescalecal_key(scale_cal)
    colorshiftid = the_instrument.get_colorshiftcal_key(shift_cal)

    the_instrument.setcalibrationid(pattern, colorcalibrationid, imagescaleid, colorshiftid)
    imagekey = pattern
    is_savedb = True
    flag = the_instrument.capture(pattern, imagekey, True)
    print flag

    export_name = "tempdata"
    output_dir = os.getcwd()
    the_instrument.export_data(pattern, output_dir, export_name)
    analysis_item = "UniformityRegister"
    override = ""
    the_instrument.run_analysis_by_name(analysis_item, pattern, override)
    filename = export_name + ".csv"
    analysis_result = the_instrument.get_last_results()
    mesh_data = the_instrument.get_last_mesh()


