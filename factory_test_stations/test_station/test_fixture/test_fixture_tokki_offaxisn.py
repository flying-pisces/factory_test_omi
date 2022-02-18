import hardware_station_common.test_station.test_fixture


class TokkiOffAxisNFixture(hardware_station_common.test_station.test_fixture.TestFixture):
    """
        class for Tokki offaxisn Fixture
            this is for doing all the specific things necessary to interface with instruments
    """
    def __init__(self, station_config, operator_interface):
        hardware_station_common.test_station.test_fixture.TestFixture.__init__(self, station_config, operator_interface)

    def is_ready(self):
        pass

    def initialize(self):
        self._operator_interface.print_to_console("Initializing Tokki OffAxisN Fixture\n")

    def close(self):
        self._operator_interface.print_to_console("Closing Tokki OffAxisN Fixture\n")
