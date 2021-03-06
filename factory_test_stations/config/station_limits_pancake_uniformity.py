CURRENT_FW_VERSION = 1001

STATION_LIMITS_ARRAYS = [
    ["SW_VERSION", None, None, 95],
    ["MPK_API_Version", 'MPK_API_CS-1.0.12.0', 'MPK_API_CS-1.0.12.0', 96],
    ["DUT_ScreenOnRetries", 0, 5, 97],
    ["DUT_ScreenOnStatus", True, True, 98],
    ["ENV_ParticleCounter", None, None, 99],

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

    ['W255_P1_duv', -1E+12, 0.01, 41010],
    ['W255_P2_duv', -1E+12, 0.01, 41011],
    ['W255_P3_duv', -1E+12, 0.01, 41012],
    ['W255_P4_duv', -1E+12, 0.01, 41013],
    ['W255_P5_duv', -1E+12, 0.01, 41014],
    ['W255_P6_duv', -1E+12, 0.01, 41015],
    ['W255_P7_duv', -1E+12, 0.01, 41016],
    ['W255_P8_duv', -1E+12, 0.01, 41017],
    ['W255_P9_duv', -1E+12, 0.01, 41018],
    ['W255_duv_max', 0, 0.01, 41019],

    ['W255_P1_P2_duv', None, None, 41020],
    ['W255_P1_P3_duv', None, None, 41021],
    ['W255_P1_P4_duv', None, None, 41022],
    ['W255_P1_P5_duv', None, None, 41023],
    ['W255_P1_P6_duv', None, None, 41024],
    ['W255_P1_P7_duv', None, None, 41025],
    ['W255_P1_P8_duv', None, None, 41026],
    ['W255_P1_P9_duv', None, None, 41027],
    ['W255_P1_neighbor_duv_max', -1E+12, 0.05, 41028],

    ['W255_P2_P3_duv', None, None, 41029],
    ['W255_P2_P1_duv', None, None, 41030],
    ['W255_P2_P9_duv', None, None, 41031],
    ['W255_P2_neighbor_duv_max', -1E+12, 0.05, 41032],

    ['W255_P3_P2_duv', None, None, 41033],
    ['W255_P3_P1_duv', None, None, 41034],
    ['W255_P3_P4_duv', None, None, 41035],
    ['W255_P3_neighbor_duv_max', -1E+12, 0.05, 41036],

    ['W255_P4_P3_duv', None, None, 41037],
    ['W255_P4_P1_duv', None, None, 41038],
    ['W255_P4_P5_duv', None, None, 41039],
    ['W255_P4_neighbor_duv_max', -1E+12, 0.05, 41040],

    ['W255_P5_P4_duv', None, None, 41041],
    ['W255_P5_P1_duv', None, None, 41042],
    ['W255_P5_P6_duv', None, None, 41043],
    ['W255_P5_neighbor_duv_max', -1E+12, 0.05, 41044],

    ['W255_P6_P5_duv', None, None, 41045],
    ['W255_P6_P1_duv', None, None, 41046],
    ['W255_P6_P7_duv', None, None, 41047],
    ['W255_P6_neighbor_duv_max', -1E+12, 0.05, 41048],

    ['W255_P7_P6_duv', None, None, 41049],
    ['W255_P7_P1_duv', None, None, 41050],
    ['W255_P7_P8_duv', None, None, 41051],
    ['W255_P7_neighbor_duv_max', -1E+12, 0.05, 41052],

    ['W255_P8_P7_duv', None, None, 41053],
    ['W255_P8_P1_duv', None, None, 41054],
    ['W255_P8_P9_duv', None, None, 41055],
    ['W255_P8_neighbor_duv_max', -1E+12, 0.05, 41056],

    ['W255_P9_P8_duv', None, None, 41057],
    ['W255_P9_P1_duv', None, None, 41058],
    ['W255_P9_P2_duv', None, None, 41059],
    ['W255_P9_neighbor_duv_max', -1E+12, 0.05, 41060],

    ['W127_P1_Lv', None, None, 42000],
    ['W127_P2_Lv', None, None, 42001],
    ['W127_P3_Lv', None, None, 42002],
    ['W127_P4_Lv', None, None, 42003],
    ['W127_P5_Lv', None, None, 42004],
    ['W127_P6_Lv', None, None, 42005],
    ['W127_P7_Lv', None, None, 42006],
    ['W127_P8_Lv', None, None, 42007],
    ['W127_P9_Lv', None, None, 42008],
    ['W127_Lv_max_variation', 0, 0.20, 42009],

    ['W127_P1_duv', -1E+12, 0.01, 42010],
    ['W127_P2_duv', -1E+12, 0.01, 42011],
    ['W127_P3_duv', -1E+12, 0.01, 42012],
    ['W127_P4_duv', -1E+12, 0.01, 42013],
    ['W127_P5_duv', -1E+12, 0.01, 42014],
    ['W127_P6_duv', -1E+12, 0.01, 42015],
    ['W127_P7_duv', -1E+12, 0.01, 42016],
    ['W127_P8_duv', -1E+12, 0.01, 42017],
    ['W127_P9_duv', -1E+12, 0.01, 42018],
    ['W127_duv_max', 0, 0.01, 42019],

    ['W127_P1_P2_duv', None, None, 42020],
    ['W127_P1_P3_duv', None, None, 42021],
    ['W127_P1_P4_duv', None, None, 42022],
    ['W127_P1_P5_duv', None, None, 42023],
    ['W127_P1_P6_duv', None, None, 42024],
    ['W127_P1_P7_duv', None, None, 42025],
    ['W127_P1_P8_duv', None, None, 42026],
    ['W127_P1_P9_duv', None, None, 42027],
    ['W127_P1_neighbor_duv_max', -1E+12, 0.05, 42028],

    ['W127_P2_P3_duv', None, None, 42029],
    ['W127_P2_P1_duv', None, None, 42030],
    ['W127_P2_P9_duv', None, None, 42031],
    ['W127_P2_neighbor_duv_max', -1E+12, 0.05, 42032],

    ['W127_P3_P2_duv', None, None, 42033],
    ['W127_P3_P1_duv', None, None, 42034],
    ['W127_P3_P4_duv', None, None, 42035],
    ['W127_P3_neighbor_duv_max', -1E+12, 0.05, 42036],

    ['W127_P4_P3_duv', None, None, 42037],
    ['W127_P4_P1_duv', None, None, 42038],
    ['W127_P4_P5_duv', None, None, 42039],
    ['W127_P4_neighbor_duv_max', -1E+12, 0.05, 42040],

    ['W127_P5_P4_duv', None, None, 42041],
    ['W127_P5_P1_duv', None, None, 42042],
    ['W127_P5_P6_duv', None, None, 42043],
    ['W127_P5_neighbor_duv_max', -1E+12, 0.05, 42044],

    ['W127_P6_P5_duv', None, None, 42045],
    ['W127_P6_P1_duv', None, None, 42046],
    ['W127_P6_P7_duv', None, None, 42047],
    ['W127_P6_neighbor_duv_max', -1E+12, 0.05, 42048],

    ['W127_P7_P6_duv', None, None, 42049],
    ['W127_P7_P1_duv', None, None, 42050],
    ['W127_P7_P8_duv', None, None, 42051],
    ['W127_P7_neighbor_duv_max', -1E+12, 0.05, 42052],

    ['W127_P8_P7_duv', None, None, 42053],
    ['W127_P8_P1_duv', None, None, 42054],
    ['W127_P8_P9_duv', None, None, 42055],
    ['W127_P8_neighbor_duv_max', -1E+12, 0.05, 42056],

    ['W127_P9_P8_duv', None, None, 42057],
    ['W127_P9_P1_duv', None, None, 42058],
    ['W127_P9_P2_duv', None, None, 42059],
    ['W127_P9_neighbor_duv_max', -1E+12, 0.05, 42060],

    # ['R255_P1_Lv', 400, 600, 43000],
    # ['R255_P2_Lv', None, None, 43001],
    # ['R255_P3_Lv', None, None, 43002],
    # ['R255_P4_Lv', None, None, 43003],
    # ['R255_P5_Lv', None, None, 43004],
    # ['R255_P6_Lv', None, None, 43005],
    # ['R255_P7_Lv', None, None, 43006],
    # ['R255_P8_Lv', None, None, 43007],
    # ['R255_P9_Lv', None, None, 43008],
    # ['R255_Lv_max_variation', 0, 0.20, 43009],

    ['R255_P1_duv', -1E+12, 0.01, 43010],
    ['R255_P2_duv', -1E+12, 0.01, 43011],
    ['R255_P3_duv', -1E+12, 0.01, 43012],
    ['R255_P4_duv', -1E+12, 0.01, 43013],
    ['R255_P5_duv', -1E+12, 0.01, 43014],
    ['R255_P6_duv', -1E+12, 0.01, 43015],
    ['R255_P7_duv', -1E+12, 0.01, 43016],
    ['R255_P8_duv', -1E+12, 0.01, 43017],
    ['R255_P9_duv', -1E+12, 0.01, 43018],
    ['R255_duv_max', 0, 0.01, 43019],

    ['R255_P1_P2_duv', None, None, 43020],
    ['R255_P1_P3_duv', None, None, 43021],
    ['R255_P1_P4_duv', None, None, 43022],
    ['R255_P1_P5_duv', None, None, 43023],
    ['R255_P1_P6_duv', None, None, 43024],
    ['R255_P1_P7_duv', None, None, 43025],
    ['R255_P1_P8_duv', None, None, 43026],
    ['R255_P1_P9_duv', None, None, 43027],
    ['R255_P1_neighbor_duv_max', -1E+12, 0.05, 43028],

    ['R255_P2_P3_duv', None, None, 43029],
    ['R255_P2_P1_duv', None, None, 43030],
    ['R255_P2_P9_duv', None, None, 43031],
    ['R255_P2_neighbor_duv_max', -1E+12, 0.05, 43032],

    ['R255_P3_P2_duv', None, None, 43033],
    ['R255_P3_P1_duv', None, None, 43034],
    ['R255_P3_P4_duv', None, None, 43035],
    ['R255_P3_neighbor_duv_max', -1E+12, 0.05, 43036],

    ['R255_P4_P3_duv', None, None, 43037],
    ['R255_P4_P1_duv', None, None, 43038],
    ['R255_P4_P5_duv', None, None, 43039],
    ['R255_P4_neighbor_duv_max', -1E+12, 0.05, 43040],

    ['R255_P5_P4_duv', None, None, 43041],
    ['R255_P5_P1_duv', None, None, 43042],
    ['R255_P5_P6_duv', None, None, 43043],
    ['R255_P5_neighbor_duv_max', -1E+12, 0.05, 43044],

    ['R255_P6_P5_duv', None, None, 43045],
    ['R255_P6_P1_duv', None, None, 43046],
    ['R255_P6_P7_duv', None, None, 43047],
    ['R255_P6_neighbor_duv_max', -1E+12, 0.05, 43048],

    ['R255_P7_P6_duv', None, None, 43049],
    ['R255_P7_P1_duv', None, None, 43050],
    ['R255_P7_P8_duv', None, None, 43051],
    ['R255_P7_neighbor_duv_max', -1E+12, 0.05, 43052],

    ['R255_P8_P7_duv', None, None, 43053],
    ['R255_P8_P1_duv', None, None, 43054],
    ['R255_P8_P9_duv', None, None, 43055],
    ['R255_P8_neighbor_duv_max', -1E+12, 0.05, 43056],

    ['R255_P9_P8_duv', None, None, 43057],
    ['R255_P9_P1_duv', None, None, 43058],
    ['R255_P9_P2_duv', None, None, 43059],
    ['R255_P9_neighbor_duv_max', -1E+12, 0.05, 43060],

    # ['G255_P1_Lv', 400, 600, 44000],
    # ['G255_P2_Lv', None, None, 44001],
    # ['G255_P3_Lv', None, None, 44002],
    # ['G255_P4_Lv', None, None, 44003],
    # ['G255_P5_Lv', None, None, 44004],
    # ['G255_P6_Lv', None, None, 44005],
    # ['G255_P7_Lv', None, None, 44006],
    # ['G255_P8_Lv', None, None, 44007],
    # ['G255_P9_Lv', None, None, 44008],
    # ['G255_Lv_max_variation', 0, 0.20, 44009],

    ['G255_P1_duv', -1E+12, 0.01, 44010],
    ['G255_P2_duv', -1E+12, 0.01, 44011],
    ['G255_P3_duv', -1E+12, 0.01, 44012],
    ['G255_P4_duv', -1E+12, 0.01, 44013],
    ['G255_P5_duv', -1E+12, 0.01, 44014],
    ['G255_P6_duv', -1E+12, 0.01, 44015],
    ['G255_P7_duv', -1E+12, 0.01, 44016],
    ['G255_P8_duv', -1E+12, 0.01, 44017],
    ['G255_P9_duv', -1E+12, 0.01, 44018],
    ['G255_duv_max', 0, 0.01, 44019],

    ['G255_P1_P2_duv', None, None, 44020],
    ['G255_P1_P3_duv', None, None, 44021],
    ['G255_P1_P4_duv', None, None, 44022],
    ['G255_P1_P5_duv', None, None, 44023],
    ['G255_P1_P6_duv', None, None, 44024],
    ['G255_P1_P7_duv', None, None, 44025],
    ['G255_P1_P8_duv', None, None, 44026],
    ['G255_P1_P9_duv', None, None, 44027],
    ['G255_P1_neighbor_duv_max', -1E+12, 0.05, 44028],

    ['G255_P2_P3_duv', None, None, 44029],
    ['G255_P2_P1_duv', None, None, 44030],
    ['G255_P2_P9_duv', None, None, 44031],
    ['G255_P2_neighbor_duv_max', -1E+12, 0.05, 44032],

    ['G255_P3_P2_duv', None, None, 44033],
    ['G255_P3_P1_duv', None, None, 44034],
    ['G255_P3_P4_duv', None, None, 44035],
    ['G255_P3_neighbor_duv_max', -1E+12, 0.05, 44036],

    ['G255_P4_P3_duv', None, None, 44037],
    ['G255_P4_P1_duv', None, None, 44038],
    ['G255_P4_P5_duv', None, None, 44039],
    ['G255_P4_neighbor_duv_max', -1E+12, 0.05, 44040],

    ['G255_P5_P4_duv', None, None, 44041],
    ['G255_P5_P1_duv', None, None, 44042],
    ['G255_P5_P6_duv', None, None, 44043],
    ['G255_P5_neighbor_duv_max', -1E+12, 0.05, 44044],

    ['G255_P6_P5_duv', None, None, 44045],
    ['G255_P6_P1_duv', None, None, 44046],
    ['G255_P6_P7_duv', None, None, 44047],
    ['G255_P6_neighbor_duv_max', -1E+12, 0.05, 44048],

    ['G255_P7_P6_duv', None, None, 44049],
    ['G255_P7_P1_duv', None, None, 44050],
    ['G255_P7_P8_duv', None, None, 44051],
    ['G255_P7_neighbor_duv_max', -1E+12, 0.05, 44052],

    ['G255_P8_P7_duv', None, None, 44053],
    ['G255_P8_P1_duv', None, None, 44054],
    ['G255_P8_P9_duv', None, None, 44055],
    ['G255_P8_neighbor_duv_max', -1E+12, 0.05, 44056],

    ['G255_P9_P8_duv', None, None, 44057],
    ['G255_P9_P1_duv', None, None, 44058],
    ['G255_P9_P2_duv', None, None, 44059],
    ['G255_P9_neighbor_duv_max', -1E+12, 0.05, 44060],

    # ['B255_P1_Lv', 400, 600, 45000],
    # ['B255_P2_Lv', None, None, 45001],
    # ['B255_P3_Lv', None, None, 45002],
    # ['B255_P4_Lv', None, None, 45003],
    # ['B255_P5_Lv', None, None, 45004],
    # ['B255_P6_Lv', None, None, 45005],
    # ['B255_P7_Lv', None, None, 45006],
    # ['B255_P8_Lv', None, None, 45007],
    # ['B255_P9_Lv', None, None, 45008],
    # ['B255_Lv_max_variation', 0, 0.20, 45009],

    ['B255_P1_duv', -1E+12, 0.01, 45010],
    ['B255_P2_duv', -1E+12, 0.01, 45011],
    ['B255_P3_duv', -1E+12, 0.01, 45012],
    ['B255_P4_duv', -1E+12, 0.01, 45013],
    ['B255_P5_duv', -1E+12, 0.01, 45014],
    ['B255_P6_duv', -1E+12, 0.01, 45015],
    ['B255_P7_duv', -1E+12, 0.01, 45016],
    ['B255_P8_duv', -1E+12, 0.01, 45017],
    ['B255_P9_duv', -1E+12, 0.01, 45018],
    ['B255_duv_max', 0, 0.01, 45019],

    ['B255_P1_P2_duv', None, None, 45020],
    ['B255_P1_P3_duv', None, None, 45021],
    ['B255_P1_P4_duv', None, None, 45022],
    ['B255_P1_P5_duv', None, None, 45023],
    ['B255_P1_P6_duv', None, None, 45024],
    ['B255_P1_P7_duv', None, None, 45025],
    ['B255_P1_P8_duv', None, None, 45026],
    ['B255_P1_P9_duv', None, None, 45027],
    ['B255_P1_neighbor_duv_max', -1E+12, 0.05, 45028],

    ['B255_P2_P3_duv', None, None, 45029],
    ['B255_P2_P1_duv', None, None, 45030],
    ['B255_P2_P9_duv', None, None, 45031],
    ['B255_P2_neighbor_duv_max', -1E+12, 0.05, 45032],

    ['B255_P3_P2_duv', None, None, 45033],
    ['B255_P3_P1_duv', None, None, 45034],
    ['B255_P3_P4_duv', None, None, 45035],
    ['B255_P3_neighbor_duv_max', -1E+12, 0.05, 45036],

    ['B255_P4_P3_duv', None, None, 45037],
    ['B255_P4_P1_duv', None, None, 45038],
    ['B255_P4_P5_duv', None, None, 45039],
    ['B255_P4_neighbor_duv_max', -1E+12, 0.05, 45040],

    ['B255_P5_P4_duv', None, None, 45041],
    ['B255_P5_P1_duv', None, None, 45042],
    ['B255_P5_P6_duv', None, None, 45043],
    ['B255_P5_neighbor_duv_max', -1E+12, 0.05, 45044],

    ['B255_P6_P5_duv', None, None, 45045],
    ['B255_P6_P1_duv', None, None, 45046],
    ['B255_P6_P7_duv', None, None, 45047],
    ['B255_P6_neighbor_duv_max', -1E+12, 0.05, 45048],

    ['B255_P7_P6_duv', None, None, 45049],
    ['B255_P7_P1_duv', None, None, 45050],
    ['B255_P7_P8_duv', None, None, 45051],
    ['B255_P7_neighbor_duv_max', -1E+12, 0.05, 45052],

    ['B255_P8_P7_duv', None, None, 45053],
    ['B255_P8_P1_duv', None, None, 45054],
    ['B255_P8_P9_duv', None, None, 45055],
    ['B255_P8_neighbor_duv_max', -1E+12, 0.05, 45056],

    ['B255_P9_P8_duv', None, None, 45057],
    ['B255_P9_P1_duv', None, None, 45058],
    ['B255_P9_P2_duv', None, None, 45059],
    ['B255_P9_neighbor_duv_max', -1E+12, 0.05, 45060],

    # Avgu/Avgv/CenterLv/AvgLv/LvUniformity
    # ["W255_Avgu",  -1E+12, 1E+12, 101],
    # ["W255_Avgv",  -1E+12, 1E+12, 102],
    # ["W255_CenterLv", 400, 600, 103],
    # ["W255_AvgLv", -1E+12, 1E+12, 104],
    # ["W255_LvUniformity",  -1E+12, 1E+12, 105],
    # ["W255_GlobalContrast",  -1E+12, 1E+12, 106],
    #
    # ["W180_Avgu",  -1E+12, 1E+12, 111],
    # ["W180_Avgv",  -1E+12, 1E+12, 112],
    # ["W180_CenterLv",  -1E+12, 1E+12, 113],
    # ["W180_AvgLv", -1E+12, 1E+12, 114],
    # ["W180_LvUniformity", -1E+12, 1E+12, 115],
    # ["W180_GlobalContrast", -1E+12, 1E+12, 116],
    #
    # ["W127_Avgu",  -1E+12, 1E+12, 121],
    # ["W127_Avgv",  -1E+12, 1E+12, 122],
    # ["W127_CenterLv",  -1E+12, 1E+12, 123],
    # ["W127_AvgLv", -1E+12, 1E+12, 124],
    # ["W127_LvUniformity", -1E+12, 1E+12, 125],
    # ["W127_GlobalContrast", -1E+12, 1E+12, 126],
    #
    # ["W090_Avgu", -1E+12, 1E+12, 131],
    # ["W090_Avgv", -1E+12, 1E+12, 132],
    # ["W090_CenterLv", -1E+12, 1E+12, 133],
    # ["W090_AvgLv", -1E+12, 1E+12, 134],
    # ["W090_LvUniformity", -1E+12, 1E+12, 135],
    # ["W090_GlobalContrast", -1E+12, 1E+12, 136],
    #
    # ["R255_Avgu", -1E+12, 1E+12, 141],
    # ["R255_Avgv", -1E+12, 1E+12, 142],
    # ["R255_CenterLv", -1E+12, 1E+12, 143],
    # ["R255_AvgLv", -1E+12, 1E+12, 144],
    # ["R255_LvUniformity", -1E+12, 1E+12, 145],
    # ["R255_GlobalContrast", -1E+12, 1E+12, 146],
    #
    # ["G255_Avgu", -1E+12, 1E+12, 151],
    # ["G255_Avgv", -1E+12, 1E+12, 152],
    # ["G255_CenterLv", -1E+12, 1E+12, 153],
    # ["G255_AvgLv", -1E+12, 1E+12, 154],
    # ["G255_LvUniformity", -1E+12, 1E+12, 155],
    # ["G255_GlobalContrast", -1E+12, 1E+12, 156],
    #
    # ["B255_Avgu", -1E+12, 1E+12, 161],
    # ["B255_Avgv", -1E+12, 1E+12, 162],
    # ["B255_CenterLv", -1E+12, 1E+12, 163],
    # ["B255_AvgLv", -1E+12, 1E+12, 164],
    # ["B255_LvUniformity", -1E+12, 1E+12, 165],
    # ["B255_GlobalContrast", -1E+12, 1E+12, 166],
    #
    # ["DISPLAY_GAMMA",  -1E+12, 1E+12, 500],
]
global STATION_LIMITS

STATION_LIMITS = []
# turn the above array of arrays into
# a dictionary of arrays for ease of typing
for station_limit in STATION_LIMITS_ARRAYS:
    STATION_LIMITS.append(dict(zip(['name', 'low_limit', 'high_limit', 'unique_id'], station_limit)))
