
STATION_LIMITS_ARRAYS = [
    ["TEST ITEM 1", 1, 2, 11],
    ["TEST ITEM 2", 1, 2, 12],
    ["TEST ITEM 3", 1, 2, 13],
]

global STATION_LIMITS
STATION_LIMITS = []
# turn the above array of arrays into
# a dictionary of arrays for ease of typing
for station_limit in STATION_LIMITS_ARRAYS:
    STATION_LIMITS.append(dict(zip(['name', 'low_limit', 'high_limit', 'unique_id'], station_limit)))
