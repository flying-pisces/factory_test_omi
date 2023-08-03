import hardware_station_common.test_station.test_equipment
import os
import json
import clr
clr.AddReference('System.Drawing')
clr.AddReference('System')
from System.Collections.Generic import List
import System
apipath = os.path.join(r"C:\Program Files\Radiant Vision Systems\TrueTest 1.7\MPK_API.dll")
clr.AddReference(apipath)
from MPK_API_CS import *
from System.Drawing import *
from System import String
import numpy as np
import sys
import pprint
sys.path.append("../")
sys.path.append("../../")
sys.path.append("../../../")
from datetime import datetime
import logging

class pancakeuniformityEquipmentError(Exception):
    pass
	
class pancakeuniformityEquipment(hardware_station_common.test_station.test_equipment.TestEquipment):
    def __init__(self, station_config):
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
        if verbose:
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

    def export_measurement(self, imageName, exportPath, exportFilename = "", resX = 0, resY = 0):
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

#####################################################################################################
######### Measurement Setup ##################
    # CreateMeasurementSetup(patternName as String, redEFilterxposure as Single, greenFilterExposure as Single,
#                       blueFilterExposure as Single, xbFilterExposure as Single, focusDistance as Single,
#                       lenAperture as Single, autoAdjustExposure as Boolean, subframeRegion as Rectangle) 
#     def measurementsetup(self, pattern, eR, eG, eB, eXB, focus, aperture, is_autoexp, rect, distance_unit, spectral_response, rotation):
#         meas_setup = self._device.CreateMeasurementSetup(pattern,
#                                            eR, eG, eB, eXB,
#                                            focus,
#                                            aperture,
#                                            is_autoexp, rect, distance_unit, spectral_response, rotation)
#         response = int(str(String.Format("Measurement Setup Result for " + pattern +" - ErrorCode: {0}", meas_setup['ErrorCode'])).split(":")[1])
#         if self._verbose:
#             print response
#         return response
#colorCals = mpkapi.GetColorCalibrationList()
#print('Color Cals:')
#print(colorCals)
    # def get_colorcal_key(self, cc_name):
    #     response = str(self._device.GetColorCalibrationList()).replace('\r\n', '')
    #     cc_json = json.loads(response)
    #     if cc_name in cc_json.values():
    #         for key, value in cc_json.iteritems():
    #             if cc_name == value:
    #                 break
    #     else:
    #         raise pancakeuniformityEquipmentError("Color calibration not in list {}".format(cc_json.values))
    #     return int(key)
    #
    # def get_colorshiftcal_key(self, cc_name):
    #     response = str(self._device.GetColorShiftCalibrationList()).replace('\r\n', '')
    #     cc_json = json.loads(response)
    #     if cc_name in cc_json.values():
    #         for key, value in cc_json.iteritems():
    #             if cc_name == value:
    #                 break
    #     else:
    #         raise pancakeuniformityEquipmentError("Shift calibration not in list {}".format(cc_json.values))
    #     return int(key)
    #
    # def get_imagescalecal_key(self, cc_name):
    #     response = str(self._device.GetImageScaleCalibrationList()).replace('\r\n', '')
    #     cc_json = json.loads(response)
    #     if cc_name in cc_json.values():
    #         for key, value in cc_json.iteritems():
    #             if cc_name == value:
    #                 break
    #     else:
    #         raise pancakeuniformityEquipmentError("Scale calibration not in list {}".format(cc_json.values))
    #     return int(key)




######################
#SetCalibration(measurementSetupName As String, colorCalibrationID As Integer, imageScaleID As Integer, colorShiftID As Integer)

#setwhitecalibration = mpkapi.SetCalibrations("White", 20, 3, 4)
#print('Set Calibrations for White')
#print(setwhitecalibration)

    # def setcalibrationid(self, meassetup, colorcalibrationid, imagescaleid, colorshiftid):
    #     response = self._device.SetCalibrations(meassetup, colorcalibrationid, imagescaleid, colorshiftid)
    #     if self._verbose:
    #         print(response)


#resultSN1 = mpkapi.SetSerialNumber("SN1", 0)
#print('Serial 1 Set')
#print(resultSN1)
    # def setsn(self, sn, channel=0):
    #     response = self._device.SetSerialNumber(sn, channel)
    #     if self._verbose:
    #         print(response)

#getSerialResult1 = mpkapi.ReadSerialNumbers(0)
#print(getSerialResult1)
            
#####################################################################################################
## Camera Control

# CaptureMeasurement(measurementSetupName as String, imageKey as String, saveToDatabase as Boolean)
#     def capture(self, pattern, imagekey="photopickey", SaveToDatabase = False):
#         response = self._device.CaptureMeasurement(pattern, imagekey, SaveToDatabase)
#         if self._verbose:
#             print(String.Format("Measurement Capture Result for " + pattern + " - Image Key: {0}", response['Imagekey']))
#         return String.Format("Measurement Capture Result for " + pattern + " - Image Key: {0}", response['Imagekey'])


############ DATA EXPORT ##################################################
#could pass in imageKey as array of strings, or single string
    # def export_data(self,imageHandle, path, filename):
    #     response = self._device.ExportData(imageHandle, path, filename)
    #     return self._parse_result(response)
    #
    # def delete_file(self, filename):
    #     os.remove(filename)
    #
    # def get_raw_data(self, imageHandle, temp_dir , filename):
    #     self.export_data(imageHandle, temp_dir, filename)
    #     cam_data = self.load_camera_measurement(temp_dir + filename + ".csv")
    #     return cam_data
    #
    # def load_camera_measurement(self, filename):
    #     with open(filename) as f:
    #         start_time = datetime.now()
    #         meas_data = f.read()
    #         out = {}
    #         split_data = meas_data.split("\n\n")
    #         info = split_data[0].split("\n")
    #         out['serial'] = info[0].split(" ")[1]
    #         out['date'] = info[1].split(" ")[1]
    #         out['time'] = info[2].split(" ")[1]
    #         measname = ""
    #
    #         for i in range(1, len(split_data)):
    #             if len(split_data[i]) <= 2 and split_data[i] in "LvCxCy":
    #                 measname = split_data[i]
    #             else:
    #                 meas = split_data[i]
    #                 floatmeas = np.genfromtxt(StringIO.StringIO(meas), dtype=np.float16)
    #                 out[measname] = floatmeas
    #         self.logger.debug("Loaded camera measurement in {}".format(str(datetime.now()-start_time)))
    #         return out

#####################################################################################################
## Image Analysis

#     def prepare_for_run(self):
#         response = self._device.PrepareForRun()
#         return not bool(int(self._parse_result(response)))
#
#     def get_last_results(self):
#         response = self._device.GetLastResults()
#         results = []
#         for i in range(response.get_Count()):
#             res_str = str(response.get_Item(i).encode('ascii', 'ignore'))
#             results.append(res_str.split(","))
#         return results
#
#     def run_analysis_by_name(self,analysisName, imageKey, xmlParameterSet=""):
#         if isinstance(imageKey, list):
#             imageKey = Array[String](imageKey)
#         response = self._device.RunAnalysisByName(analysisName, imageKey, xmlParameterSet)
# #        return self._parse_result(response)
#
#
#
#
#     def get_last_mesh(self):
#         start_time = datetime.now()
#         response = self._device.GetLastMeshData()
#         num_chan = response.get_Count()
#         # channels are in the order Lv, Cx, Cy, u', v'.
#         ret = {}
#         for c in range(num_chan):
#             chan = ['Lv', "Cx", "Cy", "u'", "v'"][c]
#
#             d = response.get_Item(c)
#             xl = d.GetLength(0)
#             yl = d.GetLength(1)
#             arr = np.array(list(d), np.float32).reshape((xl,yl))
#             arr = np.rot90(arr, 3)
#             arr = np.fliplr(arr)
#             ret[chan] = arr
#         print "Loaded analysis measurement in {}".format(str(datetime.now() - start_time))
#         return ret

#####################################################################################################
## flush measurements
    # def flush_measurements(self):
    #     response = self._device.FlushMeasurements()
    #     return self._parse_result(response)
    #
    # def flush_measurement_setups(self):
    #     response = self._device.FlushMeasurementSetups()
    #     return self._parse_result(response)
    #
    # def clean_analysis_dir(self, simulate=False):
    #     try:
    #       self.clean_dir(self.analysis_dir, simulate=simulate)
    #       for f in os.listdir(self.analysis_dir):
    #         file_path = os.path.join(self.analysis_dir, f)
    #         if os.path.isdir(file_path):
    #             mesh_path = os.path.join(file_path, "Mesh")
    #             self.clean_dir(mesh_path, extension=[".csv", ".txt"],simulate=simulate)
    #     except Exception as e:
    #       raise pancakeuniformityEquipmentError(e)

if __name__ == "__main__":
    import sys
    sys.path.append(r'..\..')
    import station_config
    verbose = True

    # focus_distance=0.50
    # lens_aperture=2.8
    # auto_exposure=False
    # cx = 1916 #Left
    # cy = 831 #Top
    # cl = 1252 #Width
    # cw = 1405 #Height
#    rect = Rectangle(cx, cy, cl, cw)

    newDatabaseName = str(datetime.now().strftime("%y%m%d%H%M%S")) + ".ttxm"
    databasePath = r"C:\Radiant Vision Systems Data\TrueTest\\" + newDatabaseName
    databasePath = r'C:\oculus\factory_test_omi\factory_test_stations\factory-test_logs\1PR00001UB9262_pancake_pixel-02_20190726-220417_P.ttxm'
    sequencePath = r"C:\oculus\factory_test_omi\factory_test_stations\test_station\test_equipment\algorithm\Myzy_Sequence_10-3-19.seqx"

    station_config.load_station('pancake_uniformity')
    the_instrument = pancakeuniformityEquipment(station_config)
    print  "ready before init :{}" .format(the_instrument.ready())
    isinit = the_instrument.initialize()
    print  "ready after init :{}" .format(the_instrument.ready())
    # print  "PrepareForRun after init:{}" .format(the_instrument.prepare_for_run())

    # the_instrument.create_database(databasePath)
    the_instrument.set_database(databasePath)
    the_instrument.set_sequence(sequencePath)

    # version = the_instrument.version()

    # the_instrument.init(sn)
    # pattern = "W255"
    # eR = 113.0
    # eG = 113.0
    # eB = 113.0
    # eXB = 113.0
    # focus = 0.575
    # aperture = 8.0
    # is_autoexp = False
    # rect = Rectangle(cx, cy, cl, cw)
    # distance_unit = 'Millimeters'
    # spectral_response = 'Photometric'
    # rotation = 0
    # the_instrument.measurementsetup(pattern, eR, eG, eB, eXB, focus, aperture, is_autoexp, rect, distance_unit, spectral_response, rotation)
    #
    # color_cal = 'camera_color_cal_255_20180116'
    # scale_cal = 'image_scale_cal_20180116'
    # shift_cal = '158763491 Color Shift Correction'
    #
    # colorcalibrationid = the_instrument.get_colorcal_key(color_cal)
    # imagescaleid = the_instrument.get_imagescalecal_key(scale_cal)
    # colorshiftid = the_instrument.get_colorshiftcal_key(shift_cal)
    #
    # the_instrument.setcalibrationid(pattern, colorcalibrationid, imagescaleid, colorshiftid)

#   imagekey = "whitekey" # can be set by end user.
#     imagekey = pattern
#     isSavetoDatabase = True
#     the_instrument.capture(pattern, imagekey, isSavetoDatabase)

    patternList = ["White", "Gray180", "Gray127", "Gray90", "Red", "Green", "Blue"]
    for pattern in patternList:
        anaList = []
        analysisList = ["MLO_Uniformity", "ANSI Brightness", "Particle Defects"]
        for analysis in analysisList:
            anaList.append(analysis + " " + pattern)
        #the_instrument.sequence_run_step_list(anaList, True, True)
        the_instrument.sequence_run_step(anaList[0], True, True)
        # CODE TO CHANGE THE PATTERN NEEDS TO GO HERE

    path = os.getcwd()
    filename = "temp.csv"
    resolutionX = 200
    resolutionY = 300

    measIDlist = the_instrument.get_list_of_meas_IDs()
    for ID in measIDlist:
        the_instrument.export_measurement(ID, path, "", resolutionX, resolutionY)

    # the_instrument.prepare_for_run()
    # analysis_item = 'UniformityRegister'
    # override = ''
    # the_instrument.run_analysis_by_name(analysis_item, imageKey=imagekey)
    # mesh_data = the_instrument.get_last_mesh()
    # if mesh_data != {}:
    #     output_data = StringIO.StringIO()
    #     np.savez_compressed(output_data, **mesh_data)
    #     npzdata = output_data.getvalue()
    #     print "npzdata : {}".format(npzdata)
    #     #also calculate some statistical infdir()o about the measurement
    #     for c in ["Lv", "Cx", "Cy" "u'", "v'"]:
    #         cdata = mesh_data.get(c)
    #         if cdata is not None:
    #             cmean = np.mean(cdata, dtype=np.float32)
    #             cmax = cdata.max()
    #             cmin = cdata.min()
    #             cstd = np.std(cdata, dtype=np.float32)
    #             print c





