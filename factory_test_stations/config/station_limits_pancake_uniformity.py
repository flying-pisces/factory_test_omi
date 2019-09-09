CURRENT_FW_VERSION = 1001

STATION_LIMITS_ARRAYS = [
    ["DUT_ScreenOnRetries", 0, 100, 97],
    ["DUT_ScreenOnStatus", 0, 100, 98],
    ["ENV_ParticleCounter", 0, 1000, 99],

    ["W255_CenterColor(Cx)",  -1E+12, 1E+12, 101],
    ["W255_CenterColor(Cy)",  -1E+12, 1E+12, 102],
    ["W255_CenterLv",  -1E+12, 1E+12, 103],
    ["W255_MinLv",  -1E+12, 1E+12, 104],
    ["W255_MaxLv",  -1E+12, 1E+12, 105],
    ["W255_MLOGlobalLvMaxVariation", -1E+12, 1E+12, 106],
    ["W255_MLOLocalLvMaxVariation", -1E+12, 1E+12, 107],
    ["W255_MLOGlobalColorMaxVariation", -1E+12, 1E+12, 108],
    ["W255_MLOLocalColorMaxVariation", -1E+12, 1E+12, 109],
    ["W255_Centeru_prime",  -1E+12, 1E+12, 110],
    ["W255_Centerv_prime",  -1E+12, 1E+12, 111],
    ["W255_LvUniformity",  -1E+12, 1E+12, 112], ## added by CY

    ["W180_CenterLv",  -1E+12, 1E+12, 203],
    ["W180_MinLv",  -1E+12, 1E+12, 204],
    ["W180_MaxLv",  -1E+12, 1E+12, 205],
    ["W180_MLOGlobalLvMaxVariation", -1E+12, 1E+12, 206],
    ["W180_MLOLocalLvMaxVariation", -1E+12, 1E+12, 207],
    ["W180_MLOGlobalColorMaxVariation", -1E+12, 1E+12, 208],
    ["W180_MLOLocalColorMaxVariation", -1E+12, 1E+12, 209],
    ["W180_CenterColorDifference", -1E+12, 1E+12, 210],

    ["W127_CenterLv",  -1E+12, 1E+12, 303],
    ["W127_MinLv",  -1E+12, 1E+12, 304],
    ["W127_MaxLv",  -1E+12, 1E+12, 305],
    ["W127_MLOGlobalLvMaxVariation", -1E+12, 1E+12, 306],
    ["W127_MLOLocalLvMaxVariation", -1E+12, 1E+12, 307],
    ["W127_MLOGlobalColorMaxVariation", -1E+12, 1E+12, 308],
    ["W127_MLOLocalColorMaxVariation", -1E+12, 1E+12, 309],
    ["W127_CenterColorDifference", -1E+12, 1E+12, 310],

    ["W090_CenterLv",  -1E+12, 1E+12, 403],
    ["W090_MinLv",  -1E+12, 1E+12, 404],
    ["W090_MaxLv",  -1E+12, 1E+12, 405],
    ["W090_MLOGlobalLvMaxVariation", -1E+12, 1E+12, 406],
    ["W090_MLOLocalLvMaxVariation", -1E+12, 1E+12, 407],
    ["W090_MLOGlobalColorMaxVariation", -1E+12, 1E+12, 408],
    ["W090_MLOLocalColorMaxVariation", -1E+12, 1E+12, 409],
    ["W090_CenterColorDifference", -1E+12, 1E+12, 410],

    ["R255_CenterColor(Cx)",  -1E+12, 1E+12, 801],
    ["R255_CenterColor(Cy)",  -1E+12, 1E+12, 802],
    ["R255_CenterLv",  -1E+12, 1E+12, 803],
    ["R255_MinLv",  -1E+12, 1E+12, 804],
    ["R255_MaxLv",  -1E+12, 1E+12, 805],
    ["R255_MLOGlobalLvMaxVariation", -1E+12, 1E+12, 806],
    ["R255_MLOLocalLvMaxVariation", -1E+12, 1E+12, 807],
    ["R255_MLOGlobalColorMaxVariation", -1E+12, 1E+12, 808],
    ["R255_MLOLocalColorMaxVariation", -1E+12, 1E+12, 809],
    ["R255_Centeru_prime",  -1E+12, 1E+12, 810],
    ["R255_Centerv_prime",  -1E+12, 1E+12, 811],

    ["G255_CenterColor(Cx)",  -1E+12, 1E+12, 901],
    ["G255_CenterColor(Cy)",  -1E+12, 1E+12, 902],
    ["G255_CenterLv",  -1E+12, 1E+12, 903],
    ["G255_MinLv",  -1E+12, 1E+12, 904],
    ["G255_MaxLv",  -1E+12, 1E+12, 905],
    ["G255_MLOGlobalLvMaxVariation", -1E+12, 1E+12, 906],
    ["G255_MLOLocalLvMaxVariation", -1E+12, 1E+12, 907],
    ["G255_MLOGlobalColorMaxVariation", -1E+12, 1E+12, 908],
    ["G255_MLOLocalColorMaxVariation", -1E+12, 1E+12, 909],
    ["G255_Centeru_prime",  -1E+12, 1E+12, 910],
    ["G255_Centerv_prime",  -1E+12, 1E+12, 911],

    ["B255_CenterColor(Cx)",  -1E+12, 1E+12, 1001],
    ["B255_CenterColor(Cy)",  -1E+12, 1E+12, 1002],
    ["B255_CenterLv",  -1E+12, 1E+12, 1003],
    ["B255_MinLv",  -1E+12, 1E+12, 1004],
    ["B255_MaxLv",  -1E+12, 1E+12, 1005],
    ["B255_MLOGlobalLvMaxVariation", -1E+12, 1E+12, 1006],
    ["B255_MLOLocalLvMaxVariation", -1E+12, 1E+12, 1007],
    ["B255_MLOGlobalColorMaxVariation", -1E+12, 1E+12, 1008],
    ["B255_MLOLocalColorMaxVariation", -1E+12, 1E+12, 1009],
    ["B255_Centeru_prime",  -1E+12, 1E+12, 1010],
    ["B255_Centerv_prime",  -1E+12, 1E+12, 1011],

    ["DISPLAY_GAMMA",  -1E+12, 1E+12, 3000],
]
global STATION_LIMITS

STATION_LIMITS = []
# turn the above array of arrays into
# a dictionary of arrays for ease of typing
for station_limit in STATION_LIMITS_ARRAYS:
    STATION_LIMITS.append(dict(zip(['name', 'low_limit', 'high_limit', 'unique_id'], station_limit)))
