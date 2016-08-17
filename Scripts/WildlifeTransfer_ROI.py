import arcpy
import sys
import os

arcpy.env.overwriteOutput = True

def run_CBA():

    # Get the value of the input parameter
    inputFC = arcpy.GetParameterAsText(0)  #Polygon or point feature class
    inputFC_join_field = arcpy.GetParameterAsText(1) #field in the input feature class used for join
    economics_table = arcpy.GetParameterAsText(2) # CSV file with data on economic costs and revenues
    join_field = arcpy.GetParameterAsText(3)   #field in the economics table used for join with input feature class

    try:

        ### JOIN: only keep common records between input layer and join table ###
        arcpy.AddMessage('Joining Economics Data to Input Feature Class ...')
        arcpy.SetProgressorLabel('Joining Economics Data to Input Feature Class ...')

        ### Create a temporary copy of the input feature to manipulate ###
        outFC_temp = os.path.join(arcpy.env.scratchGDB, "outFC_temp")
        arcpy.CopyFeatures_management(inputFC, outFC_temp)

        # add three new fields ("costs", "revenues", "returns")
        arcpy.AddField_management(in_table=outFC_temp, field_name="COSTS", field_type="DOUBLE", field_scale=2)
        arcpy.AddField_management(in_table=outFC_temp, field_name="REVENUES", field_type="DOUBLE", field_scale=2)
        arcpy.AddField_management(in_table=outFC_temp, field_name="RETURNS", field_type="DOUBLE", field_scale=2)

        # Process: Copy Table to a temporary GDB table (workaround for bug in MakeTableView --ArcGIS 10.3.1)
        strata_tab = os.path.join(arcpy.env.scratchGDB, "JoinTable")
        arcpy.CopyRows_management(economics_table, strata_tab)

        #strata_tab = "StrataTbl_temp"
        #arcpy.MakeTableView_management(tempGDBTable, strata_tab)

        ### Create list of value fields, leaving out OID field and key/join field ###
        flistObj = arcpy.ListFields(strata_tab)
        flist = [f.name for f in flistObj if f.type != "OID" and f.name != join_field]

        ### Create empty dict object then populate each key with a sub dict by row using value fields as keys ###
        strataDict = {}
        for r in arcpy.SearchCursor(strata_tab):
            fieldvaldict = {}
            for field in flist:
                fieldvaldict[field] = r.getValue(field)

            strataDict[r.getValue(join_field)] = fieldvaldict

        del strata_tab, flistObj

        arcpy.AddMessage('Calculating Returns from Costs and Revenues ...')
        arcpy.SetProgressorLabel('Calculating Returns from Costs and Revenues ...')

        with arcpy.da.UpdateCursor(outFC_temp, [inputFC_join_field, 'COSTS', 'REVENUES', 'RETURNS'],
                                   where_clause="\"%s\" IS NOT NULL" % inputFC_join_field) as cursor:
            for row in cursor:
                strata = row[0]
                if not strata in strataDict:
                    arcpy.AddWarning("The attribute \"{}\" was not found in the economics table!".format(strata))
                    continue
                else:
                    costs = strataDict[strata]['price_per_unit'] + \
                        strataDict[strata]['price_feed_per_unit'] + \
                        strataDict[strata]['cost_transportation_per_travel'] + \
                        strataDict[strata]['cost_maintenance_per_unit']

                    revenues = strataDict[strata]['revenue_from_tourism'] + \
                               strataDict[strata]['revenue_from_food_prod']

                    returns = revenues - costs

                    row[1] = costs
                    row[2] = revenues
                    row[3] = returns

                    cursor.updateRow(row)

        #### Set Parameters ####
        arcpy.SetParameterAsText(4, outFC_temp)

    except Exception:
        e = sys.exc_info()[1]
        arcpy.AddError('An error occurred: {}'.format(e.args[0]))


if __name__ == '__main__':
    outFC = run_CBA()

