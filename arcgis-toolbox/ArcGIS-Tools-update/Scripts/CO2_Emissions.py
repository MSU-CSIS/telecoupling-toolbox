import arcpy
import sys
import os
import math

arcpy.env.overwriteOutput = True

def calc_CO2_emissions():

    # Get the value of the input parameter
    inputFC = arcpy.GetParameterAsText(0)  # Polyline feature class
    wildlife_units = arcpy.GetParameterAsText(1) # Field from input FC representing number of wildlife units transferred
    capacity_per_trip = arcpy.GetParameter(2) # Transportation capacity (wildlife units per trip)
    CO2_emission = arcpy.GetParameter(3)  # Amount of CO2 emission (kg/unit)
    scenarioFC = arcpy.GetParameterAsText(4)  # Scenario: Polyline feature class
    wildlife_units_scn = arcpy.GetParameterAsText(5) # Field from scenario FC representing number of wildlife units transferred
    capacity_per_trip_scn = arcpy.GetParameter(6) # Scenario: Transportation capacity (wildlife units per trip)
    CO2_emission_scn = arcpy.GetParameter(7)  # Scenario: Amount of CO2 emission (kg/unit)

    try:
        # create empty list to append all output layers
        outList = []

        ### ADD FIELD: creating new field to store CO2 total emission per trip ###
        arcpy.AddMessage('Adding CO2 Emission Field to Input Feature Class ...')
        arcpy.SetProgressorLabel('Adding CO2 Emission Field to Input Feature Class ...')

        # add new CO2 emission field
        arcpy.AddField_management(in_table=inputFC, field_name="CO2_EMISSIONS_KG", field_type="LONG")

        ### ADD FIELD: creating new field to store CO2 total emission per trip ###
        arcpy.AddMessage('Calculating CO2 Emissions for Each Flow ...')
        arcpy.SetProgressorLabel('Calculating CO2 Emissions for Each Flow ...')

        tot_emissions = 0
        with arcpy.da.UpdateCursor(inputFC, ['SHAPE@LENGTH', wildlife_units, 'CO2_EMISSIONS_KG']) as cursor:
            for row in cursor:
                total_trips = math.ceil(float(row[1])/capacity_per_trip)
                #SHAPE@LENGTH will be likely in meters (depending on coordinate system)
                row[2] = row[0] * total_trips * CO2_emission
                tot_emissions += row[2]
                cursor.updateRow(row)

        outList.append(inputFC)
        arcpy.AddMessage("The current scenario produces an estimated amount of CO2 equal to: " + str(tot_emissions) + " kilograms")

        if scenarioFC and scenarioFC != "#":
            ### ADD FIELD: creating new field to store CO2 total emission per trip ###
            arcpy.AddMessage('Adding CO2 Emission Field to Scenario Feature Class ...')
            arcpy.SetProgressorLabel('Adding CO2 Emission Field to Scenario Feature Class ...')

            # add new CO2 emission field
            arcpy.AddField_management(in_table=scenarioFC, field_name="CO2_EMISSIONS_KG", field_type="LONG")

            ### ADD FIELD: creating new field to store CO2 total emission per trip ###
            arcpy.AddMessage('Calculating CO2 Emissions for Each Flow in Scenario Feature Class...')
            arcpy.SetProgressorLabel('Calculating CO2 Emissions for Each Flow in Scenario Feature Class...')

            tot_emissions_scn = 0
            with arcpy.da.UpdateCursor(scenarioFC, ['SHAPE@LENGTH', wildlife_units_scn, 'CO2_EMISSIONS_KG']) as cursor:
                for row in cursor:
                    total_trips_scn = math.ceil(float(row[1])/capacity_per_trip_scn)
                    #SHAPE@LENGTH will be likely in meters (depending on coordinate system)
                    row[2] = row[0] * total_trips_scn * CO2_emission_scn
                    tot_emissions_scn += row[2]
                    cursor.updateRow(row)

            outList.append(scenarioFC)
            arcpy.AddMessage("The future scenario produces an estimated amount of CO2 equal to: " + str(tot_emissions_scn) + " kilograms")

            diff_tot_emissions = tot_emissions_scn - tot_emissions
            if diff_tot_emissions > 0:
                arcpy.AddMessage("The future scenario will increase the estimated amount of CO2 by: " + str(tot_emissions) + " kilograms")
            elif diff_tot_emissions < 0:
                arcpy.AddMessage("The future scenario will decrease the estimated amount of CO2 by: " + str(tot_emissions) + " kilograms")
            else:
                arcpy.AddMessage("The future scenario will produce no change in the estimated amount of CO2!")

        #### Set Parameters ####
        results = ";".join(outList)
        arcpy.SetParameterAsText(8, results)

    except Exception:
        e = sys.exc_info()[1]
        arcpy.AddError('An error occurred: {}'.format(e.args[0]))


if __name__ == '__main__':
    outFC = calc_CO2_emissions()