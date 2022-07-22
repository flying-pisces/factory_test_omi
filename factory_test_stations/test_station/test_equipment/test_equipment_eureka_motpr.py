import hardware_station_common.test_station.test_equipment
from enum import Enum
import clr


class EurekaMotPREquipmentError(Exception):
    pass


class InternalND(int, Enum):
    QueryState = -1
    Open = 0
    Close = 1


class UnitsType(int, Enum):
    ImperialUnits = 0,
    MetricUnits = 1,


class SpeedMode(int, Enum):
    SpeedNormal = 0,
    SpeedFast = 1,
    Speed2XFast = 2,
    Speed4XFast = 3


class MeasurementData(int, Enum):
    New = 0,
    Last = 1,


class EurekaMotPREquipment(hardware_station_common.test_station.test_equipment.TestEquipment):
    """
        class for Eureka motpr Equipment
            this is for doing all the specific things necessary to interface with equipment
    """
    def __init__(self, station_config, operator_interface):
        clr.AddReference(
            r'c:/oculus_src/factory_test_omi/factory_test_stations/test_station/test_equipment/PR6xxComm.dll')
        from PR6xxComm import CommBase
        hardware_station_common.test_station.test_equipment.TestEquipment.__init__(self, station_config, operator_interface)
        self._device = CommBase()
        pass

    def is_ready(self):
        pass

    def initialize(self):
        self._operator_interface.print_to_console("Initializing Eureka MotPR Equipment\n")

    def close(self):
        self._operator_interface.print_to_console("Closing Eureka MotPR Equipment\n")

    def version_info(self):
        """
        Get SDK version information.
        @return:
        """
        info = self._device.prVersionInfo()
        return info.splitlines(keepends=False)

    def _update_firmware(self, fw):
        """
        Load new firmware image on to the instrument. Both the new image and the current image checked to
         insure that the load will succeed
        @param fw:
        @return:
        """
        return self._device.prUpdateFirmware(fw)

    def _err_string(self, code):
        """
        create a printable String from the error code
        @param code:
        @return:
        """
        return self._device.ErrString(code)

    def _set_echo(self, echo_on):
        """
        set echo state
        @param echo_on:
        @return:
        """
        return self._device.SetEcho(echo_on)

    def _open_log_file(self, log_file):
        """
        Creates SDK level log file and starts logging process.
        @param log_file:
        @return:
        """
        self._device.prOpenLogFile(log_file)

    def _serial_port_open(self, port):
        """
        open the serial port
        @param port:
        @return:
        """
        self._device.SerialPortOpen(port)

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

    def _device_get_accessory_list(self, accessory_list):
        """
        Gets accessory list separated by "\r\n"
        @param accessory_list:
        @return:
        """
        return dict(zip('Res', 'AccessoryList'), self._device.prDeviceGetAccessoryList(accessory_list))

    def _device_set_primary(self, index_num):
        """
        32 bit integer indicating the method completion status; 0 = success, negative number is error code
        @param index_num:
        @return:
        """
        return self._device.prDeviceSetPrimary(index_num)

    def _device_set_accessory(self, index_num):
        """
        Sets accessory with an index number
        @param index_num:
        @return:
        """
        return self._device.prDeviceSetAccessory(index_num)

    def _set_short_result(self):
        self._device.prSetShortResult()

    def _reset_short_result(self):
        self._device.prSetShortResult()

    def _device_open_on_port(self, port: str):
        return self._device.prDeviceOpenOnPort(port)

    def _device_open(self):
        return self._device.prDeviceOpen()

    def _get_spectral_range(self):
        """
        set the minimum and maximum wavelengths of the instrument
        @return:
        """
        return self._device.GetSpectralRange()

    def _device_close(self):
        return self._device.prDeviceClose()

    def _device_internal_nd(self, internal_nd: InternalND):
        """
        return status of InternalND
        @param internal_nd:
        @return:
        """
        return self._device.prDeviceInternalND(internal_nd)

    def _device_model(self, sz_model):
        return dict(zip('Res', 'Model'), self._device.prDeviceModel(sz_model))

    def _device_inst_cal_due(self, sz_due_date):
        """
        Report the date and time when the instrument will be out of calibration.
        @param sz_due_date:
        @return:
        """
        return dict(zip('Res', 'DueDate'), self._device.prDeviceInstCalDue(sz_due_date))

    def _device_serial_number(self):
        """
        Gets the serial number of the currently opened PRI spectral device
        @param sz_serial_number:
        @return:
        """
        return dict(zip('Res', 'SN'), self._device.prDeviceSerialNumber(""))

    def _device_firmware_version(self, sz_firmware_version):
        return dict(zip('Res', 'FW'), self._device.prDeviceFirmwareVersion(sz_firmware_version))

    def _device_units(self, units: UnitsType):
        """
        Units selector: Imperial or Metric
        @param units:
        @return:
        """
        return self._device.prDeviceUnits(units)

    def _device_speed(self, speed_mode: SpeedMode):
        """
        Adjusts the device measurement speed by altering the gain for the measurement
        """
        return self._device.prDeviceSpeed(speed_mode)

    def _device_observer(self, nobserver):
        """
        Set CIE standard observer for subsequent measurements
        @param nobserver: 2 = 2 degree set, 10 = 10 degree set
        @return:
        """
        return self._device.prDeviceObserver(nobserver)

    def _device_exposure(self, m_secs: int):
        """
        Set exposure time for subsequent measurements.
        @param m_secs:
        @return:
        """
        return self._device.prDeviceExposure(m_secs)

    def _device_smart_dark(self, turn_on):
        """
        Enable/disable mandatory capturing of a dark frame before each measurement.
            When this feature is enabled the spectrometer determines if a dark frame is required.
        @param turn_on:
        @return:
        """
        return self._device.prDeviceSmartDark(turn_on)

    def _device_measure(self, measure_data: MeasurementData):
        """
        Take luminance measurement
        @return:
        """
        cie_x, cie_y, cie_z = 0.0, 0.0, 0.0
        return dict(zip('Res', 'x', 'y', 'z'), self._device.prDeviceMeasure(cie_x, cie_y, cie_z, measure_data))

    def _device_cap_measure(self, measure_data: MeasurementData):
        """
        Take XYZ measurement
        @param cap_x:
        @param cap_y:
        @param cap_z:
        @param measure_data:
        @return:
        """
        cap_x, cap_y, cap_z = 0.0, 0.0, 0.0
        return dict(zip('Res', 'X', 'Y', 'Z'), self._device.prDeviceCapMeasure(cap_x, cap_y, cap_z, measure_data))

    def _device_last_measurement_info(self):
        """
        Get additional information for last luminance or spectral measurement.
        @param pixel:
        @param light_dark:
        @param exposure:
        @param brightness:
        @param cct:
        @param temperature:
        @return:
        """
        pixel, light_dark, cct = 0, 0, 0
        exposure, brightness, temperature = 0.0, 0.0, 0.0
        return dict(zip(('Res', 'pixel', 'light_dark', 'exposure', 'brightness', 'cct', 'temperature'),
                        self._device.prDeviceLastMeasurementInfo(
                            pixel, light_dark, exposure, brightness, cct, temperature)))

    def _device_spectral_measure(self, m: MeasurementData):
        """
        Take spectral measurement
        @param m:
        @return:
        """
        spectral_data = ''
        return dict(zip('Res', 'Spectral'), self._device.prDeviceSpectralMeasure(spectral_data, m))

    def _device_get_takt(self):
        """
        Get previously configured TAKT table values. (These are saved by the SDK to )
        @return:
        """
        takt1, takt2, takt3, takt4 = 0, 0, 0, 0
        return dict(zip('Res', 'Takt1', 'Takt2', 'Takt3', 'Takt4'), self._device.prDeviceGetTakt(takt1, takt2, takt3, takt4))


if __name__ == '__main__':
    class cfgstub(object):

        def print_to_console(self, msg):
            print(msg)


    station_config = cfgstub()

    the_equip = EurekaMotPREquipment(station_config, station_config)
    the_equip.initialize()
    print(the_equip.version_info())
    pass
