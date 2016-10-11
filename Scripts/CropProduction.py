import arcpy
import natcap.invest.crop_production.crop_production
import os

arcpy.env.overwriteOutput = True
workspace_dir = arcpy.env.scratchFolder


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

_OUTPUT = {
    'nutrient_contents_table': r'output/nutritional_analysis.csv',
    'financial_analysis_table': r'output/financial_analysis.csv',
    'yield_raster': r'output/yield.tif'
}

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

if __name__ == '__main__':
    natcap.invest.crop_production.crop_production.execute(args)
    #### Set Parameters ####
    out_yield = os.path.join(arcpy.env.scratchFolder, _OUTPUT['yield_raster'])
    arcpy.SetParameter(11, out_yield)
    if compute_financial_analysis or compute_nutritional_contents:
        outList_tabs = [l for sublist in outList_tabs for l in sublist]
        results_tabs = ";".join(outList_tabs)
        arcpy.SetParameter(12, results_tabs)