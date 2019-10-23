
STATION_LIMITS_ARRAYS = [
    ["TT_Version", 'MPK_API_CS-1.0.6.0', 'MPK_API_CS-1.0.6.0', 96],
    ["DUT_ScreenOnRetries", 0, 10, 97],
    ["DUT_ScreenOnStatus", True, True, 98],
    ["ENV_ParticleCounter", 0, 1000, 99],

    ["White_NumDarkParticles", -1E+12, 1E+12, 101],
    ["White_NumDarkBlobs", -1E+12, 1E+12, 102],
    ["White_NumBrightParticles", -1E+12, 1E+12, 103],
    ["White_NumBrightBlobs", -1E+12, 1E+12, 104],
    ["White_NumDefects", -1E+12, 1E+12, 105],
    ["White_BlemishIndex", -1E+12, 1E+12, 106],

    ["Black_NumDarkParticles", -1E+12, 1E+12, 111],
    ["Black_NumDarkBlobs", -1E+12, 1E+12, 112],
    ["Black_NumBrightParticles", -1E+12, 1E+12, 113],
    ["Black_NumBrightBlobs", -1E+12, 1E+12, 114],
    ["Black_NumDefects", -1E+12, 1E+12, 115],
    ["Black_BlemishIndex", -1E+12, 1E+12, 116],

    ["Red_NumDarkParticles", -1E+12, 1E+12, 121],
    ["Red_NumDarkBlobs", -1E+12, 1E+12, 122],
    ["Red_NumBrightParticles", -1E+12, 1E+12, 123],
    ["Red_NumBrightBlobs", -1E+12, 1E+12, 124],
    ["Red_NumDefects", -1E+12, 1E+12, 125],
    ["Red_BlemishIndex", -1E+12, 1E+12, 126],

    ["Green_NumDarkParticles", -1E+12, 1E+12, 131],
    ["Green_NumDarkBlobs", -1E+12, 1E+12, 132],
    ["Green_NumBrightParticles", -1E+12, 1E+12, 133],
    ["Green_NumBrightBlobs", -1E+12, 1E+12, 134],
    ["Green_NumDefects", -1E+12, 1E+12, 135],
    ["Green_BlemishIndex", -1E+12, 1E+12, 136],

    ["Blue_NumDarkParticles", -1E+12, 1E+12, 141],
    ["Blue_NumDarkBlobs", -1E+12, 1E+12, 142],
    ["Blue_NumBrightParticles", -1E+12, 1E+12, 143],
    ["Blue_NumBrightBlobs", -1E+12, 1E+12, 144],
    ["Blue_NumDefects", -1E+12, 1E+12, 145],
    ["Blue_BlemishIndex", -1E+12, 1E+12, 146],
]

global STATION_LIMITS
STATION_LIMITS = []
# turn the above array of arrays into
# a dictionary of arrays for ease of typing
for station_limit in STATION_LIMITS_ARRAYS:
    STATION_LIMITS.append(dict(zip(['name', 'low_limit', 'high_limit', 'unique_id'], station_limit)))
