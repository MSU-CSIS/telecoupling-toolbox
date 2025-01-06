import arcpy
import natcap.invest.forest_carbon_edge_effect
import os
import shutil
import sys

arcpy.env.overwriteOutput = True
workspace_dir = arcpy.env.scratchFolder

def GetArgs():

    lulc_uri = arcpy.GetParameterAsText(0)
    biophysical_table_uri = arcpy.GetParameterAsText(1)
    pools_to_calculate = arcpy.GetParameterAsText(2)
    compute_forest_edge_effects = arcpy.GetParameter(3)
    tropical_forest_edge_carbon_model_shape_uri = arcpy.GetParameterAsText(4)
    n_nearest_model_points = arcpy.GetParameter(5)
    biomass_to_carbon_conversion_factor = arcpy.GetParameter(6)
    aoi_uri = arcpy.GetParameterAsText(7)

    try:

        if not compute_forest_edge_effects:

            args = {
                u'lulc_uri': lulc_uri,
                u'biophysical_table_uri': biophysical_table_uri,
                u'compute_forest_edge_effects': False,
                u'workspace_dir': workspace_dir,
            }

            if 'all' in pools_to_calculate:
                args[u'pools_to_calculate'] = u'all'
            else:
                args[u'pools_to_calculate'] = u'above_ground'

        #COMPUTE FOREST EDGE EFFECTS
        else:
            args = {
                u'lulc_uri': lulc_uri,
                u'biophysical_table_uri': biophysical_table_uri,
                u'compute_forest_edge_effects': True,
                u'tropical_forest_edge_carbon_model_shape_uri': tropical_forest_edge_carbon_model_shape_uri,
                u'n_nearest_model_points': n_nearest_model_points,
                u'biomass_to_carbon_conversion_factor': biomass_to_carbon_conversion_factor,
                u'workspace_dir': workspace_dir,
            }

            if 'all' in pools_to_calculate:
                args[u'pools_to_calculate'] = u'all'
            else:
                args[u'pools_to_calculate'] = u'above_ground'

        if aoi_uri and aoi_uri != "#":
            args[u'aoi_uri'] = aoi_uri

    except Exception:
        e = sys.exc_info()[1]
        arcpy.AddError('An error occurred: {}'.format(e.args[0]))

    return args


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
    args = GetArgs()
    natcap.invest.forest_carbon_edge_effect.execute(args)
    #remove entire folder and all its content
    shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "intermediate_outputs"))
    outCarbon_rast = os.path.join(arcpy.env.scratchFolder, "carbon_map.tif")
    ##This step is a workaround to correct proj alignment issue in ArcGIS with output from InVEST
    DefineProj(args[u'lulc_uri'], outCarbon_rast)
    #### Set Parameters ####
    arcpy.SetParameter(8, outCarbon_rast)
    if 'aoi_uri' in args:
        outAggrCstock_shp = os.path.join(arcpy.env.scratchFolder, "aggregated_carbon_stocks.shp")
        DefineProj(args[u'lulc_uri'], outAggrCstock_shp)
        arcpy.SetParameter(9, outAggrCstock_shp)
