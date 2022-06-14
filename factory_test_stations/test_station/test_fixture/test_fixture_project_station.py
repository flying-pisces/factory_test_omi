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

    def initialize(self, **kwargs):
        self._operator_interface.print_to_console("Initializing project station Fixture\n")

    def close(self):
        self._operator_interface.print_to_console("Closing project station Fixture\n")

    def __getattr__(self, item):
        def not_find(*args, **kwargs):
            return
        if item in ['status', 'elminator_off', 'elminator_on', 'mov_abs_xy', 'unload',
                    'load', 'button_disable', 'button_enable', 'flush_data', 'mov_abs_xya',
                    'is_ready', 'power_on_button_status', 'start_button_status', 'query_temp',
                    'mov_abs_xy_wrt_alignment', 'mov_camera_z_wrt_alignment', 'query_probe_status',
                    'particle_counter_state', 'version', 'particle_counter_read_val', 'mov_abs_xy_wrt_dut',
                    'ca_postion_z', 'calib_zero_pos', 'id', 'set_tri_color' ]:
            return not_find
