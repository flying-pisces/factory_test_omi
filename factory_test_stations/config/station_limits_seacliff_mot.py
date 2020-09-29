
STATION_LIMITS_ARRAYS = [
    ["TEST_RAW_IMAGE_SAVE_SUCCESS_1", 1, 1, 11],
    ["TEST_RAW_IMAGE_SAVE_SUCCESS_2", 1, 1, 12],
    ["TEST_RAW_IMAGE_SAVE_SUCCESS_3", 1, 1, 13],
    ["TEST_RAW_IMAGE_SAVE_SUCCESS_4", 1, 1, 14],
    ["TEST_RAW_IMAGE_SAVE_SUCCESS_5", 1, 1, 15],
    ["TEST_RAW_IMAGE_SAVE_SUCCESS_6", 1, 1, 16],
    ["TEST_RAW_IMAGE_SAVE_SUCCESS_7", 1, 1, 17],
    ["TEST_RAW_IMAGE_SAVE_SUCCESS_8", 1, 1, 18],
    ["TEST_RAW_IMAGE_SAVE_SUCCESS_9", 1, 1, 19],
    ["TEST_RAW_IMAGE_SAVE_SUCCESS_10", 1, 1, 20],
]

global STATION_LIMITS
STATION_LIMITS = []
# turn the above array of arrays into
# a dictionary of arrays for ease of typing
for station_limit in STATION_LIMITS_ARRAYS:
    STATION_LIMITS.append(dict(zip(['name', 'low_limit', 'high_limit', 'unique_id'], station_limit)))
