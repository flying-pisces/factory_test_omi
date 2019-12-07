
STATION_LIMITS_ARRAYS = [
    ["TT_Version", 'MPK_API_CS-1.0.12.0', 'MPK_API_CS-1.0.12.0', 96],
    ["DUT_ScreenOnRetries", 0, 10, 97],
    ["DUT_ScreenOnStatus", True, True, 98],
    ["ENV_ParticleCounter", 0, 1000, 99],

    # ["W000_SuperQuality_Brighter_NumDefects", None, None, 10],
    # ["W000_SuperQuality_Brighter_MinSeparationDistance", None, None, 11],
    # ["W000_SuperQuality_Brighter_Res", True, True, 12],
    #
    # ["W000_SuperQuality_Dimmer_NumDefects", None, None, 13],
    # ["W000_SuperQuality_Dimmer_MinSeparationDistance", None, None, 14],
    # ["W000_SuperQuality_Dimmer_Res", True, True, 15],
    #
    # ["W000_Quality_Brighter_NumDefects", 0, 0, 16],
    # ["W000_Quality_Brighter_MinSeparationDistance", None, None, 17],
    # ["W000_Quality_Brighter_Res", True, True, 18],
    #
    # ["W000_Quality_DimmerU_NumDefects", 0, 2, 19],
    # ["W000_Quality_DimmerU_MinSeparationDistance", None, None, 20],
    # ["W000_Quality_DimmerU_Res", True, True, 21],
    #
    # ["W000_Quality_DimmerL_NumDefects", 0, 3, 22],
    # ["W000_Quality_DimmerL_MinSeparationDistance", None, None, 23],
    # ["W000_Quality_DimmerL_Res", True, True, 24],
    #
    # ["W255_SuperQuality_NumDefects", None, None, 25],
    # ["W255_SuperQuality_MinSeparationDistance", None, None, 26],
    # ["W255_SuperQuality_Res", True, True, 27],
    #
    # ["W255_Quality_NumDefects", None, None, 28],
    # ["W255_Quality_MinSeparationDistance", None, None, 29],
    # ["W255_Quality_Res", True, True, 30],
    #
    # ["R255_SuperQuality_NumDefects", 0, 0, 31],
    # ["R255_SuperQuality_MinSeparationDistance", None, None, 32],
    # ["R255_SuperQuality_Res", True, True, 33],
    #
    # ["R255_Quality_NumDefects", 0, 1, 34],
    # ["R255_Quality_MinSeparationDistance", None, None, 35],
    # ["R255_Quality_Res", True, True, 36],
    #
    # ["G255_SuperQuality_NumDefects", 0, 0, 37],
    # ["G255_SuperQuality_MinSeparationDistance", None, None, 38],
    # ["G255_SuperQuality_Res", True, True, 39],
    #
    # ["G255_Quality_NumDefects", 0, 1, 40],
    # ["G255_Quality_MinSeparationDistance", None, None, 41],
    # ["G255_Quality_Res", True, True, 42],
    #
    # ["B255_SuperQuality_NumDefects", 0, 0, 43],
    # ["B255_SuperQuality_MinSeparationDistance", None, None, 44],
    # ["B255_SuperQuality_Res", True, True, 45],
    #
    # ["B255_Quality_NumDefects", 0, 1, 46],
    # ["B255_Quality_MinSeparationDistance", None, None, 47],
    # ["B255_Quality_Res", True, True, 48],

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
