#! /usr/bin
# -*- coding: utf-8 -*-

import serial
import serial.tools.list_ports
import time
import logging
import argparse
# from hardware.hardware import *
COMMAND_IDO = "IDO\r\n" # information
COMMAND_ZRC = "ZRC\r\n" # zero cal
COMMAND_XYZ = "XYZ\r\n" # measurement

########
#Note: this driver was originally written for the Konica 310 but works for the 410 as well

"""
        x,  y
  R    0.6  0.3
  W    0.3  0.5
  G    0.3  0.65
  B    0.14 0.04
"""
class CA310(object):
  def __init__(self, fixture_port, name="CA310", hw_name="Konica CA310", verbose=False):
    self.name = name
    self._hw_name = hw_name
    self.logger = logging.getLogger(self.name)
    self._verbose = verbose
    self._end_delimiter = '\r\n'
    self._fixture_port = fixture_port

  def initialize(self):
    self._serial_port = None
    self.initialize_camera()
    self._busy = False

## is_connected_clean function will make sure there is clean connection between fixture to PC. Only defined FIXTURE_COMPORT or FIXTURE_COMPORTS will be there.
  def _is_connected_clean(self):
    ports = list(serial.tools.list_ports.comports())
    result = []
    for p in ports:
      result.append(p.device)

    if self._fixture_port in result:
      return True
    else:
      self.logger.warning( "PORT Fails to Find {}".format(self._fixture_port) )
      return False


  def initialize_camera(self):
    # need define the initialization event in the whole flow.
    self._serial_port = None
    #previously was dynamically searching ports. We will alias ports going forward.
    #Keeping this code here in case the aliasing method fails
    # try:
    #   serialtest = serial.Serial(port='/dev/Konica')
    #   self._serial_port = serial.Serial(self._fixture_port,
    #                                     38400,
    #                                     parity='E',
    #                                     bytesize=7,
    #                                     stopbits=2,
    #                                     timeout=6,
    #                                     xonxoff=False,
    #                                     rtscts=False)
    # except Exception as e:
    #   print e.message
    # try:
    #   if not self.test_connection():  #if caller provided port doesn't work, try all on system
    #     ports = list(serial.tools.list_ports.comports())
    #     for p in ports: #this can be useful for other serial devices to check all the ports
    #       if p.device is not self._fixture_port and str(p.device).find('ACM'): #don't retry the first entry, only test ACMs
    #         self._serial_port = serial.Serial(p.device,
    #                                           38400,
    #                                           parity='E',
    #                                           bytesize=7,
    #                                           stopbits=2,
    #                                           timeout=6,
    #                                           xonxoff=False,
    #                                           rtscts=False)
    #         if self.test_connection():
    #           self._fixture_port = p.device
    #           print "succesful Konica connect"
    #           break
    # except:
    #   pass

    # trying to alias the ports, but this is causing problems when new devices are connected, so abandoning for now
    # self._fixture_port = '/dev/Konica'
    #ports = list(serial.tools.list_ports.comports())
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
      #not yet time to set status to connected; let status_check validate the connect

    if not self._serial_port:
      self.logging.warning("Unable to connect to Konica ca-410")
      time.sleep(.5)
    #if not self._serial_port:
    #  self.logging.warning('Unable to open fixture port: {}'.format(self._fixture_port))

  def close_camera(self):
    if self._serial_port:
      self._serial_port.close()

  def test_connection(self):
    if not self._serial_port:
      return False
    self._write_serial(COMMAND_IDO)
    time.sleep(.5)
    rsp = self._read_response()
    if rsp != None and rsp[0] != "" and rsp[0][0][:2] == 'OK':
      return True
    else:
      return False


  def _write_serial(self, input_bytes):
    bytes_written = ''
    while self._busy:
      time.sleep(.1)
    #if self._serial_port:
      #self._serial_port.flush()
    if self._verbose:
      self.logger.debug('writing: ' + input_bytes)
    if self._serial_port:
      self._busy = True
      try:
        bytes_written = self._serial_port.write(input_bytes)
      except:
        return ''
    return bytes_written


  def _read_response(self):
      response = ""
      try:
        if self._serial_port:
          try:
            response = self._serial_port.readline()
          except Exception as e:
            self.logging.warning("CA-3/410a Serial error: " + e.message)
          #this used to throw assertion errors, now it logs them
        if response is "":
          self.logging.warning("Instrument returned no data, check instrument is connected and in remote mode")
        if response[0:2] == "ER":
          self.logging.warning("Instrument returned error, maybe instrument is not in remote mode: {}".format(response))
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
  def measureXYZ(self):
    self._write_serial(COMMAND_XYZ)
    cmd, data = self._read_response()
    return map(float, data)

  def measurexyLv(self):
    X,Y,Z = self.measureXYZ()
    xp = X/(X+Y+Z)
    yp = Y/(X+Y+Z)
    Lv = Y
    return xp, yp, Lv

######################
# Scan and read SN
######################

if __name__ == "__main__":
  # parser = argparse.ArgumentParser(description='Test hardness for ca310')
  # parser.add_argument("--port", help="Comport", type=str, default="/dev/ttyACM0")
  # args = parser.parse_args()
  logging.basicConfig(level=logging.DEBUG)

  ports = list(serial.tools.list_ports.comports())

  the_fixture = CA310('COM4')
  the_fixture.initialize()

  print the_fixture.test_connection()
  # the_fixture.zero_cal()

  # print the_fixture.measureXYZ()
  #print the_fixture.info() ## Need set Remote mode
  #print the_fixture.config() ## Need at zero cal mode
  print the_fixture.measurexyLv() ## Need at Measurement mode

  the_fixture.close_camera()


