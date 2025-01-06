""""
This is a saved model run from natcap.invest.ndr.ndr.
Generated: 10/09/17 13:37:20
InVEST version: 3.3.3
"""

import natcap.invest.ndr.ndr


args = {
        u'biophysical_table_path': u'C:\\InVEST_3.3.3_x86\\Base_Data\\Freshwater\\biophysical_table.csv',
        u'calc_n': True,
        u'calc_p': True,
        u'dem_path': u'C:\\InVEST_3.3.3_x86\\Base_Data\\Freshwater\\dem',
        u'k_param': u'2',
        u'lulc_path': u'C:\\InVEST_3.3.3_x86\\Base_Data\\Freshwater\\landuse_90',
        u'runoff_proxy_path': u'C:\\InVEST_3.3.3_x86\\Base_Data\\Freshwater\\precip',
        u'subsurface_critical_length_n': u'150',
        u'subsurface_critical_length_p': u'150',
        u'subsurface_eff_n': u'0.8',
        u'subsurface_eff_p': u'0.8',
        u'threshold_flow_accumulation': u'1000',
        u'watersheds_path': u'C:\\InVEST_3.3.3_x86\\Base_Data\\Freshwater\\watersheds.shp',
        u'workspace_dir': u'C:\\Users\\Paul McCord/Documents/ndr_workspace',
}

if __name__ == '__main__':
    natcap.invest.ndr.ndr.execute(args)
