import test_station
import station_config
import hardware_station_common.factory_test_gui as gui

# here we can override the station_config so that we don't have
# to monkey with it in the build system
station_config.load_station('pancake_uniformity')
# we just have to pass in the TestStation constructor for this specific station
# and the station_config
FACTORY_TEST_GUI = gui.FactoryTestGui(station_config, test_station.pancakeuniformityStation)
# enter the main loop
FACTORY_TEST_GUI.main_loop()
