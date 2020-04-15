import sys
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.register_write_message import WriteSingleRegisterResponse
from pymodbus.register_read_message import ReadHoldingRegistersResponse
from pymodbus.constants import Defaults
import time
import ctypes
sys.path.append('../../')
import station_config

class ParticleCounterError(Exception):
    pass


class ParticleCounter(object):
    def __init__(self, station_config):
        self._station_config = station_config  # type: StationConfig
        self._particle_counter_client = None  # type: ModbusSerialClient
        self._init = False
        pass

    def initialize(self):
        if self._station_config.FIXTURE_PARTICLE_COUNTER:
            if not self._init:
                parity = 'N'
                Defaults.Retries = 5
                Defaults.RetryOnEmpty = True
                self._particle_counter_client = ModbusSerialClient(method='rtu', baudrate=9600, bytesize=8, parity=parity,
                                                                   stopbits=1,
                                                                   port=self._station_config.FIXTURE_PARTICLE_COMPORT,
                                                                   timeout=2000)
                if not self._particle_counter_client.connect():
                    raise ParticleCounterError(
                        'Unable to open Particle Counter port: %s' % self._station_config.FIXTURE_PARTICLE_COMPORT)
                self._init = True

    def is_ready(self):
        return self._init

    def particle_counter_on(self):
        if self._particle_counter_client is not None:
            wrs = self._particle_counter_client.\
                write_register(self._station_config.FIXTRUE_PARTICLE_ADDR_START,
                               1, unit=self._station_config.FIXTURE_PARTICLE_ADDR)
            if wrs is None or wrs.isError():
                raise ParticleCounterError('Failed to start particle counter .')

    def particle_counter_off(self):
        if self._particle_counter_client is not None:
            self._particle_counter_client. write_register(self._station_config.FIXTRUE_PARTICLE_ADDR_START,
                                                          0, unit=self._station_config.FIXTURE_PARTICLE_ADDR)  # type: WriteSingleRegisterResponse

    def particle_counter_read_val(self):
        if self._particle_counter_client is not None:
            val = None
            retries = 1
            while retries <= 10:
                rs = self._particle_counter_client.read_holding_registers(self._station_config.FIXTRUE_PARTICLE_ADDR_READ,
                                                                          2, unit=self._station_config.FIXTURE_PARTICLE_ADDR)  # type: ReadHoldingRegistersResponse
                if rs is None or rs.isError():
                    if self._station_config.IS_VERBOSE:
                        print "Retries to read data from particle counter {}/10. ".format(retries)
                    retries += 1
                    time.sleep(0.5)
                else:
                    # val = rs.registers[0] * 65535 + rs.registers[1]
                    # modified by elton.  for apc-r210/310
                    val = ctypes.c_int32(rs.registers[0]  + (rs.registers[1] << 16)).value
                    if hasattr(station_config, 'PARTICLE_COUNTER_APC') and station_config.PARTICLE_COUNTER_APC:
                        val = (ctypes.c_int32((rs.registers[0] << 16) + rs.registers[1])).value
                    break
            if val is None:
                raise ParticleCounterError('Failed to read data from particle counter.')
            return val

    def particle_counter_state(self):
        if self._particle_counter_client is not None:
            rs = self._particle_counter_client.read_holding_registers(self._station_config.FIXTRUE_PARTICLE_ADDR_STATUS,
                                                                      2,
                                                                      unit=self._station_config.FIXTURE_PARTICLE_ADDR)  # type: ReadHoldingRegistersResponse
            if rs is None or rs.isError():
                raise ParticleCounterError('Fail to read data from particle counter. ')
            else:
                return rs.registers[0]

    def close(self):
        self.particle_counter_off()


if __name__ == '__main__':
    sys.path.append("../../../")
    import station_config
    import time
    import hardware_station_common.operator_interface.operator_interface

    print 'Self check for %s' % (__file__,)
    station_config.load_station('pancake_offaxis')
    station_config.FIXTURE_PARTICLE_COUNTER = True
    station_config.FIXTURE_PARTICLE_COMPORT = 'COM3'
    # station_config.FIXTRUE_PARTICLE_ADDR_READ = 8
    # station_config.FIXTRUE_PARTICLE_ADDR_START = 30
    # station_config.FIXTRUE_PARTICLE_ADDR_STATUS = 30


    the_particle_counter = ParticleCounter(station_config)
    the_particle_counter.initialize()

    # print the_particle_counter.particle_counter_state()

    # the_particle_counter.particle_counter_on()

    print the_particle_counter.particle_counter_read_val()

    # the_particle_counter.particle_counter_off()

    # the_particle_counter.particle_counter_on()
    # the_particle_counter.particle_counter_off()
    # if the_particle_counter.particle_counter_state() == 0:
    # time.sleep(2.1)
    # the_particle_counter.particle_counter_on()
    time.sleep(2.1)
    for i in range(1, 9999000):
        val = the_particle_counter.particle_counter_read_val()
        print  (i, val)
        pass
    the_particle_counter._particle_counter_client.close()
    # the_particle_counter.particle_counter_off()
    pass




