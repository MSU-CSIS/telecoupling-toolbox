"""
Use this script to measure the effect of one or more factors (predictors) on visitation rates.
Model Used: InVEST 3.3.x Recreation Model
"""


import arcpy
import SSUtilities as UTILS
import natcap.invest.recreation.recmodel_client
import os
import shutil

arcpy.env.overwriteOutput = True
workspace_dir = arcpy.env.scratchFolder

aoi_path = arcpy.GetParameterAsText(0)
start_year = arcpy.GetParameterAsText(1)
end_year = arcpy.GetParameterAsText(2)
compute_regression = arcpy.GetParameter(3)
predictor_table_path = arcpy.GetParameterAsText(4)
scenario_predictor_table_path = arcpy.GetParameterAsText(5)
grid_aoi = arcpy.GetParameter(6)
grid_type = arcpy.GetParameterAsText(7)
cell_size = UTILS.getNumericParameter(8)

outList_shp = []
outList_tabs = []

if compute_regression and grid_aoi:

    args = {
        u'aoi_path': aoi_path,
        u'start_year': start_year,
        u'end_year': end_year,
        u'compute_regression': compute_regression,
        u'predictor_table_path': predictor_table_path,
        u'scenario_predictor_table_path': scenario_predictor_table_path,
        u'grid_aoi': grid_aoi,
        u'grid_type': grid_type,
        u'cell_size': cell_size,
        u'workspace_dir': workspace_dir,
    }
    out_scenario_shp = os.path.join(arcpy.env.scratchFolder, "scenario_results.shp")
    out_pud_shp = os.path.join(arcpy.env.scratchFolder, "pud_results.shp")
    out_coeff_shp = os.path.join(arcpy.env.scratchFolder, "regression_coefficients.shp")
    outList_shp.append([out_scenario_shp, out_pud_shp, out_coeff_shp])

    out_coeff_txt = os.path.join(arcpy.env.scratchFolder, "regression_coefficients.txt")
    out_monthlyTab_csv = os.path.join(arcpy.env.scratchFolder, "monthly_table.csv")
    outList_tabs.append([out_coeff_txt, out_monthlyTab_csv])

elif compute_regression and not grid_aoi:

    args = {
        u'aoi_path': aoi_path,
        u'start_year': start_year,
        u'end_year': end_year,
        u'compute_regression': compute_regression,
        u'predictor_table_path': predictor_table_path,
        u'scenario_predictor_table_path': scenario_predictor_table_path,
        u'grid_aoi': False,
        u'workspace_dir': workspace_dir,
    }
    out_scenario_shp = os.path.join(arcpy.env.scratchFolder, "scenario_results.shp")
    out_pud_shp = os.path.join(arcpy.env.scratchFolder, "pud_results.shp")
    out_coeff_shp = os.path.join(arcpy.env.scratchFolder, "regression_coefficients.shp")
    outList_shp.append([out_scenario_shp, out_pud_shp, out_coeff_shp])

    out_coeff_txt = os.path.join(arcpy.env.scratchFolder, "regression_coefficients.txt")
    out_monthlyTab_csv = os.path.join(arcpy.env.scratchFolder, "monthly_table.csv")
    outList_tabs.append([out_coeff_txt, out_monthlyTab_csv])

elif not compute_regression and grid_aoi:

    args = {
        u'aoi_path': aoi_path,
        u'start_year': start_year,
        u'end_year': end_year,
        u'compute_regression': False,
        u'grid_aoi': grid_aoi,
        u'grid_type': grid_type,
        u'cell_size': cell_size,
        u'workspace_dir': workspace_dir,
    }
    out_pud_shp = os.path.join(arcpy.env.scratchFolder, "pud_results.shp")
    outList_shp.append(out_pud_shp)
    out_monthlyTab_csv = os.path.join(arcpy.env.scratchFolder, "monthly_table.csv")
    outList_tabs.append(out_monthlyTab_csv)

else:
    args = {
        u'aoi_path': aoi_path,
        u'start_year': start_year,
        u'end_year': end_year,
        u'compute_regression': False,
        u'grid_aoi': False,
        u'workspace_dir': workspace_dir,
    }
    out_pud_shp = os.path.join(arcpy.env.scratchFolder, "pud_results.shp")
    outList_shp.append(out_pud_shp)
    out_monthlyTab_csv = os.path.join(arcpy.env.scratchFolder, "monthly_table.csv")
    outList_tabs.append(out_monthlyTab_csv)

if __name__ == '__main__':
    natcap.invest.recreation.recmodel_client.execute(args)
    #### Set Parameters ####
    outList_shp = [l for sublist in outList_shp for l in sublist]
    results_shp = ";".join(outList_shp)
    outList_tabs = [l for sublist in outList_tabs for l in sublist]
    results_tabs = ";".join(outList_tabs)
    arcpy.SetParameter(9, results_shp)
    arcpy.SetParameter(10, results_tabs)