import arcpy
import sys
import os
import SSUtilities as UTILS
import math

arcpy.env.overwriteOutput = True

def calc_CO2_emissions():

    # Get the value of the input parameter
    inputFC = arcpy.GetParameterAsText(0)  # Polygon or point feature class
    wildlife_units = arcpy.GetParameterAsText(1) # Field from input FC representing number of wildlife units transferred
    capacity_per_trip = UTILS.getNumericParameter(2) # Transportation capacity (wildlife units per trip)
    CO2_emission = UTILS.getNumericParameter(3)  # Amount of CO2 emission (kg/unit)

    try:

        ### ADD FIELD: creating new field to store CO2 total emission per trip ###
        arcpy.AddMessage('Adding CO2 Emission Field to Input Feature Class ...')
        arcpy.SetProgressorLabel('Adding CO2 Emission Field to Input Feature Class ...')

        # add new CO2 emission field
        arcpy.AddField_management(in_table=inputFC, field_name="CO2_EMISSIONS_KG", field_type="LONG")

        ### ADD FIELD: creating new field to store CO2 total emission per trip ###
        arcpy.AddMessage('Calculating CO2 Emissions for Each Flow ...')
        arcpy.SetProgressorLabel('Calculating CO2 Emissions for Each Flow ...')

        with arcpy.da.UpdateCursor(inputFC, ['SHAPE@LENGTH', wildlife_units, 'CO2_EMISSIONS_KG']) as cursor:
            for row in cursor:
                total_trips = math.ceil(float(row[1])/capacity_per_trip)
                #SHAPE@LENGTH will be likely in meters (depending on coordinate system)
                row[2] = row[0] * total_trips * CO2_emission
                cursor.updateRow(row)

        #### Set Parameters ####
        arcpy.SetParameterAsText(4, inputFC)

    except Exception:
        e = sys.exc_info()[1]
        arcpy.AddError('An error occurred: {}'.format(e.args[0]))


if __name__ == '__main__':
    outFC = calc_CO2_emissions()