import arcpy
import SSUtilities as UTILS
import natcap.invest.forest_carbon_edge_effect
import os
import shutil

arcpy.env.overwriteOutput = True

workspace_dir = arcpy.env.scratchFolder

lulc_uri = arcpy.GetParameterAsText(0)
biophysical_table_uri = arcpy.GetParameterAsText(1)
pools_to_calculate = arcpy.GetParameterAsText(2)
compute_forest_edge_effects = arcpy.GetParameter(3)
tropical_forest_edge_carbon_model_shape_uri = arcpy.GetParameterAsText(4)
n_nearest_model_points = UTILS.getNumericParameter(5)
biomass_to_carbon_conversion_factor = UTILS.getNumericParameter(6)
aoi_uri = arcpy.GetParameterAsText(7)

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

if aoi_uri != "":
    args['aoi_uri'] = aoi_uri


if __name__ == '__main__':
    natcap.invest.forest_carbon_edge_effect.execute(args)
    #remove entire folder and all its content
    shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "intermediate_outputs"))
    #### Set Parameters ####
    outCarbon_rast = os.path.join(arcpy.env.scratchFolder, "carbon_map.tif")
    arcpy.SetParameter(8, outCarbon_rast)
    if aoi_uri != "":
        args['aoi_uri'] = aoi_uri
        outAggrCstock_shp = os.path.join(arcpy.env.scratchFolder, "aggregated_carbon_stocks.shp")
        arcpy.SetParameter(9, outAggrCstock_shp)
