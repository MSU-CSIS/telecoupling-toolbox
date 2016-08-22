import arcpy
import sys
import os
import SSUtilities as UTILS

arcpy.env.overwriteOutput = True

def calc_CO2_emissions():

    # Get the value of the input parameter
    inputFC = arcpy.GetParameterAsText(0)  # Polygon or point feature class
    CO2_emission = UTILS.getNumericParameter(1)  # Amount of CO2 emission (kg/unit)

    try:

        ### ADD FIELD: creating new field to store CO2 total emission per trip ###
        arcpy.AddMessage('Adding CO2 Emission Field to Input Feature Class ...')
        arcpy.SetProgressorLabel('Adding CO2 Emission Field to Input Feature Class ...')

        # add new CO2 emission field
        arcpy.AddField_management(in_table=inputFC, field_name="CO2_EMISSIONS_KG", field_type="DOUBLE", field_scale=2)

        ### ADD FIELD: creating new field to store CO2 total emission per trip ###
        arcpy.AddMessage('Calculating CO2 Emissions for Each Flow ...')
        arcpy.SetProgressorLabel('Calculating CO2 Emissions for Each Flow ...')

        with arcpy.da.UpdateCursor(inputFC, ['SHAPE@LENGTH', 'CO2_EMISSIONS_KG']) as cursor:
            for row in cursor:
                #SHAPE@LENGTH will be likely in meters (depending on coordinate system)
                row[1] = float(row[0] * CO2_emission)
                cursor.updateRow(row)

        #### Set Parameters ####
        arcpy.SetParameterAsText(2, inputFC)

    except Exception:
        e = sys.exc_info()[1]
        arcpy.AddError('An error occurred: {}'.format(e.args[0]))


if __name__ == '__main__':
    outFC = calc_CO2_emissions()