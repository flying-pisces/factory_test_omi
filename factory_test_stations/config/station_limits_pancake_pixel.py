
STATION_LIMITS_ARRAYS = [
    ["TT_Version", '1.0.0', '1.0.0', 96],
    ["DUT_ScreenOnRetries", 0, 10, 97],
    ["DUT_ScreenOnStatus", 1, 1, 98],
    ["ENV_ParticleCounter", 0, 1000, 99],

    ["W255_NumDarkParticles", -1E+12, 1E+12, 101],
    ["W255_NumDarkBlobs", -1E+12, 1E+12, 102],
    ["W255_NumBrightParticles", -1E+12, 1E+12, 103],
    ["W255_NumBrightBlobs", -1E+12, 1E+12, 104],
    ["W255_NumDefects", -1E+12, 1E+12, 105],
    ["W255_BlemishIndex", -1E+12, 1E+12, 106],

    ["W000_NumDarkParticles", -1E+12, 1E+12, 111],
    ["W000_NumDarkBlobs", -1E+12, 1E+12, 112],
    ["W000_NumBrightParticles", -1E+12, 1E+12, 113],
    ["W000_NumBrightBlobs", -1E+12, 1E+12, 114],
    ["W000_NumDefects", -1E+12, 1E+12, 115],
    ["W000_BlemishIndex", -1E+12, 1E+12, 116],

    ["R255_NumDarkParticles", -1E+12, 1E+12, 121],
    ["R255_NumDarkBlobs", -1E+12, 1E+12, 122],
    ["R255_NumBrightParticles", -1E+12, 1E+12, 123],
    ["R255_NumBrightBlobs", -1E+12, 1E+12, 124],
    ["R255_NumDefects", -1E+12, 1E+12, 125],
    ["R255_BlemishIndex", -1E+12, 1E+12, 126],

    ["G255_NumDarkParticles", -1E+12, 1E+12, 131],
    ["G255_NumDarkBlobs", -1E+12, 1E+12, 132],
    ["G255_NumBrightParticles", -1E+12, 1E+12, 133],
    ["G255_NumBrightBlobs", -1E+12, 1E+12, 134],
    ["G255_NumDefects", -1E+12, 1E+12, 135],
    ["G255_BlemishIndex", -1E+12, 1E+12, 136],

    ["B255_NumDarkParticles", -1E+12, 1E+12, 141],
    ["B255_NumDarkBlobs", -1E+12, 1E+12, 142],
    ["B255_NumBrightParticles", -1E+12, 1E+12, 143],
    ["B255_NumBrightBlobs", -1E+12, 1E+12, 144],
    ["B255_NumDefects", -1E+12, 1E+12, 145],
    ["B255_BlemishIndex", -1E+12, 1E+12, 146],
]

global STATION_LIMITS
STATION_LIMITS = []
# turn the above array of arrays into
# a dictionary of arrays for ease of typing
for station_limit in STATION_LIMITS_ARRAYS:
    STATION_LIMITS.append(dict(zip(['name', 'low_limit', 'high_limit', 'unique_id'], station_limit)))
