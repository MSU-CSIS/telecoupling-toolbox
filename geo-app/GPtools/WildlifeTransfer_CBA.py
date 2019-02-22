import arcpy
import sys, zipfile, os

arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3857)

def run_CBA():

    # Get the value of the input parameter
    inputFC = arcpy.GetParameterAsText(0)  #Polygon or point feature class
    inputFC_join_field = arcpy.GetParameterAsText(1) #field in the input feature class used for join
    economics_table = arcpy.GetParameterAsText(2) # CSV file with data on economic costs and revenues
    economics_join_field = arcpy.GetParameterAsText(3)   #field in the economics table used for join with input feature class

    # Local variable:
    outCBA_fc = r"in_memory\SystemsCopy"
    strata_tab = r"in_memory\JoinTable"
    out_Name = "Cost-Benefit Analysis"	

    try:
        ##Check if Input Join Field from Input Feature Layer exists as attribute
        fieldnames_inputFC = [f.name for f in arcpy.ListFields(inputFC)]
        if inputFC_join_field not in fieldnames_inputFC:
            arcpy.AddError("Input Join Field \"%s\" is not an attribute inside the Input Feature Layer!" % inputFC_join_field)
            raise arcpy.ExecuteError
			
        #Create feature class from copy of input feature layer 
        arcpy.AddMessage('Creating Feature Class from Input Feature Layer ...')
        arcpy.SetProgressorLabel('Creating Feature Class from Input Feature Layer ...')
        arcpy.CopyFeatures_management(inputFC, outCBA_fc)

        ### ADD FIELD: creating new field to store CO2 total emission per trip ###
        arcpy.AddMessage('Adding New Fields to Feature Class ...')
        arcpy.SetProgressorLabel('Adding New Fields to Feature Class ...')
        # add three new fields ("costs", "revenues", "returns")
        arcpy.AddField_management(outCBA_fc, "COSTS", "DOUBLE")
        arcpy.AddField_management(outCBA_fc, "REVENUES", "DOUBLE")
        arcpy.AddField_management(outCBA_fc, "RETURNS", "DOUBLE")
		
        # Process: Copy Table to a temporary GDB table (workaround for bug in MakeTableView --ArcGIS 10.3.1)
        ### JOIN: only keep common records between input layer and join table ###
        arcpy.AddMessage('Creating Copy of Table from Input Economic Data ...')
        arcpy.SetProgressorLabel('Creating Copy of Table from Input Economic Data ...')
        arcpy.CopyRows_management(economics_table, strata_tab)
		
        ##Check if Economic Table Join Field from Economic Data Table exists as attribute
        fieldnames_tbl = [f.name for f in arcpy.ListFields(strata_tab)]
        if economics_join_field not in fieldnames_tbl:
            arcpy.AddError("Economic Table Join Field \"%s\" is not an attribute inside the Input Feature Layer!" % economics_join_field)
            raise arcpy.ExecuteError

        ### Create list of value fields, leaving out OID field and key/join field ###
        flistObj = arcpy.ListFields(strata_tab)
        flist = [f.name for f in flistObj if f.type != "OID" and f.name != economics_join_field]

        ### Create empty dict object then populate each key with a sub dict by row using value fields as keys ###
        arcpy.AddMessage('Creating Join Dictionary for Economics Data ...')
        arcpy.SetProgressorLabel('Creating Join Dictionary for Economics Data ...')
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

                    costs = float(strataDict[strata]['cost_per_animal_transfer']) + \
                            float(strataDict[strata]['cost_feeding_per_animal']) + \
                            float(strataDict[strata]['cost_transportation_per_travel']) + \
                            float(strataDict[strata]['cost_maintenance_per_animal'])

                    revenues = float(strataDict[strata]['revenue_from_transfer_per_animal']) + \
                               float(strataDict[strata]['revenue_from_tourism']) + \
                               float(strataDict[strata]['revenue_from_food_prod'])

                    returns = revenues - costs

                    row[1] = costs
                    row[2] = revenues
                    row[3] = returns

                    cursor.updateRow(row)
								   
        arcpy.AddWarning("Warning: negative monetary values in 'RETURNS' " + \
                         "can be the consequence of missing values in the financial table!!")

        #convert temp feature class to feature layer for output
        out_fl = arcpy.MakeFeatureLayer_management(outCBA_fc, out_Name)
        
		#### Set Parameters ####
        arcpy.SetParameter(4, out_fl)


    except Exception:
        e = sys.exc_info()[1]
        arcpy.AddError('An error occurred: {}'.format(e.args[0]))


if __name__ == '__main__':
    run_CBA()

