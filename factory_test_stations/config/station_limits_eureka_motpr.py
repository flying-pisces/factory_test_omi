CURRENT_FW_VERSION = 1001

STATION_LIMITS_ARRAYS = [
    ['STATION_SN', None, None, 20004],
    ['SW_Version', None, None, 20005],
    ["EQUIP_VERSION", None, None, 20006],
    ["Device_SN", None, None, 20007],
    ["Device_Model", None, None, 20008],
    ["DUT_ModuleType", None, None, 20009],


    ["ERR_FIXTURE", False, False, 101],
    ["ERR_EQUIPMENT", False, False, 102],
    ["ERR_DUT", False, False, 103],

    ["ENV_ParticleCounter", None, None, 20010],

    ["Nominal_W255_OnAxis Lum", 85, 135, 20011],
    ["Nominal_W255_OnAxis x", 0.29, 0.35, 20012],
    ["Nominal_W255_OnAxis y", 0.293, 0.383, 20013],
    ["Nominal_W255_TEMPERATURE", None, None, 20014],
    ["Nominal_W255_Exposure", None, None, 20015],

    ["Nominal_R255_OnAxis Lum", None, None, 21011],
    ["Nominal_R255_OnAxis x", 0.622, 0.667, 21012],
    ["Nominal_R255_OnAxis y", 0.316, 0.366, 21013],
    ["Nominal_R255_TEMPERATURE", None, None, 21014],
    ["Nominal_R255_Exposure", None, None, 21015],

    ["Nominal_G255_OnAxis Lum", None, None, 22011],
    ["Nominal_G255_OnAxis x", 0.274, 0.324, 22012],
    ["Nominal_G255_OnAxis y", 0.586, 0.636, 22013],
    ["Nominal_G255_TEMPERATURE", None, None, 22014],
    ["Nominal_G255_Exposure", None, None, 22015],

    ["Nominal_B255_OnAxis Lum", None, None, 23011],
    ["Nominal_B255_OnAxis x", 0.128, 0.178, 23012],
    ["Nominal_B255_OnAxis y", 0.036, 0.086, 23013],
    ["Nominal_B255_TEMPERATURE", None, None, 23014],
    ["Nominal_B255_Exposure", None, None, 23015],

    ["Nominal_CW255_OnAxis Lum", None, None, 24012],
    ["Nominal_CW255_TEMPERATURE", None, None, 24013],
    ["Nominal_CW000_OnAxis Lum", None, None, 24014],
    ["Nominal_CW000_TEMPERATURE", None, None, 24015],
    ["Nominal_OnAxisContrast", None, None, 24016],

]

global STATION_LIMITS
STATION_LIMITS = []
# turn the above array of arrays into
# a dictionary of arrays for ease of typing
for station_limit in STATION_LIMITS_ARRAYS:
    STATION_LIMITS.append(dict(zip(['name', 'low_limit', 'high_limit', 'unique_id'], station_limit)))
