import hardware_station_common.test_station.test_fixture
import os
import sys
import re
### Below two lines will be used for debug.
sys.path.append("../")
import glob
import serial
import serial.tools.list_ports
import time

class pancakeoffaxisFixtureError(Exception):
    pass

class pancakeoffaxisFixture(hardware_station_common.test_station.test_fixture.TestFixture):
    """
        class for auo unif Fixture
            this is for doing all the specific things necessary to interface with instruments
    """
    def __init__(self, station_config, operator_interface):
        hardware_station_common.test_station.test_fixture.TestFixture.__init__(self, station_config, operator_interface)
        self._serial_port = None
        self._verbose = station_config.IS_VERBOSE
        self._start_delimiter = ':'
        self._end_delimiter = '\r\n'
        self._error_msg = r'Please scanf "CMD_HELP" check help command'
        self._error_flag = r'err!'
        self._read_error = False
        self._particle_counter_client = None

    def is_ready(self):
        pass

    def initialize(self):
        self._operator_interface.print_to_console("Initializing offaxis Fixture\n")
        self._serial_port = serial.Serial(self._station_config.FIXTURE_COMPORT,
                                          115200,
                                          parity='N',
                                          stopbits=1,
                                          timeout=1,
                                          xonxoff=0,
                                          rtscts=0)
        if not self._serial_port:
            raise pancakeoffaxisFixtureError('Unable to open fixture port: %s' % self._station_config.FIXTURE_COMPORT)
            return False
        else:
            if self._verbose:
                print "Fixture %s Initialized" % self._station_config.FIXTURE_COMPORT
            return True

    def _parsing_response(self, response):
        value = []
        for item in response[1:len(response) - 1]:
            value.append((item.split(self._start_delimiter))[1].split(self._end_delimiter)[0])
        return value

    def _write_serial(self, input_bytes):
        if self._verbose:
            print('writing: ' + input_bytes)
        bytes_written = self._serial_port.write(input_bytes)
        if self._verbose:
            print("wrote, flushing")
        self._serial_port.flush()
        if self._verbose:
            print("flushed")
        return bytes_written

    def _read_response(self, end_delimiter='@_@', timeout=5):
        response = []
        line_in = ""
        tim = time.time()
        while (not re.search(end_delimiter, line_in, re.IGNORECASE)
               and not re.search(self._error_flag, line_in, re.IGNORECASE)
               and (time.time() - tim < timeout)):
            line_in = self._serial_port.readline()
            if line_in != "":
                response.append(line_in)
        if self._verbose:
            print response
        return response

    def help(self):
        self._write_serial(self._station_config.COMMAND_HELP)
        response = self._read_response()
        if self._verbose:
            print response
        return response

    def reset(self):
        self._write_serial(self._station_config.COMMAND_RESET)
        response = self._read_response()
        if self._verbose:
            print(response[1])
        value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
        return value

    def id(self):
        self._write_serial(self._station_config.COMMAND_ID)
        response = self._read_response()
        if self._verbose:
            print(response[1])
        value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
        return value

    def close(self):
        self._operator_interface.print_to_console("Closing auo unif Fixture\n")
        if hasattr(self, '_serial_port') \
                and self._serial_port is not None \
                and self._station_config.FIXTURE_COMPORT:
            self._serial_port.close()
            self._serial_port = None
        if hasattr(self, '_particle_counter_client') and \
                self._particle_counter_client is not None \
                and self._station_config.FIXTURE_PARTICLE_COUNTER:
            self._particle_counter_client.close()
            self._particle_counter_client = None
            if self._verbose:
                print "====== Fixture Close ========="
        return True

    ######################
    # Fixture control
    ######################

    def move_abs_xy(self, x, y):
        CMD_MOVE_STRING = self._station_config.COMMAND_ABS_X_Y + str(x) + " " + str(y) + "\r\n"
        self._write_serial(CMD_MOVE_STRING)
        expect_rev = "move_y_axis_over"
        resp = self._prase_command_normal(expect_rev)
        return resp[1]

    # def move_res_xy(self, x, y):
    #     CMD_MOVE_STRING = self._station_config.COMMAND_RES_X_Y + str(x) + " " + str(y) + "\r\n"
    #     self._write_serial(CMD_MOVE_STRING)
    #     response = self._read_response()
    #     print(response[1])
    #     value = (response[1].split(self._start_delimiter))[1].split(self._end_delimiter)[0]
    #     return value

    def load(self):
        self._write_serial(self._station_config.COMMAND_LOAD)
        # expect_rev = (self._station_config.COMMAND_LOAD + '_OK').replace('\r\n', '')
        expect_rev = "load_ok"
        return self._prase_command_normal(expect_rev)

    def unload(self):
        self._write_serial(self._station_config.COMMAND_UNLOAD)
        # expect_rev = (self._station_config.COMMAND_UNLOAD + '_OK').replace('\r\n', '')
        expect_rev = "unload_ok"
        return self._prase_command_normal(expect_rev)

    def _prase_command_normal(self, expect_rev):
        # type: (str) -> bool
        response = self._read_response(expect_rev)
        if len(response) >= 1:
            err_list = [r for r in response if re.search(self._error_flag, r, re.I)]
            ok_list = [r for l in response if re.search(expect_rev, r, re.I)]
            if len(err_list) == 0 and len(ok_list) > 0:
                return response
            else:
                msg = ','.join(err_list)
                raise pancakeoffaxisFixtureError('Fail to read {}, Msg = {}'.format(expect_rev, msg))
        else:
            self._read_error = True
            raise pancakeoffaxisFixtureError('Fail to read %s' % expect_rev)

def print_to_console(self, msg):
    pass

if __name__ == "__main__":
        sys.path.append("../../")
        import types
        import station_config
        import hardware_station_common.operator_interface.operator_interface

        print 'Self check for pancake_offaxis'
        station_config.load_station('pancake_offaxis')
        station_config.print_to_console = types.MethodType(print_to_console, station_config)
        the_fixture = pancakeoffaxisFixture(station_config, station_config)
        the_fixture._verbose = True

        try:
            the_fixture.initialize()

            the_fixture.move_abs_xy(5, 1)

            for i in range(0, 100):
                the_fixture.load()
                time.sleep(4)
                the_fixture.unload()
                time.sleep(4)

        except pancakeoffaxisFixtureError as e:
            print 'exception {}'.format(e.message)
        finally:
            the_fixture.close()