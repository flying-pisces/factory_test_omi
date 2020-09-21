
STATION_LIMITS_ARRAYS = [
    ["SW_VERSION", None, None, 95],
    ["MPK_API_Version", 'MPK_API_CS-1.0.13.0', 'MPK_API_CS-1.0.13.0', 96],
    ["DUT_ScreenOnRetries", 0, 5, 97],
    ["DUT_ScreenOnStatus", True, True, 98],
    ["ENV_ParticleCounter", None, None, 99],

    ["W000_SuperQuality_Brighter_NumDefects", None, None, 30010],
    ["W000_SuperQuality_Brighter_MinSeparationDistance", None, None, 30011],
    ["W000_SuperQuality_Brighter_Res", True, True, 30012],

    ["W000_SuperQuality_Dimmer_NumDefects", None, None, 30013],
    ["W000_SuperQuality_Dimmer_MinSeparationDistance", None, None, 30014],
    ["W000_SuperQuality_Dimmer_Res", True, True, 30015],

    ["W000_Quality_Brighter_NumDefects", 0, 0, 30016],
    ["W000_Quality_Brighter_MinSeparationDistance", None, None, 30017],
    ["W000_Quality_Brighter_Res", True, True, 30018],

    ["W000_Quality_DimmerU_NumDefects", 0, 2, 30019],
    ["W000_Quality_DimmerU_MinSeparationDistance", None, None, 30020],
    ["W000_Quality_DimmerU_Res", True, True, 30021],

    ["W000_Quality_DimmerL_NumDefects", 0, 3, 30022],
    ["W000_Quality_DimmerL_MinSeparationDistance", None, None, 30023],
    ["W000_Quality_DimmerL_Res", True, True, 30024],

    ["W255_SuperQuality_NumDefects", None, None, 30025],
    ["W255_SuperQuality_MinSeparationDistance", None, None, 30026],
    ["W255_SuperQuality_Res", True, True, 30027],

    ["W255_Quality_NumDefects", None, None, 30028],
    ["W255_Quality_MinSeparationDistance", None, None, 30029],
    ["W255_Quality_Res", True, True, 30030],

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

    # ["W255_NumDarkParticles", None, None, 101],
    # ["W255_NumDarkBlobs", None, None, 102],
    # ["W255_NumBrightParticles", None, None, 103],
    # ["W255_NumBrightBlobs", None, None, 104],
    # ["W255_NumDefects", None, None, 105],
    # ["W255_BlemishIndex", None, None, 106],
    #
    # ["W000_NumDarkParticles", None, None, 111],
    # ["W000_NumDarkBlobs", None, None, 112],
    # ["W000_NumBrightParticles", None, None, 113],
    # ["W000_NumBrightBlobs", None, None, 114],
    # ["W000_NumDefects", None, None, 115],
    # ["W000_BlemishIndex", None, None, 116],
    #
    # ["R255_NumDarkParticles", None, None, 121],
    # ["R255_NumDarkBlobs", None, None, 122],
    # ["R255_NumBrightParticles", None, None, 123],
    # ["R255_NumBrightBlobs", None, None, 124],
    # ["R255_NumDefects", None, None, 125],
    # ["R255_BlemishIndex", None, None, 126],
    #
    # ["G255_NumDarkParticles", None, None, 131],
    # ["G255_NumDarkBlobs", None, None, 132],
    # ["G255_NumBrightParticles", None, None, 133],
    # ["G255_NumBrightBlobs", None, None, 134],
    # ["G255_NumDefects", None, None, 135],
    # ["G255_BlemishIndex", None, None, 136],
    #
    # ["B255_NumDarkParticles", None, None, 141],
    # ["B255_NumDarkBlobs", None, None, 142],
    # ["B255_NumBrightParticles", None, None, 143],
    # ["B255_NumBrightBlobs", None, None, 144],
    # ["B255_NumDefects", None, None, 145],
    # ["B255_BlemishIndex", None, None, 146],
]

global STATION_LIMITS
STATION_LIMITS = []
# turn the above array of arrays into
# a dictionary of arrays for ease of typing
for station_limit in STATION_LIMITS_ARRAYS:
    STATION_LIMITS.append(dict(zip(['name', 'low_limit', 'high_limit', 'unique_id'], station_limit)))
