# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# AddAgentInteractive.py
# Created on: 2016-06-24 12:05:46.00000
#
# Usage:
# Description:
# ---------------------------------------------------------------------------

# Import all necessary module dependencies
import arcpy
import os
import sys
import csv
import json

arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3857)

def Encode(x):
    """Encodes values into 'utf-8' format"""
    if isinstance(x, unicode):
        return x.encode("utf-8", 'ignore')
    else:
        return str(x)

def ExcludeFields(table, types=[]):
    """Return a list of fields minus those with specified field types"""
    fieldNames = []
    fds = arcpy.ListFields(table)
    for f in fds:
        if f.type not in types:
            fieldNames.append(f.name)
    return fieldNames

def ExportToCSV(fc, output):
    """Export Data to a CSV file"""
    # create the output writer
    outWriter = csv.writer(open(output, 'w'), dialect='excel')

    excludeTypes = ['Geometry', 'OID']
    fields = ExcludeFields(fc, excludeTypes)

    # Create Search Cursor: the following only works with ArcGIS 10.1+
    with arcpy.da.SearchCursor(fc, fields) as cursor:
        outWriter.writerow(cursor.fields)
        for row in cursor:
            row = [v if isinstance(v, str) else v for v in row]
            outWriter.writerow([str(s).encode("utf-8") for s in row])
    del row, cursor

def AddAgents():
    """Draws telecoupling agents on top of basemap interactively or from table"""

    # Local variable:
    out_layer = "Agents_lyr"

    # Get the value of the input parameter
    inFeatureSet = arcpy.GetParameterAsText(0)
    in_RecordSet = arcpy.GetParameter(1)
    isChecked_AddXY = arcpy.GetParameter(2)

    arcpy.SetProgressorLabel('Creating System Components ...')
    arcpy.AddMessage('Creating System Components ...')

    if inFeatureSet or inFeatureSet != "#":
        try:
            # Process: Make Feature Layer (temporary)
            arcpy.MakeFeatureLayer_management(in_features=inFeatureSet, out_layer=out_layer)

            #arcpy.AddField_management(in_table=out_layer, field_name="Name", field_type="TEXT", field_length=50)
            #arcpy.AddField_management(in_table=out_layer, field_name="Text", field_type="TEXT", field_length=100)

            fields = ['Name', 'Text']
            sysTable = in_RecordSet
            

            idx = 0
            tablerowcount = int(arcpy.management.GetCount(in_RecordSet).getOutput(0))
            countRows = int(arcpy.GetCount_management(out_layer).getOutput(0))
            arcpy.AddMessage('HERE..')

            if countRows != tablerowcount:
                arcpy.AddError("Number of records in 'Input Attribute Table' MUST equal number of agents on the map!!")
                raise arcpy.ExecuteError
            else:

                systablefieldsName = [i.name for i in  arcpy.ListFields(sysTable)]
                Name_idx = systablefieldsName.index('Name')
                Text_idx = systablefieldsName.index('Text')
                Name_list = []
                Text_list = []
                with arcpy.da.UpdateCursor(sysTable,systablefieldsName) as syscursor:
                    for row in syscursor:
                        Name_list.append(row[Name_idx])
                        Text_list.append(row[Text_idx])
                del syscursor
                

                              
                with arcpy.da.UpdateCursor(out_layer, fields) as cursor:

  

                    for row in cursor:
                        row[0] = Name_list[idx]
                        row[1] = Text_list[idx]
                        # Update the cursor with the updated list
                        cursor.updateRow(row)
                        idx += 1
                del cursor

            # Process: Copy Feature Class
            outAgents_fc = os.path.join(arcpy.env.scratchGDB, "Agents")
            arcpy.CopyFeatures_management(out_layer, outAgents_fc)

            if isChecked_AddXY:
                arcpy.SetProgressorLabel('Adding XY Coordinates ...')
                arcpy.AddMessage('Adding XY Coordinates ...')
                # Process: Add Coordinates
                arcpy.AddXY_management(outAgents_fc)

            # Process: Delete Unwanted/Unnecessary fields
            arcpy.SetProgressorLabel('Removing Unwanted Fields ...')
            arcpy.AddMessage('Removing Unwanted Fields ...')
            arcpy.DeleteField_management(outAgents_fc, "Id")

            # Process: Export Data to CSV File
            arcpy.SetProgressorLabel('Exporting Feature Class Attributes to CSV ...')
            arcpy.AddMessage('Exporting Feature Class Attributes to CSV ...')
            outTable_CSV = os.path.join(arcpy.env.scratchFolder, "Agents_Table.csv")
            ExportToCSV(fc=outAgents_fc, output=outTable_CSV)

            #### Set Parameters ####
            arcpy.SetParameterAsText(3, outAgents_fc)

        except Exception:
            e = sys.exc_info()[1]
            arcpy.AddError('An error occurred: {}'.format(e.args[0]))
    else:
        arcpy.AddError('No Features Have Been Added to the Map!')


if __name__ == '__main__':
    AddAgents()



