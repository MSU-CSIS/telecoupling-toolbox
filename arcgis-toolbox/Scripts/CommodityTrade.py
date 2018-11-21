#This tool maps the flows of commodities from importing and exporting countries.
#Trade data were provided by the Observatory of Economic Complexity
#https://atlas.media.mit.edu/en/resources/permissions/
#Citation: AJG Simoes, CA Hidalgo. The Economic Complexity Observatory: An Analytical Tool for Understanding the Dynamics of Economic Development. 
#          Workshops at the Twenty-Fifth AAAI Conference on Artificial Intelligence. (2011)

#Import modules
import arcpy
import pandas as pd
import numpy as np
import os
import sys

arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3857)

def CommodityTrade():
	countrySelection = arcpy.GetParameterAsText(0) #the user's country selection
	commodityData = arcpy.GetParameterAsText(1) #the OEC data set cleaned for the purposes of this tool
	direction = arcpy.GetParameterAsText(2) #select whether interested in commodity export or import
	commodityItem = arcpy.GetParameterAsText(3) #select commodity of interest from list
	startYear = arcpy.GetParameterAsText(4) #start year of analysis
	endYear = arcpy.GetParameterAsText(5) #end year of analysis
	outputName = arcpy.GetParameterAsText(6) #name of output feature class
	limit = arcpy.GetParameterAsText(7) #gives users the ability to limit trade partners
	numLimit = arcpy.GetParameterAsText(8) #the number of trade partners to limit output to
	
	try:
		#make sure end year follows the start year
		arcpy.AddMessage("here0")
		startYear = int(startYear)
		endYear = int(endYear)
		if endYear < startYear:
			arcpy.AddMessage("End year must follow the start year.")
			sys.exit()
		#read CSV as a dataframe
		df = pd.read_csv(commodityData)
		
		#subset by year
		yearList = range(startYear, endYear + 1)
		df_year = df[df["year"].isin(yearList)]
		
		#subset by commodity
		df_comm_yr = df_year[df_year["comm_name"] == commodityItem]

		#subset by exporting or importing country
		if direction == "Export":
			df_trade = df_comm_yr[df_comm_yr["country_origin"] == countrySelection] #select the exporting country
			df_trade = df_trade[np.isfinite(df_trade["export_val"])] #remove NaN values from export_val 
		else:
			df_trade = df_comm_yr[df_comm_yr["country_dest"] == countrySelection] #select the importing country
			df_trade = df_trade[np.isfinite(df_trade["import_val"])] #remove NaN values from import_val
		
		#limit the number of output linkages if limit is TRUE
		if limit == True:
			if direction == "Export":
				df_trade = df_trade.groupby(["year"], sort = False).apply(lambda x: x.sort_values(["export_val"], ascending = False)) #group data by year and sort descending by export_val
				df_trade = df_trade.groupby("year").head(numLimit).reset_index(drop=True) #Take only as many top trading partners as specified in numLimit
			else:
				df_trade = df_trade.groupby(["year"], sort = False).apply(lambda x: x.sort_values(["import_val"], ascending = False)) #group data by year and sort descending by import_val 
				df_trade = df_trade.groupby("year").head(numLimit).reset_index(drop=True) #Take only as many top trading partners as specified in numLimit
		
		#create feature class for commodity output
		wgs = arcpy.SpatialReference(4326)
		fc = arcpy.CreateFeatureclass_management(arcpy.env.scratchFolder, outputName, "Polyline", "", "", "", wgs)
		arcpy.AddField_management(fc, "Year", "SHORT")  #add year field
		arcpy.AddField_management(fc, "Value", "DOUBLE")  #add export/import value field
		arcpy.AddField_management(fc, "Commodity", "TEXT")  #add commodity name field
		arcpy.AddField_management(fc, "Origin", "TEXT")  #add flow origin field
		arcpy.AddField_management(fc, "Dest", "TEXT") #add flow destination field
		
		arcpy.AddMessage("created fc with column names")
		
		#populate feature class with geographic and commodity trade information
		#establish cursor
		cursor = arcpy.InsertCursor(fc)
		
		arcpy.AddMessage("established cursor")
		
		#direction == "Export"
		#flows are drawn by 1) plotting origin and destination points, then 2) drawing line between points
		if direction == "Export":
			point = arcpy.Point()
			array = arcpy.Array()
			featureList = []
			feat = cursor.newRow()
			for i, row in df_trade.iterrows():
				point.X = row["long_origin"]
				point.Y = row["lat_origin"]
				array.add(point)
				point.X = row["long_dest"]
				point.Y = row["lat_dest"]
				array.add(point)
				polyline = arcpy.Polyline(array)
				array.removeAll()
				featureList.append(polyline)
				feat.shape = polyline
				cursor.insertRow(feat)
			del feat
			del cursor
			
			arcpy.AddMessage("geometry added to fc")
			
			#add year, value, commodity name, origin, and destination information
			j = 0
			with arcpy.da.UpdateCursor(fc, ("Year", "Value", "Commodity", "Origin", "Dest")) as cursor:
				for ROW in cursor:
					ROW[0] = df_trade["year"][j]
					ROW[1] = df_trade["export_val"][j]
					ROW[2] = df_trade["comm_name"][j]
					ROW[3] = df_trade["country_origin"][j]
					ROW[4] = df_trade["country_dest"][j]
					cursor.updateRow(ROW)
					j += 1
			
			arcpy.AddMessage("commodity trade information added")
			
		arcpy.AddMessage("here2")
	
	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError('An error occurred: {}'.format(e.args[0]))

if __name__ == '__main__':
	CommodityTrade()