""""
This is a saved model run from natcap.invest.habitat_quality.habitat_quality.
Generated: 08/04/16 11:20:04
InVEST version: 3.3.1
"""

import natcap.invest.habitat_quality.habitat_quality
import arcpy
import SSUtilities as UTILS
import os
import shutil

arcpy.env.overwriteOutput = True
workspace_dir = arcpy.env.scratchFolder

landuse_cur_uri = arcpy.GetParameterAsText(0)
landuse_fut_uri = arcpy.GetParameterAsText(1)
landuse_bas_uri = arcpy.GetParameterAsText(2)
threat_raster_folder = arcpy.GetParameterAsText(3)
threats_uri = arcpy.GetParameterAsText(4)
access_uri = arcpy.GetParameterAsText(5)
sensitivity_uri = arcpy.GetParameterAsText(6)
half_saturation_constant = UTILS.getNumericParameter(7)

outList = []

if not landuse_fut_uri and not landuse_bas_uri:
        args = {
                u'half_saturation_constant': half_saturation_constant,
                u'landuse_cur_uri': landuse_cur_uri,
                u'sensitivity_uri': sensitivity_uri,
                u'threat_raster_folder': threat_raster_folder,
                u'threats_uri': threats_uri,
                u'workspace_dir': workspace_dir,
        }
        if access_uri:
                args[u'access_uri'] = access_uri

        outQuality_cur_rast = os.path.join(arcpy.env.scratchFolder, "output", "quality_out_c.tif")
        outDegSum_cur_rast = os.path.join(arcpy.env.scratchFolder, "output", "deg_sum_out_c.tif")
        outList.append([outQuality_cur_rast, outDegSum_cur_rast])

elif landuse_fut_uri and not landuse_bas_uri:
        args = {
                u'half_saturation_constant': half_saturation_constant,
                u'landuse_fut_uri': landuse_fut_uri,
                u'landuse_cur_uri': landuse_cur_uri,
                u'sensitivity_uri': sensitivity_uri,
                u'threat_raster_folder': threat_raster_folder,
                u'threats_uri': threats_uri,
                u'workspace_dir': workspace_dir,
        }
        if access_uri:
                args[u'access_uri'] = access_uri

        outQuality_cur_rast = os.path.join(arcpy.env.scratchFolder, "output", "quality_out_c.tif")
        outQuality_fut_rast = os.path.join(arcpy.env.scratchFolder, "output", "quality_out_f.tif")
        outDegSum_cur_rast = os.path.join(arcpy.env.scratchFolder, "output", "deg_sum_out_c.tif")
        outDegSum_fut_rast = os.path.join(arcpy.env.scratchFolder, "output", "deg_sum_out_f.tif")
        outList.append([outQuality_cur_rast, outQuality_fut_rast, outDegSum_cur_rast, outDegSum_fut_rast])

elif not landuse_fut_uri and landuse_bas_uri:

        args = {
                u'half_saturation_constant': half_saturation_constant,
                u'landuse_bas_uri': landuse_bas_uri,
                u'landuse_cur_uri': landuse_cur_uri,
                u'sensitivity_uri': sensitivity_uri,
                u'threat_raster_folder': threat_raster_folder,
                u'threats_uri': threats_uri,
                u'workspace_dir': workspace_dir,
        }
        if access_uri:
                args[u'access_uri'] = access_uri

        outQuality_cur_rast = os.path.join(arcpy.env.scratchFolder, "output", "quality_out_c.tif")
        outDegSum_cur_rast = os.path.join(arcpy.env.scratchFolder, "output", "deg_sum_out_c.tif")
        outRarity_cur_rast = os.path.join(arcpy.env.scratchFolder, "output", "rarity_c.tif")
        outList.append([outQuality_cur_rast, outDegSum_cur_rast, outRarity_cur_rast])

else:
        args = {
                u'half_saturation_constant': half_saturation_constant,
                u'landuse_bas_uri': landuse_bas_uri,
                u'landuse_fut_uri': landuse_fut_uri,
                u'landuse_cur_uri': landuse_cur_uri,
                u'sensitivity_uri': sensitivity_uri,
                u'threat_raster_folder': threat_raster_folder,
                u'threats_uri': threats_uri,
                u'workspace_dir': workspace_dir,
        }
        if access_uri:
                args[u'access_uri'] = access_uri
            
        outQuality_cur_rast = os.path.join(arcpy.env.scratchFolder, "output", "quality_out_c.tif")
        outQuality_fut_rast = os.path.join(arcpy.env.scratchFolder, "output", "quality_out_f.tif")
        outDegSum_cur_rast = os.path.join(arcpy.env.scratchFolder, "output", "deg_sum_out_c.tif")
        outDegSum_fut_rast = os.path.join(arcpy.env.scratchFolder, "output", "deg_sum_out_f.tif")
        outRarity_cur_rast = os.path.join(arcpy.env.scratchFolder, "output", "rarity_c.tif")
        outRarity_fut_rast = os.path.join(arcpy.env.scratchFolder, "output", "rarity_f.tif")
        outList.append([outQuality_cur_rast, outQuality_fut_rast, outDegSum_cur_rast, outDegSum_fut_rast, outRarity_cur_rast, outRarity_fut_rast])

if __name__ == '__main__':
    natcap.invest.habitat_quality.habitat_quality.execute(args)
    #remove entire folder and all its content
    shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "intermediate"))
    #### Set Parameters ####
    outList = [l for sublist in outList for l in sublist]
    results = ";".join(outList)
    arcpy.SetParameter(8, results)