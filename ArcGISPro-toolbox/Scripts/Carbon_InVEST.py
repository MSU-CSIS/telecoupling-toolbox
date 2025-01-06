""""
This is a saved model run from natcap.invest.carbon.carbon_combined.
Generated: 07/05/16 15:08:53
InVEST version: 3.3.0
"""

import arcpy
import natcap.invest.carbon.carbon_combined
import os
import shutil
import sys

arcpy.env.overwriteOutput = True
workspace_dir = arcpy.env.scratchFolder


def GetArgs():

    do_biophysical = arcpy.GetParameter(0)
    do_sequestration = arcpy.GetParameter(1)
    lulc_cur_uri = arcpy.GetParameterAsText(2)
    lulc_cur_year = arcpy.GetParameter(3)
    lulc_fut_uri = arcpy.GetParameterAsText(4)
    lulc_fut_year = arcpy.GetParameter(5)
    carbon_pools_uri = arcpy.GetParameterAsText(6)
    hwp_cur_shape_uri = arcpy.GetParameterAsText(7)
    hwp_fut_shape_uri = arcpy.GetParameterAsText(8)
    do_uncertainty = arcpy.GetParameter(9)
    carbon_pools_uncertain_uri = arcpy.GetParameterAsText(10)
    confidence_threshold = arcpy.GetParameter(11)
    sequest_uri = arcpy.GetParameterAsText(12)
    yr_cur = arcpy.GetParameter(13)
    yr_fut = arcpy.GetParameter(14)
    do_valuation = arcpy.GetParameter(15)
    carbon_price_units = arcpy.GetParameterAsText(16)
    V = arcpy.GetParameter(17)
    c = arcpy.GetParameter(18)
    r = arcpy.GetParameter(19)

    outList = []

    try:

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
                outCarbon_cur_rast = os.path.join(arcpy.env.scratchFolder, "output", "tot_C_cur.tif")
                outList.append(outCarbon_cur_rast)

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
                outCarbon_cur_rast = os.path.join(arcpy.env.scratchFolder, "output", "tot_C_cur.tif")
                outCarbon_fut_rast = os.path.join(arcpy.env.scratchFolder, "output", "tot_C_fut.tif")
                outCarbon_seq_rast = os.path.join(arcpy.env.scratchFolder, "output", "sequest_fut.tif")
                outCarbon_val_rast = os.path.join(arcpy.env.scratchFolder, "output", "value_seq.tif")
                outList.append(outCarbon_cur_rast)
                outList.append(outCarbon_fut_rast)
                outList.append(outCarbon_seq_rast)
                outList.append(outCarbon_val_rast)

            #RUN SEQUESTRATION...BUT NO VALUATION MODEL
            else:
                args = {
                        u'carbon_pools_uri': carbon_pools_uri,
                        u'do_biophysical': True,
                        u'do_uncertainty': False,
                        u'do_valuation': False,
                        u'lulc_cur_uri': lulc_cur_uri,
                        u'lulc_cur_year': lulc_cur_year,
                        u'lulc_fut_uri': lulc_fut_uri,
                        u'lulc_fut_year': lulc_fut_year,
                        u'workspace_dir': workspace_dir,
                }
                if hwp_cur_shape_uri:
                        args[u'hwp_cur_shape_uri'] = hwp_cur_shape_uri
                        if not hwp_fut_shape_uri:
                                arcpy.AddError("A harvest rate map must be provided for FUTURE scenario!")
                                raise SystemExit()
                        else:
                                args[u'hwp_fut_shape_uri'] = hwp_fut_shape_uri

                outCarbon_cur_rast = os.path.join(arcpy.env.scratchFolder, "output", "tot_C_cur.tif")
                outCarbon_fut_rast = os.path.join(arcpy.env.scratchFolder, "output", "tot_C_fut.tif")
                outCarbon_seq_rast = os.path.join(arcpy.env.scratchFolder, "output", "sequest_fut.tif")
                outList.append(outCarbon_cur_rast)
                outList.append(outCarbon_fut_rast)
                outList.append(outCarbon_seq_rast)

            #IF ADDING UNCERTAINTY...
            if do_uncertainty:
                args[u'carbon_pools_uncertain_uri'] = carbon_pools_uncertain_uri
                args[u'confidence_threshold'] = confidence_threshold
                args[u'do_uncertainty'] = True
                del args[u'carbon_pools_uri'] #remove unused carbon pool parameter
                outCarbon_val_mask_rast = os.path.join(arcpy.env.scratchFolder, "output", "val_mask.tif")
                outCarbon_seq_mask_rast = os.path.join(arcpy.env.scratchFolder, "output", "seq_mask.tif")
                outCarbon_conf_fut_rast = os.path.join(arcpy.env.scratchFolder, "output", "conf_fut.tif")
                outList.append(outCarbon_val_mask_rast)
                outList.append(outCarbon_seq_mask_rast)
                outList.append(outCarbon_conf_fut_rast)

        #RUN WITHOUT BIOPHYSICAL MODEL...SEQUESTRATION INPUT IS REQUIRED!
        else:
            #RUN WITH VALUATION...
            if do_valuation:
                args = {
                    u'do_biophysical': False,
                    u'do_valuation': True,
                    u'sequest_uri': sequest_uri,
                    u'yr_cur': yr_cur,
                    u'yr_fut': yr_fut,
                    u'carbon_price_units': carbon_price_units,
                    u'V': V,
                    u'c': c,
                    u'r': r,
                    u'workspace_dir': workspace_dir,
                }
            outCarbon_val_rast = os.path.join(arcpy.env.scratchFolder, "output", "value_seq.tif")
            outList.append(outCarbon_val_rast)

    except Exception:
        e = sys.exc_info()[1]
        arcpy.AddError('An error occurred: {}'.format(e.args[0]))

    return args, outList


def DefineProj(ref_lyr, out_lyr):

    try:
        # get the coordinate system by describing a feature class
        dsc = arcpy.Describe(ref_lyr)
        coord_sys = dsc.spatialReference
        # run the Define Projection GP tool
        arcpy.DefineProjection_management(out_lyr, coord_sys)

    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages(2))

    except Exception as ex:
        arcpy.AddError(ex.args[0])


if __name__ == '__main__':
    args, outList = GetArgs()
    natcap.invest.carbon.carbon_combined.execute(args)
    #remove entire folder and all its content
    shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "intermediate"))
    #remove file not needed
    os.remove(os.path.join(arcpy.env.scratchFolder, "output\summary.html"))
    for lyr in outList:
        ##This step is a workaround to correct proj alignment issue in ArcGIS with output from InVEST
        if args[u'do_biophysical'] == True:
            DefineProj(args[u'lulc_cur_uri'], lyr)
        else:
            DefineProj(args[u'sequest_uri'], lyr)
    results = ";".join(outList)
    #### Set Parameters ####
    arcpy.SetParameter(20, results)
