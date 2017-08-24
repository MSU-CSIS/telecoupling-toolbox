# Import all necessary module dependencies
import arcpy
import os
import sys
import json
import csv

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
    outWriter = csv.writer(open(output, 'wb'), dialect='excel')

    excludeTypes = ['Geometry', 'OID']
    fields = ExcludeFields(fc, excludeTypes)

    # Create Search Cursor: the following only works with ArcGIS 10.1+
    with arcpy.da.SearchCursor(fc, fields) as cursor:
        outWriter.writerow(cursor.fields)
        for row in cursor:
            row = [v.decode('utf8') if isinstance(v, str) else v for v in row]
            outWriter.writerow([unicode(s).encode("utf-8") for s in row])
    del cursor

def SelectAddCauses():

    """Draws telecoupling causes on top of basemap interactively"""

    # Local variable:
    out_layer = "Causes_lyr"

    # Get the value of the input parameter
    inFeatureSet = arcpy.GetParameterAsText(0)
    in_RecordSet = arcpy.GetParameter(1)

    arcpy.SetProgressorLabel('Creating Causes Categories ...')
    arcpy.AddMessage('Creating Causes Categories ...')


    if inFeatureSet or inFeatureSet != "#":
        try:
            # Process: Make Feature Layer (temporary)
            arcpy.MakeFeatureLayer_management(in_features=inFeatureSet, out_layer=out_layer)
            arcpy.AddField_management(in_table=out_layer, field_name="DESCRIPTION", field_type="TEXT", field_length=100)

            causeTable = json.loads(in_RecordSet.JSON)

            idx = 0
            countRows = int(arcpy.GetCount_management(out_layer).getOutput(0))

            if countRows != len(causeTable['features']):
                arcpy.AddError("Number of records in 'Input Attribute Table' MUST equal number of causes on the map!!")
                raise arcpy.ExecuteError
            else:
                with arcpy.da.UpdateCursor(out_layer, 'DESCRIPTION') as cursor:
                    for row in cursor:
                        row[0] = causeTable['features'][idx]['attributes']['DESCRIPTION']
                        # Update the cursor with the updated list
                        cursor.updateRow(row)
                        idx += 1
                del cursor

            # Process: Copy Feature Class
            outCauses_fc = os.path.join(arcpy.env.scratchGDB, "Causes")
            arcpy.CopyFeatures_management(out_layer, outCauses_fc)

            # Process: Delete Unwanted/Unnecessary fields
            arcpy.SetProgressorLabel('Removing Unwanted Fields ...')
            arcpy.AddMessage('Removing Unwanted Fields ...')
            arcpy.DeleteField_management(outCauses_fc, "Id")

            # Process: Export Data to CSV File
            arcpy.SetProgressorLabel('Exporting Feature Class Attributes to CSV ...')
            arcpy.AddMessage('Exporting Feature Class Attributes to CSV ...')
            outTable_CSV = os.path.join(arcpy.env.scratchFolder, "Causes_Table.csv")
            ExportToCSV(fc=outCauses_fc, output=outTable_CSV)

            #### Set Parameters ####
            arcpy.SetParameterAsText(2, outCauses_fc)

        except Exception:
            e = sys.exc_info()[1]
            arcpy.AddError('An error occurred: {}'.format(e.args[0]))
    else:
        arcpy.AddError('No Features Have Been Added to the Map!')


if __name__ == '__main__':
    SelectAddCauses()
