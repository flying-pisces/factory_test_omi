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

class pancakeuniformityEquipmentError(Exception):
    pass
	
class pancakeuniformityEquipment(hardware_station_common.test_station.test_equipment.TestEquipment):
    def __init__(self, verbose=False, focus_distance=0.575, lens_aperture=8.0, auto_exposure=False, cx =0, cy =0, cl =0, cw =0):
        self.name = "i16"
        self._verbose = verbose
        self._device = MPK_API()
        self._error_message = self.name + "is out of work"
        self._read_error = False
        self._focus_distance = focus_distance; #dimension of m
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
        response = self._device.InitializeCamera(sn, False, True)
        init_result = int(str(String.Format("Init Camera Result - ErrorCode: {0}", response['ErrorCode'])).split(":")[1]) # 0 means return successful
        if self._verbose:
            print(init_result)
        return init_result

    def uninit(self):
        response = self._device.CloseCommunication()
        return int(self._parse_result(response))

    def ready(self):
        response = self._device.EquipmentReady()
        ready_result = int(str(String.Format("Ready - ErrorCode: {0}", response['ErrorCode'])).split(":")[1])
        return not bool(ready_result)
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
            raise pancakeuniformityEquipmentError("Color calibration not in list {}".format(cc_json.values))
        return int(key)
    
    def get_colorshiftcal_key(self, cc_name):
        response = str(self._device.GetColorShiftCalibrationList()).replace('\r\n', '')
        cc_json = json.loads(response)
        if cc_name in cc_json.values():
            for key, value in cc_json.iteritems():
                if cc_name == value:
                    break
        else:
            raise pancakeuniformityEquipmentError("Shift calibration not in list {}".format(cc_json.values))
        return int(key)
    
    def get_imagescalecal_key(self, cc_name):
        response = str(self._device.GetImageScaleCalibrationList()).replace('\r\n', '')
        cc_json = json.loads(response)
        if cc_name in cc_json.values():
            for key, value in cc_json.iteritems():
                if cc_name == value:
                    break
        else:
            raise pancakeuniformityEquipmentError("Scale calibration not in list {}".format(cc_json.values))
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


############ DATA EXPORT ##################################################
#could pass in imageKey as array of strings, or single string
    def export_data(self,imageHandle, path, filename):
        response = self._device.ExportData(imageHandle, path, filename)
        return self._parse_result(response)

    def delete_file(self, filename):
        os.remove(filename)

    def get_raw_data(self, imageHandle, temp_dir , filename):
        self.export_data(imageHandle, temp_dir, filename)
        cam_data = self.load_camera_measurement(temp_dir + filename + ".csv")
        return cam_data

    def load_camera_measurement(self, filename):
        with open(filename) as f:
            start_time = datetime.now()
            meas_data = f.read()
            out = {}
            split_data = meas_data.split("\n\n")
            info = split_data[0].split("\n")
            out['serial'] = info[0].split(" ")[1]
            out['date'] = info[1].split(" ")[1]
            out['time'] = info[2].split(" ")[1]
            measname = ""

            for i in range(1, len(split_data)):
                if len(split_data[i]) <= 2 and split_data[i] in "LvCxCy":
                    measname = split_data[i]
                else:
                    meas = split_data[i]
                    floatmeas = np.genfromtxt(StringIO.StringIO(meas), dtype=np.float16)
                    out[measname] = floatmeas
            self.logger.debug("Loaded camera measurement in {}".format(str(datetime.now()-start_time)))
            return out
#####################################################################################################
## Image Analysis

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

    def run_analysis_by_name(self,analysisName, imageKey, xmlParameterSet=""):
        if isinstance(imageKey, list):
            imageKey = Array[String](imageKey)
        response = self._device.RunAnalysisByName(analysisName, imageKey, xmlParameterSet)
#        return self._parse_result(response)




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
          raise pancakeuniformityEquipmentError(e)

if __name__ == "__main__":
    verbose=True
    focus_distance=0.50
    lens_aperture=2.8
    auto_exposure=False
    cx = 1916 #Left
    cy = 831 #Top
    cl = 1252 #Width
    cw = 1405 #Height
#    rect = Rectangle(cx, cy, cl, cw)
    the_instrument = pancakeuniformityEquipment(verbose, focus_distance, lens_aperture, auto_exposure, cx, cy, cl, cw)
    sn = the_instrument.serialnumber()
    sn = "159185561"
    
    print  "ready before init :{}" .format(the_instrument.ready())
    isinit = the_instrument.init(sn)
    print  "ready after init :{}" .format(the_instrument.ready())
    print  "PrepareForRun after init:{}" .format(the_instrument.prepare_for_run())

    version = the_instrument.version()
    the_instrument.init(sn)
    pattern = "W255"
    eR = 113.0
    eG = 113.0
    eB = 113.0
    eXB = 113.0
    focus = 0.575
    aperture = 8.0
    is_autoexp = False
    rect = Rectangle(cx, cy, cl, cw)
    distance_unit = 'Millimeters'
    spectral_response = 'Photometric'
    rotation = 0
    the_instrument.measurementsetup(pattern, eR, eG, eB, eXB, focus, aperture, is_autoexp, rect, distance_unit, spectral_response, rotation)

    color_cal = 'camera_color_cal_255_20180116'
    scale_cal = 'image_scale_cal_20180116'
    shift_cal = '158763491 Color Shift Correction'

    colorcalibrationid = the_instrument.get_colorcal_key(color_cal)
    imagescaleid = the_instrument.get_imagescalecal_key(scale_cal)
    colorshiftid = the_instrument.get_colorshiftcal_key(shift_cal)
    
    the_instrument.setcalibrationid(pattern, colorcalibrationid, imagescaleid, colorshiftid) 

#    imagekey = "whitekey" # can be set by end user.
    imagekey = pattern
    isSavetoDatabase = True
    the_instrument.capture(pattern, imagekey, isSavetoDatabase)

    path = os.getcwd()
    filename = "temp.csv"
    the_instrument.export_data(imagekey, path, filename)

    the_instrument.prepare_for_run()
    analysis_item = 'UniformityRegister'
    override = ''
    the_instrument.run_analysis_by_name(analysis_item, imageKey=imagekey)
    mesh_data = the_instrument.get_last_mesh()
    if mesh_data != {}:
        output_data = StringIO.StringIO()
        np.savez_compressed(output_data, **mesh_data)
        npzdata = output_data.getvalue()
        print "npzdata : {}".format(npzdata)
        #also calculate some statistical infdir()o about the measurement
        for c in ["Lv", "Cx", "Cy" "u'", "v'"]:
            cdata = mesh_data.get(c)
            if cdata is not None:
                cmean = np.mean(cdata, dtype=np.float32)
                cmax = cdata.max()
                cmin = cdata.min()
                cstd = np.std(cdata, dtype=np.float32)
                print c





