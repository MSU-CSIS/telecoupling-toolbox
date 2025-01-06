""""
This is a saved model run from natcap.invest.habitat_quality.habitat_quality.
Generated: 08/04/16 11:20:04
InVEST version: 3.3.1
"""

import natcap.invest.habitat_quality
import arcpy
import os
import glob
import shutil
import sys
from arcpy.sa import *

arcpy.env.overwriteOutput = True
workspace_dir = arcpy.env.scratchFolder

def isLicensed():
    """Set whether tool is licensed to execute."""
    try:
        if arcpy.CheckExtension("Spatial") == "Available":
            arcpy.CheckOutExtension("Spatial")
        else:
            raise Exception
    except:
        return False
    return True

def GetArgs():

    landuse_cur_uri = arcpy.GetParameterAsText(0)
    landuse_fut_uri = arcpy.GetParameterAsText(1)
    landuse_bas_uri = arcpy.GetParameterAsText(2)
    threat_raster_folder = arcpy.GetParameterAsText(3)
    threats_uri = arcpy.GetParameterAsText(4)
    access_uri = arcpy.GetParameterAsText(5)
    sensitivity_uri = arcpy.GetParameterAsText(6)
    half_saturation_constant = arcpy.GetParameter(7)

    outList = []

    try:

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

    except Exception:
        e = sys.exc_info()[1]
        arcpy.AddError('An error occurred: {}'.format(e.args[0]))

    return args

def ClampRaster(in_raster):

    try:
        inRaster = Raster(in_raster)
        outCon = Con(inRaster >= 0, inRaster, 0)
        outFile = os.path.splitext(in_raster)[0] + "_cl0.tif"
        outCon.save(os.path.join(arcpy.env.scratchFolder, "output", outFile))
        del inRaster, outCon
        os.remove(in_raster)

    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages(2))

    except Exception as ex:
        arcpy.AddError(ex.args[0])


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
    isLicensed()
    args = GetArgs()
    natcap.invest.habitat_quality.execute(args)
    #remove entire folder and all its content
    shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "intermediate"))
    os.chdir(os.path.join(arcpy.env.scratchFolder, "output"))
    for lyr in glob.glob("*.tif"):
        ##This step is a workaround to correct proj alignment issue in ArcGIS with output from InVEST
        DefineProj(args[u'landuse_cur_uri'], lyr)
        if "deg_sum" in lyr or "quality" in lyr:
            ClampRaster(lyr)
    outList = [lyr for lyr in glob.glob(os.path.join(arcpy.env.scratchFolder, "output/*.tif"))]
    results = ";".join(outList)
    #### Set Parameters ####
    arcpy.SetParameter(8, results)
