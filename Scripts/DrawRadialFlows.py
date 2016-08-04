# Import all necessary module dependencies
import arcpy
import os
import sys

arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3857)

def DrawRadialFlows():

    # Get the value of the input parameter
    inTable = arcpy.GetParameterAsText(0)
    startX_field = arcpy.GetParameterAsText(1)
    startY_field = arcpy.GetParameterAsText(2)
    endX_field = arcpy.GetParameterAsText(3)
    endY_field = arcpy.GetParameterAsText(4)
    id_field = arcpy.GetParameterAsText(5)
    lineType_str = arcpy.GetParameterAsText(6)
    spRef = arcpy.GetParameterAsText(7)
    joinFields = arcpy.GetParameterAsText(8)
    joinFields = joinFields.split(";")

    if inTable and inTable != "#":

        try:
            # XY To Line
            flowsOutputFC = os.path.join(arcpy.env.scratchGDB, "FlowLines")
            arcpy.AddMessage('Saved Flow Lines to: ' + flowsOutputFC)
            arcpy.SetProgressorLabel('Creating Radial Flow Lines ...')
            if id_field:
                arcpy.XYToLine_management(in_table=inTable, out_featureclass=flowsOutputFC,
                                          startx_field=startX_field, starty_field=startY_field,
                                          endx_field=endX_field, endy_field=endY_field,
                                          line_type=lineType_str, id_field=id_field, spatial_reference=spRef)

                if joinFields[0] != '':
                    ### IF any Join Fields are specified, then Copy Rows first and Join that to the input table ###
                    arcpy.AddMessage('Creating Temporary Join Table ...')
                    arcpy.SetProgressorLabel('Creating Temporary Join Table ...')
                    ### Copy Rows from Input Table to make sure it has an OID ###
                    outTable = r"in_memory\tempTable"
                    arcpy.CopyRows_management(inTable, outTable)

                    ### JOIN ###
                    arcpy.AddMessage('Joining Selected Fields ...')
                    arcpy.SetProgressorLabel('Joining Selected Fields ...')
                    arcpy.JoinField_management(in_data=flowsOutputFC, in_field=id_field,
                                               join_table=outTable, join_field=id_field,
                                               fields=joinFields)
                else:
                    arcpy.AddWarning("WARNING: No join fields have been selected. Only the ID field will be copied to the output feature class!")

            else:
                arcpy.XYToLine_management(in_table=inTable, out_featureclass=flowsOutputFC,
                                          startx_field=startX_field, starty_field=startY_field,
                                          endx_field=endX_field, endy_field=endY_field,
                                          line_type=lineType_str, spatial_reference=spRef)

            # Send string of (derived) output parameters back to the tool
            arcpy.SetParameterAsText(9, flowsOutputFC)
            arcpy.ResetProgressor()

        except Exception:
            e = sys.exc_info()[1]
            arcpy.AddError('An error occurred: {}'.format(e.args[0]))


if __name__ == '__main__':
    DrawRadialFlows()