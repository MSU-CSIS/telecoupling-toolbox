# Import all necessary module dependencies
import arcpy, os, sys, shutil, json
import natcap.invest.habitat_risk_assessment.hra_preprocessor

arcpy.env.overwriteOutput = True
workspace_dir = arcpy.env.scratchFolder

def GetArgs(*args):

    try:
        if len(exposure_crits) == 0 or len(sensitivity_crits) == 0 or len(resilience_crits) == 0:
            arcpy.AddError("Choose at least 1 criteria for each category!")
            raise arcpy.ExecuteError

        if (len(exposure_crits) + len(sensitivity_crits) + len(resilience_crits)) < 4:
            arcpy.AddError("Choose at least 4 criteria total between all categories!")
            raise arcpy.ExecuteError

        args = {
                u'stressors_dir': stressors_dir,
                u'exposure_crits': exposure_crits,
                u'sensitivity_crits': sensitivity_crits,
                u'resilience_crits': resilience_crits,
                u'workspace_dir': workspace_dir,
                u'habitats_dir': layer_dir,
                u'species_dir': layer_dir,
        }

    except Exception:
        e = sys.exc_info()[1]
        arcpy.AddError('An error occurred: {}'.format(e.args[0]))

    except arcpy.ExecuteError:
        arcpy.AddError("Choose at least 1 criteria for each category!")

    return args

def json_parser(input_var):

    crits_lst = []
    json_table = json.loads(input_var.JSON)
    for row in json_table['features']:
        crits_lst.append(row['attributes']['CRITERIA_NAME'])

    return crits_lst


if __name__ == '__main__':

    ##Read input par
    layer_dir = arcpy.GetParameterAsText(0)
    stressors_dir = arcpy.GetParameterAsText(1)
    exposure_RecordSet = arcpy.GetParameter(2)
    sensitivity_RecordSet = arcpy.GetParameter(3)
    resilience_RecordSet = arcpy.GetParameter(4)
    do_criteria_bool = arcpy.GetParameter(5)
    criteria_dir = arcpy.GetParameterAsText(6)

    exposure_crits = json_parser(exposure_RecordSet)
    sensitivity_crits = json_parser(sensitivity_RecordSet)
    resilience_crits = json_parser(resilience_RecordSet)

    #create dictionary of args to pass onto the InVEST model execute function
    arcpy.AddMessage("Parsing input parameters...")
    args = GetArgs(layer_dir, stressors_dir, exposure_crits, sensitivity_crits, resilience_crits, do_criteria_bool, criteria_dir, workspace_dir)

    #Run the InVEST model
    arcpy.AddMessage("Running hra_preprocessor model...")
    natcap.invest.habitat_risk_assessment.hra_preprocessor.execute(args)

    #remove entire folder and all its content
    #shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "habitat_stressor_ratings"))

    #return derived parameter(s) to the GUI using the SetParameter() call
    out_ratings_folder = os.path.join(arcpy.env.scratchFolder, "habitat_stressor_ratings")
    arcpy.SetParameterAsText(7, out_ratings_folder)
