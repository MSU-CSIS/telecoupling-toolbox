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
import shutil
import glob

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
	limit = arcpy.GetParameter(7) #gives users the ability to limit trade partners
	numLimit = arcpy.GetParameterAsText(8) #the number of trade partners to limit output to
	
	#remove commodity trade shapefile if if already exists from a previous run
	if os.path.exists(os.path.join(arcpy.env.scratchFolder, outputName + ".shp")):
		for filename in glob.glob(os.path.join(arcpy.env.scratchFolder, outputName + "*")):
			os.remove(filename)

	try:
		#make sure end year follows the start year
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
			df_trade = df_comm_yr[df_comm_yr["cntry_orig"] == countrySelection] #select the exporting country
			if df_trade["export_val"].isnull().all():
				arcpy.AddMessage("Nothing to map! " + countrySelection + " did not export " + commodityItem + " from " + str(startYear) + " to " + str(endYear) + ".")
				sys.exit()
			df_trade = df_trade[np.isfinite(df_trade["export_val"])] #remove NaN values from export_val
			df_trade["import_val"].fillna(0, inplace=True) #import values not important. replace NaN with 0
		else:
			df_trade = df_comm_yr[df_comm_yr["cntry_dest"] == countrySelection] #select the importing country
			if df_trade["import_val"].isnull().all():
				arcpy.AddMessage("Nothing to map! " + countrySelection + " did not import " + commodityItem + " from " + str(startYear) + " to " + str(endYear) + ".")
				sys.exit()
			df_trade = df_trade[np.isfinite(df_trade["import_val"])] #remove NaN values from import_val
			df_trade["export_val"].fillna(0, inplace=True) #export values not important. replace NaN with 0
		
		#limit the number of output linkages if limit is TRUE
		if limit:
			numLimit = int(numLimit)
			if direction == "Export":
				df_trade = df_trade.groupby("year", group_keys = False).apply(lambda g: g.nlargest(numLimit, "export_val")) #group data by year and return the top trading partners as specified in numLimit
			else:
				df_trade = df_trade.groupby("year", group_keys = False).apply(lambda g: g.nlargest(numLimit, "import_val")) #group data by year and return the top trading partners as specified in numLimit
			#count number of records in each year. if record count is below numLimit for any year, then below message is printed to inform user that there are fewer returned records than the number requested
			count_occur = df_trade.groupby(["year"]).size()
			count_occur = count_occur.to_frame(name="size").reset_index()
			if (count_occur["size"] == numLimit).all() == False:
				arcpy.AddMessage("FYI, the number of returned trade partners is less than the specified limit for some or all analysis years.")
		
		#create dbase table. this will be used to put Pandas DataFrame content within fc
		arr = np.array(np.rec.fromrecords(df_trade.values))
		names = df_trade.dtypes.index.tolist()
		arr.dtype.names = tuple(names)
		arcpy.da.NumPyArrayToTable(arr, os.path.join(arcpy.env.scratchFolder, "df_table.dbf"))
		table = os.path.join(arcpy.env.scratchFolder, "df_table.dbf")
		
		#draw radial flows using dbase table
		wgs = arcpy.SpatialReference(4326)
		flowsOutputFC = os.path.join(arcpy.env.scratchFolder, outputName + ".shp")
		if direction == "Export":
			arcpy.XYToLine_management(in_table = table, out_featureclass = flowsOutputFC,
										startx_field = "lon_origin", starty_field = "lat_origin",
										endx_field = "lon_dest", endy_field = "lat_dest",
										line_type="GEODESIC", id_field = "id", spatial_reference = wgs)
		else:
			arcpy.XYToLine_management(in_table = table, out_featureclass = flowsOutputFC,
										startx_field = "lon_dest", starty_field = "lat_dest",
										endx_field = "lon_origin", endy_field = "lat_origin",
										line_type="GEODESIC", id_field = "id", spatial_reference = wgs)
		
		#join commodity trade data from dbase table to radial flows feature class
		arcpy.JoinField_management(in_data = flowsOutputFC, in_field = "id", join_table = table, join_field = "id")
		
		#drop unnecesary fields
		if direction == "Export":
			dropFields = ["Unnamed__0", "id", "orgid", "origin", "dest", "comm_code", "import_val", "lat_origin", "lon_origin", "lat_dest", "lon_dest", "id_1", "lat_orig_1", "lon_orig_1", "lat_dest_1", "lon_dest_1"]
		else:
			dropFields = ["Unnamed__0", "id", "orgid", "origin", "dest", "comm_code", "export_val", "lat_origin", "lon_origin", "lat_dest", "lon_dest", "id_1", "lat_orig_1", "lon_orig_1", "lat_dest_1", "lon_dest_1"]
		arcpy.DeleteField_management(flowsOutputFC, dropFields)
		
		#remove the dbase table from the scratch folder
		os.chdir(arcpy.env.scratchFolder)
		os.remove(os.path.join(arcpy.env.scratchFolder, 'df_table.dbf'))

		#add output to map
		arcpy.SetParameter(9, flowsOutputFC)

	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError('An error occurred: {}'.format(e.args[0]))

if __name__ == '__main__':
	CommodityTrade()