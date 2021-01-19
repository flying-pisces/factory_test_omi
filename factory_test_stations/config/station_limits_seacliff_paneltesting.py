CURRENT_FW_VERSION = 1001

STATION_LIMITS_ARRAYS = [
    ["SW_VERSION", None, None, 94],
    ["FW_VERSION_FIXTURE", None, None, 95],
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

    ["R255_SuperQuality_NumDefects", 0, 0, 30031],
    ["R255_SuperQuality_MinSeparationDistance", None, None, 30032],
    ["R255_SuperQuality_Res", True, True, 30033],

    ["R255_Quality_NumDefects", 0, 1, 30034],
    ["R255_Quality_MinSeparationDistance", None, None, 30035],
    ["R255_Quality_Res", True, True, 30036],

    ["G255_SuperQuality_NumDefects", 0, 0, 30037],
    ["G255_SuperQuality_MinSeparationDistance", None, None, 30038],
    ["G255_SuperQuality_Res", True, True, 30039],

    ["G255_Quality_NumDefects", 0, 1, 30040],
    ["G255_Quality_MinSeparationDistance", None, None, 30041],
    ["G255_Quality_Res", True, True, 30042],

    ["B255_SuperQuality_NumDefects", 0, 0, 30043],
    ["B255_SuperQuality_MinSeparationDistance", None, None, 30044],
    ["B255_SuperQuality_Res", True, True, 30045],

    ["B255_Quality_NumDefects", 0, 1, 30046],
    ["B255_Quality_MinSeparationDistance", None, None, 30047],
    ["B255_Quality_Res", True, True, 30048],

    ['W000_Raw_Blemish_Info_X', None, None, 31000],
    ['W000_Raw_Blemish_Info_Y', None, None, 31001],
    ['W000_Raw_Blemish_Info_Size', None, None, 31002],
    ['W000_Raw_Blemish_Info_Pixel', None, None, 31003],
    ['W000_Raw_Blemish_Info_Contrast', None, None, 31004],

    ['W255_Raw_Blemish_Info_X', None, None, 32000],
    ['W255_Raw_Blemish_Info_Y', None, None, 32001],
    ['W255_Raw_Blemish_Info_Size', None, None, 32002],
    ['W255_Raw_Blemish_Info_Pixel', None, None, 32003],
    ['W255_Raw_Blemish_Info_Contrast', None, None, 32004],

    ['R255_Raw_Blemish_Info_X', None, None, 33000],
    ['R255_Raw_Blemish_Info_Y', None, None, 33001],
    ['R255_Raw_Blemish_Info_Size', None, None, 33002],
    ['R255_Raw_Blemish_Info_Pixel', None, None, 33003],
    ['R255_Raw_Blemish_Info_Contrast', None, None, 33004],

    ['G255_Raw_Blemish_Info_X', None, None, 34000],
    ['G255_Raw_Blemish_Info_Y', None, None, 34001],
    ['G255_Raw_Blemish_Info_Size', None, None, 34002],
    ['G255_Raw_Blemish_Info_Pixel', None, None, 34003],
    ['G255_Raw_Blemish_Info_Contrast', None, None, 34004],

    ['B255_Raw_Blemish_Info_X', None, None, 35000],
    ['B255_Raw_Blemish_Info_Y', None, None, 35001],
    ['B255_Raw_Blemish_Info_Size', None, None, 35002],
    ['B255_Raw_Blemish_Info_Pixel', None, None, 35003],
    ['B255_Raw_Blemish_Info_Contrast', None, None, 35004],

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

    ['W255_P1_Lv', 400, 600, 41000],
    ['W255_P2_Lv', None, None, 41001],
    ['W255_P3_Lv', None, None, 41002],
    ['W255_P4_Lv', None, None, 41003],
    ['W255_P5_Lv', None, None, 41004],
    ['W255_P6_Lv', None, None, 41005],
    ['W255_P7_Lv', None, None, 41006],
    ['W255_P8_Lv', None, None, 41007],
    ['W255_P9_Lv', None, None, 41008],
    ['W255_Lv_max_variation', 0, 0.20, 41009],

    ['W255_P1_duv', 0, 0.01, 41010],
    ['W255_P2_duv', 0, 0.01, 41011],
    ['W255_P3_duv', 0, 0.01, 41012],
    ['W255_P4_duv', 0, 0.01, 41013],
    ['W255_P5_duv', 0, 0.01, 41014],
    ['W255_P6_duv', 0, 0.01, 41015],
    ['W255_P7_duv', 0, 0.01, 41016],
    ['W255_P8_duv', 0, 0.01, 41017],
    ['W255_P9_duv', 0, 0.01, 41018],
    ['W255_duv_max', 0, 0.01, 41019],

    ['W255_P1_P2_duv', None, None, 41020],
    ['W255_P1_P3_duv', None, None, 41021],
    ['W255_P1_P4_duv', None, None, 41022],
    ['W255_P1_P5_duv', None, None, 41023],
    ['W255_P1_P6_duv', None, None, 41024],
    ['W255_P1_P7_duv', None, None, 41025],
    ['W255_P1_P8_duv', None, None, 41026],
    ['W255_P1_P9_duv', None, None, 41027],
    ['W255_P1_neighbor_duv_max', 0, 0.05, 41028],

    ['W255_P2_P3_duv', None, None, 41029],
    ['W255_P2_P1_duv', None, None, 41030],
    ['W255_P2_P9_duv', None, None, 41031],
    ['W255_P2_neighbor_duv_max', 0, 0.05, 41032],

    ['W255_P3_P2_duv', None, None, 41033],
    ['W255_P3_P1_duv', None, None, 41034],
    ['W255_P3_P4_duv', None, None, 41035],
    ['W255_P3_neighbor_duv_max', 0, 0.05, 41036],

    ['W255_P4_P3_duv', None, None, 41037],
    ['W255_P4_P1_duv', None, None, 41038],
    ['W255_P4_P5_duv', None, None, 41039],
    ['W255_P4_neighbor_duv_max', 0, 0.05, 41040],

    ['W255_P5_P4_duv', None, None, 41041],
    ['W255_P5_P1_duv', None, None, 41042],
    ['W255_P5_P6_duv', None, None, 41043],
    ['W255_P5_neighbor_duv_max', 0, 0.05, 41044],

    ['W255_P6_P5_duv', None, None, 41045],
    ['W255_P6_P1_duv', None, None, 41046],
    ['W255_P6_P7_duv', None, None, 41047],
    ['W255_P6_neighbor_duv_max', 0, 0.05, 41048],

    ['W255_P7_P6_duv', None, None, 41049],
    ['W255_P7_P1_duv', None, None, 41050],
    ['W255_P7_P8_duv', None, None, 41051],
    ['W255_P7_neighbor_duv_max', 0, 0.05, 41052],

    ['W255_P8_P7_duv', None, None, 41053],
    ['W255_P8_P1_duv', None, None, 41054],
    ['W255_P8_P9_duv', None, None, 41055],
    ['W255_P8_neighbor_duv_max', 0, 0.05, 41056],

    ['W255_P9_P8_duv', None, None, 41057],
    ['W255_P9_P1_duv', None, None, 41058],
    ['W255_P9_P2_duv', None, None, 41059],
    ['W255_P9_neighbor_duv_max', 0, 0.05, 41060],
]

global STATION_LIMITS
STATION_LIMITS = []
# turn the above array of arrays into
# a dictionary of arrays for ease of typing
for station_limit in STATION_LIMITS_ARRAYS:
    STATION_LIMITS.append(dict(zip(['name', 'low_limit', 'high_limit', 'unique_id'], station_limit)))
