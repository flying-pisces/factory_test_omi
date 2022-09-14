CURRENT_FW_VERSION = 1001

STATION_LIMITS_ARRAYS = [
    ["Device_SN", None, None, 20008],
    ["Device_Model", None, None, 20009],
    ["Device_Firmware_Ver", None, None, 20010],
    ["Nominal_W255_OnAxis Lum", 85, None, 20011],
    ["Nominal_W255_OnAxis x", 0.291, 0.351, 20012],
    ["Nominal_W255_OnAxis y", 0.292, 0.382, 20013],
    ["Nominal_W255_Exposure", None, None, 20014],

    ["Nominal_R255_OnAxis Lum", 25, None, 21011],
    ["Nominal_R255_OnAxis x", 0.6, 0.65, 21012],
    ["Nominal_R255_OnAxis y", 0.3, 0.38, 21013],
    ["Nominal_R255_Exposure", None, None, 21014],

    ["Nominal_G255_OnAxis Lum", 70, None, 22011],
    ["Nominal_G255_OnAxis x", 0.28, 0.38, 22012],
    ["Nominal_G255_OnAxis y", 0.5, 0.6, 22013],
    ["Nominal_G255_Exposure", None, None, 22014],

    ["Nominal_B255_OnAxis Lum", 10, None, 23011],
    ["Nominal_B255_OnAxis x", 0.14, 0.21, 23012],
    ["Nominal_B255_OnAxis y", 0.03, 0.05, 23013],
    ["Nominal_B255_Exposure", None, None, 23014],
]

global STATION_LIMITS
STATION_LIMITS = []
# turn the above array of arrays into
# a dictionary of arrays for ease of typing
for station_limit in STATION_LIMITS_ARRAYS:
    STATION_LIMITS.append(dict(zip(['name', 'low_limit', 'high_limit', 'unique_id'], station_limit)))
