import arcpy
import sys
import os

arcpy.env.overwriteOutput = True

def run_CBA():

    # Get the value of the input parameter
    inputFC = arcpy.GetParameterAsText(0)  #Polygon or point feature class
    inputFC_join_field = arcpy.GetParameterAsText(1) #field in the input feature class used for join
    economics_table = arcpy.GetParameterAsText(2) # CSV file with data on economic costs and revenues
    economics_join_field = arcpy.GetParameterAsText(3)   #field in the economics table used for join with input feature class
    outLyrName = arcpy.GetParameterAsText(4)

    try:

        outCBA_fc = os.path.join(arcpy.env.scratchGDB, outLyrName)
        arcpy.CopyFeatures_management(inputFC, outCBA_fc)

        ### JOIN: only keep common records between input layer and join table ###
        ### ADD FIELD: creating new field to store CO2 total emission per trip ###
        arcpy.AddMessage('Copying Input Feature and Adding New Fields ...')
        arcpy.SetProgressorLabel('Copying Input Feature and Adding New Fields ...')

        # add three new fields ("costs", "revenues", "returns")
        arcpy.AddField_management(outCBA_fc, "COSTS", "DOUBLE")
        arcpy.AddField_management(outCBA_fc, "REVENUES", "DOUBLE")
        arcpy.AddField_management(outCBA_fc, "RETURNS", "DOUBLE")

        # Process: Copy Table to a temporary GDB table (workaround for bug in MakeTableView --ArcGIS 10.3.1)
        ### JOIN: only keep common records between input layer and join table ###
        arcpy.AddMessage('Creating Join Dictionary for Economics Data ...')
        arcpy.SetProgressorLabel('Creating Join Dictionary for Economics Data ...')

        strata_tab = os.path.join(arcpy.env.scratchGDB, "JoinTable")
        arcpy.CopyRows_management(economics_table, strata_tab)

        ### Create list of value fields, leaving out OID field and key/join field ###
        flistObj = arcpy.ListFields(strata_tab)
        flist = [f.name for f in flistObj if f.type != "OID" and f.name != economics_join_field]

        ### Create empty dict object then populate each key with a sub dict by row using value fields as keys ###
        strataDict = {}
        for r in arcpy.SearchCursor(strata_tab):
            fieldvaldict = {}
            for field in flist:
                fieldvaldict[field] = r.getValue(field)

            strataDict[r.getValue(economics_join_field)] = fieldvaldict

        del strata_tab, flistObj

        arcpy.AddMessage('Calculating Returns from Costs and Revenues ...')
        arcpy.SetProgressorLabel('Calculating Returns from Costs and Revenues ...')

        #LOOP through nested dictionaries to check whether any values are missing or n/a
        for k, v in strataDict.iteritems():
            for k2, v2 in strataDict[k].iteritems():
                if v2 is None or v2 == "n/a" or v2 == r"n\a":
                    strataDict[k][k2] = 0.0

        with arcpy.da.UpdateCursor(outCBA_fc, [inputFC_join_field, 'COSTS', 'REVENUES', 'RETURNS'],
                                   where_clause="\"%s\" IS NOT NULL" % inputFC_join_field) as cursor:

            for row in cursor:
                costs = 0.0
                revenues = 0.0
                strata = row[0]
                if not strata in strataDict:
                    arcpy.AddWarning("The attribute \"{}\" was not found in the economics table!".format(strata))
                    continue
                else:
                    cost_lst = [float(v) for k, v in strataDict[strata].iteritems() if 'cost' in k]
                    costs += sum(cost_lst)

                    revenues_lst = [float(v) for k, v in strataDict[strata].iteritems() if 'revenue' in k]
                    revenues += sum(revenues_lst)

                    returns = revenues - costs

                    row[1] = costs
                    row[2] = revenues
                    row[3] = returns

                    cursor.updateRow(row)

        arcpy.AddWarning("Warning: negative monetary values in 'RETURNS' " + \
                         "can be the consequence of missing values in the financial table!!")

        #### Set Parameters ####
        arcpy.SetParameterAsText(5, outCBA_fc)


    except Exception:
        e = sys.exc_info()[1]
        arcpy.AddError('An error occurred: {}'.format(e.args[0]))


if __name__ == '__main__':
    run_CBA()

