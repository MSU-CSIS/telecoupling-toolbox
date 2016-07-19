""""
This is a saved model run from natcap.invest.carbon.carbon_combined.
Generated: 07/05/16 15:08:53
InVEST version: 3.3.0
"""

#import arcpy
#import sys
#import SSUtilities as UTILS

#print sys.path
#arcpy.AddMessage(sys.path)

import mylib.natcap.carbon_ALL

'''
arcpy.env.overwriteOutput = True

workspace_dir = arcpy.env.scratchFolder

do_biophysical = arcpy.GetParameter(0)
do_sequestration = arcpy.GetParameter(1)
lulc_cur_uri = arcpy.GetParameterAsText(2)
lulc_cur_year = UTILS.getNumericParameter(3)
lulc_fut_uri = arcpy.GetParameterAsText(4)
lulc_fut_year = UTILS.getNumericParameter(5)
carbon_pools_uri = arcpy.GetParameterAsText(6)
hwp_cur_shape_uri = arcpy.GetParameterAsText(7)
hwp_fut_shape_uri = arcpy.GetParameterAsText(8)
do_uncertainty = arcpy.GetParameter(9)
carbon_pools_uncertain_uri = arcpy.GetParameterAsText(10)
confidence_threshold = UTILS.getNumericParameter(11)
sequest_uri = arcpy.GetParameterAsText(12)
yr_cur = UTILS.getNumericParameter(13)
yr_fut = UTILS.getNumericParameter(14)
do_valuation = arcpy.GetParameter(15)
carbon_price_units = arcpy.GetParameterAsText(16)
V = UTILS.getNumericParameter(17)
c = UTILS.getNumericParameter(18)
r = UTILS.getNumericParameter(19)

#RUN BIOPHYSICAL MODEL...
if do_biophysical:

        #DO NOT USE SEQUESTRATION...
        if not do_sequestration:
                args = {
                        u'carbon_pools_uri': carbon_pools_uri,
                        u'do_biophysical': True,
                        u'do_uncertainty': False,
                        u'do_valuation': False,
                        u'lulc_cur_uri': lulc_cur_uri,
                        u'workspace_dir': workspace_dir,
                }
        #RUN VALUATION MODEL...NEEDS TO RUN SEQUESTRATION!
        elif do_sequestration and do_valuation:
                args = {
                        u'carbon_pools_uri': carbon_pools_uri,
                        u'do_biophysical': True,
                        u'do_uncertainty': False,
                        u'do_valuation': True,
                        u'hwp_cur_shape_uri': hwp_cur_shape_uri,
                        u'hwp_fut_shape_uri': hwp_fut_shape_uri,
                        u'lulc_cur_uri': lulc_cur_uri,
                        u'lulc_cur_year': lulc_cur_year,
                        u'lulc_fut_uri': lulc_fut_uri,
                        u'lulc_fut_year': lulc_fut_year,
                        u'carbon_price_units': carbon_price_units,
                        u'V': V,
                        u'c': c,
                        u'r': r,
                        u'workspace_dir': workspace_dir,
                }
        #RUN SEQUESTRATION...BUT NO VALUATION MODEL
        else:
                args = {
                        u'carbon_pools_uri': carbon_pools_uri,
                        u'do_biophysical': True,
                        u'do_uncertainty': False,
                        u'do_valuation': False,
                        u'hwp_cur_shape_uri': hwp_cur_shape_uri,
                        u'hwp_fut_shape_uri': hwp_fut_shape_uri,
                        u'lulc_cur_uri': lulc_cur_uri,
                        u'lulc_cur_year': lulc_cur_year,
                        u'lulc_fut_uri': lulc_fut_uri,
                        u'lulc_fut_year': lulc_fut_year,
                        u'workspace_dir': workspace_dir,
                }

        #IF ADDING UNCERTAINTY...
        if do_uncertainty:
                args[u'carbon_pools_uncertain_uri'] = carbon_pools_uncertain_uri
                args[u'confidence_threshold'] = confidence_threshold
                args[u'do_uncertainty'] = True
                del args[u'carbon_pools_uri'] #remove unused carbon pool parameter


#RUN WITHOUT BIOPHYSICAL MODEL...SEQUESTRATION INPUT IS REQUIRED!
else:
        #RUN WITHOUT VALUATION...
        if not do_valuation:
                args = {
                        u'do_biophysical': do_biophysical,
                        u'do_valuation': do_valuation,
                        u'sequest_uri': sequest_uri,
                        u'yr_cur': yr_cur,
                        u'yr_fut': yr_fut,
                        u'workspace_dir': workspace_dir,
                }
        #RUN WITH VALUATION...
        else:
                args = {
                        u'do_biophysical': do_biophysical,
                        u'do_valuation': do_valuation,
                        u'sequest_uri': sequest_uri,
                        u'yr_cur': yr_cur,
                        u'yr_fut': yr_fut,
                        u'carbon_price_units': carbon_price_units,
                        u'V': V,
                        u'c': c,
                        u'r': r,
                        u'workspace_dir': workspace_dir,
                }
'''

#if __name__ == '__main__':
    #natcap.invest.carbon.carbon_combined.execute(args)
    #natcap.invest.carbon.carbon_ALL
    #carbon_combined.execute(args)