import arcpy
from bs4 import BeautifulSoup
import sys
import os
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
    f = open(output, 'wb')
    outWriter = csv.writer(f, dialect='excel')

    excludeTypes = ['Geometry', 'OID']
    excludeTypes = []
    fields = ExcludeFields(fc, excludeTypes)

    # Create Search Cursor: the following only works with ArcGIS 10.1+
    with arcpy.da.SearchCursor(fc, fields) as cursor:
        outWriter.writerow(cursor.fields)
        for row in cursor:
            row = [v.decode('utf8') if isinstance(v, str) else v for v in row]
            outWriter.writerow([unicode(s).encode("utf-8") for s in row])
    del row, cursor

    # Close opened file
    f.close()

def AddMediaFlows():

    # Local variable:
    out_layer_src = r"in_memory\source_lyr"
    out_layer_pnt = r"in_memory\country_lyr"
    out_media_flows = r"in_memory\media_lyr"

    # Get the value of the input parameter
    input_fc = arcpy.GetParameterAsText(0)
    input_fc_field = arcpy.GetParameterAsText(1)
    input_html = arcpy.GetParameterAsText(2)
    source_FeatureSet = arcpy.GetParameterAsText(3)
    is_checked_table = arcpy.GetParameter(4)
    input_flow_lyr = arcpy.GetParameterAsText(5)
    lineType_str = arcpy.GetParameterAsText(6)

    try:

        ### 1. Create temp feature layer from source point and add XY coordinates ###
        # Process: Make Feature Layer (temporary)
        arcpy.MakeFeatureLayer_management(in_features=source_FeatureSet, out_layer=out_layer_src)
        #### Add XY Coordinates To Point Layer ####
        arcpy.AddXY_management(out_layer_src)

        ### 2. The user should only add a single source location. If so, then store the XY coordinate values into a list object ###
        countRows = int(arcpy.GetCount_management(out_layer_src).getOutput(0))

        if countRows > 1:
            arcpy.AddError("You need to specify ONLY ONE source location on the map!!")
            raise arcpy.ExecuteError
        else:
            with arcpy.da.SearchCursor(out_layer_src, ['POINT_X', 'POINT_Y']) as cursor:
                for row in cursor:
                    srcPnt_XY = [row[0], row[1]]
            del cursor

        ### 3. Create Dictionary of Values Based on Selected Input Feature Field ###
        fNames_lst = []
        # Search Cursor: the following only works with ArcGIS 10.1+ ###
        arcpy.SetProgressorLabel('Creating Dictionary From Input Feature ...')
        arcpy.AddMessage('Creating Dictionary From Input Feature ...')
        with arcpy.da.SearchCursor(input_fc, input_fc_field) as cursor:
            for row in cursor:
                fNames_lst.append(row[0])
        del cursor

        ### 4. Read HTML input report file and parse its content grabbing desired tags ###
        arcpy.SetProgressorLabel('Reading and Parsing HTML File ...')
        arcpy.AddMessage('Reading and Parsing HTML File ...')
        soup = BeautifulSoup(open(input_html),"lxml")
        links_geo = soup.find_all(lambda tag: tag.name == 'p' and tag.get('class') == ['c1'])
        #links_p = soup.find_all('p')
        text_elements_geo = [links_geo[i].find_all(text=True) for i in range(len(links_geo))]

        ### 5. Initialize a dictionary to store frequency of geographic locations to be mapped: ###
        ### Keys ---> unique values of the selected input feature field;
        ### Values ---> count frequency of word match between parsed HTML string and dictionary key (e.g. country name) ###
        #country_parse = {k: None for k in country_lst}
        country_parse = {}
        for el in text_elements_geo:
            for geo in fNames_lst:
                if len(el) == 1 and geo in el[0]:
                    if not geo in country_parse:
                        country_parse[geo] = 1
                    else:
                        country_parse[geo] += 1
        arcpy.AddMessage('Dictionary Filled With Frequency Counts From Parsed HTML ...')

        ### 6. Create a temporary point layer from the input Polygon feature class ###
        arcpy.SetProgressorLabel('Creating Temporary Point Layer from Input Feature ...')
        arcpy.AddMessage('Creating Temporary Point Layer from Input Feature ...')
        ### Process: Feature To Point Layer ###
        arcpy.FeatureToPoint_management(input_fc, out_layer_pnt, "INSIDE")

        ### 7. Add Fields Required as Input by the XY To Line GP tool ###
        arcpy.SetProgressorLabel('Adding New Field ...')
        arcpy.AddMessage('Adding New Field ...')
        #### Add Fields to temporary feature layer ###
        arcpy.AddField_management(in_table=out_layer_pnt, field_name="FROM_X", field_type="DOUBLE")
        arcpy.AddField_management(in_table=out_layer_pnt, field_name="FROM_Y", field_type="DOUBLE")
        arcpy.AddField_management(in_table=out_layer_pnt, field_name="TO_X", field_type="DOUBLE")
        arcpy.AddField_management(in_table=out_layer_pnt, field_name="TO_Y", field_type="DOUBLE")
        arcpy.AddField_management(in_table=out_layer_pnt, field_name="Frequency", field_type="SHORT")
        #### Add XY Coordinates To Point Layer ####
        arcpy.AddXY_management(out_layer_pnt)

        ### 8. Fill Out Values for All Newly Added Fields in the Temp Point Feature Layer ###
        arcpy.SetProgressorLabel('Transferring Values from Dictionary to Feature Layer ...')
        arcpy.AddMessage('Transferring Values from Dictionary to Feature Layer ...')
        fields_selection = ['FROM_X', 'FROM_Y', input_fc_field, 'TO_X', 'TO_Y', 'POINT_X', 'POINT_Y', 'Frequency']
        with arcpy.da.UpdateCursor(out_layer_pnt, fields_selection) as cursor:
            for row in cursor:
                if row[2] in country_parse.keys():
                    row[0] = srcPnt_XY[0]
                    row[1] = srcPnt_XY[1]
                    row[3] = row[5]
                    row[4] = row[6]
                    row[7] = country_parse[row[2]]
                    # Update the cursor with the updated list
                    cursor.updateRow(row)
                else:
                    cursor.deleteRow()
        del cursor

        ### 9. Remove Unnecessary Fields From the Temp Point Feature Class ###
        fields = arcpy.ListFields(out_layer_pnt)
        keepFields = ['FROM_X', 'FROM_Y', 'TO_X', 'TO_Y', 'Frequency']
        dropFields = [f.name for f in fields if f.name not in keepFields and f.type != 'OID' and f.type != 'Geometry']
        # delete fields
        arcpy.DeleteField_management(out_layer_pnt, dropFields)

        ### 10. Export temp feature class to CSV and use to draw flow lines ###
        arcpy.SetProgressorLabel('Exporting Geographic Location to CSV Table ...')
        arcpy.AddMessage('Exporting Geographic Location to CSV Table ...')
        outTable_CSV = os.path.join(arcpy.env.scratchFolder, "Media_Flows_Table.csv")
        ExportToCSV(fc=out_layer_pnt, output=outTable_CSV)

        ### 11. If Merging Box is Checked, Merge Temp Point Feature Class To Copy of Input Flow Layer ###
        if is_checked_table:
            arcpy.SetProgressorLabel('Creating Media Information Radial Flow Lines ...')
            arcpy.AddMessage('Creating Media Information Radial Flow Lines ...')
            arcpy.XYToLine_management(in_table=outTable_CSV, out_featureclass=out_media_flows,
                                      startx_field='FROM_X', starty_field='FROM_Y',
                                      endx_field='TO_X', endy_field='TO_Y',
                                      line_type=lineType_str, id_field='Frequency',
                                      spatial_reference=out_layer_pnt)
            arcpy.SetProgressorLabel('Merging Media Information Flows With Existing Flow Layer ...')
            arcpy.AddMessage('Merging Media Information Flows With Existing Flow Layer ...')
            out_fc = os.path.join(arcpy.env.scratchGDB, "Merged_Flow_Lines")
            arcpy.Merge_management([out_media_flows, input_flow_lyr], out_fc)

        else:
            arcpy.SetProgressorLabel('Creating Media Information Radial Flow Lines ...')
            arcpy.AddMessage('Creating Media Information Radial Flow Lines ...')
            out_fc = os.path.join(arcpy.env.scratchGDB, "FlowLines")
            arcpy.XYToLine_management(in_table=outTable_CSV, out_featureclass=out_fc,
                                      startx_field='FROM_X', starty_field='FROM_Y',
                                      endx_field='TO_X', endy_field='TO_Y',
                                      line_type=lineType_str, id_field='Frequency',
                                      spatial_reference=out_layer_pnt)

        # Remove CSV Table
        os.remove(os.path.join(arcpy.env.scratchFolder, "Media_Flows_Table.csv"))
        arcpy.SetParameterAsText(7, out_fc)

    except Exception:
        e = sys.exc_info()[1]
        arcpy.AddError('An error occurred: {}'.format(e.args[0]))


if __name__ == '__main__':
    AddMediaFlows()

