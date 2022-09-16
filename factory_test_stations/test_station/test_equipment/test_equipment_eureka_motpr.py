import hardware_station_common.test_station.test_equipment
from enum import Enum
import clr
import sys
import os
import re


class EurekaMotPREquipmentError(Exception):
    def __init__(self, msg, err_code=0):
        Exception.__init__(self)
        self.message = msg
        self._err_code = err_code

    def __str__(self):
        return repr(self.message)

    @property
    def err_code(self):
        return self._err_code


class ErrorCodes(Enum):
    BadArguments = -5001
    BadData = -5004


class MeasurementData(Enum):
    New = 0
    last = 1


class InternalND(Enum):
    Close = 1
    Open = 0
    QueryState = -1


class TaktLearnPhases(Enum):
    GetFrequency = 0
    MaxWhite = 1
    StandardDark = 2
    EndPhases = 3


class SynchMode(Enum):
    Non = 0
    Auto = 1
    Learn = 2
    User = 3


class SpeedMode(Enum):
    SpeedNormal = 0
    SpeedFast = 1
    Speed2XFast = 2
    Speed4XFast = 3


class UnitsType(Enum):
    ImperialUnits = 0
    MetricUnits = 1


class EurekaMotPREquipment(hardware_station_common.test_station.test_equipment.TestEquipment):
    """
        class for Eureka motpr Equipment
            this is for doing all the specific things necessary to interface with equipment
    """

    def __init__(self, station_config, operator_interface):
        fullpath = os.path.abspath(sys.modules[EurekaMotPREquipment.__module__].__file__)
        cur = os.path.dirname(fullpath)
        print(f'Cur directory = {cur} =======================')
        clr.AddReference(os.path.join(cur, r'PR6xxComm.dll'))

        from PR6xxComm import CommBase
        hardware_station_common.test_station.test_equipment.TestEquipment.__init__(self, station_config,
                                                                                   operator_interface)
        self._device = CommBase()
        self._station_config = station_config
        pass

    def initialize(self):
        self.deviceOpen()
        synchMode = self._station_config.PR788_Config['SynchMode']
        speedMode = self._station_config.PR788_Config['SpeedMode']
        Oberserve = self._station_config.PR788_Config['Oberserve']
        self.deviceSpeed(speedMode)
        self.deviceSetSynchMode(synchMode)
        self.deviceObserver(nObsever=Oberserve)

    def close(self):
        self.deviceClose()
        self._operator_interface.print_to_console("Closing Eureka MotPR Equipment\n")

    def version_info(self):
        """
        Get SDK version information.
        @return:
        """
        info = self._device.prVersionInfo()
        return dict([tuple(re.split(r':\s*', c)) for c in info.splitlines(keepends=False)])

    def _rmt_mode_enter(self):
        """
        enter and validate remote mode
        @return:
        """
        return self._device.RmtModeEnter()

    def _get_exposure_range(self):
        """
        get min and max exposure time values
        @return:
        """
        return self._device.GetExposureRange()

    def ApplyCycleTime(self, exposure_µs):
        return self._device.ApplyCycleTime(exposure_µs)

    def errorcodes(self, Errorcode):
        return self._device.ErrString(Errorcode)

    def deviceOpen(self):
        res = self._device.prDeviceOpen()
        if res != 0:
            raise EurekaMotPREquipmentError(f"Eureka MotPR Equipment is Not Ready, Pr788 Open Fail. {res}")

    def deviceClose(self):
        self._device.prDeviceClose()

    def deviceSerialNumber(self):
        '''
        Gets the serial number of the currently opened PRI spectral device
        :param szSerialNumber:
        :return: tuple
        '''
        szSerialNumber = ''
        res, serial_number = self._device.prDeviceSerialNumber(szSerialNumber)
        if res != 0:
            raise EurekaMotPREquipmentError('Fail to get serial number.')
        return serial_number

    def deviceGetFirmwareVersion(self):
        '''
        get fw version
        :return:
        '''
        res = self._device.prDeviceFirmwareVersion('')
        if isinstance(res, tuple) and len(res) == 2 and res[0] == 0:
            return res[1]
        else:
            raise EurekaMotPREquipmentError('Fail to get FirmwareVersion')

    def deviceGetGetAccessoryList(self):
        '''
        get accessory list
        :param preStr:
        :return: string
        '''
        preStr = ''
        return self._device.prDeviceGetAccessoryList(preStr)

    def deviceGetFrequency(self, preNum=0):
        '''
        get Frequency
        :param preNum:
        :return: float
        '''
        return self._device.prDeviceGetFrequency(preNum)

    def deviceGetMinExposure(self, minExposure=0):
        '''
        prDeviceGetMinExposure
        :param minExposure:
        :return: tuple
        '''
        return self._device.prDeviceGetMinExposure(minExposure)

    def deviceGetTakt(self, takt1=0, takt2=0, takt3=0, takt4=0):
        '''
        prDeviceGetTakt
        :param takt1:
        :param takt2:
        :param takt3:
        :param takt4:
        :return: tulpe
        '''
        return self._device.prDeviceGetTakt(takt1, takt2, takt3, takt4)

    def deviceGetDateTime(self):
        return self._device.prGetDateTime()

    def deviceInstCalDue(self, szDueDate=''):
        '''
        Report the date and time when the instrument will be out of calibration.
        :param szDueDate:
        :return: tuple
        '''
        return self._device.prDeviceInstCalDue(szDueDate)

    def deviceExposure(self, milliseconds):
        '''

        :param milliseconds:
        :return: 0 = success
        '''
        return self._device.prDeviceExposure(milliseconds)

    def deviceprEnableCorrelationTable(self, bool):
        '''
        true selects loaded correlation table, false selects factory table
        :param bool:
        :return: 0 = seccess
        '''
        return self._device.prDeviceEnableCorrelationTable(bool)

    def deviceprDeviceCapMeasure(self, measurementData: MeasurementData):
        '''
        Take spectral measurement
        :param capX:
        :param capY:
        :param capZ:
        :param new:
        :return:
        '''
        capX, capY, capZ = 0, 0, 0
        return self._device.prDeviceCapMeasure(capX, capY, capZ, MeasurementData.last.value)

    def deviceMeasure(self, measurementData: MeasurementData):
        '''
        Take luminance measurement
        :param brightness: double
        :param cieX: double
        :param cieY: double
        :param measurementData:
        :return: tuple
        '''
        brightness, cieX, cieY = 0, 0, 0
        self._operator_interface.print_to_console("Eureka MotPR Equipment Start Measurement \n")
        res = self._device.prDeviceMeasure(brightness, cieX, cieY, measurementData)
        if isinstance(res, tuple) and len(res) == 4:
            self._operator_interface.print_to_console("Measurement result\n")
            return res[1:4]
        else:
            raise EurekaMotPREquipmentError(f'Fail to deviceMeasure. {res}')

    def deviceInternalND(self, internalND: InternalND):
        '''
        returns status of Internal ND or ERROR_PARSER_PARAM_NA_FOR_THIS_INSTRUMENT if not configured
        :param internalND:
        :return: int
        '''
        return self._device.prDeviceInternalND(internalND)

    def deviceLastMeasurementInfo(self):
        '''
        Get additional information for last luminance or spectral measurement.
        :param pxie:
        :param lightDark:
        :param exposure:
        :param brightness:
        :param cct:
        :param temperature:
        :return: tuple
        '''
        pxie, lightDark, exposure, brightness, cct, temperature = 0, 0, 0, 0, 0, 0
        return self._device.prDeviceLastMeasurementInfo(pxie, lightDark, exposure, brightness, cct, temperature)

    def deviceLearnFreqAdjustedTakt(self, taktlearnphase: TaktLearnPhases, fTaktSetFreq):
        '''
        Interactive method to use when determining takt table values for customer target.
            Each phase or pass requires that the DUT be set to a desired luminance/color level.
            Upon completion of all the required phases a takt table is generated and applied to the instrument.
        :param taktlearnphase:
        :param fTaktSetFreq: float
        :return: int
        '''
        return self._device.prDeviceLearnFreqAdjustedTakt(taktlearnphase, fTaktSetFreq)

    def deviceModel(self, szModel=''):
        '''
        Gets the model number of the currently opened PRI spectral device
        :param szModel:
        :return: tuple
        '''
        res = self._device.prDeviceModel(szModel)
        if isinstance(res, tuple) and len(res) == 2 and res[0] == 0:
            return res[1]
        else:
            raise EurekaMotPREquipmentError(f'Fail to deviceMeasure. {res}')

    def deviceObserver(self, nObsever=2):
        '''
        Set CIE standard observer for subsequent measurements
        :param nObsever: only 2 or 10, other occur Error
        :return: int
        '''
        res = self._device.prDeviceObserver(nObsever)
        if res != 0:
            raise EurekaMotPREquipmentError(f'Fail to deviceObserver. {res}')

    def deviceSetAccessory(self, accIndex):
        '''
        Sets accessory with an index number
        :param accIndex: int
        :return: int 0 = success
        '''
        return self._device.prDeviceSetAccessory(accIndex)

    def deviceSetFrequency(self, synchFrequency):
        '''
        sets the synch frequency for subsequent luminance measurements.
        :param synchFrequency:   synchFrequency >= 20 or synchFrequency <= 2000
        :return: int 0 = success
        '''
        return self._device.prDeviceSetFrequency(synchFrequency)

    def deviceSetPrimary(self, accIndex):
        '''
        Sets accessory with an index number
        :param accIndex:
        :return: int  0 = success
        '''
        return self._device.prDeviceSetPrimary(accIndex)

    def deviceSetSynchMode(self, synchMode: SynchMode):
        '''
        This method assumes that the client has previously used the prDeviceSetSynchMode method to configure the instrument
        for user synch mode operation
        :param synchMode:
        :return: 0 = success
        '''
        res = self._device.prDeviceSetSynchMode(synchMode)
        if res != 0:
            raise EurekaMotPREquipmentError(f'Fail to deviceSetSynchMode. {res}')

    def deviceSmartDark(self, bTurnOn):
        '''
        Enable/disable mandatory capturing of a dark frame before each measurement.
            When this feature is enabled the spectrometer determines if a dark frame is required.
        :param bTurnOn: bool True or False
        :return: 0 = success
        '''
        return self._device.prDeviceSmartDark(bTurnOn)

    def deviceSpectralMeasure(self, measurementData: MeasurementData, spectralData=''):
        '''
        Take spectral measurement
        :param spectralData:
        :param measurementData:
        :return: tuple
        '''
        self._operator_interface.print_to_console("Eureka MotPR Equipment Start Spectral Measurement \n")
        res = self._device.prDeviceSpectralMeasure(spectralData, measurementData)
        if isinstance(res, tuple) and len(res) == 2:
            return res[1]
        else:
            raise EurekaMotPREquipmentError(f'Fail to deviceSpectralMeasure {res}')

    def deviceSpeed(self, speedMode: SpeedMode):
        '''
        Adjusts the device measurement speed by altering the gain for the measurement
        :param speedMode: Normal, Fast, 2XFast, 4XFast
        :return: 0 = success
        '''
        res = self._device.prDeviceSpeed(speedMode)
        if res != 0:
            raise EurekaMotPREquipmentError(f'Fail to deviceSpeed. {res}')

    def deviceStartCamera(self, viewerPath):
        '''
        Launch instrument viewing camera application.
        :param viewerPath: camera.exe file path
        :return:
        '''
        self._device.prDeviceStartCamera(viewerPath)

    def deviceStopCamera(self):
        '''
        Kill instrument viewing camera application.
        :return:
        '''
        self._device.prDeviceStopCamera()

    def deviceSyncLearn(self, syncFrequency):
        '''
        retrieves the synch frequency detected by instrument.
        :param syncFrequency:
        :return: tuple
        '''
        return self._device.prDeviceSyncLearn(syncFrequency)

    def deviceTaktIndex(self, index):
        '''

        :param index: 0 = adaptive,1-4 = use value at specified index
        :return:
        '''
        return self._device.prDeviceTaktIndex(index)

    def deviceTaktTable(self, takt1, takt2, takt3, takt4):
        '''
        Set TAKT table using user provided values.
        :param takt1: Desired exposure time in microseconds for bright light/color levels
        :param takt2: Desired exposure time in microseconds for bright light/color levels
        :param takt3: Desired exposure time in microseconds for low light/color levels
        :param takt4: Desired exposure time in microseconds for very low light/color levels
        :return: 0 = success
        '''
        return self._device.prDeviceTaktTable(takt1, takt2, takt3, takt4)

    def deviceUnits(self, unitType: UnitsType):
        '''
        Sets returned measurement units to either metric or imperial
        :param unitType:
        :return: 0 = success
        '''
        return self._device.prDeviceUnits(unitType)

    def deviceUserCorrelationTable(self, table, brightness, cieX, cieY):
        '''
        Provide instrument with user specified spectral correlation table. This table must be applied while the
        instrument is measuring the same light source used to generate the table. The application measurement
        will be executed as part of this procedure.
        :param table: string
        :param brightness: double
        :param cieX: double
        :param cieY: double
        :return: tuple
        '''
        return self._device.prDeviceUserCorrelationTable(table, brightness, cieX, cieY)

    def deviceOpenLog(self, filepath):
        '''
        Creates SDK level log file and starts logging process.
        :param filepath:
        :return:
        '''
        return self._device.prOpenLogFile(filepath)


if __name__ == '__main__':
    class cfgstub(object):

        def print_to_console(self, msg):
            print(msg)


    station_config = cfgstub()
    station_config.PR788_Config = {
        "Log_Path": r'C:/oculus/factory_test_omi/factory_test_stations/factory-test_logs/PR788',
        "Auto_Exposure": True,
        # "Granularity": 1/9 * 10**6,
        "Oberserve": 2,     ## 2 ~ 10
        "SynchMode": 0,     ## Non = 0, Auto = 1, Learn = 2, User = 3
        "SpeedMode": 0,     ## Normal = 0, Fast = 1, 2xFast = 2, 4xFast = 3
    }

    the_equip = EurekaMotPREquipment(station_config, station_config)
    the_equip.initialize()
    the_equip.version_info()
    the_equip.deviceSerialNumber()

    ####start new Measure

    ###Luminance measurement
    result = the_equip.deviceMeasure(MeasurementData.New.value)

    ###Spectral Measurement
    result = the_equip.deviceSpectralMeasure(MeasurementData.New.value)

    ###XYZ measurement
    result = the_equip.deviceprDeviceCapMeasure(MeasurementData.New.value)

    the_equip.deviceClose()
    pass
