import hardware_station_common.test_station.test_fixture


class projectstationFixture(hardware_station_common.test_station.test_fixture.TestFixture):
    """
        class for project station Fixture
            this is for doing all the specific things necessary to interface with instruments
    """
    def __init__(self, station_config, operator_interface):
        hardware_station_common.test_station.test_fixture.TestFixture.__init__(self, station_config, operator_interface)

    def is_ready(self):
        pass

    def initialize(self):
        self._operator_interface.print_to_console("Initializing project station Fixture\n")

    def close(self):
        self._operator_interface.print_to_console("Closing project station Fixture\n")

    def __getattr__(self, item):
        def not_find(*args, **kwargs):
            return
        if item in ['status', 'elminator_off', 'elminator_on', 'mov_abs_xy', 'unload',
                    'load', 'button_disable', 'button_enable']:
            return not_find
