import arcpy
from arcpy.sa import *
import natcap.invest.crop_production.crop_production
import os
import sys

arcpy.env.overwriteOutput = True
workspace_dir = arcpy.env.scratchFolder

_OUTPUT = {
    'nutrient_contents_table': r'output\nutritional_analysis.csv',
    'financial_analysis_table': r'output\financial_analysis.csv',
    'yield_raster': r'output\yield.tif',
    'yield_raster_mask': r'output\yield_msk'
}

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

    lookup_table = arcpy.GetParameterAsText(0)
    aoi_raster = arcpy.GetParameterAsText(1)
    dataset_dir = arcpy.GetParameterAsText(2)
    yield_function = arcpy.GetParameterAsText(3)
    percentile_column = arcpy.GetParameterAsText(4)
    fertilizer_dir = arcpy.GetParameterAsText(5)
    irrigation_raster = arcpy.GetParameterAsText(6)
    compute_nutritional_contents = arcpy.GetParameter(7)
    nutrient_table = arcpy.GetParameterAsText(8)
    compute_financial_analysis = arcpy.GetParameter(9)
    economics_table = arcpy.GetParameterAsText(10)

    outList_tabs = []

    try:

        args = {
            u'lookup_table': lookup_table,
            u'aoi_raster': aoi_raster,
            u'dataset_dir': dataset_dir,
            u'yield_function': yield_function,
            u'compute_financial_analysis': False,
            u'compute_nutritional_contents': False,
            u'workspace_dir': workspace_dir,
            u'results_suffix': u'',
        }

        if fertilizer_dir and fertilizer_dir != "#":
            args[u'fertilizer_dir'] = fertilizer_dir

        if yield_function == 'percentile':
            args[u'percentile_column'] = percentile_column
        if yield_function == 'regression':
            if not fertilizer_dir or fertilizer_dir == "#":
                arcpy.AddError("A fertilizer raster folder is required when choosing regression as 'Yield Function'!")
                raise SystemExit()
            args[u'irrigation_raster'] = irrigation_raster

        if compute_financial_analysis:
            args[u'compute_financial_analysis'] = True
            args[u'economics_table'] = economics_table
            out_economic_tab = os.path.join(arcpy.env.scratchFolder, _OUTPUT['financial_analysis_table'])
            outList_tabs.append(out_economic_tab)
        if compute_nutritional_contents:
            args[u'compute_nutritional_contents'] = True
            args[u'nutrient_table'] = nutrient_table
            out_nutr_tab = os.path.join(arcpy.env.scratchFolder, _OUTPUT['nutrient_contents_table'])
            outList_tabs.append(out_nutr_tab)

    except Exception:
        e = sys.exc_info()[1]
        arcpy.AddError('An error occurred: {}'.format(e.args[0]))

    return args, outList_tabs


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

def ExtractMask(in_lyr, msk_lyr, out_lyr):
    inRaster = Raster(in_lyr)
    inMaskData = Raster(msk_lyr)
    # Execute ExtractByMask
    outExtractByMask = ExtractByMask(inRaster, inMaskData)
    # Save the output
    outExtractByMask.save(out_lyr)

if __name__ == '__main__':
    isLicensed()
    args, outList_tabs = GetArgs()
    natcap.invest.crop_production.crop_production.execute(args)
    out_yield = os.path.join(arcpy.env.scratchFolder, _OUTPUT['yield_raster'])
    ##This step is a workaround to correct proj alignment issue in ArcGIS with output from InVEST
    DefineProj(args[u'aoi_raster'], out_yield)
    ##This step is a workaround the fact that yield output from InVEST is not masked to the
    ##input raster area but rather a rectangular frame encompassing the entire extent
    out_yield_msk = os.path.join(arcpy.env.scratchFolder, _OUTPUT['yield_raster_mask'])
    ExtractMask(out_yield, args[u'aoi_raster'], out_yield_msk)
    #remove file not needed
    os.remove(os.path.join(arcpy.env.scratchFolder, _OUTPUT['yield_raster']))
    #### Set Parameters ####
    arcpy.SetParameter(11, out_yield_msk)
    if args[u'compute_financial_analysis'] == True or args[u'compute_nutritional_contents'] == True:
        results_tabs = ";".join(outList_tabs)
        arcpy.SetParameter(12, results_tabs)