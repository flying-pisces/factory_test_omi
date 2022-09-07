import hardware_station_common.test_station.test_equipment
import serial.tools.list_ports
import time
import logging
import argparse

import sys
import pprint
sys.path.append("../")
sys.path.append("../../")
sys.path.append("../../../")

COMMAND_REM = "P\r\nH\r\nO\r\nT\r\n\O\r\n" # remote
COMMAND_MES = "M\r\n" # measurement

class pancakepr788EquipmentError(Exception):
    pass


class pancakepr788Equipment(hardware_station_common.test_station.test_equipment.TestEquipment):
    def __init__(self, station_config):
        self.name = "PR788"
        self.logger = logging.getLogger(self.name)
        self._station_config = station_config
        self._verbose = self._station_config.IS_VERBOSE
        self._serial_port = station_config.EQUIPMENT_PORT
        self._end_delimiter = '\r\n'

    def is_ready(self):
        ports = list(serial.tools.list_ports.comports())
        result = []
        for p in ports:
            result.append(p[0])
        if self._serial_port in result:
            print ("Equipment Find at {}".format(self._serial_port))
            return True
        else:
            self.logger.warning("PORT Fails to Find {}".format(self._serial_port))
            raise False

    def initialize(self):
        if self.is_ready():
            self._serial_port = serial.Serial(self._serial_port,
                                              115200,
                                              parity='E',
                                              bytesize=8,
                                              stopbits=1,
                                              timeout=30,
                                              xonxoff=False,
                                              rtscts=False)
        if not self._serial_port:
            raise AssertionError('Unable to open fixture port: {}'.format(self._serial_port))

    def remote_mode(self):
        self._serial_port.write("PHOTO\r\n".encode())
        response = True #ugly hack
        return response

    def quit(self):
        self._serial_port.write("Q\r\n".encode())
        time.sleep(1)
        response = True #ugly hack
        return response

    def measure(self):
        self._serial_port.write("M\r\n".encode())
        response = self._read_response()
        return response

    def close(self):
        if self._serial_port.isOpen():
            self._serial_port.close()
            print ("Equipment Port Close at {}".format(self._serial_port))
        pass

    def _write_serial(self, input_bytes):
        if self._verbose:
          self.logger.debug('writing: ' + input_bytes)
        bytes_written = self._serial_port.write(input_bytes.encode())
        return bytes_written

    def _read_response(self):
      self._serial_port.flush()
      response = self._serial_port.readline()
      return response

if __name__ == "__main__":
    import sys
    sys.path.append(r'..\..')
    import station_config
    verbose = True

    station_config.load_station('pancake_pr788')
    the_instrument = pancakepr788Equipment(station_config)
    isinit = the_instrument.is_ready()
    print(the_instrument.initialize())
    print(the_instrument.remote_mode())
    print(the_instrument.measure())
#    print(the_instrument.quit())
    the_instrument.close()