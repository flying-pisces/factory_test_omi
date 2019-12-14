CURRENT_FW_VERSION = 1001

STATION_LIMITS_ARRAYS = [
    ["TT_Version", 'MPK_API_CS-1.0.12.0', 'MPK_API_CS-1.0.12.0', 96],
    ["DUT_ScreenOnRetries", 0, 10, 97],
    ["DUT_ScreenOnStatus", True, True, 98],
    ["ENV_ParticleCounter", 0, 1000, 99],

    ['W255_Brightness_Variation', 0, 0.02, 10],
    ['W127_Brightness_Variation', 0, 0.02, 11],

    ['W255_Brightness_Max',  None, None,  12],
    ['W127_Brightness_Max',  None, None, 13],

    ['R255_Color_Variation', 0, 0.01, 14],
    ['G255_Color_Variation', 0, 0.01, 15],
    ['B255_Color_Variation', 0, 0.01, 16],
    ['W255_Color_Variation', 0, 0.01, 17],

    ['R255_Max_Neighbor_Color_Variation', 0, 0.005, 18],
    ['G255_Max_Neighbor_Color_Variation', 0, 0.005, 19],
    ['B255_Max_Neighbor_Color_Variation', 0, 0.005, 20],
    ['W255_Max_Neighbor_Color_Variation', 0, 0.005, 21],

    # Avgu/Avgv/CenterLv/AvgLv/LvUniformity
    ["W255_Avgu",  -1E+12, 1E+12, 101],
    ["W255_Avgv",  -1E+12, 1E+12, 102],
    ["W255_CenterLv", 400, 600, 103],
    ["W255_AvgLv", -1E+12, 1E+12, 104],
    ["W255_LvUniformity",  -1E+12, 1E+12, 105],
    ["W255_GlobalContrast",  -1E+12, 1E+12, 106],

    ["W180_Avgu",  -1E+12, 1E+12, 111],
    ["W180_Avgv",  -1E+12, 1E+12, 112],
    ["W180_CenterLv",  -1E+12, 1E+12, 113],
    ["W180_AvgLv", -1E+12, 1E+12, 114],
    ["W180_LvUniformity", -1E+12, 1E+12, 115],
    ["W180_GlobalContrast", -1E+12, 1E+12, 116],

    ["W127_Avgu",  -1E+12, 1E+12, 121],
    ["W127_Avgv",  -1E+12, 1E+12, 122],
    ["W127_CenterLv",  -1E+12, 1E+12, 123],
    ["W127_AvgLv", -1E+12, 1E+12, 124],
    ["W127_LvUniformity", -1E+12, 1E+12, 125],
    ["W127_GlobalContrast", -1E+12, 1E+12, 126],

    ["W090_Avgu", -1E+12, 1E+12, 131],
    ["W090_Avgv", -1E+12, 1E+12, 132],
    ["W090_CenterLv", -1E+12, 1E+12, 133],
    ["W090_AvgLv", -1E+12, 1E+12, 134],
    ["W090_LvUniformity", -1E+12, 1E+12, 135],
    ["W090_GlobalContrast", -1E+12, 1E+12, 136],

    ["R255_Avgu", -1E+12, 1E+12, 141],
    ["R255_Avgv", -1E+12, 1E+12, 142],
    ["R255_CenterLv", -1E+12, 1E+12, 143],
    ["R255_AvgLv", -1E+12, 1E+12, 144],
    ["R255_LvUniformity", -1E+12, 1E+12, 145],
    ["R255_GlobalContrast", -1E+12, 1E+12, 146],

    ["G255_Avgu", -1E+12, 1E+12, 151],
    ["G255_Avgv", -1E+12, 1E+12, 152],
    ["G255_CenterLv", -1E+12, 1E+12, 153],
    ["G255_AvgLv", -1E+12, 1E+12, 154],
    ["G255_LvUniformity", -1E+12, 1E+12, 155],
    ["G255_GlobalContrast", -1E+12, 1E+12, 156],

    ["B255_Avgu", -1E+12, 1E+12, 161],
    ["B255_Avgv", -1E+12, 1E+12, 162],
    ["B255_CenterLv", -1E+12, 1E+12, 163],
    ["B255_AvgLv", -1E+12, 1E+12, 164],
    ["B255_LvUniformity", -1E+12, 1E+12, 165],
    ["B255_GlobalContrast", -1E+12, 1E+12, 166],

    ["DISPLAY_GAMMA",  -1E+12, 1E+12, 3000],
]
global STATION_LIMITS

STATION_LIMITS = []
# turn the above array of arrays into
# a dictionary of arrays for ease of typing
for station_limit in STATION_LIMITS_ARRAYS:
    STATION_LIMITS.append(dict(zip(['name', 'low_limit', 'high_limit', 'unique_id'], station_limit)))
