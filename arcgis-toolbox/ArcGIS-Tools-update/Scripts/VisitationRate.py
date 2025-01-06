"""
Use this script to measure the effect of one or more factors (predictors) on visitation rates.
Model Used: InVEST 3.3.x Recreation Model
"""


import arcpy
import natcap.invest.recreation.recmodel_client
import os
import sys

arcpy.env.overwriteOutput = True
workspace_dir = arcpy.env.scratchFolder

_OUTPUT = {
    'pud_map': 'pud_results.shp',
    'pud_scenario_map': 'scenario_results.shp',
    'coefficients_map': 'regression_coefficients.shp',
    'coefficients_table': 'regression_coefficients.txt',
    'monthly_pud_table': 'monthly_table.csv'
}

def GetArgs():

    try:
        aoi_path = arcpy.GetParameterAsText(0)
        start_year = arcpy.GetParameterAsText(1)
        end_year = arcpy.GetParameterAsText(2)
        compute_regression = arcpy.GetParameter(3)
        predictor_table_path = arcpy.GetParameterAsText(4)
        scenario_predictor_table_path = arcpy.GetParameterAsText(5)
        grid_aoi = arcpy.GetParameter(6)
        grid_type = arcpy.GetParameterAsText(7)
        cell_size = arcpy.GetParameter(8)

        args = {
            u'aoi_path': aoi_path,
            u'start_year': start_year,
            u'end_year': end_year,
            u'compute_regression': compute_regression,
            u'grid_aoi': grid_aoi,
            u'workspace_dir': workspace_dir,
            u'predictor_table_path': u'',
            u'scenario_predictor_table_path': u'',
        }

        if predictor_table_path and predictor_table_path != '#':
            args[u'predictor_table_path'] = predictor_table_path
            if scenario_predictor_table_path and scenario_predictor_table_path != '#':
                args[u'scenario_predictor_table_path'] = scenario_predictor_table_path

        if grid_aoi:
            args[u'grid_type'] = grid_type
            args[u'cell_size'] = cell_size

    except Exception:
        e = sys.exc_info()[1]
        arcpy.AddError('An error occurred: {}'.format(e.args[0]))

    return args


def path_to_output_files(compute_regression, scenario_predictor_table_path, _OUTPUT, outList_shp, outList_tabs):

    out_pud_shp = os.path.join(arcpy.env.scratchFolder, _OUTPUT['pud_map'])
    outList_shp.append(out_pud_shp)
    out_monthlyTab_csv = os.path.join(arcpy.env.scratchFolder, _OUTPUT['monthly_pud_table'])
    outList_tabs.append(out_monthlyTab_csv)

    if compute_regression:
        out_coeff_shp = os.path.join(arcpy.env.scratchFolder, _OUTPUT['coefficients_map'])
        outList_shp.append(out_coeff_shp)
        out_coeff_txt = os.path.join(arcpy.env.scratchFolder, _OUTPUT['coefficients_table'])
        outList_tabs.append(out_coeff_txt)
        if scenario_predictor_table_path and scenario_predictor_table_path != '':
            out_scenario_shp = os.path.join(arcpy.env.scratchFolder, _OUTPUT['pud_scenario_map'])
            outList_shp.append(out_scenario_shp)

    return outList_shp, outList_tabs


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
    arcpy.AddMessage(args)
    natcap.invest.recreation.recmodel_client.execute(args)
    #### Connect to Output Files ####
    outList_shp, outList_tabs = path_to_output_files(args[u'compute_regression'], args[u'scenario_predictor_table_path'],
                                                     _OUTPUT, outList_shp=[], outList_tabs=[])
    for lyr in outList_shp:
        ##This step is a workaround to correct proj alignment issue in ArcGIS with output from InVEST
        DefineProj(args[u'aoi_path'], lyr)
    results_shp = ";".join(outList_shp)
    results_tabs = ";".join(outList_tabs)
    #### Set Parameters ####
    arcpy.SetParameter(9, results_shp)
    arcpy.SetParameter(10, results_tabs)