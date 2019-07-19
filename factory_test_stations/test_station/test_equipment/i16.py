import os
import json
import clr
clr.AddReference('System.Drawing')
apipath = os.path.join(os.getcwd(), "MPK_API.dll")
clr.AddReference(apipath)
from MPK_API import *
from System.Drawing import *
from System import String

class I16Error():
    pass

class I16():
    def __init__(self, verbose=False, focus_distance=0.575, lens_aperture=8.0, auto_exposure=False, rect=[0, 0, 0, 0]):
        self.name = "i16"
        self._verbose = verbose
        self._device = MPK_API()
        self._error_message = self.name + "is out of work"
        self._read_error = False
        self._focus_distance = focus_distance; #dimension of m
        self._lens_aperture = lens_aperture;
        self._auto_exposure = auto_exposure;
        self._rect = rect;
     
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
#####################################################################################################
######### Measurement Setup ##################
    # CreateMeasurementSetup(patternName as String, redEFilterxposure as Single, greenFilterExposure as Single,
#                       blueFilterExposure as Single, xbFilterExposure as Single, focusDistance as Single,
#                       lenAperture as Single, autoAdjustExposure as Boolean, subframeRegion as Rectangle) 
    def measurementsetup(self, pattern="photopic", eR = 100, eG = 100, eB = 100, eXB = 100):
        meas_setup = self._device.CreateMeasurementSetup(pattern,
                                           eR, eG, eB, eXB,
                                           self._focus_distance,
                                           self._lens_aperture,
                                           self._auto_exposure ,
                                           self._rect)
        response = int(str(String.Format("Measurement Setup Result for " + pattern +" - ErrorCode: {0}", meas_setup['ErrorCode'])).split(":")[1])
        if self._verbose:
            print response
        return response 
#colorCals = mpkapi.GetColorCalibrationList()
#print('Color Cals:')
#print(colorCals)
    def getcolorcalibrationlist(self):
        response = str(self._device.GetColorCalibrationList()).replace('\r\n', '')
        colorcalibrationlistjson = json.loads(response)
        colorcalibrationlistid = colorcalibrationlistjson.keys()
        if self._verbose:
            print colorcalibrationlistjson
        return colorcalibrationlistid
    
    def getcolorshiftcalibrationlist(self):
        response = str(self._device.GetColorShiftCalibrationList()).replace('\r\n', '')
        colorshiftcalibrationlistjson = json.loads(response)
        colorshiftcalibrationlistid = colorshiftcalibrationlistjson.keys()
        if self._verbose:
            print colorshiftcalibrationlistjson
        return colorshiftcalibrationlistid
    
    def getimagescalecalibrationlist(self):
        response = str(self._device.GetImageScaleCalibrationList()).replace('\r\n', '')
        imagescalecalibrationlistjson = json.loads(response)
        imagescalecalibrationlistid = imagescalecalibrationlistjson.keys()
        if self._verbose:
            print imagescalecalibrationlistjson
        return imagescalecalibrationlistid

    def getflatfieldcalibrationlist(self):
        response = str(self._device.GetFlatFieldCalibrationList()).replace('\r\n', '')
        flatfieldcalibrationlistjson = json.loads(response)
        flatfieldcalibrationlistid = flatfieldcalibrationlistjson.keys()
        if self._verbose:
            print flatfieldcalibrationlistjson
        return flatfieldcalibrationlistid


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
        

#####################################################################################################
## Image Analysis

#result = mpkapi.PrepareForRun()
#print(String.Format("Prepare For Run - ErrorCode: {0}", result['ErrorCode']))
    def prepareanalysis(self):
        response = str(self._device.PrepareForRun).replace('\r\n', '')
        prepareforrunjson = json.loads(response)
        isprepareforrun = "0" in prepareforrunjson.values()
        if self._verbose:
            print(response)
        return isprepareforrun
            


if __name__ == "__main__":
    verbose=True
    focus_distance=0.50
    lens_aperture=2.8
    auto_exposure=False
    cx = 1816 #Left
    cy = 740 #Top
    cl = 1446 #Width
    cw = 1575 #Height
    rect = Rectangle(cx, cy, cl, cw)
    the_instrument = I16(verbose, focus_distance, lens_aperture, auto_exposure, rect)
    sn = the_instrument.serialnumber()
    sn = "158763491"
    isinit = the_instrument.init(sn)
    version = the_instrument.version()
    the_instrument.init(sn)
    pattern = "W255"
    the_instrument.measurementsetup("White", 156.29, 243.88, 160.00)

    the_instrument.getcolorcalibrationlist() #11
    the_instrument.getcolorshiftcalibrationlist() #6
    the_instrument.getimagescalecalibrationlist() #3
    the_instrument.getflatfieldcalibrationlist() #6
    
    meassetup = "White"
    colorcalibrationid = 5
    imagescaleid = 1
    colorshiftid = 1
    the_instrument.setcalibrationid(meassetup, colorcalibrationid, imagescaleid, colorshiftid) 

    pattern = "white"
    imagekey = "whitekey" # can be set by end user.
    isSavetoDatabase = True
    the_instrument.capture(meassetup, imagekey, isSavetoDatabase)

  
  