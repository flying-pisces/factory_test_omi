CURRENT_FW_VERSION = 1001

STATION_LIMITS_ARRAYS = [
    ["SW_VERSION", None, None, 79],
    ["JUDGED_BY_CAM", True, True, 80],

    ["PRE_WRITE_COUNTS", 0, 7, 1000],

    # all the setting should be changed in this fixture.
    # ["CURRENT_BAK_BORESIGHT_X", None, None, 1001],
    # ["CURRENT_BAK_BORESIGHT_Y", None, None, 1002],
    # ["CURRENT_BAK_ROTATION", None, None, 1003],
    # ["CURRENT_BAK_LV_W255", None, None, 1004],
    # ["CURRENT_BAK_X_W255", None, None, 1005],
    # ["CURRENT_BAK_Y_W255", None, None, 1006],
    # ["CURRENT_BAK_LV_R255", None, None, 1007],
    # ["CURRENT_BAK_X_R255", None, None, 1008],
    # ["CURRENT_BAK_Y_R255", None, None, 1009],
    #
    # ["CURRENT_BAK_LV_G255", None, None, 1010],
    # ["CURRENT_BAK_X_G255", None, None, 1011],
    # ["CURRENT_BAK_Y_G255", None, None, 1012],
    #
    # ["CURRENT_BAK_LV_B255", None, None, 1013],
    # ["CURRENT_BAK_X_B255", None, None, 1014],
    # ["CURRENT_BAK_Y_B255", None, None, 1015],
    #
    # ["CURRENT_CS", None, None, 1016],
    # ["CURRENT_VALIDATION_FIELD", None, None, 1017],

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

    ["CFG_CS", None, None, 2016],
    ["CFG_VALIDATION_FIELD", None, None, 2017],

    ['POST_DATA_CHECK', True, True, 3001],

    ["POST_WRITE_COUNTS", 0, 7, 5001],
    ["WRITE_COUNTS_CHECK", True, True, 5002],
]

global STATION_LIMITS
STATION_LIMITS = []
# turn the above array of arrays into
# a dictionary of arrays for ease of typing
for station_limit in STATION_LIMITS_ARRAYS:
    STATION_LIMITS.append(dict(zip(['name', 'low_limit', 'high_limit', 'unique_id'], station_limit)))
