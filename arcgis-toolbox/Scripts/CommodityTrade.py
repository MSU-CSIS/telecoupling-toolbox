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
	limit = arcpy.GetParameterAsText(6) #gives users the ability to limit trade partners
	numLimit = arcpy.GetParameterAsText(7) #the number of trade partners to limit output to
	
	try:
		#make sure end year follows the start year
		startYear = int(startYear)
		endYear = int(endYear)
		if endYear < startYear:
			arcpy.AddMessage("End year must follow the start year.")
			sys.exit()
		#read CSV as a dataframe and apply column headers
		df = pd.read_csv(commodityData, names=["id", "orgid", "year", "origin", "dest", "comm_code", "export_val", "import_val", "comm_name", 
												"country_origin", "lat_origin", "long_origin", "country_dest", "lat_dest", "long_dest"])
		
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

		
		
		
		
		"""
		ILL EVENTUALLY NEED TO RUN THIS CODE
		#limit output to the top ten export destinations or import origins
		if limit == True:
			if direction == "Export":
				sortDF = df_trade.sort_values("export_val", ascending=False)
		"""