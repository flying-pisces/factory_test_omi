
STATION_LIMITS_ARRAYS = [
    ["SW_VERSION", None, None, 79],
    ["EQUIP_VERSION", None, None, 80],
    ['SPEC_VERSION', None, None, 81],

    ["DUT_ModuleType", None, None, 93],
    ["Carrier_ProbeConnectStatus", None, None, 94],
    ["DUT_ScreenOnRetries", 0, 5, 95],
    ["DUT_ScreenOnStatus", True, True, 96],
    ["DUT_CancelByOperator", False, False, 97],
    ["ENV_ParticleCounter", None, None, 98],
    ["ENV_AmbientTemp", None, None, 99],
    ["DUT_AlignmentSuccess", True, True, 100],

    ["Test_RAW_IMAGE_SAVE_SUCCESS_normal_W255", True, True, 10001],
    # ["Test_RAW_IMAGE_SAVE_SUCCESS_normal_R255", True, True, 10002],
    # ["Test_RAW_IMAGE_SAVE_SUCCESS_normal_G255", True, True, 10003],
    # ["Test_RAW_IMAGE_SAVE_SUCCESS_normal_B255", True, True, 10004],
    ["Test_RAW_IMAGE_SAVE_SUCCESS_normal_RGBBoresight", True, True, 10005],
    # ["Test_RAW_IMAGE_SAVE_SUCCESS_normal_GreenDistortion", True, True, 10006],
    ["Test_RAW_IMAGE_SAVE_SUCCESS_normal_WhiteDot", True, True, 10007],
    # ["Test_RAW_IMAGE_SAVE_SUCCESS_normal_PW255", True, True, 10008],

    ["UUT_TEMPERATURE_normal_W255", None, None, 11001],
    # ["UUT_TEMPERATURE_normal_R255", None, None, 11002],
    # ["UUT_TEMPERATURE_normal_G255", None, None, 11003],
    # ["UUT_TEMPERATURE_normal_B255", None, None, 11004],
    ["UUT_TEMPERATURE_normal_RGBBoresight", None, None, 11005],
    # ["UUT_TEMPERATURE_normal_GreenDistortion", None, None, 11006],
    ["UUT_TEMPERATURE_normal_WhiteDot", None, None, 11007],
    # ["UUT_TEMPERATURE_normal_PW255", None, None, 11008],

    # ["UUT_READ_EEP_DATA", True, True, 11009],
    # ["UUT_PW255_WhitePointGLR", None, None, 11010],
    # ["UUT_PW255_WhitePointGLG", None, None, 11011],
    # ["UUT_PW255_WhitePointGLB", None, None, 11012],

    ["normal_W255_ExposureTime_X", None, None, 20000],
    ["normal_W255_ExposureTime_Xz", None, None, 20001],
    ["normal_W255_ExposureTime_Ya", None, None, 20002],
    ["normal_W255_ExposureTime_Yb", None, None, 20003],
    ["normal_W255_ExposureTime_Z", None, None, 20004],
    ["normal_W255_SaturationLevel_X", None, None, 20005],
    ["normal_W255_SaturationLevel_Xz", None, None, 20006],
    ["normal_W255_SaturationLevel_Ya", None, None, 20007],
    ["normal_W255_SaturationLevel_Yb", None, None, 20008],
    ["normal_W255_SaturationLevel_Z", None, None, 20009],
    ["normal_W255_Module Temperature", None, None, 20010],
    ["normal_W255_OnAxis Lum", 85, None, 20011],
    ["normal_W255_OnAxis x", 0.291, 0.351, 20012],
    ["normal_W255_OnAxis y", 0.292, 0.382, 20013],
    ["normal_W255_OnAxis Lum at 47C", None, None, 20014],
    ["normal_W255_OnAxis x at 47C", None, None, 20015],
    ["normal_W255_OnAxis y at 47C", None, None, 20016],
    ["normal_W255_Sky Lum(30deg)", None, None, 20017],
    ["normal_W255_Sky x(30deg)", None, None, 20018],
    ["normal_W255_Sky y(30deg)", None, None, 20019],
    ["normal_W255_Ground Lum(30deg)", None, None, 20020],
    ["normal_W255_Ground x(30deg)", None, None, 20021],
    ["normal_W255_Ground y(30deg)", None, None, 20022],
    ["normal_W255_Nasal Lum(30deg)", None, None, 20023],
    ["normal_W255_Nasal x(30deg)", None, None, 20024],
    ["normal_W255_Nasal y(30deg)", None, None, 20025],
    ["normal_W255_Temporal Lum(30deg)", None, None, 20026],
    ["normal_W255_Temporal x(30deg)", None, None, 20027],
    ["normal_W255_Temporal y(30deg)", None, None, 20028],
    ["normal_W255_Sky_Nasal Lum(30deg)", None, None, 20029],
    ["normal_W255_Sky_Nasal x(30deg)", None, None, 20030],
    ["normal_W255_Sky_Nasal y(30deg)", None, None, 20031],
    ["normal_W255_Sky_Temporal Lum(30deg)", None, None, 20032],
    ["normal_W255_Sky_Temporal x(30deg)", None, None, 20033],
    ["normal_W255_Sky_Temporal y(30deg)", None, None, 20034],
    ["normal_W255_Ground_Nasal Lum(30deg)", None, None, 20035],
    ["normal_W255_Ground_Nasal x(30deg)", None, None, 20036],
    ["normal_W255_Ground_Nasal y(30deg)", None, None, 20037],
    ["normal_W255_Ground_Temporal Lum(30deg)", None, None, 20038],
    ["normal_W255_Ground_Temporal x(30deg)", None, None, 20039],
    ["normal_W255_Ground_Temporal y(30deg)", None, None, 20040],
    ["normal_W255_Max Lum", None, None, 20041],
    ["normal_W255_Max Lum x", None, None, 20042],
    ["normal_W255_Max Lum y", None, None, 20043],
    ["normal_W255_Max Lum x(deg)", None, None, 20044],
    ["normal_W255_Max Lum y(deg)", None, None, 20045],
    ["normal_W255_Lum_mean_30deg", None, None, 20046],
    ["normal_W255_Lum_delta_30deg", None, None, 20047],
    ["normal_W255_Lum 5%30deg", None, None, 20048],
    ["normal_W255_Lum 95%30deg", None, None, 20049],
    ["normal_W255_Lum_Ratio>0.7OnAxisLum_30deg", None, None, 20050],
    ["normal_W255_Lum_Ratio>0.7MaxLum_30deg", 0.7, 1.0, 20051],
    ["normal_W255_u'_mean_30deg", None, None, 20052],
    ["normal_W255_v'_mean_30deg", None, None, 20053],
    ["normal_W255_u'v'_delta_to_OnAxis_30deg", 0, 0.014, 20054],
    ["normal_W255_du'v' 95%30deg", None, None, 20055],

    # ["normal_R255_ExposureTime_X", None, None, 21000],
    # ["normal_R255_ExposureTime_Xz", None, None, 21001],
    # ["normal_R255_ExposureTime_Ya", None, None, 21002],
    # ["normal_R255_ExposureTime_Yb", None, None, 21003],
    # ["normal_R255_ExposureTime_Z", None, None, 21004],
    # ["normal_R255_SaturationLevel_X", None, None, 21005],
    # ["normal_R255_SaturationLevel_Xz", None, None, 21006],
    # ["normal_R255_SaturationLevel_Ya", None, None, 21007],
    # ["normal_R255_SaturationLevel_Yb", None, None, 21008],
    # ["normal_R255_SaturationLevel_Z", None, None, 21009],
    # ["normal_R255_Module Temperature", None, None, 21010],
    # ["normal_R255_OnAxis Lum", 20, 36, 21011],
    # ["normal_R255_OnAxis x", 0.6424, 0.6924, 21012],
    # ["normal_R255_OnAxis y", 0.291, 0.341, 21013],
    # ["normal_R255_OnAxis Lum at 47C", None, None, 21014],
    # ["normal_R255_OnAxis x at 47C", None, None, 21015],
    # ["normal_R255_OnAxis y at 47C", None, None, 21016],
    #
    # ["normal_G255_ExposureTime_X", None, None, 22000],
    # ["normal_G255_ExposureTime_Xz", None, None, 22001],
    # ["normal_G255_ExposureTime_Ya", None, None, 22002],
    # ["normal_G255_ExposureTime_Yb", None, None, 22003],
    # ["normal_G255_ExposureTime_Z", None, None, 22004],
    # ["normal_G255_SaturationLevel_X", None, None, 22005],
    # ["normal_G255_SaturationLevel_Xz", None, None, 22006],
    # ["normal_G255_SaturationLevel_Ya", None, None, 22007],
    # ["normal_G255_SaturationLevel_Yb", None, None, 22008],
    # ["normal_G255_SaturationLevel_Z", None, None, 22009],
    # ["normal_G255_Module Temperature", None, None, 22010],
    # ["normal_G255_OnAxis Lum", 57, 112, 22011],
    # ["normal_G255_OnAxis x", 0.2404, 0.2904, 22012],
    # ["normal_G255_OnAxis y", 0.6286, 0.6786, 22013],
    # ["normal_G255_OnAxis Lum at 47C", None, None, 22014],
    # ["normal_G255_OnAxis x at 47C", None, None, 22015],
    # ["normal_G255_OnAxis y at 47C", None, None, 22016],
    #
    # ["normal_B255_ExposureTime_X", None, None, 23000],
    # ["normal_B255_ExposureTime_Xz", None, None, 23001],
    # ["normal_B255_ExposureTime_Ya", None, None, 23002],
    # ["normal_B255_ExposureTime_Yb", None, None, 23003],
    # ["normal_B255_ExposureTime_Z", None, None, 23004],
    # ["normal_B255_SaturationLevel_X", None, None, 23005],
    # ["normal_B255_SaturationLevel_Xz", None, None, 23006],
    # ["normal_B255_SaturationLevel_Ya", None, None, 23007],
    # ["normal_B255_SaturationLevel_Yb", None, None, 23008],
    # ["normal_B255_SaturationLevel_Z", None, None, 23009],
    # ["normal_B255_Module Temperature", None, None, 23010],
    # ["normal_B255_OnAxis Lum", 4, 8, 23011],
    # ["normal_B255_OnAxis x", 0.1302, 0.1802, 23012],
    # ["normal_B255_OnAxis y", 0.0221, 0.0721, 23013],
    # ["normal_B255_OnAxis Lum at 47C", None, None, 23014],
    # ["normal_B255_OnAxis x at 47C", None, None, 23015],
    # ["normal_B255_OnAxis y at 47C", None, None, 23016],

    ["normal_RGBBoresight_ExposureTime_X", None, None, 24000],
    ["normal_RGBBoresight_ExposureTime_Xz", None, None, 24001],
    ["normal_RGBBoresight_ExposureTime_Ya", None, None, 24002],
    ["normal_RGBBoresight_ExposureTime_Yb", None, None, 24003],
    ["normal_RGBBoresight_ExposureTime_Z", None, None, 24004],
    ["normal_RGBBoresight_SaturationLevel_X", None, None, 24005],
    ["normal_RGBBoresight_SaturationLevel_Xz", None, None, 24006],
    ["normal_RGBBoresight_SaturationLevel_Ya", None, None, 24007],
    ["normal_RGBBoresight_SaturationLevel_Yb", None, None, 24008],
    ["normal_RGBBoresight_SaturationLevel_Z", None, None, 24009],
    ["normal_RGBBoresight_Module Temperature", None, None, 24010],
    ["normal_RGBBoresight_R_Lum", None, None, 24011],
    ["normal_RGBBoresight_R_x", None, None, 24012],
    ["normal_RGBBoresight_R_y", None, None, 24013],
    ["normal_RGBBoresight_R_Lum at 47C", None, None, 24014],
    ["normal_RGBBoresight_R_x at 47C", None, None, 24015],
    ["normal_RGBBoresight_R_y at 47C", None, None, 24016],
    ["normal_RGBBoresight_G_Lum", None, None, 24017],
    ["normal_RGBBoresight_G_x", None, None, 24018],
    ["normal_RGBBoresight_G_y", None, None, 24019],
    ["normal_RGBBoresight_G_Lum at 47C", None, None, 24020],
    ["normal_RGBBoresight_G_x at 47C", None, None, 24021],
    ["normal_RGBBoresight_G_y at 47C", None, None, 24022],
    ["normal_RGBBoresight_B_Lum", None, None, 24023],
    ["normal_RGBBoresight_B_x", None, None, 24024],
    ["normal_RGBBoresight_B_y", None, None, 24025],
    ["normal_RGBBoresight_B_Lum at 47C", None, None, 24026],
    ["normal_RGBBoresight_B_x at 47C", None, None, 24027],
    ["normal_RGBBoresight_B_y at 47C", None, None, 24028],
    ["normal_RGBBoresight_DispCen_x_cono", None, None, 24029],
    ["normal_RGBBoresight_DispCen_y_cono", None, None, 24030],
    ["normal_RGBBoresight_DispCen_x_display", -20, 20, 24031],
    ["normal_RGBBoresight_DispCen_y_display", -20, 20, 24032],
    ["normal_RGBBoresight_Disp_Rotate_x", -1.5, 1.5, 24033],

    ["normal_RGBBoresight_R_Lum_corrected", None, None, 24034],
    ["normal_RGBBoresight_R_x_corrected", 0.642, 0.692, 24035],
    ["normal_RGBBoresight_R_y_corrected", 0.291, 0.341, 24036],
    ["normal_RGBBoresight_G_Lum_corrected", None, None, 24037],
    ["normal_RGBBoresight_G_x_corrected", 0.240, 0.290, 24038],
    ["normal_RGBBoresight_G_y_corrected", 0.629, 0.679, 24039],
    ["normal_RGBBoresight_B_Lum_corrected", None, None, 24040],
    ["normal_RGBBoresight_B_x_corrected", 0.130, 0.180, 24041],
    ["normal_RGBBoresight_B_y_corrected", 0.022, 0.072, 24042],

    # ["normal_GreenDistortion_ExposureTime_X", None, None, 25000],
    # ["normal_GreenDistortion_ExposureTime_Xz", None, None, 25001],
    # ["normal_GreenDistortion_ExposureTime_Ya", None, None, 25002],
    # ["normal_GreenDistortion_ExposureTime_Yb", None, None, 25003],
    # ["normal_GreenDistortion_ExposureTime_Z", None, None, 25004],
    # ["normal_GreenDistortion_SaturationLevel_X", None, None, 25005],
    # ["normal_GreenDistortion_SaturationLevel_Xz", None, None, 25006],
    # ["normal_GreenDistortion_SaturationLevel_Ya", None, None, 25007],
    # ["normal_GreenDistortion_SaturationLevel_Yb", None, None, 25008],
    # ["normal_GreenDistortion_SaturationLevel_Z", None, None, 25009],
    # ["normal_GreenDistortion_Y_Module Temperature", None, None, 25010],
    # ["normal_GreenDistortion_Y_DispCen_x_cono", None, None, 25011],
    # ["normal_GreenDistortion_Y_DispCen_y_cono", None, None, 25012],
    # ["normal_GreenDistortion_Y_DispCen_x_display", None, None, 25013],
    # ["normal_GreenDistortion_Y_DispCen_y_display", None, None, 25014],
    # ["normal_GreenDistortion_Y_Disp_Rotate_x", None, None, 25015],
    # ["normal_GreenDistortion_Y_Disp_Rotate_y", None, None, 25016],

    ["Test_Pattern_normal_WhiteDot", None, None, 26000],
    ["normal_WhiteDot_ExposureTime_X", None, None, 26001],
    ["normal_WhiteDot_ExposureTime_Xz", None, None, 26002],
    ["normal_WhiteDot_ExposureTime_Ya", None, None, 26003],
    ["normal_WhiteDot_ExposureTime_Yb", None, None, 26004],
    ["normal_WhiteDot_ExposureTime_Z", None, None, 26005],
    ["normal_WhiteDot_SaturationLevel_X", None, None, 26006],
    ["normal_WhiteDot_SaturationLevel_Xz", None, None, 26007],
    ["normal_WhiteDot_SaturationLevel_Ya", None, None, 26008],
    ["normal_WhiteDot_SaturationLevel_Yb", None, None, 26009],
    ["normal_WhiteDot_SaturationLevel_Z", None, None, 26010],
    ["normal_WhiteDot_Module Temperature", None, None, 26011],
    ["normal_WhiteDot_Target color x", None, None, 26012],
    ["normal_WhiteDot_Target color y", None, None, 26013],
    ["normal_WhiteDot_WP255 Lum", None, None, 26014],
    ["normal_WhiteDot_WP255 x", None, None, 26015],
    ["normal_WhiteDot_WP255 y", None, None, 26016],
    ["normal_WhiteDot_WP R Quest Algo", None, None, 26017],
    ["normal_WhiteDot_WP G Quest Algo", None, None, 26018],
    ["normal_WhiteDot_WP B Quest Algo", None, None, 26019],
    ["normal_WhiteDot_WP Lum Quest Algo", None, None, 26020],
    ["normal_WhiteDot_WP x  Quest Algo", None, None, 26021],
    ["normal_WhiteDot_WP y  Quest Algo", None, None, 26022],
    ["normal_WhiteDot_WP R Seacliff Algo", None, None, 26023],
    ["normal_WhiteDot_WP G Seacliff Algo", None, None, 26024],
    ["normal_WhiteDot_WP B Seacliff Algo", None, None, 26025],
    ["normal_WhiteDot_WP Lum Seacliff Algo", None, None, 26026],
    ["normal_WhiteDot_WP x Seacliff Algo", None, None, 26027],
    ["normal_WhiteDot_WP y Seacliff Algo", None, None, 26028],
    ["normal_WhiteDot_WP R to DDIC", None, None, 26029],
    ["normal_WhiteDot_WP G to DDIC", None, None, 26030],
    ["normal_WhiteDot_WP B to DDIC", None, None, 26031],

    # ["normal_PW255_ExposureTime_X", None, None, 27000],
    # ["normal_PW255_ExposureTime_Xz", None, None, 27001],
    # ["normal_PW255_ExposureTime_Ya", None, None, 27002],
    # ["normal_PW255_ExposureTime_Yb", None, None, 27003],
    # ["normal_PW255_ExposureTime_Z", None, None, 27004],
    # ["normal_PW255_SaturationLevel_X", None, None, 27005],
    # ["normal_PW255_SaturationLevel_Xz", None, None, 27006],
    # ["normal_PW255_SaturationLevel_Ya", None, None, 27007],
    # ["normal_PW255_SaturationLevel_Yb", None, None, 27008],
    # ["normal_PW255_SaturationLevel_Z", None, None, 27009],
    # ["normal_PW255_Module Temperature", None, None, 27010],
    # ["normal_PW255_OnAxis Lum", 80, None, 27011],
    # ["normal_PW255_OnAxis x", 0.2971, 0.3521, 27012],
    # ["normal_PW255_OnAxis y", 0.3112, 0.3662, 27013],
    # ["normal_PW255_OnAxis Lum at 47C", None, None, 27014],
    # ["normal_PW255_OnAxis x at 47C", None, None, 27015],
    # ["normal_PW255_OnAxis y at 47C", None, None, 27016],
    # ["normal_PW255_Sky Lum(30deg)", None, None, 27017],
    # ["normal_PW255_Sky x(30deg)", None, None, 27018],
    # ["normal_PW255_Sky y(30deg)", None, None, 27019],
    # ["normal_PW255_Ground Lum(30deg)", None, None, 27020],
    # ["normal_PW255_Ground x(30deg)", None, None, 27021],
    # ["normal_PW255_Ground y(30deg)", None, None, 27022],
    # ["normal_PW255_Nasal Lum(30deg)", None, None, 27023],
    # ["normal_PW255_Nasal x(30deg)", None, None, 27024],
    # ["normal_PW255_Nasal y(30deg)", None, None, 27025],
    # ["normal_PW255_Temporal Lum(30deg)", None, None, 27026],
    # ["normal_PW255_Temporal x(30deg)", None, None, 27027],
    # ["normal_PW255_Temporal y(30deg)", None, None, 27028],
    # ["normal_PW255_Sky_Nasal Lum(30deg)", None, None, 27029],
    # ["normal_PW255_Sky_Nasal x(30deg)", None, None, 27030],
    # ["normal_PW255_Sky_Nasal y(30deg)", None, None, 27031],
    # ["normal_PW255_Sky_Temporal Lum(30deg)", None, None, 27032],
    # ["normal_PW255_Sky_Temporal x(30deg)", None, None, 27033],
    # ["normal_PW255_Sky_Temporal y(30deg)", None, None, 27034],
    # ["normal_PW255_Ground_Nasal Lum(30deg)", None, None, 27035],
    # ["normal_PW255_Ground_Nasal x(30deg)", None, None, 27036],
    # ["normal_PW255_Ground_Nasal y(30deg)", None, None, 27037],
    # ["normal_PW255_Ground_Temporal Lum(30deg)", None, None, 27038],
    # ["normal_PW255_Ground_Temporal x(30deg)", None, None, 27039],
    # ["normal_PW255_Ground_Temporal y(30deg)", None, None, 27040],
    # ["normal_PW255_Max Lum", None, None, 27041],
    # ["normal_PW255_Max Lum x", None, None, 27042],
    # ["normal_PW255_Max Lum y", None, None, 27043],
    # ["normal_PW255_Max Lum x(deg)", None, None, 27044],
    # ["normal_PW255_Max Lum y(deg)", None, None, 27045],
    # ["normal_PW255_Lum_mean_30deg", None, None, 27046],
    # ["normal_PW255_Lum_delta_30deg", None, None, 27047],
    # ["normal_PW255_Lum 5%30deg", None, None, 27048],
    # ["normal_PW255_Lum 95%30deg", None, None, 27049],
    # ["normal_PW255_Lum_Ratio>0.7OnAxisLum_30deg", None, None, 27050],
    # ["normal_PW255_Lum_Ratio>0.7MaxLum_30deg", 0.7, 1.0, 27051],
    # ["normal_PW255_u'_mean_30deg", None, None, 27052],
    # ["normal_PW255_v'_mean_30deg", None, None, 27053],
    # ["normal_PW255_u'v'_delta_to_OnAxis_30deg", 0, 0.02, 27054],
    # ["normal_PW255_du'v' 95%30deg", None, None, 27055],

    ["COMPENSATION_DispCen_x_display", None, None, 11013],
    ["COMPENSATION_DispCen_y_display", None, None, 11014],
]

global STATION_LIMITS
STATION_LIMITS = []
# turn the above array of arrays into
# a dictionary of arrays for ease of typing
for station_limit in STATION_LIMITS_ARRAYS:
    STATION_LIMITS.append(dict(zip(['name', 'low_limit', 'high_limit', 'unique_id'], station_limit)))

if __name__ == '__main__':
    TEST_ITEM_POS_DUMMY = [
        {'name': 'normal', 'pos': (0, 0, 15000),
         'pattern': ['W255', 'R255', 'G255', 'B255', 'RGBBoresight', 'GreenDistortion'],
         'condition_A_patterns': [('WhiteDot', 25, ['WhiteDot10', 'WhiteDot11', 'WhiteDot12'])]
         },


        # {'name': 'normal', 'pos': (0, 0, 15000),
        #  'pattern': ['W255', 'G127', 'W000', 'RGB', 'R255', 'G255', 'B255', 'GreenContrast', 'WhiteContrast',
        #              'GreenSharpness', 'GreenDistortion']
        #  },
        # {'name': 'extendedz', 'pos': (0, 0, 27000),
        #  'pattern': ['W255', 'GreenDistortion']
        #  },
        # {'name': 'blemish', 'pos': (0, 0, 5000),
        #  'pattern': ['W255']
        #  },
        # {'name': 'extendedxpos', 'pos': (5071, 0, 16124),
        #  'pattern': ['W255']
        #  },
        # {'name': 'extendedxneg', 'pos': (-5071, 0, 16124),
        #  'pattern': ['W255']
        #  },
        # {'name': 'extendedypos', 'pos': (0, 5071, 16124),
        #  'pattern': ['W255']
        #  },
        # {'name': 'extendedyneg', 'pos': (0, -5071, 16124),
        #  'pattern': ['W255']
        #  },
    ]
    DATA_AT_POLE_AZI = [(-10.0, 0.0), (-20.0, 0.0), (-30.0, 0.0),
                        (0.0, -10.0), (0.0, -20.0), (0.0, -30.0),
                        (0.0, 0.0), (0.0, 10.0), (0.0, 20.0), (0.0, 30.0),
                        (10.0, 0.0), (20.0, 0.0), (30.0, 0.0)]
    DATA_STATUS_DEGS = [10, 20, 30]

    Exposure_Times = ['X', 'Xz', 'Ya', 'Yb', 'Z']

    W255_Items = "Module Temperature,OnAxis Lum,OnAxis x,OnAxis y,OnAixs Lum at 47C,OnAxis x at 47C,OnAxis y at 47C,Sky Lum(30deg),Sky x(30deg),Sky y(30deg),Ground Lum(30deg),Ground x(30deg),Ground y(30deg),Nasal Lum(30deg),Nasal x(30deg),Nasal y(30deg),Temporal Lum(30deg),Temporal x(30deg),Temporal y(30deg),Sky_Nasal Lum(30deg),Sky_Nasal x(30deg),Sky_Nasal y(30deg),Sky_Temporal Lum(30deg),Sky_Temporal x(30deg),Sky_Temporal y(30deg),Ground_Nasal Lum(30deg),Ground_Nasal x(30deg),Ground_Nasal y(30deg),Ground_Temporal Lum(30deg),Ground_Temporal x(30deg),Ground_Temporal y(30deg),Max Lum,Max Lum x,Max Lum y,Max Lum x(deg),Max Lum y(deg),Lum_mean_30deg,Lum_delta_30deg,Lum 5%30deg,Lum 95%30deg,Lum_Ratio>0.7OnAxisLum_30deg,Lum_Ratio>0.7MaxLum_30deg,u'_mean_30deg,v'_mean_30deg,u'v'_delta_to_OnAxis_30deg,du'v' 95%30deg"
    R255_Items = "Module Temperature,OnAxis Lum,OnAxis x,OnAxis y,OnAxis Lum at 47C,OnAxis x at 47C,OnAxis y at 47C"
    G255_Items = "Module Temperature,OnAxis Lum,OnAxis x,OnAxis y,OnAxis Lum at 47C,OnAxis x at 47C,OnAxis y at 47C"
    B255_Items = "Module Temperature,OnAxis Lum,OnAxis x,OnAxis y,OnAxis Lum at 47C,OnAxis x at 47C,OnAxis y at 47C"
    GREENDISTORTION_Items_V3 = "Module Temperature, DispCen_x_cono,DispCen_y_cono,DispCen_x_display,DispCen_y_display,Disp_Rotate_x,Disp_Rotate_y"
    BORESIGHT_Items = "Module Temperature,R_Lum,R_x,R_y,R_Lum at 47C,R_x at 47C,R_y at 47C,G_Lum,G_x,G_y,G_Lum at 47C,G_x at 47C,G_y at 47C,B_Lum,B_x,B_y,B_Lum at 47C,B_x at 47C,B_y at 47C,DispCen_x_cono,DispCen_y_cono,DispCen_x_display,DispCen_y_display,Disp_Rotate_x"
    WHITE_DOT_V3 = "Module Temperature,Target color x,Target color y,WP255 Lum,WP255 x,WP255 y,WP R Quest Alg,WP G Quest Alg,WP B Quest Alg,WP Lum Quest Alg,WP x  Quest Alg,WP y  Quest Alg,WP R Arcata Algorithm,WP G Arcata Algorithm,WP B Arcata Algorithm,WP Lum Arcata Algorithm,WP x Arcata Algorithm,WP y Arcata Algorithm"
    export_items = [('W255', W255_Items), ('R255', R255_Items), ('G255', G255_Items), ('B255', B255_Items),
                    ('RGBBoresight', BORESIGHT_Items), ('GreenDistortion', [f'Y_{c}' for c in GREENDISTORTION_Items_V3.split(',')]),
                    ('WhiteDot', WHITE_DOT_V3)]
    for pos_id, pos_item in enumerate(TEST_ITEM_POS_DUMMY):
        pos_name = pos_item['name']
        item_patterns = pos_item.get('pattern')
        if item_patterns is None:
            continue
        pattern_idx = 0
        for pattern_name in item_patterns:
            code_ind = 0
            for exposure in Exposure_Times:
                measure_item_name = f'{pos_name}_{pattern_name}_ExposureTime_{exposure}'
                print('["{0}", None, None, {1}],'.format(
                    measure_item_name, (pos_id + 2) * 10000 + pattern_idx * 1000 + code_ind))
                code_ind += 1
            for exposure in Exposure_Times:
                measure_item_name = f'{pos_name}_{pattern_name}_SaturationLevel_{exposure}'
                print('["{0}", None, None, {1}],'.format(
                    measure_item_name, (pos_id + 2) * 10000 + pattern_idx * 1000 + code_ind))
                code_ind += 1
            exports = [v for k, v in export_items if k == pattern_name]
            for exp in exports:
                export_item_collection = exp
                if not isinstance(exp, list):
                    export_item_collection = exp.split(",")
                for export_item in export_item_collection:
                    measure_item_name = '{0}_{1}_{2}'.format(pos_name, pattern_name, export_item.lstrip(" "))
                    print('["{0}", None, None, {1}],'.format(
                        measure_item_name, (pos_id + 2) * 10000 + pattern_idx * 1000 + code_ind))
                    code_ind += 1
            pattern_idx += 1
            print('')

        item_patterns = pos_item.get('condition_A_patterns')
        if item_patterns is None:
            continue
        for pattern_grp_name, __, __ in item_patterns:
            code_ind = 0
            print(f'["Test_Pattern_{pos_name}_{pattern_grp_name}", None, None, {(pos_id + 2) * 10000 + pattern_idx * 1000 + code_ind}],')
            code_ind += 1
            for exposure in Exposure_Times:
                measure_item_name = f'{pos_name}_{pattern_grp_name}_ExposureTime_{exposure}'
                print('["{0}", None, None, {1}],'.format(
                    measure_item_name, (pos_id + 2) * 10000 + pattern_idx * 1000 + code_ind))
                code_ind += 1
            for exposure in Exposure_Times:
                measure_item_name = f'{pos_name}_{pattern_grp_name}_SaturationLevel_{exposure}'
                print('["{0}", None, None, {1}],'.format(
                    measure_item_name, (pos_id + 2) * 10000 + pattern_idx * 1000 + code_ind))
                code_ind += 1
            exports = [v for k, v in export_items if k == pattern_grp_name]
            for exp in exports:
                export_item_collection = exp
                if not isinstance(exp, list):
                    export_item_collection = exp.split(",")
                for export_item in export_item_collection:
                    measure_item_name = '{0}_{1}_{2}'.format(pos_name, pattern_grp_name, export_item.lstrip(" "))
                    print('["{0}", None, None, {1}],'.format(
                        measure_item_name, (pos_id + 2) * 10000 + pattern_idx * 1000 + code_ind))
                    code_ind += 1
            pattern_idx += 1
            print('')


