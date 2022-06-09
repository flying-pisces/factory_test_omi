CURRENT_FW_VERSION = 1001

STATION_LIMITS_ARRAYS = [
    ["SW_VERSION", None, None, 79],
    ["DUT_POWER_ON_INFO", None, None, 81],
    ["DUT_POWER_ON_RES", True, True, 82],
    ["JUDGED_BY_CAM", True, True, 83],

    ["PRE_WRITE_COUNTS", 0, 5, 1000],
    ["VENDOR_INFO", None, None, 1001],

    # current setting for EEPROM
    ["CFG_BORESIGHT_X", None, None, 2001],
    ["CFG_BORESIGHT_Y", None, None, 2002],
    ["CFG_ROTATION", None, None, 2003],
    ["CFG_LV_W255", None, None, 2004],
    ["CFG_X_W255", None, None, 2005],
    ["CFG_Y_W255", None, None, 2006],

    ["CFG_LV_R255", None, None, 2007],
    ["CFG_X_R255", None, None, 2008],
    ["CFG_Y_R255", None, None, 2009],

    ["CFG_LV_G255", None, None, 2010],
    ["CFG_X_G255", None, None, 2011],
    ["CFG_Y_G255", None, None, 2012],

    ["CFG_LV_B255", None, None, 2013],
    ["CFG_X_B255", None, None, 2014],
    ["CFG_Y_B255", None, None, 2015],

    ["CFG_TemperatureW", None, None, 2016],
    ["CFG_TemperatureR", None, None, 2017],
    ["CFG_TemperatureG", None, None, 2018],
    ["CFG_TemperatureB", None, None, 2019],
    ["CFG_TemperatureWD", None, None, 2020],

    ["CFG_WhitePointGLR", None, None, 2021],
    ["CFG_WhitePointGLG", None, None, 2022],
    ["CFG_WhitePointGLB", None, None, 2023],

    ["CFG_CS", None, None, 2024],
    ["CFG_VALIDATION_FIELD", None, None, 2025],

    ['POST_DATA_CHECK', True, True, 3001],
    ['RESOLUTION_CHECK', True, True, 3002],

    ["POST_WRITE_COUNTS", 0, 5, 5001],
    ["WRITE_COUNTS_CHECK", True, True, 5002],
]

global STATION_LIMITS
STATION_LIMITS = []
# turn the above array of arrays into
# a dictionary of arrays for ease of typing
for station_limit in STATION_LIMITS_ARRAYS:
    STATION_LIMITS.append(dict(zip(['name', 'low_limit', 'high_limit', 'unique_id'], station_limit)))
