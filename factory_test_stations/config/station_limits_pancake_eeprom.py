CURRENT_FW_VERSION = 1001

STATION_LIMITS_ARRAYS = [
    ["TEST ITEM", 1, 5, 10],
    ["Verify Firmware Load", CURRENT_FW_VERSION, CURRENT_FW_VERSION, 11],
]

global STATION_LIMITS
STATION_LIMITS = []
# turn the above array of arrays into
# a dictionary of arrays for ease of typing
for station_limit in STATION_LIMITS_ARRAYS:
    STATION_LIMITS.append(dict(zip(['name', 'low_limit', 'high_limit', 'unique_id'], station_limit)))
