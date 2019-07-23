
STATION_LIMITS_ARRAYS = [
    ["W255_NumDarkParticles", -1E+12, 1E+12, 101],
    ["W255_NumDarkBlobs", -1E+12, 1E+12, 102],
    ["W255_NumBrightParticles", -1E+12, 1E+12, 103],
    ["W255_NumBrightBlobs", -1E+12, 1E+12, 104],
    ["W255_NumDefects", -1E+12, 1E+12, 105],

    ["W000_NumDarkParticles", -1E+12, 1E+12, 106],
    ["W000_NumDarkBlobs", -1E+12, 1E+12, 107],
    ["W000_NumBrightParticles", -1E+12, 1E+12, 108],
    ["W000_NumBrightBlobs", -1E+12, 1E+12, 109],
    ["W000_NumDefects", -1E+12, 1E+12, 110],

    ["R255_NumDarkParticles", -1E+12, 1E+12, 111],
    ["R255_NumDarkBlobs", -1E+12, 1E+12, 112],
    ["R255_NumBrightParticles", -1E+12, 1E+12, 113],
    ["R255_NumBrightBlobs", -1E+12, 1E+12, 114],
    ["R255_NumDefects", -1E+12, 1E+12, 115],

    ["G255_NumDarkParticles", -1E+12, 1E+12, 116],
    ["G255_NumDarkBlobs", -1E+12, 1E+12, 117],
    ["G255_NumBrightParticles", -1E+12, 1E+12, 118],
    ["G255_NumBrightBlobs", -1E+12, 1E+12, 119],
    ["G255_NumDefects", -1E+12, 1E+12, 120],

    ["B255_NumDarkParticles", -1E+12, 1E+12, 121],
    ["B255_NumDarkBlobs", -1E+12, 1E+12, 122],
    ["B255_NumBrightParticles", -1E+12, 1E+12, 123],
    ["B255_NumBrightBlobs", -1E+12, 1E+12, 124],
    ["B255_NumDefects", -1E+12, 1E+12, 125],

    ["SaveRawImage_success", -1E+12, 1, 126],
]

global STATION_LIMITS
STATION_LIMITS = []
# turn the above array of arrays into
# a dictionary of arrays for ease of typing
for station_limit in STATION_LIMITS_ARRAYS:
    STATION_LIMITS.append(dict(zip(['name', 'low_limit', 'high_limit', 'unique_id'], station_limit)))
