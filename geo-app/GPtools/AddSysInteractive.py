# Import all necessary module dependencies
import arcpy
import os
import sys

arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3857)

def AddSystems():

    # Get the value of the input parameter
    inFeatureSet = arcpy.GetParameterAsText(0)
    in_role_attr = arcpy.GetParameterAsText(1)
    in_role_attr = in_role_attr.split(",")
    in_name_attr = arcpy.GetParameterAsText(2)
    in_name_attr = in_name_attr.split(",")
	# Store number of attributes the user typed in the attribute input parameter
    role_attr_len = len(in_role_attr)
    name_attr_len = len(in_name_attr)
    if role_attr_len != name_attr_len:
        arcpy.AddError("The number of role attributes MUST equal number of name attributes!!")
        raise arcpy.ExecuteError
    # Correct potential user input mistakes: remove white spaces and capitalize first letter
    in_role_attr_correct = []
    for role in in_role_attr:
        j = role.replace(" ", "")
        in_role_attr_correct.append(j.capitalize())
    in_name_attr_correct = []
    for name in in_name_attr:
        j = name.replace(" ", "")
        in_name_attr_correct.append(j.capitalize())

    # Local variable:
    gpTempPlace = "in_memory" #"arcpy.env.scratchGDB"
    out_layerXY = "SystemsXY"
    out_Name = "Telecoupling Systems"	

    arcpy.SetProgressorLabel('Creating System Components ...')
    arcpy.AddMessage('Creating System Components ...')

    if inFeatureSet or inFeatureSet != "#":
        
        try:
            # Process: Create a temporary featurel layer from the user input FeatureSet
            arcpy.MakeFeatureLayer_management(in_features=inFeatureSet, out_layer=out_layerXY)
			
			# Process: Add Attribute to feature layer to store names of telecoupling systems
            arcpy.AddField_management(in_table=out_layerXY, field_name="ROLE", field_type="TEXT", field_length=50)
            arcpy.AddField_management(in_table=out_layerXY, field_name="NAME", field_type="TEXT", field_length=50)

            # Store number of rows found in feature layer
            countRows = int(arcpy.GetCount_management(out_layerXY).getOutput(0))
			# If the number of features in the feature layer is not equal to the number of attributes typed in, raise ERROR msg!
            if countRows != role_attr_len:
                arcpy.AddError("The number of role/name attributes MUST equal number of points on the map!!")
                raise arcpy.ExecuteError
            else:
                idx = 0
                with arcpy.da.UpdateCursor(out_layerXY, ['ROLE','NAME']) as cursor:
                    for row in cursor:
                        row[0] = in_role_attr_correct[idx]
                        row[1] = in_name_attr_correct[idx]
                        # Update the cursor with the updated list
                        cursor.updateRow(row)
                        idx += 1
                del cursor

            # Process: Create temporary copy of feature layer in memory
            out_layer_temp = os.path.join(gpTempPlace,"SystemsXY_fc")
            arcpy.CopyFeatures_management(out_layerXY, out_layer_temp)

			#Process: Add XY Coordinates (in web map default WKID:3857) using GP environ settings 
            arcpy.SetProgressorLabel('Adding XY Coordinates ...')
            arcpy.AddMessage('Adding XY Coordinates ...')
	        # Process: Add Coordinates
            arcpy.AddXY_management(out_layer_temp)

			# Process: After adding XY to the temporary feature class (in memory or local GDB), create a feature layer 
			#          to send back as output to GP tools
            out_fl = arcpy.MakeFeatureLayer_management(out_layer_temp, out_Name) 

        except Exception:
            e = sys.exc_info()[1]
            arcpy.AddError('An error occurred: {}'.format(e.args[0]))

    else:
        arcpy.AddError('No Features Have Been Added to the Map!')

    
	#### Set Parameters ####
    arcpy.SetParameter(3, out_fl)

if __name__ == '__main__':
    AddSystems()






