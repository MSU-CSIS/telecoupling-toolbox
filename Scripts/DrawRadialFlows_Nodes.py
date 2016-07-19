# Import all necessary module dependencies
import arcpy
import os
import sys

arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3857)

def DrawRadialFlows_Nodes():

    # Get the value of the input parameter
    inTable = arcpy.GetParameterAsText(0)
    startX_field = arcpy.GetParameterAsText(1)
    startY_field = arcpy.GetParameterAsText(2)
    endX_field = arcpy.GetParameterAsText(3)
    endY_field = arcpy.GetParameterAsText(4)
    flowAmnt_field = arcpy.GetParameterAsText(5)
    lineType_str = arcpy.GetParameterAsText(6)
    SpRef = arcpy.GetParameterAsText(7)

    if inTable and inTable != "#":

        try:
            # create empty list to append all output layers
            outList = []

            # XY To Line
            flowsOutputFC = os.path.join(arcpy.env.scratchGDB, "FlowLines")
            arcpy.SetProgressorLabel('Creating Radial Flow Lines ...')
            if flowAmnt_field and flowAmnt_field != "#":
                arcpy.XYToLine_management(in_table=inTable, out_featureclass=flowsOutputFC,
                                          startx_field=startX_field, starty_field=startY_field,
                                          endx_field=endX_field, endy_field=endY_field,
                                          line_type=lineType_str, id_field=flowAmnt_field, spatial_reference=SpRef)
            else:
                arcpy.XYToLine_management(in_table=inTable, out_featureclass=flowsOutputFC,
                                          startx_field=startX_field, starty_field=startY_field,
                                          endx_field=endX_field, endy_field=endY_field,
                                          line_type=lineType_str, spatial_reference=SpRef)
            outList.append(flowsOutputFC)

            # Make XY Event Layer (temporary)
            nodesOutput = "DestNodes"
            arcpy.SetProgressorLabel('Creating Nodes at Flow Destinations ...')
            arcpy.MakeXYEventLayer_management(table=inTable,
                                              in_x_field=endX_field, in_y_field=endY_field,
                                              out_layer=nodesOutput)

            # Copy XY Event Layer to Feature Class
            nodesOutputFC = os.path.join(arcpy.env.scratchGDB, "DestNodesFC")
            arcpy.CopyFeatures_management(in_features=nodesOutput, out_feature_class=nodesOutputFC)
            outList.append(nodesOutputFC)

            results = ";".join(outList)
            # Send string of (derived) output parameters back to the tool
            arcpy.SetParameterAsText(8, results)

            arcpy.ResetProgressor()

        except Exception:
            e = sys.exc_info()[1]
            arcpy.AddError('An error occurred: {}'.format(e.args[0]))



if __name__ == '__main__':
    DrawRadialFlows_Nodes()