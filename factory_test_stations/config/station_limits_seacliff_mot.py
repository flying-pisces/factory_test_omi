
STATION_LIMITS_ARRAYS = [
    ["SW_VERSION", None, None, 93],
    ["EQUIP_VERSION", None, None, 94],
    ["DUT_ScreenOnRetries", 0, 5, 95],
    ["DUT_ScreenOnStatus", True, True, 96],
    ["DUT_CancelByOperator", False, False, 97],
    ["ENV_ParticleCounter", None, None, 98],
    ["ENV_AmbientTemp", None, None, 99],
    ["DUT_AlignmentSuccess", True, True, 100],

    ["Test_RAW_IMAGE_SAVE_SUCCESS_normal_W255", True, True, 10001],
    ["Test_RAW_IMAGE_SAVE_SUCCESS_normal_G127", True, True, 10002],
    ["Test_RAW_IMAGE_SAVE_SUCCESS_normal_W000", True, True, 10003],
    ["Test_RAW_IMAGE_SAVE_SUCCESS_normal_RGB", True, True, 10004],
    ["Test_RAW_IMAGE_SAVE_SUCCESS_normal_R255", True, True, 10005],
    ["Test_RAW_IMAGE_SAVE_SUCCESS_normal_G255", True, True, 10006],
    ["Test_RAW_IMAGE_SAVE_SUCCESS_normal_B255", True, True, 10007],
    ["Test_RAW_IMAGE_SAVE_SUCCESS_normal_GreenContrast", True, True, 10008],
    ["Test_RAW_IMAGE_SAVE_SUCCESS_normal_WhiteContrast", True, True, 10009],
    ["Test_RAW_IMAGE_SAVE_SUCCESS_normal_GreenSharpness", True, True, 10010],
    ["Test_RAW_IMAGE_SAVE_SUCCESS_normal_GreenDistortion", True, True, 10011],

    ["Test_RAW_IMAGE_SAVE_SUCCESS_extendedz_GreenDistortion", True, True, 10012],
    ["Test_RAW_IMAGE_SAVE_SUCCESS_blemish_W255", True, True, 10013],
    ["Test_RAW_IMAGE_SAVE_SUCCESS_extendedxpos_W255", True, True, 10014],
    ["Test_RAW_IMAGE_SAVE_SUCCESS_extendedxneg_W255", True, True, 10015],
    ["Test_RAW_IMAGE_SAVE_SUCCESS_extendedypos_W255", True, True, 10016],
    ["Test_RAW_IMAGE_SAVE_SUCCESS_extendedyneg_W255", True, True, 10017],
]

global STATION_LIMITS
STATION_LIMITS = []
# turn the above array of arrays into
# a dictionary of arrays for ease of typing
for station_limit in STATION_LIMITS_ARRAYS:
    STATION_LIMITS.append(dict(zip(['name', 'low_limit', 'high_limit', 'unique_id'], station_limit)))
