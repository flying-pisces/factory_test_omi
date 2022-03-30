STATION_LIMITS_ARRAYS = [
    ["SW_VERSION", None, None, 79],
    ["EQUIP_SN", None, None, 80],
    ['SPEC_VERSION', None, None, 81],

    ["Carrier_ProbeConnectStatus", None, None, 82],
    ["DUT_ScreenOnRetries", 0, 5, 83],
    ["DUT_ScreenOnStatus", True, True, 84],
    ["DUT_CancelByOperator", False, False, 85],
    ["DUT_ModuleType", None, None, 86],

    ["Audit_P1", None, float('inf'), 91001],
    ["Audit_P2", None, float('inf'), 91002],
    ["Audit_P4", None, float('inf'), 91003],
    ["Audit_P6", None, float('inf'), 91004],
    ["Audit_P8", None, float('inf'), 91005],

    ["R255_P1", None, float('inf'), 21001],
    ["R255_P2", None, float('inf'), 21002],
    ["R255_P4", None, float('inf'), 21003],
    ["R255_P6", None, float('inf'), 21004],
    ["R255_P8", None, float('inf'), 21005],

    ["G255_P1", None, float('inf'), 31001],
    ["G255_P2", None, float('inf'), 31002],
    ["G255_P4", None, float('inf'), 31003],
    ["G255_P6", None, float('inf'), 31004],
    ["G255_P8", None, float('inf'), 31005],

    ["B255_P1", None, float('inf'), 41001],
    ["B255_P2", None, float('inf'), 41002],
    ["B255_P4", None, float('inf'), 41003],
    ["B255_P6", None, float('inf'), 41004],
    ["B255_P8", None, float('inf'), 41005],

    ["W127_P1", None, float('inf'), 81001],
    ["W127_P2", None, float('inf'), 81002],
    ["W127_P4", None, float('inf'), 81003],
    ["W127_P6", None, float('inf'), 81004],
    ["W127_P8", None, float('inf'), 81005],
]

global STATION_LIMITS
STATION_LIMITS = []
# turn the above array of arrays into
# a dictionary of arrays for ease of typing
for station_limit in STATION_LIMITS_ARRAYS:
    STATION_LIMITS.append(dict(zip(['name', 'low_limit', 'high_limit', 'unique_id'], station_limit)))


if __name__ == '__main__':
    patterns = ['W255']
    position = ['P0', 'P1', 'P2', 'P3', 'P4']

    code_ind = 1000
    for pos_id, pos in enumerate(position):
        for pattern_idx, pattern_name in enumerate(patterns):
            measure_item_name = f'{pattern_name}_{pos}'
            print('["{0}", None, None, {1}],'.format(
                measure_item_name, (pos_id + 2) * 10000 + pattern_idx * 1000 + code_ind))
