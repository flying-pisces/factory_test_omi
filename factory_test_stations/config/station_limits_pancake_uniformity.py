CURRENT_FW_VERSION = 1001

STATION_LIMITS_ARRAYS = [
    ["TT_Version", 'MPK_API_CS-1.0.12.0', 'MPK_API_CS-1.0.12.0', 96],
    ["DUT_ScreenOnRetries", 0, 10, 97],
    ["DUT_ScreenOnStatus", True, True, 98],
    ["ENV_ParticleCounter", 0, 1000, 99],

    ['W255_Brightness_Variation', 0, 0.02, 10],
    ['W127_Brightness_Variation', 0, 0.02, 11],
    ['R255_Color_Variation', 0, 0.01, 12],
    ['G255_Color_Variation', 0, 0.01, 13],
    ['B255_Color_Variation', 0, 0.01, 14],
    ['W255_Color_Variation', 0, 0.01, 15],

    ['R255_Max_Neighbor_Color_Variation', 0, 0.005, 16],
    ['G255_Max_Neighbor_Color_Variation', 0, 0.005, 17],
    ['B255_Max_Neighbor_Color_Variation', 0, 0.005, 18],
    ['W255_Max_Neighbor_Color_Variation', 0, 0.005, 19],

    # Avgu/Avgv/CenterLv/AvgLv/LvUniformity
    ["White_Avgu",  -1E+12, 1E+12, 101],
    ["White_Avgv",  -1E+12, 1E+12, 102],
    ["White_CenterLv", 400, 600, 103],
    ["White_AvgLv", -1E+12, 1E+12, 104],
    ["White_LvUniformity",  -1E+12, 1E+12, 105],
    ["White_GlobalContrast",  -1E+12, 1E+12, 106],

    ["Gray180_Avgu",  -1E+12, 1E+12, 111],
    ["Gray180_Avgv",  -1E+12, 1E+12, 112],
    ["Gray180_CenterLv",  -1E+12, 1E+12, 113],
    ["Gray180_AvgLv", -1E+12, 1E+12, 114],
    ["Gray180_LvUniformity", -1E+12, 1E+12, 115],
    ["Gray180_GlobalContrast", -1E+12, 1E+12, 116],

    ["Gray127_Avgu",  -1E+12, 1E+12, 121],
    ["Gray127_Avgv",  -1E+12, 1E+12, 122],
    ["Gray127_CenterLv",  -1E+12, 1E+12, 123],
    ["Gray127_AvgLv", -1E+12, 1E+12, 124],
    ["Gray127_LvUniformity", -1E+12, 1E+12, 125],
    ["Gray127_GlobalContrast", -1E+12, 1E+12, 126],

    ["Gray90_Avgu", -1E+12, 1E+12, 131],
    ["Gray90_Avgv", -1E+12, 1E+12, 132],
    ["Gray90_CenterLv", -1E+12, 1E+12, 133],
    ["Gray90_AvgLv", -1E+12, 1E+12, 134],
    ["Gray90_LvUniformity", -1E+12, 1E+12, 135],
    ["Gray90_GlobalContrast", -1E+12, 1E+12, 136],

    ["Red_Avgu", -1E+12, 1E+12, 141],
    ["Red_Avgv", -1E+12, 1E+12, 142],
    ["Red_CenterLv", -1E+12, 1E+12, 143],
    ["Red_AvgLv", -1E+12, 1E+12, 144],
    ["Red_LvUniformity", -1E+12, 1E+12, 145],
    ["Red_GlobalContrast", -1E+12, 1E+12, 146],

    ["Green_Avgu", -1E+12, 1E+12, 151],
    ["Green_Avgv", -1E+12, 1E+12, 152],
    ["Green_CenterLv", -1E+12, 1E+12, 153],
    ["Green_AvgLv", -1E+12, 1E+12, 154],
    ["Green_LvUniformity", -1E+12, 1E+12, 155],
    ["Green_GlobalContrast", -1E+12, 1E+12, 156],

    ["Blue_Avgu", -1E+12, 1E+12, 161],
    ["Blue_Avgv", -1E+12, 1E+12, 162],
    ["Blue_CenterLv", -1E+12, 1E+12, 163],
    ["Blue_AvgLv", -1E+12, 1E+12, 164],
    ["Blue_LvUniformity", -1E+12, 1E+12, 165],
    ["Blue_GlobalContrast", -1E+12, 1E+12, 166],

    ["DISPLAY_GAMMA",  -1E+12, 1E+12, 3000],
]
global STATION_LIMITS

STATION_LIMITS = []
# turn the above array of arrays into
# a dictionary of arrays for ease of typing
for station_limit in STATION_LIMITS_ARRAYS:
    STATION_LIMITS.append(dict(zip(['name', 'low_limit', 'high_limit', 'unique_id'], station_limit)))
