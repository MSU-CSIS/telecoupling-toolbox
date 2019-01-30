# Import all necessary module dependencies
import arcpy
import os
import sys

arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3857)

def UploadSystems():

    # Get the value of the input parameter
    inTable = arcpy.GetParameterAsText(0)
    X_field = arcpy.GetParameterAsText(1)
    Y_field = arcpy.GetParameterAsText(2)
	
    # Local variable:
    gpTempPlace = "in_memory" #"arcpy.env.scratchGDB"
    XY_event_lyr = "SystemsXY"
    out_Name = "Telecoupling Systems"
	
    arcpy.SetProgressorLabel('Creating System Components ...')
    arcpy.AddMessage('Creating System Components ...')

    if inTable or inTable != "#":

        try:

            # Process: Make XY Event Layer (temporary)
            arcpy.MakeXYEventLayer_management(table=inTable,
                                              in_x_field=X_field, in_y_field=Y_field,
                                              out_layer=XY_event_lyr)
            
			# Process: Create temporary copy of XY event layer in memory
            out_layer_temp = os.path.join(gpTempPlace,"SystemsXY_fc")
            arcpy.CopyFeatures_management(XY_event_lyr, out_layer_temp)
			
			# Process: Add XY coordinates using GP environ settings
            arcpy.AddXY_management(out_layer_temp)
			
			# Process: After adding XY to the temporary feature class (in memory or local GDB), create a feature layer 
			#          to send back as output to GP tools
            out_fl = arcpy.MakeFeatureLayer_management(out_layer_temp, out_Name)            

        except Exception:
            e = sys.exc_info()[1]
            arcpy.AddError('An error occurred: {}'.format(e.args[0]))
    else:
        arcpy.AddError('No Features Uploaded to the Map!')

    #### Set Parameters ####
    arcpy.SetParameter(3, out_fl)
    arcpy.ResetProgressor()

if __name__ == '__main__':
    UploadSystems()